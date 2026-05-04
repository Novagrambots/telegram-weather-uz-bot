"""Иконки для погодных кодов OWM, направления ветра и AQI."""
from __future__ import annotations

# OWM weather id → emoji
# https://openweathermap.org/weather-conditions
def emoji_for_owm_id(weather_id: int) -> str:
    if 200 <= weather_id < 300:
        return "⛈"
    if 300 <= weather_id < 400:
        return "🌦"
    if 500 <= weather_id < 600:
        return "🌧"
    if 600 <= weather_id < 700:
        return "❄️"
    if 700 <= weather_id < 800:
        return "🌫"
    if weather_id == 800:
        return "☀️"
    if weather_id == 801:
        return "🌤"
    if weather_id == 802:
        return "⛅"
    if weather_id in (803, 804):
        return "☁️"
    return "🌡"


def emoji_for_owm_icon(icon: str | None) -> str:
    """OWM icon code (например '01d', '10n') → emoji"""
    if not icon:
        return "🌡"
    base = icon[:2]
    return {
        "01": "☀️",
        "02": "🌤",
        "03": "⛅",
        "04": "☁️",
        "09": "🌧",
        "10": "🌦",
        "11": "⛈",
        "13": "❄️",
        "50": "🌫",
    }.get(base, "🌡")


_WIND_ARROWS = ["↑", "↗", "→", "↘", "↓", "↙", "←", "↖"]


def wind_arrow(deg: float | int | None) -> str:
    """Направление ветра в градусах → стрелка"""
    if deg is None:
        return ""
    idx = int((deg % 360) / 45 + 0.5) % 8
    return _WIND_ARROWS[idx]


def aqi_label(aqi: int, lang: str = "ru") -> str:
    """AQI 1..5 (OWM шкала) → описание + emoji"""
    table = {
        1: ("🟢", {"ru": "Отличный", "uz": "Ajoyib", "en": "Good"}),
        2: ("🟡", {"ru": "Хороший", "uz": "Yaxshi", "en": "Fair"}),
        3: ("🟠", {"ru": "Умеренный", "uz": "O'rta", "en": "Moderate"}),
        4: ("🔴", {"ru": "Плохой", "uz": "Yomon", "en": "Poor"}),
        5: ("🟣", {"ru": "Опасный", "uz": "Xavfli", "en": "Very Poor"}),
    }
    emoji, names = table.get(aqi, ("⚪", {"ru": "—", "uz": "—", "en": "—"}))
    return f"{emoji} {names.get(lang, names['ru'])}"


def owm_icon_url(icon: str) -> str:
    """URL картинки OWM (для отправки фото)."""
    return f"https://openweathermap.org/img/wn/{icon}@2x.png"


