from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

TWO_PLACES = Decimal("0.01")


def to_decimal(value: float | int | str | Decimal) -> Decimal:
    return Decimal(str(value)).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def to_rate_decimal(value: float | int | str | Decimal) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)


def to_float(value: Decimal | int | float | None) -> float | None:
    if value is None:
        return None
    decimal_value = value if isinstance(value, Decimal) else Decimal(str(value))
    return float(decimal_value.quantize(TWO_PLACES, rounding=ROUND_HALF_UP))
