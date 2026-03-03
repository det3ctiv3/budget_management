from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.ai import AICategoryRequest
from app.services import ai as ai_service

router = APIRouter(tags=["ai"])


@router.post("/ai/suggest-category")
def ai_suggest_category(payload: AICategoryRequest) -> dict[str, Any]:
    return ai_service.ai_suggest_category(payload.description)


@router.get("/ai/alerts/{month}")
def ai_alerts(month: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    return ai_service.ai_alerts(db, month)
