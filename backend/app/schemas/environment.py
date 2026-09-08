import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class IrrigationRecommendationOut(BaseModel):
    field_id: uuid.UUID
    zone_id: uuid.UUID | None
    recommendation: str  # IRRIGATE_NOW|IRRIGATE_SOON|DELAY|NO_IRRIGATION|UNKNOWN
    water_stress_status: str
    over_irrigation_status: str
    soil_moisture_pct: float | None
    temperature_c: float | None
    humidity_pct: float | None
    forecast_rainfall_mm: float | None
    reason: str


class EnvironmentalRiskOut(BaseModel):
    field_id: uuid.UUID
    drought_risk: str
    flood_risk: str
    heat_risk: str
    disease_environment_risk: str


class IrrigationEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    field_id: uuid.UUID
    zone_id: uuid.UUID | None
    source: str
    status: str
    started_at: datetime
    ended_at: datetime | None
    water_volume_l: float | None


class SprayEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    field_id: uuid.UUID
    zone_id: uuid.UUID | None
    latitude: float
    longitude: float
    status: str
    completed_at: datetime
    duration_seconds: float | None
    quantity_ml: float | None


class WaterUsageOut(BaseModel):
    field_id: uuid.UUID
    total_water_l: float
    irrigated_area_m2: float
    water_usage_per_m2: float
    irrigation_saving_estimate_pct: float | None
