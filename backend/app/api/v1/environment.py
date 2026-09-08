import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from geoalchemy2.shape import to_shape
from sqlalchemy.orm import Session

from app.api.deps import get_owned_field
from app.db.session import get_db
from app.models.environment import WeatherObservation
from app.models.field import Field
from app.models.irrigation import IrrigationEvent
from app.models.spray import SprayEvent
from app.schemas.environment import (
    EnvironmentalRiskOut,
    IrrigationEventOut,
    IrrigationRecommendationOut,
    SprayEventOut,
    WaterUsageOut,
)
from app.services.environmental_risk import evaluate_environmental_risk
from app.services.irrigation_engine import evaluate_irrigation
from app.services.weather_client import WeatherFetchError, fetch_current_and_forecast

router = APIRouter(prefix="/fields/{field_id}", tags=["environment"])


@router.get("/irrigation", response_model=IrrigationRecommendationOut)
def get_irrigation_recommendation(
    field: Field = Depends(get_owned_field), db: Session = Depends(get_db), zone_id: uuid.UUID | None = None
):
    return evaluate_irrigation(db, field.id, zone_id)


@router.get("/environmental-risk", response_model=EnvironmentalRiskOut)
def get_environmental_risk(field: Field = Depends(get_owned_field), db: Session = Depends(get_db)):
    return evaluate_environmental_risk(db, field.id)


@router.post("/weather/refresh", response_model=EnvironmentalRiskOut)
async def refresh_weather(field: Field = Depends(get_owned_field), db: Session = Depends(get_db)):
    if field.boundary is None:
        raise HTTPException(status_code=400, detail="Field has no boundary to derive a location from")
    centroid = to_shape(field.boundary).centroid

    try:
        data = await fetch_current_and_forecast(centroid.y, centroid.x)
    except WeatherFetchError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=502, detail="Weather provider request failed")

    db.add(WeatherObservation(field_id=field.id, **data))
    db.commit()

    evaluate_irrigation(db, field.id)
    risk = evaluate_environmental_risk(db, field.id)
    db.commit()
    return risk


@router.get("/irrigation-events", response_model=list[IrrigationEventOut])
def list_irrigation_events(field: Field = Depends(get_owned_field), db: Session = Depends(get_db)):
    events = (
        db.query(IrrigationEvent)
        .filter(IrrigationEvent.field_id == field.id)
        .order_by(IrrigationEvent.started_at.desc())
        .limit(200)
        .all()
    )
    return events


@router.get("/spray-events", response_model=list[SprayEventOut])
def list_spray_events(field: Field = Depends(get_owned_field), db: Session = Depends(get_db)):
    events = (
        db.query(SprayEvent)
        .filter(SprayEvent.field_id == field.id, SprayEvent.status == "SPRAY_COMPLETED")
        .order_by(SprayEvent.completed_at.desc())
        .limit(200)
        .all()
    )
    return events


@router.get("/water-usage", response_model=WaterUsageOut)
def water_usage(field: Field = Depends(get_owned_field), db: Session = Depends(get_db), days: int = 30):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    events = (
        db.query(IrrigationEvent)
        .filter(IrrigationEvent.field_id == field.id, IrrigationEvent.started_at >= since, IrrigationEvent.water_volume_l.isnot(None))
        .all()
    )
    total = sum(e.water_volume_l or 0 for e in events)
    area = field.area_m2 or 1.0
    return WaterUsageOut(
        field_id=field.id,
        total_water_l=round(total, 1),
        irrigated_area_m2=round(area, 1),
        water_usage_per_m2=round(total / area, 3) if area else 0.0,
        irrigation_saving_estimate_pct=None,
    )
