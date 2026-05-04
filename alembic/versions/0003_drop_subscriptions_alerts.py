"""drop subscriptions and alerts tables

Revision ID: 0003
Revises: 0002
Create Date: 2026-05-05
"""
from alembic import op


revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DROP TABLE IF EXISTS alert_subscriptions CASCADE")
    op.execute("DROP TABLE IF EXISTS daily_subscribers CASCADE")
    # удаляем закешированные onecall-данные (значение enum остаётся в PG —
    # ALTER TYPE DROP VALUE не поддерживается, но это безвредно)
    op.execute("DELETE FROM weather_cache WHERE type = 'onecall'")


def downgrade() -> None:
    # обратной миграции не предусмотрено — данные подписок всё равно потеряны
    pass
