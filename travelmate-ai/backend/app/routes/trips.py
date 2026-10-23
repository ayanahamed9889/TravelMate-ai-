import logging
from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Itinerary, SavedPlace, Trip, User, utcnow
from app.schemas import (
    ItineraryOut, TripCreate, TripListOut, TripOut, TripStatsOut, TripUpdate,
)
from app.services import ai_service, pdf_service
from app.services.itinerary_utils import normalize_itinerary
from app.services.travel_service import resolve_place

log = logging.getLogger("travelmate.trips")
router = APIRouter(prefix="/trips", tags=["trips"])

StatusFilter = Literal["all", "active", "past", "drafts"]


def _owned_trip(db: Session, trip_id: int, user: User) -> Trip:
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == user.id).first()
    if not trip:
        raise HTTPException(404, "Trip not found")
    return trip


def _index(trip: Trip) -> float:
    try:
        return resolve_place(trip.destination)["index"]
    except Exception:  # noqa: BLE001
        return 1.0


def _is_draft(t: Trip) -> bool:
    return (t.status or "draft") == "draft"


def _is_past(t: Trip, today: str) -> bool:
    return bool(t.end_date) and t.end_date < today          # ISO dates compare correctly as text


def _matches(t: Trip, status: str, today: str) -> bool:
    if status == "drafts":
        return _is_draft(t)
    if status == "past":
        return not _is_draft(t) and _is_past(t, today)
    if status == "active":
        return not _is_draft(t) and not _is_past(t, today)
    return True


@router.post("", response_model=TripOut, status_code=201)
def create_trip(payload: TripCreate, db: Session = Depends(get_db),
                user: User = Depends(get_current_user)):
    trip = Trip(user_id=user.id, **payload.model_dump())
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


@router.get("", response_model=TripListOut)
def list_trips(status: StatusFilter = "all", limit: int = Query(100, ge=1, le=200),
               db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    today = date.today().isoformat()
    trips = db.query(Trip).filter(Trip.user_id == user.id).order_by(Trip.id.desc()).all()
    items = [t for t in trips if _matches(t, status, today)]
    return {"items": items[:limit], "total": len(items)}


# NOTE: must be declared before "/{trip_id}" or "stats" would be parsed as a trip id
@router.get("/stats", response_model=TripStatsOut)
def trip_stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    today = date.today().isoformat()
    trips = db.query(Trip).filter(Trip.user_id == user.id).all()
    planned = [t for t in trips if not _is_draft(t)]
    upcoming = [t for t in planned if not _is_past(t, today)]
    return {
        "upcoming": len(upcoming),
        "destinations": len({(t.destination or "").strip().lower() for t in planned}),
        "saved": db.query(SavedPlace).filter(SavedPlace.user_id == user.id).count(),
        "total_budget": float(sum(t.budget or 0 for t in upcoming)),
    }


@router.get("/{trip_id}", response_model=TripOut)
def get_trip(trip_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return _owned_trip(db, trip_id, user)


@router.put("/{trip_id}", response_model=TripOut)
def update_trip(trip_id: int, payload: TripUpdate, db: Session = Depends(get_db),
                user: User = Depends(get_current_user)):
    trip = _owned_trip(db, trip_id, user)
    changes = payload.model_dump(exclude_unset=True)
    for k, v in changes.items():
        if v is None and k in ("destination", "travelers", "budget"):
            continue                       # never null out required columns
        setattr(trip, k, v)
    if trip.start_date and trip.end_date and trip.end_date < trip.start_date:
        raise HTTPException(422, "End date cannot be before the start date")
    db.commit()
    db.refresh(trip)
    return trip


@router.delete("/{trip_id}")
def delete_trip(trip_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    trip = _owned_trip(db, trip_id, user)
    db.delete(trip)
    db.commit()
    return {"ok": True}


@router.post("/{trip_id}/generate", response_model=ItineraryOut)
def generate(trip_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    trip = _owned_trip(db, trip_id, user)
    try:
        data = ai_service.generate_itinerary(trip)
    except Exception:  # noqa: BLE001
        log.exception("Itinerary generation crashed for trip %s", trip_id)
        raise HTTPException(503, "Could not generate the itinerary right now. Please try again.")

    existing = db.query(Itinerary).filter(Itinerary.trip_id == trip.id).first()
    if existing:
        existing.data = data
        existing.warnings = data.get("warnings", [])
        existing.assumptions = data.get("assumptions", [])
        existing.generated_at = utcnow()
    else:
        db.add(Itinerary(trip_id=trip.id, data=data,
                         warnings=data.get("warnings", []),
                         assumptions=data.get("assumptions", [])))
    trip.status = "generated"
    db.commit()
    return data


@router.get("/{trip_id}/itinerary", response_model=ItineraryOut)
def get_itinerary(trip_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    trip = _owned_trip(db, trip_id, user)
    it = db.query(Itinerary).filter(Itinerary.trip_id == trip.id).first()
    if not it:
        raise HTTPException(404, "No itinerary yet")
    # also repairs older rows (e.g. the legacy `estimated_cost` key)
    return normalize_itinerary(it.data, destination=trip.destination, start_date=trip.start_date,
                               travelers=trip.travelers, tier=trip.budget_tier,
                               price_index=_index(trip))


@router.get("/{trip_id}/export/pdf")
def export_pdf(trip_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    trip = _owned_trip(db, trip_id, user)
    it = db.query(Itinerary).filter(Itinerary.trip_id == trip.id).first()
    if not it:
        raise HTTPException(400, "Generate the itinerary first")
    data = normalize_itinerary(it.data, destination=trip.destination, start_date=trip.start_date,
                               travelers=trip.travelers, tier=trip.budget_tier,
                               price_index=_index(trip))
    buf = pdf_service.build_trip_pdf(trip, data)
    return StreamingResponse(
        buf, media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=travelmate-trip-{trip_id}.pdf"},
    )
