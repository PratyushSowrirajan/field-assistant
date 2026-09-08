import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.environment import WeatherObservation
from app.models.observation import CameraObservation, CNNDetection
from app.schemas.environment import EnvironmentalRiskOut
from app.services.alerts_engine import resolve_alerts_matching, upsert_alert

HEAT_MODERATE_C = 35.0
HEAT_HIGH_C = 38.0
HEAT_CRITICAL_C = 42.0

FLOOD_MODERATE_MM = 25.0
FLOOD_HIGH_MM = 50.0

DROUGHT_LOOKBACK = timedelta(days=7)
DISEASE_HUMIDITY_PCT = 80.0
DISEASE_TEMP_RANGE = (20.0, 32.0)


def _recent_weather(db: Session, field_id: uuid.UUID, since: datetime) -> list[WeatherObservation]:
    return (
        db.query(WeatherObservation)
        .filter(WeatherObservation.field_id == field_id, WeatherObservation.fetched_at >= since)
        .order_by(WeatherObservation.fetched_at.desc())
        .all()
    )


def evaluate_environmental_risk(db: Session, field_id: uuid.UUID) -> EnvironmentalRiskOut:
    now = datetime.now(timezone.utc)
    latest = (
        db.query(WeatherObservation)
        .filter(WeatherObservation.field_id == field_id)
        .order_by(WeatherObservation.fetched_at.desc())
        .first()
    )
    recent = _recent_weather(db, field_id, now - DROUGHT_LOOKBACK)

    heat_risk = "NONE"
    flood_risk = "LOW"
    drought_risk = "LOW"
    disease_env_risk = "LOW"

    if latest:
        temp = latest.temperature_c or 0
        if temp >= HEAT_CRITICAL_C:
            heat_risk = "CRITICAL"
        elif temp >= HEAT_HIGH_C:
            heat_risk = "HIGH"
        elif temp >= HEAT_MODERATE_C:
            heat_risk = "MODERATE"

        forecast = latest.forecast_rainfall_mm or 0
        if forecast >= FLOOD_HIGH_MM:
            flood_risk = "HIGH"
        elif forecast >= FLOOD_MODERATE_MM:
            flood_risk = "MODERATE"

        humidity = latest.humidity_pct or 0
        if humidity >= DISEASE_HUMIDITY_PCT and DISEASE_TEMP_RANGE[0] <= temp <= DISEASE_TEMP_RANGE[1]:
            disease_env_risk = "MODERATE"
            recent_disease = (
                db.query(CNNDetection)
                .join(CameraObservation, CNNDetection.observation_id == CameraObservation.id)
                .filter(
                    CameraObservation.field_id == field_id,
                    CNNDetection.detection_type == "DISEASE",
                    CNNDetection.created_at >= now - timedelta(days=3),
                )
                .first()
            )
            if recent_disease:
                disease_env_risk = "HIGH"

    if recent:
        cumulative_rain = sum((w.rainfall_mm or 0) for w in recent)
        avg_temp = sum((w.temperature_c or 0) for w in recent) / len(recent)
        if cumulative_rain < 5 and avg_temp >= 30:
            drought_risk = "HIGH"
        elif cumulative_rain < 15:
            drought_risk = "MODERATE"

    prefix = f"HEAT:{field_id}"
    if heat_risk in ("HIGH", "CRITICAL"):
        upsert_alert(
            db, field_id, None, "HEAT", heat_risk,
            f"Heat risk {heat_risk.lower()}: expected high heat exposure today.",
            f"{prefix}", "Monitor crop stress and follow crop-specific advisory.",
            "Field", "Heat-stress warning",
        )
    else:
        resolve_alerts_matching(db, prefix)

    prefix = f"FLOOD:{field_id}"
    if flood_risk in ("MODERATE", "HIGH"):
        upsert_alert(
            db, field_id, None, "FLOOD", flood_risk,
            f"Flood risk {flood_risk.lower()}: heavy rainfall forecast (~{latest.forecast_rainfall_mm:.0f}mm).",
            f"{prefix}", "Check field drainage and low-lying zones.",
            "Field", "Flood-risk alert",
        )
    else:
        resolve_alerts_matching(db, prefix)

    prefix = f"DROUGHT:{field_id}"
    if drought_risk == "HIGH":
        upsert_alert(
            db, field_id, None, "DROUGHT", "HIGH",
            "Drought risk high: low rainfall and sustained high temperatures.",
            f"{prefix}", "Prioritize irrigation and monitor soil moisture closely.",
            "Field", "Drought-risk alert",
        )
    else:
        resolve_alerts_matching(db, prefix)

    return EnvironmentalRiskOut(
        field_id=field_id,
        drought_risk=drought_risk,
        flood_risk=flood_risk,
        heat_risk=heat_risk,
        disease_environment_risk=disease_env_risk,
    )
