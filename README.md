# bot_4_weather_uz

Telegram-бот прогноза погоды через OpenWeatherMap API.
Мультиязычность: ru / uz / en.

## Стек

- Python 3.11 + aiogram 3.4
- SQLAlchemy 2.0 async + asyncpg
- PostgreSQL 16
- httpx (запросы к OWM API)
- Local Bot API (порт 8090)
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
├── main.py              # entrypoint
├── config.py            # настройки из .env
├── i18n.py              # переводы ru/uz/en
├── emojis.py            # премиум-эмодзи
├── database/
│   ├── models.py        # User, Channel + TODO доменные
│   └── crud.py          # CRUD функции
├── handlers/
│   ├── start.py         # /start, меню, профиль, язык
│   ├── admin.py         # /admin: статистика, каналы, рассылка
│   └── __todo_weather.py  # TODO: погодные хендлеры
├── middlewares/
│   ├── subscription.py  # обязательная подписка
│   └── rate_limit.py    # 5 запросов/мин
├── keyboards/
│   ├── inline.py        # юзерские кнопки
│   └── admin.py         # админские кнопки
├── services/
│   └── __todo_weather.py  # TODO: OWM сервис
└── utils/
    └── commands.py      # меню команд Telegram
```

## Переменные окружения

| Переменная | Обязательная | Описание |
|-----------|-------------|---------|
| BOT_TOKEN | да | Токен от @BotFather |
| OWM_API_KEY | да | Ключ OpenWeatherMap |
| DB_PASSWORD | да | Пароль PostgreSQL |
| ADMIN_IDS | да | Telegram ID админов (через запятую) |
| WEATHERAPI_KEY | нет | Резервный провайдер |
| API_ID / API_HASH | нет | Для Local Bot API (файлы >50МБ) |
