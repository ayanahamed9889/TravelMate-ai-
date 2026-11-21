import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import SavedPlace, User
from app.schemas import DestinationOut, SavedPlaceIn, SavedPlaceOut
from app.services.place_service import geocode, search_attractions, search_restaurants
from app.utils.destinations import REGIONS, recommended, search_destinations

log = logging.getLogger("travelmate.places")
router = APIRouter(prefix="/places", tags=["places"])


# ---------- curated Indian destinations (Explore + Dashboard) ----------
@router.get("", response_model=list[DestinationOut])
def list_destinations(q: str = "", region: str = "", limit: int = Query(60, ge=1, le=100)):
    if region and region not in REGIONS:
        raise HTTPException(400, f"Unknown region. Use one of: {', '.join(REGIONS)}")
    return search_destinations(q, region, limit)


@router.get("/recommended", response_model=list[DestinationOut])
def recommended_destinations(limit: int = Query(6, ge=1, le=12)):
    return recommended(limit)


# ---------- saved places (per user) ----------
def _saved_out(row: SavedPlace) -> dict:
    data = row.data or {}
    return {
        "id": row.id,
        "place_id": row.place_id,
        "name": data.get("name", row.place_id),
        "state": data.get("state", ""),
        "category": data.get("category", ""),
        "description": data.get("description", ""),
        "image": data.get("image"),
        "avg_daily": data.get("avg_daily"),
        "lat": data.get("lat"),
        "lon": data.get("lon"),
    }


@router.get("/saved", response_model=list[SavedPlaceOut])
def list_saved(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(SavedPlace).filter(SavedPlace.user_id == user.id).order_by(SavedPlace.id.desc()).all()
    return [_saved_out(r) for r in rows]


@router.post("/saved", response_model=SavedPlaceOut, status_code=201)
def save_place(payload: SavedPlaceIn, db: Session = Depends(get_db),
               user: User = Depends(get_current_user)):
    existing = (db.query(SavedPlace)
                .filter(SavedPlace.user_id == user.id, SavedPlace.place_id == payload.place_id).first())
    if existing:                                   # saving twice is harmless
        return _saved_out(existing)
    row = SavedPlace(user_id=user.id, place_id=payload.place_id,
                     data=payload.model_dump(exclude={"place_id"}))
    db.add(row)
    db.commit()
    db.refresh(row)
    return _saved_out(row)


@router.delete("/saved/{saved_id}")
def delete_saved(saved_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = db.query(SavedPlace).filter(SavedPlace.id == saved_id, SavedPlace.user_id == user.id).first()
    if not row:
        raise HTTPException(404, "Saved place not found")
    db.delete(row)
    db.commit()
    return {"ok": True}


# ---------- live data around a city (OpenStreetMap / Foursquare) ----------
@router.get("/attractions")
def attractions(city: str = Query(..., min_length=2), limit: int = Query(15, ge=1, le=50)):
    try:
        return search_attractions(city, limit)
    except Exception:  # noqa: BLE001
        log.exception("attractions failed for %s", city)
        raise HTTPException(503, "Attractions are unavailable right now. Please try again.")


@router.get("/restaurants")
def restaurants(city: str = Query(..., min_length=2), limit: int = Query(12, ge=1, le=50)):
    try:
        return search_restaurants(city, limit)
    except Exception:  # noqa: BLE001
        log.exception("restaurants failed for %s", city)
        raise HTTPException(503, "Restaurants are unavailable right now. Please try again.")


@router.get("/geocode")
def geo(q: str = Query(..., min_length=2)):
    r = geocode(q)
    if not r:
        raise HTTPException(404, "Place not found")
    return r
