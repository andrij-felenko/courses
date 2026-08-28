class LoggingCachingOrderService:
    def __init__(self, real: OrderService) -> None:
        self._real = real
        self._cache: dict[str, "Order"] = {}   # id → вже прочитане замовлення

    def get_order(self, id: str) -> "Order":
        if id in self._cache:
            log(f"get_order({id}) — з кешу")
            return self._cache[id]             # база не чіпається взагалі
        log(f"get_order({id}) — промах, іду в базу")
        order = self._real.get_order(id)
        self._cache[id] = order                # запам'ятали на майбутнє
        return order

    def place_order(self, order: "Order") -> str:
        log("place_order(...)")
        id = self._real.place_order(order)
        self._cache[id] = order                # свіже замовлення одразу відоме
        return id

    def cancel_order(self, id: str) -> None:
        log(f"cancel_order({id})")
        self._real.cancel_order(id)
        self._cache.pop(id, None)   # ← ІНВАЛІДАЦІЯ: кеш більше не відповідає базі
