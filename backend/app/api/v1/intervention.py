import uuid

from fastapi import APIRouter, Depends
from geoalchemy2.shape import from_shape, to_shape
from sqlalchemy.orm import Session

from app.api.deps import get_owned_field
from app.db.session import get_db
from app.models.field import Field
from app.models.spray import SprayRecommendation
from app.models.zone import Zone
from app.services.analytics_service import zone_summary

router = APIRouter(prefix="/fields/{field_id}/spray-recommendations", tags=["intervention"])

TARGET_RISK_LEVELS = {"HIGH", "CRITICAL"}


@router.get("")
def list_spray_recommendations(field: Field = Depends(get_owned_field), db: Session = Depends(get_db)):
    recs = (
        db.query(SprayRecommendation)
        .filter(SprayRecommendation.field_id == field.id)
        .order_by(SprayRecommendation.created_at.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "field_id": r.field_id,
            "zone_id": r.zone_id,
            "reason": r.reason,
            "priority": r.priority,
            "status": r.status,
            "target_latitude": r.target_latitude,
            "target_longitude": r.target_longitude,
            "created_at": r.created_at,
        }
        for r in recs
    ]


@router.post("/generate")
def generate_spray_recommendations(field: Field = Depends(get_owned_field), db: Session = Depends(get_db)):
    """Identify zones with high disease/pest risk and no PENDING recommendation yet,
    then propose a targeted intervention there instead of a blanket field spray."""
    zones = db.query(Zone).filter(Zone.field_id == field.id).all()
    created = []

    for zone in zones:
        summary = zone_summary(db, zone)
        if summary.risk_level not in TARGET_RISK_LEVELS or summary.treatment_status == "TREATED":
            continue

        existing = (
            db.query(SprayRecommendation)
            .filter(SprayRecommendation.zone_id == zone.id, SprayRecommendation.status == "PENDING")
            .first()
        )
        if existing:
            continue

        centroid = to_shape(zone.polygon).centroid
        reason = f"{summary.risk_level.title()} risk in Zone {zone.code} (disease {summary.disease_prevalence_pct}%, pest {summary.pest_prevalence_pct}%, trend {summary.trend.lower()})"
        rec = SprayRecommendation(
            field_id=field.id,
            zone_id=zone.id,
            target_location=from_shape(centroid, srid=4326),
            target_latitude=centroid.y,
            target_longitude=centroid.x,
            reason=reason,
            priority=summary.risk_level,
            status="PENDING",
        )
        db.add(rec)
        created.append(rec)

    db.commit()
    return {"created": len(created), "zone_ids": [r.zone_id for r in created]}


@router.post("/{recommendation_id}/dismiss")
def dismiss_recommendation(recommendation_id: uuid.UUID, field: Field = Depends(get_owned_field), db: Session = Depends(get_db)):
    rec = db.get(SprayRecommendation, recommendation_id)
    if rec and rec.field_id == field.id:
        rec.status = "DISMISSED"
        db.commit()
    return {"status": "ok"}
