import uuid
from datetime import datetime

from pydantic import BaseModel


class RoverRegisterRequest(BaseModel):
    name: str
    device_id: str
    field_ids: list[uuid.UUID] = []


class RoverRegisterResponse(BaseModel):
    id: uuid.UUID
    device_id: str
    device_secret: str  # returned once at registration only


class RoverOut(BaseModel):
    id: uuid.UUID
    device_id: str
    name: str
    status: str
    sprayer_status: str | None
    battery_level: float | None
    firmware_version: str | None
    last_seen_at: datetime | None
    field_ids: list[uuid.UUID] = []


class RoverDeviceLoginRequest(BaseModel):
    device_id: str
    device_secret: str


class RoverLiveState(BaseModel):
    rover_id: uuid.UUID
    device_id: str
    status: str
    sprayer_status: str | None
    battery_level: float | None
    latitude: float | None
    longitude: float | None
    speed_mps: float | None
    heading_deg: float | None
    field_id: uuid.UUID | None
    zone_id: uuid.UUID | None
    zone_code: str | None
    scan_session_id: uuid.UUID | None
    latest_detection: dict | None
    connection_status: str
    last_update_at: datetime | None
