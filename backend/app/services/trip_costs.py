"""Trip cost model: hotel/stay estimate, full cost summary, budget advice and rule-based suggestions.

Everything here is a pure function (no database, no network) so it is easy to test.
All amounts are INR for the WHOLE group unless a key says otherwise.
"""
import math
from collections import defaultdict
from urllib.parse import quote_plus

from app.services.itinerary_utils import clean_hotel, clean_suggestions
from app.utils.destinations import find_by_name
from app.utils.helpers import days_between

# ---------------------------------------------------------------- buckets
# Chart / budget buckets (the frontend colours these names)
STAYS, GETTING_THERE, TRANSIT, FOOD, EXPERIENCES, SHOPPING, OTHER = (
    "Stays", "Getting there", "Transit", "Food", "Experiences", "Shopping", "Other")

_KEYWORDS = [
    (FOOD, ("food", "restaurant", "dining", "dinner", "lunch", "breakfast", "cafe", "street food", "meal")),
    (GETTING_THERE, ("getting there", "flight", "airfare", "airline", "air ticket")),
    (TRANSIT, ("transit", "transport", "travel", "train", "bus", "taxi", "cab", "transfer", "commute")),
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
    """Activities + local travel + stay + trip to the destination -> (total, {bucket: amount})."""
    data = data or {}
    by: dict[str, float] = defaultdict(float)
    hotel = data.get("hotel") if isinstance(data.get("hotel"), dict) else {}
    stay_total = _num(hotel.get("cost_inr"))

    for day in data.get("days", []) or []:
        for act in day.get("activities", []) or []:
            bucket = bucket_for(act.get("category"))
            cost = _num(act.get("estimated_cost_inr", act.get("estimated_cost", 0)))
            # the hotel is priced once by estimate_stay(); never count a "Stay" activity on top of it
            if cost > 0 and not (bucket == STAYS and stay_total > 0):
                by[bucket] += cost
            travel = act.get("travel") or {}
            if isinstance(travel, dict) and _num(travel.get("cost_inr")) > 0:
                by[TRANSIT] += _num(travel.get("cost_inr"))

    if stay_total > 0:
        by[STAYS] += stay_total
    gt = data.get("getting_there") or {}
    if isinstance(gt, dict) and _num(gt.get("cost_inr")) > 0:
        by[GETTING_THERE] += _num(gt.get("cost_inr"))

    by = {k: round(v, 2) for k, v in by.items()}
    return round(sum(by.values()), 2), by


# ---------------------------------------------------------------- stay (hotel)
# Typical price of ONE room per night (a bed for hostels) at Indian mid-range level, in INR.
_STAY_BASE = {"hotel": 3500, "resort": 7500, "hostel": 900, "homestay": 2200}
_TIER_MULT = {"budget": 0.55, "moderate": 1.0, "luxury": 2.4}
_TIER_LABEL = {"budget": "Budget", "moderate": "Mid-range", "luxury": "Premium"}


def _round_to(value: float, step: int = 50) -> float:
    return float(int(round(value / step)) * step)


def _unit_price(key: str, tier: str, index: float) -> float:
    mult = _TIER_MULT.get(tier, 1.0)
    if key == "hostel":
        mult = min(mult, 1.5)                       # hostels have no real "luxury" level
    return max(300.0, _round_to(_STAY_BASE[key] * mult * (max(index, 0.5) ** 0.9)))


def _units(key: str, people: int, trip_type: str) -> tuple[int, str]:
    if key == "hostel":
        return people, "bed"
    occupancy = 3 if key == "homestay" or (trip_type or "").strip().lower() == "family" else 2
    return math.ceil(people / occupancy), "room"


def booking_link(destination: str, start_date: str | None, end_date: str | None,
                 adults: int, rooms: int) -> str:
    url = f"https://www.booking.com/searchresults.html?ss={quote_plus(destination or '')}"
    if start_date and end_date:
        url += f"&checkin={start_date}&checkout={end_date}"
    return url + f"&group_adults={max(1, adults)}&no_rooms={max(1, rooms)}"


def trip_nights(start_date: str | None, end_date: str | None) -> tuple[int, int]:
    """(nights, days). A one-day trip has no overnight stay."""
    days = days_between(start_date, end_date)
    return max(0, days - 1), days


def estimate_stay(*, accommodation: str, tier: str, travelers: int, trip_type: str, nights: int,
                  index: float, destination: str = "", start_date: str | None = None,
                  end_date: str | None = None, country: str = "") -> dict:
    key = (accommodation or "hotel").strip().lower()
    key = key if key in _STAY_BASE else "hotel"
    tier = (tier or "moderate").strip().lower()
    tier = tier if tier in _TIER_MULT else "moderate"
    people = max(1, int(travelers or 1))
    nights = max(0, int(nights or 0))
    units, unit = _units(key, people, trip_type)
    per_night = _unit_price(key, tier, index)

    options = []
    for t in ("budget", "moderate", "luxury"):
        price = _unit_price(key, t, index)
        options.append({"label": f"{_TIER_LABEL[t]} {key}", "tier": t, "per_night_inr": price,
                        "total_inr": float(price * units * nights), "selected": t == tier})

    if nights == 0:
        note = "Single-day trip - no overnight stay is counted."
    else:
        where = country or destination or "this destination"
        note = (f"{nights} night{'s' if nights != 1 else ''} x {units} {unit}{'s' if units != 1 else ''} "
                f"x {_fmt(per_night)} per {unit} per night. Typical {tier} {key} prices in {where}; "
                "check live prices before booking.")

    return {
        "accommodation": key.title(), "tier": tier, "nights": nights, "rooms": units, "unit": unit,
        "per_night_inr": per_night, "cost_inr": float(per_night * units * nights), "options": options,
        "booking_link": booking_link(destination, start_date, end_date, people, units) if destination else "",
        "note": note, "cheaper_option": None,
    }


def _cheaper_option(trip, stay: dict, index: float, country: str) -> dict | None:
    """The cheapest realistic alternative to the chosen stay (None when already the cheapest)."""
    if stay["cost_inr"] <= 0:
        return None
    best = None
    people = max(1, int(trip.travelers or 1))
    social = (trip.trip_type or "").strip().lower() in ("solo", "friends") and people <= 8
    for acc in (("hotel", "homestay", "hostel") if social else ("hotel", "homestay")):
        alt = estimate_stay(accommodation=acc, tier="budget", travelers=trip.travelers,
                            trip_type=trip.trip_type, nights=stay["nights"], index=index, country=country)
        if best is None or alt["cost_inr"] < best["cost_inr"]:
            best = alt
    saving = stay["cost_inr"] - best["cost_inr"]
    if saving < max(1000.0, stay["cost_inr"] * 0.1):
        return None
    return {"label": f"Budget {best['accommodation'].lower()}", "total_inr": best["cost_inr"],
            "saving_inr": float(round(saving, -2))}


# ---------------------------------------------------------------- suggestions
def _tags(dest_info) -> list[str]:
    return [str(t).lower() for t in (dest_info or {}).get("tags", [])]


def rule_suggestions(trip, *, num_days: int, country: str = "", cc: str = "") -> dict:
    """Useful, honest general tips when the live AI gave none (no invented places or prices)."""
    dest_name = (trip.destination or "").strip().title()
    info = find_by_name(trip.destination or "")
    international = bool(cc) and cc.upper() != "IN"
    people = max(1, int(trip.travelers or 1))
    tier = (trip.budget_tier or "moderate").lower()
    prefs = [str(p).lower() for p in (trip.preferences or [])]
    tags = _tags(info)
    place = country or dest_name

    money = [
        "Book flights 6-10 weeks ahead and compare 2-3 nearby dates; moving by a day or two can cut fares by 10-25%.",
        "Stay near a metro or railway station instead of the very centre - often 20-30% cheaper and well connected.",
        "Eat one meal a day where locals eat (lunch sets and street stalls are the cheapest way to try local food).",
        "Walk or use public transport for short hops - this plan shows the cost of every hop so you can compare.",
        "Look for free things: walking tours, parks, viewpoints and market visits.",
    ]
    if people >= 3:
        money.append("In a group of 3+, share cabs and pick triple/family rooms instead of separate rooms.")
    if international:
        money.append("Use a forex card or no-fee debit card and avoid airport currency counters (worse rates).")

    food = ["Ask your hotel for 2-3 local favourites; a queue of locals is a good sign."]
    if "food" in prefs:
        food.append("You enjoy food - add a street-food walk or a local cooking class.")
    if international:
        food.append(f"Pure vegetarian? Search '{place} vegetarian restaurants' and save a few places offline.")

    transport = [f"Download an offline map of {dest_name or 'the city'} and install the local ride app (varies by city).",
                 "Keep small change for autos, buses and tips."]
    if international:
        transport.append("Buy an eSIM or local SIM on arrival, or check international roaming packs before you leave.")

    safety = ["Keep digital and paper copies of ID, tickets and bookings.",
              "Use metered or app-based cabs; avoid unmarked taxis at the airport."]
    if international:
        safety.append("Buy travel insurance (medical + baggage) and make sure your passport is valid for 6+ months.")
    if "adventure" in tags or "adventure" in prefs:
        safety.append("Book adventure activities only with licensed operators and check the weather first.")

    packing = ["Power bank, a universal adapter (if abroad) and a reusable water bottle."]
    if "snow" in tags:
        packing.append("Warm layers, gloves and shoes with good grip.")
    if "beaches" in tags or "beaches" in prefs:
        packing.append("Sunscreen, swimwear and quick-dry clothes.")
    if {"spiritual", "heritage"} & set(tags):
        packing.append("Modest clothing (shoulders and knees covered) for temples and heritage sites.")
    if "desert" in tags:
        packing.append("Light cotton clothes by day and a jacket for cold desert nights.")

    out = {
        "summary": (f"{num_days}-day {(trip.trip_type or 'trip').lower()} trip to {dest_name} for {people} "
                    f"traveller{'s' if people != 1 else ''} on a {tier} budget. Flights, hotel and the cost of "
                    "every stop are included in the estimate."),
        "best_areas_to_stay": [
            "Close to the main sights / old town - walk more and spend less on cabs.",
            "Near a metro or railway station - cheaper and well connected.",
            "A quieter residential area - calmer nights and good value.",
        ],
        "hotel_picks": [],
        "money_saving": money, "food": food, "transport": transport, "safety": safety, "packing": packing,
        "hidden_gems": [],
        "best_time": f"Best time to visit {dest_name}: {info['best_time']}." if info and info.get("best_time") else "",
        "visa": (f"Indian passport holders: check visa / e-visa / visa-on-arrival rules for {place} before booking. "
                 "Rules change, so confirm on the official immigration or embassy website.") if international else "",
        "source": "rules",
    }
    return out


_LIST_KEYS = ("best_areas_to_stay", "money_saving", "food", "transport", "safety", "packing", "hidden_gems")


def merge_suggestions(ai_raw, rules: dict) -> dict:
    """AI suggestions win; anything the AI left out is filled from the rule-based tips."""
    out = dict(rules)
    ai = clean_suggestions(ai_raw)
    if not ai or ai.get("source") == "rules":      # stored rule-based tips are simply regenerated
        return out
    used_ai = False
    for k in _LIST_KEYS:
        if ai.get(k):
            out[k] = ai[k]
            used_ai = True
    for k in ("summary", "best_time"):
        if ai.get(k):
            out[k] = ai[k]
            used_ai = True
    if ai.get("hotel_picks"):
        out["hotel_picks"] = ai["hotel_picks"]
        used_ai = True
    out["source"] = "ai" if used_ai else "rules"
    return out


# ---------------------------------------------------------------- enrich + summary
def enrich_itinerary(data: dict, trip, *, index: float = 1.0, country: str = "", cc: str = "") -> dict:
    """Idempotent: (re)computes the hotel from the trip, fills suggestions, never double-counts the stay."""
    data = data if isinstance(data, dict) else {}
    nights, days = trip_nights(trip.start_date, trip.end_date)
    stay = estimate_stay(accommodation=trip.accommodation, tier=trip.budget_tier, travelers=trip.travelers,
                         trip_type=trip.trip_type, nights=nights, index=index, destination=trip.destination,
                         start_date=trip.start_date, end_date=trip.end_date, country=country)
    stay["cheaper_option"] = _cheaper_option(trip, stay, index, country)
    data["hotel"] = clean_hotel(stay)

    if stay["cost_inr"] > 0:                       # the hotel is priced separately
        for day in data.get("days", []) or []:
            for act in day.get("activities", []) or []:
                if bucket_for(act.get("category")) == STAYS:
                    act["estimated_cost_inr"] = 0

    num_days = len(data.get("days") or []) or days
    data["suggestions"] = merge_suggestions(data.get("suggestions"),
                                            rule_suggestions(trip, num_days=num_days, country=country, cc=cc))
    return data


_LABELS = {
    GETTING_THERE: "Flights / getting there", STAYS: "Hotel / stay", TRANSIT: "Local transport",
    FOOD: "Food & dining", EXPERIENCES: "Sightseeing & activities", SHOPPING: "Shopping", OTHER: "Other",
}


def _fmt(n: float) -> str:
    """Rs. 1,23,456 (Indian digit grouping)."""
    n = int(round(n))
    sign, digits = ("-" if n < 0 else ""), str(abs(n))
    if len(digits) > 3:
        head, tail = digits[:-3], digits[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        digits = ",".join(parts + [tail])
    return f"{sign}Rs. {digits}"


def build_cost_summary(data: dict, trip) -> dict:
    total, by = itinerary_estimate(data)
    hotel = data.get("hotel") or {}
    gt = data.get("getting_there") or {}
    people = max(1, int(trip.travelers or 1))
    _, days = trip_nights(trip.start_date, trip.end_date)
    budget = float(trip.budget or 0)

    details = {
        GETTING_THERE: (f"{gt.get('mode', 'Travel')} round trip for {people} - {gt.get('from_place') or 'home'} to "
                        f"{gt.get('to', trip.destination)}") if _num(gt.get("cost_inr")) > 0
        else "Add your home city to the trip to see the flight / travel cost.",
        STAYS: (hotel.get("note") or "") if hotel else "",
        TRANSIT: "Taxis, autos, metro and buses between stops",
        FOOD: "Meals planned in the itinerary",
        EXPERIENCES: "Entry tickets, tours and experiences",
        SHOPPING: "Markets and souvenirs",
        OTHER: "Miscellaneous",
    }
    labels = dict(_LABELS)
    mode = (gt.get("mode") or "").strip()
    if _num(gt.get("cost_inr")) > 0 and mode:
        labels[GETTING_THERE] = "Flights" if mode.lower() == "flight" else f"{mode} fare (getting there)"
    items = []
    for key in (GETTING_THERE, STAYS, TRANSIT, FOOD, EXPERIENCES, SHOPPING, OTHER):
        amount = float(by.get(key, 0))
        if amount <= 0 and key not in (GETTING_THERE, STAYS):
            continue
        items.append({"key": key, "label": labels[key], "amount": round(amount, 2),
                      "detail": details[key], "percent": round(amount / total * 100, 1) if total else 0.0})

    buffer = round(total * 0.10, 2)
    with_buffer = round(total + buffer, 2)
    if budget <= 0:
        status = "no_budget"
    elif with_buffer <= budget:
        status = "within"
    elif total <= budget:
        status = "tight"
    else:
        status = "over"

    advice: list[str] = []
    top = max((i for i in items if i["amount"] > 0), key=lambda i: i["amount"], default=None)
    if status == "over":
        advice.append(f"Estimated {_fmt(total)} is {_fmt(total - budget)} more than your budget of {_fmt(budget)}."
                      + (f" Biggest cost: {top['label']} ({_fmt(top['amount'])})." if top else ""))
        cheaper = hotel.get("cheaper_option")
        if cheaper:
            advice.append(f"Switching to a {cheaper['label'].lower()} would save about {_fmt(cheaper['saving_inr'])}.")
        if by.get(GETTING_THERE, 0) > 0.25 * total:
            advice.append("Flights/travel are a big share - try flexible dates or booking 6-10 weeks ahead.")
        advice.append("You can also shorten the trip or pick a lower budget tier and re-generate the plan.")
    elif status == "tight":
        advice.append(f"Within budget, but only {_fmt(budget - total)} is left - keep it for surprises.")
    elif status == "within":
        spare = budget - with_buffer
        advice.append(f"Looks affordable: even with a 10% safety buffer you keep about {_fmt(spare)} of your budget.")
        nxt = {"budget": "moderate", "moderate": "luxury"}.get((hotel.get("tier") or ""), "")
        up = next((o for o in hotel.get("options", []) if o.get("tier") == nxt), None)
        if up and hotel.get("cost_inr", 0) > 0:
            extra = up["total_inr"] - hotel["cost_inr"]
            if 0 < extra <= spare:
                advice.append(f"You could upgrade to a {up['label'].lower()} for about {_fmt(extra)} more.")

    return {
        "items": items, "subtotal_inr": round(total, 2), "buffer_inr": buffer, "total_with_buffer_inr": with_buffer,
        "budget_inr": budget, "remaining_inr": round(budget - total, 2) if budget > 0 else 0.0,
        "per_person_inr": round(total / people, 2), "per_day_inr": round(total / max(1, days), 2),
        "status": status, "advice": advice,
    }


def finalize_itinerary(data: dict, trip, *, index: float = 1.0, country: str = "", cc: str = "") -> dict:
    """Enrich + attach the cost summary. This is what the API returns."""
    data = enrich_itinerary(data, trip, index=index, country=country, cc=cc)
    data["cost_summary"] = build_cost_summary(data, trip)
    return data
