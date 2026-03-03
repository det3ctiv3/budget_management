from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from enum import Enum
from threading import Lock
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


app = FastAPI(title="CBU Coding Fintech MVP", version="0.1.0")
db_lock = Lock()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AccountType(str, Enum):
    CARD = "CARD"
    BANK_ACCOUNT = "BANK_ACCOUNT"
    CASH = "CASH"


class TransactionCategory(str, Enum):
    FOOD = "FOOD"
    TRANSPORT = "TRANSPORT"
    UTILITIES = "UTILITIES"
    SHOPPING = "SHOPPING"
    HEALTH = "HEALTH"
    EDUCATION = "EDUCATION"
    SALARY = "SALARY"
    FREELANCE = "FREELANCE"
    INVESTMENT = "INVESTMENT"
    OTHER = "OTHER"


class DebtKind(str, Enum):
    DEBT = "DEBT"
    RECEIVABLE = "RECEIVABLE"


class DebtStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class AccountIn(BaseModel):
    name: str = Field(min_length=1)
    type: AccountType
    currency: str = Field(default="USD", min_length=3, max_length=3)
    initial_balance: float = 0


class Account(BaseModel):
    id: str
    name: str
    type: AccountType
    currency: str
    balance: float


class ExpenseIn(BaseModel):
    account_id: str
    amount: float = Field(gt=0)
    date: date
    description: str = ""
    category: TransactionCategory = TransactionCategory.OTHER


class IncomeIn(BaseModel):
    account_id: str
    amount: float = Field(gt=0)
    date: date
    source: str = ""
    category: TransactionCategory = TransactionCategory.OTHER


class Expense(BaseModel):
    id: str
    account_id: str
    amount: float
    date: date
    description: str
    category: TransactionCategory


class Income(BaseModel):
    id: str
    account_id: str
    amount: float
    date: date
    source: str
    category: TransactionCategory


class TransferIn(BaseModel):
    from_account_id: str
    to_account_id: str
    amount: float = Field(gt=0)
    date: date
    exchange_rate: float | None = Field(default=None, gt=0)
    description: str = ""


class Transfer(BaseModel):
    id: str
    from_account_id: str
    to_account_id: str
    amount: float
    converted_amount: float
    date: date
    exchange_rate: float | None
    description: str


class DebtIn(BaseModel):
    kind: DebtKind
    counterparty: str = Field(min_length=1)
    amount: float = Field(gt=0)
    date: date
    due_date: date | None = None
    note: str = ""


class Debt(BaseModel):
    id: str
    kind: DebtKind
    counterparty: str
    amount: float
    paid_amount: float
    date: date
    due_date: date | None = None
    note: str = ""
    status: DebtStatus


class DebtPaymentIn(BaseModel):
    amount: float = Field(gt=0)


class MonthlyBudgetIn(BaseModel):
    month: str = Field(pattern=r"^\d{4}-\d{2}$")
    income_target: float = Field(ge=0)


class CategoryLimitIn(BaseModel):
    month: str = Field(pattern=r"^\d{4}-\d{2}$")
    category: TransactionCategory
    limit: float = Field(ge=0)


class AICategoryRequest(BaseModel):
    description: str


accounts: dict[str, Account] = {}
expenses: dict[str, Expense] = {}
incomes: dict[str, Income] = {}
transfers: dict[str, Transfer] = {}
debts: dict[str, Debt] = {}
monthly_income_budget: dict[str, float] = {}
category_limits: dict[str, dict[TransactionCategory, float]] = defaultdict(dict)


def month_key(dt: date) -> str:
    return f"{dt.year:04d}-{dt.month:02d}"


def get_account_or_404(account_id: str) -> Account:
    account = accounts.get(account_id)
    if not account:
        raise HTTPException(status_code=404, detail=f"Account '{account_id}' not found")
    return account


def get_expense_or_404(expense_id: str) -> Expense:
    expense = expenses.get(expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail=f"Expense '{expense_id}' not found")
    return expense


def get_income_or_404(income_id: str) -> Income:
    income = incomes.get(income_id)
    if not income:
        raise HTTPException(status_code=404, detail=f"Income '{income_id}' not found")
    return income


