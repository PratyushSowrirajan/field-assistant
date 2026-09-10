import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, confloat


class GPSData(BaseModel):
    latitude: confloat(ge=-90, le=90)
    longitude: confloat(ge=-180, le=180)
    accuracy_m: float | None = None
    altitude_m: float | None = None
    speed_mps: float | None = None
    heading_deg: float | None = None


class CameraData(BaseModel):
    camera_id: str | None = None
    frame_id: str | None = None
    image_uri: str | None = None


class CNNResult(BaseModel):
    detection_type: Literal["DISEASE", "PEST", "NUTRIENT_DEFICIENCY", "GROWTH_STAGE"]
    class_name: str = Field(alias="class")
    confidence: confloat(ge=0, le=1)
    severity: str | None = None
    model_name: str | None = None
    model_version: str | None = None
    bounding_box: dict | None = None

    model_config = {"populate_by_name": True, "protected_namespaces": ()}


class RoverStatusData(BaseModel):
    status: str | None = None
    sprayer_status: str | None = None
    battery_level: float | None = None
    firmware_version: str | None = None


class RoverTelemetryIn(BaseModel):
    """Combined position + optional camera/CNN + rover status event."""

    device_id: str
    timestamp: datetime
    scan_session_id: uuid.UUID | None = None
    gps: GPSData
    camera: CameraData | None = None
    cnn: CNNResult | None = None
    rover: RoverStatusData | None = None


class SensorReadingIn(BaseModel):
    device_id: str
    timestamp: datetime
    sensor_id: str | None = None
    reading_type: Literal[
        "SOIL_MOISTURE", "AIR_TEMPERATURE", "RELATIVE_HUMIDITY", "NITROGEN", "PHOSPHORUS", "POTASSIUM"
    ]
    value: float
    unit: str | None = None
    gps: GPSData | None = None
    field_id: uuid.UUID | None = None


class SprayEventIn(BaseModel):
    device_id: str
    event: Literal["SPRAY_STARTED", "SPRAY_COMPLETED", "SPRAY_FAILED"]
    timestamp: datetime
    location: GPSData
    recommendation_id: uuid.UUID | None = None
    duration_seconds: float | None = None
    quantity_ml: float | None = None


class IrrigationEventIn(BaseModel):
    device_id: str
    field_id: uuid.UUID
    zone_id: uuid.UUID | None = None
    event: Literal["IRRIGATION_STARTED", "IRRIGATION_COMPLETED"]
    timestamp: datetime
    water_volume_l: float | None = None
    source: Literal["MANUAL", "EQUIPMENT"] = "EQUIPMENT"


class ScanSessionEventIn(BaseModel):
    device_id: str
    field_id: uuid.UUID
    event: Literal["SCAN_START", "SCAN_END"]
    timestamp: datetime
    interrupted: bool = False


class EdgeEventEnvelope(BaseModel):
    """Generic batched/offline-queued event wrapper (PRD section 42)."""

    event_id: str
    device_id: str
    timestamp: datetime
    event_type: Literal[
        "TELEMETRY",
        "SENSOR_READING",
        "SPRAY_EVENT",
        "IRRIGATION_EVENT",
        "SCAN_SESSION_EVENT",
    ]
    payload: dict


class EdgeEventAck(BaseModel):
    event_id: str
    status: Literal["SYNCED", "DUPLICATE", "FAILED"]
    error: str | None = None


class EdgeBatchResponse(BaseModel):
    results: list[EdgeEventAck]
