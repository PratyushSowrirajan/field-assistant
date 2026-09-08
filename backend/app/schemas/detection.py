import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DetectionOut(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    id: uuid.UUID
    observation_id: uuid.UUID
    detection_type: str
    class_name: str
    confidence: float
    severity: str | None
    model_name: str | None
    model_version: str | None
    created_at: datetime

    image_uri: str | None
    latitude: float
    longitude: float
    field_id: uuid.UUID | None
    zone_id: uuid.UUID | None
    zone_code: str | None = None
    rover_id: uuid.UUID
    scan_session_id: uuid.UUID | None
    treatment_status: str = "UNTREATED"
