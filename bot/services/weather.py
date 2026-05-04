"""Высокоуровневый сервис погоды.
Объединяет OWM (главный) + WeatherAPI (fallback) + кэш в БД + форматирование.
"""
from __future__ import annotations

import asyncio
import html
import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import settings
from bot.database import async_session
from bot.database.crud import (
    find_city_by_name, find_nearest_city, get_cache, get_or_create_city,
    log_request, set_cache,
)
from bot.database.models import CacheTypeEnum, City, User, WeatherSourceEnum
from bot.i18n import t
from bot.services.icons import (
    aqi_label, desc_for_owm_id, emoji_for_owm_icon, emoji_for_owm_id, wind_arrow,
)
from bot.services.openweathermap import (
    OWMError, OWMNotFound, OWMQuotaError, owm_client,
)
from bot.services.weatherapi import WeatherAPIError, weatherapi_client

logger = logging.getLogger(__name__)


# in-memory locks: один lock на (city_id, cache_type), чтобы исключить
# параллельный fetch одних и тех же данных и устранить race condition
_fetch_locks: dict[tuple[int, str], asyncio.Lock] = {}
_fetch_locks_guard = asyncio.Lock()


async def _get_fetch_lock(city_id: int, cache_type: "CacheTypeEnum") -> asyncio.Lock:
    key = (city_id, cache_type.value)
    async with _fetch_locks_guard:
        lock = _fetch_locks.get(key)
        if lock is None:
            lock = asyncio.Lock()
            _fetch_locks[key] = lock
        return lock


def classify_error(exc: Exception) -> str:
    if isinstance(exc, OWMQuotaError):
        return "api_quota"
    if isinstance(exc, OWMNotFound):
        return "not_found"
    if isinstance(exc, (OWMError, WeatherAPIError)):
        return "api_error"
    return "unknown"


# ------------------------------------------------------------------
# Резолв города
# ------------------------------------------------------------------

async def resolve_city(session: AsyncSession, query: str) -> City | None:
    """Ищет в БД по любому из имён → если нет, идёт в геокодинг OWM."""
    if not query:
        return None
    city = await find_city_by_name(session, query)
    if city:
        return city

    # геокодинг
    try:
        results = await owm_client.geocode(query, limit=1)
    except OWMError as e:
        logger.warning("Geocode failed for %r: %s", query, e)
        return None
    if not results:
        return None

    g = results[0]
    name_en = g.get("name") or query
    name_ru = (g.get("local_names") or {}).get("ru")
    name_uz = (g.get("local_names") or {}).get("uz")
    return await get_or_create_city(
        session,
        name_en=name_en,
        lat=float(g["lat"]),
        lon=float(g["lon"]),
        name_ru=name_ru,
        name_uz=name_uz,
        country_code=g.get("country", "UZ"),
    )


async def resolve_city_by_coords(
    session: AsyncSession, lat: float, lon: float
) -> City | None:
    """По координатам — ищем ближайший UZ-город в БД, иначе делаем reverse-geocode и
    создаём настоящий город (без псевдо-имён loc_*)."""
    nearest = await find_nearest_city(session, lat, lon, only_uz=True)
    # если есть UZ-город в радиусе ~ <0.5° — считаем что это он
    if nearest and ((nearest.lat - lat) ** 2 + (nearest.lon - lon) ** 2) < 0.25:
        return nearest

    # reverse geocode через OWM /geo/1.0/reverse
    try:
        results = await owm_client.reverse_geocode(lat, lon, limit=1)
    except OWMError as e:
        logger.warning("Reverse geocode failed for (%s, %s): %s", lat, lon, e)
        results = []

    if results:
        g = results[0]
        name_en = g.get("name") or f"{lat:.4f},{lon:.4f}"
        name_ru = (g.get("local_names") or {}).get("ru")
        name_uz = (g.get("local_names") or {}).get("uz")
        return await get_or_create_city(
            session,
            name_en=name_en,
            lat=float(g.get("lat", lat)),
            lon=float(g.get("lon", lon)),
            name_ru=name_ru,
            name_uz=name_uz,
            country_code=g.get("country", "UZ"),
        )

    # ничего не нашли — отдаём ближайший UZ-город (если был), иначе None
    return nearest


