import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_farmer
from app.db.session import get_db
from app.models.farm import Farm
from app.models.field import Field
from app.models.zone import Zone
from app.models.user import Farmer
from app.schemas.zone import ZoneSummary
from app.services.analytics_service import treatment_response, zone_summary

router = APIRouter(prefix="/zones", tags=["zones"])


def _owned_zone(zone_id: uuid.UUID, farmer: Farmer, db: Session) -> Zone:
    zone = db.get(Zone, zone_id)
    if zone is None:
        raise HTTPException(status_code=404, detail="Zone not found")
    field = db.get(Field, zone.field_id)
    farm = db.get(Farm, field.farm_id) if field else None
    if farm is None or farm.farmer_id != farmer.id:
        raise HTTPException(status_code=404, detail="Zone not found")
    return zone


@router.get("/{zone_id}/summary", response_model=ZoneSummary)
def get_zone_summary(zone_id: uuid.UUID, farmer: Farmer = Depends(get_current_farmer), db: Session = Depends(get_db)):
    zone = _owned_zone(zone_id, farmer, db)
    return zone_summary(db, zone)


@router.get("/{zone_id}/treatment-response")
def get_zone_treatment_response(zone_id: uuid.UUID, farmer: Farmer = Depends(get_current_farmer), db: Session = Depends(get_db)):
    zone = _owned_zone(zone_id, farmer, db)
    return {"zone_id": zone.id, "treatment_response": treatment_response(db, zone)}
