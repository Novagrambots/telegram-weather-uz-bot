"""Доменные хендлеры погоды."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery, InlineQuery, InlineQueryResultArticle,
    InputTextMessageContent, Message,
)
from sqlalchemy import select

from bot.database import async_session
from bot.database.crud import (
    add_favorite, find_city_by_name, get_city_by_id,
    get_or_create_user, get_user_language, list_favorites,
    list_uz_cities, remove_favorite, update_user_units,
)
from bot.database.models import FavoriteCity, User
from bot.i18n import t
from bot.keyboards.weather import (
    get_city_actions_kb, get_favorites_kb,
    get_units_kb, get_uz_cities_kb, get_weather_back_keyboard, get_weather_main_kb,
)
from bot.services.weather import (
    classify_error, format_air, format_current,
    format_forecast, get_air, get_clothes_recommendation,
    get_current_weather, get_forecast, resolve_city,
    resolve_city_by_coords,
)

logger = logging.getLogger(__name__)
router = Router()


class WeatherStates(StatesGroup):
    waiting_city = State()
    waiting_forecast_city = State()
    waiting_clothes_city = State()
    waiting_air_city = State()
    waiting_subscribe_time = State()


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

async def _get_user_and_lang(tg_id: int, username: str | None, name: str | None) -> tuple[User, str]:
    async with async_session() as session:
        user = await get_or_create_user(session, tg_id, username, name)
        return user, user.language_code or "ru"


async def _send_weather_for_city(message_or_cb, city, user: User, lang: str) -> None:
    """Универсальный показ текущей погоды + клавиатуры действий."""
    units = user.units.value if user.units else "metric"
    try:
        data, _src, fetched = await get_current_weather(user, city, lang=lang, units=units)
    except Exception as e:
        cat = classify_error(e)
        key = {
            "not_found": "error.city_not_found",
            "api_quota": "error.api_unavailable",
            "api_error": "error.api_unavailable",
        }.get(cat, "error.generic")
        text = t(key, lang)
        kb = get_weather_back_keyboard(lang)
        if isinstance(message_or_cb, CallbackQuery):
            await message_or_cb.message.answer(text, reply_markup=kb)
            await message_or_cb.answer()
        else:
            await message_or_cb.answer(text, reply_markup=kb)
        return

    text = format_current(data, city, fetched, lang=lang, units=units)
    # проверим избранное
    async with async_session() as session:
        res = await session.execute(
            select(FavoriteCity).where(
                (FavoriteCity.user_id == user.id) & (FavoriteCity.city_id == city.id)
            )
        )
        is_fav = res.scalar_one_or_none() is not None
    kb = get_city_actions_kb(city.id, lang=lang, is_fav=is_fav)

    if isinstance(message_or_cb, CallbackQuery):
        await message_or_cb.message.answer(text, reply_markup=kb, parse_mode="HTML")
        await message_or_cb.answer()
    else:
        await message_or_cb.answer(text, reply_markup=kb, parse_mode="HTML")


# ------------------------------------------------------------------
# /weather, /forecast, /tomorrow, /clothes, /air, /history
# ------------------------------------------------------------------

@router.message(Command("weather"))
async def cmd_weather(message: Message, state: FSMContext) -> None:
    user, lang = await _get_user_and_lang(message.from_user.id, message.from_user.username, message.from_user.first_name)
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await state.set_state(WeatherStates.waiting_city)
        await message.answer(t("weather.ask_city", lang), reply_markup=get_weather_main_kb(lang))
        return
    await _resolve_and_show_current(message, args[1].strip(), user, lang)


async def _resolve_and_show_current(message: Message, city_query: str, user: User, lang: str) -> None:
    async with async_session() as session:
        city = await resolve_city(session, city_query)
    if not city:
        await message.answer(t("error.city_not_found", lang), reply_markup=get_weather_back_keyboard(lang))
        return
    await _send_weather_for_city(message, city, user, lang)


RESERVED_BUTTON_TEXTS = {
    "По геолокации", "Geolokatsiya", "By location",
    "Сейчас", "Hozir", "Now",
    "Прогноз", "Bashorat", "Forecast",
    "Города UZ", "UZ shaharlari", "UZ cities",
    "Избранные", "Sevimlilar", "Favorites",
    "Одежда", "Kiyim", "Clothes",
}


@router.message(F.text.in_({"По геолокации", "Geolokatsiya", "By location"}))
async def btn_location_text(message: Message) -> None:
    """Юзер тапнул reply-кнопку 'По геолокации', но клиент не прислал локацию
    (десктоп / отказ в доступе). Подсказываем как прислать вручную."""
    _u, lang = await _get_user_and_lang(message.from_user.id, message.from_user.username, message.from_user.first_name)
    await message.answer(t("weather.location_manual_hint", lang), reply_markup=get_weather_back_keyboard(lang))


@router.message(WeatherStates.waiting_city, F.text & ~F.text.startswith("/") & ~F.text.in_(RESERVED_BUTTON_TEXTS))
async def fsm_city_input(message: Message, state: FSMContext) -> None:
    await state.clear()
    user, lang = await _get_user_and_lang(message.from_user.id, message.from_user.username, message.from_user.first_name)
    await _resolve_and_show_current(message, message.text.strip(), user, lang)


@router.message(Command("forecast"))
async def cmd_forecast(message: Message, state: FSMContext) -> None:
    user, lang = await _get_user_and_lang(message.from_user.id, message.from_user.username, message.from_user.first_name)
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await state.set_state(WeatherStates.waiting_forecast_city)
        await message.answer(t("weather.ask_city", lang), reply_markup=get_weather_back_keyboard(lang))
        return
    await _send_forecast(message, args[1].strip(), user, lang)


@router.message(WeatherStates.waiting_forecast_city, F.text & ~F.text.startswith("/") & ~F.text.in_(RESERVED_BUTTON_TEXTS))
async def fsm_forecast_city(message: Message, state: FSMContext) -> None:
    await state.clear()
    user, lang = await _get_user_and_lang(message.from_user.id, message.from_user.username, message.from_user.first_name)
    await _send_forecast(message, message.text.strip(), user, lang)


@router.message(WeatherStates.waiting_clothes_city, F.text & ~F.text.startswith("/") & ~F.text.in_(RESERVED_BUTTON_TEXTS))
async def fsm_clothes_city(message: Message, state: FSMContext) -> None:
    await state.clear()
    user, lang = await _get_user_and_lang(message.from_user.id, message.from_user.username, message.from_user.first_name)
    async with async_session() as session:
        city = await resolve_city(session, message.text.strip())
    if not city:
        await message.answer(t("error.city_not_found", lang), reply_markup=get_weather_back_keyboard(lang))
        return
    units = user.units.value if user.units else "metric"
    try:
        data, _src, _f = await get_current_weather(user, city, lang=lang, units=units)
    except Exception:
        await message.answer(t("error.api_unavailable", lang), reply_markup=get_weather_back_keyboard(lang))
        return
    await message.answer(get_clothes_recommendation(data, lang=lang), reply_markup=get_weather_back_keyboard(lang))


async def _send_forecast(message: Message, query: str, user: User, lang: str) -> None:
    async with async_session() as session:
        city = await resolve_city(session, query)
    if not city:
        await message.answer(t("error.city_not_found", lang), reply_markup=get_weather_back_keyboard(lang))
        return
    units = user.units.value if user.units else "metric"
    try:
        data, _src, fetched = await get_forecast(user, city, lang=lang, units=units)
    except Exception as e:
        await message.answer(t("error.api_unavailable", lang), reply_markup=get_weather_back_keyboard(lang))
        logger.warning("forecast fail: %s", e)
        return
    await message.answer(format_forecast(data, city, fetched, lang=lang, units=units), parse_mode="HTML", reply_markup=get_weather_back_keyboard(lang))


@router.message(Command("tomorrow"))
async def cmd_tomorrow(message: Message) -> None:
    """Прогноз на завтра — 4 ближайших слота к 9, 12, 15, 18 завтрашнего дня."""
    user, lang = await _get_user_and_lang(message.from_user.id, message.from_user.username, message.from_user.first_name)
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(t("weather.ask_city", lang), reply_markup=get_weather_back_keyboard(lang))
        return
    async with async_session() as session:
        city = await resolve_city(session, args[1].strip())
    if not city:
        await message.answer(t("error.city_not_found", lang), reply_markup=get_weather_back_keyboard(lang))
        return
    units = user.units.value if user.units else "metric"
    try:
        data, _src, _fetched = await get_forecast(user, city, lang=lang, units=units)
    except Exception:
        await message.answer(t("error.api_unavailable", lang), reply_markup=get_weather_back_keyboard(lang))
        return

    tomorrow = (datetime.now() + timedelta(days=1)).date()
    items = [it for it in data.get("list", [])
             if datetime.fromtimestamp(it["dt"]).date() == tomorrow]
    if not items:
        await message.answer(t("error.api_unavailable", lang), reply_markup=get_weather_back_keyboard(lang))
        return

    title = {"ru": "На завтра", "uz": "Ertaga", "en": "Tomorrow"}.get(lang, "Tomorrow")
    lines = [f"📅 <b>{title} — {city.name_ru or city.name_en}</b>", ""]
    unit_t = "°C" if units == "metric" else "°F"
    for it in items:
        dt = datetime.fromtimestamp(it["dt"])
        w = it.get("weather", [{}])[0]
        from bot.services.icons import desc_for_owm_id, emoji_for_owm_id
        wid = w.get("id", 800)
        lines.append(
            f"{emoji_for_owm_id(wid)} {dt.strftime('%H:%M')} — "
            f"<b>{it['main']['temp']:.1f}{unit_t}</b>, {desc_for_owm_id(wid, lang)}"
        )
    await message.answer("\n".join(lines), parse_mode="HTML", reply_markup=get_weather_back_keyboard(lang))


@router.message(Command("clothes"))
async def cmd_clothes(message: Message) -> None:
    user, lang = await _get_user_and_lang(message.from_user.id, message.from_user.username, message.from_user.first_name)
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(t("weather.ask_city", lang), reply_markup=get_weather_back_keyboard(lang))
        return
    async with async_session() as session:
        city = await resolve_city(session, args[1].strip())
    if not city:
        await message.answer(t("error.city_not_found", lang), reply_markup=get_weather_back_keyboard(lang))
        return
    units = user.units.value if user.units else "metric"
    try:
        data, _src, _f = await get_current_weather(user, city, lang=lang, units=units)
    except Exception:
        await message.answer(t("error.api_unavailable", lang), reply_markup=get_weather_back_keyboard(lang))
        return
    await message.answer(get_clothes_recommendation(data, lang=lang), reply_markup=get_weather_back_keyboard(lang))


@router.message(Command("air"))
async def cmd_air(message: Message) -> None:
    user, lang = await _get_user_and_lang(message.from_user.id, message.from_user.username, message.from_user.first_name)
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(t("weather.ask_city", lang), reply_markup=get_weather_back_keyboard(lang))
        return
    async with async_session() as session:
        city = await resolve_city(session, args[1].strip())
    if not city:
        await message.answer(t("error.city_not_found", lang), reply_markup=get_weather_back_keyboard(lang))
        return
    try:
        data, _src, fetched = await get_air(user, city)
    except Exception:
        await message.answer(t("error.api_unavailable", lang), reply_markup=get_weather_back_keyboard(lang))
        return
    await message.answer(format_air(data, city, fetched, lang=lang), parse_mode="HTML", reply_markup=get_weather_back_keyboard(lang))


@router.message(Command("map"))
async def cmd_map(message: Message) -> None:
    user, lang = await _get_user_and_lang(message.from_user.id, message.from_user.username, message.from_user.first_name)
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(t("weather.ask_city", lang), reply_markup=get_weather_back_keyboard(lang))
        return
    async with async_session() as session:
        city = await resolve_city(session, args[1].strip())
    if not city:
        await message.answer(t("error.city_not_found", lang), reply_markup=get_weather_back_keyboard(lang))
        return
    await message.answer_location(latitude=city.lat, longitude=city.lon)
    osm = f"https://www.openstreetmap.org/?mlat={city.lat}&mlon={city.lon}#map=10/{city.lat}/{city.lon}"
    await message.answer(f"🗺 {city.name_ru or city.name_en}\n{osm}", reply_markup=get_weather_back_keyboard(lang))


# ------------------------------------------------------------------
# Геолокация
# ------------------------------------------------------------------

@router.message(Command("location"))
async def cmd_location_request(message: Message) -> None:
    _user, lang = await _get_user_and_lang(message.from_user.id, message.from_user.username, message.from_user.first_name)
    from bot.keyboards.weather import get_location_request_kb
    await message.answer(
        t("weather.send_location", lang),
        reply_markup=get_location_request_kb(lang),
        parse_mode="HTML",
    )


@router.message(F.location)
async def handle_location(message: Message, state: FSMContext) -> None:
    await state.clear()
    user, lang = await _get_user_and_lang(message.from_user.id, message.from_user.username, message.from_user.first_name)
    lat, lon = message.location.latitude, message.location.longitude
    async with async_session() as session:
        city = await resolve_city_by_coords(session, lat, lon)
    if not city:
        await message.answer(t("error.city_not_found", lang), reply_markup=get_weather_back_keyboard(lang))
        return
    # снимаем reply-клавиатуру с request_location, чтобы не висела
    from aiogram.types import ReplyKeyboardRemove
    await message.answer("📍", reply_markup=ReplyKeyboardRemove())
    await _send_weather_for_city(message, city, user, lang)


# ------------------------------------------------------------------
# Inline-кнопки главного меню погоды (wmenu:*)
# ------------------------------------------------------------------

@router.callback_query(F.data == "wmenu:now")
async def cb_menu_now(callback: CallbackQuery, state: FSMContext) -> None:
    _u, lang = await _get_user_and_lang(callback.from_user.id, callback.from_user.username, callback.from_user.first_name)
    await state.set_state(WeatherStates.waiting_city)
    await callback.message.answer(t("weather.ask_city", lang), reply_markup=get_weather_back_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data == "wmenu:forecast")
async def cb_menu_forecast(callback: CallbackQuery, state: FSMContext) -> None:
    _u, lang = await _get_user_and_lang(callback.from_user.id, callback.from_user.username, callback.from_user.first_name)
    await state.set_state(WeatherStates.waiting_forecast_city)
    await callback.message.answer(t("weather.ask_city", lang), reply_markup=get_weather_back_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data == "wmenu:uz")
async def cb_menu_uz(callback: CallbackQuery) -> None:
    _u, lang = await _get_user_and_lang(callback.from_user.id, callback.from_user.username, callback.from_user.first_name)
    async with async_session() as session:
        cities = await list_uz_cities(session, limit=20)
    await callback.message.answer(t("weather.uz_cities_title", lang),
                                  reply_markup=get_uz_cities_kb(cities, lang=lang))
    await callback.answer()


@router.callback_query(F.data == "wmenu:fav")
async def cb_menu_fav(callback: CallbackQuery) -> None:
    user, lang = await _get_user_and_lang(callback.from_user.id, callback.from_user.username, callback.from_user.first_name)
    async with async_session() as session:
        favs = await list_favorites(session, user.id)
    if not favs:
        await callback.message.answer(t("weather.no_favorites", lang), reply_markup=get_weather_back_keyboard(lang))
    else:
        await callback.message.answer(t("weather.favorites_title", lang),
                                      reply_markup=get_favorites_kb(favs, lang=lang))
    await callback.answer()


@router.callback_query(F.data == "wmenu:clothes")
async def cb_menu_clothes(callback: CallbackQuery, state: FSMContext) -> None:
    _u, lang = await _get_user_and_lang(callback.from_user.id, callback.from_user.username, callback.from_user.first_name)
    await state.set_state(WeatherStates.waiting_clothes_city)
    await callback.message.answer(t("weather.ask_city", lang), reply_markup=get_weather_back_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data == "wmenu:loc")
async def cb_menu_loc(callback: CallbackQuery) -> None:
    _u, lang = await _get_user_and_lang(callback.from_user.id, callback.from_user.username, callback.from_user.first_name)
    from bot.keyboards.weather import get_location_request_kb
    await callback.message.answer(
        t("weather.send_location", lang),
        reply_markup=get_location_request_kb(lang),
        parse_mode="HTML",
    )
    await callback.answer()


# ------------------------------------------------------------------
# Callback'и
# ------------------------------------------------------------------

@router.callback_query(F.data.in_({"weather_menu", "back_to_weather"}))
async def cb_weather_menu(callback: CallbackQuery, state: FSMContext) -> None:
    """Открывает inline-меню погоды."""
    _u, lang = await _get_user_and_lang(
        callback.from_user.id, callback.from_user.username, callback.from_user.first_name,
    )
    await state.clear()
    try:
        await callback.message.edit_text(
            t("weather.menu_title", lang),
            reply_markup=get_weather_main_kb(lang),
        )
    except Exception:
        await callback.message.answer(
            t("weather.menu_title", lang),
            reply_markup=get_weather_main_kb(lang),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("wcity:"))
async def cb_pick_city(callback: CallbackQuery) -> None:
    user, lang = await _get_user_and_lang(callback.from_user.id, callback.from_user.username, callback.from_user.first_name)
    city_id = int(callback.data.split(":", 1)[1])
    async with async_session() as session:
        city = await get_city_by_id(session, city_id)
    if not city:
        await callback.answer(t("error.city_not_found", lang), show_alert=True)
        return
    await _send_weather_for_city(callback, city, user, lang)


@router.callback_query(F.data.startswith("wfc:"))
async def cb_forecast(callback: CallbackQuery) -> None:
    user, lang = await _get_user_and_lang(callback.from_user.id, callback.from_user.username, callback.from_user.first_name)
    city_id = int(callback.data.split(":", 1)[1])
    async with async_session() as session:
        city = await get_city_by_id(session, city_id)
    if not city:
        await callback.answer(t("error.city_not_found", lang), show_alert=True)
        return
    units = user.units.value if user.units else "metric"
    try:
        data, _src, fetched = await get_forecast(user, city, lang=lang, units=units)
    except Exception:
        await callback.answer(t("error.api_unavailable", lang), show_alert=True)
        return
    await callback.message.answer(
        format_forecast(data, city, fetched, lang=lang, units=units),
        parse_mode="HTML",
        reply_markup=get_weather_back_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("wair:"))
async def cb_air(callback: CallbackQuery) -> None:
    user, lang = await _get_user_and_lang(callback.from_user.id, callback.from_user.username, callback.from_user.first_name)
    city_id = int(callback.data.split(":", 1)[1])
    async with async_session() as session:
        city = await get_city_by_id(session, city_id)
    if not city:
        await callback.answer(t("error.city_not_found", lang), show_alert=True)
        return
    try:
        data, _src, fetched = await get_air(user, city)
    except Exception:
        await callback.answer(t("error.api_unavailable", lang), show_alert=True)
        return
    await callback.message.answer(format_air(data, city, fetched, lang=lang), parse_mode="HTML", reply_markup=get_weather_back_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("wclo:"))
async def cb_clothes(callback: CallbackQuery) -> None:
    user, lang = await _get_user_and_lang(callback.from_user.id, callback.from_user.username, callback.from_user.first_name)
    city_id = int(callback.data.split(":", 1)[1])
    async with async_session() as session:
        city = await get_city_by_id(session, city_id)
    if not city:
        await callback.answer(t("error.city_not_found", lang), show_alert=True)
        return
    units = user.units.value if user.units else "metric"
    try:
        data, _src, _f = await get_current_weather(user, city, lang=lang, units=units)
    except Exception:
        await callback.answer(t("error.api_unavailable", lang), show_alert=True)
        return
    await callback.message.answer(get_clothes_recommendation(data, lang=lang), reply_markup=get_weather_back_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("wfav_add:"))
async def cb_fav_add(callback: CallbackQuery) -> None:
    user, lang = await _get_user_and_lang(callback.from_user.id, callback.from_user.username, callback.from_user.first_name)
    city_id = int(callback.data.split(":", 1)[1])
    async with async_session() as session:
        added = await add_favorite(session, user.id, city_id)
    msg = t("weather.fav_added" if added else "weather.fav_exists", lang)
    await callback.answer(msg, show_alert=False)


@router.callback_query(F.data.startswith("wfav_del:"))
async def cb_fav_del(callback: CallbackQuery) -> None:
    user, lang = await _get_user_and_lang(callback.from_user.id, callback.from_user.username, callback.from_user.first_name)
    city_id = int(callback.data.split(":", 1)[1])
    async with async_session() as session:
        await remove_favorite(session, user.id, city_id)
    await callback.answer(t("weather.fav_removed", lang))


# ------------------------------------------------------------------
# Подписка/отписка/единицы
# ------------------------------------------------------------------

@router.message(Command("favorites"))
async def cmd_favorites(message: Message) -> None:
    user, lang = await _get_user_and_lang(message.from_user.id, message.from_user.username, message.from_user.first_name)
    async with async_session() as session:
        favs = await list_favorites(session, user.id)
    if not favs:
        await message.answer(t("weather.no_favorites", lang), reply_markup=get_weather_back_keyboard(lang))
        return
    await message.answer(
        t("weather.favorites_title", lang),
        reply_markup=get_favorites_kb(favs, lang=lang),
    )


@router.message(Command("units"))
async def cmd_units(message: Message) -> None:
    user, lang = await _get_user_and_lang(message.from_user.id, message.from_user.username, message.from_user.first_name)
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        cur = user.units.value if user.units else "metric"
        await message.answer(t("weather.units_choose", lang),
                             reply_markup=get_units_kb(current=cur, lang=lang))
        return
    val = parts[1].strip().lower()
    if val not in ("metric", "imperial"):
        await message.answer(t("weather.units_bad", lang), reply_markup=get_weather_back_keyboard(lang))
        return
    async with async_session() as session:
        await update_user_units(session, message.from_user.id, val)
    await message.answer(t("weather.units_set", lang, units=val), reply_markup=get_weather_back_keyboard(lang))


@router.callback_query(F.data.startswith("wunits:"))
async def cb_units(callback: CallbackQuery) -> None:
    val = callback.data.split(":", 1)[1]
    if val not in ("metric", "imperial"):
        await callback.answer()
        return
    async with async_session() as session:
        await update_user_units(session, callback.from_user.id, val)
        lang = await get_user_language(session, callback.from_user.id)
    await callback.answer(t("weather.units_set", lang, units=val))


# ------------------------------------------------------------------
# Inline mode
# ------------------------------------------------------------------

@router.inline_query()
async def inline_search(query: InlineQuery) -> None:
    text = (query.query or "").strip()
    user, lang = await _get_user_and_lang(query.from_user.id, query.from_user.username, query.from_user.first_name)
    if not text:
        await query.answer([], cache_time=5)
        return
    # inline-режим: только локальный поиск по БД, без внешнего геокодинга
    async with async_session() as session:
        city = await find_city_by_name(session, text)
    if not city:
        await query.answer([], cache_time=5, switch_pm_text=t("weather.inline_city_not_found", lang), switch_pm_parameter="start")
        return
    units = user.units.value if user.units else "metric"
    try:
        data, _src, fetched = await get_current_weather(user, city, lang=lang, units=units)
        body = format_current(data, city, fetched, lang=lang, units=units)
    except Exception:
        body = t("error.api_unavailable", lang)

    title = city.name_ru or city.name_en
    result = InlineQueryResultArticle(
        id=str(city.id),
        title=f"🌤 {title}",
        description=text,
        input_message_content=InputTextMessageContent(message_text=body, parse_mode="HTML"),
    )
    await query.answer([result], cache_time=60, is_personal=True)


# ------------------------------------------------------------------
# Текстовый запрос — fallback "просто прислал название города"
# ------------------------------------------------------------------

@router.message(F.text & ~F.text.startswith("/") & ~F.text.in_(RESERVED_BUTTON_TEXTS))
async def fallback_city_text(message: Message) -> None:
    """Любой текст без команды трактуем как название города."""
    user, lang = await _get_user_and_lang(message.from_user.id, message.from_user.username, message.from_user.first_name)
    await _resolve_and_show_current(message, message.text.strip(), user, lang)
