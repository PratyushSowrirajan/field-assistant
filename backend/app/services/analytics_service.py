import uuid
from datetime import datetime, timedelta, timezone

from geoalchemy2.shape import to_shape
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.environment import EnvironmentalReading
from app.models.field import Field
from app.models.irrigation import IrrigationEvent
from app.models.observation import CameraObservation, CNNDetection
from app.models.spray import SprayEvent
from app.models.zone import Zone
from app.schemas.analytics import (
    DecisionInsightOut,
    FieldHealthOut,
    HotspotOut,
    TimeSeriesPoint,
    TreatmentCoverageOut,
    YieldRiskOut,
)
from app.schemas.zone import ZoneSummary
from app.services.environmental_risk import evaluate_environmental_risk
from app.services.geo import haversine_m
from app.services.irrigation_engine import evaluate_irrigation

RELEVANT_TYPES = ("DISEASE", "PEST")
TREATMENT_MATCH_RADIUS_M = 8.0


def _observation_count(db: Session, field_id: uuid.UUID, zone_id: uuid.UUID | None, since: datetime | None = None) -> int:
    q = db.query(func.count(CameraObservation.id)).filter(CameraObservation.field_id == field_id)
    if zone_id:
        q = q.filter(CameraObservation.zone_id == zone_id)
    if since:
        q = q.filter(CameraObservation.timestamp >= since)
    return q.scalar() or 0


def _detection_count(
    db: Session,
    field_id: uuid.UUID,
    zone_id: uuid.UUID | None,
    detection_type: str | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
) -> int:
    q = (
        db.query(func.count(CNNDetection.id))
        .join(CameraObservation, CNNDetection.observation_id == CameraObservation.id)
        .filter(CameraObservation.field_id == field_id)
    )
    if zone_id:
        q = q.filter(CameraObservation.zone_id == zone_id)
    if detection_type:
        q = q.filter(CNNDetection.detection_type == detection_type)
    if since:
        q = q.filter(CNNDetection.created_at >= since)
    if until:
        q = q.filter(CNNDetection.created_at < until)
    return q.scalar() or 0


def zone_summary(db: Session, zone: Zone) -> ZoneSummary:
    now = datetime.now(timezone.utc)
    obs_count = _observation_count(db, zone.field_id, zone.id)
    disease_count = _detection_count(db, zone.field_id, zone.id, "DISEASE")
    pest_count = _detection_count(db, zone.field_id, zone.id, "PEST")
    nutrient_count = _detection_count(db, zone.field_id, zone.id, "NUTRIENT_DEFICIENCY")

    disease_prevalence = (disease_count / obs_count * 100) if obs_count else 0.0
    pest_prevalence = (pest_count / obs_count * 100) if obs_count else 0.0
    nutrient_risk = "HIGH" if nutrient_count >= 3 else ("MODERATE" if nutrient_count >= 1 else "LOW")

    recent = _detection_count(db, zone.field_id, zone.id, "DISEASE", since=now - timedelta(days=7)) + \
        _detection_count(db, zone.field_id, zone.id, "PEST", since=now - timedelta(days=7))
    prior = _detection_count(
        db, zone.field_id, zone.id, "DISEASE", since=now - timedelta(days=14), until=now - timedelta(days=7)
    ) + _detection_count(
        db, zone.field_id, zone.id, "PEST", since=now - timedelta(days=14), until=now - timedelta(days=7)
    )
    if recent > prior:
        trend = "INCREASING"
    elif recent < prior:
        trend = "DECREASING"
    else:
        trend = "STABLE"

    max_prevalence = max(disease_prevalence, pest_prevalence)
    if max_prevalence >= 30 or trend == "INCREASING" and max_prevalence >= 15:
        risk_level = "CRITICAL" if max_prevalence >= 50 else "HIGH"
    elif max_prevalence >= 10:
        risk_level = "MODERATE"
    else:
        risk_level = "LOW"

    sprays = db.query(func.count(SprayEvent.id)).filter(
        SprayEvent.zone_id == zone.id, SprayEvent.status == "SPRAY_COMPLETED"
    ).scalar() or 0
    treatment_status = "TREATED" if sprays > 0 else "UNTREATED"

    last_scan = (
        db.query(func.max(CameraObservation.timestamp)).filter(CameraObservation.zone_id == zone.id).scalar()
    )

    return ZoneSummary(
        id=zone.id,
        code=zone.code,
        area_m2=zone.area_m2,
        disease_prevalence_pct=round(disease_prevalence, 1),
        pest_prevalence_pct=round(pest_prevalence, 1),
        nutrient_risk=nutrient_risk,
        risk_level=risk_level,
        trend=trend,
        observation_count=obs_count,
        detection_count=disease_count + pest_count + nutrient_count,
        treatment_status=treatment_status,
        last_scan_at=last_scan,
    )


