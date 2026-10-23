"""Place context (country, price level) and the cost of getting from home to the destination."""
import logging
import math

from app.services.place_service import geocode
from app.utils.destinations import find_by_name
from app.utils.pricing import price_index

log = logging.getLogger("travelmate.travel")


def resolve_place(name: str | None) -> dict:
    """{country, cc, index} for a destination. Uses the built-in catalog first, then OpenStreetMap."""
    name = (name or "").strip()
    if not name:
        return {"country": "", "cc": "", "index": price_index(None)}
    d = find_by_name(name)
    if d:
        return {"country": d["country"], "cc": d["cc"], "index": price_index(d["cc"])}
    try:
        g = geocode(name) or {}
    except Exception as e:  # noqa: BLE001
        log.warning("resolve_place geocode failed: %s", e)
        g = {}
    cc = g.get("cc", "")
    return {"country": g.get("country", ""), "cc": cc, "index": price_index(cc)}


def _haversine_km(a: dict, b: dict) -> float:
    r = 6371.0
    p1, p2 = math.radians(a["lat"]), math.radians(b["lat"])
    dphi, dl = p2 - p1, math.radians(b["lon"] - a["lon"])
    h = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def _flight_one_way(air_km: float) -> float:
    """Economy one-way per person in INR (planning estimate)."""
    if air_km <= 2500:
        return max(3000, 2500 + 4.2 * air_km)
    return 9000 + 2.4 * air_km            # long-haul is cheaper per km


def estimate(distance_air_km: float, mode: str, travelers: int, dest_index: float = 1.0) -> dict:
    """Round-trip estimate for the whole group. Rough planning numbers, not fares."""
    people = max(1, int(travelers or 1))
    road = distance_air_km * 1.3
    m = (mode or "").lower()
    wants_flight = any(k in m for k in ("flight", "air", "fly"))
    switched = False
    if not wants_flight and distance_air_km > 1500:      # too far (or across an ocean) for land travel
        wants_flight, switched = True, True
    land = max(1.0, dest_index) ** 0.6                   # Europe/Japan rail & fuel cost more than India

    if wants_flight:
        label, km = "Flight", distance_air_km
        total = _flight_one_way(distance_air_km) * 2 * people
        minutes = int(distance_air_km / 780 * 60 + 150 + (90 if distance_air_km > 6000 else 0))
        note = "Typical economy fare incl. taxes; prices vary a lot by date - check live fares."
        if switched:
            note = "Too far for land travel, so a flight is assumed. " + note
    elif "train" in m or "rail" in m:
        label, km = "Train", road
        total = max(350, 2.4 * road) * land * 2 * people
        minutes = int(road / 55 * 60)
        note = "Based on a mid-class (3AC-type) fare; budget classes are cheaper."
    elif "bus" in m:
        label, km = "Bus", road
        total = max(250, 1.1 * road) * land * 2 * people
        minutes = int(road / 45 * 60)
        note = "Typical AC coach fare."
    else:                                                # Car
        label, km = "Car", road
        total = road * 2 * 12 * land * math.ceil(people / 4)
        minutes = int(road / 50 * 60)
        note = "Fuel + tolls for the round trip; excludes driver and parking."
    return {"mode": label, "distance_km": round(km), "duration_minutes": minutes,
            "cost_inr": float(round(total, -2)), "round_trip": True, "note": note}


def getting_there(departure: str | None, destination: str, mode: str, travelers: int,
                  dest_index: float = 1.0) -> dict | None:
    """None when the home city is unknown, cannot be located, or is practically the same place."""
    if not departure or not departure.strip() or not destination:
        return None
    try:
        a, b = geocode(departure.strip()), geocode(destination.strip())
    except Exception as e:  # noqa: BLE001
        log.warning("geocode failed: %s", e)
        return None
    if not a or not b:
        return None
    air = _haversine_km(a, b)
    if air < 30:
        return None
    out = estimate(air, mode, travelers, dest_index)
    out.update({"from_place": departure.strip().title(), "to": destination.strip().title()})
    return out
