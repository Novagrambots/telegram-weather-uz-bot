"""cache UNIQUE (city_id,type), digest atomic last_sent_date, alert sent_alert_ids

Revision ID: 0002_cache_unique_digest_atomic_alert_ids
Revises: 0001_init_weather
Create Date: 2026-05-04
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0002_cache_unique_digest_atomic_alert_ids"
down_revision = "0001_init_weather"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1) UNIQUE (city_id, type) на weather_cache — нужен для ON CONFLICT
    # сначала чистим возможные дубликаты
    op.execute("""
        DELETE FROM weather_cache wc1
        USING weather_cache wc2
        WHERE wc1.id < wc2.id
          AND wc1.city_id = wc2.city_id
          AND wc1.type = wc2.type
    """)
    op.create_unique_constraint(
        "uq_weather_cache_city_type", "weather_cache", ["city_id", "type"]
    )

    # 2) daily_subscribers.last_sent_date — атомарная проверка отправки
    op.add_column(
        "daily_subscribers",
        sa.Column("last_sent_date", sa.Date(), nullable=True),
    )

    # 3) alert_subscriptions.sent_alert_ids — список последних 50 uid
    op.add_column(
        "alert_subscriptions",
        sa.Column(
            "sent_alert_ids",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )


def downgrade() -> None:
    op.drop_column("alert_subscriptions", "sent_alert_ids")
    op.drop_column("daily_subscribers", "last_sent_date")
    op.drop_constraint("uq_weather_cache_city_type", "weather_cache", type_="unique")
