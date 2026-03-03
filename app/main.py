from __future__ import annotations

import logging
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    accounts_router,
    ai_router,
    analytics_router,
    budgets_router,
    debts_router,
    expenses_router,
    health_router,
    incomes_router,
    transfers_router,
)
from app.core.config import get_settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging
from app.db.init_db import init_db

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(title=settings.app_name, version=settings.app_version)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    @app.middleware("http")
    async def request_context_middleware(request: Request, call_next):  # type: ignore[no-untyped-def]
        request_id = str(uuid4())
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Group-Name"] = settings.group_name
        logger.info("%s %s %s", request.method, request.url.path, response.status_code)
        return response

    @app.on_event("startup")
    def on_startup() -> None:
        init_db()

    app.include_router(health_router)
    app.include_router(accounts_router)
    app.include_router(expenses_router)
    app.include_router(incomes_router)
    app.include_router(transfers_router)
    app.include_router(debts_router)
    app.include_router(budgets_router)
    app.include_router(analytics_router)
    app.include_router(ai_router)

    return app


app = create_app()
