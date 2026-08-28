# test_place_order.py ── СЦЕНАРІЙ-ТЕСТ. Той самий сценарій, але на підробках.
import pytest
from domain.place_order import PlaceOrder, NewOrder
from domain.order import Line
from infra.in_memory import InMemoryOrders, InMemoryNotifier


@pytest.mark.asyncio
async def test_зберігає_і_шле_рівно_одне_сповіщення():
    orders = InMemoryOrders()
    notifier = InMemoryNotifier()             # шпигун
    seq = iter("123456789")
    place_order = PlaceOrder(orders, notifier, lambda: next(seq))

    order = await place_order.run(NewOrder("kate@example.com", [Line("book", 200, 2)]))

    # ефект 1 — замовлення справді збережене, і саме те
    assert await orders.by_id("1") == order
    assert order.total() == 400

    # ефект 2 — сповіщення надіслане РІВНО раз, на пошту клієнта
    assert len(notifier.sent) == 1
    assert notifier.sent[0].email == "kate@example.com"
