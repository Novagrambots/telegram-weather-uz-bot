"""Сидер базовых городов Узбекистана из seeds/uz_cities.json"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import City

logger = logging.getLogger(__name__)

SEED_FILE = Path(__file__).resolve().parents[2] / "seeds" / "uz_cities.json"


async def seed_uz_cities(session: AsyncSession) -> int:
    """Вставляет города UZ в БД (ON CONFLICT DO NOTHING по name_en).
    Возвращает кол-во новых записей.
    """
    if not SEED_FILE.exists():
        logger.warning("Seed-файл не найден: %s", SEED_FILE)
        return 0

    try:
        data = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error("Не удалось прочитать seed: %s", e)
        return 0

    inserted = 0
    for entry in data:
        try:
            stmt = pg_insert(City).values(
                name_ru=entry.get("name_ru"),
                name_uz=entry.get("name_uz"),
                name_en=entry["name_en"],
                lat=float(entry["lat"]),
                lon=float(entry["lon"]),
                owm_id=entry.get("owm_id"),
                country_code=entry.get("country_code", "UZ"),
                is_uz=(entry.get("country_code", "UZ").upper() == "UZ"),
            ).on_conflict_do_nothing(index_elements=["name_en"])
            res = await session.execute(stmt)
            if res.rowcount:
                inserted += 1
        except Exception as e:
            logger.warning("Не удалось засеять %s: %s", entry.get("name_en"), e)
    await session.commit()
    logger.info("Seed UZ cities: добавлено %d новых записей", inserted)
    return inserted
