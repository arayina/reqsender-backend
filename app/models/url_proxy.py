import uuid

from sqlalchemy import ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TargetUrlProxy(Base):
    __tablename__ = "target_url_proxies"

    __table_args__ = (
        UniqueConstraint(
            "target_url_id",
            "proxy_id",
            name="uq_target_url_proxy",
        ),
        Index(
            "ix_target_url_proxies_target_url_id",
            "target_url_id",
        ),
        Index(
            "ix_target_url_proxies_proxy_id",
            "proxy_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    target_url_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "target_urls.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    proxy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "proxies.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )