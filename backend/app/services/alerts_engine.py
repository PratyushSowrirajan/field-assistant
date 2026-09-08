import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.alert import Advisory, Alert


def upsert_alert(
    db: Session,
    field_id: uuid.UUID,
    zone_id: uuid.UUID | None,
    alert_type: str,
    severity: str,
    message: str,
    dedup_key: str,
    recommended_action: str,
    where_label: str,
    what: str,
) -> Alert:
    """Create a new active alert, or refresh an existing active one with the same
    dedup_key instead of spamming duplicates (PRD section 23: 'Avoid notification spam')."""
    now = datetime.now(timezone.utc)

    existing = (
        db.query(Alert)
        .filter(Alert.dedup_key == dedup_key, Alert.status == "ACTIVE")
        .first()
    )
    if existing:
        existing.severity = severity
        existing.message = message
        existing.last_seen_at = now
        alert = existing
    else:
        alert = Alert(
            field_id=field_id,
            zone_id=zone_id,
            type=alert_type,
            severity=severity,
            message=message,
            status="ACTIVE",
            dedup_key=dedup_key,
            last_seen_at=now,
        )
        db.add(alert)
        db.flush()

        db.add(
            Advisory(
                alert_id=alert.id,
                field_id=field_id,
                zone_id=zone_id,
                what=what,
                where_label=where_label,
                severity=severity,
                recommended_action=recommended_action,
                action_taken=False,
            )
        )

    db.flush()
    return alert


def resolve_alerts_matching(db: Session, dedup_prefix: str) -> None:
    """Auto-resolve active alerts whose dedup_key starts with the given prefix
    (used when a condition that triggered them is no longer present)."""
    alerts = (
        db.query(Alert)
        .filter(Alert.dedup_key.like(f"{dedup_prefix}%"), Alert.status == "ACTIVE")
        .all()
    )
    for alert in alerts:
        alert.status = "RESOLVED"
    db.flush()