def get_debt_or_404(debt_id: str) -> Debt:
    debt = debts.get(debt_id)
    if not debt:
        raise HTTPException(status_code=404, detail=f"Debt '{debt_id}' not found")
    return debt


def ensure_funds(account: Account, amount: float) -> None:
    if account.balance < amount:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient funds on account '{account.id}'",
        )


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


def in_period(tx_date: date, period: str, anchor: date) -> bool:
    if period == "day":
        return tx_date == anchor
    if period == "week":
        start = anchor - timedelta(days=anchor.weekday())
        end = start + timedelta(days=6)
        return start <= tx_date <= end
    if period == "month":
        return tx_date.year == anchor.year and tx_date.month == anchor.month
    if period == "year":
        return tx_date.year == anchor.year
    raise HTTPException(status_code=400, detail="period must be day|week|month|year")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/accounts", response_model=Account)
def create_account(payload: AccountIn) -> Account:
    with db_lock:
        account = Account(
            id=str(uuid4()),
            name=payload.name,
            type=payload.type,
            currency=payload.currency.upper(),
            balance=payload.initial_balance,
        )
        accounts[account.id] = account
        return account


@app.get("/accounts", response_model=list[Account])
def list_accounts() -> list[Account]:
    return list(accounts.values())


@app.post("/expenses", response_model=Expense)
def create_expense(payload: ExpenseIn) -> Expense:
    with db_lock:
        account = get_account_or_404(payload.account_id)
        ensure_funds(account, payload.amount)
        account.balance -= payload.amount
        expense = Expense(id=str(uuid4()), **payload.model_dump())
        expenses[expense.id] = expense
        return expense


@app.get("/expenses", response_model=list[Expense])
def list_expenses() -> list[Expense]:
    return sorted(expenses.values(), key=lambda x: x.date, reverse=True)


@app.put("/expenses/{expense_id}", response_model=Expense)
def update_expense(expense_id: str, payload: ExpenseIn) -> Expense:
    with db_lock:
        old = get_expense_or_404(expense_id)
        old_account = get_account_or_404(old.account_id)
        old_account.balance += old.amount
        new_account = get_account_or_404(payload.account_id)
        ensure_funds(new_account, payload.amount)
        new_account.balance -= payload.amount
        updated = Expense(id=expense_id, **payload.model_dump())
        expenses[expense_id] = updated
        return updated


@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: str) -> dict[str, str]:
    with db_lock:
        expense = get_expense_or_404(expense_id)
        account = get_account_or_404(expense.account_id)
        account.balance += expense.amount
        del expenses[expense_id]
        return {"message": "Expense deleted"}


@app.post("/incomes", response_model=Income)
def create_income(payload: IncomeIn) -> Income:
    with db_lock:
        account = get_account_or_404(payload.account_id)
        account.balance += payload.amount
        income = Income(id=str(uuid4()), **payload.model_dump())
        incomes[income.id] = income
        return income


@app.get("/incomes", response_model=list[Income])
def list_incomes() -> list[Income]:
    return sorted(incomes.values(), key=lambda x: x.date, reverse=True)


@app.put("/incomes/{income_id}", response_model=Income)
def update_income(income_id: str, payload: IncomeIn) -> Income:
    with db_lock:
        old = get_income_or_404(income_id)
        old_account = get_account_or_404(old.account_id)
        old_account.balance -= old.amount
        new_account = get_account_or_404(payload.account_id)
        new_account.balance += payload.amount
        updated = Income(id=income_id, **payload.model_dump())
        incomes[income_id] = updated
        return updated


@app.delete("/incomes/{income_id}")
def delete_income(income_id: str) -> dict[str, str]:
    with db_lock:
        income = get_income_or_404(income_id)
        account = get_account_or_404(income.account_id)
        ensure_funds(account, income.amount)
        account.balance -= income.amount
        del incomes[income_id]
        return {"message": "Income deleted"}


