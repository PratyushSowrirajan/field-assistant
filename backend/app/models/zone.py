import uuid

from geoalchemy2 import Geometry
from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin, UUIDPKMixin


class Zone(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "zones"

    field_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fields.id"), index=True
    )
    code: Mapped[str] = mapped_column(String(20))
    polygon = mapped_column(Geometry(geometry_type="POLYGON", srid=4326))
    area_m2: Mapped[float] = mapped_column(Float)
    resolution_m: Mapped[float] = mapped_column(Float)

    field = relationship("Field", back_populates="zones")
