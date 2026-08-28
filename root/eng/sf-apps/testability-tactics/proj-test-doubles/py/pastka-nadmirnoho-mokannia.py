def test_place_order_fragile() -> None:
    seq: list[str] = []

    class Rec:
        def price_of(self, s: str) -> Money: seq.append(f"price:{s}"); return 250
        def save(self, o: Order) -> None: seq.append("save")
        def find(self, i: str) -> "Order | None": return None
        def send_confirmation(self, e: str, t: Money) -> None: seq.append("notify")
        def record(self, e: str, i: str) -> None: seq.append("audit")

    r = Rec()
    place_order(
        PlaceOrderCmd("ORD-4", "o@x", [Line("KAVA-250", 2)]),
        Deps(r, r, r, r),
    )

    # припущення про ТОЧНУ структуру, а не про поведінку:
    assert seq == ["price:KAVA-250", "save", "notify", "audit"]
