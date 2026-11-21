"""Photos for destinations, attractions and hotels.

Sources (no key needed for the first):
  1. Wikipedia / Wikimedia Commons - main photo of the best-matching article (CC-licensed)
  2. Pexels - only for hotels, only when PEXELS_API_KEY is set (free key)
Results are cached in memory. A photo is only returned when the article title really
matches what was asked for, so a "Hawa Mahal" card never shows an unrelated picture.
"""
import logging
import re
import time
import zlib

import httpx

from app.config import settings

log = logging.getLogger("travelmate.images")

HEADERS = {"User-Agent": "TravelMateAI/1.1 (student project; image lookup)"}
WIKI_API = "https://en.wikipedia.org/w/api.php"

_CACHE: dict[str, tuple[dict, float]] = {}
_TTL_HIT = 7 * 24 * 3600
_TTL_MISS = 3600

# words that do not identify a place on their own
_STOP = {
    "the", "and", "of", "in", "at", "to", "for", "with", "a", "an", "old", "new", "city", "town",
    "visit", "tour", "walk", "trip", "local", "morning", "evening", "sunset", "sunrise", "view",
    "viewpoint", "hotel", "resort", "inn", "stay", "guest", "house", "palace", "fort", "temple",
    "museum", "market", "park", "lake", "garden", "gardens", "road", "street", "india", "indian",
}
_BAD_IMAGE = re.compile(r"(flag_of|coat_of_arms|locator|location_map|_map[_.]|seal_of|logo|emblem|\.svg)", re.I)


def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", (text or "").lower()) if len(t) >= 3}


def _relevant(title: str, query: str, exclude: str = "") -> bool:
    """The article title must share a distinctive word with the query."""
    wanted = _tokens(query) - _tokens(exclude) - _STOP
    if not wanted:                       # query only had generic words -> use plain overlap
        wanted = _tokens(query) - _tokens(exclude)
    return bool(wanted & _tokens(title))


def _wiki_image(query: str, exclude: str = "") -> dict | None:
    params = {
        "action": "query", "generator": "search", "gsrsearch": query, "gsrlimit": 4,
        "prop": "pageimages", "piprop": "thumbnail", "pithumbsize": 900, "pilimit": 4,
        "redirects": 1, "format": "json",
    }
    with httpx.Client(timeout=8, headers=HEADERS) as c:
        r = c.get(WIKI_API, params=params)
        r.raise_for_status()
        pages = (r.json().get("query") or {}).get("pages") or {}
    for page in sorted(pages.values(), key=lambda p: p.get("index", 99)):
        url = (page.get("thumbnail") or {}).get("source")
        if url and not _BAD_IMAGE.search(url) and _relevant(page.get("title", ""), query, exclude):
            return {"url": url, "source": "wikipedia", "credit": f"Wikipedia: {page.get('title')}", "generic": False}
    return None


def _pexels_image(query: str, pick: str) -> dict | None:
    if not settings.pexels_api_key:
        return None
    with httpx.Client(timeout=8, headers={"Authorization": settings.pexels_api_key, **HEADERS}) as c:
        r = c.get("https://api.pexels.com/v1/search",
                  params={"query": query, "per_page": 15, "orientation": "landscape"})
        r.raise_for_status()
        photos = r.json().get("photos") or []
    if not photos:
        return None
    ph = photos[zlib.crc32(pick.encode()) % len(photos)]     # different hotels -> different photos
    return {"url": (ph.get("src") or {}).get("large"), "source": "pexels",
            "credit": f"Photo: {ph.get('photographer', 'Pexels')} / Pexels", "generic": True}


def _lookup(q: str, kind: str, exclude: str, city: str) -> dict | None:
    if kind == "hotel":
        found = _wiki_image(f"{q} {city}".strip(), exclude=city)       # real hotel with its own article
        if not found:
            found = _pexels_image(f"hotel room {city}".strip(), q)
        if not found and city:
            found = _wiki_image(city)
            if found:
                found["generic"] = True                                  # city photo, not this hotel
        return found
    return _wiki_image(q, exclude=exclude)


def find_image(q: str, kind: str = "place", exclude: str = "", city: str = "") -> dict:
    q, city = (q or "").strip(), (city or "").strip()
    key = f"{kind}|{q.lower()}|{exclude.lower()}|{city.lower()}"
    hit = _CACHE.get(key)
    if hit and time.time() - hit[1] < (_TTL_HIT if hit[0].get("url") else _TTL_MISS):
        return hit[0]
    try:
        result = _lookup(q, kind, exclude, city)
    except Exception as e:  # noqa: BLE001
        log.warning("image lookup failed for %r: %s", q, type(e).__name__)
        return {"url": None, "source": None, "credit": "", "generic": False}   # not cached: may be a blip
    result = result or {"url": None, "source": None, "credit": "", "generic": False}
    _CACHE[key] = (result, time.time())
    return result
