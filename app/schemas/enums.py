from __future__ import annotations

from enum import Enum


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
