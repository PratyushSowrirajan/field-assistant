import uuid

from fastapi import APIRouter, Depends, HTTPException
from geoalchemy2.shape import from_shape, to_shape
from sqlalchemy.orm import Session

from app.api.deps import get_owned_farm, get_owned_field
from app.core.config import settings
from app.db.session import get_db
from app.models.farm import Farm
from app.models.field import Field
from app.models.zone import Zone
from app.schemas.field import FieldBoundaryIn, FieldCreate, FieldOut, FieldUpdate
from app.schemas.geo import GeoJSONPolygon
from app.schemas.zone import ZoneOut
from app.services.geo import geojson_to_shapely, shapely_to_geojson
from app.services.geo_db import geodesic_area_m2, to_wkb
from app.services.zoning import regenerate_zones

router = APIRouter(tags=["fields"])


def _field_to_out(field: Field) -> FieldOut:
    boundary = None
    if field.boundary is not None:
        boundary = GeoJSONPolygon(**shapely_to_geojson(to_shape(field.boundary)))
    return FieldOut(
        id=field.id,
        farm_id=field.farm_id,
        name=field.name,
        crop_type=field.crop_type,
        crop_variety=field.crop_variety,
        planting_date=field.planting_date,
        expected_harvest_date=field.expected_harvest_date,
        area_m2=field.area_m2,
        zone_resolution_m=field.zone_resolution_m,
        archived=field.archived,
        created_at=field.created_at,
        boundary=boundary,
    )


def _zone_to_out(zone: Zone) -> ZoneOut:
    return ZoneOut(
        id=zone.id,
        field_id=zone.field_id,
        code=zone.code,
        area_m2=zone.area_m2,
        resolution_m=zone.resolution_m,
        polygon=GeoJSONPolygon(**shapely_to_geojson(to_shape(zone.polygon))),
    )


@router.post("/farms/{farm_id}/fields", response_model=FieldOut, status_code=201)
def create_field(payload: FieldCreate, farm: Farm = Depends(get_owned_farm), db: Session = Depends(get_db)):
    field = Field(
        farm_id=farm.id,
        name=payload.name,
        crop_type=payload.crop_type,
        crop_variety=payload.crop_variety,
        planting_date=payload.planting_date,
        expected_harvest_date=payload.expected_harvest_date,
        zone_resolution_m=payload.zone_resolution_m or settings.default_zone_resolution_m,
    )
    db.add(field)
    db.flush()

    if payload.boundary:
        geom = geojson_to_shapely(payload.boundary.model_dump())
        field.boundary = to_wkb(geom)
        field.area_m2 = geodesic_area_m2(db, geom)
        regenerate_zones(db, field, geom, field.zone_resolution_m)

    db.commit()
    db.refresh(field)
    return _field_to_out(field)


@router.get("/farms/{farm_id}/fields", response_model=list[FieldOut])
def list_fields(farm: Farm = Depends(get_owned_farm), db: Session = Depends(get_db)):
    fields = db.query(Field).filter(Field.farm_id == farm.id, Field.archived.is_(False)).all()
    return [_field_to_out(f) for f in fields]


@router.get("/fields/{field_id}", response_model=FieldOut)
def get_field(field: Field = Depends(get_owned_field)):
    return _field_to_out(field)


@router.patch("/fields/{field_id}", response_model=FieldOut)
def update_field(payload: FieldUpdate, field: Field = Depends(get_owned_field), db: Session = Depends(get_db)):
    for attr in ("name", "crop_type", "crop_variety", "planting_date", "expected_harvest_date", "archived"):
        value = getattr(payload, attr)
        if value is not None:
            setattr(field, attr, value)
    db.commit()
    db.refresh(field)
    return _field_to_out(field)


@router.delete("/fields/{field_id}", status_code=204)
def archive_field(field: Field = Depends(get_owned_field), db: Session = Depends(get_db)):
    field.archived = True
    db.commit()


@router.put("/fields/{field_id}/boundary", response_model=FieldOut)
def set_field_boundary(payload: FieldBoundaryIn, field: Field = Depends(get_owned_field), db: Session = Depends(get_db)):
    geom = geojson_to_shapely(payload.boundary.model_dump())
    if not geom.is_valid or geom.area == 0:
        raise HTTPException(status_code=400, detail="Boundary polygon is invalid or has zero area")

    field.boundary = to_wkb(geom)
    field.area_m2 = geodesic_area_m2(db, geom)
    if payload.zone_resolution_m:
        field.zone_resolution_m = payload.zone_resolution_m
    elif not field.zone_resolution_m:
        field.zone_resolution_m = settings.default_zone_resolution_m

    regenerate_zones(db, field, geom, field.zone_resolution_m)

    db.commit()
    db.refresh(field)
    return _field_to_out(field)


@router.get("/fields/{field_id}/zones", response_model=list[ZoneOut])
def list_zones(field: Field = Depends(get_owned_field), db: Session = Depends(get_db)):
    zones = db.query(Zone).filter(Zone.field_id == field.id).order_by(Zone.code).all()
    return [_zone_to_out(z) for z in zones]


@router.put("/fields/{field_id}/zones/resolution", response_model=list[ZoneOut])
def update_zone_resolution(
    resolution_m: float, field: Field = Depends(get_owned_field), db: Session = Depends(get_db)
):
    if field.boundary is None:
        raise HTTPException(status_code=400, detail="Field has no boundary yet")
    if resolution_m <= 0:
        raise HTTPException(status_code=400, detail="resolution_m must be positive")

    geom = to_shape(field.boundary)
    field.zone_resolution_m = resolution_m
    zones = regenerate_zones(db, field, geom, resolution_m)
    db.commit()
    return [_zone_to_out(z) for z in zones]
