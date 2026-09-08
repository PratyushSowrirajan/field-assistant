import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.geo import GeoJSONPoint


class FarmCreate(BaseModel):
    name: str
    location: GeoJSONPoint | None = None


class FarmUpdate(BaseModel):
    name: str | None = None
    location: GeoJSONPoint | None = None
    archived: bool | None = None


class FarmOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    archived: bool
    created_at: datetime
    field_count: int = 0
