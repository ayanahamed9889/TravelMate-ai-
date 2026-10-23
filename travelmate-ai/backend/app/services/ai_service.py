"""Itinerary + chat via Gemini (google-genai SDK) with model fallbacks and a demo mode.

Demo mode (no API key / FORCE_DEMO_MODE=true / LLM_PROVIDER=mock) returns clearly
labelled sample data, so the whole app stays usable without any key.
"""
import json
import logging
import time

from app.config import settings
from app.services.itinerary_utils import normalize_itinerary
from app.services.travel_service import getting_there, resolve_place
from app.utils.demo_data import get_demo_chat_reply, get_demo_itinerary
from app.utils.helpers import days_between

log = logging.getLogger("travelmate.ai")

MAX_AI_DAYS = 14   # keeps the JSON answer small enough to be reliable

try:
    from google import genai
except ImportError:  # app still runs in demo mode
    genai = None

client = None
if genai and settings.gemini_api_key and not settings.demo_mode:
    try:
        kwargs = {"api_key": settings.gemini_api_key,
                  "http_options": {"timeout": settings.llm_timeout_seconds * 1000}}
        # Google Cloud / Vertex AI express-mode keys start with "AQ." and must use the Vertex endpoint;
        # normal Google AI Studio keys start with "AIza".
        if settings.gemini_api_key.startswith("AQ."):
            kwargs["vertexai"] = True
        client = genai.Client(**kwargs)
        log.info("Gemini client ready (%s) | primary model: %s",
                 "vertex" if kwargs.get("vertexai") else "ai-studio", settings.llm_model)
    except Exception as e:  # noqa: BLE001
        log.error("Gemini client init failed: %s", e)

# Tried in order; unknown models (404) are skipped automatically.
FALLBACK_MODELS = list(dict.fromkeys([
    settings.llm_model,
    "gemini-3.7-flash",
    "gemini-3.5-flash",
    "gemini-2.5-flash",
    "gemini-flash-latest",
]))


def is_demo() -> bool:
    return client is None


last_model_used = ""


def _clean_error(err) -> str:
    """Short, key-free reason that is safe to show in the UI."""
    text = " ".join(str(err).split())
    if settings.gemini_api_key:
        text = text.replace(settings.gemini_api_key, "***")
    return text[:240]


SYSTEM_PROMPT = """You are TravelMate AI, an expert travel planner for travellers from India who may go ANYWHERE in the world.

Return ONLY valid JSON (no markdown, no code fences) in exactly this shape:

{
  "trip_title": "string",
  "destination": "string",
  "duration_days": 3,
  "currency": "INR",
  "days": [{
    "day_number": 1,
    "date": "YYYY-MM-DD",
    "theme": "string",
    "activities": [{
      "name": "string",
      "description": "string",
      "location": "string",
      "category": "Food|Culture|History|Nature|Adventure|Shopping|Relaxation|Transit|Stay|Experience",
      "slot": "morning|afternoon|evening",
      "start_time": "HH:MM",
      "duration_minutes": 90,
      "estimated_cost_inr": 500,
      "notes": "string",
      "travel": {
        "mode": "Walk|Auto|Cab|Metro|Bus|Train|Ferry (Cab = taxi / Uber; Metro = metro, tram, subway)",
        "distance_km": 4.5,
        "duration_minutes": 20,
        "cost_inr": 180
      }
    }]
  }],
  "assumptions": ["string"],
  "warnings": ["string"]
}

RULES:
- ALL costs are plain integers in INR for the WHOLE group (not per person)
- "travel" = how the group gets TO that activity from the previous one (for the first activity of a day: from the hotel).
  Give a realistic mode, distance_km, duration_minutes and cost_inr for the whole group (e.g. 2 autos for 5 people)
  using typical LOCAL fares of that city converted to INR (e.g. India: auto ~Rs 20-25/km; Europe/USA/Japan taxis cost
  5-10x more; use the city's real metro/tram/bus where it exists); Walk costs 0
- Use well-known, real places of the destination city/country and local food; convert all prices to INR at current approximate rates
- If the destination is outside India, add a warning about visa/passport requirements for an Indian passport holder
- Create exactly the requested number of days
- 3-5 activities per day, in time order, no overlaps, realistic travel time between them
- Respect the budget tier and the traveller preferences
- Put real, well-known places only; use "warnings" for seasonal or safety notes
- ONLY JSON
"""


