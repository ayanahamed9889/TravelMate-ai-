"""Attractions + restaurants: OpenStreetMap (Nominatim/Overpass) with optional Foursquare."""
import logging
import time

import httpx

from app.config import settings

log = logging.getLogger("travelmate.places")

HEADERS = {"User-Agent": "TravelMateAI/1.1 (student project)"}
OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]

# Nominatim allows ~1 request/second, so geocoding results are cached
_GEO_CACHE: dict[str, tuple[dict | None, float]] = {}
_GEO_TTL = 24 * 3600


def geocode(place: str):
    key = (place or "").strip().lower()
    if not key:
        return None
    hit = _GEO_CACHE.get(key)
    if hit and time.time() - hit[1] < _GEO_TTL:
        return hit[0]

    for attempt in range(3):
        try:
            with httpx.Client(timeout=10) as c:
                r = c.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={"q": place, "format": "json", "limit": 1, "accept-language": "en", "addressdetails": 1},
                    headers=HEADERS,
                )
            r.raise_for_status()
            data = r.json()
            result = None
            if data:
                addr = data[0].get("address") or {}
                result = {"lat": float(data[0]["lat"]), "lon": float(data[0]["lon"]),
                          "cc": (addr.get("country_code") or "").upper(), "country": addr.get("country", "")}
            _GEO_CACHE[key] = (result, time.time())     # "not found" is cached too
            return result
        except Exception as e:  # noqa: BLE001
            log.warning("geocode(%s) attempt %d failed: %s", place, attempt + 1, e)
            time.sleep(1)
    return None


def _overpass(query: str):
    for url in OVERPASS_URLS:
        for _ in range(2):
            try:
                with httpx.Client(timeout=30) as c:
                    res = c.get(url, params={"data": query}, headers=HEADERS)
                if res.status_code == 200:
                    return res.json()
                if res.status_code in (429, 502, 503, 504):
                    time.sleep(2)
                    continue
                break
            except Exception as e:  # noqa: BLE001
                log.warning("overpass %s failed: %s", url, e)
                time.sleep(1)
    return None


def _coords(el: dict):
    lat = el.get("lat") or (el.get("center") or {}).get("lat")
    lon = el.get("lon") or (el.get("center") or {}).get("lon")
    return (lat, lon) if lat and lon else (None, None)


def search_attractions(city: str, limit: int = 20):
    geo = geocode(city)
    if not geo:
        return []
    lat, lon = geo["lat"], geo["lon"]
    query = f"""
    [out:json][timeout:25];
    (
      node["tourism"~"attraction|museum|viewpoint"](around:10000,{lat},{lon});
      way["tourism"~"attraction|museum|viewpoint"](around:10000,{lat},{lon});
      node["historic"~"monument|castle|fort|ruins|memorial"](around:10000,{lat},{lon});
      way["historic"~"monument|castle|fort|ruins"](around:10000,{lat},{lon});
    );
    out center {limit * 3};
    """
    data = _overpass(query)
    if not data:
        return []

    places, seen = [], set()
    for el in data.get("elements", []):
        tags = el.get("tags", {})
        name = tags.get("name:en") or tags.get("name")
        if not name or name in seen:
            continue
        lat_p, lon_p = _coords(el)
        if lat_p is None:
            continue
        seen.add(name)
        places.append({
            "id": str(el.get("id")),
            "name": name,
            "category": (tags.get("tourism") or tags.get("historic") or "attraction").replace("_", " ").title(),
            "description": (tags.get("description") or "")[:200],
            "lat": lat_p,
            "lon": lon_p,
            "image": "",
            "source": "openstreetmap",
        })
        if len(places) >= limit:
            break
    return places


def _foursquare_restaurants(geo: dict, limit: int):
    if not settings.foursquare_api_key:
        return []
    headers = {"Authorization": settings.foursquare_api_key, "Accept": "application/json"}
    params = {
        "ll": f"{geo['lat']},{geo['lon']}",
        "categories": "13065",
        "limit": limit,
        "sort": "RATING",
        "fields": "fsq_id,name,categories,location,geocodes,rating,price",
    }
    try:
        with httpx.Client(timeout=15) as c:
            r = c.get("https://api.foursquare.com/v3/places/search", headers=headers, params=params)
        if r.status_code != 200:
            log.warning("Foursquare returned %s - falling back to OpenStreetMap", r.status_code)
            return []
        out = []
        for p in r.json().get("results", []):
            main = (p.get("geocodes") or {}).get("main") or {}
            cats = p.get("categories") or []
            out.append({
                "id": p.get("fsq_id", ""),
                "name": p.get("name", ""),
                "category": cats[0].get("name", "Restaurant") if cats else "Restaurant",
                "description": (p.get("location") or {}).get("formatted_address", ""),
                "lat": main.get("latitude"),
                "lon": main.get("longitude"),
                "rating": round((p.get("rating") or 0) / 2, 1),   # Foursquare is 0-10, UI shows 0-5 stars
                "price_level": p.get("price", 0),
                "source": "foursquare",
            })
        return [r_ for r_ in out if r_["name"]]
    except Exception as e:  # noqa: BLE001
        log.warning("Foursquare error: %s", e)
        return []


def _osm_restaurants(geo: dict, limit: int):
    query = f"""
    [out:json][timeout:25];
    (
      node["amenity"~"restaurant|cafe"]["name"](around:3000,{geo['lat']},{geo['lon']});
      way["amenity"~"restaurant|cafe"]["name"](around:3000,{geo['lat']},{geo['lon']});
    );
    out center {limit * 3};
    """
    data = _overpass(query)
    if not data:
        return []
    out, seen = [], set()
    for el in data.get("elements", []):
        tags = el.get("tags", {})
        name = tags.get("name:en") or tags.get("name")
        if not name or name in seen:
            continue
        lat_p, lon_p = _coords(el)
        if lat_p is None:
            continue
        seen.add(name)
        cuisine = (tags.get("cuisine") or "").replace(";", ", ").replace("_", " ").title()
        addr = " ".join(x for x in [tags.get("addr:street"), tags.get("addr:city")] if x)
        out.append({
            "id": str(el.get("id")),
            "name": name,
            "category": cuisine or tags.get("amenity", "restaurant").title(),
            "description": addr,
            "lat": lat_p,
            "lon": lon_p,
            "rating": 0,
            "price_level": 0,
            "source": "openstreetmap",
        })
        if len(out) >= limit:
            break
    return out


def search_restaurants(city: str, limit: int = 15):
    geo = geocode(city)
    if not geo:
        return []
    return _foursquare_restaurants(geo, limit) or _osm_restaurants(geo, limit)
