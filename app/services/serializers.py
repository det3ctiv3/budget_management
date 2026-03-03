from __future__ import annotations

from app.db.models import AccountModel, DebtModel, ExpenseModel, IncomeModel, TransferModel
from app.schemas.accounts import Account
from app.schemas.debts import Debt
from app.schemas.transactions import Expense, Income, Transfer
from app.utils.money import to_float


def account_out(model: AccountModel) -> Account:
    return Account(
        id=model.id,
        name=model.name,
        type=model.type,
        currency=model.currency,
        balance=to_float(model.balance) or 0.0,
    )


def expense_out(model: ExpenseModel) -> Expense:
    return Expense(
        id=model.id,
        account_id=model.account_id,
        amount=to_float(model.amount) or 0.0,
        date=model.date,
        description=model.description,
        category=model.category,
    )


def income_out(model: IncomeModel) -> Income:
    return Income(
        id=model.id,
        account_id=model.account_id,
        amount=to_float(model.amount) or 0.0,
        date=model.date,
        source=model.source,
        category=model.category,
    )


def transfer_out(model: TransferModel) -> Transfer:
    return Transfer(
        id=model.id,
        from_account_id=model.from_account_id,
        to_account_id=model.to_account_id,
        amount=to_float(model.amount) or 0.0,
        converted_amount=to_float(model.converted_amount) or 0.0,
        date=model.date,
        exchange_rate=float(model.exchange_rate) if model.exchange_rate is not None else None,
        description=model.description,
    )


def debt_out(model: DebtModel) -> Debt:
    return Debt(
        id=model.id,
        kind=model.kind,
        counterparty=model.counterparty,
        amount=to_float(model.amount) or 0.0,
        paid_amount=to_float(model.paid_amount) or 0.0,
        date=model.date,
        due_date=model.due_date,
        note=model.note,
        status=model.status,
    )
