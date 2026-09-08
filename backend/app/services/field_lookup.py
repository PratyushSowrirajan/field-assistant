import uuid

from geoalchemy2.shape import to_shape
from sqlalchemy.orm import Session

from app.models.field import Field
from app.models.zone import Zone


def locate_point(
    db: Session, lat: float, lon: float, candidate_field_ids: list[uuid.UUID]
) -> tuple[uuid.UUID | None, uuid.UUID | None]:
    """Point-in-polygon: which field (and which zone within it) contains (lat, lon).
    candidate_field_ids narrows the search to fields associated with the reporting rover.
    """
    if not candidate_field_ids:
        return None, None

    from shapely.geometry import Point

    point = Point(lon, lat)

    fields = db.query(Field).filter(Field.id.in_(candidate_field_ids), Field.boundary.isnot(None)).all()
    matched_field: Field | None = None
    for field in fields:
        boundary = to_shape(field.boundary)
        if boundary.contains(point) or boundary.touches(point):
            matched_field = field
            break

    if matched_field is None:
        return None, None

    zones = db.query(Zone).filter(Zone.field_id == matched_field.id).all()
    matched_zone_id = None
    for zone in zones:
        poly = to_shape(zone.polygon)
        if poly.contains(point) or poly.touches(point):
            matched_zone_id = zone.id
            break

    return matched_field.id, matched_zone_id
