# domain/order.py — правила предметної області, і більш нічого
from dataclasses import dataclass
from enum import Enum

class Promo(Enum):
    NONE = 1.0
    SPRING = 0.9
    VIP = 0.8

@dataclass(frozen=True)
class Line:
    sku: str
    qty: int
    price: float          # ціну домен отримує ззовні, сам її не шукає

@dataclass
class Order:
    lines: list[Line]
    promo: Promo = Promo.NONE

    def total(self) -> float:
        raw = sum(l.price * l.qty for l in self.lines)
        return round(raw * self.promo.value, 2)
