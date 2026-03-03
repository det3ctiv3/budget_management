from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.debts import Debt, DebtIn, DebtPaymentIn
from app.schemas.enums import DebtStatus
from app.services import debts as debts_service

router = APIRouter(tags=["debts"])


@router.post("/debts", response_model=Debt)
def create_debt(payload: DebtIn, db: Session = Depends(get_db)) -> Debt:
    return debts_service.create_debt(db, payload)


@router.get("/debts", response_model=list[Debt])
def list_debts(status: DebtStatus | None = None, db: Session = Depends(get_db)) -> list[Debt]:
    return debts_service.list_debts(db, status)


@router.post("/debts/{debt_id}/payments", response_model=Debt)
def add_debt_payment(debt_id: str, payload: DebtPaymentIn, db: Session = Depends(get_db)) -> Debt:
    return debts_service.add_debt_payment(db, debt_id, payload)


@router.put("/debts/{debt_id}/close", response_model=Debt)
def close_debt(debt_id: str, db: Session = Depends(get_db)) -> Debt:
    return debts_service.close_debt(db, debt_id)
