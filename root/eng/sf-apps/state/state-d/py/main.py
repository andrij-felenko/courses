from __future__ import annotations
from typing import Protocol

class OrderState(Protocol):
    def pay(self, order: "Order") -> None: ...
    def ship(self, order: "Order") -> None: ...

class NewState:
    def pay(self, order: "Order") -> None:
        # ...провести оплату...
        order.set_state(PaidState())     # стан САМ переводить власника далі
    def ship(self, order: "Order") -> None:
        raise RuntimeError("спершу оплатіть")  # у цьому стані відправляти не можна

class PaidState:
    def pay(self, order: "Order") -> None:
        raise RuntimeError("уже оплачено")
    def ship(self, order: "Order") -> None:
        # ...відвантажити...
        order.set_state(ShippedState())

class ShippedState:
    def pay(self, order: "Order") -> None:
        raise RuntimeError("надто пізно")
    def ship(self, order: "Order") -> None:
        raise RuntimeError("уже відправлено")
