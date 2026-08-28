from typing import Optional, Protocol


class OrderRepository(Protocol):
    def by_id(self, id: OrderId) -> Optional[Order]: ...

    def recent_paid_orders(self, customer_id: CustomerId, limit: int) -> list[Order]:
        """Оплачені замовлення клієнта: найновіші перші, не більше за limit.
        За однакового часу — старшим вважається більший id."""
        ...

    def save(self, order: Order) -> None: ...
    def remove(self, order: Order) -> None: ...


class LoyaltyService:
    def __init__(self, orders: OrderRepository) -> None:
        self._orders = orders

    def is_loyal(self, customer_id: CustomerId) -> bool:
        recent = self._orders.recent_paid_orders(customer_id, 3)
        return len(recent) == 3 and all(o.total > 500 for o in recent)
