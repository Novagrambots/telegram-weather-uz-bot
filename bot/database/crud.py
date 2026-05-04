"""CRUD операции с базой данных"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import and_, delete, func as sa_func, or_, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import (
    CacheTypeEnum, Channel, City, FavoriteCity, User,
    WeatherCache, WeatherRequest, WeatherSourceEnum,
)


# === Пользователи ===

async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    username: str | None,
    first_name: str | None,
    language_code: str | None = None,
) -> User:
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            language_code=language_code or "ru",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    return user


async def get_user_by_tg(session: AsyncSession, telegram_id: int) -> User | None:
    res = await session.execute(select(User).where(User.telegram_id == telegram_id))
    return res.scalar_one_or_none()


async def get_user_language(session: AsyncSession, telegram_id: int) -> str:
    result = await session.execute(
        select(User.language_code).where(User.telegram_id == telegram_id)
    )
    lang = result.scalar_one_or_none()
    return lang or "ru"


async def update_user_language(
    session: AsyncSession, telegram_id: int, language: str
) -> None:
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    if user:
        user.language_code = language
        await session.commit()


async def update_user_blocked(
    session: AsyncSession, telegram_id: int, is_blocked: bool
) -> None:
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    if user:
        user.is_blocked = is_blocked
        await session.commit()


async def update_user_units(session: AsyncSession, telegram_id: int, units: str) -> None:
    user = await get_user_by_tg(session, telegram_id)
    if user:
        from bot.database.models import UnitsEnum
        user.units = UnitsEnum(units)
        await session.commit()


# === Каналы ===

async def get_active_channels(session: AsyncSession) -> list[Channel]:
    result = await session.execute(select(Channel))
    return list(result.scalars().all())


async def add_channel(
    session: AsyncSession, channel_id: int, title: str, invite_link: str
) -> Channel:
    result = await session.execute(
        select(Channel).where(Channel.channel_id == channel_id)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise ValueError(f"Канал {channel_id} уже добавлен")
    channel = Channel(channel_id=channel_id, title=title, invite_link=invite_link)
    session.add(channel)
    await session.commit()
    await session.refresh(channel)
    return channel


async def remove_channel(session: AsyncSession, channel_id: int) -> bool:
    result = await session.execute(
        select(Channel).where(Channel.channel_id == channel_id)
    )
    channel = result.scalar_one_or_none()
    if not channel:
        return False
    await session.delete(channel)
    await session.commit()
    return True


# === Статистика ===

async def get_user_stats(session: AsyncSession) -> dict:
    total = await session.execute(select(sa_func.count(User.id)))
    total_users = total.scalar() or 0

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_result = await session.execute(
        select(sa_func.count(User.id)).where(User.created_at >= today)
    )
    today_users = today_result.scalar() or 0

    channels = await session.execute(select(sa_func.count(Channel.id)))
    total_channels = channels.scalar() or 0

    requests = await session.execute(select(sa_func.count(WeatherRequest.id)))
    total_requests = requests.scalar() or 0

    return {
        "total_users": total_users,
        "today_users": today_users,
        "total_channels": total_channels,
        "total_requests": total_requests,
    }


async def get_all_user_ids(session: AsyncSession) -> list[int]:
    result = await session.execute(
        select(User.telegram_id).where(User.is_blocked == False)  # noqa: E712
    )
    return [row[0] for row in result.all()]


# === Города ===

def _normalize(s: str) -> str:
    return (s or "").strip().lower().replace("'", "").replace("`", "").replace("ʻ", "")


async def find_city_by_name(session: AsyncSession, query: str) -> City | None:
    """Поиск по name_ru/uz/en (case-insensitive + нормализация апострофов в БД)."""
    if not query:
        return None
    q = query.strip()
    qn = _normalize(q)
    ql = q.lower()

    # быстрый путь — точное совпадение
    res = await session.execute(
        select(City).where(
            or_(
                sa_func.lower(City.name_ru) == ql,
                sa_func.lower(City.name_uz) == ql,
                sa_func.lower(City.name_en) == ql,
            )
        )
    )
    city = res.scalar_one_or_none()
    if city:
        return city

    # нормализуем апострофы в БД через translate(): убираем ' ` ʻ
    apos = "'`ʻ"
    res2 = await session.execute(
        select(City).where(
            or_(
                sa_func.translate(sa_func.lower(sa_func.coalesce(City.name_ru, "")), apos, "") == qn,
                sa_func.translate(sa_func.lower(sa_func.coalesce(City.name_uz, "")), apos, "") == qn,
                sa_func.translate(sa_func.lower(sa_func.coalesce(City.name_en, "")), apos, "") == qn,
            )
        ).limit(1)
    )
    return res2.scalar_one_or_none()


async def get_city_by_id(session: AsyncSession, city_id: int) -> City | None:
    res = await session.execute(select(City).where(City.id == city_id))
    return res.scalar_one_or_none()


async def get_or_create_city(
    session: AsyncSession,
    name_en: str,
    lat: float,
    lon: float,
    name_ru: str | None = None,
    name_uz: str | None = None,
    country_code: str = "UZ",
    owm_id: int | None = None,
) -> City:
    res = await session.execute(
        select(City).where(sa_func.lower(City.name_en) == name_en.lower())
    )
    city = res.scalar_one_or_none()
    if city:
        return city
    is_uz = country_code.upper() == "UZ"
    city = City(
        name_en=name_en,
        name_ru=name_ru,
        name_uz=name_uz,
        lat=lat,
        lon=lon,
        country_code=country_code,
        owm_id=owm_id,
        is_uz=is_uz,
    )
    session.add(city)
    await session.commit()
    await session.refresh(city)
    return city


async def list_uz_cities(session: AsyncSession, limit: int = 50) -> list[City]:
    res = await session.execute(
        select(City).where(City.is_uz == True).order_by(City.name_ru).limit(limit)  # noqa
    )
    return list(res.scalars().all())


async def find_nearest_city(
    session: AsyncSession, lat: float, lon: float, only_uz: bool = False,
) -> City | None:
    """Ближайший город по евклидовому расстоянию (вычисление на стороне БД).
    only_uz=True ограничивает выбор городами Узбекистана."""
    dist = (City.lat - lat) * (City.lat - lat) + (City.lon - lon) * (City.lon - lon)
    stmt = select(City).order_by(dist).limit(1)
    if only_uz:
        stmt = select(City).where(City.is_uz == True).order_by(dist).limit(1)  # noqa: E712
    res = await session.execute(stmt)
    return res.scalar_one_or_none()


# === Кэш погоды ===

async def get_cache(
    session: AsyncSession, city_id: int, type_: CacheTypeEnum
) -> WeatherCache | None:
    now = datetime.now(timezone.utc)
    res = await session.execute(
        select(WeatherCache)
        .where(
            and_(
                WeatherCache.city_id == city_id,
                WeatherCache.type == type_,
                WeatherCache.expires_at > now,
            )
        )
        .order_by(WeatherCache.fetched_at.desc())
        .limit(1)
    )
    return res.scalar_one_or_none()


async def set_cache(
    session: AsyncSession,
    city_id: int,
    type_: CacheTypeEnum,
    data: dict,
    ttl_minutes: int,
) -> WeatherCache:
    """UPSERT кэша по уникальному ключу (city_id, type) — устраняет race condition."""
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=ttl_minutes)
    stmt = pg_insert(WeatherCache).values(
        city_id=city_id,
        type=type_,
        data=data,
        fetched_at=now,
        expires_at=expires_at,
    )
    stmt = stmt.on_conflict_do_update(
        constraint="uq_weather_cache_city_type",
        set_={
            "data": stmt.excluded.data,
            "fetched_at": stmt.excluded.fetched_at,
            "expires_at": stmt.excluded.expires_at,
        },
    )
    await session.execute(stmt)
    await session.commit()
    # читаем обратно, чтобы вернуть актуальную запись
    res = await session.execute(
        select(WeatherCache).where(
            and_(WeatherCache.city_id == city_id, WeatherCache.type == type_)
        )
    )
    return res.scalar_one()


# === Избранные ===

async def add_favorite(session: AsyncSession, user_id: int, city_id: int) -> bool:
    res = await session.execute(
        select(FavoriteCity).where(
            and_(FavoriteCity.user_id == user_id, FavoriteCity.city_id == city_id)
        )
    )
    if res.scalar_one_or_none():
        return False
    fav = FavoriteCity(user_id=user_id, city_id=city_id)
    session.add(fav)
    await session.commit()
    return True


async def list_favorites(session: AsyncSession, user_id: int) -> list[City]:
    res = await session.execute(
        select(City)
        .join(FavoriteCity, FavoriteCity.city_id == City.id)
        .where(FavoriteCity.user_id == user_id)
        .order_by(FavoriteCity.sort_order, FavoriteCity.added_at)
    )
    return list(res.scalars().all())


async def remove_favorite(session: AsyncSession, user_id: int, city_id: int) -> bool:
    res = await session.execute(
        delete(FavoriteCity).where(
            and_(FavoriteCity.user_id == user_id, FavoriteCity.city_id == city_id)
        )
    )
    await session.commit()
    return (res.rowcount or 0) > 0


# === Лог запросов ===

async def log_request(
    session: AsyncSession,
    user_id: int,
    city_id: int,
    type_: str,
    source: WeatherSourceEnum,
) -> None:
    req = WeatherRequest(
        user_id=user_id, city_id=city_id, type=type_, source=source,
    )
    session.add(req)
    await session.commit()


# === Очистка мусора ===

async def cleanup_expired_cache(session: AsyncSession) -> int:
    """Удаляет просроченные записи WeatherCache. Возвращает число удалённых строк."""
    res = await session.execute(
        delete(WeatherCache).where(WeatherCache.expires_at < datetime.now(timezone.utc))
    )
    await session.commit()
    return res.rowcount or 0


async def cleanup_old_requests(session: AsyncSession, days: int = 30) -> int:
    """Удаляет лог-записи WeatherRequest старше N дней."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    res = await session.execute(
        delete(WeatherRequest).where(WeatherRequest.created_at < cutoff)
    )
    await session.commit()
    return res.rowcount or 0


async def cleanup_orphan_cities(session: AsyncSession, days: int = 90) -> int:
    """Удаляет не-UZ города без избранных и без запросов за N дней."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    # подзапрос: id городов, у которых есть свежие запросы или избранное
    keep = (
        select(City.id)
        .outerjoin(FavoriteCity, FavoriteCity.city_id == City.id)
        .outerjoin(
            WeatherRequest,
            and_(WeatherRequest.city_id == City.id, WeatherRequest.created_at >= cutoff),
        )
        .where(
            (City.is_uz.is_(True))
            | (FavoriteCity.id.is_not(None))
            | (WeatherRequest.id.is_not(None))
        )
    )
    res = await session.execute(
        delete(City).where(City.id.notin_(keep))
    )
    await session.commit()
    return res.rowcount or 0
