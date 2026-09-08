"""PostGIS-backed geospatial helpers that require a DB session (accurate geodesic area)."""
from geoalchemy2.shape import from_shape
from shapely.geometry.base import BaseGeometry
from sqlalchemy import text
from sqlalchemy.orm import Session


def to_wkb(geom: BaseGeometry, srid: int = 4326):
    return from_shape(geom, srid=srid)


def geodesic_area_m2(db: Session, geom: BaseGeometry) -> float:
    result = db.execute(
        text("SELECT ST_Area(geography(ST_GeomFromText(:wkt, 4326)))"),
        {"wkt": geom.wkt},
    ).scalar_one()
    return float(result)
