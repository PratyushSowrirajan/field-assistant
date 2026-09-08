import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_farmer
from app.core.security import (
    create_device_token,
    generate_device_secret,
    hash_password,
    verify_password,
)
from app.db.session import get_db
from app.models.farm import Farm
from app.models.field import Field
from app.models.observation import CameraObservation, CNNDetection
from app.models.rover import Rover, RoverFieldAssignment, RoverPosition
from app.models.user import Farmer
from app.models.zone import Zone
from app.schemas.auth import TokenResponse
from app.schemas.rover import (
    RoverDeviceLoginRequest,
    RoverLiveState,
    RoverOut,
    RoverRegisterRequest,
    RoverRegisterResponse,
)

CONNECTION_TIMEOUT = timedelta(minutes=2)

router = APIRouter(prefix="/rovers", tags=["rovers"])


def _assert_fields_owned(field_ids: list[uuid.UUID], farmer: Farmer, db: Session):
    if not field_ids:
        return
    fields = db.query(Field).join(Farm, Field.farm_id == Farm.id).filter(
        Field.id.in_(field_ids), Farm.farmer_id == farmer.id
    ).all()
    if len(fields) != len(set(field_ids)):
        raise HTTPException(status_code=404, detail="One or more fields not found")


def _to_out(rover: Rover, db: Session) -> RoverOut:
    field_ids = [
        a.field_id
        for a in db.query(RoverFieldAssignment).filter(RoverFieldAssignment.rover_id == rover.id).all()
    ]
    return RoverOut(
        id=rover.id,
        device_id=rover.device_id,
        name=rover.name,
        status=rover.status,
        sprayer_status=rover.sprayer_status,
        battery_level=rover.battery_level,
        firmware_version=rover.firmware_version,
        last_seen_at=rover.last_seen_at,
        field_ids=field_ids,
    )


@router.post("", response_model=RoverRegisterResponse, status_code=201)
def register_rover(payload: RoverRegisterRequest, farmer: Farmer = Depends(get_current_farmer), db: Session = Depends(get_db)):
    existing = db.query(Rover).filter(Rover.device_id == payload.device_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="A rover with this device_id is already registered")

    _assert_fields_owned(payload.field_ids, farmer, db)

    secret = generate_device_secret()
    rover = Rover(
        farmer_id=farmer.id,
        device_id=payload.device_id,
        name=payload.name,
        device_secret_hash=hash_password(secret),
        status="OFFLINE",
    )
    db.add(rover)
    db.flush()

    for field_id in payload.field_ids:
        db.add(RoverFieldAssignment(rover_id=rover.id, field_id=field_id))

    db.commit()
    db.refresh(rover)
    return RoverRegisterResponse(id=rover.id, device_id=rover.device_id, device_secret=secret)


@router.get("", response_model=list[RoverOut])
def list_rovers(farmer: Farmer = Depends(get_current_farmer), db: Session = Depends(get_db)):
    rovers = db.query(Rover).filter(Rover.farmer_id == farmer.id).all()
    return [_to_out(r, db) for r in rovers]


@router.get("/{rover_id}", response_model=RoverOut)
def get_rover(rover_id: uuid.UUID, farmer: Farmer = Depends(get_current_farmer), db: Session = Depends(get_db)):
    rover = db.get(Rover, rover_id)
    if rover is None or rover.farmer_id != farmer.id:
        raise HTTPException(status_code=404, detail="Rover not found")
    return _to_out(rover, db)


@router.put("/{rover_id}/fields", response_model=RoverOut)
def assign_fields(
    rover_id: uuid.UUID,
    field_ids: list[uuid.UUID],
    farmer: Farmer = Depends(get_current_farmer),
    db: Session = Depends(get_db),
):
    rover = db.get(Rover, rover_id)
    if rover is None or rover.farmer_id != farmer.id:
        raise HTTPException(status_code=404, detail="Rover not found")

    _assert_fields_owned(field_ids, farmer, db)

    db.query(RoverFieldAssignment).filter(RoverFieldAssignment.rover_id == rover.id).delete()
    for field_id in field_ids:
        db.add(RoverFieldAssignment(rover_id=rover.id, field_id=field_id))
    db.commit()
    db.refresh(rover)
    return _to_out(rover, db)


