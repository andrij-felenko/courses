# test/stub_tariff_gateway.py — підробка: той самий інтерфейс, без мережі.
import pytest
from domain.tariff_gateway import ТарифШлюз
from domain.tariff import Напрямок, Тариф
from domain.доставка_сервіс import ДоставкаСервіс

class StubТарифШлюз(ТарифШлюз):
    def __init__(self, фіксований: Тариф):
        self._тариф = фіксований
    async def тариф_для(self, напрямок: Напрямок) -> Тариф:
        return self._тариф        # жодного HTTP — просто віддали, що просили

# Тест НАШОГО правила — без сервера, без мережі, за мілісекунди
@pytest.mark.asyncio
async def test_дорого_самовивіз():
    домен = ДоставкаСервіс(StubТарифШлюз(Тариф(500)))    # дорого
    assert await домен.порадити_спосіб(Напрямок("SEG_A")) == "самовивіз"

@pytest.mark.asyncio
async def test_дешево_доставка():
    домен = ДоставкаСервіс(StubТарифШлюз(Тариф(50)))     # дешево
    assert await домен.порадити_спосіб(Напрямок("SEG_A")) == "доставка"