# ------------------------------------------------------------------
# Получение данных (с кэшем + fallback)
# ------------------------------------------------------------------

async def _fetch_with_cache(
    session: AsyncSession,
    city: City,
    cache_type: CacheTypeEnum,
    ttl_min: int,
    fetcher,  # async callable -> dict
    user_id: int | None = None,
) -> tuple[dict, WeatherSourceEnum]:
    """Возвращает (data, source). Источник: cache | owm | weatherapi.
    Использует in-memory lock per (city_id, cache_type) — защита от race condition,
    когда несколько корутин одновременно дёрнут API при пустом кэше."""
    cached = await get_cache(session, city.id, cache_type)
    if cached:
        if user_id is not None:
            await log_request(session, user_id, city.id, cache_type.value, WeatherSourceEnum.cache)
        return cached.data, WeatherSourceEnum.cache

    lock = await _get_fetch_lock(city.id, cache_type)
    async with lock:
        # double-check: пока ждали лок — кто-то мог уже заполнить кэш
        cached = await get_cache(session, city.id, cache_type)
        if cached:
            if user_id is not None:
                await log_request(session, user_id, city.id, cache_type.value, WeatherSourceEnum.cache)
            return cached.data, WeatherSourceEnum.cache

        try:
            data = await fetcher()
            source = WeatherSourceEnum.owm
        except (OWMQuotaError, OWMError) as e:
            # пробуем WeatherAPI fallback (только для current/forecast)
            logger.warning("OWM failed (%s), trying WeatherAPI fallback", e)
            if cache_type in (CacheTypeEnum.current, CacheTypeEnum.forecast) and settings.weatherapi_key:
                try:
                    if cache_type == CacheTypeEnum.current:
                        data = await weatherapi_client.get_current(q=f"{city.lat},{city.lon}")
                    else:
                        data = await weatherapi_client.get_forecast(q=f"{city.lat},{city.lon}", days=5)
                    # помечаем что fallback, чтобы форматтер мог разобрать другую структуру
                    data["__source"] = "weatherapi"
                    source = WeatherSourceEnum.weatherapi
                except WeatherAPIError:
                    raise e
            else:
                raise

        # сохраняем в кэш (UPSERT внутри set_cache)
        await set_cache(session, city.id, cache_type, data, ttl_min)
        if user_id is not None:
            await log_request(session, user_id, city.id, cache_type.value, source)
        return data, source


async def get_current_weather(
    user: User, city: City, lang: str = "ru", units: str = "metric"
) -> tuple[dict, WeatherSourceEnum, datetime]:
    """Текущая погода (TTL 10 мин). Возвращает (data, source, fetched_at)."""
    async with async_session() as session:
        async def _fetch():
            return await owm_client.get_current(
                lat=city.lat, lon=city.lon, lang=lang, units=units,
            )
        data, source = await _fetch_with_cache(
            session, city, CacheTypeEnum.current,
            settings.cache_current_ttl_min, _fetch, user.id,
        )
        cached = await get_cache(session, city.id, CacheTypeEnum.current)
        fetched_at = cached.fetched_at if cached else datetime.now(timezone.utc)
    return data, source, fetched_at


async def get_forecast(
    user: User, city: City, lang: str = "ru", units: str = "metric"
) -> tuple[dict, WeatherSourceEnum, datetime]:
    async with async_session() as session:
        async def _fetch():
            return await owm_client.get_forecast(
                lat=city.lat, lon=city.lon, lang=lang, units=units,
            )
        data, source = await _fetch_with_cache(
            session, city, CacheTypeEnum.forecast,
            settings.cache_forecast_ttl_min, _fetch, user.id,
        )
        cached = await get_cache(session, city.id, CacheTypeEnum.forecast)
        fetched_at = cached.fetched_at if cached else datetime.now(timezone.utc)
    return data, source, fetched_at


async def get_air(
    user: User, city: City
) -> tuple[dict, WeatherSourceEnum, datetime]:
    async with async_session() as session:
        async def _fetch():
            return await owm_client.get_air_pollution(lat=city.lat, lon=city.lon)
        data, source = await _fetch_with_cache(
            session, city, CacheTypeEnum.air, 30, _fetch, user.id,
        )
        cached = await get_cache(session, city.id, CacheTypeEnum.air)
        fetched_at = cached.fetched_at if cached else datetime.now(timezone.utc)
    return data, source, fetched_at


