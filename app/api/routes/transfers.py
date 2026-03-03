from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.transactions import Transfer, TransferIn
from app.services import transfers as transfers_service

router = APIRouter(tags=["transfers"])


@router.post("/transfers", response_model=Transfer)
def create_transfer(payload: TransferIn, db: Session = Depends(get_db)) -> Transfer:
    return transfers_service.create_transfer(db, payload)


@router.get("/transfers", response_model=list[Transfer])
def list_transfers(db: Session = Depends(get_db)) -> list[Transfer]:
    return transfers_service.list_transfers(db)
