"""Open-Meteo - real weather, free, no key."""
import time

import httpx

from app.services.place_service import geocode

_CACHE: dict[str, tuple[dict, float]] = {}
_TTL = 10 * 60


def get_weather(city: str):
    key = (city or "").strip().lower()
    hit = _CACHE.get(key)
    if hit and time.time() - hit[1] < _TTL:
        return hit[0]

    geo = geocode(city)
    if not geo:
        raise LookupError(f"Could not find city: {city}")

    with httpx.Client(timeout=15) as c:
        r = c.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": geo["lat"], "longitude": geo["lon"],
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
                "timezone": "auto",
            },
        )
        r.raise_for_status()
        w = r.json()

    cur = w.get("current") or {}
    if not cur:
        raise RuntimeError("Weather data unavailable")

    condition, icon = describe(cur.get("weather_code", 0))
    result = {
        "city": city.strip(),
        "temp": round(cur.get("temperature_2m", 0), 1),
        "condition": condition,
        "icon": icon,
        "humidity": int(cur.get("relative_humidity_2m", 0)),
        "wind": round(cur.get("wind_speed_10m", 0), 1),
        "source": "open-meteo",
    }
    _CACHE[key] = (result, time.time())
    return result


def describe(code: int) -> tuple[str, str]:
    """WMO weather code -> (label, icon key used by the frontend)."""
    if code == 0:
        return "Clear sky", "sun"
    if code in (1, 2):
        return "Partly cloudy", "cloud-sun"
    if code == 3:
        return "Overcast", "cloud"
    if code in (45, 48):
        return "Foggy", "fog"
    if 51 <= code <= 57:
        return "Drizzle", "rain"
    if 61 <= code <= 67:
        return "Rain", "rain"
    if 71 <= code <= 77 or code in (85, 86):
        return "Snow", "snow"
    if 80 <= code <= 82:
        return "Rain showers", "rain"
    if 95 <= code <= 99:
        return "Thunderstorm", "storm"
    return "Mild", "cloud"