def field_health(db: Session, field: Field) -> FieldHealthOut:
    zones = db.query(Zone).filter(Zone.field_id == field.id).all()
    summaries = [zone_summary(db, z) for z in zones]

    obs_total = sum(s.observation_count for s in summaries) or 1
    disease_total = sum(round(s.disease_prevalence_pct / 100 * s.observation_count) for s in summaries)
    pest_total = sum(round(s.pest_prevalence_pct / 100 * s.observation_count) for s in summaries)
    disease_prevalence = disease_total / obs_total * 100
    pest_prevalence = pest_total / obs_total * 100

    irrigation = evaluate_irrigation(db, field.id)
    env_risk = evaluate_environmental_risk(db, field.id)

    risk_weight = {"LOW": 0, "MODERATE": 1, "HIGH": 2, "CRITICAL": 3}
    zone_risk_avg = (
        sum(risk_weight.get(s.risk_level, 0) for s in summaries) / len(summaries) if summaries else 0
    )
    water_weight = {"NONE": 0, "LOW": 0.5, "MODERATE": 1.5, "HIGH": 3}.get(irrigation.water_stress_status, 0)
    env_weight = max(
        risk_weight.get(env_risk.heat_risk, 0),
        risk_weight.get(env_risk.flood_risk, 0),
        risk_weight.get(env_risk.drought_risk, 0),
    )

    composite = zone_risk_avg + water_weight * 0.6 + env_weight * 0.6
    score = max(0.0, 100 - composite * 12)

    if composite >= 6 or score < 35:
        status = "CRITICAL"
    elif composite >= 4 or score < 55:
        status = "HIGH_RISK"
    elif composite >= 2 or score < 75:
        status = "ATTENTION"
    elif composite >= 0.5 or score < 90:
        status = "MONITOR"
    else:
        status = "HEALTHY"

    yr = yield_risk(db, field)

    return FieldHealthOut(
        field_id=field.id,
        status=status,
        score=round(score, 1),
        disease_prevalence_pct=round(disease_prevalence, 1),
        pest_prevalence_pct=round(pest_prevalence, 1),
        water_stress_status=irrigation.water_stress_status,
        environmental_risk=max(
            [env_risk.heat_risk, env_risk.flood_risk, env_risk.drought_risk],
            key=lambda v: risk_weight.get(v, 0),
        ),
        yield_risk=yr.yield_risk,
    )


