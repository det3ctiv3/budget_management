from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, Enum, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.schemas.enums import AccountType, DebtKind, DebtStatus, TransactionCategory


class AccountModel(Base):
    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[AccountType] = mapped_column(Enum(AccountType), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0"))


class ExpenseModel(Base):
    __tablename__ = "expenses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    account_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    category: Mapped[TransactionCategory] = mapped_column(Enum(TransactionCategory), nullable=False)

    __table_args__ = (CheckConstraint("amount > 0", name="ck_expenses_amount_positive"),)


class IncomeModel(Base):
    __tablename__ = "incomes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    account_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    category: Mapped[TransactionCategory] = mapped_column(Enum(TransactionCategory), nullable=False)

    __table_args__ = (CheckConstraint("amount > 0", name="ck_incomes_amount_positive"),)


class TransferModel(Base):
    __tablename__ = "transfers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    from_account_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    to_account_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    converted_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    exchange_rate: Mapped[Decimal | None] = mapped_column(Numeric(14, 6), nullable=True)
    description: Mapped[str] = mapped_column(String(500), nullable=False, default="")

    __table_args__ = (CheckConstraint("amount > 0", name="ck_transfers_amount_positive"),)


class DebtModel(Base):
    __tablename__ = "debts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    kind: Mapped[DebtKind] = mapped_column(Enum(DebtKind), nullable=False)
    counterparty: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    note: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    status: Mapped[DebtStatus] = mapped_column(Enum(DebtStatus), nullable=False)

    __table_args__ = (CheckConstraint("amount > 0", name="ck_debts_amount_positive"),)


class MonthlyIncomeBudgetModel(Base):
    __tablename__ = "monthly_income_budgets"

    month: Mapped[str] = mapped_column(String(7), primary_key=True)
    income_target: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)


class CategoryLimitModel(Base):
    __tablename__ = "category_limits"

    month: Mapped[str] = mapped_column(String(7), primary_key=True)
    category: Mapped[TransactionCategory] = mapped_column(Enum(TransactionCategory), primary_key=True)
    limit: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
