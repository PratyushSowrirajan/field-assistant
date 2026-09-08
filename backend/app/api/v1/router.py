from fastapi import APIRouter

from app.api.v1 import (
    alerts,
    analytics,
    auth,
    dashboard,
    detections,
    edge,
    environment,
    farms,
    fields,
    intervention,
    live,
    rovers,
    zones,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(farms.router)
api_router.include_router(fields.router)
api_router.include_router(zones.router)
api_router.include_router(rovers.router)
api_router.include_router(edge.router)
api_router.include_router(detections.router)
api_router.include_router(alerts.router)
api_router.include_router(dashboard.router)
api_router.include_router(analytics.router)
api_router.include_router(environment.router)
api_router.include_router(intervention.router)

# WebSocket route is mounted at the app root (not under /api/v1) so it stays a short, stable URL.
ws_router = APIRouter()
ws_router.include_router(live.router)
