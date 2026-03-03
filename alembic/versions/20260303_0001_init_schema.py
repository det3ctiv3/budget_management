"""init schema

Revision ID: 20260303_0001
Revises:
Create Date: 2026-03-03 12:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260303_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("type", sa.Enum("CARD", "BANK_ACCOUNT", "CASH", name="accounttype"), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("balance", sa.Numeric(14, 2), nullable=False),
    )

    op.create_table(
        "expenses",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("account_id", sa.String(length=36), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column(
            "category",
            sa.Enum(
                "FOOD",
                "TRANSPORT",
                "UTILITIES",
                "SHOPPING",
                "HEALTH",
                "EDUCATION",
                "SALARY",
                "FREELANCE",
                "INVESTMENT",
                "OTHER",
                name="transactioncategory",
            ),
            nullable=False,
        ),
        sa.CheckConstraint("amount > 0", name="ck_expenses_amount_positive"),
    )
    op.create_index("ix_expenses_account_id", "expenses", ["account_id"])
    op.create_index("ix_expenses_date", "expenses", ["date"])

    op.create_table(
        "incomes",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("account_id", sa.String(length=36), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("source", sa.String(length=500), nullable=False),
        sa.Column(
            "category",
            sa.Enum(
                "FOOD",
                "TRANSPORT",
                "UTILITIES",
                "SHOPPING",
                "HEALTH",
                "EDUCATION",
                "SALARY",
                "FREELANCE",
                "INVESTMENT",
                "OTHER",
                name="transactioncategory",
            ),
            nullable=False,
        ),
        sa.CheckConstraint("amount > 0", name="ck_incomes_amount_positive"),
    )
    op.create_index("ix_incomes_account_id", "incomes", ["account_id"])
    op.create_index("ix_incomes_date", "incomes", ["date"])

    op.create_table(
        "transfers",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("from_account_id", sa.String(length=36), nullable=False),
        sa.Column("to_account_id", sa.String(length=36), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("converted_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("exchange_rate", sa.Numeric(14, 6), nullable=True),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.CheckConstraint("amount > 0", name="ck_transfers_amount_positive"),
    )
    op.create_index("ix_transfers_from_account_id", "transfers", ["from_account_id"])
    op.create_index("ix_transfers_to_account_id", "transfers", ["to_account_id"])
    op.create_index("ix_transfers_date", "transfers", ["date"])

    op.create_table(
        "debts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("kind", sa.Enum("DEBT", "RECEIVABLE", name="debtkind"), nullable=False),
        sa.Column("counterparty", sa.String(length=200), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("paid_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("note", sa.String(length=500), nullable=False),
        sa.Column("status", sa.Enum("OPEN", "CLOSED", name="debtstatus"), nullable=False),
        sa.CheckConstraint("amount > 0", name="ck_debts_amount_positive"),
    )
    op.create_index("ix_debts_date", "debts", ["date"])

    op.create_table(
        "monthly_income_budgets",
        sa.Column("month", sa.String(length=7), primary_key=True),
        sa.Column("income_target", sa.Numeric(14, 2), nullable=False),
    )

    op.create_table(
        "category_limits",
        sa.Column("month", sa.String(length=7), primary_key=True),
        sa.Column(
            "category",
            sa.Enum(
                "FOOD",
                "TRANSPORT",
                "UTILITIES",
                "SHOPPING",
                "HEALTH",
                "EDUCATION",
                "SALARY",
                "FREELANCE",
                "INVESTMENT",
                "OTHER",
                name="transactioncategory",
            ),
            primary_key=True,
        ),
        sa.Column("limit", sa.Numeric(14, 2), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("category_limits")
    op.drop_table("monthly_income_budgets")
    op.drop_index("ix_debts_date", table_name="debts")
    op.drop_table("debts")
    op.drop_index("ix_transfers_date", table_name="transfers")
    op.drop_index("ix_transfers_to_account_id", table_name="transfers")
    op.drop_index("ix_transfers_from_account_id", table_name="transfers")
    op.drop_table("transfers")
    op.drop_index("ix_incomes_date", table_name="incomes")
    op.drop_index("ix_incomes_account_id", table_name="incomes")
    op.drop_table("incomes")
    op.drop_index("ix_expenses_date", table_name="expenses")
    op.drop_index("ix_expenses_account_id", table_name="expenses")
    op.drop_table("expenses")
    op.drop_table("accounts")
