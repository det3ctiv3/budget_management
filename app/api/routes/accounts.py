from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.accounts import Account, AccountIn
from app.services import accounts as accounts_service

router = APIRouter(tags=["accounts"])


@router.post("/accounts", response_model=Account)
def create_account(payload: AccountIn, db: Session = Depends(get_db)) -> Account:
    return accounts_service.create_account(db, payload)


@router.get("/accounts", response_model=list[Account])
def list_accounts(db: Session = Depends(get_db)) -> list[Account]:
    return accounts_service.list_accounts(db)
