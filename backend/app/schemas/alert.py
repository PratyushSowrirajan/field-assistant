import uuid
from datetime import datetime

from pydantic import BaseModel


class AlertOut(BaseModel):
    id: uuid.UUID
    field_id: uuid.UUID
    zone_id: uuid.UUID | None
    zone_code: str | None = None
    field_name: str | None = None
    type: str
    severity: str
    message: str
    status: str
    acknowledged: bool
    created_at: datetime
    last_seen_at: datetime


class AdvisoryOut(BaseModel):
    id: uuid.UUID
    field_id: uuid.UUID
    zone_id: uuid.UUID | None
    what: str
    where_label: str
    severity: str
    recommended_action: str
    action_taken: bool
    created_at: datetime
