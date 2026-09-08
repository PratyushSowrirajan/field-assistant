import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.environment import EnvironmentalReading, WeatherObservation
from app.models.zone import Zone
from app.schemas.environment import IrrigationRecommendationOut
from app.services.alerts_engine import resolve_alerts_matching, upsert_alert

# Configurable thresholds (percent soil moisture, mm forecast rainfall).
DRY_THRESHOLD = 30.0
CRITICAL_DRY_THRESHOLD = 20.0
WET_THRESHOLD = 60.0
OVER_IRRIGATION_THRESHOLD = 80.0
OVER_IRRIGATION_CRITICAL = 90.0
RAIN_SOON_MM = 10.0
LOOKBACK = timedelta(hours=48)


def _latest_moisture(db: Session, field_id: uuid.UUID, zone_id: uuid.UUID | None):
    q = db.query(EnvironmentalReading).filter(
        EnvironmentalReading.field_id == field_id,
        EnvironmentalReading.reading_type == "SOIL_MOISTURE",
        EnvironmentalReading.timestamp >= datetime.now(timezone.utc) - LOOKBACK,
    )
    if zone_id:
        q = q.filter(EnvironmentalReading.zone_id == zone_id)
    return q.order_by(EnvironmentalReading.timestamp.desc()).first()


def _latest_weather(db: Session, field_id: uuid.UUID) -> WeatherObservation | None:
    return (
        db.query(WeatherObservation)
        .filter(WeatherObservation.field_id == field_id)
        .order_by(WeatherObservation.fetched_at.desc())
        .first()
    )


def evaluate_irrigation(db: Session, field_id: uuid.UUID, zone_id: uuid.UUID | None = None) -> IrrigationRecommendationOut:
    moisture_reading = _latest_moisture(db, field_id, zone_id)
    weather = _latest_weather(db, field_id)

    moisture = moisture_reading.value if moisture_reading else None
    forecast_rain = weather.forecast_rainfall_mm if weather else None
    temperature = weather.temperature_c if weather else None
    humidity = weather.humidity_pct if weather else None

    if moisture is None:
        recommendation, water_stress, over_irrigation, reason = (
            "UNKNOWN",
            "NONE",
            "NORMAL",
            "No recent soil moisture reading available for this field.",
        )
    else:
        rain_expected = (forecast_rain or 0) >= RAIN_SOON_MM

        if moisture < CRITICAL_DRY_THRESHOLD and not rain_expected:
            recommendation = "IRRIGATE_NOW"
            water_stress = "HIGH"
            reason = f"Soil moisture is critically low ({moisture:.0f}%) with little rain forecast."
        elif moisture < DRY_THRESHOLD and not rain_expected:
            recommendation = "IRRIGATE_SOON"
            water_stress = "MODERATE"
            reason = f"Soil moisture is low ({moisture:.0f}%)."
        elif rain_expected and moisture < WET_THRESHOLD:
            recommendation = "DELAY"
            water_stress = "LOW"
            reason = f"Rain expected soon (~{forecast_rain:.0f}mm); delaying irrigation conserves water."
        elif moisture >= WET_THRESHOLD:
            recommendation = "NO_IRRIGATION"
            water_stress = "NONE"
            reason = f"Soil moisture is adequate to high ({moisture:.0f}%)."
        else:
            recommendation = "NO_IRRIGATION"
            water_stress = "LOW"
            reason = f"Soil moisture is adequate ({moisture:.0f}%)."

        if moisture >= OVER_IRRIGATION_CRITICAL:
            over_irrigation = "HIGH_RISK"
        elif moisture >= OVER_IRRIGATION_THRESHOLD:
            over_irrigation = "POSSIBLE_OVER_IRRIGATION"
        else:
            over_irrigation = "NORMAL"

    dedup_prefix = f"IRRIGATION:{field_id}"
    if moisture is not None and recommendation == "IRRIGATE_NOW":
        upsert_alert(
            db,
            field_id=field_id,
            zone_id=zone_id,
            alert_type="IRRIGATION",
            severity="HIGH",
            message=f"Irrigate now: {reason}",
            dedup_key=f"{dedup_prefix}:NOW",
            recommended_action="Irrigate now.",
            where_label=(f"Zone {db.get(Zone, zone_id).code}" if zone_id else "Field"),
            what="Water stress detected",
        )
    else:
        resolve_alerts_matching(db, f"{dedup_prefix}:NOW")

    if moisture is not None and over_irrigation == "HIGH_RISK":
        upsert_alert(
            db,
            field_id=field_id,
            zone_id=zone_id,
            alert_type="OVER_IRRIGATION",
            severity="MODERATE",
            message=f"Soil moisture very high ({moisture:.0f}%); risk of over-irrigation.",
            dedup_key=f"{dedup_prefix}:OVER",
            recommended_action="Delay irrigation and check drainage.",
            where_label=(f"Zone {db.get(Zone, zone_id).code}" if zone_id else "Field"),
            what="Possible over-irrigation",
        )
    else:
        resolve_alerts_matching(db, f"{dedup_prefix}:OVER")

    return IrrigationRecommendationOut(
        field_id=field_id,
        zone_id=zone_id,
        recommendation=recommendation,
        water_stress_status=water_stress,
        over_irrigation_status=over_irrigation,
        soil_moisture_pct=moisture,
        temperature_c=temperature,
        humidity_pct=humidity,
        forecast_rainfall_mm=forecast_rain,
        reason=reason,
    )