@app.post("/transfers", response_model=Transfer)
def create_transfer(payload: TransferIn) -> Transfer:
    with db_lock:
        if payload.from_account_id == payload.to_account_id:
            raise HTTPException(status_code=400, detail="from and to accounts must be different")
        source = get_account_or_404(payload.from_account_id)
        target = get_account_or_404(payload.to_account_id)
        ensure_funds(source, payload.amount)

        if source.currency != target.currency:
            if payload.exchange_rate is None:
                raise HTTPException(
                    status_code=400,
                    detail="exchange_rate is required for different currencies",
                )
            converted = payload.amount * payload.exchange_rate
        else:
            converted = payload.amount

        source.balance -= payload.amount
        target.balance += converted
        transfer = Transfer(
            id=str(uuid4()),
            from_account_id=payload.from_account_id,
            to_account_id=payload.to_account_id,
            amount=payload.amount,
            converted_amount=converted,
            date=payload.date,
            exchange_rate=payload.exchange_rate,
            description=payload.description,
        )
        transfers[transfer.id] = transfer
        return transfer


@app.get("/transfers", response_model=list[Transfer])
def list_transfers() -> list[Transfer]:
    return sorted(transfers.values(), key=lambda x: x.date, reverse=True)


@app.post("/debts", response_model=Debt)
def create_debt(payload: DebtIn) -> Debt:
    with db_lock:
        debt = Debt(
            id=str(uuid4()),
            kind=payload.kind,
            counterparty=payload.counterparty,
            amount=payload.amount,
            paid_amount=0,
            date=payload.date,
            due_date=payload.due_date,
            note=payload.note,
            status=DebtStatus.OPEN,
        )
        debts[debt.id] = debt
        return debt


@app.get("/debts", response_model=list[Debt])
def list_debts(status: DebtStatus | None = None) -> list[Debt]:
    all_debts = list(debts.values())
    if status:
        all_debts = [d for d in all_debts if d.status == status]
    return sorted(all_debts, key=lambda x: x.date, reverse=True)


@app.post("/debts/{debt_id}/payments", response_model=Debt)
def add_debt_payment(debt_id: str, payload: DebtPaymentIn) -> Debt:
    with db_lock:
        debt = get_debt_or_404(debt_id)
        if debt.status == DebtStatus.CLOSED:
            raise HTTPException(status_code=400, detail="Debt already closed")
        new_paid = debt.paid_amount + payload.amount
        if new_paid > debt.amount:
            raise HTTPException(status_code=400, detail="Payment exceeds debt amount")
        debt.paid_amount = new_paid
        if debt.paid_amount == debt.amount:
            debt.status = DebtStatus.CLOSED
        debts[debt.id] = debt
        return debt


@app.put("/debts/{debt_id}/close", response_model=Debt)
def close_debt(debt_id: str) -> Debt:
    with db_lock:
        debt = get_debt_or_404(debt_id)
        debt.paid_amount = debt.amount
        debt.status = DebtStatus.CLOSED
        debts[debt.id] = debt
        return debt


@app.post("/budgets/monthly-income")
def set_monthly_income_budget(payload: MonthlyBudgetIn) -> dict[str, Any]:
    monthly_income_budget[payload.month] = payload.income_target
    return {"month": payload.month, "income_target": payload.income_target}


@app.post("/budgets/category-limits")
def set_category_limit(payload: CategoryLimitIn) -> dict[str, Any]:
    category_limits[payload.month][payload.category] = payload.limit
    return {
        "month": payload.month,
        "category": payload.category,
        "limit": payload.limit,
    }


@app.get("/budgets/monthly/{month}/comparison")
def monthly_budget_comparison(month: str) -> dict[str, Any]:
    month_expenses = [x for x in expenses.values() if month_key(x.date) == month]
    month_incomes = [x for x in incomes.values() if month_key(x.date) == month]
    total_income = sum(x.amount for x in month_incomes)
    total_expense = sum(x.amount for x in month_expenses)
    target_income = monthly_income_budget.get(month)
    per_category_actual: dict[str, float] = defaultdict(float)
    for expense in month_expenses:
        per_category_actual[expense.category.value] += expense.amount

    category_report = []
    for category, actual in per_category_actual.items():
        limit = category_limits.get(month, {}).get(TransactionCategory(category))
        category_report.append(
            {
                "category": category,
                "actual": round(actual, 2),
                "limit": limit,
                "remaining": round(limit - actual, 2) if limit is not None else None,
                "is_over_limit": limit is not None and actual > limit,
            }
        )

    return {
        "month": month,
        "income_target": target_income,
        "actual_income": round(total_income, 2),
        "income_delta": round(total_income - target_income, 2) if target_income is not None else None,
        "actual_expense": round(total_expense, 2),
        "net_result": round(total_income - total_expense, 2),
        "category_comparison": sorted(category_report, key=lambda x: x["category"]),
    }


