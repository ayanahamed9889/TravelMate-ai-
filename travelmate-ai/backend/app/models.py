from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship
from app.database import Base


def utcnow() -> datetime:
    """Naive UTC timestamp (datetime.utcnow() is deprecated)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(120), nullable=True)
    created_at = Column(DateTime, default=utcnow)
    trips = relationship("Trip", back_populates="user", cascade="all, delete-orphan")


class Trip(Base):
    __tablename__ = "trips"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    destination = Column(String(255), nullable=False)
    departure = Column(String(255), nullable=True)
    start_date = Column(String(20), nullable=True)
    end_date = Column(String(20), nullable=True)
    travelers = Column(Integer, default=1)
    trip_type = Column(String(40), default="Solo")
    preferences = Column(JSON, default=list)
    accommodation = Column(String(40), default="Hotel")
    transport = Column(String(40), default="Flight")
    budget = Column(Float, default=0)
    currency = Column(String(10), default="INR")
    budget_tier = Column(String(20), default="moderate")
    status = Column(String(20), default="draft")
    cover_image = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    user = relationship("User", back_populates="trips")
    itinerary = relationship("Itinerary", back_populates="trip", uselist=False, cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="trip", cascade="all, delete-orphan")


class Itinerary(Base):
    __tablename__ = "itineraries"
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"), unique=True)
    data = Column(JSON, default=dict)
    warnings = Column(JSON, default=list)
    assumptions = Column(JSON, default=list)
    generated_at = Column(DateTime, default=utcnow)
    trip = relationship("Trip", back_populates="itinerary")


class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"), index=True)
    item = Column(String(255), nullable=False)
    category = Column(String(60), default="Misc")
    amount = Column(Float, default=0)
    is_actual = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)
    trip = relationship("Trip", back_populates="expenses")


class SavedPlace(Base):
    __tablename__ = "saved_places"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    place_id = Column(String(120), nullable=False)
    data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utcnow)


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    role = Column(String(20), default="user")
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utcnow)