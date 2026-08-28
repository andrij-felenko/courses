from typing import Protocol, Optional

# контракт — біля домену; названий доменною мовою, не мовою таблиць
class OrderRepository(Protocol):
    def by_id(self, id: OrderId) -> Optional[Order]: ...
    def for_customer(self, id: CustomerId) -> list[Order]: ...
    def save(self, order: Order) -> None: ...
    def remove(self, order: Order) -> None: ...

# сервіс залежить ЛИШЕ від контракту — жодного натяку на сховище
class LoyaltyService:
    def __init__(self, orders: OrderRepository):
        self._orders = orders

    def is_loyal(self, customer_id: CustomerId) -> bool:
        paid = [o for o in self._orders.for_customer(customer_id) if o.is_paid()]
        return len(paid) >= 3 and all(o.total > 500 for o in paid)
