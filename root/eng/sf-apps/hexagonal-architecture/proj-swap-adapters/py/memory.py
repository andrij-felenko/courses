# adapters/memory.py ── ДРАЙВОВАНИЙ АДАПТЕР. Той самий порт, але в пам'яті.
from order.core import ЗамовленняСховище, Замовлення


class ПамятьСховище(ЗамовленняСховище):
    def __init__(self):
        self._дані: dict[str, Замовлення] = {}

    async def зберегти(self, з: Замовлення) -> None:
        self._дані[з.id] = з           # усе «сховище» — один словник

    async def узяти(self, id: str) -> Замовлення | None:
        return self._дані.get(id)
