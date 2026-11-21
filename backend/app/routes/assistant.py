import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import ChatMessage, Trip, User
from app.schemas import ChatIn, ChatOut
from app.services.ai_service import chat_reply

log = logging.getLogger("travelmate.assistant")
router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/chat", response_model=ChatOut)
def chat(payload: ChatIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    trip_ctx = None
    if payload.trip_id:
        t = db.query(Trip).filter(Trip.id == payload.trip_id, Trip.user_id == user.id).first()
        if t:
            trip_ctx = {
                "destination": t.destination, "from": t.departure,
                "start_date": t.start_date, "end_date": t.end_date,
                "travelers": t.travelers, "budget_inr": t.budget,
                "preferences": t.preferences,
            }
    try:
        reply, demo = chat_reply(payload.message, payload.history, trip_ctx)
    except Exception:  # noqa: BLE001
        log.exception("chat failed")
        raise HTTPException(503, "The assistant is busy right now. Please try again in a moment.")

    trip_id = payload.trip_id if trip_ctx else None
    db.add(ChatMessage(trip_id=trip_id, user_id=user.id, role="user", content=payload.message))
    db.add(ChatMessage(trip_id=trip_id, user_id=user.id, role="assistant", content=reply))
    db.commit()
    return {"reply": reply, "demo": demo}
