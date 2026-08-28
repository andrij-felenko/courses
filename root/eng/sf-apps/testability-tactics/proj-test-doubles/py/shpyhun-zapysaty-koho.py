class SpyNotifier:
    def __init__(self) -> None:
        self.calls: list[tuple[str, Money]] = []

    def send_confirmation(self, email: str, total: Money) -> None:
        self.calls.append((email, total))

def test_confirmation_sent() -> None:
    spy = SpyNotifier()
    place_order(
        PlaceOrderCmd("ORD-2", "olena@shop.ua", [Line("KAVA-250", 2)]),
        Deps(StubCatalog({"KAVA-250": 250}), InMemoryOrders(), spy, DummyAudit()),
    )

    # перевірка ВЗАЄМОДІЇ: рівно одне сповіщення, з тими даними
    assert len(spy.calls) == 1
    assert spy.calls[0] == ("olena@shop.ua", 500)  # 2·250
