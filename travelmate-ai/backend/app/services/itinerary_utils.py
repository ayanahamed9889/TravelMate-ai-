"""Pure helpers to clean up itineraries (AI output, demo data, old DB rows)."""
import math
import re
from datetime import date, timedelta
from typing import Any

SLOTS = ("morning", "afternoon", "evening")


def to_number(value: Any, default: float = 0.0) -> float:
    """'₹1,500' / '1500.5' / 1500 -> float. Negative or junk -> default."""
    if value is None or isinstance(value, bool):
        return default
    if isinstance(value, (int, float)):
        return float(value) if value >= 0 else default
    m = re.search(r"\d[\d,]*\.?\d*", str(value))
    if not m:
        return default
    try:
        n = float(m.group(0).replace(",", ""))
    except ValueError:
        return default
    return n if n >= 0 else default


# ---------------- local travel between stops ----------------
# (cost per km, minimum fare per vehicle, seats) - typical Indian city fares in INR
_VEHICLE = {"Auto": (22, 40, 3), "Cab": (15, 120, 4)}
_PER_PERSON = {"Metro": (15, 1.5, 60), "Bus": (10, 1.0, 50), "Train": (20, 1.5, 120), "Ferry": (100, 0, 100)}


def canonical_mode(mode: Any) -> str:
    m = str(mode or "").lower()
    if any(k in m for k in ("walk", "foot")):
        return "Walk"
    if any(k in m for k in ("auto", "rickshaw", "tuk")):
        return "Auto"
    if any(k in m for k in ("cab", "taxi", "uber", "ola", "car", "drive", "grab", "rideshare", "lyft")):
        return "Cab"
    if any(k in m for k in ("metro", "subway", "tram", "underground", "tube", "mrt", "light rail")):
        return "Metro"
    if "bus" in m:
        return "Bus"
    if "train" in m:
        return "Train"
    if any(k in m for k in ("boat", "ferry")):
        return "Ferry"
    return "Cab" if m else "Cab"


def travel_cost(mode: str, distance_km: float, travelers: int = 1, price_index: float = 1.0) -> float:
    """Estimated cost in INR for the WHOLE group for one hop.
    Base rates are Indian city fares; `price_index` scales them for the destination country."""
    mode, km, people = canonical_mode(mode), max(0.0, float(distance_km or 0)), max(1, int(travelers or 1))
    if mode == "Walk" or km == 0:
        return 0.0
    if mode in _VEHICLE:
        per_km, minimum, seats = _VEHICLE[mode]
        return float(round(max(minimum, per_km * km) * math.ceil(people / seats) * price_index, -1))
    base, per_km, cap = _PER_PERSON.get(mode, _PER_PERSON["Bus"])
    return float(round(min(cap, base + per_km * km) * people * price_index, -1))


def pick_mode(distance_km: float, tier: str = "moderate") -> str:
    """Sensible default vehicle for a hop when the AI did not say."""
    tier = (tier or "moderate").lower()
    if distance_km <= 1:
        return "Walk"
    if tier == "luxury":
        return "Cab"
    if tier == "budget":
        return "Auto" if distance_km <= 10 else "Bus"
    return "Auto" if distance_km <= 6 else "Cab"


def _speed_kmph(mode: str) -> float:
    return {"Walk": 4.5, "Auto": 18, "Cab": 22, "Metro": 28, "Bus": 16, "Train": 35, "Ferry": 12}.get(mode, 20)


def make_travel(distance_km: float, mode: str | None = None, travelers: int = 1, tier: str = "moderate",
                duration_minutes: int | None = None, cost_inr: float | None = None, note: str = "",
                price_index: float = 1.0) -> dict:
    km = round(max(0.0, float(distance_km or 0)), 1)
    mode = canonical_mode(mode) if mode else pick_mode(km, tier)
    minutes = duration_minutes or max(5, int(round(km / _speed_kmph(mode) * 60 / 5.0)) * 5)
    cost = cost_inr if cost_inr and cost_inr > 0 else travel_cost(mode, km, travelers, price_index)
    return {"mode": mode, "distance_km": km, "duration_minutes": int(minutes),
            "cost_inr": round(float(cost), 2), "note": note}


