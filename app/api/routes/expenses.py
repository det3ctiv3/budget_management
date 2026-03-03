from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.transactions import Expense, ExpenseIn
from app.services import expenses as expenses_service

router = APIRouter(tags=["expenses"])


@router.post("/expenses", response_model=Expense)
def create_expense(payload: ExpenseIn, db: Session = Depends(get_db)) -> Expense:
    return expenses_service.create_expense(db, payload)


@router.get("/expenses", response_model=list[Expense])
def list_expenses(db: Session = Depends(get_db)) -> list[Expense]:
    return expenses_service.list_expenses(db)


@router.put("/expenses/{expense_id}", response_model=Expense)
def update_expense(expense_id: str, payload: ExpenseIn, db: Session = Depends(get_db)) -> Expense:
    return expenses_service.update_expense(db, expense_id, payload)


@router.delete("/expenses/{expense_id}")
def delete_expense(expense_id: str, db: Session = Depends(get_db)) -> dict[str, str]:
    return expenses_service.delete_expense(db, expense_id)
