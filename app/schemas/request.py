from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.browser import BrowserSettings


class RequestCreate(BaseModel):
    url: str = Field(min_length=1, max_length=2048)
    proxy_id: UUID | None = None
    target_url_id: UUID | None = None
    mode: Literal["http", "browser", "random"] = "http"
    browser_settings: BrowserSettings = Field(default_factory=BrowserSettings)


class RequestResponse(BaseModel):
    success: bool
    status_code: int | None = None
    latency_ms: float
    final_url: str | None = None
    title: str | None = None
    error: str | None = None


class BatchRequestCreate(BaseModel):
    target_url_id: UUID
    url: str = Field(min_length=1, max_length=2048)
    proxy_ids: list[UUID] = Field(default_factory=list)
    proxy_strategy: Literal["fixed", "round_robin", "random"] = "fixed"
    mode: Literal["http", "browser", "random"] = "http"
    count: int = Field(default=1, ge=1, le=20000)
    concurrency: int = Field(default=1, ge=1, le=20)
    browser_settings: BrowserSettings = Field(default_factory=BrowserSettings)


class BatchRequestResponse(BaseModel):
    total: int
    success: int
    failed: int
    results: list[RequestResponse]
