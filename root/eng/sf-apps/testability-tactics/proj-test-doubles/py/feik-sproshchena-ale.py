def test_total_and_persisted() -> None:
    catalog = StubCatalog({"KAVA-250": 250, "CUKOR-1": 90})  # заглушка
    repo = InMemoryOrders()                                  # фейк
    spy = SpyNotifier()                                      # тут байдужий
    cmd = PlaceOrderCmd(
        order_id="ORD-1", email="olena@shop.ua",
        items=[Line("KAVA-250", 2), Line("CUKOR-1", 1)],
    )

    order = place_order(cmd, Deps(catalog, repo, spy, DummyAudit()))

    # перевірка СТАНУ: сума порахована й замовлення справді збережене
    assert order.total == 590             # 2·250 + 1·90 = 590
    assert repo.find("ORD-1") == order    # фейк повертає те, що поклали
