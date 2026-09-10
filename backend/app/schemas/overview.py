import uuid
from datetime import datetime

from pydantic import BaseModel

Trend = str  # "UP" | "DOWN" | "FLAT"


class EnvironmentTile(BaseModel):
    label: str
    value: float | None
    unit: str
    trend: Trend
    history: list[float]  # recent readings, oldest -> newest, for a sparkline


class NutrientTile(BaseModel):
    nutrient: str  # NITROGEN | PHOSPHORUS | POTASSIUM
    label: str
    value: float | None
    unit: str
    status: str  # LOW | OPTIMAL | HIGH | UNKNOWN
    delta_vs_previous: float | None
    low_threshold: float
    high_threshold: float
    display_max: float
    history: list[float]


class LatestPrediction(BaseModel):
    detection_type: str | None
    class_label: str | None
    zone_code: str | None
    confidence: float | None
    confidence_label: str | None  # LOW | MEDIUM | HIGH
    message: str | None
    minutes_ago: float | None


class FieldOverviewOut(BaseModel):
    field_id: uuid.UUID
    field_name: str
    farm_name: str
    crop_type: str | None
    growth_stage: str | None
    area_m2: float | None

    health_status: str
    health_score: float

    connection_status: str  # CONNECTED | OFFLINE | NO_ROVER
    last_scan_at: datetime | None

    latest_prediction: LatestPrediction | None
    environment: list[EnvironmentTile]
    nutrients: list[NutrientTile]
