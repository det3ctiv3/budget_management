from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.transactions import Income, IncomeIn
from app.services import incomes as incomes_service

router = APIRouter(tags=["incomes"])


@router.post("/incomes", response_model=Income)
def create_income(payload: IncomeIn, db: Session = Depends(get_db)) -> Income:
    return incomes_service.create_income(db, payload)


@router.get("/incomes", response_model=list[Income])
def list_incomes(db: Session = Depends(get_db)) -> list[Income]:
    return incomes_service.list_incomes(db)


@router.put("/incomes/{income_id}", response_model=Income)
def update_income(income_id: str, payload: IncomeIn, db: Session = Depends(get_db)) -> Income:
    return incomes_service.update_income(db, income_id, payload)


@router.delete("/incomes/{income_id}")
def delete_income(income_id: str, db: Session = Depends(get_db)) -> dict[str, str]:
    return incomes_service.delete_income(db, income_id)