@app.get("/analytics/summary")
def analytics_summary(
    period: str = Query(default="month"),
    anchor_date: date | None = Query(default=None),
) -> dict[str, Any]:
    anchor_date = anchor_date or date.today()
    filtered_expenses = [x for x in expenses.values() if in_period(x.date, period, anchor_date)]
    filtered_incomes = [x for x in incomes.values() if in_period(x.date, period, anchor_date)]
    expense_total = sum(x.amount for x in filtered_expenses)
    income_total = sum(x.amount for x in filtered_incomes)
    return {
        "period": period,
        "anchor_date": anchor_date,
        "total_income": round(income_total, 2),
        "total_expense": round(expense_total, 2),
        "net": round(income_total - expense_total, 2),
    }


@app.get("/analytics/by-category")
def analytics_by_category(
    period: str = Query(default="month"),
    anchor_date: date | None = Query(default=None),
) -> dict[str, Any]:
    anchor_date = anchor_date or date.today()
    expense_stats: dict[str, float] = defaultdict(float)
    income_stats: dict[str, float] = defaultdict(float)

    for expense in expenses.values():
        if in_period(expense.date, period, anchor_date):
            expense_stats[expense.category.value] += expense.amount
    for income in incomes.values():
        if in_period(income.date, period, anchor_date):
            income_stats[income.category.value] += income.amount

    categories = sorted(set(expense_stats) | set(income_stats))
    rows = []
    for category in categories:
        income_amount = income_stats.get(category, 0)
        expense_amount = expense_stats.get(category, 0)
        rows.append(
            {
                "category": category,
                "income": round(income_amount, 2),
                "expense": round(expense_amount, 2),
                "net": round(income_amount - expense_amount, 2),
            }
        )
    return {"period": period, "anchor_date": anchor_date, "rows": rows}


@app.get("/analytics/calendar")
def analytics_calendar(
    from_date: date,
    to_date: date,
) -> dict[str, Any]:
    if to_date < from_date:
        raise HTTPException(status_code=400, detail="to_date must be greater than or equal to from_date")

    days: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"income_total": 0.0, "expense_total": 0.0, "income_items": [], "expense_items": []}
    )

    for inc in incomes.values():
        if from_date <= inc.date <= to_date:
            key = inc.date.isoformat()
            days[key]["income_total"] += inc.amount
            days[key]["income_items"].append(inc)

    for exp in expenses.values():
        if from_date <= exp.date <= to_date:
            key = exp.date.isoformat()
            days[key]["expense_total"] += exp.amount
            days[key]["expense_items"].append(exp)

    result = []
    for day, value in sorted(days.items()):
        result.append(
            {
                "date": day,
                "income_total": round(value["income_total"], 2),
                "expense_total": round(value["expense_total"], 2),
                "net": round(value["income_total"] - value["expense_total"], 2),
                "income_count": len(value["income_items"]),
                "expense_count": len(value["expense_items"]),
            }
        )
    return {"from_date": from_date, "to_date": to_date, "days": result}


@app.post("/ai/suggest-category")
def ai_suggest_category(payload: AICategoryRequest) -> dict[str, Any]:
    return {
        "description": payload.description,
        "suggested_category": suggest_category(payload.description),
        "method": "rule-based",
    }


@app.get("/ai/alerts/{month}")
def ai_alerts(month: str) -> dict[str, Any]:
    month_expenses = [x for x in expenses.values() if month_key(x.date) == month]
    per_category_actual: dict[str, float] = defaultdict(float)
    for expense in month_expenses:
        per_category_actual[expense.category.value] += expense.amount

    alerts = []
    for category, amount in per_category_actual.items():
        limit = category_limits.get(month, {}).get(TransactionCategory(category))
        if limit is not None and amount > limit:
            alerts.append(
                {
                    "type": "CATEGORY_OVERSPEND",
                    "category": category,
                    "actual": round(amount, 2),
                    "limit": limit,
                    "message": f"Spending in {category} exceeded limit by {round(amount - limit, 2)}",
                }
            )
    return {"month": month, "alerts": alerts}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
