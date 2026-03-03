from __future__ import annotations

from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import DomainError
from app.db.models import DebtModel
from app.schemas.debts import Debt, DebtIn, DebtPaymentIn
from app.schemas.enums import DebtStatus
from app.services.common import get_debt_or_404
from app.services.serializers import debt_out
from app.utils.money import to_decimal


def create_debt(db: Session, payload: DebtIn) -> Debt:
    model = DebtModel(
        id=str(uuid4()),
        kind=payload.kind,
        counterparty=payload.counterparty,
        amount=to_decimal(payload.amount),
        paid_amount=to_decimal(0),
        date=payload.date,
        due_date=payload.due_date,
        note=payload.note,
        status=DebtStatus.OPEN,
    )
    db.add(model)
    db.commit()
    return debt_out(model)


def list_debts(db: Session, status: DebtStatus | None = None) -> list[Debt]:
    query = select(DebtModel)
    if status is not None:
        query = query.where(DebtModel.status == status)
    rows = db.execute(query.order_by(DebtModel.date.desc())).scalars().all()
    return [debt_out(row) for row in rows]


def add_debt_payment(db: Session, debt_id: str, payload: DebtPaymentIn) -> Debt:
    debt = get_debt_or_404(db, debt_id)
    if debt.status == DebtStatus.CLOSED:
        raise DomainError(status_code=400, detail="Debt already closed")

    new_paid = debt.paid_amount + to_decimal(payload.amount)
    if new_paid > debt.amount:
        raise DomainError(status_code=400, detail="Payment exceeds debt amount")

    debt.paid_amount = new_paid
    if debt.paid_amount == debt.amount:
        debt.status = DebtStatus.CLOSED

    db.commit()
    return debt_out(debt)


def close_debt(db: Session, debt_id: str) -> Debt:
    debt = get_debt_or_404(db, debt_id)
    debt.paid_amount = debt.amount
    debt.status = DebtStatus.CLOSED
    db.commit()
    return debt_out(debt)
