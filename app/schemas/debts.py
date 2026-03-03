from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import DebtKind, DebtStatus


class DebtIn(BaseModel):
    kind: DebtKind
    counterparty: str = Field(min_length=1)
    amount: float = Field(gt=0)
    date: date
    due_date: date | None = None
    note: str = ""


class Debt(BaseModel):
    id: str
    kind: DebtKind
    counterparty: str
    amount: float
    paid_amount: float
    date: date
    due_date: date | None = None
    note: str = ""
    status: DebtStatus

    model_config = ConfigDict(from_attributes=True)


class DebtPaymentIn(BaseModel):
    amount: float = Field(gt=0)
