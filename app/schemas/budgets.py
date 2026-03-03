from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.enums import TransactionCategory


class MonthlyBudgetIn(BaseModel):
    month: str = Field(pattern=r"^\d{4}-\d{2}$")
    income_target: float = Field(ge=0)


class CategoryLimitIn(BaseModel):
    month: str = Field(pattern=r"^\d{4}-\d{2}$")
    category: TransactionCategory
    limit: float = Field(ge=0)
