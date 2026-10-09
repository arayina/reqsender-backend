from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TargetUrlSettingsUpdate(BaseModel):
    mode: Literal["http", "browser", "random"] = "http"
    connection: Literal["direct", "proxy"] = "direct"
    proxy_strategy: Literal["fixed", "round_robin", "random"] = "round_robin"
    proxy_ids: list[UUID] = Field(default_factory=list, max_length=20)
    count: int = Field(default=10, ge=1, le=100)
    concurrency: int = Field(default=2, ge=1, le=20)
    show_browser: bool = False
    delay_before_navigation_ms: int = Field(default=0, ge=0, le=60000)
    wait_after_load_ms: int = Field(default=3000, ge=0, le=60000)
    scroll_enabled: bool = True
    scroll_amount: int = Field(default=800, ge=0, le=10000)
    wait_after_scroll_ms: int = Field(default=2000, ge=0, le=60000)
    delay_after_navigation_ms: int = Field(default=0, ge=0, le=60000)
    navigation_timeout_ms: int = Field(default=30000, ge=1000, le=120000)


class TargetUrlSettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    target_url_id: UUID
    mode: Literal["http", "browser", "random"]
    connection: Literal["direct", "proxy"]
    proxy_strategy: Literal["fixed", "round_robin", "random"]
    proxy_ids: list[UUID]
    count: int
    concurrency: int
    show_browser: bool
    delay_before_navigation_ms: int
    wait_after_load_ms: int
    scroll_enabled: bool
    scroll_amount: int
    wait_after_scroll_ms: int
    delay_after_navigation_ms: int
    navigation_timeout_ms: int
