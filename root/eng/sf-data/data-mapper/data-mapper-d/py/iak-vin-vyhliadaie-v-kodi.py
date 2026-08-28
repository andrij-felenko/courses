from dataclasses import dataclass
from datetime import datetime
from functools import reduce
import operator

# ── ДОМЕН: жодного натяку на базу ──────────────────────────────
@dataclass(frozen=True)
class Money:
    cents: int
    currency: str

    def __add__(self, other: "Money") -> "Money":
        if other.currency != self.currency:
            raise ValueError("різні валюти не додаються")
        return Money(self.cents + other.cents, self.currency)

    def __mul__(self, k: int) -> "Money":
        return Money(self.cents * k, self.currency)


@dataclass(frozen=True)
class OrderLine:
    sku: str
    qty: int
    price: Money

    def subtotal(self) -> Money:
        return self.price * self.qty


class Order:
    def __init__(self, id, placed_at, lines, status="new"):
        if not lines:
            raise ValueError("замовлення без позицій не буває")
        self.id = id
        self.placed_at = placed_at
        self.lines = list(lines)
        self.status = status

    def total(self) -> Money:
        return reduce(operator.add, (l.subtotal() for l in self.lines))

    def cancel(self) -> None:
        if self.status == "shipped":
            raise ValueError("відвантажене не скасовують")
        self.status = "cancelled"
