"""Wipes one demo account and everything under it (farms, fields, zones,
rovers, detections, alerts, sensor history — all of it) back to a clean
slate. Talks directly to Postgres, so it works even if the backend API
isn't running — only the `db` container needs to be up.

Safe to re-run any time. seed_demo.py always recreates the account from
scratch afterwards, so clearing never leaves you without a way back to a
working demo.

Usage:
    python scripts/clear_demo_data.py
    python scripts/clear_demo_data.py --email someoneelse@example.com
"""
import argparse
import sys
from pathlib import Path

import psycopg

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.core.config import settings  # noqa: E402

# Deletion order matters — children before the tables they reference.
DELETE_PLAN = [
    ("edge_events", "rover_id", "rover_ids"),
    ("spray_events", "field_id", "field_ids"),
    ("spray_recommendations", "field_id", "field_ids"),
    ("irrigation_events", "field_id", "field_ids"),
    # cnn_detections has no field_id column directly — handled separately below.
    ("camera_observations", "field_id", "field_ids"),
    ("environmental_readings", "field_id", "field_ids"),
    ("weather_observations", "field_id", "field_ids"),
    ("advisories", "field_id", "field_ids"),
    ("alerts", "field_id", "field_ids"),
    ("rover_positions", "rover_id", "rover_ids"),
    ("scan_sessions", "rover_id", "rover_ids"),
    ("rover_field_assignments", "rover_id", "rover_ids"),
    ("rovers", "farmer_id", "farmer_id_list"),
    ("zones", "id", "zone_ids"),
    ("fields", "id", "field_ids"),
    ("farms", "id", "farm_ids"),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--email", default="farmer2@example.com")
    args = parser.parse_args()

    dsn = settings.database_url.replace("postgresql+psycopg://", "postgresql://")
    conn = psycopg.connect(dsn, autocommit=True)
    cur = conn.cursor()

    cur.execute("SELECT id FROM farmers WHERE email = %s", (args.email,))
    row = cur.fetchone()
    if not row:
        print(f"No account found for {args.email} — nothing to clear.")
        return
    farmer_id = row[0]

    cur.execute("SELECT id FROM farms WHERE farmer_id = %s", (farmer_id,))
    farm_ids = [r[0] for r in cur.fetchall()]

    field_ids = []
    if farm_ids:
        cur.execute("SELECT id FROM fields WHERE farm_id = ANY(%s)", (farm_ids,))
        field_ids = [r[0] for r in cur.fetchall()]

    zone_ids = []
    if field_ids:
        cur.execute("SELECT id FROM zones WHERE field_id = ANY(%s)", (field_ids,))
        zone_ids = [r[0] for r in cur.fetchall()]

    cur.execute("SELECT id FROM rovers WHERE farmer_id = %s", (farmer_id,))
    rover_ids = [r[0] for r in cur.fetchall()]

    ids = {
        "farmer_id_list": [farmer_id],
        "farm_ids": farm_ids,
        "field_ids": field_ids,
        "zone_ids": zone_ids,
        "rover_ids": rover_ids,
    }

    if field_ids:
        cur.execute(
            "DELETE FROM cnn_detections WHERE observation_id IN "
            "(SELECT id FROM camera_observations WHERE field_id = ANY(%s))",
            (field_ids,),
        )
        print(f"  cnn_detections: {cur.rowcount} deleted")

    for table, column, id_key in DELETE_PLAN:
        values = ids[id_key]
        if not values:
            print(f"  {table}: 0 deleted")
            continue
        cur.execute(f"DELETE FROM {table} WHERE {column} = ANY(%s)", (values,))
        print(f"  {table}: {cur.rowcount} deleted")

    cur.execute("DELETE FROM farmers WHERE id = %s", (farmer_id,))
    print(f"  farmers: {cur.rowcount} deleted")

    print(f"\nAccount {args.email} fully cleared. Run seed_demo.py to rebuild it.")


if __name__ == "__main__":
    main()
