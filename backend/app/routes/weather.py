import logging

from fastapi import APIRouter, HTTPException, Query

from app.schemas import WeatherOut
from app.services.weather_service import get_weather

log = logging.getLogger("travelmate.weather")
router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("/forecast", response_model=WeatherOut)
def forecast(city: str = Query(..., min_length=2)):
    try:
        return get_weather(city)
    except LookupError as e:
        raise HTTPException(404, str(e))
    except Exception:  # noqa: BLE001
        log.exception("weather failed for %s", city)
        raise HTTPException(503, "Weather is unavailable right now.")
