import uuid

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin, UUIDPKMixin


class Farm(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "farms"

    farmer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("farmers.id"), index=True
    )
    name: Mapped[str] = mapped_column(String(120))
    location = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, default=False)

    farmer = relationship("Farmer", back_populates="farms")
    fields = relationship("Field", back_populates="farm", cascade="all, delete-orphan")