def _build_prompt(trip, num_days: int, place=None) -> str:
    prefs = ", ".join(trip.preferences or []) or "general sightseeing"
    country = (place or {}).get("country") or "unknown"
    return f"""Plan a trip with these details:
Destination: {trip.destination} (country: {country})
Travelling from: {trip.departure or 'not specified'}
Dates: {trip.start_date or 'flexible'} to {trip.end_date or 'flexible'}
Number of days: {num_days}
Travellers: {trip.travelers} ({trip.trip_type})
Preferences: {prefs}
Accommodation: {trip.accommodation}
Main transport: {trip.transport}
Total budget: INR {int(trip.budget or 0)} ({trip.budget_tier} tier)

Return the JSON itinerary with exactly {num_days} days and INR costs only."""


def _extract_json(text: str) -> dict:
    text = (text or "").strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.rsplit("```", 1)[0]
    start, end = text.find("{"), text.rfind("}")
    if start >= 0 and end > start:
        text = text[start:end + 1]
    return json.loads(text)


def _is_fatal(err: str) -> bool:
    """Errors that will not go away by trying another model."""
    e = err.upper()
    return any(k in e for k in ("API_KEY_INVALID", "UNAUTHENTICATED", "PERMISSION_DENIED", "API KEY NOT VALID"))


def _generate_text(contents, *, system: str, json_mode: bool, temperature: float = 0.7) -> str:
    config = {"temperature": temperature, "system_instruction": system}
    if json_mode:
        config["response_mime_type"] = "application/json"

    last_error = "unknown"
    for model_name in FALLBACK_MODELS:
        for attempt in range(2):
            try:
                log.info("Trying %s (attempt %d)", model_name, attempt + 1)
                response = client.models.generate_content(
                    model=model_name, contents=contents, config=config)
                text = (response.text or "").strip()
                if not text:
                    raise RuntimeError("empty response")
                global last_model_used
                last_model_used = model_name
                return text
            except Exception as e:  # noqa: BLE001
                last_error = str(e)
                log.warning("%s failed: %s", model_name, _clean_error(last_error)[:160])
                if _is_fatal(last_error):
                    raise RuntimeError("Gemini API key is invalid or has no access") from e
                if "503" in last_error or "UNAVAILABLE" in last_error:
                    if attempt == 0:
                        time.sleep(2)
                        continue
                break  # 404 / 429 / other -> next model
    raise RuntimeError(f"All Gemini models failed. Last error: {last_error[:200]}")


def _with_getting_there(data: dict, trip, place=None) -> dict:
    try:
        data["getting_there"] = getting_there(trip.departure, trip.destination, trip.transport, trip.travelers,
                                              (place or {}).get("index", 1.0))
    except Exception as e:  # noqa: BLE001
        log.warning("getting_there skipped: %s", e)
        data["getting_there"] = None
    return data


def generate_itinerary(trip) -> dict:
    place = _safe_place(trip.destination)
    data = _generate_itinerary(trip, place)
    return _with_getting_there(data, trip, place)


def _safe_place(destination: str) -> dict:
    try:
        return resolve_place(destination)
    except Exception as e:  # noqa: BLE001
        log.warning("resolve_place failed: %s", e)
        return {"country": "", "cc": "", "index": 3.0}


