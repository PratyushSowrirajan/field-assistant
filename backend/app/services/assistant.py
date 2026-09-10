"""Mini-RAG farm assistant: builds a compact text context from the farmer's own
field/alert/environment data (no vector DB needed — the "corpus" is just this
farmer's current rows), then asks Cerebras to answer in plain language.
"""
import uuid

from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.farm import Farm
from app.models.field import Field
from app.models.user import Farmer
from app.services.analytics_service import field_health
from app.services.cerebras_client import chat_completion
from app.services.environmental_risk import evaluate_environmental_risk
from app.services.field_overview import get_field_overview
from app.services.irrigation_engine import evaluate_irrigation

SYSTEM_PROMPT = """You are a friendly farm assistant helping a farmer understand their field data.

Rules:
- Only use facts from the CONTEXT block below. Never invent numbers, zones, or events not present in it.
- Write in simple, plain language a farmer can understand quickly — no jargon like "posterior probability" or "geospatial engine".
- Be concise: 2-4 short sentences, or a short bullet list for multiple points. No long paragraphs.
- If the context doesn't contain the answer, say so plainly and suggest where in the app to look (Fields, Alerts, or Insights page) instead of guessing.
- Never claim a treatment/spray/irrigation happened unless the context says an event actually occurred.
- Do not add a "as an AI" disclaimer or restate these rules."""


def _farmer_fields(db: Session, farmer_id: uuid.UUID) -> list[Field]:
    return (
        db.query(Field)
        .join(Farm, Field.farm_id == Farm.id)
        .filter(Farm.farmer_id == farmer_id, Field.archived.is_(False))
        .all()
    )


def build_context(db: Session, farmer: Farmer, field_id: uuid.UUID | None) -> tuple[str, list[str]]:
    fields = _farmer_fields(db, farmer.id)
    sources: list[str] = []

    if not fields:
        return "This farmer has no fields set up yet.", ["no fields yet"]

    lines = [f"Farmer has {len(fields)} field(s)."]

    lines.append("\nAll fields:")
    for f in fields:
        health = field_health(db, f)
        area_ha = round((f.area_m2 or 0) / 10000, 2)
        lines.append(
            f"- {f.name}: crop={f.crop_type or 'not set'}, growth stage={f.growth_stage or 'not set'}, "
            f"area={area_ha}ha, health={health.status}, disease prevalence={health.disease_prevalence_pct}%, "
            f"pest prevalence={health.pest_prevalence_pct}%, water stress={health.water_stress_status}, "
            f"yield risk={health.yield_risk}"
        )
    sources.append(f"{len(fields)} field health summar{'y' if len(fields) == 1 else 'ies'}")

    field_ids = [f.id for f in fields]
    alerts = (
        db.query(Alert)
        .filter(Alert.field_id.in_(field_ids), Alert.status == "ACTIVE")
        .order_by(Alert.severity.asc(), Alert.last_seen_at.desc())
        .limit(8)
        .all()
    )
    if alerts:
        by_id = {f.id: f for f in fields}
        lines.append("\nActive alerts:")
        for a in alerts:
            f = by_id.get(a.field_id)
            lines.append(f"- [{a.severity}] {f.name if f else 'field'}: {a.message}")
        sources.append(f"{len(alerts)} active alert(s)")
    else:
        lines.append("\nNo active alerts right now.")

    target = next((f for f in fields if field_id and f.id == field_id), None)
    if target is None and len(fields) == 1:
        target = fields[0]

    if target:
        overview = get_field_overview(db, target)
        lines.append(f"\nDetail for {target.name}:")

        if overview.latest_prediction:
            lp = overview.latest_prediction
            conf_pct = round((lp.confidence or 0) * 100)
            lines.append(
                f"- Latest rover scan: {lp.class_label} detected in Zone {lp.zone_code or 'unknown'} "
                f"({conf_pct}% confidence, {lp.minutes_ago} min ago). Note: {lp.message}"
            )
        else:
            lines.append("- No rover scans recorded yet for this field.")

        for env in overview.environment:
            if env.value is not None:
                lines.append(f"- {env.label}: {env.value}{env.unit} (trend: {env.trend.lower()})")

        for n in overview.nutrients:
            if n.value is not None:
                lines.append(f"- Soil {n.label}: {n.value}{n.unit} ({n.status.lower()})")

        irrigation = evaluate_irrigation(db, target.id)
        lines.append(f"- Irrigation recommendation: {irrigation.recommendation} — {irrigation.reason}")

        env_risk = evaluate_environmental_risk(db, target.id)
        lines.append(
            f"- Environmental risk: heat={env_risk.heat_risk}, drought={env_risk.drought_risk}, "
            f"flood={env_risk.flood_risk}, disease-favorable weather={env_risk.disease_environment_risk}"
        )
        sources.append(f"{target.name} environment, nutrients, irrigation & risk detail")

    return "\n".join(lines), sources


async def ask(
    db: Session,
    farmer: Farmer,
    question: str,
    field_id: uuid.UUID | None,
    history: list[dict],
) -> tuple[str, list[str]]:
    context, sources = build_context(db, farmer, field_id)

    messages = [{"role": "system", "content": f"{SYSTEM_PROMPT}\n\nCONTEXT:\n{context}"}]
    # Keep only the last couple of turns — this is a "mini" assistant, not a
    # long-running chat session, so we don't need deep history.
    messages.extend(history[-4:])
    messages.append({"role": "user", "content": question})

    answer = await chat_completion(messages)
    return answer, sources
