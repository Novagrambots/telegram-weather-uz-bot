# Weather Telegram Bot

Telegram-бот прогноза погоды для городов Узбекистана и всего мира.
Мультиязычность: ru / uz / en.

## Возможности

- Текущая погода по городу или геолокации
- Прогноз на 5 дней / на завтра (по 3-часовым интервалам)
- Качество воздуха (AQI: PM2.5, PM10, CO, NO2, O3)
- Рекомендации по одежде на основе температуры и осадков
- Избранные города (до 10 на юзера)
- Inline-режим (`@bot tashkent`)
- Карта города по координатам

## Стек

- Python 3.12 + aiogram 3
- SQLAlchemy 2.0 async + asyncpg
- PostgreSQL 16 + Alembic
- httpx (OpenWeatherMap + WeatherAPI fallback)
- Docker Compose

## Быстрый старт

```bash
cp .env.example .env
# заполни .env: BOT_TOKEN, OWM_API_KEY, DB_PASSWORD, ADMIN_IDS

docker compose up -d
```

## Структура

```
bot/
├── main.py                 # точка входа, polling, фоновые задачи
├── config.py               # настройки из .env (pydantic-settings)
├── i18n.py                 # переводы ru/uz/en
├── emojis.py               # премиум-эмодзи Telegram
├── database/
│   ├── models.py           # User, City, WeatherCache, FavoriteCity, WeatherRequest
│   └── crud.py             # CRUD + очистка устаревших данных
├── handlers/
│   ├── start.py            # /start, меню, профиль, язык
│   ├── admin.py            # /admin: статистика, каналы, рассылка
│   └── weather.py          # /weather, /forecast, /air, /clothes, /favorites, inline
├── middlewares/
│   ├── subscription.py     # обязательная подписка на каналы
│   └── rate_limit.py       # 5 запросов/мин на юзера
├── keyboards/
│   ├── inline.py           # главное меню, подписка, выбор языка
│   ├── admin.py            # админские клавиатуры
│   └── weather.py          # меню погоды, города UZ, избранные, единицы
├── services/
│   ├── weather.py          # высокоуровневый сервис: кэш, форматирование, fallback
│   ├── openweathermap.py   # клиент OWM API
│   ├── weatherapi.py       # клиент WeatherAPI.com (резервный)
│   ├── icons.py            # эмодзи и локализованные описания погоды
│   └── seeder.py           # сидинг областных центров Узбекистана
└── utils/
    └── commands.py         # регистрация меню команд Telegram

alembic/versions/           # миграции БД
seeds/uz_cities.json        # 14 областных центров UZ
```

## Команды

| Команда | Описание |
|---------|----------|
| `/start`, `/menu` | Главное меню |
| `/weather <город>` | Текущая погода |
| `/forecast <город>` | Прогноз на 5 дней |
| `/tomorrow <город>` | Прогноз на завтра |
| `/location` | Погода по геолокации |
| `/favorites` | Избранные города |
| `/clothes <город>` | Рекомендации по одежде |
| `/air <город>` | Качество воздуха |
| `/map <город>` | Карта на координатах |
| `/units metric/imperial` | Единицы измерения |
| `/profile` | Профиль |
| `/language` | Смена языка |
| `/stats` (admin) | Статистика бота |
| `/broadcast` (admin) | Рассылка |

## Переменные окружения

| Переменная | Обязательная | Описание |
|-----------|-------------|---------|
| `BOT_TOKEN` | да | Токен от @BotFather |
| `OWM_API_KEY` | да | Ключ OpenWeatherMap (free tier 1000 req/day) |
| `DB_PASSWORD` | да | Пароль PostgreSQL |
| `ADMIN_IDS` | да | Telegram ID админов через запятую |
| `WEATHERAPI_KEY` | нет | Резервный провайдер при сбое OWM |
| `TIMEZONE` | нет | По умолчанию `Asia/Tashkent` |
| `CACHE_CURRENT_TTL_MIN` | нет | TTL кэша текущей погоды (10 мин) |
| `CACHE_FORECAST_TTL_MIN` | нет | TTL кэша прогноза (60 мин) |

## Кэширование

Все ответы погоды кэшируются в `weather_cache` по `(city_id, type)`:
- текущая погода — 10 минут
- прогноз 5 дней — 60 минут
- качество воздуха — 30 минут

Просроченные записи + старые логи запросов чистятся фоновой задачей раз в час.

## Источники данных

- **OpenWeatherMap** (основной): `/data/2.5/weather`, `/forecast`, `/air_pollution`, `/geo/1.0/direct|reverse`
- **WeatherAPI.com** (fallback): `/v1/current.json`, `/v1/forecast.json`
