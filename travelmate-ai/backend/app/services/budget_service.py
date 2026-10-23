from collections import defaultdict

from sqlalchemy.orm import Session

from app.models import Expense, Itinerary, Trip

# Chart buckets (the frontend colours these names)
STAYS, TRANSIT, FOOD, EXPERIENCES, SHOPPING, OTHER = (
    "Stays", "Transit", "Food", "Experiences", "Shopping", "Other")

_KEYWORDS = [
    (FOOD, ("food", "restaurant", "dining", "dinner", "lunch", "breakfast", "cafe", "street food", "meal")),
    (TRANSIT, ("transit", "transport", "travel", "flight", "train", "bus", "taxi", "cab", "transfer", "commute")),
    (STAYS, ("stay", "hotel", "accommodation", "lodging", "resort", "hostel", "homestay", "check-in")),
    (SHOPPING, ("shopping", "market", "souvenir")),
]


def bucket_for(category: str) -> str:
    c = (category or "").strip().lower()
    for bucket, words in _KEYWORDS:
        if any(w in c for w in words):
            return bucket
    if c in ("misc", "other", "miscellaneous", ""):
        return OTHER
    return EXPERIENCES


def _num(x) -> float:
    try:
        return max(0.0, float(x or 0))
    except (TypeError, ValueError):
        return 0.0


def itinerary_estimate(data: dict | None) -> tuple[float, dict]:
    """Activities + local travel between stops + trip to the destination -> (total, {bucket: amount})."""
    by_bucket: dict[str, float] = defaultdict(float)
    for day in (data or {}).get("days", []) or []:
        for act in day.get("activities", []) or []:
            cost = _num(act.get("estimated_cost_inr", act.get("estimated_cost", 0)))
            if cost > 0:
                by_bucket[bucket_for(act.get("category"))] += cost
            travel = act.get("travel") or {}
            if isinstance(travel, dict) and _num(travel.get("cost_inr")) > 0:
                by_bucket[TRANSIT] += _num(travel.get("cost_inr"))
    gt = (data or {}).get("getting_there") or {}
    if isinstance(gt, dict) and _num(gt.get("cost_inr")) > 0:
        by_bucket[TRANSIT] += _num(gt.get("cost_inr"))
    by_bucket = {k: round(v, 2) for k, v in by_bucket.items()}
    return round(sum(by_bucket.values()), 2), by_bucket


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
    estimated, est_by_cat = itinerary_estimate(itin.data if itin else None)
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
