import uuid
from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import JSON, DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin, UUIDPKMixin


class CameraObservation(UUIDPKMixin, Base):
    __tablename__ = "camera_observations"

    rover_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rovers.id"), index=True
    )
    scan_session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scan_sessions.id"), nullable=True, index=True
    )
    camera_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    frame_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    image_uri: Mapped[str | None] = mapped_column(String(500), nullable=True)

    location = mapped_column(Geometry(geometry_type="POINT", srid=4326))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    field_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fields.id"), nullable=True, index=True
    )
    zone_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("zones.id"), nullable=True, index=True
    )

    detections = relationship(
        "CNNDetection", back_populates="observation", cascade="all, delete-orphan"
    )


class CNNDetection(UUIDPKMixin, Base):
    __tablename__ = "cnn_detections"

    observation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("camera_observations.id"), index=True
    )
    # DISEASE | PEST | NUTRIENT_DEFICIENCY | GROWTH_STAGE
    detection_type: Mapped[str] = mapped_column(String(30), index=True)
    class_name: Mapped[str] = mapped_column(String(80), index=True)
    confidence: Mapped[float] = mapped_column(Float)
    severity: Mapped[str | None] = mapped_column(String(20), nullable=True)
    model_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(40), nullable=True)
    bounding_box: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    observation = relationship("CameraObservation", back_populates="detections")
