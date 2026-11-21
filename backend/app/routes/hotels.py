import logging

from fastapi import APIRouter, HTTPException, Query

from app.services.hotel_service import search_hotels

log = logging.getLogger("travelmate.hotels")
router = APIRouter(prefix="/hotels", tags=["hotels"])


@router.get("/search")
def search(
    city: str = Query(..., min_length=2, description="City name"),
    check_in: str = Query("", description="YYYY-MM-DD (defaults to a week from today)"),
    check_out: str = Query("", description="YYYY-MM-DD (defaults to check-in + 2 nights)"),
    adults: int = Query(2, ge=1, le=20),
    rooms: int = Query(1, ge=1, le=10),
):
    try:
        return search_hotels(city.strip(), check_in, check_out, adults, rooms)
    except Exception:  # noqa: BLE001
        log.exception("hotel search failed for %s", city)
        raise HTTPException(500, "Hotel search failed. Please try again.")