@router.post("/device/login", response_model=TokenResponse)
def device_login(payload: RoverDeviceLoginRequest, db: Session = Depends(get_db)):
    rover = db.query(Rover).filter(Rover.device_id == payload.device_id).first()
    if rover is None or not verify_password(payload.device_secret, rover.device_secret_hash):
        raise HTTPException(status_code=401, detail="Invalid device credentials")
    return TokenResponse(access_token=create_device_token(rover.device_id))


@router.get("/{rover_id}/live", response_model=RoverLiveState)
def rover_live_state(rover_id: uuid.UUID, farmer: Farmer = Depends(get_current_farmer), db: Session = Depends(get_db)):
    rover = db.get(Rover, rover_id)
    if rover is None or rover.farmer_id != farmer.id:
        raise HTTPException(status_code=404, detail="Rover not found")

    last_position = (
        db.query(RoverPosition).filter(RoverPosition.rover_id == rover.id).order_by(RoverPosition.timestamp.desc()).first()
    )
    last_detection_row = (
        db.query(CNNDetection, CameraObservation)
        .join(CameraObservation, CNNDetection.observation_id == CameraObservation.id)
        .filter(CameraObservation.rover_id == rover.id)
        .order_by(CNNDetection.created_at.desc())
        .first()
    )
    latest_detection = None
    if last_detection_row:
        detection, _obs = last_detection_row
        latest_detection = {
            "detection_type": detection.detection_type,
            "class_name": detection.class_name,
            "confidence": detection.confidence,
        }

    zone_code = None
    zone_id = last_position.zone_id if last_position else None
    if zone_id:
        zone = db.get(Zone, zone_id)
        zone_code = zone.code if zone else None

    connected = bool(rover.last_seen_at and datetime.now(timezone.utc) - rover.last_seen_at < CONNECTION_TIMEOUT)

    return RoverLiveState(
        rover_id=rover.id,
        device_id=rover.device_id,
        status=rover.status,
        sprayer_status=rover.sprayer_status,
        battery_level=rover.battery_level,
        latitude=last_position.latitude if last_position else None,
        longitude=last_position.longitude if last_position else None,
        speed_mps=last_position.speed_mps if last_position else None,
        heading_deg=last_position.heading_deg if last_position else None,
        field_id=last_position.field_id if last_position else None,
        zone_id=zone_id,
        zone_code=zone_code,
        scan_session_id=last_position.scan_session_id if last_position else None,
        latest_detection=latest_detection,
        connection_status="CONNECTED" if connected else "OFFLINE",
        last_update_at=rover.last_seen_at,
    )


@router.get("/{rover_id}/route")
def rover_route(
    rover_id: uuid.UUID,
    scan_session_id: uuid.UUID | None = None,
    farmer: Farmer = Depends(get_current_farmer),
    db: Session = Depends(get_db),
):
    from app.services.geo import points_to_linestring_geojson, route_distance_m

    rover = db.get(Rover, rover_id)
    if rover is None or rover.farmer_id != farmer.id:
        raise HTTPException(status_code=404, detail="Rover not found")

    q = db.query(RoverPosition).filter(RoverPosition.rover_id == rover.id)
    if scan_session_id:
        q = q.filter(RoverPosition.scan_session_id == scan_session_id)
    positions = q.order_by(RoverPosition.timestamp.asc()).limit(5000).all()

    points = [(p.latitude, p.longitude) for p in positions]
    return {
        "route": points_to_linestring_geojson(points),
        "distance_travelled_m": round(route_distance_m(points), 1),
        "point_count": len(points),
    }
