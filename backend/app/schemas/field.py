import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.geo import GeoJSONPolygon


class FieldCreate(BaseModel):
    name: str
    crop_type: str | None = None
    crop_variety: str | None = None
    planting_date: date | None = None
    expected_harvest_date: date | None = None
    boundary: GeoJSONPolygon | None = None
    zone_resolution_m: float | None = None


class FieldUpdate(BaseModel):
    name: str | None = None
    crop_type: str | None = None
    crop_variety: str | None = None
    planting_date: date | None = None
    expected_harvest_date: date | None = None
    archived: bool | None = None


class FieldBoundaryIn(BaseModel):
    boundary: GeoJSONPolygon
    zone_resolution_m: float | None = None


class FieldOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    farm_id: uuid.UUID
    name: str
    crop_type: str | None
    crop_variety: str | None
    planting_date: date | None
    expected_harvest_date: date | None
    area_m2: float | None
    zone_resolution_m: float | None
    archived: bool
    created_at: datetime
    boundary: GeoJSONPolygon | None = None


class FieldSummary(BaseModel):
    id: uuid.UUID
    name: str
    crop_type: str | None
    area_m2: float | None
    health_status: str
    top_issue: str | None
    last_scan_at: datetime | None
    active_rover_status: str | None
