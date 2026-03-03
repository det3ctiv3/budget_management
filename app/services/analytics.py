from __future__ import annotations

from collections import defaultdict
from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import DomainError
from app.db.models import ExpenseModel, IncomeModel
from app.services.common import in_period
from app.utils.money import to_float


def analytics_summary(db: Session, period: str, anchor_date: date) -> dict[str, Any]:
    expenses = db.execute(select(ExpenseModel)).scalars().all()
    incomes = db.execute(select(IncomeModel)).scalars().all()

    filtered_expenses = [row for row in expenses if in_period(row.date, period, anchor_date)]
    filtered_incomes = [row for row in incomes if in_period(row.date, period, anchor_date)]

    expense_total = sum((row.amount for row in filtered_expenses), Decimal("0"))
    income_total = sum((row.amount for row in filtered_incomes), Decimal("0"))

    return {
        "period": period,
        "anchor_date": anchor_date,
        "total_income": to_float(income_total),
        "total_expense": to_float(expense_total),
        "net": to_float(income_total - expense_total),
    }


def analytics_by_category(db: Session, period: str, anchor_date: date) -> dict[str, Any]:
    expenses = db.execute(select(ExpenseModel)).scalars().all()
    incomes = db.execute(select(IncomeModel)).scalars().all()

    expense_stats: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    income_stats: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))

    for expense in expenses:
        if in_period(expense.date, period, anchor_date):
            expense_stats[expense.category.value] += expense.amount

    for income in incomes:
        if in_period(income.date, period, anchor_date):
            income_stats[income.category.value] += income.amount

    categories = sorted(set(expense_stats) | set(income_stats))
    rows: list[dict[str, Any]] = []
    for category in categories:
        income_amount = income_stats.get(category, Decimal("0"))
        expense_amount = expense_stats.get(category, Decimal("0"))
        rows.append(
            {
                "category": category,
                "income": to_float(income_amount),
                "expense": to_float(expense_amount),
                "net": to_float(income_amount - expense_amount),
            }
        )

    return {"period": period, "anchor_date": anchor_date, "rows": rows}


def analytics_calendar(db: Session, from_date: date, to_date: date) -> dict[str, Any]:
    if to_date < from_date:
        raise DomainError(status_code=400, detail="to_date must be greater than or equal to from_date")

    expenses = db.execute(select(ExpenseModel)).scalars().all()
    incomes = db.execute(select(IncomeModel)).scalars().all()

    days: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"income_total": Decimal("0"), "expense_total": Decimal("0"), "income_count": 0, "expense_count": 0}
    )

    for inc in incomes:
        if from_date <= inc.date <= to_date:
            key = inc.date.isoformat()
            days[key]["income_total"] += inc.amount
            days[key]["income_count"] += 1

    for exp in expenses:
        if from_date <= exp.date <= to_date:
            key = exp.date.isoformat()
            days[key]["expense_total"] += exp.amount
            days[key]["expense_count"] += 1

    result = []
    for day, value in sorted(days.items()):
        result.append(
            {
                "date": day,
                "income_total": to_float(value["income_total"]),
                "expense_total": to_float(value["expense_total"]),
                "net": to_float(value["income_total"] - value["expense_total"]),
                "income_count": value["income_count"],
                "expense_count": value["expense_count"],
            }
        )

    return {"from_date": from_date, "to_date": to_date, "days": result}
