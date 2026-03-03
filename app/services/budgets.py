from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import CategoryLimitModel, ExpenseModel, IncomeModel, MonthlyIncomeBudgetModel
from app.schemas.budgets import CategoryLimitIn, MonthlyBudgetIn
from app.schemas.enums import TransactionCategory
from app.services.common import month_key
from app.utils.money import to_decimal, to_float


def set_monthly_income_budget(db: Session, payload: MonthlyBudgetIn) -> dict[str, Any]:
    existing = db.get(MonthlyIncomeBudgetModel, payload.month)
    if existing is None:
        existing = MonthlyIncomeBudgetModel(month=payload.month, income_target=to_decimal(payload.income_target))
        db.add(existing)
    else:
        existing.income_target = to_decimal(payload.income_target)
    db.commit()
    return {"month": payload.month, "income_target": payload.income_target}


def set_category_limit(db: Session, payload: CategoryLimitIn) -> dict[str, Any]:
    existing = db.execute(
        select(CategoryLimitModel).where(
            CategoryLimitModel.month == payload.month,
            CategoryLimitModel.category == payload.category,
        )
    ).scalar_one_or_none()
    if existing is None:
        existing = CategoryLimitModel(month=payload.month, category=payload.category, limit=to_decimal(payload.limit))
        db.add(existing)
    else:
        existing.limit = to_decimal(payload.limit)
    db.commit()
    return {"month": payload.month, "category": payload.category, "limit": payload.limit}


def monthly_budget_comparison(db: Session, month: str) -> dict[str, Any]:
    expenses = db.execute(select(ExpenseModel)).scalars().all()
    incomes = db.execute(select(IncomeModel)).scalars().all()
    month_expenses = [row for row in expenses if month_key(row.date) == month]
    month_incomes = [row for row in incomes if month_key(row.date) == month]

    total_income = sum((row.amount for row in month_incomes), Decimal("0"))
    total_expense = sum((row.amount for row in month_expenses), Decimal("0"))

    target = db.get(MonthlyIncomeBudgetModel, month)
    target_income = target.income_target if target else None

    limits = db.execute(select(CategoryLimitModel).where(CategoryLimitModel.month == month)).scalars().all()
    limits_map = {limit.category: limit.limit for limit in limits}

    per_category_actual: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    for expense in month_expenses:
        per_category_actual[expense.category.value] += expense.amount

    category_report: list[dict[str, Any]] = []
    for category, actual in per_category_actual.items():
        category_enum = TransactionCategory(category)
        limit = limits_map.get(category_enum)
        category_report.append(
            {
                "category": category,
                "actual": to_float(actual),
                "limit": to_float(limit),
                "remaining": to_float(limit - actual) if limit is not None else None,
                "is_over_limit": limit is not None and actual > limit,
            }
        )

    return {
        "month": month,
        "income_target": to_float(target_income),
        "actual_income": to_float(total_income),
        "income_delta": to_float(total_income - target_income) if target_income is not None else None,
        "actual_expense": to_float(total_expense),
        "net_result": to_float(total_income - total_expense),
        "category_comparison": sorted(category_report, key=lambda x: x["category"]),
    }
