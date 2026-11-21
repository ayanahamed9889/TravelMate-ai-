# What was fixed

## Critical (app did not work)
- **Frontend ↔ backend mismatch.** The UI called endpoints that did not exist (`/trips/stats`, `/places/recommended`,
  `/places`, `/places/saved`, `/places/hotels`, `/places/flights`, `/budget/overview`, `PUT /auth/me`,
  `POST /trips/generate`, `/weather`). Added/aligned all of them; Dashboard, Explore, Saved, Budget, Settings,
  Hotels and Flights now work end to end.
- **Invalid AI model** `gemini-3.8-flash` (does not exist) → `gemini-3.7-flash` + automatic fallbacks. Retired
  `gemini-1.5-flash` removed from the example env.
- **No demo mode** although README promised it (`demo_data.py` was never used, `FORCE_DEMO_MODE` ignored). Implemented.
  Without a key (or if Gemini fails) you now get a clearly-labelled sample itinerary instead of a 503.
- **Wrong password reloaded the page** and swallowed the error (axios 401 interceptor). Fixed.
- **422 validation errors crashed React** (`detail` is an array). New `getErrorMessage()` helper everywhere.
- **TripDetail rendered a second Sidebar + Navbar** inside the app layout and used non-existent Tailwind tokens
  (`bg-canvas`, `shadow-float`, `text-tertiary`). Rebuilt; MapView props now match.
- **Trip page was blank when no itinerary existed**; now offers *Generate*. Added PDF download button.
- **Flights:** Amadeus Self-Service is shut down (17 Jul 2026) → labelled sample fares + Google Flights links.
- **Hotels:** `source.unsplash.com` is discontinued (all images were broken) → cover placeholders; price ₹0 → "Price on Booking.com".
- **docker-compose** referenced a missing `frontend/Dockerfile` and PostgreSQL without a driver → both added.
- **`.env.example` contained a real-looking Gemini key** → removed. `frontend/.env.example` used the wrong variable name.

## Backend
- Input validation (dates, travellers, budget, password ≤ 72 bytes, trip ≤ 60 days); case-insensitive email login.
- `GET /trips?status=active|past|drafts|all`, `/trips/stats`, expense delete.
- AI output normalised (strings → numbers, legacy `estimated_cost` → `estimated_cost_inr`, dates filled, days trimmed).
- Budget now uses the itinerary estimate (it was always ₹0 before) and tracks logged expenses separately.
- PDF: ₹ symbol rendered as a black box and `&`/`<` in AI text could break it → fixed; Indian digit grouping.
- Foursquare rating scale, OSM fallback for restaurants, cached geocoding (Nominatim rate limit), weather icons,
  currency API replaced (exchangerate.host now needs a key), SQLite foreign keys on, no raw exception text leaked to users.

## Frontend / design
- One palette everywhere (Royal Indigo `#1e1b4b` + Saffron `#f97316`); removed the leftover blue/teal colours.
- Fully responsive (mobile sidebar drawer), shared `.field`/`.btn-*` styles, accessible labels and focus rings.
- Removed hard-coded "Arjun", fake bell/⌘K/currency buttons, random avatar service, USD budget tiers, dead files.
- Wizard validates each step, can't create duplicate drafts, sends the right fields; Explore saves places;
  trips can be deleted; Assistant can chat about a chosen trip and remembers conversation history.

# Update 2 - photos, bolder itinerary, travel costs
- **Photos** for destinations, attractions, activities, trip hero and hotels (`/api/images`, Wikipedia + optional Pexels key).
  A photo is only shown when the article really matches the place; otherwise a gradient is used.
- **Itinerary redesign:** bold activity titles/details, time + cost pills, big day headers with day totals, photo per landmark.
- **Travel cost between places:** every stop shows mode (walk/auto/cab/metro/bus), km, minutes and group cost.
  **Getting there:** home city → destination round trip (flight/train/bus/car) estimate.
  Both are added to the trip budget (Transit), budget page and PDF. Existing trips need *AI Re-Optimize* once to get them.

# Update 3 - whole world
- 73 destinations (24 India + 49 worldwide) in 7 regions; search by country, vibe or city on Explore.
- Per-country price levels for local transport / activities; world airports (97) with realistic distance, duration and fares.
- AI prompt is no longer India-specific (local fares converted to INR, real local transport, visa reminder for Indian passport).
- Home -> destination: land modes switch to flight when too far; long-haul fares priced per distance.
- Photos for any place via Wikipedia (Explore, Dashboard, trips, activities).

# Update 4 - full trip costs + AI suggestions + bug fixes
## New: every trip now shows the complete cost
- **Trip cost summary card** (top of the trip page): flights / getting there, hotel, local transport, food, sightseeing,
  shopping -> total, 10% safety buffer, per person, per day, and "within / tight / over budget" with advice
  (e.g. "a budget homestay would save about Rs. 20,000").
- **Hotel / stay cost** (`services/trip_costs.py`): nights x rooms x price per night, scaled by budget tier, stay type
  (Hotel / Resort / Hostel / Homestay), group size and the destination's price level. Three stay levels to compare,
  a Booking.com link, and AI hotel ideas when Gemini is connected. Counted once in the budget (a "Stay" activity is never added on top).
- **Flights / getting there**: round-trip cost for the whole group, per person and one-way per person
  (flights); the "From" city is now required in the planner so this is never empty.
- **Cost of every place**: each stop shows its cost (and per person); each day shows activities + local travel + hotel tonight.
- **AI suggestions panel**: best areas to stay, hotel ideas, money-saving tips, food, getting around, safety, packing,
  hidden gems, best time, visa note. Without a Gemini key you get clearly-labelled general tips instead.
- Hotels search: guests + rooms, and every listing shows an estimated price per night / total (live listings had no price).
- Budget page and PDF use the same numbers; PDF has the cost summary, stay, flights and suggestions.
- Old trips get the hotel estimate, suggestions and summary automatically (no Re-Optimize needed; flights need one Re-Optimize).

## Bugs fixed in this round
- Demo itineraries abroad used auto-rickshaws (Paris, Tokyo...) -> metro/cab outside India and nearby countries.
- Sample hotel prices were the same everywhere (Paris = Jaipur) -> scaled by country price level.
- Assistant chat returned 422 after ~20 messages (history limit) -> only the last 20 messages are sent.
- Places with latitude/longitude 0 were dropped by the OpenStreetMap parser.
- Budget "Stays" was always Rs. 0 (nothing priced the hotel); "Flights" are now their own "Getting there" bucket.
- PDF showed a long-haul distance as "6600.0 km".

