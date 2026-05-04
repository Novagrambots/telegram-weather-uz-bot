"""Точка входа — запуск бота погоды"""
import asyncio
import logging
import os
import sys
import time

# uvloop ускоряет asyncio в 2-4 раза (не работает на Windows!)
try:
    import uvloop
    uvloop.install()
except ImportError:
    pass

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import settings

# настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# флаг-файл для crash recovery
CRASH_FLAG = ".crash_flag"


async def main() -> None:
    """Инициализация и запуск бота"""
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # подключаем хэндлеры (порядок важен — domain последним!)
    from bot.handlers import start, admin, weather

    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(weather.router)

    # подключаем мидлвари
    from bot.middlewares.rate_limit import RateLimitMiddleware
    from bot.middlewares.subscription import SubscriptionMiddleware

    dp.message.middleware(RateLimitMiddleware())
    dp.message.middleware(SubscriptionMiddleware())
    dp.callback_query.middleware(SubscriptionMiddleware())

    # фоновая задача: очистка памяти каждые 5 минут
    async def _background_cleanup() -> None:
        from bot.middlewares.rate_limit import cleanup_stale_entries
        while True:
            await asyncio.sleep(300)
            removed = cleanup_stale_entries()
            if removed:
                logger.info("Фоновая очистка: удалено %d записей rate limit", removed)

    # фоновая задача: очистка БД-мусора раз в час
    async def _db_cleanup() -> None:
        from bot.database import async_session
        from bot.database.crud import (
            cleanup_expired_cache, cleanup_old_requests, cleanup_orphan_cities,
        )
        # ждём минуту после старта чтобы не нагружать запуск
        await asyncio.sleep(60)
        while True:
            try:
                async with async_session() as session:
                    cache = await cleanup_expired_cache(session)
                    reqs = await cleanup_old_requests(session, days=30)
                    cities = await cleanup_orphan_cities(session, days=90)
                if cache or reqs or cities:
                    logger.info(
                        "DB-очистка: weather_cache=%d, weather_requests=%d, cities=%d",
                        cache, reqs, cities,
                    )
            except Exception as e:
                logger.warning("DB-очистка упала: %s", e)
            await asyncio.sleep(3600)

    @dp.startup()
    async def on_startup() -> None:
        # создаём таблицы в БД
        from bot.database import engine, async_session
        from bot.database.models import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Таблицы БД созданы")

        # сидим UZ-города
        from bot.services.seeder import seed_uz_cities
        async with async_session() as session:
            inserted = await seed_uz_cities(session)
        logger.info("UZ cities seeded: %d new rows", inserted)

        # проверяем crash recovery
        if os.path.exists(CRASH_FLAG):
            logger.warning("Обнаружен crash-flag — предыдущий запуск завершился аварийно")
            os.remove(CRASH_FLAG)

        with open(CRASH_FLAG, "w") as f:
            f.write("running")

        # запускаем фоновые очистки
        asyncio.create_task(_background_cleanup())
        asyncio.create_task(_db_cleanup())
        logger.info("Фоновые очистки запущены: rate-limit (5 мин), БД (1 ч)")


        bot_info = await bot.get_me()
        logger.info(f"Бот @{bot_info.username} запущен!")

        # ставим дефолтное меню команд
        from bot.utils.commands import set_default_commands
        await set_default_commands(bot)
        logger.info("Дефолтное меню команд установлено")

    @dp.shutdown()
    async def on_shutdown() -> None:
        # закрываем httpx-клиенты погодных API
        try:
            from bot.services.openweathermap import owm_client
            from bot.services.weatherapi import weatherapi_client
            await owm_client.close()
            await weatherapi_client.close()
        except Exception as e:
            logger.warning("Ошибка закрытия weather-клиентов: %s", e)

        if os.path.exists(CRASH_FLAG):
            os.remove(CRASH_FLAG)
        logger.info("Бот остановлен")

    # запускаем polling
    try:
        logger.info("Запуск polling...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
