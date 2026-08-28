@pytest.mark.asyncio
async def test_недійсне_не_зберігається_і_не_шле():
    orders = InMemoryOrders()
    notifier = InMemoryNotifier()
    place_order = PlaceOrder(orders, notifier, lambda: "x")

    with pytest.raises(Exception):
        await place_order.run(NewOrder("no-at-sign", []))   # правило відхилило

    assert await orders.by_id("x") is None    # нічого не збережено
    assert notifier.sent == []                # нікого не сповіщено
