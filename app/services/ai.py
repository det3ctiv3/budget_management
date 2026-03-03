from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import CategoryLimitModel, ExpenseModel
from app.schemas.enums import TransactionCategory
from app.services.common import month_key
from app.utils.money import to_float


def suggest_category(description: str) -> TransactionCategory:
    text = description.lower()
    rules: list[tuple[list[str], TransactionCategory]] = [
        (["taxi", "bus", "metro", "fuel", "petrol"], TransactionCategory.TRANSPORT),
        (["food", "cafe", "restaurant", "grocery"], TransactionCategory.FOOD),
        (["salary", "payroll", "bonus"], TransactionCategory.SALARY),
        (["water", "electricity", "internet", "gas"], TransactionCategory.UTILITIES),
        (["doctor", "medicine", "pharmacy"], TransactionCategory.HEALTH),
        (["course", "school", "book", "tuition"], TransactionCategory.EDUCATION),
    ]
    for keywords, category in rules:
        if any(word in text for word in keywords):
            return category
    return TransactionCategory.OTHER


def ai_suggest_category(description: str) -> dict[str, Any]:
    return {
        "description": description,
        "suggested_category": suggest_category(description),
        "method": "rule-based",
    }


def ai_alerts(db: Session, month: str) -> dict[str, Any]:
    expenses = db.execute(select(ExpenseModel)).scalars().all()
    month_expenses = [row for row in expenses if month_key(row.date) == month]

    limits = db.execute(select(CategoryLimitModel).where(CategoryLimitModel.month == month)).scalars().all()
    limits_map = {limit.category: limit.limit for limit in limits}

    per_category_actual: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    for expense in month_expenses:
        per_category_actual[expense.category.value] += expense.amount

    alerts: list[dict[str, Any]] = []
    for category, amount in per_category_actual.items():
        limit = limits_map.get(TransactionCategory(category))
        if limit is not None and amount > limit:
            alerts.append(
                {
                    "type": "CATEGORY_OVERSPEND",
                    "category": category,
                    "actual": to_float(amount),
                    "limit": to_float(limit),
                    "message": f"Spending in {category} exceeded limit by {to_float(amount - limit)}",
                }
            )

    return {"month": month, "alerts": alerts}
