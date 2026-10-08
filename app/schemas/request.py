from uuid import UUID

from pydantic import BaseModel, Field


class RequestCreate(BaseModel):
    url: str = Field(min_length=1, max_length=2048)
    proxy_id: UUID | None = None


class RequestResponse(BaseModel):
    success: bool
    status_code: int | None = None
    latency_ms: float
    final_url: str | None = None
    error: str | None = None