# Локализованные описания по OWM weather id.
# Используем вместо data["weather"][0]["description"] из OWM, чтобы текст
# не зависел от lang первого юзера, чей запрос попал в общий WeatherCache.
_DESC_TABLE: dict[int, dict[str, str]] = {
    # 2xx — гроза
    200: {"ru": "гроза с лёгким дождём", "uz": "yengil yomg'irli momaqaldiroq", "en": "thunderstorm with light rain"},
    201: {"ru": "гроза с дождём", "uz": "yomg'irli momaqaldiroq", "en": "thunderstorm with rain"},
    202: {"ru": "гроза с сильным дождём", "uz": "kuchli yomg'irli momaqaldiroq", "en": "thunderstorm with heavy rain"},
    210: {"ru": "лёгкая гроза", "uz": "yengil momaqaldiroq", "en": "light thunderstorm"},
    211: {"ru": "гроза", "uz": "momaqaldiroq", "en": "thunderstorm"},
    212: {"ru": "сильная гроза", "uz": "kuchli momaqaldiroq", "en": "heavy thunderstorm"},
    221: {"ru": "шквальная гроза", "uz": "shamolli momaqaldiroq", "en": "ragged thunderstorm"},
    230: {"ru": "гроза с моросью", "uz": "mayda yomg'irli momaqaldiroq", "en": "thunderstorm with light drizzle"},
    231: {"ru": "гроза с моросью", "uz": "mayda yomg'irli momaqaldiroq", "en": "thunderstorm with drizzle"},
    232: {"ru": "гроза с сильной моросью", "uz": "kuchli mayda yomg'irli momaqaldiroq", "en": "thunderstorm with heavy drizzle"},
    # 3xx — морось
    300: {"ru": "лёгкая морось", "uz": "yengil mayda yomg'ir", "en": "light drizzle"},
    301: {"ru": "морось", "uz": "mayda yomg'ir", "en": "drizzle"},
    302: {"ru": "сильная морось", "uz": "kuchli mayda yomg'ir", "en": "heavy drizzle"},
    310: {"ru": "морось с дождём", "uz": "yomg'irli mayda yomg'ir", "en": "light intensity drizzle rain"},
    311: {"ru": "морось с дождём", "uz": "yomg'irli mayda yomg'ir", "en": "drizzle rain"},
    312: {"ru": "сильная морось с дождём", "uz": "kuchli mayda yomg'ir", "en": "heavy intensity drizzle rain"},
    313: {"ru": "ливневая морось", "uz": "jala mayda yomg'iri", "en": "shower rain and drizzle"},
    314: {"ru": "сильная ливневая морось", "uz": "kuchli jala", "en": "heavy shower rain and drizzle"},
    321: {"ru": "ливневая морось", "uz": "jala", "en": "shower drizzle"},
    # 5xx — дождь
    500: {"ru": "небольшой дождь", "uz": "kichik yomg'ir", "en": "light rain"},
    501: {"ru": "дождь", "uz": "yomg'ir", "en": "moderate rain"},
    502: {"ru": "сильный дождь", "uz": "kuchli yomg'ir", "en": "heavy rain"},
    503: {"ru": "очень сильный дождь", "uz": "juda kuchli yomg'ir", "en": "very heavy rain"},
    504: {"ru": "ливень", "uz": "jala", "en": "extreme rain"},
    511: {"ru": "ледяной дождь", "uz": "muzli yomg'ir", "en": "freezing rain"},
    520: {"ru": "лёгкий ливень", "uz": "yengil jala", "en": "light shower rain"},
    521: {"ru": "ливень", "uz": "jala", "en": "shower rain"},
    522: {"ru": "сильный ливень", "uz": "kuchli jala", "en": "heavy shower rain"},
    531: {"ru": "ливневый дождь", "uz": "jala yomg'iri", "en": "ragged shower rain"},
    # 6xx — снег
    600: {"ru": "небольшой снег", "uz": "kichik qor", "en": "light snow"},
    601: {"ru": "снег", "uz": "qor", "en": "snow"},
    602: {"ru": "сильный снегопад", "uz": "kuchli qor", "en": "heavy snow"},
    611: {"ru": "мокрый снег", "uz": "ho'l qor", "en": "sleet"},
    612: {"ru": "лёгкий мокрый снег", "uz": "yengil ho'l qor", "en": "light sleet shower"},
    613: {"ru": "ливневый мокрый снег", "uz": "jala ho'l qor", "en": "sleet shower"},
    615: {"ru": "дождь со снегом", "uz": "qorli yomg'ir", "en": "light rain and snow"},
    616: {"ru": "дождь со снегом", "uz": "qorli yomg'ir", "en": "rain and snow"},
    620: {"ru": "лёгкий снегопад", "uz": "yengil qor", "en": "light shower snow"},
    621: {"ru": "снегопад", "uz": "qor yog'ishi", "en": "shower snow"},
    622: {"ru": "сильный снегопад", "uz": "kuchli qor", "en": "heavy shower snow"},
    # 7xx — атмосферные
    701: {"ru": "туман", "uz": "tuman", "en": "mist"},
    711: {"ru": "дым", "uz": "tutun", "en": "smoke"},
    721: {"ru": "дымка", "uz": "tuman", "en": "haze"},
    731: {"ru": "пыльные вихри", "uz": "chang", "en": "sand/dust whirls"},
    741: {"ru": "туман", "uz": "qalin tuman", "en": "fog"},
    751: {"ru": "песок", "uz": "qum", "en": "sand"},
    761: {"ru": "пыль", "uz": "chang", "en": "dust"},
    762: {"ru": "вулканический пепел", "uz": "vulqon kuli", "en": "volcanic ash"},
    771: {"ru": "шквал", "uz": "shamol shiddati", "en": "squalls"},
    781: {"ru": "торнадо", "uz": "tornado", "en": "tornado"},
    # 8xx — облачность
    800: {"ru": "ясно", "uz": "ochiq", "en": "clear sky"},
    801: {"ru": "небольшая облачность", "uz": "ozgina bulutli", "en": "few clouds"},
    802: {"ru": "переменная облачность", "uz": "qisman bulutli", "en": "scattered clouds"},
    803: {"ru": "облачно", "uz": "bulutli", "en": "broken clouds"},
    804: {"ru": "пасмурно", "uz": "qoplangan", "en": "overcast clouds"},
}


def desc_for_owm_id(weather_id: int, lang: str = "ru") -> str:
    """Локализованное описание погоды по OWM weather id (не зависит от языка кэша)."""
    entry = _DESC_TABLE.get(weather_id)
    if not entry:
        return ""
    return entry.get(lang) or entry.get("ru", "")
