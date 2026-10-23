"""Hotels via Geoapify Places (free tier). Prices are not available from this API,
so cards link to a Booking.com search for the live price. Without a key (or if the
API fails) clearly-labelled sample hotels are returned."""
import logging
from datetime import date, timedelta
from urllib.parse import quote_plus

import httpx

from app.config import settings

log = logging.getLogger("travelmate.hotels")

TYPE_LABELS = {
    "hotel": "Hotel", "hostel": "Hostel", "guest_house": "Guest house",
    "motel": "Motel", "apartment": "Apartment", "chalet": "Chalet",
}


def _nights(check_in: str, check_out: str) -> int:
    try:
        return max(1, (date.fromisoformat(check_out) - date.fromisoformat(check_in)).days)
    except ValueError:
        return 1


def _booking_link(name: str, check_in: str, check_out: str, adults: int, rooms: int) -> str:
    return (
        "https://www.booking.com/searchresults.html"
        f"?ss={quote_plus(name)}&checkin={check_in}&checkout={check_out}"
        f"&group_adults={adults}&no_rooms={rooms}"
    )


def _normalize_dates(check_in: str, check_out: str) -> tuple[str, str]:
    today = date.today()
    try:
        ci = date.fromisoformat(check_in) if check_in else today + timedelta(days=7)
    except ValueError:
        ci = today + timedelta(days=7)
    try:
        co = date.fromisoformat(check_out) if check_out else ci + timedelta(days=2)
    except ValueError:
        co = ci + timedelta(days=2)
    if co <= ci:
        co = ci + timedelta(days=1)
    return ci.isoformat(), co.isoformat()


def search_hotels(city: str, check_in: str = "", check_out: str = "", adults: int = 2, rooms: int = 1):
    check_in, check_out = _normalize_dates(check_in, check_out)
    nights = _nights(check_in, check_out)

    if not settings.geoapify_api_key:
        return get_fallback_hotels(city, check_in, check_out, adults, rooms)

    try:
        with httpx.Client(timeout=15) as c:
            geo = c.get("https://api.geoapify.com/v1/geocode/search", params={
                "text": city, "limit": 1, "apiKey": settings.geoapify_api_key})
            geo.raise_for_status()
            features = geo.json().get("features") or []
            if not features:
                return get_fallback_hotels(city, check_in, check_out, adults, rooms)
            lat = features[0]["properties"]["lat"]
            lon = features[0]["properties"]["lon"]

            r = c.get("https://api.geoapify.com/v2/places", params={
                "categories": "accommodation.hotel,accommodation.hostel,accommodation.guest_house",
                "filter": f"circle:{lon},{lat},4000",
                "bias": f"proximity:{lon},{lat}",
                "limit": 30,
                "apiKey": settings.geoapify_api_key,
            })
            r.raise_for_status()
            data = r.json()
    except Exception as e:  # noqa: BLE001  (never log the URL: it contains the API key)
        log.warning("Geoapify hotel search failed: %s", type(e).__name__)
        return get_fallback_hotels(city, check_in, check_out, adults, rooms)

    hotels, seen = [], set()
    for feature in data.get("features", []):
        props = feature.get("properties", {})
        name = (props.get("name") or "").strip()
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        raw = (props.get("datasource") or {}).get("raw") or {}
        try:
            stars = int(float(str(raw.get("stars", 0)).split()[0]))
        except (ValueError, IndexError):
            stars = 0
        kind = (props.get("categories") or ["accommodation.hotel"])[0].split(".")[-1]
        hotels.append({
            "id": str(props.get("place_id", name)),
            "name": name,
            "type": TYPE_LABELS.get(kind, "Hotel"),
            "address": props.get("address_line2") or props.get("formatted") or city,
            "location": props.get("suburb") or props.get("city") or city,
            "city": city,
            "lat": props.get("lat"),
            "lon": props.get("lon"),
            "stars": max(0, min(stars, 5)),
            "phone": (props.get("contact") or {}).get("phone", ""),
            "website": props.get("website") or raw.get("website") or "",
            "price_inr": None,                 # not provided by Geoapify
            "price_per_night_inr": None,
            "nights": nights,
            "image": "",                       # frontend draws a placeholder cover
            "booking_link": _booking_link(name, check_in, check_out, adults, rooms),
            "source": "geoapify",
        })

    return hotels or get_fallback_hotels(city, check_in, check_out, adults, rooms)


_SAMPLE = [
    ("Heritage Palace Stay", 5, 9500, "Old City"),
    ("Riverside Boutique Hotel", 4, 6200, "Riverfront"),
    ("Central Plaza Hotel", 4, 4800, "City Centre"),
    ("Comfort Inn Station Road", 3, 2800, "Near Railway Station"),
    ("Backpackers Hostel", 2, 900, "Market Area"),
    ("Garden View Guest House", 3, 2200, "Quiet Residential Area"),
]


def get_fallback_hotels(city: str, check_in: str = "", check_out: str = "",
                        adults: int = 2, rooms: int = 1):
    check_in, check_out = _normalize_dates(check_in, check_out)
    nights = _nights(check_in, check_out)
    rooms = max(1, rooms)
    return [{
        "id": f"demo-{i + 1}",
        "name": f"{name} ({city})",
        "type": "Hotel",
        "address": area,
        "location": area,
        "city": city,
        "lat": None,
        "lon": None,
        "stars": stars,
        "price_per_night_inr": float(price),
        "price_inr": float(price * nights * rooms),
        "nights": nights,
        "image": "",
        "booking_link": f"https://www.booking.com/searchresults.html?ss={quote_plus(city)}"
                        f"&checkin={check_in}&checkout={check_out}&group_adults={adults}&no_rooms={rooms}",
        "source": "demo",
    } for i, (name, stars, price, area) in enumerate(_SAMPLE)]
