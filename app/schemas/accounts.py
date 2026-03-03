from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.enums import AccountType


class AccountIn(BaseModel):
    name: str = Field(min_length=1)
    type: AccountType
    currency: str = Field(default="USD", min_length=3, max_length=3)
    initial_balance: float = 0

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.upper()


class Account(BaseModel):
    id: str
    name: str
    type: AccountType
    currency: str
    balance: float

    model_config = ConfigDict(from_attributes=True)
