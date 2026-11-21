# TravelMate AI 🌍

AI-powered travel planning for trips **anywhere in the world** (built for travellers from India, prices in ₹): day-by-day itineraries with travel costs, hotel & flight search, weather, photos, saved places and PDF export.

## Stack
- **Frontend:** React 18 + Vite + Tailwind CSS + Framer Motion + Lucide icons
- **Backend:** FastAPI + SQLAlchemy + JWT auth (SQLite by default, PostgreSQL via Docker)
- **AI:** Google Gemini (automatic model fallback) — or built-in **demo mode**
- **Data sources:** Open-Meteo (weather), OpenStreetMap Nominatim/Overpass (attractions, geocoding),
  Geoapify (hotels, optional), Foursquare (restaurants, optional)

## Quick start (manual)

```bash
# 1) Backend  (Python 3.11+)
cd backend
python -m venv venv
venv\Scripts\activate            # Windows   |  source venv/bin/activate  (macOS/Linux)
pip install -r requirements.txt
copy .env.example .env           # cp .env.example .env  (macOS/Linux)  - then edit .env
uvicorn app.main:app --reload
#   API docs: http://localhost:8000/docs      health: http://localhost:8000/api/health

# 2) Frontend (Node 18+)
cd frontend
npm install
copy .env.example .env           # cp .env.example .env
npm run dev
#   App: http://localhost:5173
```

## Docker
```bash
docker compose up --build        # frontend :5173, backend :8000, PostgreSQL :5432
```
Docker starts in demo mode by default. To use Gemini, export `GEMINI_API_KEY`, `LLM_PROVIDER=gemini`
and `FORCE_DEMO_MODE=false` before `docker compose up` (or put them in a root `.env` file).

## Configuration (`backend/.env`)

| Variable | Purpose |
|---|---|
| `GEMINI_API_KEY` | Live AI itineraries + chat. Leave empty for demo mode. |
| `LLM_MODEL` | Primary model (default `gemini-3.7-flash`); older ones are tried automatically if it is unavailable. |
| `FORCE_DEMO_MODE` | `true` = always use built-in sample itineraries/chat. |
| `JWT_SECRET_KEY` | **Set a long random string.** `python -c "import secrets; print(secrets.token_urlsafe(48))"` |
| `GEOAPIFY_API_KEY` | Live hotel listings (otherwise clearly-labelled sample hotels). |
| `PEXELS_API_KEY` | Hotel photos (free key at pexels.com/api). Without it, hotels show a photo of the area. |
| `FOURSQUARE_API_KEY` | Restaurants (otherwise OpenStreetMap is used). |
| `DATABASE_URL` | `sqlite:///./travelmate.db` (default) or a PostgreSQL URL. |

**Never commit `.env` or share it** — it holds your API keys. `.gitignore` already excludes it.

## Demo mode — what is real, what is sample
The *Settings → Data sources* page shows this live. In short:

- **AI itinerary / chat:** real Gemini when a key is set, otherwise (or if Gemini fails) a labelled **sample itinerary**.
- **Hotels:** real listings with Geoapify (price comes from the Booking.com link); otherwise labelled **sample** hotels.
- **Flights:** **sample fares only.** Amadeus shut down its Self-Service API on 17 July 2026, so live
  search is not connected. Every result links to Google Flights for real prices.
- **Weather, attractions:** live (free, no key), worldwide.
- **Destinations:** 73 curated places (24 in India, 49 across Asia, Middle East, Europe, Africa, Americas, Oceania); any other city can be typed into the planner.
- **Costs abroad:** local transport and activity costs are scaled by a per-country price level (`backend/app/utils/pricing.py`), so a cab in Paris is not priced like an auto in Jaipur. Too-far trips switch to a flight estimate automatically. Non-India trips get a visa/passport reminder.
- **Photos:** places and destinations use Wikipedia/Wikimedia photos (free, no key; credit shown on hover). Hotels use Pexels if a key is set.
- **Hotel cost:** nights x rooms x a per-night estimate (tier, stay type, group size, country price level) - an estimate; every trip links to Booking.com for the live price.
- **Trip cost summary:** flights/travel + hotel + local transport + food + sightseeing + shopping vs your budget, plus AI suggestions (general tips in demo mode).
- **Travel costs:** local hops (walk/auto/cab/metro/bus) and home-city → destination round trip are **estimates** based on typical Indian fares, and are included in the trip budget under *Transit*.

## Project layout
```
backend/app   main.py · auth.py · routes/ · services/ · utils/ · models.py · schemas.py
frontend/src  pages/ · components/ · context/ · api/ · utils/
```
See `CHANGES.md` for everything that was fixed in this version.
