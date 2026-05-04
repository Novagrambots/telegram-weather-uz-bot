"""Модели базы данных"""
import enum
from datetime import datetime

from sqlalchemy import (
    BigInteger, DateTime, Enum, Float, ForeignKey, Index, Integer,
    String, UniqueConstraint, func, Boolean,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


class UnitsEnum(str, enum.Enum):
    metric = "metric"
    imperial = "imperial"


class CacheTypeEnum(str, enum.Enum):
    current = "current"
    forecast = "forecast"
    air = "air"


class WeatherSourceEnum(str, enum.Enum):
    owm = "owm"
    weatherapi = "weatherapi"
    cache = "cache"


class User(Base):
    """Пользователь бота"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    language_code: Mapped[str] = mapped_column(String(5), default="ru")
    is_blocked: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    units: Mapped[UnitsEnum] = mapped_column(
        Enum(UnitsEnum), default=UnitsEnum.metric
    )
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Tashkent")

    def __repr__(self) -> str:
        return f"<User {self.telegram_id} ({self.username})>"


class Channel(Base):
    """Канал/группа для обязательной подписки"""
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    channel_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    title: Mapped[str] = mapped_column(String(255))
    invite_link: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Channel {self.channel_id} ({self.title})>"


class City(Base):
    """Город — справочник + динамическое пополнение через геокодинг"""
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name_ru: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    name_uz: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    name_en: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    country_code: Mapped[str] = mapped_column(String(4), default="UZ")
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    owm_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    is_uz: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<City {self.name_en} ({self.lat}, {self.lon})>"


class WeatherCache(Base):
    """Кэш ответов API погоды"""
    __tablename__ = "weather_cache"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id", ondelete="CASCADE"))
    type: Mapped[CacheTypeEnum] = mapped_column(Enum(CacheTypeEnum))
    data: Mapped[dict] = mapped_column(JSONB)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        Index("ix_weather_cache_lookup", "city_id", "type", "expires_at"),
        UniqueConstraint("city_id", "type", name="uq_weather_cache_city_type"),
    )


class FavoriteCity(Base):
    """Избранные города юзера"""
    __tablename__ = "favorite_cities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id", ondelete="CASCADE"))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("user_id", "city_id", name="uq_fav_user_city"),
    )


class WeatherRequest(Base):
    """Лог запросов погоды (для аналитики)"""
    __tablename__ = "weather_requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id", ondelete="CASCADE"))
    type: Mapped[str] = mapped_column(String(32))
    source: Mapped[WeatherSourceEnum] = mapped_column(Enum(WeatherSourceEnum))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
