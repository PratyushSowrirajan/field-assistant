import uuid
from datetime import datetime

from pydantic import BaseModel


class TimeSeriesPoint(BaseModel):
    timestamp: datetime
    value: float


class FieldHealthOut(BaseModel):
    field_id: uuid.UUID
    status: str  # HEALTHY|MONITOR|ATTENTION|HIGH_RISK|CRITICAL
    score: float
    disease_prevalence_pct: float
    pest_prevalence_pct: float
    water_stress_status: str
    environmental_risk: str
    yield_risk: str


class HotspotOut(BaseModel):
    id: str
    field_id: uuid.UUID
    zone_id: uuid.UUID | None
    detection_type: str
    class_name: str | None
    center_lat: float
    center_lon: float
    detection_count: int
    density_per_ha: float
    severity: str


class DecisionInsightOut(BaseModel):
    type: str
    severity: str
    field_id: uuid.UUID
    zone_id: uuid.UUID | None
    message: str
    evidence: str
    recommended_action: str


class YieldRiskOut(BaseModel):
    field_id: uuid.UUID
    yield_risk: str
    contributing_factors: list[str]


class TreatmentCoverageOut(BaseModel):
    field_id: uuid.UUID
    qualifying_detections: int
    treated_detections: int
    treatment_coverage_pct: float
    untreated_problem_count: int
