import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.field import Field
from app.models.observation import CameraObservation, CNNDetection
from app.models.zone import Zone
from app.services.alerts_engine import upsert_alert

CONFIDENCE_ALERT_THRESHOLD = 0.55
RECENT_WINDOW = timedelta(hours=24)
INCREASING_COUNT_THRESHOLD = 3

TYPE_LABEL = {
    "DISEASE": "Possible disease detected",
    "PEST": "Pest activity detected",
    "NUTRIENT_DEFICIENCY": "Possible nutrient deficiency",
}
ALERT_TYPE_MAP = {"DISEASE": "DISEASE", "PEST": "PEST", "NUTRIENT_DEFICIENCY": "NUTRIENT"}


def evaluate_detection_alert(db: Session, detection: CNNDetection, observation: CameraObservation) -> None:
    if detection.detection_type not in TYPE_LABEL:
        return
    if detection.confidence < CONFIDENCE_ALERT_THRESHOLD:
        return
    if observation.field_id is None:
        return

    since = datetime.now(timezone.utc) - RECENT_WINDOW
    recent_count = (
        db.query(func.count(CNNDetection.id))
        .join(CameraObservation, CNNDetection.observation_id == CameraObservation.id)
        .filter(
            CameraObservation.field_id == observation.field_id,
            CameraObservation.zone_id == observation.zone_id,
            CNNDetection.detection_type == detection.detection_type,
            CNNDetection.class_name == detection.class_name,
            CNNDetection.created_at >= since,
        )
        .scalar()
    )

    zone_code = None
    if observation.zone_id:
        zone = db.get(Zone, observation.zone_id)
        zone_code = zone.code if zone else None
    where_label = f"Zone {zone_code}" if zone_code else "Field"

    increasing = recent_count >= INCREASING_COUNT_THRESHOLD
    severity = "HIGH" if (increasing or detection.confidence >= 0.85) else "MODERATE"

    class_label = detection.class_name.replace("_", " ")
    if increasing:
        message = f"{TYPE_LABEL[detection.detection_type]} increasing in {where_label}: {class_label} ({recent_count} observations in 24h)"
        what = f"{class_label.title()} activity increasing"
    else:
        message = f"{TYPE_LABEL[detection.detection_type]} in {where_label}: {class_label} (confidence {detection.confidence:.0%})"
        what = TYPE_LABEL[detection.detection_type]

    action = {
        "DISEASE": "Inspect the affected area and treat if confirmed.",
        "PEST": "Inspect the area; consider targeted treatment if infestation is confirmed.",
        "NUTRIENT_DEFICIENCY": "Inspect crop for nutrient stress; consider soil/leaf testing before fertilizing.",
    }[detection.detection_type]

    dedup_key = f"{ALERT_TYPE_MAP[detection.detection_type]}:{observation.field_id}:{observation.zone_id}:{detection.class_name}"

    upsert_alert(
        db,
        field_id=observation.field_id,
        zone_id=observation.zone_id,
        alert_type=ALERT_TYPE_MAP[detection.detection_type],
        severity=severity,
        message=message,
        dedup_key=dedup_key,
        recommended_action=action,
        where_label=where_label,
        what=what,
    )
