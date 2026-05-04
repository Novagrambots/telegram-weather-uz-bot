"""Клавиатуры погоды."""
from __future__ import annotations

from aiogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove,
)

from bot.emojis import E_ID
from bot.i18n import t


def get_weather_main_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    """Главное inline-меню погоды."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=t("btn.weather.now", lang),
                callback_data="wmenu:now",
                style="primary",
                icon_custom_emoji_id=E_ID["search"],
            ),
            InlineKeyboardButton(
                text=t("btn.weather.forecast", lang),
                callback_data="wmenu:forecast",
                style="primary",
                icon_custom_emoji_id=E_ID["clock"],
            ),
        ],
        [
            InlineKeyboardButton(
                text=t("btn.weather.location", lang),
                callback_data="wmenu:loc",
                style="success",
                icon_custom_emoji_id=E_ID["pin"],
            ),
            InlineKeyboardButton(
                text=t("btn.weather.uz_cities", lang),
                callback_data="wmenu:uz",
                style="success",
                icon_custom_emoji_id=E_ID["home"],
            ),
        ],
        [
            InlineKeyboardButton(
                text=t("btn.weather.favorites", lang),
                callback_data="wmenu:fav",
                style="success",
                icon_custom_emoji_id=E_ID["star"],
            ),
            InlineKeyboardButton(
                text=t("btn.weather.clothes", lang),
                callback_data="wmenu:clothes",
                style="success",
                icon_custom_emoji_id=E_ID["package"],
            ),
        ],
        [InlineKeyboardButton(
            text=t("btn.back", lang),
            callback_data="back_to_menu",
            style="success",
            icon_custom_emoji_id=E_ID["back"],
        )],
    ])


def get_weather_back_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Кнопка 'Назад' в меню погоды (не в главное меню бота)."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=t("btn.back", lang),
            callback_data="back_to_weather",
            style="success",
            icon_custom_emoji_id=E_ID["back"],
        )],
    ])


def get_location_request_kb(lang: str = "ru") -> ReplyKeyboardMarkup:
    """Одноразовая reply-клавиатура с запросом геолокации (Telegram API не поддерживает custom emoji в reply-клавиатурах)."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t("btn.weather.location", lang), request_location=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def get_uz_cities_kb(cities: list, lang: str = "ru") -> InlineKeyboardMarkup:
    """Inline с топ-городами Узбекистана. cities — list[City]."""
    buttons: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []
    for c in cities:
        title = c.name_ru if (lang == "ru" and c.name_ru) else (c.name_uz if (lang == "uz" and c.name_uz) else c.name_en)
        row.append(InlineKeyboardButton(
            text=title,
            callback_data=f"wcity:{c.id}",
            style="primary",
            icon_custom_emoji_id=E_ID["pin"],
        ))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(
        text=t("btn.back", lang),
        callback_data="back_to_weather",
        style="success",
        icon_custom_emoji_id=E_ID["back"],
    )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_city_actions_kb(city_id: int, lang: str = "ru", is_fav: bool = False) -> InlineKeyboardMarkup:
    """Действия над городом: прогноз / воздух / алерты / избранное."""
    fav_text = t("btn.weather.fav_remove", lang) if is_fav else t("btn.weather.fav_add", lang)
    fav_cb = f"wfav_del:{city_id}" if is_fav else f"wfav_add:{city_id}"
    fav_icon = E_ID["trash"] if is_fav else E_ID["star"]
    fav_style = "danger" if is_fav else "success"
    buttons = [
        [
            InlineKeyboardButton(
                text=t("btn.weather.forecast", lang),
                callback_data=f"wfc:{city_id}",
                style="primary",
                icon_custom_emoji_id=E_ID["clock"],
            ),
            InlineKeyboardButton(
                text=t("btn.weather.air", lang),
                callback_data=f"wair:{city_id}",
                style="primary",
                icon_custom_emoji_id=E_ID["bulb"],
            ),
        ],
        [
            InlineKeyboardButton(
                text=t("btn.weather.clothes", lang),
                callback_data=f"wclo:{city_id}",
                style="success",
                icon_custom_emoji_id=E_ID["package"],
            ),
        ],
        [InlineKeyboardButton(
            text=fav_text,
            callback_data=fav_cb,
            style=fav_style,
            icon_custom_emoji_id=fav_icon,
        )],
        [InlineKeyboardButton(
            text=t("btn.back", lang),
            callback_data="back_to_weather",
            style="success",
            icon_custom_emoji_id=E_ID["back"],
        )],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_favorites_kb(cities: list, lang: str = "ru") -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = []
    for c in cities:
        title = c.name_ru if (lang == "ru" and c.name_ru) else (c.name_uz if (lang == "uz" and c.name_uz) else c.name_en)
        buttons.append([
            InlineKeyboardButton(
                text=title,
                callback_data=f"wcity:{c.id}",
                style="primary",
                icon_custom_emoji_id=E_ID["star"],
            ),
            InlineKeyboardButton(
                text=t("btn.weather.fav_remove", lang),
                callback_data=f"wfav_del:{c.id}",
                style="danger",
                icon_custom_emoji_id=E_ID["trash"],
            ),
        ])
    buttons.append([InlineKeyboardButton(
        text=t("btn.back", lang),
        callback_data="back_to_weather",
        style="success",
        icon_custom_emoji_id=E_ID["back"],
    )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_units_kb(current: str = "metric", lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Metric (°C)",
                callback_data="wunits:metric",
                style="primary" if current == "metric" else "success",
                icon_custom_emoji_id=E_ID["check"] if current == "metric" else E_ID["gear"],
            ),
            InlineKeyboardButton(
                text="Imperial (°F)",
                callback_data="wunits:imperial",
                style="primary" if current == "imperial" else "success",
                icon_custom_emoji_id=E_ID["check"] if current == "imperial" else E_ID["gear"],
            ),
        ],
        [InlineKeyboardButton(
            text=t("btn.back", lang),
            callback_data="back_to_weather",
            style="success",
            icon_custom_emoji_id=E_ID["back"],
        )],
    ])


