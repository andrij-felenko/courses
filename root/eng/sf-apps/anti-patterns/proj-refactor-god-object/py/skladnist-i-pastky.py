def test_service_calls_in_order():
    seen = []
    class V: check = lambda s, c: seen.append("check")
    class P: total = lambda s, c, u: (seen.append("total"), 100)[1]
    class R: save = lambda s, u, t: seen.append("save")
    class N: order_placed = lambda s, u, t: seen.append("notify")

    OrderService(V(), P(), R(), N()).place_order(
        Cart([Item("Кава", price_cents=1999, qty=1)]), User(42, "vip@x", True))
    assert seen == ["check", "total", "save", "notify"]
