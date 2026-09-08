import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.mixins import UUIDPKMixin


class IrrigationEvent(UUIDPKMixin, Base):
    __tablename__ = "irrigation_events"

    field_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fields.id"), index=True
    )
    zone_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("zones.id"), nullable=True, index=True
    )
    source: Mapped[str] = mapped_column(String(30), default="MANUAL")  # MANUAL | EQUIPMENT
    status: Mapped[str] = mapped_column(String(20), default="COMPLETED")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    water_volume_l: Mapped[float | None] = mapped_column(Float, nullable=True)
