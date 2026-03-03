from __future__ import annotations

from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(tags=["health"])
settings = get_settings()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/meta")
def metadata() -> dict[str, str]:
    return {
        "group": settings.group_name,
        "app_name": settings.app_name,
        "version": settings.app_version,
    }
