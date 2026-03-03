from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.errors import DomainError
from app.db.models import TransferModel
from app.schemas.transactions import Transfer, TransferIn
from app.services.common import ensure_funds, get_account_or_404
from app.services.serializers import transfer_out
from app.utils.money import to_decimal, to_rate_decimal


def create_transfer(db: Session, payload: TransferIn) -> Transfer:
    if payload.from_account_id == payload.to_account_id:
        raise DomainError(status_code=400, detail="from and to accounts must be different")

    source = get_account_or_404(db, payload.from_account_id)
    target = get_account_or_404(db, payload.to_account_id)
    ensure_funds(source, payload.amount)

    amount = to_decimal(payload.amount)
    if source.currency != target.currency:
        if payload.exchange_rate is None:
            raise DomainError(status_code=400, detail="exchange_rate is required for different currencies")
        rate = to_rate_decimal(payload.exchange_rate)
        converted = (amount * rate).quantize(Decimal("0.01"))
    else:
        rate = to_rate_decimal(payload.exchange_rate) if payload.exchange_rate is not None else None
        converted = amount

    source.balance -= amount
    target.balance += converted

    model = TransferModel(
        id=str(uuid4()),
        from_account_id=payload.from_account_id,
        to_account_id=payload.to_account_id,
        amount=amount,
        converted_amount=converted,
        date=payload.date,
        exchange_rate=rate,
        description=payload.description,
    )
    db.add(model)
    db.commit()
    return transfer_out(model)


def list_transfers(db: Session) -> list[Transfer]:
    rows = db.execute(select(TransferModel).order_by(TransferModel.date.desc())).scalars().all()
    return [transfer_out(row) for row in rows]
