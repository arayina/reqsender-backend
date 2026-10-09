from pydantic import BaseModel


class ProxyHealthResponse(BaseModel):
    healthy: bool
    status_code: int | None
    latency_ms: float
    error: str | None