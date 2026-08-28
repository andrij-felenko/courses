# infra/in_memory.py ── адаптери БЕЗ інфраструктури. Реалізують ті самі порти.
from typing import Optional
from domain.order import Order


class InMemoryOrders:                 # структурно задовольняє Orders (Protocol)
    def __init__(self) -> None:
        self._by_key: dict[str, Order] = {}

    async def save(self, o: Order) -> None:
        self._by_key[o.id] = o

    async def by_id(self, id: str) -> Optional[Order]:
        return self._by_key.get(id)


class InMemoryNotifier:               # шпигун: ЗАПИСУЄ, кого сповістили
    def __init__(self) -> None:
        self.sent: list[Order] = []

    async def order_placed(self, o: Order) -> None:
        self.sent.append(o)