# ------------------------------------------------------------------
# Рекомендация одежды
# ------------------------------------------------------------------

def get_clothes_recommendation(weather_data: dict, lang: str = "ru") -> str:
    """По текущей температуре и осадкам — короткий совет."""
    if weather_data.get("__source") == "weatherapi":
        cur = weather_data.get("current", {})
        temp = cur.get("feelslike_c", cur.get("temp_c", 0))
        wid = (cur.get("condition") or {}).get("code", 1000)
        # WeatherAPI condition codes: 1063,1150-1201 — дождь; 1066,1210-1237 — снег; 1273-1282 — гроза
        rain = wid in {1063, 1066, 1069, 1072, 1087, 1150, 1153, 1168, 1171, 1180,
                        1183, 1186, 1189, 1192, 1195, 1198, 1201, 1204, 1207, 1210,
                        1213, 1216, 1219, 1222, 1225, 1237, 1240, 1243, 1246, 1249,
                        1252, 1255, 1258, 1261, 1264, 1273, 1276, 1279, 1282}
    else:
        main = weather_data.get("main", {})
        temp = main.get("feels_like", main.get("temp", 0))
        weather = (weather_data.get("weather") or [{}])[0]
        wid = weather.get("id", 800)
        rain = wid // 100 in (2, 3, 5, 6)

    if temp >= 28:
        msg = {
            "ru": "🔥 Жарко! Лёгкая футболка, шорты, головной убор и вода.",
            "uz": "🔥 Issiq! Yengil futbolka, shim, bosh kiyimi va suv.",
            "en": "🔥 Hot! Light t-shirt, shorts, hat and water.",
        }
    elif temp >= 20:
        msg = {
            "ru": "😎 Тепло. Футболка и лёгкие штаны.",
            "uz": "😎 Iliq. Futbolka va yengil shim.",
            "en": "😎 Warm. T-shirt and light pants.",
        }
    elif temp >= 10:
        msg = {
            "ru": "🧥 Прохладно. Куртка или толстовка не помешают.",
            "uz": "🧥 Salqin. Kurtka yoki tolstovka kerak.",
            "en": "🧥 Cool. A jacket or hoodie is recommended.",
        }
    elif temp >= 0:
        msg = {
            "ru": "🧣 Холодно. Тёплая куртка, шарф, шапка.",
            "uz": "🧣 Sovuq. Issiq kurtka, sharf, qalpoq.",
            "en": "🧣 Cold. Warm jacket, scarf, hat.",
        }
    else:
        msg = {
            "ru": "❄️ Морозно. Пуховик, перчатки, шапка обязательно.",
            "uz": "❄️ Qattiq sovuq. Puxovik, qo'lqop, qalpoq shart.",
            "en": "❄️ Freezing. Down jacket, gloves, hat are a must.",
        }
    out = msg.get(lang, msg["ru"])
    if rain:
        rain_msg = {"ru": "\n☔️ Возьми зонт!", "uz": "\n☔️ Soyabon oling!", "en": "\n☔️ Take an umbrella!"}
        out += rain_msg.get(lang, rain_msg["ru"])
    return out


# ------------------------------------------------------------------
# Форматирование
# ------------------------------------------------------------------

def _city_display(city: City, lang: str) -> str:
    if lang == "ru" and city.name_ru:
        return city.name_ru
    if lang == "uz" and city.name_uz:
        return city.name_uz
    return city.name_en


