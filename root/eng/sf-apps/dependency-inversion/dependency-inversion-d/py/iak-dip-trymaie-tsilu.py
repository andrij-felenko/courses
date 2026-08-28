from typing import Protocol, Optional

class Orders(Protocol):                          # репозиторій як абстракція домену
    async def save(self, order: "Order") -> None: ...
    async def by_id(self, id: "OrderId") -> Optional["Order"]: ...

class PlaceOrder:                                # сценарій-політика
    def __init__(self, orders: Orders):
        self._orders = orders

    async def run(self, cmd: "NewOrder") -> None:
        order = Order.create(cmd)
        await self._orders.save(order)           # знає лише обіцянку домену
