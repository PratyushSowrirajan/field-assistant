# Smart Farming Assistant

An edge-AI-powered smart farming platform: a FastAPI + PostGIS backend that turns
rover/edge observations into geospatial farm intelligence, and a React + Mapbox
frontend farmers use to see field health, alerts, and recommendations.

Built from `docs/Smart_Farming_Assistant_Software_PRD_v2.md` (functional source of
truth) and `docs/Smart_Farming_Assistant_UI_Design_Rules.md` (design source of truth),
for problem statement 26180 (`docs/sih2026-sih26180.txt`).

## Architecture

```
React (Vite + Mapbox GL) → FastAPI → PostgreSQL/PostGIS
                                ↑
                    Raspberry Pi / rover (REST + WebSocket)
```

- **Backend** — `backend/`: FastAPI, SQLAlchemy + GeoAlchemy2, Alembic migrations,
  JWT auth (farmer accounts + separate device tokens for rovers), WebSocket live
  rover feed, rule-based irrigation/environmental-risk/alerting engines,
  OpenWeatherMap integration.
- **Frontend** — `frontend/`: React + TypeScript + Vite, Tailwind CSS, Mapbox GL JS,
  React Query, Recharts.
- **Database** — PostgreSQL 16 with PostGIS (via Docker Compose), storing raw
  edge observations separately from derived analytics (PRD section 53).

## Prerequisites

- Python 3.11+ (developed against 3.13)
- Node.js 18+
- Docker Desktop (for Postgres/PostGIS)

## 1. Database

```bash
docker compose up -d
```

Starts Postgres+PostGIS on `localhost:5434` (mapped off the default 5432 to avoid
clashing with any other local Postgres install). Credentials are in
`backend/.env` (dev-only, not for production).

## 2. Backend

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash; use .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 127.0.0.1 --port 8010
```

Copy `backend/.env.example` to `backend/.env` and fill in your own values if you
don't already have one — a real `.env` with working dev credentials was created for
this build and is intentionally **not committed** (see `.gitignore`). Required vars:

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Postgres connection string |
| `JWT_SECRET` | Signs farmer + device auth tokens |
| `OPENWEATHER_API_KEY` | Weather integration (irrigation/environmental risk) |
| `CORS_ORIGINS` | Comma-separated list of allowed frontend origins |

API docs: `http://127.0.0.1:8010/docs`

> **Port note:** this machine already had other local projects bound to the usual
> `5432`/`8000` ports, so this project deliberately uses `5434` (Postgres) and
> `8010` (API) instead. Adjust freely if your environment is clean.

## 3. Frontend

```bash
cd frontend
npm install
npm run dev -- --port 5175
```

Copy `frontend/.env.example` to `frontend/.env` and set:

| Variable | Purpose |
|---|---|
| `VITE_API_BASE_URL` | Backend base URL, e.g. `http://127.0.0.1:8010` |
| `VITE_WS_BASE_URL` | Backend WebSocket base URL, e.g. `ws://127.0.0.1:8010` |
| `VITE_MAPBOX_TOKEN` | Your Mapbox access token (`pk....`) |

App: `http://localhost:5175`

## Rover / edge integration

Rovers authenticate separately from farmers:

1. Farmer registers a rover in the app (Live Rover → Add rover), which returns a
   one-time `device_secret`.
2. The Raspberry Pi calls `POST /api/v1/rovers/device/login` with `device_id` +
   `device_secret` to get a short-lived device JWT.
3. That token authenticates all edge ingestion calls:
   - `POST /api/v1/edge/telemetry` — GPS + optional camera/CNN result + rover status
     (matches the PRD's combined rover event contract).
   - `POST /api/v1/edge/sensors`, `/edge/spray`, `/edge/irrigation`, `/edge/scan-session`
   - `POST /api/v1/edge/events` — batched/offline-queued events with `event_id`
     dedup, for syncing after a connectivity gap.

Full request/response shapes are in `backend/app/schemas/edge.py` and the live
OpenAPI docs.

## What's implemented

Covers the MVP scope in PRD section 56: auth, farms/fields, interactive
boundary drawing, automatic PostGIS-based zoning, rover pairing + live
GPS/zone tracking, CNN detection ingestion with field/zone point-in-polygon
mapping, zone-level prevalence + hotspot analytics, spray recommendation +
treatment coverage tracking, soil/environmental sensor ingestion, an
irrigation recommendation engine, environmental risk alerts (drought/flood/
heat), a dedup'd alert + advisory system, historical analytics/charts, and an
offline-sync endpoint with event dedup.

Not yet built (flagged as Phase 2 in the PRD): plant-level infestation
counting, DBSCAN-grade spatial clustering (hotspots currently aggregate at
zone granularity), a trained yield-prediction model (yield risk is a
rules-based indicator, not a numeric forecast), and SMS notifications.
