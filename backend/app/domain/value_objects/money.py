from dataclasses import dataclass
from decimal import Decimal
from typing import Union


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "USD"

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Cannot subtract different currencies")
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: Union[int, float, Decimal]) -> "Money":
        return Money(self.amount * Decimal(factor), self.currency)

    def __truediv__(self, divisor: Union[int, float, Decimal]) -> "Money":
        return Money(self.amount / Decimal(divisor), self.currency)

    def __str__(self) -> str:
        return f"{self.currency} {self.amount:.2f}"
