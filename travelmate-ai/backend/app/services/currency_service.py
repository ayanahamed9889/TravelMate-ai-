"""Currency conversion via open.er-api.com (free, no key). Not used by the UI yet."""
import logging
import time

import httpx

log = logging.getLogger("travelmate.currency")

_CACHE: dict[str, tuple[float, float]] = {}      # currency -> (rate_to_inr, fetched_at)
_TTL = 6 * 3600
_STATIC = {"USD": 85.0, "EUR": 92.0, "GBP": 108.0, "AED": 23.1}   # offline fallback only


def get_rate_to_inr(from_currency: str) -> float:
    c = (from_currency or "INR").upper()
    if c == "INR":
        return 1.0
    hit = _CACHE.get(c)
    if hit and time.time() - hit[1] < _TTL:
        return hit[0]
    try:
        with httpx.Client(timeout=10) as client:
            r = client.get(f"https://open.er-api.com/v6/latest/{c}")
            r.raise_for_status()
            rate = r.json().get("rates", {}).get("INR")
        if rate:
            _CACHE[c] = (float(rate), time.time())
            return float(rate)
    except Exception as e:  # noqa: BLE001
        log.warning("rate lookup failed for %s: %s", c, e)
    if c in _STATIC:                      # failures are never cached
        return _STATIC[c]
    raise ValueError(f"No exchange rate available for {c}")


def to_inr(amount: float, currency: str = "INR") -> float:
    return round(amount * get_rate_to_inr(currency), 2)
