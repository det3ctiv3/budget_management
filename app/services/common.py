from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import DomainError
from app.db.models import AccountModel, DebtModel, ExpenseModel, IncomeModel
from app.utils.money import to_decimal


def month_key(dt: date) -> str:
    return f"{dt.year:04d}-{dt.month:02d}"


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
    raise DomainError(status_code=400, detail="period must be day|week|month|year")


def get_account_or_404(db: Session, account_id: str) -> AccountModel:
    account = db.get(AccountModel, account_id)
    if account is None:
        raise DomainError(status_code=404, detail=f"Account '{account_id}' not found")
    return account


def get_expense_or_404(db: Session, expense_id: str) -> ExpenseModel:
    expense = db.get(ExpenseModel, expense_id)
    if expense is None:
        raise DomainError(status_code=404, detail=f"Expense '{expense_id}' not found")
    return expense


def get_income_or_404(db: Session, income_id: str) -> IncomeModel:
    income = db.get(IncomeModel, income_id)
    if income is None:
        raise DomainError(status_code=404, detail=f"Income '{income_id}' not found")
    return income


def get_debt_or_404(db: Session, debt_id: str) -> DebtModel:
    debt = db.get(DebtModel, debt_id)
    if debt is None:
        raise DomainError(status_code=404, detail=f"Debt '{debt_id}' not found")
    return debt


def ensure_funds(account: AccountModel, amount: float) -> None:
    if account.balance < to_decimal(amount):
        raise DomainError(status_code=400, detail=f"Insufficient funds on account '{account.id}'")


def ensure_account_exists(db: Session, account_id: str) -> None:
    exists = db.execute(select(AccountModel.id).where(AccountModel.id == account_id)).scalar_one_or_none()
    if exists is None:
        raise DomainError(status_code=404, detail=f"Account '{account_id}' not found")
