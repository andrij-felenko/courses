# adapters/http.py ── ДРАЙВЕР-АДАПТЕР. Залежить від ПОРТУ, не від сервісу.
from order.core import ОформленняЗамовлення


class ЗамовленняHttp:
    def __init__(self, застосунок: ОформленняЗамовлення):  # ← порт, не клас
        self._застосунок = застосунок

    async def post(self, req):
        try:
            з = await self._застосунок.оформити(req.json["пошта"], req.json["позиції"])
            return {"id": з.id, "сума": з.сума()}, 201       # домен → HTTP
        except ValueError as e:
            return {"помилка": str(e)}, 400
