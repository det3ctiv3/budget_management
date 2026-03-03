from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel

Period = Literal["day", "week", "month", "year"]


class SummaryResponse(BaseModel):
    period: str
    anchor_date: date
    total_income: float
    total_expense: float
    net: float


class ByCategoryRow(BaseModel):
    category: str
    income: float
    expense: float
    net: float


class ByCategoryResponse(BaseModel):
    period: str
    anchor_date: date
    rows: list[ByCategoryRow]


class CalendarDay(BaseModel):
    date: str
    income_total: float
    expense_total: float
    net: float
    income_count: int
    expense_count: int


class CalendarResponse(BaseModel):
    from_date: date
    to_date: date
    days: list[CalendarDay]
