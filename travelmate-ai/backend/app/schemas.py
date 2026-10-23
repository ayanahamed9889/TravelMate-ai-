from datetime import date
from typing import Any, List, Optional

from pydantic import (
    BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator,
)

MAX_TRIP_DAYS = 60


# ---------- AUTH ----------
class RegisterRequest(BaseModel):
    email: EmailStr
    # bcrypt only looks at the first 72 bytes, so cap it explicitly
    password: str = Field(min_length=6, max_length=72)
    name: Optional[str] = Field(default=None, max_length=120)

    @field_validator("name")
    @classmethod
    def _clean_name(cls, v):
        v = (v or "").strip()
        return v or None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(max_length=72)


class UserUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=120)

    @field_validator("name")
    @classmethod
    def _clean_name(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty")
        return v


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    name: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- TRIPS ----------
def _check_iso_date(v: Optional[str]) -> Optional[str]:
    if v in (None, ""):
        return None
    try:
        return date.fromisoformat(v).isoformat()
    except ValueError:
        raise ValueError("Dates must be in YYYY-MM-DD format")


class TripCreate(BaseModel):
    destination: str = Field(min_length=2, max_length=255)
    departure: Optional[str] = Field(default=None, max_length=255)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    travelers: int = Field(default=1, ge=1, le=50)
    trip_type: str = Field(default="Solo", max_length=40)
    preferences: List[str] = Field(default_factory=list, max_length=20)
    accommodation: str = Field(default="Hotel", max_length=40)
    transport: str = Field(default="Flight", max_length=40)
    budget: float = Field(default=0, ge=0, le=1e9)
    currency: str = Field(default="INR", max_length=10)
    budget_tier: str = Field(default="moderate", max_length=20)

    @field_validator("destination", "departure")
    @classmethod
    def _strip(cls, v):
        return v.strip() if isinstance(v, str) else v

    @field_validator("start_date", "end_date")
    @classmethod
    def _dates(cls, v):
        return _check_iso_date(v)

    @model_validator(mode="after")
    def _date_order(self):
        if self.start_date and self.end_date:
            s, e = date.fromisoformat(self.start_date), date.fromisoformat(self.end_date)
            if e < s:
                raise ValueError("End date cannot be before the start date")
            if (e - s).days + 1 > MAX_TRIP_DAYS:
                raise ValueError(f"Trips can be at most {MAX_TRIP_DAYS} days long")
        return self


class TripUpdate(BaseModel):
    destination: Optional[str] = Field(default=None, min_length=2, max_length=255)
    departure: Optional[str] = Field(default=None, max_length=255)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    travelers: Optional[int] = Field(default=None, ge=1, le=50)
    trip_type: Optional[str] = Field(default=None, max_length=40)
    preferences: Optional[List[str]] = Field(default=None, max_length=20)
    accommodation: Optional[str] = Field(default=None, max_length=40)
    transport: Optional[str] = Field(default=None, max_length=40)
    budget: Optional[float] = Field(default=None, ge=0, le=1e9)
    currency: Optional[str] = Field(default=None, max_length=10)
    budget_tier: Optional[str] = Field(default=None, max_length=20)

    @field_validator("start_date", "end_date")
    @classmethod
    def _dates(cls, v):
        return _check_iso_date(v)


class TripOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    destination: str
    departure: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    travelers: int = 1
    trip_type: str = "Solo"
    preferences: List[str] = Field(default_factory=list)
    accommodation: Optional[str] = "Hotel"
    transport: Optional[str] = "Flight"
    budget: float = 0
    currency: str = "INR"
    budget_tier: str = "moderate"
    status: str = "draft"
    cover_image: Optional[str] = None

    @field_validator("preferences", mode="before")
    @classmethod
    def _none_to_list(cls, v):
        return v or []

    @field_validator("budget", "travelers", mode="before")
    @classmethod
    def _none_to_zero(cls, v):
        return 0 if v is None else v


class TripListOut(BaseModel):
    items: List[TripOut]
    total: int


class TripStatsOut(BaseModel):
    upcoming: int = 0
    destinations: int = 0
    saved: int = 0
    total_budget: float = 0


# ---------- ITINERARY ----------
class TravelOut(BaseModel):
    """How to get TO this stop from the previous one (first stop: from your stay)."""
    mode: str = "Cab"
    distance_km: float = 0
    duration_minutes: int = 0
    cost_inr: float = 0          # whole group
    note: Optional[str] = ""


class GettingThereOut(BaseModel):
    """Home city -> destination (and back)."""
    from_place: Optional[str] = ""
    to: str = ""
    mode: str = ""
    distance_km: float = 0
    duration_minutes: int = 0
    cost_inr: float = 0          # whole group, round trip
    round_trip: bool = True
    note: Optional[str] = ""


class ActivityOut(BaseModel):
    name: str = ""
    description: Optional[str] = ""
    location: Optional[str] = ""
    category: Optional[str] = "Activity"
    slot: Optional[str] = "morning"
    start_time: Optional[str] = "09:00"
    duration_minutes: Optional[int] = 90
    estimated_cost_inr: Optional[float] = 0
    notes: Optional[str] = ""
    travel: Optional[TravelOut] = None


class DayOut(BaseModel):
    day_number: int
    date: Optional[str] = ""
    theme: Optional[str] = ""
    activities: List[ActivityOut] = Field(default_factory=list)


class ItineraryOut(BaseModel):
    trip_title: Optional[str] = ""
    destination: Optional[str] = ""
    duration_days: Optional[int] = 0
    currency: Optional[str] = "INR"
    days: List[DayOut] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    source: Optional[str] = None  # "ai" | "demo"
    getting_there: Optional[GettingThereOut] = None
    ai_error: Optional[str] = None   # why the live AI was not used (shown on the sample banner)


# ---------- BUDGET ----------
class ExpenseIn(BaseModel):
    item: str = Field(min_length=1, max_length=255)
    category: str = Field(default="Misc", max_length=60)
    amount: float = Field(gt=0, le=1e9)

    @field_validator("item")
    @classmethod
    def _strip_item(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Item cannot be empty")
        return v


class ExpenseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    item: str
    category: str
    amount: float


class BudgetOut(BaseModel):
    total_budget_inr: float
    estimated_total_inr: float          # from the AI itinerary
    spent_inr: float                    # expenses the user logged
    remaining_inr: float                # budget - estimated
    utilization: float                  # estimated / budget, in %
    by_category_inr: dict               # estimated, grouped
    spent_by_category_inr: dict = Field(default_factory=dict)
    expenses: List[ExpenseOut] = Field(default_factory=list)


class BudgetBreakdownItem(BaseModel):
    category: str
    amount: float


class BudgetTripOut(BaseModel):
    id: int
    title: str
    budget_inr: float
    estimated_inr: float
    spent_inr: float
    remaining_inr: float
    utilization: float
    breakdown: List[BudgetBreakdownItem] = Field(default_factory=list)
    expenses: List[ExpenseOut] = Field(default_factory=list)


class BudgetOverviewOut(BaseModel):
    trips: List[BudgetTripOut]
    total_budget_inr: float = 0
    total_estimated_inr: float = 0
    total_spent_inr: float = 0


# ---------- PLACES ----------
class PlaceOut(BaseModel):
    id: str
    name: str
    category: Optional[str] = ""
    description: Optional[str] = ""
    lat: Optional[float] = None
    lon: Optional[float] = None
    image: Optional[str] = ""
    source: str = "openstreetmap"


class DestinationOut(BaseModel):
    id: str
    name: str
    state: str
    country: str = ""
    region: str
    zone: str = ""
    tagline: str
    avg_daily: int
    best_time: str = ""
    tags: List[str] = Field(default_factory=list)
    image: Optional[str] = None


class SavedPlaceIn(BaseModel):
    place_id: str = Field(min_length=1, max_length=120)
    name: str = Field(min_length=1, max_length=255)
    state: Optional[str] = ""
    category: Optional[str] = ""
    description: Optional[str] = ""
    image: Optional[str] = None
    avg_daily: Optional[int] = None
    lat: Optional[float] = None
    lon: Optional[float] = None


class SavedPlaceOut(BaseModel):
    id: int                 # row id (used for DELETE)
    place_id: str
    name: str
    state: Optional[str] = ""
    category: Optional[str] = ""
    description: Optional[str] = ""
    image: Optional[str] = None
    avg_daily: Optional[int] = None
    lat: Optional[float] = None
    lon: Optional[float] = None


# ---------- CHAT ----------
class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    trip_id: Optional[int] = None
    history: List[dict[str, Any]] = Field(default_factory=list, max_length=40)

    @field_validator("message")
    @classmethod
    def _strip_message(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Message cannot be empty")
        return v


class ChatOut(BaseModel):
    reply: str
    demo: bool = False


# ---------- WEATHER ----------
class WeatherOut(BaseModel):
    city: str
    temp: float
    condition: str
    icon: str = "cloud"
    humidity: int
    wind: float
    source: str = "open-meteo"
