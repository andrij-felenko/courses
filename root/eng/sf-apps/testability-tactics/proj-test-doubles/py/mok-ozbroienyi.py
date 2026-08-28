class MockNotifier:
    def __init__(self) -> None:
        self._expected: "tuple[str, Money] | None" = None
        self._actual:   "tuple[str, Money] | None" = None

    def expect_confirmation(self, email: str, total: Money) -> None:
        self._expected = (email, total)            # очікування — НАПЕРЕД

    def send_confirmation(self, email: str, total: Money) -> None:
        if self._actual is not None:
            raise AssertionError("сповіщення надіслано двічі")  # падає одразу
        self._actual = (email, total)

    def verify(self) -> None:                       # мок звіряє себе сам
        assert self._actual == self._expected, \
            f"очікували {self._expected}, дістали {self._actual}"

def test_confirmation_mock() -> None:
    mock = MockNotifier()
    mock.expect_confirmation("olena@shop.ua", 500)  # ← спершу озброюємо
    place_order(
        PlaceOrderCmd("ORD-3", "olena@shop.ua", [Line("KAVA-250", 2)]),
        Deps(StubCatalog({"KAVA-250": 250}), InMemoryOrders(), mock, DummyAudit()),
    )
    mock.verify()                                   # ← мок сам виносить вирок
