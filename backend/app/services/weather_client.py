from datetime import datetime, timezone

import httpx

from app.core.config import settings


class WeatherFetchError(Exception):
    pass


async def fetch_current_and_forecast(lat: float, lon: float) -> dict:
    """Fetch current conditions + next-24h forecast rainfall from OpenWeatherMap.
    Uses the free /weather and /forecast (3-hour step) endpoints.
    """
    if not settings.openweather_api_key:
        raise WeatherFetchError("OPENWEATHER_API_KEY is not configured")

    params_common = {"lat": lat, "lon": lon, "appid": settings.openweather_api_key, "units": "metric"}

    async with httpx.AsyncClient(timeout=10.0) as client:
        current_resp = await client.get(f"{settings.openweather_base_url}/weather", params=params_common)
        current_resp.raise_for_status()
        current = current_resp.json()

        forecast_resp = await client.get(f"{settings.openweather_base_url}/forecast", params=params_common)
        forecast_resp.raise_for_status()
        forecast = forecast_resp.json()

    forecast_rainfall_mm = 0.0
    for entry in forecast.get("list", [])[:8]:  # next 8 x 3h steps = 24h
        rain = entry.get("rain", {})
        forecast_rainfall_mm += rain.get("3h", 0.0)

    current_rain = current.get("rain", {})
    rainfall_mm = current_rain.get("1h", current_rain.get("3h", 0.0))

    return {
        "temperature_c": current.get("main", {}).get("temp"),
        "humidity_pct": current.get("main", {}).get("humidity"),
        "rainfall_mm": rainfall_mm,
        "forecast_rainfall_mm": round(forecast_rainfall_mm, 2),
        "wind_speed_mps": current.get("wind", {}).get("speed"),
        "condition": (current.get("weather") or [{}])[0].get("main"),
        "fetched_at": datetime.now(timezone.utc),
    }
