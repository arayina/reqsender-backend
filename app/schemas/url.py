from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TargetUrlCreate(BaseModel):
    url: str = Field(min_length=1, max_length=2048)
    name: str | None = Field(default=None, max_length=255)
    enabled: bool = True


class TargetUrlUpdate(BaseModel):
    url: str | None = Field(default=None, min_length=1, max_length=2048)
    name: str | None = Field(default=None, max_length=255)
    enabled: bool | None = None


class TargetUrlResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    url: str
    name: str | None
    enabled: bool