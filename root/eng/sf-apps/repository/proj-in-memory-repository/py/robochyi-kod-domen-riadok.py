from __future__ import annotations
from datetime import datetime

OrderId = str
CustomerId = str


class Order:
    def __init__(self, id: OrderId, customer_id: CustomerId, total: int,
                 created_at: datetime, status: str = "new") -> None:
        self.id = id
        self.customer_id = customer_id
        self.total = total
        self.created_at = created_at
        self._status = status

    @property
    def status(self) -> str:
        return self._status

    def is_paid(self) -> bool:
        return self._status == "paid"

    def mark_paid(self) -> None:
        if self._status != "new":
            raise ValueError(f"оплатити можна лише нове замовлення, а це «{self._status}»")
        self._status = "paid"
