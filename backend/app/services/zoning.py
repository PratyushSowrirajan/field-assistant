from shapely.geometry import Polygon
from sqlalchemy.orm import Session

from app.models.field import Field
from app.models.zone import Zone
from app.services.geo import generate_zone_grid
from app.services.geo_db import geodesic_area_m2, to_wkb


def regenerate_zones(db: Session, field: Field, boundary: Polygon, resolution_m: float) -> list[Zone]:
    """Delete existing zones for a field and generate a fresh grid clipped to the boundary."""
    db.query(Zone).filter(Zone.field_id == field.id).delete()

    zone_cells = generate_zone_grid(boundary, resolution_m)
    zones: list[Zone] = []
    for code, poly in zone_cells:
        area = geodesic_area_m2(db, poly)
        zone = Zone(
            field_id=field.id,
            code=code,
            polygon=to_wkb(poly),
            area_m2=area,
            resolution_m=resolution_m,
        )
        db.add(zone)
        zones.append(zone)

    db.flush()
    return zones
