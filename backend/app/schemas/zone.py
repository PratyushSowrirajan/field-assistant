import uuid
from datetime import datetime

from pydantic import BaseModel

from app.schemas.geo import GeoJSONPolygon


class ZoneOut(BaseModel):
    id: uuid.UUID
    field_id: uuid.UUID
    code: str
    area_m2: float
    resolution_m: float
    polygon: GeoJSONPolygon


class ZoneSummary(BaseModel):
    id: uuid.UUID
    code: str
    area_m2: float
    disease_prevalence_pct: float
    pest_prevalence_pct: float
    nutrient_risk: str
    risk_level: str
    trend: str
    observation_count: int
    detection_count: int
    treatment_status: str
    last_scan_at: datetime | None
