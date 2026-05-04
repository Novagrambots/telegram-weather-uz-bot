"""init weather schema

Revision ID: 0001_init_weather
Revises:
Create Date: 2026-05-04
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_init_weather"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # users
    units_enum = sa.Enum("metric", "imperial", name="unitsenum")
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False, unique=True),
        sa.Column("username", sa.String(255), nullable=True),
        sa.Column("first_name", sa.String(255), nullable=True),
        sa.Column("language_code", sa.String(5), server_default="ru"),
        sa.Column("is_blocked", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("units", units_enum, server_default="metric"),
        sa.Column("timezone", sa.String(64), server_default="Asia/Tashkent"),
    )
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"], unique=True)

    # channels
    op.create_table(
        "channels",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("channel_id", sa.BigInteger(), nullable=False, unique=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("invite_link", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # cities
    op.create_table(
        "cities",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name_ru", sa.String(128), nullable=True),
        sa.Column("name_uz", sa.String(128), nullable=True),
        sa.Column("name_en", sa.String(128), nullable=False, unique=True),
        sa.Column("country_code", sa.String(4), server_default="UZ"),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lon", sa.Float(), nullable=False),
        sa.Column("owm_id", sa.BigInteger(), nullable=True),
        sa.Column("is_uz", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_cities_name_ru", "cities", ["name_ru"])
    op.create_index("ix_cities_name_uz", "cities", ["name_uz"])
    op.create_index("ix_cities_name_en", "cities", ["name_en"])

    # weather_cache
    cache_type = sa.Enum("current", "forecast", "onecall", "air", name="cachetypeenum")
    op.create_table(
        "weather_cache",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("city_id", sa.Integer(), sa.ForeignKey("cities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", cache_type, nullable=False),
        sa.Column("data", postgresql.JSONB(), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_weather_cache_lookup", "weather_cache", ["city_id", "type", "expires_at"])

    # favorite_cities
    op.create_table(
        "favorite_cities",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("city_id", sa.Integer(), sa.ForeignKey("cities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0"),
        sa.Column("added_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "city_id", name="uq_fav_user_city"),
    )

    # daily_subscribers
    op.create_table(
        "daily_subscribers",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("time_local", sa.Time(), server_default="07:30"),
        sa.Column("city_ids", postgresql.ARRAY(sa.Integer()), server_default="{}"),
        sa.Column("include_all_favorites", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("last_sent_at", sa.DateTime(timezone=True), nullable=True),
    )

    # alert_subscriptions
    op.create_table(
        "alert_subscriptions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("city_id", sa.Integer(), sa.ForeignKey("cities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("last_alert_id", sa.String(128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "city_id", name="uq_alert_user_city"),
    )

    # weather_requests
    source_enum = sa.Enum("owm", "weatherapi", "cache", name="weathersourceenum")
    op.create_table(
        "weather_requests",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("city_id", sa.Integer(), sa.ForeignKey("cities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.String(32), nullable=False),
        sa.Column("source", source_enum, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("weather_requests")
    op.drop_table("alert_subscriptions")
    op.drop_table("daily_subscribers")
    op.drop_table("favorite_cities")
    op.drop_index("ix_weather_cache_lookup", table_name="weather_cache")
    op.drop_table("weather_cache")
    op.drop_index("ix_cities_name_en", table_name="cities")
    op.drop_index("ix_cities_name_uz", table_name="cities")
    op.drop_index("ix_cities_name_ru", table_name="cities")
    op.drop_table("cities")
    op.drop_table("channels")
    op.drop_index("ix_users_telegram_id", table_name="users")
    op.drop_table("users")
    sa.Enum(name="weathersourceenum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="cachetypeenum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="unitsenum").drop(op.get_bind(), checkfirst=True)
