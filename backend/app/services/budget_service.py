from collections import defaultdict

from sqlalchemy.orm import Session

from app.models import Expense, Itinerary, Trip

from app.services.trip_costs import (  # noqa: F401  (re-exported for callers)
    STAYS, GETTING_THERE, TRANSIT, FOOD, EXPERIENCES, SHOPPING, OTHER,
    bucket_for, enrich_itinerary, itinerary_estimate,
)
from app.services.travel_service import resolve_place


def _spent(expenses) -> tuple[float, dict]:
    by_bucket: dict[str, float] = defaultdict(float)
    for e in expenses:
        by_bucket[bucket_for(e.category)] += e.amount or 0
    by_bucket = {k: round(v, 2) for k, v in by_bucket.items()}
    return round(sum(by_bucket.values()), 2), by_bucket


def _pct(part: float, whole: float) -> float:
    return round(part / whole * 100, 1) if whole else 0.0


def compute_budget(db: Session, trip: Trip) -> dict:
    expenses = (db.query(Expense).filter(Expense.trip_id == trip.id)
                .order_by(Expense.id.desc()).all())
    itin = db.query(Itinerary).filter(Itinerary.trip_id == trip.id).first()
    data = None
    if itin:
        # older itineraries have no hotel yet: add the stay estimate so budget == trip page
        try:
            place = resolve_place(trip.destination)
        except Exception:  # noqa: BLE001
            place = {"index": 1.0, "country": "", "cc": ""}
        data = enrich_itinerary(dict(itin.data or {}), trip, index=place.get("index", 1.0),
                                country=place.get("country", ""), cc=place.get("cc", ""))
    estimated, est_by_cat = itinerary_estimate(data)
    spent, spent_by_cat = _spent(expenses)
    total_budget = float(trip.budget or 0)

    return {
        "total_budget_inr": total_budget,
        "estimated_total_inr": estimated,
        "spent_inr": spent,
        "remaining_inr": round(total_budget - estimated, 2),
        "utilization": _pct(estimated, total_budget),
        "by_category_inr": est_by_cat,
        "spent_by_category_inr": spent_by_cat,
        "expenses": expenses,
    }


def budget_overview(db: Session, user_id: int) -> dict:
    trips = (db.query(Trip).filter(Trip.user_id == user_id)
             .order_by(Trip.id.desc()).all())
    out, tb, te, ts = [], 0.0, 0.0, 0.0
    for t in trips:
        b = compute_budget(db, t)
        # Chart shows what was spent if the user logged expenses, otherwise the AI estimate
        source = b["spent_by_category_inr"] if b["spent_inr"] > 0 else b["by_category_inr"]
        out.append({
            "id": t.id,
            "title": t.destination,
            "budget_inr": b["total_budget_inr"],
            "estimated_inr": b["estimated_total_inr"],
            "spent_inr": b["spent_inr"],
            "remaining_inr": round(b["total_budget_inr"] - (b["spent_inr"] or b["estimated_total_inr"]), 2),
            "utilization": _pct(b["spent_inr"] or b["estimated_total_inr"], b["total_budget_inr"]),
            "breakdown": [{"category": k, "amount": v} for k, v in source.items()],
            "expenses": b["expenses"][:5],
        })
        tb += b["total_budget_inr"]
        te += b["estimated_total_inr"]
        ts += b["spent_inr"]
    return {"trips": out, "total_budget_inr": round(tb, 2),
            "total_estimated_inr": round(te, 2), "total_spent_inr": round(ts, 2)}