def _clean_travel(raw: Any, travelers: int, tier: str, price_index: float = 1.0) -> dict | None:
    if not isinstance(raw, dict):
        return None
    km = to_number(raw.get("distance_km"))
    mode = raw.get("mode")
    if km <= 0 and not raw.get("cost_inr") and not mode:
        return None
    mins = int(to_number(raw.get("duration_minutes"))) or None
    cost = to_number(raw.get("cost_inr"))
    return make_travel(km, mode, travelers, tier, mins, cost or None, _text(raw.get("note")), price_index)


def _clean_getting_there(raw: Any) -> dict | None:
    if not isinstance(raw, dict) or not _text(raw.get("to")):
        return None
    return {
        "from_place": _text(raw.get("from_place") or raw.get("from")),
        "to": _text(raw.get("to")),
        "mode": _text(raw.get("mode")) or "Transport",
        "distance_km": round(to_number(raw.get("distance_km")), 1),
        "duration_minutes": int(to_number(raw.get("duration_minutes"))),
        "cost_inr": round(to_number(raw.get("cost_inr")), 2),
        "round_trip": bool(raw.get("round_trip", True)),
        "note": _text(raw.get("note")),
    }


def _clean_time(value: Any) -> str:
    m = re.match(r"^\s*(\d{1,2}):(\d{2})", str(value or ""))
    if m and int(m.group(1)) < 24 and int(m.group(2)) < 60:
        return f"{int(m.group(1)):02d}:{m.group(2)}"
    return "09:00"


def _slot_for(start_time: str) -> str:
    hour = int(start_time[:2])
    return "morning" if hour < 12 else "afternoon" if hour < 17 else "evening"


def _text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _str_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(v).strip() for v in value if v is not None and str(v).strip()]


def normalize_itinerary(data: Any, *, destination: str = "", start_date: str | None = None,
                        num_days: int | None = None, travelers: int = 1, tier: str = "moderate",
                        price_index: float = 1.0) -> dict:
    """Return an itinerary dict that always matches ItineraryOut.

    - maps the legacy `estimated_cost` key to `estimated_cost_inr`
    - coerces numbers / times, fills slot, renumbers days, fills dates
    - trims to `num_days` when the model returned more days than requested
    """
    data = data if isinstance(data, dict) else {}
    warnings = _str_list(data.get("warnings"))
    assumptions = _str_list(data.get("assumptions"))

    try:
        start = date.fromisoformat(start_date) if start_date else None
    except ValueError:
        start = None

    raw_days = data.get("days") if isinstance(data.get("days"), list) else []
    if num_days and len(raw_days) > num_days:
        raw_days = raw_days[:num_days]
    elif num_days and 0 < len(raw_days) < num_days:
        warnings.append(f"The AI returned {len(raw_days)} of {num_days} days. "
                        "Use Re-Optimize to try again.")

    days = []
    for i, d in enumerate(raw_days):
        d = d if isinstance(d, dict) else {}
        acts = []
        for a in (d.get("activities") if isinstance(d.get("activities"), list) else []):
            if not isinstance(a, dict) or not _text(a.get("name")):
                continue
            cost = a.get("estimated_cost_inr", a.get("estimated_cost"))
            start_time = _clean_time(a.get("start_time"))
            slot = _text(a.get("slot")).lower()
            acts.append({
                "name": _text(a.get("name")),
                "description": _text(a.get("description")),
                "location": _text(a.get("location")),
                "category": _text(a.get("category")) or "Activity",
                "slot": slot if slot in SLOTS else _slot_for(start_time),
                "start_time": start_time,
                "duration_minutes": int(to_number(a.get("duration_minutes"), 90)) or 90,
                "estimated_cost_inr": round(to_number(cost), 2),
                "notes": _text(a.get("notes")),
                "travel": _clean_travel(a.get("travel"), travelers, tier, price_index),
            })
        acts.sort(key=lambda x: x["start_time"])
        day_date = (start + timedelta(days=i)).isoformat() if start else _text(d.get("date"))
        days.append({
            "day_number": i + 1,
            "date": day_date,
            "theme": _text(d.get("theme") or d.get("title")),
            "activities": acts,
        })

    return {
        "trip_title": _text(data.get("trip_title")) or (f"Trip to {destination}" if destination else ""),
        "destination": _text(data.get("destination")) or destination,
        "duration_days": len(days),
        "currency": "INR",
        "days": days,
        "assumptions": assumptions,
        "warnings": warnings,
        "source": data.get("source"),
        "getting_there": _clean_getting_there(data.get("getting_there")),
        "ai_error": _text(data.get("ai_error")) or None,
    }
