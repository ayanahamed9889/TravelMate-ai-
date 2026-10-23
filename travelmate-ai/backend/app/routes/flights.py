import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.services.flight_service import search_flights

log = logging.getLogger("travelmate.flights")
router = APIRouter(prefix="/flights", tags=["flights"])


@router.get("/search")
def search(
    origin: str = Query(..., min_length=3, max_length=3, description="IATA code: DEL, BOM, BLR"),
    destination: str = Query(..., min_length=3, max_length=3, description="IATA code: JAI, GOI, DXB"),
    depart_date: str = Query(..., description="YYYY-MM-DD"),
    return_date: Optional[str] = None,
    adults: int = Query(1, ge=1, le=9),
):
    try:
        return search_flights(origin, destination, depart_date, return_date, adults)
    except ValueError as e:                    # bad input -> 400 with a readable message
        raise HTTPException(400, str(e))
    except Exception:  # noqa: BLE001
        log.exception("flight search failed")
        raise HTTPException(503, "Flight search failed. Please try again.")
