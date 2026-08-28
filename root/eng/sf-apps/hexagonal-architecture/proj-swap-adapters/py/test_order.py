# test_order.py ── ТЕСТ — це драйвер. Збирає ядро з підробленим сховищем.
import pytest
from order.service import ЗамовленняСервіс
from order.core import Позиція
from adapters.memory import ПамятьСховище   # ← той самий адаптер, що й локально


@pytest.mark.asyncio
async def test_оформлення_зберігає_і_рахує():
    # збірка «під тест»: пам'ять + детермінований id
    лічильник = iter("123456789")
    сховище = ПамятьСховище()
    сервіс = ЗамовленняСервіс(сховище, lambda: next(лічильник))

    з = await сервіс.оформити("a@b.com", [Позиція("книга", 200, 2)])

    assert з.id == "1"                       # id передбачуваний — джерело підроблене
    assert з.сума() == 400                   # правило суми спрацювало
    assert await сховище.узяти("1") == з     # адаптер справді зберіг


@pytest.mark.asyncio
async def test_порожнє_замовлення_відхиляється():
    сервіс = ЗамовленняСервіс(ПамятьСховище(), lambda: "x")
    with pytest.raises(ValueError, match="порожнє"):
        await сервіс.оформити("a@b.com", [])
