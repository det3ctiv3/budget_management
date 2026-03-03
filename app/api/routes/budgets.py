from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.budgets import CategoryLimitIn, MonthlyBudgetIn
from app.services import budgets as budgets_service

router = APIRouter(tags=["budgets"])


@router.post("/budgets/monthly-income")
def set_monthly_income_budget(payload: MonthlyBudgetIn, db: Session = Depends(get_db)) -> dict[str, Any]:
    return budgets_service.set_monthly_income_budget(db, payload)


@router.post("/budgets/category-limits")
def set_category_limit(payload: CategoryLimitIn, db: Session = Depends(get_db)) -> dict[str, Any]:
    return budgets_service.set_category_limit(db, payload)


@router.get("/budgets/monthly/{month}/comparison")
def monthly_budget_comparison(month: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    return budgets_service.monthly_budget_comparison(db, month)
