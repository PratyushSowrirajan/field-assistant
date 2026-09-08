import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.mixins import TimestampMixin, UUIDPKMixin


class Alert(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "alerts"

    field_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fields.id"), index=True
    )
    zone_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("zones.id"), nullable=True, index=True
    )
    # DISEASE | PEST | NUTRIENT | WATER_STRESS | OVER_IRRIGATION | DROUGHT | FLOOD | HEAT | IRRIGATION
    type: Mapped[str] = mapped_column(String(30), index=True)
    severity: Mapped[str] = mapped_column(String(20))  # LOW|MODERATE|HIGH|CRITICAL
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")  # ACTIVE|ACKNOWLEDGED|RESOLVED
    dedup_key: Mapped[str] = mapped_column(String(160), index=True)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)


class Advisory(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "advisories"

    alert_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("alerts.id"), nullable=True, index=True
    )
    field_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fields.id"), index=True
    )
    zone_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("zones.id"), nullable=True, index=True
    )
    what: Mapped[str] = mapped_column(String(255))
    where_label: Mapped[str] = mapped_column(String(120))
    severity: Mapped[str] = mapped_column(String(20))
    recommended_action: Mapped[str] = mapped_column(Text)
    action_taken: Mapped[bool] = mapped_column(Boolean, default=False)
