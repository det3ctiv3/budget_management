from app.api.routes.accounts import router as accounts_router
from app.api.routes.ai import router as ai_router
from app.api.routes.analytics import router as analytics_router
from app.api.routes.budgets import router as budgets_router
from app.api.routes.debts import router as debts_router
from app.api.routes.expenses import router as expenses_router
from app.api.routes.health import router as health_router
from app.api.routes.incomes import router as incomes_router
from app.api.routes.transfers import router as transfers_router

__all__ = [
    "accounts_router",
    "ai_router",
    "analytics_router",
    "budgets_router",
    "debts_router",
    "expenses_router",
    "health_router",
    "incomes_router",
    "transfers_router",
]
