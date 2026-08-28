# test/test_http_tariff_gateway.py — точкові проби САМОГО шлюзу.
import pytest
from domain.tariff import ТарифНедоступний, ДоступПрострочено, Напрямок

# шлюз, у який передано підмінений транспорт: у мережу не піде
def шлюз_із_відповіддю(статус: int, тіло=None):
    from http.http_tariff_gateway import HttpТарифШлюз
    from http.transport import СираВідповідь
    g = HttpТарифШлюз("http://x", "tok")
    async def фейк(url, token, **_):
        async def т(): return тіло or {}
        return СираВідповідь(статус=статус, тіло=т)
    g._транспорт = фейк   # (у бойовому коді транспорт передають у конструктор)
    return g

@pytest.mark.asyncio
async def test_406_тариф_недоступний():
    g = шлюз_із_відповіддю(406)
    with pytest.raises(ТарифНедоступний):
        await g.тариф_для(Напрямок("SEG_A"))

@pytest.mark.asyncio
async def test_419_доступ_прострочено():
    g = шлюз_із_відповіддю(419)
    with pytest.raises(ДоступПрострочено):
        await g.тариф_для(Напрямок("SEG_A"))

@pytest.mark.asyncio
async def test_200_rate_bps():
    g = шлюз_із_відповіддю(200, {"rate_bps": 500})
    t = await g.тариф_для(Напрямок("SEG_A"))
    assert t.одиниць == 5   # 500 / 100 — переклад форми відпрацював
