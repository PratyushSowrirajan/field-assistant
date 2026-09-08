import uuid

from fastapi import APIRouter, Depends, HTTPException
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from sqlalchemy.orm import Session

from app.api.deps import get_current_farmer, get_owned_farm
from app.db.session import get_db
from app.models.farm import Farm
from app.models.field import Field
from app.models.user import Farmer
from app.schemas.farm import FarmCreate, FarmOut, FarmUpdate

router = APIRouter(prefix="/farms", tags=["farms"])


def _to_out(farm: Farm, db: Session) -> FarmOut:
    count = db.query(Field).filter(Field.farm_id == farm.id, Field.archived.is_(False)).count()
    return FarmOut(
        id=farm.id, name=farm.name, archived=farm.archived, created_at=farm.created_at, field_count=count
    )


@router.post("", response_model=FarmOut, status_code=201)
def create_farm(payload: FarmCreate, farmer: Farmer = Depends(get_current_farmer), db: Session = Depends(get_db)):
    location = None
    if payload.location:
        lon, lat = payload.location.coordinates
        location = from_shape(Point(lon, lat), srid=4326)

    farm = Farm(farmer_id=farmer.id, name=payload.name, location=location)
    db.add(farm)
    db.commit()
    db.refresh(farm)
    return _to_out(farm, db)


@router.get("", response_model=list[FarmOut])
def list_farms(farmer: Farmer = Depends(get_current_farmer), db: Session = Depends(get_db)):
    farms = db.query(Farm).filter(Farm.farmer_id == farmer.id, Farm.archived.is_(False)).all()
    return [_to_out(f, db) for f in farms]


@router.get("/{farm_id}", response_model=FarmOut)
def get_farm(farm: Farm = Depends(get_owned_farm), db: Session = Depends(get_db)):
    return _to_out(farm, db)


@router.patch("/{farm_id}", response_model=FarmOut)
def update_farm(payload: FarmUpdate, farm: Farm = Depends(get_owned_farm), db: Session = Depends(get_db)):
    if payload.name is not None:
        farm.name = payload.name
    if payload.archived is not None:
        farm.archived = payload.archived
    if payload.location is not None:
        lon, lat = payload.location.coordinates
        farm.location = from_shape(Point(lon, lat), srid=4326)
    db.commit()
    db.refresh(farm)
    return _to_out(farm, db)


@router.delete("/{farm_id}", status_code=204)
def archive_farm(farm: Farm = Depends(get_owned_farm), db: Session = Depends(get_db)):
    farm.archived = True
    db.commit()
