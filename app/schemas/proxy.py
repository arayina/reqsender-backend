from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProxyCreate(BaseModel):
    host: str = Field(min_length=1)
    port: int = Field(gt=0, le=65535)
    protocol: str = Field(default="http")
    username: str | None = None
    password: str | None = None
    enabled: bool = True


class ProxyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    host: str
    port: int
    protocol: str
    username: str | None = None
    enabled: bool
    
class ProxyUpdate(BaseModel):
    host: str | None = Field(default=None, min_length=1)
    port: int | None = Field(default=None, gt=0, le=65535)
    protocol: str | None = None
    username: str | None = None
    password: str | None = None
    enabled: bool | None = None