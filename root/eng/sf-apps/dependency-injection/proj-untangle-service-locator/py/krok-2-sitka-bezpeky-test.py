def fill():
    gw, log = FakeGateway(), FakeLog()
    Locator.reset()
    Locator.register("gateway", gw)
    Locator.register("clock", FakeClock())
    Locator.register("audit", log)
    Locator.register("templates", TemplateStore())
    return gw, log


def test_checkout_characterization():        # зліпок сьогоднішньої поведінки
    gw, log = fill()
    receipt = OrderService().checkout(Order("A-1", 1999))
    assert receipt == "[receipt] charge=ch_1 order=A-1"
    assert gw.charges == [1999]
    assert log.lines == ["2026-07-16T10:00:00Z order=A-1 charge=ch_1"]