def hotspots(db: Session, field: Field, detection_type: str | None = None) -> list[HotspotOut]:
    zones = db.query(Zone).filter(Zone.field_id == field.id).all()
    results: list[HotspotOut] = []
    for zone in zones:
        q = (
            db.query(CNNDetection.detection_type, CNNDetection.class_name, func.count(CNNDetection.id))
            .join(CameraObservation, CNNDetection.observation_id == CameraObservation.id)
            .filter(CameraObservation.zone_id == zone.id, CNNDetection.detection_type.in_(RELEVANT_TYPES))
        )
        if detection_type:
            q = q.filter(CNNDetection.detection_type == detection_type)
        q = q.group_by(CNNDetection.detection_type, CNNDetection.class_name)

        for d_type, class_name, count in q.all():
            if count < 2:
                continue  # a single detection is a marker, not a hotspot (UI rule #15)
            centroid = to_shape(zone.polygon).centroid
            area_ha = max(zone.area_m2 / 10000, 0.0001)
            density = count / area_ha
            severity = "CRITICAL" if density > 40 else "HIGH" if density > 20 else "MODERATE" if density > 8 else "LOW"
            results.append(
                HotspotOut(
                    id=f"{zone.id}:{d_type}:{class_name}",
                    field_id=field.id,
                    zone_id=zone.id,
                    detection_type=d_type,
                    class_name=class_name,
                    center_lat=centroid.y,
                    center_lon=centroid.x,
                    detection_count=count,
                    density_per_ha=round(density, 1),
                    severity=severity,
                )
            )
    return results


def treatment_coverage(db: Session, field: Field, window_days: int = 30) -> TreatmentCoverageOut:
    since = datetime.now(timezone.utc) - timedelta(days=window_days)
    detections = (
        db.query(CameraObservation.latitude, CameraObservation.longitude, CNNDetection.created_at)
        .join(CameraObservation, CNNDetection.observation_id == CameraObservation.id)
        .filter(
            CameraObservation.field_id == field.id,
            CNNDetection.detection_type.in_(RELEVANT_TYPES),
            CNNDetection.created_at >= since,
        )
        .all()
    )
    sprays = (
        db.query(SprayEvent.latitude, SprayEvent.longitude, SprayEvent.completed_at)
        .filter(
            SprayEvent.field_id == field.id,
            SprayEvent.status == "SPRAY_COMPLETED",
            SprayEvent.completed_at >= since,
        )
        .all()
    )

    treated = 0
    for lat, lon, ts in detections:
        for s_lat, s_lon, s_ts in sprays:
            if s_ts >= ts and haversine_m(lat, lon, s_lat, s_lon) <= TREATMENT_MATCH_RADIUS_M:
                treated += 1
                break

    total = len(detections)
    coverage = (treated / total * 100) if total else 0.0

    return TreatmentCoverageOut(
        field_id=field.id,
        qualifying_detections=total,
        treated_detections=treated,
        treatment_coverage_pct=round(coverage, 1),
        untreated_problem_count=total - treated,
    )


def yield_risk(db: Session, field: Field) -> YieldRiskOut:
    zones = db.query(Zone).filter(Zone.field_id == field.id).all()
    summaries = [zone_summary(db, z) for z in zones]

    irrigation = evaluate_irrigation(db, field.id)
    env_risk = evaluate_environmental_risk(db, field.id)

    factors: list[str] = []
    max_disease = max((s.disease_prevalence_pct for s in summaries), default=0)
    max_pest = max((s.pest_prevalence_pct for s in summaries), default=0)

    if max_disease >= 15:
        factors.append("Elevated disease prevalence")
    if max_pest >= 15:
        factors.append("Elevated pest pressure")
    if irrigation.water_stress_status in ("MODERATE", "HIGH"):
        factors.append("Water stress")
    if env_risk.heat_risk in ("HIGH", "CRITICAL"):
        factors.append("Heat stress")
    if env_risk.drought_risk in ("MODERATE", "HIGH"):
        factors.append("Drought risk")
    if env_risk.flood_risk in ("MODERATE", "HIGH"):
        factors.append("Flood risk")
    if any(s.trend == "INCREASING" for s in summaries):
        factors.append("Increasing detection trend")

    n = len(factors)
    level = "CRITICAL" if n >= 4 else "HIGH" if n == 3 else "MODERATE" if n >= 1 else "LOW"

    return YieldRiskOut(field_id=field.id, yield_risk=level, contributing_factors=factors)


