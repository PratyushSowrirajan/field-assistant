import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_farmer
from app.db.session import get_db
from app.models.alert import Advisory, Alert
from app.models.farm import Farm
from app.models.field import Field
from app.models.user import Farmer
from app.models.zone import Zone
from app.schemas.alert import AdvisoryOut, AlertOut

router = APIRouter(tags=["alerts"])


def _farmer_field_ids(db: Session, farmer: Farmer) -> list[uuid.UUID]:
    return [
        f.id
        for f in db.query(Field.id).join(Farm, Field.farm_id == Farm.id).filter(Farm.farmer_id == farmer.id).all()
    ]


def _alert_out(alert: Alert, db: Session) -> AlertOut:
    field = db.get(Field, alert.field_id)
    zone_code = None
    if alert.zone_id:
        zone = db.get(Zone, alert.zone_id)
        zone_code = zone.code if zone else None
    return AlertOut(
        id=alert.id,
        field_id=alert.field_id,
        zone_id=alert.zone_id,
        zone_code=zone_code,
        field_name=field.name if field else None,
        type=alert.type,
        severity=alert.severity,
        message=alert.message,
        status=alert.status,
        acknowledged=alert.acknowledged,
        created_at=alert.created_at,
        last_seen_at=alert.last_seen_at,
    )


@router.get("/alerts", response_model=list[AlertOut])
def list_alerts(
    farmer: Farmer = Depends(get_current_farmer),
    db: Session = Depends(get_db),
    field_id: uuid.UUID | None = None,
    severity: str | None = None,
    status: str | None = "ACTIVE",
    alert_type: str | None = None,
):
    field_ids = _farmer_field_ids(db, farmer)
    if not field_ids:
        return []

    q = db.query(Alert).filter(Alert.field_id.in_(field_ids))
    if field_id:
        q = q.filter(Alert.field_id == field_id)
    if severity:
        q = q.filter(Alert.severity == severity)
    if status:
        q = q.filter(Alert.status == status)
    if alert_type:
        q = q.filter(Alert.type == alert_type)

    severity_order = {"CRITICAL": 0, "HIGH": 1, "MODERATE": 2, "LOW": 3}
    alerts = q.order_by(Alert.last_seen_at.desc()).limit(200).all()
    alerts.sort(key=lambda a: severity_order.get(a.severity, 4))
    return [_alert_out(a, db) for a in alerts]


@router.post("/alerts/{alert_id}/acknowledge", response_model=AlertOut)
def acknowledge_alert(alert_id: uuid.UUID, farmer: Farmer = Depends(get_current_farmer), db: Session = Depends(get_db)):
    alert = db.get(Alert, alert_id)
    if alert is None or alert.field_id not in _farmer_field_ids(db, farmer):
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.acknowledged = True
    alert.status = "ACKNOWLEDGED"
    db.commit()
    db.refresh(alert)
    return _alert_out(alert, db)


@router.post("/alerts/{alert_id}/resolve", response_model=AlertOut)
def resolve_alert(alert_id: uuid.UUID, farmer: Farmer = Depends(get_current_farmer), db: Session = Depends(get_db)):
    alert = db.get(Alert, alert_id)
    if alert is None or alert.field_id not in _farmer_field_ids(db, farmer):
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = "RESOLVED"
    db.commit()
    db.refresh(alert)
    return _alert_out(alert, db)


@router.get("/advisories", response_model=list[AdvisoryOut])
def list_advisories(
    farmer: Farmer = Depends(get_current_farmer),
    db: Session = Depends(get_db),
    field_id: uuid.UUID | None = None,
):
    field_ids = _farmer_field_ids(db, farmer)
    if not field_ids:
        return []
    q = db.query(Advisory).filter(Advisory.field_id.in_(field_ids))
    if field_id:
        q = q.filter(Advisory.field_id == field_id)
    advisories = q.order_by(Advisory.created_at.desc()).limit(100).all()
    return [AdvisoryOut(**a.__dict__) for a in advisories]


@router.post("/advisories/{advisory_id}/mark-actioned", response_model=AdvisoryOut)
def mark_advisory_actioned(advisory_id: uuid.UUID, farmer: Farmer = Depends(get_current_farmer), db: Session = Depends(get_db)):
    advisory = db.get(Advisory, advisory_id)
    if advisory is None or advisory.field_id not in _farmer_field_ids(db, farmer):
        raise HTTPException(status_code=404, detail="Advisory not found")
    advisory.action_taken = True
    db.commit()
    db.refresh(advisory)
    return AdvisoryOut(**advisory.__dict__)
