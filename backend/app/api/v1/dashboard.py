from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_farmer
from app.db.session import get_db
from app.models.alert import Alert
from app.models.farm import Farm
from app.models.field import Field
from app.models.observation import CameraObservation
from app.models.rover import Rover, RoverFieldAssignment
from app.models.user import Farmer
from app.schemas.dashboard import DashboardFieldCard, DashboardSummary
from app.services import analytics_service
from app.api.v1.alerts import _alert_out

router = APIRouter(tags=["dashboard"])

ATTENTION_STATUSES = {"ATTENTION", "HIGH_RISK", "CRITICAL"}


@router.get("/dashboard", response_model=DashboardSummary)
def get_dashboard(farmer: Farmer = Depends(get_current_farmer), db: Session = Depends(get_db)):
    fields = (
        db.query(Field)
        .join(Farm, Field.farm_id == Farm.id)
        .filter(Farm.farmer_id == farmer.id, Field.archived.is_(False))
        .all()
    )
    field_ids = [f.id for f in fields]

    cards: list[DashboardFieldCard] = []
    attention_count = 0
    for field in fields:
        health = analytics_service.field_health(db, field)
        if health.status in ATTENTION_STATUSES:
            attention_count += 1

        top_alert = (
            db.query(Alert)
            .filter(Alert.field_id == field.id, Alert.status == "ACTIVE")
            .order_by(Alert.severity.desc(), Alert.last_seen_at.desc())
            .first()
        )
        last_scan = (
            db.query(CameraObservation.timestamp)
            .filter(CameraObservation.field_id == field.id)
            .order_by(CameraObservation.timestamp.desc())
            .first()
        )
        active_rover = (
            db.query(Rover)
            .join(RoverFieldAssignment, RoverFieldAssignment.rover_id == Rover.id)
            .filter(RoverFieldAssignment.field_id == field.id, Rover.status.notin_(["OFFLINE"]))
            .first()
        )

        cards.append(
            DashboardFieldCard(
                id=field.id,
                name=field.name,
                crop_type=field.crop_type,
                area_m2=field.area_m2,
                health_status=health.status,
                top_issue=top_alert.message if top_alert else None,
                last_scan_at=last_scan[0] if last_scan else None,
                rover_status=active_rover.status if active_rover else None,
            )
        )

    alerts_q = db.query(Alert).filter(Alert.field_id.in_(field_ids), Alert.status == "ACTIVE") if field_ids else None
    active_alerts = alerts_q.all() if alerts_q is not None else []

    disease_pest = sum(1 for a in active_alerts if a.type in ("DISEASE", "PEST", "NUTRIENT"))
    water_stress = sum(1 for a in active_alerts if a.type in ("IRRIGATION", "OVER_IRRIGATION"))
    environmental = sum(1 for a in active_alerts if a.type in ("DROUGHT", "FLOOD", "HEAT"))

    severity_order = {"CRITICAL": 0, "HIGH": 1, "MODERATE": 2, "LOW": 3}
    top_alerts_sorted = sorted(active_alerts, key=lambda a: severity_order.get(a.severity, 4))[:6]

    active_rover_count = (
        db.query(Rover).filter(Rover.farmer_id == farmer.id, Rover.status.notin_(["OFFLINE"])).count()
    )

    return DashboardSummary(
        total_fields=len(fields),
        fields_requiring_attention=attention_count,
        active_alerts=len(active_alerts),
        disease_pest_alerts=disease_pest,
        water_stress_alerts=water_stress,
        environmental_alerts=environmental,
        fields=cards,
        top_alerts=[_alert_out(a, db) for a in top_alerts_sorted],
        active_rover_count=active_rover_count,
    )
