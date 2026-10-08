from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class RequestCreate(BaseModel):
    url: str = Field(min_length=1, max_length=2048)
    proxy_id: UUID | None = None
    mode: Literal["http", "browser", "random"] = "http"


class RequestResponse(BaseModel):
    success: bool
    status_code: int | None = None
    latency_ms: float
    final_url: str | None = None
    title: str | None = None
    error: str | None = None


class BatchRequestCreate(BaseModel):
    url: str = Field(min_length=1, max_length=2048)
    proxy_id: UUID | None = None
    mode: Literal["http", "browser", "random"] = "http"
    count: int = Field(default=1, ge=1, le=100)
    concurrency: int = Field(default=1, ge=1, le=20)


class BatchRequestResponse(BaseModel):
    total: int
    success: int
    failed: int
    results: list[RequestResponse]