# domain/доставка_сервіс.py — НАШЕ правило. Кличе шлюз через ІНТЕРФЕЙС.
from domain.tariff_gateway import ТарифШлюз
from domain.tariff import Напрямок

class ДоставкаСервіс:
    def __init__(self, шлюз: ТарифШлюз, поріг: float = 300):
        self._шлюз = шлюз
        self._поріг = поріг

    async def порадити_спосіб(self, напрямок: Напрямок) -> str:
        тариф = await self._шлюз.тариф_для(напрямок)   # не знає, ХТО по той бік
        return "самовивіз" if тариф.дорожчий_за(self._поріг) else "доставка"
