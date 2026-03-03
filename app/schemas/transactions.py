from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import TransactionCategory


class ExpenseIn(BaseModel):
    account_id: str
    amount: float = Field(gt=0)
    date: date
    description: str = ""
    category: TransactionCategory = TransactionCategory.OTHER


class IncomeIn(BaseModel):
    account_id: str
    amount: float = Field(gt=0)
    date: date
    source: str = ""
    category: TransactionCategory = TransactionCategory.OTHER


class Expense(BaseModel):
    id: str
    account_id: str
    amount: float
    date: date
    description: str
    category: TransactionCategory

    model_config = ConfigDict(from_attributes=True)


class Income(BaseModel):
    id: str
    account_id: str
    amount: float
    date: date
    source: str
    category: TransactionCategory

    model_config = ConfigDict(from_attributes=True)


class TransferIn(BaseModel):
    from_account_id: str
    to_account_id: str
    amount: float = Field(gt=0)
    date: date
    exchange_rate: float | None = Field(default=None, gt=0)
    description: str = ""


class Transfer(BaseModel):
    id: str
    from_account_id: str
    to_account_id: str
    amount: float
    converted_amount: float
    date: date
    exchange_rate: float | None
    description: str

    model_config = ConfigDict(from_attributes=True)
