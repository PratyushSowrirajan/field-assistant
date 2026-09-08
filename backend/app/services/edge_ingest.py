import uuid
from datetime import datetime, timezone

from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from sqlalchemy.orm import Session

from app.models.environment import EnvironmentalReading
from app.models.irrigation import IrrigationEvent
from app.models.observation import CameraObservation, CNNDetection
from app.models.rover import Rover, RoverFieldAssignment, RoverPosition, ScanSession
from app.models.spray import SprayEvent
from app.schemas.edge import (
    IrrigationEventIn,
    RoverTelemetryIn,
    ScanSessionEventIn,
    SensorReadingIn,
    SprayEventIn,
)
from app.services.detection_pipeline import evaluate_detection_alert
from app.services.field_lookup import locate_point


def _candidate_field_ids(db: Session, rover: Rover) -> list[uuid.UUID]:
    return [
        a.field_id
        for a in db.query(RoverFieldAssignment).filter(RoverFieldAssignment.rover_id == rover.id).all()
    ]


def _active_scan_session(db: Session, rover: Rover, field_id: uuid.UUID | None) -> ScanSession | None:
    q = db.query(ScanSession).filter(ScanSession.rover_id == rover.id, ScanSession.status == "ACTIVE")
    if field_id:
        q = q.filter(ScanSession.field_id == field_id)
    return q.order_by(ScanSession.started_at.desc()).first()


def ingest_telemetry(db: Session, rover: Rover, payload: RoverTelemetryIn) -> dict:
    candidate_fields = _candidate_field_ids(db, rover)
    field_id, zone_id = locate_point(db, payload.gps.latitude, payload.gps.longitude, candidate_fields)

    session = None
    if payload.scan_session_id:
        session = db.get(ScanSession, payload.scan_session_id)
    elif field_id:
        session = _active_scan_session(db, rover, field_id)

    position = RoverPosition(
        rover_id=rover.id,
        scan_session_id=session.id if session else None,
        location=from_shape(Point(payload.gps.longitude, payload.gps.latitude), srid=4326),
        latitude=payload.gps.latitude,
        longitude=payload.gps.longitude,
        accuracy_m=payload.gps.accuracy_m,
        altitude_m=payload.gps.altitude_m,
        speed_mps=payload.gps.speed_mps,
        heading_deg=payload.gps.heading_deg,
        timestamp=payload.timestamp,
        field_id=field_id,
        zone_id=zone_id,
    )
    db.add(position)

    latest_detection = None
    observation = None
    if payload.camera or payload.cnn:
        observation = CameraObservation(
            rover_id=rover.id,
            scan_session_id=session.id if session else None,
            camera_id=payload.camera.camera_id if payload.camera else None,
            frame_id=payload.camera.frame_id if payload.camera else None,
            image_uri=payload.camera.image_uri if payload.camera else None,
            location=from_shape(Point(payload.gps.longitude, payload.gps.latitude), srid=4326),
            latitude=payload.gps.latitude,
            longitude=payload.gps.longitude,
            timestamp=payload.timestamp,
            field_id=field_id,
            zone_id=zone_id,
        )
        db.add(observation)
        db.flush()

        if payload.cnn:
            detection = CNNDetection(
                observation_id=observation.id,
                detection_type=payload.cnn.detection_type,
                class_name=payload.cnn.class_name,
                confidence=payload.cnn.confidence,
                severity=payload.cnn.severity,
                model_name=payload.cnn.model_name,
                model_version=payload.cnn.model_version,
                bounding_box=payload.cnn.bounding_box,
                created_at=payload.timestamp,
            )
            db.add(detection)
            db.flush()
            evaluate_detection_alert(db, detection, observation)
            latest_detection = {
                "detection_type": detection.detection_type,
                "class_name": detection.class_name,
                "confidence": detection.confidence,
            }

    if payload.rover:
        if payload.rover.status:
            rover.status = payload.rover.status
        if payload.rover.sprayer_status:
            rover.sprayer_status = payload.rover.sprayer_status
        if payload.rover.battery_level is not None:
            rover.battery_level = payload.rover.battery_level
        if payload.rover.firmware_version:
            rover.firmware_version = payload.rover.firmware_version
    rover.last_seen_at = datetime.now(timezone.utc)

    db.commit()

    return {
        "rover_id": str(rover.id),
        "device_id": rover.device_id,
        "status": rover.status,
        "sprayer_status": rover.sprayer_status,
        "battery_level": rover.battery_level,
        "latitude": payload.gps.latitude,
        "longitude": payload.gps.longitude,
        "speed_mps": payload.gps.speed_mps,
        "heading_deg": payload.gps.heading_deg,
        "field_id": str(field_id) if field_id else None,
        "zone_id": str(zone_id) if zone_id else None,
        "scan_session_id": str(session.id) if session else None,
        "latest_detection": latest_detection,
        "connection_status": "CONNECTED",
        "last_update_at": rover.last_seen_at.isoformat(),
    }


