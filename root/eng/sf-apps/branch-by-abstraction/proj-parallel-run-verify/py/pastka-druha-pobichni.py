from typing import Protocol, Callable

# Розчеплюємо: РІШЕННЯ (чисте, звіряємо) окремо від ДІЇ (ефект, не дублюємо)
class NotificationPlanner(Protocol):
    def plan(self, order: "Order") -> "NotificationPlan": ...   # кому, що, чи слати — чисте

class NotifyService:
    def __init__(self, planner: NotificationPlanner, send: Callable[["NotificationPlan"], None]):
        self._planner = planner   # сюди підставляємо ComparingPlanner
        self._send = send         # ефект — поза звіркою

    def notify(self, order: "Order") -> None:
        plan = self._planner.plan(order)   # тут стара й нова звіряються В ТІНІ
        self._send(plan)                    # а шлемо РІВНО РАЗ, за планом старої
