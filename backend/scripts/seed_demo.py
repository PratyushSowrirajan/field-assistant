"""Builds a complete, ready-to-demo account from scratch: farmer login,
farm, field with a drawn boundary (zones generate automatically), then
walks a simulated rover across it so there's real health/alert/environment
data to show. Run this any time you want a fresh, populated demo state —
pair it with clear_demo_data.py to reset first.

Usage:
    python scripts/seed_demo.py
    python scripts/seed_demo.py --api http://127.0.0.1:8010/api/v1

Requires the backend API to be running (unlike clear_demo_data.py, which
only needs Postgres).
"""
import argparse
import subprocess
import sys
from pathlib import Path

import httpx

DEMO_EMAIL = "farmer2@example.com"
DEMO_PASSWORD = "pass1234"
DEMO_NAME = "Demo Farmer"
FARM_NAME = "Green Valley Farm"
FIELD_NAME = "North Plot"
CROP_TYPE = "Tomato"
GROWTH_STAGE = "Flowering"
ZONE_RESOLUTION_M = 20

BOUNDARY = {
    "type": "Polygon",
    "coordinates": [[
        [80.2000, 13.0000],
        [80.2010, 13.0000],
        [80.2010, 13.0010],
        [80.2000, 13.0010],
        [80.2000, 13.0000],
    ]],
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api", default="http://127.0.0.1:8010/api/v1")
    parser.add_argument("--interval", type=float, default=0.15, help="Rover telemetry step interval (seconds)")
    parser.add_argument("--detection-chance", type=float, default=0.3)
    args = parser.parse_args()

    c = httpx.Client(base_url=args.api, timeout=15)

    print(f"Logging in / registering {DEMO_EMAIL} ...", flush=True)
    login = c.post(
        "/auth/login",
        data={"username": DEMO_EMAIL, "password": DEMO_PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    if login.status_code != 200:
        register = c.post("/auth/register", json={"name": DEMO_NAME, "email": DEMO_EMAIL, "password": DEMO_PASSWORD})
        register.raise_for_status()
        token = register.json()["access_token"]
    else:
        token = login.json()["access_token"]
    c.headers["Authorization"] = f"Bearer {token}"

    farms = c.get("/farms").json()
    farm = next((f for f in farms if f["name"] == FARM_NAME), None)
    if farm is None:
        print(f"Creating farm '{FARM_NAME}' ...", flush=True)
        farm = c.post("/farms", json={"name": FARM_NAME}).json()
    else:
        print(f"Using existing farm '{FARM_NAME}'", flush=True)

    fields = c.get(f"/farms/{farm['id']}/fields").json()
    field = next((f for f in fields if f["name"] == FIELD_NAME), None)
    if field is None:
        print(f"Creating field '{FIELD_NAME}' with boundary ...", flush=True)
        field = c.post(f"/farms/{farm['id']}/fields", json={
            "name": FIELD_NAME,
            "crop_type": CROP_TYPE,
            "growth_stage": GROWTH_STAGE,
            "zone_resolution_m": ZONE_RESOLUTION_M,
            "boundary": BOUNDARY,
        }).json()
    else:
        print(f"Using existing field '{FIELD_NAME}'", flush=True)
        if not field.get("boundary"):
            print("  field has no boundary yet — drawing one ...", flush=True)
            field = c.put(f"/fields/{field['id']}/boundary", json={
                "boundary": BOUNDARY, "zone_resolution_m": ZONE_RESOLUTION_M,
            }).json()
        if field.get("growth_stage") != GROWTH_STAGE or field.get("crop_type") != CROP_TYPE:
            c.patch(f"/fields/{field['id']}", json={"crop_type": CROP_TYPE, "growth_stage": GROWTH_STAGE})

    zones = c.get(f"/fields/{field['id']}/zones").json()
    print(f"Field ready: {field['name']} ({len(zones)} zones, {field.get('area_m2', 0):.0f} m2)", flush=True)

    print("\nSending the rover out to scan the field (this takes a minute)...", flush=True)
    script_path = Path(__file__).parent / "simulate_rover.py"
    subprocess.run([
        sys.executable, str(script_path),
        "--api", args.api,
        "--email", DEMO_EMAIL,
        "--password", DEMO_PASSWORD,
        "--field-name", FIELD_NAME,
        "--interval", str(args.interval),
        "--detection-chance", str(args.detection_chance),
    ], check=True)

    print(f"\nDemo ready. Log in as {DEMO_EMAIL} / {DEMO_PASSWORD}.", flush=True)


if __name__ == "__main__":
    main()
