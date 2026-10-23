from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Expense, Trip, User
from app.schemas import BudgetOut, BudgetOverviewOut, ExpenseIn, ExpenseOut
from app.services.budget_service import budget_overview, compute_budget

router = APIRouter(tags=["budget"])


def _owned_trip(db: Session, trip_id: int, user: User) -> Trip:
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == user.id).first()
    if not trip:
        raise HTTPException(404, "Trip not found")
    return trip


@router.get("/budget/overview", response_model=BudgetOverviewOut)
def overview(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return budget_overview(db, user.id)


@router.get("/trips/{trip_id}/budget", response_model=BudgetOut)
def get_budget(trip_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return compute_budget(db, _owned_trip(db, trip_id, user))


@router.post("/trips/{trip_id}/expenses", response_model=ExpenseOut, status_code=201)
def add_expense(trip_id: int, payload: ExpenseIn, db: Session = Depends(get_db),
                user: User = Depends(get_current_user)):
    trip = _owned_trip(db, trip_id, user)
    exp = Expense(trip_id=trip.id, **payload.model_dump())
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return exp


@router.delete("/trips/{trip_id}/expenses/{expense_id}")
def delete_expense(trip_id: int, expense_id: int, db: Session = Depends(get_db),
                   user: User = Depends(get_current_user)):
    trip = _owned_trip(db, trip_id, user)
    exp = db.query(Expense).filter(Expense.id == expense_id, Expense.trip_id == trip.id).first()
    if not exp:
        raise HTTPException(404, "Expense not found")
    db.delete(exp)
    db.commit()
    return {"ok": True}
