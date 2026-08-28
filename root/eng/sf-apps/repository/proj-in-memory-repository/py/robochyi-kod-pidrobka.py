class InMemoryOrderRepository:
    def __init__(self) -> None:
        self._rows: dict[OrderId, OrderRow] = {}           # РЯДКИ, не Order

    def by_id(self, id: OrderId) -> Optional[Order]:
        row = self._rows.get(id)
        return to_domain(row) if row is not None else None  # щоразу новий об'єкт

    def recent_paid_orders(self, customer_id: CustomerId, limit: int) -> list[Order]:
        rows = [r for r in self._rows.values()                        # WHERE
                if r.customer_id == customer_id and r.status == "paid"]
        rows.sort(key=lambda r: (datetime.fromisoformat(r.created_at), r.id),
                  reverse=True)                                       # ORDER BY … DESC
        return [to_domain(r) for r in rows[:limit]]                   # LIMIT

    def save(self, order: Order) -> None:
        self._rows[order.id] = to_row(order)               # знімок, не посилання

    def remove(self, order: Order) -> None:
        self._rows.pop(order.id, None)