def _generate_itinerary(trip, place=None) -> dict:
    """Always returns a valid itinerary dict (AI, or a labelled sample if AI is unavailable)."""
    total_days = days_between(trip.start_date, trip.end_date)
    num_days = min(total_days, MAX_AI_DAYS)
    extra_warning = (f"Itinerary covers the first {MAX_AI_DAYS} of {total_days} days."
                     if total_days > MAX_AI_DAYS else None)

    place = place or {"country": "", "cc": "IN", "index": 1.0}
    index = place.get("index", 1.0)
    international = bool(place.get("cc")) and place.get("cc") != "IN"

    def demo(note=None):
        data = get_demo_itinerary(
            trip.destination, num_days, start_date=trip.start_date,
            travelers=trip.travelers, budget_tier=trip.budget_tier,
            price_index=index, international=international,
            **({"note": note} if note else {}),
        )
        if extra_warning:
            data["warnings"].append(extra_warning)
        return data

    if client is None:
        return demo()

    try:
        raw = _generate_text(_build_prompt(trip, num_days, place), system=SYSTEM_PROMPT, json_mode=True)
        data = normalize_itinerary(_extract_json(raw), destination=trip.destination,
                                   start_date=trip.start_date, num_days=num_days,
                                   travelers=trip.travelers, tier=trip.budget_tier,
                                   price_index=index)
        if not data["days"] or not any(d["activities"] for d in data["days"]):
            raise ValueError("AI returned an empty itinerary")
    except Exception as e:  # noqa: BLE001
        reason = _clean_error(e)
        log.error("Live itinerary failed, using sample data: %s", reason)
        data = demo("The AI service was unavailable, so this is a sample itinerary. "
                    "Use Re-Optimize to try again.")
        data["ai_error"] = reason
        return data

    data["source"] = "ai"
    if extra_warning:
        data["warnings"].append(extra_warning)
    return data


CHAT_SYSTEM = (
    "You are TravelMate AI, a helpful travel assistant for travellers from India going anywhere in the world. "
    "Quote prices in INR (Rs). Mention visa/entry rules for Indian passport holders when relevant. Be concise and practical. Never invent live prices, "
    "opening hours or availability - say they should be checked."
)


def chat_reply(message: str, history=None, trip_context=None) -> tuple[str, bool]:
    """Returns (reply_text, is_demo)."""
    if client is None:
        return get_demo_chat_reply(message), True

    contents = []
    for m in (history or [])[-10:]:
        if not isinstance(m, dict):
            continue
        text = str(m.get("content", "")).strip()
        if not text:
            continue
        role = "user" if m.get("role") == "user" else "model"
        contents.append({"role": role, "parts": [{"text": text[:2000]}]})

    context = ""
    if trip_context:
        context = f"\n\n[Trip context: {json.dumps(trip_context, default=str)[:1000]}]"
    contents.append({"role": "user", "parts": [{"text": message + context}]})

    # Gemini needs the first turn to be from the user
    while contents and contents[0]["role"] != "user":
        contents.pop(0)

    try:
        return _generate_text(contents, system=CHAT_SYSTEM, json_mode=False), False
    except Exception as e:  # noqa: BLE001
        reason = _clean_error(e)
        log.error("Live chat failed, using demo reply: %s", reason)
        return f"{get_demo_chat_reply(message)}\n\n⚠ Live AI failed: {reason}", True


def diagnose() -> dict:
    """Tiny live call used by /api/health/ai so the real error is visible."""
    if client is None:
        why = ("No Gemini API key configured" if not settings.gemini_api_key
               else "Demo mode is forced (FORCE_DEMO_MODE / LLM_PROVIDER=mock) or google-genai is not installed")
        return {"ok": False, "error": why, "models_tried": []}
    try:
        reply = _generate_text("Reply with the single word OK.", system="Connection test.",
                               json_mode=False, temperature=0)
        return {"ok": True, "model": last_model_used, "reply": reply[:40],
                "key_type": "vertex" if settings.gemini_api_key.startswith("AQ.") else "ai-studio"}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": _clean_error(e), "models_tried": FALLBACK_MODELS,
                "key_type": "vertex" if settings.gemini_api_key.startswith("AQ.") else "ai-studio"}