# tests/test_place_order.py — той самий сценарій БЕЗ бази
from application.place_order import PlaceOrder, OutOfStock

class FakeRepo:                       # одна фальшивка на обидві обіцянки
    def __init__(self, catalog):
        self.catalog = dict(catalog)  # sku -> [price, stock]
        self.saved = []
    # ProductRepo
    def find(self, sku):
        row = self.catalog.get(sku)
        return (row[0], row[1]) if row else None
    # OrderRepo
    def add(self, order):
        self.saved.append(order)
        return len(self.saved)        # «id» = порядковий номер
    def reduce_stock(self, sku, qty):
        self.catalog[sku][1] -= qty

def test_places_and_reduces_stock():
    repo = FakeRepo({"A": [100.0, 5]})
    place = PlaceOrder(repo, repo)
    res = place.run([{"sku": "A", "qty": 2}], promo="VIP")

    assert res["total"] == 160.0      # 200 · 0.8
    assert repo.catalog["A"][1] == 3  # залишок зменшився 5 → 3
    assert len(repo.saved) == 1

def test_rejects_when_out_of_stock():
    repo = FakeRepo({"A": [100.0, 1]})
    place = PlaceOrder(repo, repo)
    try:
        place.run([{"sku": "A", "qty": 2}], promo=None)
        assert False, "мало впасти"
    except OutOfStock:
        pass
    assert repo.catalog["A"][1] == 1  # залишок НЕ чіпали
