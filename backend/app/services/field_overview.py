from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.environment import EnvironmentalReading
from app.models.farm import Farm
from app.models.field import Field
from app.models.observation import CameraObservation, CNNDetection
from app.models.rover import Rover, RoverFieldAssignment
from app.models.zone import Zone
from app.schemas.overview import EnvironmentTile, FieldOverviewOut, LatestPrediction, NutrientTile
from app.services.analytics_service import field_health

CONNECTION_TIMEOUT = timedelta(minutes=2)

# Illustrative soil-nutrient ranges (ppm). Configurable placeholders — swap for
# crop-specific agronomic thresholds when that data is available.
NUTRIENT_RANGES = {
    "NITROGEN": {"low": 40, "high": 80, "unit": "ppm", "label": "Nitrogen"},
    "PHOSPHORUS": {"low": 20, "high": 40, "unit": "ppm", "label": "Phosphorus"},
    "POTASSIUM": {"low": 100, "high": 200, "unit": "ppm", "label": "Potassium"},
}

ENV_READING_TYPES = {
    "AIR_TEMPERATURE": {"label": "Temperature", "unit": "°C"},
    "RELATIVE_HUMIDITY": {"label": "Air moisture", "unit": "%"},
    "SOIL_MOISTURE": {"label": "Soil moisture", "unit": "%"},
}


def _nutrient_status(nutrient: str, value: float | None) -> str:
    if value is None:
        return "UNKNOWN"
    r = NUTRIENT_RANGES[nutrient]
    if value < r["low"]:
        return "LOW"
    if value > r["high"]:
        return "HIGH"
    return "OPTIMAL"


HISTORY_POINTS = 8


def _recent_readings(db: Session, field_id, reading_type: str) -> list[EnvironmentalReading]:
    """Newest first — callers reverse for a chronological sparkline."""
    return (
        db.query(EnvironmentalReading)
        .filter(EnvironmentalReading.field_id == field_id, EnvironmentalReading.reading_type == reading_type)
        .order_by(EnvironmentalReading.timestamp.desc())
        .limit(HISTORY_POINTS)
        .all()
    )


def _trend(rows: list[EnvironmentalReading]) -> str:
    if len(rows) < 2:
        return "FLAT"
    diff = rows[0].value - rows[1].value
    if diff > 0:
        return "UP"
    if diff < 0:
        return "DOWN"
    return "FLAT"


def _confidence_label(confidence: float) -> str:
    if confidence >= 0.85:
        return "HIGH"
    if confidence >= 0.6:
        return "MEDIUM"
    return "LOW"


def get_field_overview(db: Session, field: Field) -> FieldOverviewOut:
    farm = db.get(Farm, field.farm_id)
    health = field_health(db, field)

    # Latest AI prediction: most recent detection, enriched with the matching
    # active alert's message when one exists (same story the Alerts page shows).
    latest_row = (
        db.query(CNNDetection, CameraObservation)
        .join(CameraObservation, CNNDetection.observation_id == CameraObservation.id)
        .filter(CameraObservation.field_id == field.id)
        .order_by(CNNDetection.created_at.desc())
        .first()
    )
    latest_prediction = None
    last_scan_at = None
    if latest_row:
        detection, obs = latest_row
        last_scan_at = obs.timestamp
        zone_code = None
        if obs.zone_id:
            zone = db.get(Zone, obs.zone_id)
            zone_code = zone.code if zone else None

        alert = None
        if obs.field_id:
            alert = (
                db.query(Alert)
                .filter(
                    Alert.field_id == obs.field_id,
                    Alert.zone_id == obs.zone_id,
                    Alert.status == "ACTIVE",
                    Alert.dedup_key.like(f"%{detection.class_name}%"),
                )
                .order_by(Alert.last_seen_at.desc())
                .first()
            )

        now = datetime.now(timezone.utc)
        minutes_ago = max(0.0, (now - detection.created_at).total_seconds() / 60)

        latest_prediction = LatestPrediction(
            detection_type=detection.detection_type,
            class_label=detection.class_name.replace("_", " ").title(),
            zone_code=zone_code,
            confidence=detection.confidence,
            confidence_label=_confidence_label(detection.confidence),
            message=alert.message if alert else "Inspect the affected area and confirm before treating.",
            minutes_ago=round(minutes_ago, 1),
        )

    # Connection status: any rover assigned to this field, most recently seen.
    connection_status = "NO_ROVER"
    rover = (
        db.query(Rover)
        .join(RoverFieldAssignment, RoverFieldAssignment.rover_id == Rover.id)
        .filter(RoverFieldAssignment.field_id == field.id)
        .order_by(Rover.last_seen_at.desc().nulls_last())
        .first()
    )
    if rover:
        connected = bool(rover.last_seen_at and datetime.now(timezone.utc) - rover.last_seen_at < CONNECTION_TIMEOUT)
        connection_status = "CONNECTED" if connected else "OFFLINE"

    environment: list[EnvironmentTile] = []
    for reading_type, meta in ENV_READING_TYPES.items():
        rows = _recent_readings(db, field.id, reading_type)
        environment.append(
            EnvironmentTile(
                label=meta["label"],
                value=rows[0].value if rows else None,
                unit=meta["unit"],
                trend=_trend(rows),
                history=[r.value for r in reversed(rows)],
            )
        )

    nutrients: list[NutrientTile] = []
    for nutrient, meta in NUTRIENT_RANGES.items():
        rows = _recent_readings(db, field.id, nutrient)
        value = rows[0].value if rows else None
        delta = round(rows[0].value - rows[1].value, 1) if len(rows) >= 2 else None
        nutrients.append(
            NutrientTile(
                nutrient=nutrient,
                label=meta["label"],
                value=value,
                unit=meta["unit"],
                status=_nutrient_status(nutrient, value),
                delta_vs_previous=delta,
                low_threshold=meta["low"],
                high_threshold=meta["high"],
                display_max=round(meta["high"] * 1.6, 1),
                history=[r.value for r in reversed(rows)],
            )
        )

    return FieldOverviewOut(
        field_id=field.id,
        field_name=field.name,
        farm_name=farm.name if farm else "",
        crop_type=field.crop_type,
        growth_stage=field.growth_stage,
        area_m2=field.area_m2,
        health_status=health.status,
        health_score=health.score,
        connection_status=connection_status,
        last_scan_at=last_scan_at,
        latest_prediction=latest_prediction,
        environment=environment,
        nutrients=nutrients,
    )