def ingest_sensor(db: Session, rover: Rover, payload: SensorReadingIn) -> None:
    candidate_fields = _candidate_field_ids(db, rover)
    field_id = payload.field_id
    zone_id = None
    location = None
    lat = lon = None

    if payload.gps:
        lat, lon = payload.gps.latitude, payload.gps.longitude
        location = from_shape(Point(lon, lat), srid=4326)
        located_field, zone_id = locate_point(db, lat, lon, candidate_fields)
        field_id = field_id or located_field
    elif field_id is None and candidate_fields:
        field_id = candidate_fields[0]

    reading = EnvironmentalReading(
        field_id=field_id,
        zone_id=zone_id,
        rover_id=rover.id,
        sensor_id=payload.sensor_id,
        reading_type=payload.reading_type,
        value=payload.value,
        unit=payload.unit,
        location=location,
        latitude=lat,
        longitude=lon,
        timestamp=payload.timestamp,
    )
    db.add(reading)
    rover.last_seen_at = datetime.now(timezone.utc)
    db.commit()

    if field_id and payload.reading_type == "SOIL_MOISTURE":
        from app.services.irrigation_engine import evaluate_irrigation

        evaluate_irrigation(db, field_id, zone_id)
        db.commit()


def ingest_spray(db: Session, rover: Rover, payload: SprayEventIn) -> None:
    candidate_fields = _candidate_field_ids(db, rover)
    field_id, zone_id = locate_point(db, payload.location.latitude, payload.location.longitude, candidate_fields)

    event = SprayEvent(
        field_id=field_id or (candidate_fields[0] if candidate_fields else None),
        zone_id=zone_id,
        rover_id=rover.id,
        recommendation_id=payload.recommendation_id,
        location=from_shape(Point(payload.location.longitude, payload.location.latitude), srid=4326),
        latitude=payload.location.latitude,
        longitude=payload.location.longitude,
        status=payload.event,
        completed_at=payload.timestamp,
        duration_seconds=payload.duration_seconds,
        quantity_ml=payload.quantity_ml,
    )
    db.add(event)

    if payload.recommendation_id:
        from app.models.spray import SprayRecommendation

        rec = db.get(SprayRecommendation, payload.recommendation_id)
        if rec and payload.event == "SPRAY_COMPLETED":
            rec.status = "ACTIONED"

    rover.sprayer_status = "SPRAYING" if payload.event == "SPRAY_STARTED" else "OFF"
    rover.last_seen_at = datetime.now(timezone.utc)
    db.commit()


def ingest_irrigation(db: Session, rover: Rover, payload: IrrigationEventIn) -> None:
    event = (
        db.query(IrrigationEvent)
        .filter(IrrigationEvent.field_id == payload.field_id, IrrigationEvent.status == "IN_PROGRESS")
        .order_by(IrrigationEvent.started_at.desc())
        .first()
        if payload.event == "IRRIGATION_COMPLETED"
        else None
    )

    if payload.event == "IRRIGATION_STARTED":
        event = IrrigationEvent(
            field_id=payload.field_id,
            zone_id=payload.zone_id,
            source=payload.source,
            status="IN_PROGRESS",
            started_at=payload.timestamp,
        )
        db.add(event)
    elif event:
        event.status = "COMPLETED"
        event.ended_at = payload.timestamp
        event.water_volume_l = payload.water_volume_l
    else:
        db.add(
            IrrigationEvent(
                field_id=payload.field_id,
                zone_id=payload.zone_id,
                source=payload.source,
                status="COMPLETED",
                started_at=payload.timestamp,
                ended_at=payload.timestamp,
                water_volume_l=payload.water_volume_l,
            )
        )

    rover.last_seen_at = datetime.now(timezone.utc)
    db.commit()


def ingest_scan_session(db: Session, rover: Rover, payload: ScanSessionEventIn) -> None:
    if payload.event == "SCAN_START":
        db.add(
            ScanSession(
                rover_id=rover.id,
                field_id=payload.field_id,
                started_at=payload.timestamp,
                status="ACTIVE",
            )
        )
        rover.status = "SCANNING"
    else:
        session = _active_scan_session(db, rover, payload.field_id)
        if session:
            session.ended_at = payload.timestamp
            session.status = "INTERRUPTED" if payload.interrupted else "COMPLETED"
            session.interrupted = payload.interrupted
        rover.status = "IDLE"

    rover.last_seen_at = datetime.now(timezone.utc)
    db.commit()
