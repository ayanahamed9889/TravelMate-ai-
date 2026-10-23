"""Built-in sample data used when AI demo mode is on (no Gemini key / FORCE_DEMO_MODE)
or when the live AI call fails. Everything here is clearly labelled as sample data.
"""
import re
from app.services.itinerary_utils import make_travel
from app.utils.helpers import date_plus

TIER_MULTIPLIER = {"budget": 0.7, "moderate": 1.0, "luxury": 1.9}
DEMO_NOTE = "Sample itinerary - add a Gemini API key in backend/.env for AI-personalised plans."

# (name, description, category, start_time, duration_min, base cost per person in INR)
_DAY_TEMPLATES = [
    ("Arrival & old town", [
        ("Check-in & freshen up", "Settle into your stay and plan the evening.", "Stay", "11:00", 60, 0),
        ("Local lunch", "Try a well-reviewed local speciality.", "Food", "13:00", 60, 350),
        ("Old town walk", "Wander the oldest lanes, bazaars and landmarks.", "Culture", "16:00", 120, 100),
        ("Dinner at a local favourite", "Regional dishes in a casual setting.", "Food", "19:30", 90, 500),
    ]),
    ("Landmarks & history", [
        ("Breakfast at the hotel or a cafe", "Start early before the crowds.", "Food", "08:00", 45, 250),
        ("Main landmark / museum", "The highlight sight of the destination.", "History", "09:30", 150, 400),
        ("Lunch break", "Rest and eat near the sights.", "Food", "13:00", 60, 350),
        ("Second monument or gallery", "Pick something lighter for the afternoon.", "History", "15:00", 120, 250),
        ("Sunset viewpoint", "Best light of the day; carry a jacket in winter.", "Nature", "17:45", 75, 0),
    ]),
    ("Markets & food trail", [
        ("Morning market visit", "Local produce, crafts and street snacks.", "Shopping", "09:00", 120, 600),
        ("Street-food trail", "Taste 4-5 local snacks on foot.", "Food", "12:30", 90, 400),
        ("Craft workshop or cooking class", "A hands-on local experience.", "Experience", "15:00", 120, 1200),
        ("Evening cultural show", "Folk music, dance or a local cultural show.", "Culture", "19:00", 90, 500),
    ]),
    ("Nature & relaxation", [
        ("Sunrise outing", "Garden, lake or waterfront before the crowds arrive.", "Nature", "06:30", 90, 0),
        ("Slow breakfast", "Take it easy.", "Food", "08:30", 60, 300),
        ("Day excursion nearby", "A half-day trip to a nearby sight or village.", "Experience", "10:30", 240, 1500),
        ("Spa or leisure time", "Rest your legs before dinner.", "Relaxation", "16:30", 90, 1000),
        ("Farewell dinner", "End the day with a good meal.", "Food", "19:30", 90, 700),
    ]),
]
_LAST_DAY = ("Last-minute shopping & departure", [
    ("Breakfast & packing", "Keep a buffer for check-out.", "Food", "08:30", 60, 250),
    ("Souvenir shopping", "Local crafts, food products or textiles.", "Shopping", "10:30", 90, 800),
    ("Check-out & transfer", "Leave early for your train or flight.", "Transit", "13:00", 90, 600),
])


def get_demo_itinerary(destination: str, days: int, *, start_date: str | None = None,
                       travelers: int = 1, budget_tier: str = "moderate",
                       note: str = DEMO_NOTE, price_index: float = 1.0, international: bool = False) -> dict:
    tier = (budget_tier or "moderate").strip().lower()
    mult = TIER_MULTIPLIER.get(tier, 1.0)
    people = max(1, int(travelers or 1))
    days = max(1, int(days or 1))

    # typical hop lengths inside a city (km); the first hop is stay -> first stop
    hops = [3.0, 4.5, 2.0, 6.0, 3.5, 7.0, 2.5, 5.0]
    out_days = []
    for i in range(days):
        theme, acts = (_LAST_DAY if (i == days - 1 and days > 1) else _DAY_TEMPLATES[i % len(_DAY_TEMPLATES)])
        out_days.append({
            "day_number": i + 1,
            "date": date_plus(start_date, i),
            "theme": f"{theme} - {destination}",
            "activities": [{
                "name": name,
                "description": desc,
                "location": destination,
                "category": cat,
                "slot": "morning" if int(t[:2]) < 12 else "afternoon" if int(t[:2]) < 17 else "evening",
                "start_time": t,
                "duration_minutes": mins,
                "estimated_cost_inr": round(base * mult * people * price_index / 10) * 10,
                "notes": "",
                "travel": make_travel(hops[(i + k) % len(hops)], None, people, tier,
                                      note="Sample estimate", price_index=price_index),
            } for k, (name, desc, cat, t, mins, base) in enumerate(acts)],
        })
    warnings = [note]
    if international:
        warnings.append("International trip: check passport validity, visa rules for your passport and travel insurance.")
    return {
        "trip_title": f"{days}-day trip to {destination}",
        "destination": destination,
        "duration_days": days,
        "currency": "INR",
        "days": out_days,
        "assumptions": [
            f"Costs are rough INR estimates for {people} traveller{'s' if people > 1 else ''} "
            f"on a {tier} budget.",
            "Local travel between stops is a rough estimate (taxi / public transport); stay is not included.",
        ],
        "warnings": warnings,
        "source": "demo",
    }


_CHAT_RULES = [
    (("hotel", "stay", "hostel", "resort"),
     "Use the Hotels page to search any city in the world - results link to Booking.com for live prices. "
     "For a first visit, pick a stay near the old town or a well-connected metro/train station."),
    (("flight", "fly", "airport", "train", "visa"),
     "Compare flight prices across a few dates and book 6-10 weeks ahead for international trips. "
     "For many countries you need a visa or e-visa on an Indian passport - check the embassy site before booking."),
    (("budget", "cost", "expensive", "cheap", "price"),
     "Rough daily spend per person: South/South-East Asia Rs 3,000-6,000, Middle East Rs 8,000-12,000, "
     "Europe Rs 10,000-16,000, USA/Australia Rs 15,000+. Open a trip's Budget card for your itinerary estimate."),
    (("weather", "season", "best time", "when"),
     "Pick the dry or shoulder season: Europe May-June/Sept-Oct, South-East Asia Nov-Feb, Middle East Nov-Mar, "
     "Southern hemisphere Dec-Mar. Each destination card on Explore shows its best months."),
    (("food", "eat", "restaurant", "dish"),
     "Ask locals for their favourite spot, try one street-food or market trail, and eat where the queue is "
     "mostly locals. Vegetarian? Search '<country> vegetarian food' before you go."),
    (("itinerary", "plan", "days", "trip"),
     "Tell me the destination, dates, number of travellers and budget, and use AI Trip Planner to generate "
     "a day-by-day plan with travel costs that you can export as PDF."),
]


def get_demo_chat_reply(message: str) -> str:
    text = (message or "").lower()
    for keys, reply in _CHAT_RULES:
        if any(re.search(rf"\b{k}", text) for k in keys):
            return f"{reply}\n\n(Demo mode - add a Gemini API key for personalised answers.)"
    return ("I'm TravelMate AI running in demo mode, so my answers are generic. "
            "Ask me about hotels, flights, budget, weather or food - or use the AI Trip Planner.\n\n"
            "(Add a Gemini API key in backend/.env for personalised answers.)")
