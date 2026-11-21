import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401  (registers tables on Base)
from app.auth import router as auth_router
from app.config import settings
from app.database import Base, engine
from app.services import ai_service
from app.routes import assistant, budget, flights, hotels, images, places, trips, weather

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
)
log = logging.getLogger("travelmate")

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if settings.jwt_secret_key in ("change-me", "super-secret-change-me", ""):
        log.warning("JWT_SECRET_KEY is still the default value - set a long random string in .env")
    if settings.demo_mode:
        log.info("AI demo mode is ON (sample itineraries / chat answers). "
                 "Set GEMINI_API_KEY and FORCE_DEMO_MODE=false for live AI.")
    else:
        log.info("Gemini enabled | primary model: %s", settings.llm_model)
    yield


app = FastAPI(title="TravelMate AI API", version="1.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API = "/api"
app.include_router(auth_router, prefix=API)
app.include_router(trips.router, prefix=API)
app.include_router(places.router, prefix=API)
app.include_router(budget.router, prefix=API)
app.include_router(assistant.router, prefix=API)
app.include_router(weather.router, prefix=API)
app.include_router(hotels.router, prefix=API)
app.include_router(flights.router, prefix=API)
app.include_router(images.router, prefix=API)


@app.get("/api/health/ai")
def health_ai():
    """Makes one tiny Gemini call and returns the real error if it fails."""
    return ai_service.diagnose()


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "currency": "INR",
        "demo_mode": settings.demo_mode,          # AI itinerary + chat
        "gemini": bool(settings.gemini_api_key) and not settings.demo_mode,
        "geoapify": bool(settings.geoapify_api_key),   # live hotels
        "foursquare": bool(settings.foursquare_api_key),
        "pexels": bool(settings.pexels_api_key),
        "flights": "sample",   # Amadeus Self-Service was shut down on 17 Jul 2026
    }
