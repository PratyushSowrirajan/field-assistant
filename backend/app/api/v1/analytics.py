from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_owned_field
from app.db.session import get_db
from app.models.field import Field
from app.schemas.analytics import (
    DecisionInsightOut,
    FieldHealthOut,
    HotspotOut,
    TimeSeriesPoint,
    TreatmentCoverageOut,
    YieldRiskOut,
)
from app.services import analytics_service

router = APIRouter(prefix="/fields/{field_id}", tags=["analytics"])

VALID_METRICS = {
    "disease",
    "pest",
    "nutrient",
    "soil_moisture",
    "temperature",
    "humidity",
    "irrigation",
    "treatment",
}


@router.get("/health", response_model=FieldHealthOut)
def get_field_health(field: Field = Depends(get_owned_field), db: Session = Depends(get_db)):
    return analytics_service.field_health(db, field)


@router.get("/hotspots", response_model=list[HotspotOut])
def get_hotspots(field: Field = Depends(get_owned_field), db: Session = Depends(get_db), detection_type: str | None = None):
    return analytics_service.hotspots(db, field, detection_type)


@router.get("/treatment-coverage", response_model=TreatmentCoverageOut)
def get_treatment_coverage(field: Field = Depends(get_owned_field), db: Session = Depends(get_db), days: int = 30):
    return analytics_service.treatment_coverage(db, field, days)


@router.get("/yield-risk", response_model=YieldRiskOut)
def get_yield_risk(field: Field = Depends(get_owned_field), db: Session = Depends(get_db)):
    return analytics_service.yield_risk(db, field)


@router.get("/insights", response_model=list[DecisionInsightOut])
def get_decision_insights(field: Field = Depends(get_owned_field), db: Session = Depends(get_db)):
    return analytics_service.decision_insights(db, field)


@router.get("/timeseries", response_model=list[TimeSeriesPoint])
def get_time_series(
    field: Field = Depends(get_owned_field), db: Session = Depends(get_db), metric: str = "disease", days: int = 30
):
    if metric not in VALID_METRICS:
        raise HTTPException(status_code=400, detail=f"metric must be one of {sorted(VALID_METRICS)}")
    return analytics_service.time_series_daily(db, field.id, metric, days)
