import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TargetUrlSettings(Base):
    __tablename__ = "target_url_settings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    target_url_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("target_urls.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    mode: Mapped[str] = mapped_column(String(20), nullable=False, default="http")
    connection: Mapped[str] = mapped_column(String(20), nullable=False, default="direct")
    proxy_strategy: Mapped[str] = mapped_column(String(20), nullable=False, default="round_robin")
    count: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    concurrency: Mapped[int] = mapped_column(Integer, nullable=False, default=2)

    show_browser: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    delay_before_navigation_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    wait_after_load_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=3000)
    scroll_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    scroll_amount: Mapped[int] = mapped_column(Integer, nullable=False, default=800)
    wait_after_scroll_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=2000)
    delay_after_navigation_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    navigation_timeout_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=30000)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
