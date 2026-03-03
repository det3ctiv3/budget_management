from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session
from uuid import uuid4

from app.db.models import ExpenseModel
from app.schemas.transactions import Expense, ExpenseIn
from app.services.common import ensure_funds, get_account_or_404, get_expense_or_404
from app.services.serializers import expense_out
from app.utils.money import to_decimal


def create_expense(db: Session, payload: ExpenseIn) -> Expense:
    account = get_account_or_404(db, payload.account_id)
    ensure_funds(account, payload.amount)
    account.balance -= to_decimal(payload.amount)

    model = ExpenseModel(
        id=str(uuid4()),
        account_id=payload.account_id,
        amount=to_decimal(payload.amount),
        date=payload.date,
        description=payload.description,
        category=payload.category,
    )
    db.add(model)
    db.commit()
    return expense_out(model)


def list_expenses(db: Session) -> list[Expense]:
    rows = db.execute(select(ExpenseModel).order_by(ExpenseModel.date.desc())).scalars().all()
    return [expense_out(row) for row in rows]


def update_expense(db: Session, expense_id: str, payload: ExpenseIn) -> Expense:
    old = get_expense_or_404(db, expense_id)
    old_account = get_account_or_404(db, old.account_id)
    old_account.balance += old.amount

    new_account = get_account_or_404(db, payload.account_id)
    ensure_funds(new_account, payload.amount)
    new_account.balance -= to_decimal(payload.amount)

    old.account_id = payload.account_id
    old.amount = to_decimal(payload.amount)
    old.date = payload.date
    old.description = payload.description
    old.category = payload.category

    db.commit()
    return expense_out(old)


def delete_expense(db: Session, expense_id: str) -> dict[str, str]:
    expense = get_expense_or_404(db, expense_id)
    account = get_account_or_404(db, expense.account_id)
    account.balance += expense.amount
    db.delete(expense)
    db.commit()
    return {"message": "Expense deleted"}
