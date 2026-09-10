"""Simulates a rover walking a field, for demos without physical hardware.

Logs in as an existing farmer, registers a fresh demo rover against one of
their fields, then streams telemetry (position + occasional CNN detections +
occasional spray events) through the same /api/v1/edge/* endpoints a real
Raspberry Pi would use. Watch it live on the app's Live Rover page while this
runs — updates arrive over the same WebSocket a real rover would trigger.

Usage:
    python scripts/simulate_rover.py --email farmer2@example.com --password pass1234

Run from backend/ with the project venv active (uses httpx + shapely, both
already backend dependencies).
"""
import argparse
import random
import time
from datetime import datetime, timezone

import httpx
from shapely.geometry import shape

DISEASE_CLASSES = ["early_blight", "late_blight", "leaf_spot"]
PEST_CLASSES = ["aphid", "whitefly", "fruit_borer"]
NUTRIENT_CLASSES = ["nitrogen_deficiency", "potassium_deficiency"]


def zone_sort_key(zone: dict) -> int:
    digits = "".join(c for c in zone["code"] if c.isdigit())
    return int(digits) if digits else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api", default="http://127.0.0.1:8010/api/v1")
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--field-name", default=None, help="Defaults to the first field with a boundary")
    parser.add_argument("--interval", type=float, default=2.0, help="Seconds between telemetry updates")
    parser.add_argument("--detection-chance", type=float, default=0.3)
    parser.add_argument("--laps", type=int, default=1, help="How many times to sweep the zone grid")
    args = parser.parse_args()

    client = httpx.Client(base_url=args.api, timeout=10)

    print(f"Logging in as {args.email}...")
    login = client.post(
        "/auth/login",
        data={"username": args.email, "password": args.password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    login.raise_for_status()
    client.headers["Authorization"] = f"Bearer {login.json()['access_token']}"

    farms = client.get("/farms").json()
    if not farms:
        raise SystemExit("This account has no farms yet — create one in the app first.")

    field = None
    for farm in farms:
        fields = client.get(f"/farms/{farm['id']}/fields").json()
        for f in fields:
            if f.get("boundary") and (args.field_name is None or f["name"] == args.field_name):
                field = f
                break
        if field:
            break

    if field is None:
        raise SystemExit("No field with a drawn boundary found. Draw a field boundary in the app first.")

    print(f"Using field '{field['name']}' ({field['id']})")

    zones = client.get(f"/fields/{field['id']}/zones").json()
    zones.sort(key=zone_sort_key)
    if not zones:
        raise SystemExit("This field has no zones yet.")

    waypoints = []
    for zone in zones:
        centroid = shape(zone["polygon"]).centroid
        waypoints.append((centroid.y, centroid.x))  # (lat, lon)

    device_id = f"demo-rover-{int(time.time())}"
    print(f"Registering demo rover '{device_id}'...")
    reg = client.post("/rovers", json={"name": "Demo Rover", "device_id": device_id, "field_ids": [field["id"]]})
    reg.raise_for_status()
    rover = reg.json()

    device = httpx.Client(base_url=args.api, timeout=10)
    login2 = device.post("/rovers/device/login", json={"device_id": device_id, "device_secret": rover["device_secret"]})
    login2.raise_for_status()
    device.headers["Authorization"] = f"Bearer {login2.json()['access_token']}"

    def now_iso():
        return datetime.now(timezone.utc).isoformat()

    print("Starting scan session...")
    device.post("/edge/scan-session", json={
        "device_id": device_id, "field_id": field["id"], "event": "SCAN_START", "timestamp": now_iso(),
    })

    battery = 95.0
    try:
        for lap in range(args.laps):
            for i, (lat, lon) in enumerate(waypoints):
                jitter = lambda: random.uniform(-0.00002, 0.00002)
                lat_j, lon_j = lat + jitter(), lon + jitter()
                battery = max(20.0, battery - 0.15)

                payload = {
                    "device_id": device_id,
                    "timestamp": now_iso(),
                    "gps": {
                        "latitude": lat_j, "longitude": lon_j,
                        "accuracy_m": round(random.uniform(1.5, 3.5), 1),
                        "speed_mps": round(random.uniform(0.2, 0.6), 2),
                        "heading_deg": round(random.uniform(0, 359), 1),
                    },
                    "rover": {"status": "SCANNING", "sprayer_status": "OFF", "battery_level": round(battery, 1)},
                }

                detected = None
                if random.random() < args.detection_chance:
                    detection_type, classes = random.choice([
                        ("DISEASE", DISEASE_CLASSES), ("PEST", PEST_CLASSES), ("NUTRIENT_DEFICIENCY", NUTRIENT_CLASSES),
                    ])
                    detected = random.choice(classes)
                    payload["camera"] = {"camera_id": "amb82-001", "frame_id": f"frame-{lap}-{i}"}
                    payload["cnn"] = {
                        "detection_type": detection_type,
                        "class": detected,
                        "confidence": round(random.uniform(0.6, 0.97), 2),
                        "model_name": "demo-sim",
                        "model_version": "1.0",
                    }

                zone_code = zones[i]["code"]
                r = device.post("/edge/telemetry", json=payload)
                r.raise_for_status()
                state = r.json()

                msg = f"[{lap + 1}/{args.laps}] Zone {zone_code} - battery {battery:.0f}%"
                if detected:
                    msg += f" - DETECTED {detected} ({payload['cnn']['confidence']:.0%})"
                print(msg)

                # Occasionally follow a disease/pest detection with a spray event, to
                # demonstrate the detected -> treated flow on the map/treatment tab.
                if detected and payload["cnn"]["detection_type"] in ("DISEASE", "PEST") and random.random() < 0.5:
                    time.sleep(min(args.interval, 1.0))
                    device.post("/edge/spray", json={
                        "device_id": device_id,
                        "event": "SPRAY_COMPLETED",
                        "timestamp": now_iso(),
                        "location": {"latitude": lat_j, "longitude": lon_j},
                        "duration_seconds": round(random.uniform(1.5, 4.0), 1),
                        "quantity_ml": round(random.uniform(20, 50), 1),
                    })
                    print(f"           sprayed Zone {zone_code}")

                time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nStopping early...")
    finally:
        device.post("/edge/scan-session", json={
            "device_id": device_id, "field_id": field["id"], "event": "SCAN_END", "timestamp": now_iso(),
        })
        print("Scan session ended. Rover will show OFFLINE after ~2 minutes of no updates.")


if __name__ == "__main__":
    main()
