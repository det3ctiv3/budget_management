from __future__ import annotations

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.services import analytics as analytics_service

router = APIRouter(tags=["analytics"])


@router.get("/analytics/summary")
def analytics_summary(
    period: str = Query(default="month"),
    anchor_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return analytics_service.analytics_summary(db, period, anchor_date or date.today())


@router.get("/analytics/by-category")
def analytics_by_category(
    period: str = Query(default="month"),
    anchor_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return analytics_service.analytics_by_category(db, period, anchor_date or date.today())


@router.get("/analytics/calendar")
def analytics_calendar(
    from_date: date,
    to_date: date,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return analytics_service.analytics_calendar(db, from_date, to_date)
