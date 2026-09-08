from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_rover
from app.db.session import get_db
from app.models.edge_event import EdgeEvent
from app.models.rover import Rover
from app.schemas.edge import (
    EdgeBatchResponse,
    EdgeEventAck,
    EdgeEventEnvelope,
    IrrigationEventIn,
    RoverTelemetryIn,
    ScanSessionEventIn,
    SensorReadingIn,
    SprayEventIn,
)
from app.services import edge_ingest
from app.ws.manager import manager

router = APIRouter(prefix="/edge", tags=["edge"])


@router.post("/telemetry")
async def post_telemetry(payload: RoverTelemetryIn, rover: Rover = Depends(get_current_rover), db: Session = Depends(get_db)):
    state = edge_ingest.ingest_telemetry(db, rover, payload)
    await manager.broadcast(rover.farmer_id, {"type": "rover_telemetry", "data": state})
    return state


@router.post("/sensors", status_code=202)
def post_sensor(payload: SensorReadingIn, rover: Rover = Depends(get_current_rover), db: Session = Depends(get_db)):
    edge_ingest.ingest_sensor(db, rover, payload)
    return {"status": "accepted"}


@router.post("/spray", status_code=202)
def post_spray(payload: SprayEventIn, rover: Rover = Depends(get_current_rover), db: Session = Depends(get_db)):
    edge_ingest.ingest_spray(db, rover, payload)
    return {"status": "accepted"}


@router.post("/irrigation", status_code=202)
def post_irrigation(payload: IrrigationEventIn, rover: Rover = Depends(get_current_rover), db: Session = Depends(get_db)):
    edge_ingest.ingest_irrigation(db, rover, payload)
    return {"status": "accepted"}


@router.post("/scan-session", status_code=202)
def post_scan_session(payload: ScanSessionEventIn, rover: Rover = Depends(get_current_rover), db: Session = Depends(get_db)):
    edge_ingest.ingest_scan_session(db, rover, payload)
    return {"status": "accepted"}


@router.post("/events", response_model=EdgeBatchResponse)
async def post_batch_events(
    envelopes: list[EdgeEventEnvelope], rover: Rover = Depends(get_current_rover), db: Session = Depends(get_db)
):
    """Offline/batched sync endpoint (PRD section 42). Deduplicates by event_id and
    preserves original timestamps so historical data stays accurate after reconnection."""
    results: list[EdgeEventAck] = []

    for env in envelopes:
        existing = db.query(EdgeEvent).filter(EdgeEvent.event_id == env.event_id).first()
        if existing:
            results.append(EdgeEventAck(event_id=env.event_id, status="DUPLICATE"))
            continue

        try:
            if env.event_type == "TELEMETRY":
                telemetry = RoverTelemetryIn(device_id=env.device_id, timestamp=env.timestamp, **env.payload)
                state = edge_ingest.ingest_telemetry(db, rover, telemetry)
                await manager.broadcast(rover.farmer_id, {"type": "rover_telemetry", "data": state})
            elif env.event_type == "SENSOR_READING":
                edge_ingest.ingest_sensor(
                    db, rover, SensorReadingIn(device_id=env.device_id, timestamp=env.timestamp, **env.payload)
                )
            elif env.event_type == "SPRAY_EVENT":
                edge_ingest.ingest_spray(
                    db, rover, SprayEventIn(device_id=env.device_id, timestamp=env.timestamp, **env.payload)
                )
            elif env.event_type == "IRRIGATION_EVENT":
                edge_ingest.ingest_irrigation(
                    db, rover, IrrigationEventIn(device_id=env.device_id, timestamp=env.timestamp, **env.payload)
                )
            elif env.event_type == "SCAN_SESSION_EVENT":
                edge_ingest.ingest_scan_session(
                    db, rover, ScanSessionEventIn(device_id=env.device_id, timestamp=env.timestamp, **env.payload)
                )

            db.add(
                EdgeEvent(
                    event_id=env.event_id,
                    device_id=env.device_id,
                    rover_id=rover.id,
                    event_type=env.event_type,
                    payload=env.payload,
                    original_timestamp=env.timestamp,
                    received_at=datetime.now(timezone.utc),
                    sync_status="SYNCED",
                )
            )
            db.commit()
            results.append(EdgeEventAck(event_id=env.event_id, status="SYNCED"))
        except Exception as exc:  # noqa: BLE001 - must never let one bad event break the batch
            db.rollback()
            db.add(
                EdgeEvent(
                    event_id=env.event_id,
                    device_id=env.device_id,
                    rover_id=rover.id,
                    event_type=env.event_type,
                    payload=env.payload,
                    original_timestamp=env.timestamp,
                    received_at=datetime.now(timezone.utc),
                    sync_status="FAILED",
                    error=str(exc)[:500],
                )
            )
            db.commit()
            results.append(EdgeEventAck(event_id=env.event_id, status="FAILED", error=str(exc)[:200]))

    return EdgeBatchResponse(results=results)
