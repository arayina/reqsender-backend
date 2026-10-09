"""create executions table

Revision ID: a86ed09d1c38
Revises: 7f2b1c9d4a11
Create Date: 2026-10-09 11:59:05.997837

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a86ed09d1c38'
down_revision: Union[str, Sequence[str], None] = '7f2b1c9d4a11'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "executions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "target_url_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column(
            "proxy_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column(
            "execution_mode",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column(
            "success",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "status_code",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "latency_ms",
            sa.Float(),
            nullable=False,
        ),
        sa.Column(
            "final_url",
            sa.String(length=2048),
            nullable=True,
        ),
        sa.Column(
            "error",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["target_url_id"],
            ["target_urls.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["proxy_id"],
            ["proxies.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_executions_target_url_id",
        "executions",
        ["target_url_id"],
    )

    op.create_index(
        "ix_executions_proxy_id",
        "executions",
        ["proxy_id"],
    )

    op.create_index(
        "ix_executions_created_at",
        "executions",
        ["created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_executions_created_at",
        table_name="executions",
    )

    op.drop_index(
        "ix_executions_proxy_id",
        table_name="executions",
    )

    op.drop_index(
        "ix_executions_target_url_id",
        table_name="executions",
    )

    op.drop_table("executions")