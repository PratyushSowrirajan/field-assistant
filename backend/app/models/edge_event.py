import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.mixins import UUIDPKMixin


class EdgeEvent(UUIDPKMixin, Base):
    """Raw log of every edge event received, for dedup + offline-sync auditing."""

    __tablename__ = "edge_events"

    event_id: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    device_id: Mapped[str] = mapped_column(String(80), index=True)
    rover_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rovers.id"), nullable=True, index=True
    )
    event_type: Mapped[str] = mapped_column(String(40), index=True)
    payload: Mapped[dict] = mapped_column(JSON)
    original_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    sync_status: Mapped[str] = mapped_column(String(20), default="SYNCED")  # SYNCED|FAILED|PARTIAL
    error: Mapped[str | None] = mapped_column(String(500), nullable=True)
