"""Flights.

The previous implementation used the Amadeus Self-Service API, which Amadeus
shut down on 17 July 2026 - it can no longer return data. Until a new provider
is plugged in, this module returns clearly-labelled SAMPLE fares
(`source: "demo"`) generated deterministically from the route + date.
"""
import math
import random
from datetime import date, datetime, timedelta

from app.utils.airports import AIRPORTS, INDIAN_AIRPORTS

DOMESTIC_AIRLINES = ["6E", "AI", "IX", "QP", "SG"]          # IndiGo, Air India, Air India Express, Akasa, SpiceJet
# Airlines by region of the route's far end (sample data only)
INTL_AIRLINES = ["AI", "6E", "EK", "QR", "EY", "SQ", "TK", "BA", "LH", "AF", "KL", "TG", "CX", "JL", "QF", "AA", "UA", "DL", "AC"]


def _km(a: str, b: str):
    """Great-circle distance between two known airports, else None."""
    if a not in AIRPORTS or b not in AIRPORTS:
        return None
    _, la1, lo1 = AIRPORTS[a]
    _, la2, lo2 = AIRPORTS[b]
    p1, p2 = math.radians(la1), math.radians(la2)
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lo2 - lo1) / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(h))


def _validate(origin: str, destination: str, depart_date: str, return_date: str | None):
    o, d = origin.strip().upper(), destination.strip().upper()
    if len(o) != 3 or len(d) != 3 or not o.isalpha() or not d.isalpha():
        raise ValueError("Use 3-letter airport codes, e.g. DEL, BOM, JAI")
    if o == d:
        raise ValueError("Origin and destination must be different")
    try:
        dep = date.fromisoformat(depart_date)
    except ValueError:
        raise ValueError("Departure date must be YYYY-MM-DD")
    if dep < date.today():
        raise ValueError("Departure date cannot be in the past")
    if return_date:
        try:
            ret = date.fromisoformat(return_date)
        except ValueError:
            raise ValueError("Return date must be YYYY-MM-DD")
        if ret < dep:
            raise ValueError("Return date cannot be before departure")
    return o, d, dep


def _iso_duration(minutes: int) -> str:
    return f"PT{minutes // 60}H{minutes % 60:02d}M"


def search_flights(origin: str, destination: str, depart_date: str,
                   return_date: str | None = None, adults: int = 1):
    o, d, dep = _validate(origin, destination, depart_date, return_date)
    adults = max(1, min(int(adults or 1), 9))
    domestic = o in INDIAN_AIRPORTS and d in INDIAN_AIRPORTS
    km = _km(o, d)                                           # None for airports outside our table
    rng = random.Random(f"{o}-{d}-{dep.isoformat()}")      # same search -> same sample results

    flights = []
    for i in range(rng.randint(6, 9)):
        airline = rng.choice(DOMESTIC_AIRLINES if domestic else INTL_AIRLINES)
        if km is not None:
            minutes = int(km / 800 * 60 + 40 + rng.randint(-10, 25))
            fare = (2500 + 3.2 * km) if km < 2500 else (7000 + 2.6 * km)
            fare = fare * rng.uniform(0.8, 1.35) if not domestic else min(fare, 12000) * rng.uniform(0.7, 1.3)
            long_haul = km > 6500
        else:                                                # unknown airport: rough fallback
            minutes = rng.randint(70, 180) if domestic else rng.randint(200, 720)
            fare = rng.randint(2800, 9500) if domestic else rng.randint(14000, 62000)
            long_haul = minutes > 600
        stops = 0
        if not domestic and (long_haul and rng.random() < 0.6 or (km or 0) > 3500 and rng.random() < 0.25):
            stops = 1
        if stops:
            minutes += rng.randint(90, 240)
            fare *= 0.85
        depart_at = datetime.combine(dep, datetime.min.time()) + timedelta(
            hours=rng.randint(0, 23), minutes=rng.choice([0, 10, 20, 30, 40, 50]))
        flights.append({
            "id": f"demo-{i + 1}",
            "price_inr": float(round(fare * adults, -1)),
            "airline": airline,
            "flight_number": str(rng.randint(100, 9999)),
            "origin": o,
            "destination": d,
            "departure_time": depart_at.isoformat(timespec="minutes"),
            "arrival_time": (depart_at + timedelta(minutes=minutes)).isoformat(timespec="minutes"),
            "duration": _iso_duration(minutes),
            "stops": stops,
            "cabin": "ECONOMY",
            "source": "demo",
        })
    flights.sort(key=lambda f: f["price_inr"])
    return flights
