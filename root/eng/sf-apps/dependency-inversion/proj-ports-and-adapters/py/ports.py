# domain/ports.py ── ДВІ обіцянки домену, його поняттями. Ні SQL, ні SMTP.
from typing import Optional, Protocol
from .order import Order


class Orders(Protocol):                        # вихідний порт №1: КУДИ складати
    async def save(self, order: Order) -> None: ...
    async def by_id(self, id: str) -> Optional[Order]: ...


class Notifier(Protocol):                      # вихідний порт №2: ЯК сповістити
    async def order_placed(self, order: Order) -> None: ...
