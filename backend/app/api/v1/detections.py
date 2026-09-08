import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_farmer, get_owned_field
from app.db.session import get_db
from app.models.farm import Farm
from app.models.field import Field
from app.models.observation import CameraObservation, CNNDetection
from app.models.spray import SprayEvent
from app.models.user import Farmer
from app.models.zone import Zone
from app.schemas.detection import DetectionOut
from app.services.geo import haversine_m

router = APIRouter(tags=["detections"])

MATCH_RADIUS_M = 8.0


def _treatment_status(db: Session, obs: CameraObservation, detection_created_at: datetime) -> str:
    if obs.field_id is None:
        return "UNTREATED"
    sprays = (
        db.query(SprayEvent)
        .filter(
            SprayEvent.field_id == obs.field_id,
            SprayEvent.status == "SPRAY_COMPLETED",
            SprayEvent.completed_at >= detection_created_at,
        )
        .all()
    )
    for s in sprays:
        if haversine_m(obs.latitude, obs.longitude, s.latitude, s.longitude) <= MATCH_RADIUS_M:
            return "TREATED"
    return "UNTREATED"


def _to_out(detection: CNNDetection, obs: CameraObservation, db: Session) -> DetectionOut:
    zone_code = None
    if obs.zone_id:
        zone = db.get(Zone, obs.zone_id)
        zone_code = zone.code if zone else None
    return DetectionOut(
        id=detection.id,
        observation_id=obs.id,
        detection_type=detection.detection_type,
        class_name=detection.class_name,
        confidence=detection.confidence,
        severity=detection.severity,
        model_name=detection.model_name,
        model_version=detection.model_version,
        created_at=detection.created_at,
        image_uri=obs.image_uri,
        latitude=obs.latitude,
        longitude=obs.longitude,
        field_id=obs.field_id,
        zone_id=obs.zone_id,
        zone_code=zone_code,
        rover_id=obs.rover_id,
        scan_session_id=obs.scan_session_id,
        treatment_status=_treatment_status(db, obs, detection.created_at),
    )


@router.get("/fields/{field_id}/detections", response_model=list[DetectionOut])
def list_detections(
    field: Field = Depends(get_owned_field),
    db: Session = Depends(get_db),
    zone_id: uuid.UUID | None = None,
    detection_type: str | None = None,
    class_name: str | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
    limit: int = 100,
):
    q = (
        db.query(CNNDetection, CameraObservation)
        .join(CameraObservation, CNNDetection.observation_id == CameraObservation.id)
        .filter(CameraObservation.field_id == field.id)
    )
    if zone_id:
        q = q.filter(CameraObservation.zone_id == zone_id)
    if detection_type:
        q = q.filter(CNNDetection.detection_type == detection_type)
    if class_name:
        q = q.filter(CNNDetection.class_name == class_name)
    if since:
        q = q.filter(CNNDetection.created_at >= since)
    if until:
        q = q.filter(CNNDetection.created_at <= until)

    rows = q.order_by(CNNDetection.created_at.desc()).limit(min(limit, 500)).all()
    return [_to_out(d, o, db) for d, o in rows]


@router.get("/detections/{detection_id}", response_model=DetectionOut)
def get_detection(detection_id: uuid.UUID, farmer: Farmer = Depends(get_current_farmer), db: Session = Depends(get_db)):
    row = (
        db.query(CNNDetection, CameraObservation)
        .join(CameraObservation, CNNDetection.observation_id == CameraObservation.id)
        .filter(CNNDetection.id == detection_id)
        .first()
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Detection not found")
    detection, obs = row

    field = db.get(Field, obs.field_id) if obs.field_id else None
    farm = db.get(Farm, field.farm_id) if field else None
    if farm is None or farm.farmer_id != farmer.id:
        raise HTTPException(status_code=404, detail="Detection not found")

    return _to_out(detection, obs, db)
