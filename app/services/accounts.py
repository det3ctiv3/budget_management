from __future__ import annotations

from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AccountModel
from app.schemas.accounts import Account, AccountIn
from app.services.serializers import account_out
from app.utils.money import to_decimal


def create_account(db: Session, payload: AccountIn) -> Account:
    model = AccountModel(
        id=str(uuid4()),
        name=payload.name,
        type=payload.type,
        currency=payload.currency.upper(),
        balance=to_decimal(payload.initial_balance),
    )
    db.add(model)
    db.commit()
    return account_out(model)


def list_accounts(db: Session) -> list[Account]:
    rows = db.execute(select(AccountModel)).scalars().all()
    return [account_out(row) for row in rows]
