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