def decision_insights(db: Session, field: Field) -> list[DecisionInsightOut]:
    alerts = (
        db.query(Alert)
        .filter(Alert.field_id == field.id, Alert.status == "ACTIVE")
        .order_by(Alert.severity.desc())
        .limit(10)
        .all()
    )
    insights: list[DecisionInsightOut] = []
    for alert in alerts:
        zone_code = None
        if alert.zone_id:
            zone = db.get(Zone, alert.zone_id)
            zone_code = zone.code if zone else None
        insights.append(
            DecisionInsightOut(
                type=alert.type,
                severity=alert.severity,
                field_id=field.id,
                zone_id=alert.zone_id,
                message=alert.message,
                evidence=f"Active since {alert.created_at.isoformat()}, last seen {alert.last_seen_at.isoformat()}",
                recommended_action=alert.message,
            )
        )
    return insights


def treatment_response(db: Session, zone: Zone) -> str:
    last_spray = (
        db.query(func.max(SprayEvent.completed_at))
        .filter(SprayEvent.zone_id == zone.id, SprayEvent.status == "SPRAY_COMPLETED")
        .scalar()
    )
    if not last_spray:
        return "INSUFFICIENT_DATA"

    window = timedelta(days=7)
    before = _detection_count(db, zone.field_id, zone.id, since=last_spray - window, until=last_spray)
    after = _detection_count(db, zone.field_id, zone.id, since=last_spray, until=last_spray + window)

    if before == 0:
        return "INSUFFICIENT_DATA"
    if after < before * 0.7:
        return "IMPROVING"
    if after > before * 1.3:
        return "WORSENING"
    return "UNCHANGED"


def time_series_daily(
    db: Session, field_id: uuid.UUID, metric: str, days: int = 30
) -> list[TimeSeriesPoint]:
    since = datetime.now(timezone.utc) - timedelta(days=days)

    if metric in ("disease", "pest", "nutrient"):
        type_map = {"disease": "DISEASE", "pest": "PEST", "nutrient": "NUTRIENT_DEFICIENCY"}
        rows = (
            db.query(func.date_trunc("day", CNNDetection.created_at).label("d"), func.count(CNNDetection.id))
            .join(CameraObservation, CNNDetection.observation_id == CameraObservation.id)
            .filter(
                CameraObservation.field_id == field_id,
                CNNDetection.detection_type == type_map[metric],
                CNNDetection.created_at >= since,
            )
            .group_by("d")
            .order_by("d")
            .all()
        )
    elif metric in ("soil_moisture", "temperature", "humidity"):
        type_map = {
            "soil_moisture": "SOIL_MOISTURE",
            "temperature": "AIR_TEMPERATURE",
            "humidity": "RELATIVE_HUMIDITY",
        }
        rows = (
            db.query(
                func.date_trunc("day", EnvironmentalReading.timestamp).label("d"),
                func.avg(EnvironmentalReading.value),
            )
            .filter(
                EnvironmentalReading.field_id == field_id,
                EnvironmentalReading.reading_type == type_map[metric],
                EnvironmentalReading.timestamp >= since,
            )
            .group_by("d")
            .order_by("d")
            .all()
        )
    elif metric == "irrigation":
        rows = (
            db.query(func.date_trunc("day", IrrigationEvent.started_at).label("d"), func.count(IrrigationEvent.id))
            .filter(IrrigationEvent.field_id == field_id, IrrigationEvent.started_at >= since)
            .group_by("d")
            .order_by("d")
            .all()
        )
    elif metric == "treatment":
        rows = (
            db.query(func.date_trunc("day", SprayEvent.completed_at).label("d"), func.count(SprayEvent.id))
            .filter(SprayEvent.field_id == field_id, SprayEvent.completed_at >= since)
            .group_by("d")
            .order_by("d")
            .all()
        )
    else:
        rows = []

    return [TimeSeriesPoint(timestamp=r[0], value=float(r[1] or 0)) for r in rows]
