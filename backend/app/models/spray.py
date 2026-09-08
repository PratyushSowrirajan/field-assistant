import uuid
from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.mixins import TimestampMixin, UUIDPKMixin


class SprayRecommendation(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "spray_recommendations"

    field_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fields.id"), index=True
    )
    zone_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("zones.id"), index=True
    )
    target_location = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=True)
    target_latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    target_longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    reason: Mapped[str] = mapped_column(String(255))
    priority: Mapped[str] = mapped_column(String(20), default="MODERATE")
    status: Mapped[str] = mapped_column(String(20), default="PENDING")  # PENDING|ACTIONED|DISMISSED


class SprayEvent(UUIDPKMixin, Base):
    __tablename__ = "spray_events"

    field_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fields.id"), index=True
    )
    zone_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("zones.id"), nullable=True, index=True
    )
    rover_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rovers.id"), nullable=True, index=True
    )
    recommendation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("spray_recommendations.id"), nullable=True
    )

    location = mapped_column(Geometry(geometry_type="POINT", srid=4326))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)

    status: Mapped[str] = mapped_column(String(20))  # SPRAY_STARTED|SPRAY_COMPLETED|SPRAY_FAILED
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    quantity_ml: Mapped[float | None] = mapped_column(Float, nullable=True)
