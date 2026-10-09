"""create target url settings

Revision ID: 7f2b1c9d4a11
Revises: 2118940ab29d
Create Date: 2026-10-09 11:40:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "7f2b1c9d4a11"
down_revision: Union[str, Sequence[str], None] = "2118940ab29d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "target_url_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("target_url_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mode", sa.String(length=20), nullable=False, server_default="http"),
        sa.Column("connection", sa.String(length=20), nullable=False, server_default="direct"),
        sa.Column("proxy_strategy", sa.String(length=20), nullable=False, server_default="round_robin"),
        sa.Column("count", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("concurrency", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("show_browser", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("delay_before_navigation_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("wait_after_load_ms", sa.Integer(), nullable=False, server_default="3000"),
        sa.Column("scroll_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("scroll_amount", sa.Integer(), nullable=False, server_default="800"),
        sa.Column("wait_after_scroll_ms", sa.Integer(), nullable=False, server_default="2000"),
        sa.Column("delay_after_navigation_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("navigation_timeout_ms", sa.Integer(), nullable=False, server_default="30000"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["target_url_id"], ["target_urls.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("target_url_id", name="uq_target_url_settings_target_url_id"),
    )
    op.create_index(
        "ix_target_url_settings_target_url_id",
        "target_url_settings",
        ["target_url_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_target_url_settings_target_url_id", table_name="target_url_settings")
    op.drop_constraint("uq_target_url_settings_target_url_id", "target_url_settings", type_="unique")
    op.drop_table("target_url_settings")
