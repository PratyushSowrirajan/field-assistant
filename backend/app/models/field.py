import uuid
from datetime import date

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, Date, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin, UUIDPKMixin


class Field(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "fields"

    farm_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("farms.id"), index=True
    )
    name: Mapped[str] = mapped_column(String(120))
    crop_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    crop_variety: Mapped[str | None] = mapped_column(String(80), nullable=True)
    planting_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expected_harvest_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    boundary = mapped_column(Geometry(geometry_type="POLYGON", srid=4326), nullable=True)
    area_m2: Mapped[float | None] = mapped_column(Float, nullable=True)
    zone_resolution_m: Mapped[float | None] = mapped_column(Float, nullable=True)

    archived: Mapped[bool] = mapped_column(Boolean, default=False)

    farm = relationship("Farm", back_populates="fields")
    zones = relationship("Zone", back_populates="field", cascade="all, delete-orphan")
    rover_assignments = relationship(
        "RoverFieldAssignment", back_populates="field", cascade="all, delete-orphan"
    )
