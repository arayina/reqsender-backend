"""create target url proxy assignments

Revision ID: 2118940ab29d
Revises: c15071400dfd
Create Date: 2026-10-09 09:29:25.604956

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "2118940ab29d"
down_revision: Union[str, Sequence[str], None] = "c15071400dfd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "target_url_proxies",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "target_url_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "proxy_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["target_url_id"],
            ["target_urls.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["proxy_id"],
            ["proxies.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_unique_constraint(
        "uq_target_url_proxy",
        "target_url_proxies",
        [
            "target_url_id",
            "proxy_id",
        ],
    )

    op.create_index(
        "ix_target_url_proxies_target_url_id",
        "target_url_proxies",
        ["target_url_id"],
    )

    op.create_index(
        "ix_target_url_proxies_proxy_id",
        "target_url_proxies",
        ["proxy_id"],
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        "ix_target_url_proxies_proxy_id",
        table_name="target_url_proxies",
    )

    op.drop_index(
        "ix_target_url_proxies_target_url_id",
        table_name="target_url_proxies",
    )

    op.drop_constraint(
        "uq_target_url_proxy",
        "target_url_proxies",
        type_="unique",
    )

    op.drop_table(
        "target_url_proxies",
    )