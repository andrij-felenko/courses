# ✅ Правильно: дані замовлення — у контексті, стан лишається спільним і чистим
class Order:
    def __init__(self, id: str) -> None:
        self._state: OrderState = States.NEW
        self.paid_at = None            # ← поле замовлення, не стану
        # ...

class PaidState(OrderState):
    name = "Paid"
    def ship(self, order: "Order") -> None:
        if order.paid_at is None:
            order.paid_at = datetime.now()   # ← пишемо в КОНКРЕТНЕ замовлення
        order.transition_to(States.SHIPPED)
