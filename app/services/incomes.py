from __future__ import annotations

from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import IncomeModel
from app.schemas.transactions import Income, IncomeIn
from app.services.common import ensure_funds, get_account_or_404, get_income_or_404
from app.services.serializers import income_out
from app.utils.money import to_decimal


def create_income(db: Session, payload: IncomeIn) -> Income:
    account = get_account_or_404(db, payload.account_id)
    account.balance += to_decimal(payload.amount)
    model = IncomeModel(
        id=str(uuid4()),
        account_id=payload.account_id,
        amount=to_decimal(payload.amount),
        date=payload.date,
        source=payload.source,
        category=payload.category,
    )
    db.add(model)
    db.commit()
    return income_out(model)


def list_incomes(db: Session) -> list[Income]:
    rows = db.execute(select(IncomeModel).order_by(IncomeModel.date.desc())).scalars().all()
    return [income_out(row) for row in rows]


def update_income(db: Session, income_id: str, payload: IncomeIn) -> Income:
    old = get_income_or_404(db, income_id)
    old_account = get_account_or_404(db, old.account_id)
    old_account.balance -= old.amount

    new_account = get_account_or_404(db, payload.account_id)
    new_account.balance += to_decimal(payload.amount)

    old.account_id = payload.account_id
    old.amount = to_decimal(payload.amount)
    old.date = payload.date
    old.source = payload.source
    old.category = payload.category

    db.commit()
    return income_out(old)


def delete_income(db: Session, income_id: str) -> dict[str, str]:
    income = get_income_or_404(db, income_id)
    account = get_account_or_404(db, income.account_id)
    ensure_funds(account, float(income.amount))
    account.balance -= income.amount
    db.delete(income)
    db.commit()
    return {"message": "Income deleted"}
