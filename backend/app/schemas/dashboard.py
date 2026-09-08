import uuid
from datetime import datetime

from pydantic import BaseModel

from app.schemas.alert import AlertOut


class DashboardFieldCard(BaseModel):
    id: uuid.UUID
    name: str
    crop_type: str | None
    area_m2: float | None
    health_status: str
    top_issue: str | None
    last_scan_at: datetime | None
    rover_status: str | None


class DashboardSummary(BaseModel):
    total_fields: int
    fields_requiring_attention: int
    active_alerts: int
    disease_pest_alerts: int
    water_stress_alerts: int
    environmental_alerts: int
    fields: list[DashboardFieldCard]
    top_alerts: list[AlertOut]
    active_rover_count: int
