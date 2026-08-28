# domain/place_order.py ── СЦЕНАРІЙ. Диригує двома портами, не знає адаптерів.
from collections.abc import Callable
from dataclasses import dataclass
from .order import Order, Line
from .ports import Orders, Notifier


@dataclass(frozen=True)
class NewOrder:
    email: str
    lines: list[Line]


class PlaceOrder:
    def __init__(self, orders: Orders, notifier: Notifier, new_id: Callable[[], str]):
        self._orders = orders        # ← порт, НЕ база
        self._notifier = notifier    # ← порт, НЕ SMTP
        self._new_id = new_id        # джерело id теж ззовні

    async def run(self, cmd: NewOrder) -> Order:
        order = Order.place(self._new_id(), cmd.email, cmd.lines)  # 1: правила
        await self._orders.save(order)             # 2: спершу зберегти
        await self._notifier.order_placed(order)   # 3: тоді сповістити
        return order
