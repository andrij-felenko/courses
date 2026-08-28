# ── ДОМЕН: правило + обіцянка сховища (жодного слова про SQL) ──
from dataclasses import dataclass
from typing import Protocol

@dataclass
class Order:
    items: list[tuple[str, int, float]]  # назва, к-сть, ціна
    def total(self) -> float:            # правило предметної області
        return sum(qty * price for _, qty, price in self.items)

class OrderRepo(Protocol):               # обіцянка, а не реалізація
    def save(self, order: Order) -> int: ...

# ── ІНФРАСТРУКТУРА: виконує обіцянку (залежить від домену, не навпаки) ──
class SqlOrderRepo:
    def __init__(self, conn): self.conn = conn
    def save(self, order: Order) -> int:
        return self.conn.execute("INSERT INTO orders(total) VALUES (?)",
                                 (order.total(),)).lastrowid

# ── ЗАСТОСУНОК: диригує кроками, дістає repo ззовні ──
class PlaceOrder:
    def __init__(self, repo: OrderRepo):  # бачить лише обіцянку
        self.repo = repo
    def run(self, order: Order) -> int:
        if not order.items:
            raise ValueError("порожнє замовлення")
        return self.repo.save(order)