def _ago_minutes(fetched_at: datetime) -> int:
    # ожидаем aware datetime (БД возвращает с tz, кэш-fallback тоже aware)
    now = datetime.now(timezone.utc)
    if fetched_at.tzinfo is None:
        # на всякий случай — но это не должно происходить в нормальном флоу
        fetched_at = fetched_at.replace(tzinfo=timezone.utc)
    delta = now - fetched_at
    return max(0, int(delta.total_seconds() // 60))


def _ago_label(fetched_at: datetime, lang: str) -> str:
    m = _ago_minutes(fetched_at)
    if m == 0:
        return {"ru": "только что", "uz": "hozirgina", "en": "just now"}.get(lang, "just now")
    return {
        "ru": f"обновлено {m} мин назад",
        "uz": f"{m} daqiqa oldin yangilangan",
        "en": f"updated {m} min ago",
    }.get(lang, f"{m} min ago")


def format_current(
    weather: dict, city: City, fetched_at: datetime, lang: str = "ru", units: str = "metric"
) -> str:
    """Форматирует ответ OWM /weather в красивый HTML."""
    # WeatherAPI fallback имеет другую структуру
    if weather.get("__source") == "weatherapi":
        return _format_current_weatherapi(weather, city, fetched_at, lang)

    main = weather.get("main", {})
    w = (weather.get("weather") or [{}])[0]
    wind = weather.get("wind", {})
    sys = weather.get("sys", {})
    clouds = weather.get("clouds", {}).get("all", 0)

    wid = w.get("id", 800)
    icon = emoji_for_owm_id(wid)
    desc = html.escape(desc_for_owm_id(wid, lang))
    unit_t = "°C" if units == "metric" else "°F"
    unit_v = t("weather.unit_ms", lang) if units == "metric" else t("weather.unit_mph", lang)
    unit_km = t("weather.unit_km", lang)

    arrow = wind_arrow(wind.get("deg"))
    name = _city_display(city, lang)

    labels = {
        "ru": {
            "feels": "Ощущается как", "humidity": "Влажность", "pressure": "Давление",
            "wind": "Ветер", "clouds": "Облачность", "visibility": "Видимость",
            "sunrise": "Восход", "sunset": "Закат",
        },
        "uz": {
            "feels": "His etiladi", "humidity": "Namlik", "pressure": "Bosim",
            "wind": "Shamol", "clouds": "Bulutlilik", "visibility": "Ko'rinish",
            "sunrise": "Quyosh chiqishi", "sunset": "Quyosh botishi",
        },
        "en": {
            "feels": "Feels like", "humidity": "Humidity", "pressure": "Pressure",
            "wind": "Wind", "clouds": "Clouds", "visibility": "Visibility",
            "sunrise": "Sunrise", "sunset": "Sunset",
        },
    }.get(lang, {})

    tz_offset = weather.get("timezone", 0)  # OWM: смещение города от UTC в секундах
    def _fmt_local(ts: int) -> str:
        if not ts:
            return "—"
        return datetime.fromtimestamp(ts + tz_offset, tz=timezone.utc).strftime("%H:%M")
    sunrise = _fmt_local(sys.get("sunrise", 0))
    sunset = _fmt_local(sys.get("sunset", 0))
    visibility_km = (weather.get("visibility") or 0) / 1000

    lines = [
        f"{icon} <b>{html.escape(name)}</b>",
        f"<i>{desc.capitalize()}</i>",
        "",
        f"🌡 <b>{main.get('temp', 0):.1f}{unit_t}</b>  ({labels['feels']}: {main.get('feels_like', 0):.1f}{unit_t})",
        f"💧 {labels['humidity']}: <b>{main.get('humidity', 0)}%</b>",
        f"🌬 {labels['wind']}: <b>{wind.get('speed', 0):.1f} {unit_v}</b> {arrow}",
        f"📊 {labels['pressure']}: <b>{main.get('pressure', 0)} hPa</b>",
        f"☁️ {labels['clouds']}: <b>{clouds}%</b>",
        f"👁 {labels['visibility']}: <b>{visibility_km:.1f} {unit_km}</b>",
        f"🌅 {labels['sunrise']}: <b>{sunrise}</b>  🌇 {labels['sunset']}: <b>{sunset}</b>",
        "",
        f"<i>{_ago_label(fetched_at, lang)}</i>",
    ]
    return "\n".join(lines)


def _format_current_weatherapi(weather: dict, city: City, fetched_at: datetime, lang: str) -> str:
    cur = weather.get("current", {})
    cond = cur.get("condition", {})
    name = html.escape(_city_display(city, lang))
    cond_text = html.escape(cond.get("text", "") or "")
    feels_label = t("weather.feels_like_short", lang)
    humidity_label = t("weather.humidity_label", lang)
    wind_label = t("weather.wind_label", lang)
    unit_kmh = t("weather.unit_kmh", lang)
    return (
        f"🌡 <b>{name}</b>\n"
        f"<i>{cond_text}</i>\n\n"
        f"🌡 <b>{cur.get('temp_c', 0):.1f}°C</b> "
        f"({feels_label} {cur.get('feelslike_c', 0):.1f}°C)\n"
        f"💧 {humidity_label}: <b>{cur.get('humidity', 0)}%</b>\n"
        f"🌬 {wind_label}: <b>{cur.get('wind_kph', 0):.1f} {unit_kmh}</b>\n"
        f"\n<i>{_ago_label(fetched_at, lang)} · WeatherAPI</i>"
    )


def format_forecast(
    forecast: dict, city: City, fetched_at: datetime, lang: str = "ru", units: str = "metric"
) -> str:
    """Прогноз 5дн / 3ч → агрегируем по дням (min/max/иконка дня)."""
    items = forecast.get("list", [])
    if not items:
        return t("weather.no_forecast_data", lang, city=_city_display(city, lang))

    # OWM forecast: city.timezone — смещение в секундах от UTC
    tz_offset = (forecast.get("city") or {}).get("timezone", 0)
    def _local_dt(ts: int) -> datetime:
        return datetime.fromtimestamp(ts + tz_offset, tz=timezone.utc)

    by_day: dict[str, list[dict]] = {}
    for it in items:
        key = _local_dt(it["dt"]).strftime("%Y-%m-%d")
        by_day.setdefault(key, []).append(it)

    unit_t = "°C" if units == "metric" else "°F"
    name = html.escape(_city_display(city, lang))
    days_label = {"ru": "Прогноз на 5 дней", "uz": "5 kunlik bashorat", "en": "5-day forecast"}.get(lang, "5-day forecast")

    lines = [f"📅 <b>{days_label} — {name}</b>", ""]

    weekday_names = {
        "ru": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
        "uz": ["Du", "Se", "Cho", "Pa", "Ju", "Sha", "Ya"],
        "en": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    }.get(lang, ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])

    for i, (day_key, day_items) in enumerate(list(by_day.items())[:5]):
        temps = [it["main"]["temp"] for it in day_items]
        tmin, tmax = min(temps), max(temps)
        # выбираем иконку дневного периода (12:00) или среднюю
        midday = min(day_items, key=lambda x: abs(_local_dt(x["dt"]).hour - 13))
        wid = midday.get("weather", [{}])[0].get("id", 800)
        desc = html.escape(desc_for_owm_id(wid, lang))
        icon = emoji_for_owm_id(wid)
        date = datetime.strptime(day_key, "%Y-%m-%d")
        wd = weekday_names[date.weekday()]
        lines.append(
            f"{icon} <b>{wd} {date.strftime('%d.%m')}</b>: "
            f"{tmin:.0f}…{tmax:.0f}{unit_t} <i>{desc}</i>"
        )

    lines.append("")
    lines.append(f"<i>{_ago_label(fetched_at, lang)}</i>")
    return "\n".join(lines)


def format_air(
    air: dict, city: City, fetched_at: datetime, lang: str = "ru"
) -> str:
    items = air.get("list", [])
    if not items:
        return t("weather.no_air_data", lang, city=_city_display(city, lang))
    cur = items[0]
    aqi = cur.get("main", {}).get("aqi", 0)
    components = cur.get("components", {})
    name = html.escape(_city_display(city, lang))
    ugm3 = t("weather.unit_ugm3", lang)

    title = {"ru": "Качество воздуха", "uz": "Havo sifati", "en": "Air quality"}.get(lang, "Air quality")
    lines = [
        f"🌫 <b>{title} — {name}</b>",
        "",
        f"AQI: <b>{aqi_label(aqi, lang)}</b>",
        "",
        f"PM2.5: <b>{components.get('pm2_5', 0):.1f}</b> {ugm3}",
        f"PM10:  <b>{components.get('pm10', 0):.1f}</b> {ugm3}",
        f"NO₂:   <b>{components.get('no2', 0):.1f}</b>",
        f"O₃:    <b>{components.get('o3', 0):.1f}</b>",
        f"SO₂:   <b>{components.get('so2', 0):.1f}</b>",
        f"CO:    <b>{components.get('co', 0):.1f}</b>",
        "",
        f"<i>{_ago_label(fetched_at, lang)}</i>",
    ]
    return "\n".join(lines)


