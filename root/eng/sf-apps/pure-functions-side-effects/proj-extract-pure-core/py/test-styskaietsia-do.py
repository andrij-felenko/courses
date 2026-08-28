# ── Тест ЧИСТОГО ядра: увесь тест — вхід і очікуваний вихід ──────
from math import isclose

def test_totals():
    p = Pricing()   # дефолтна політика: tax 0.20, freeShip 500, ship 49

    # gold, кошик 1200 → обсяг >1000 дає 10%, gold дає 8%
    # 1200 · 0.90 · 0.92 = 993.6 ; податок ×1.20 = 1192.32
    # 993.6 ≥ 500 → доставка безкоштовна, тож total = 1192.32
    gold = Order(1, "gold", [Item(600.0, 2)])
    g = compute_totals(gold, p)
    assert isclose(g.total, 1192.32, abs_tol=1e-6)

    # regular, кошик 200 → жодної знижки, доставка платна
    # 200 ×1.20 = 240 + 49
    small = Order(2, "regular", [Item(200.0, 1)])
    assert isclose(compute_totals(small, p).total, 289.0, abs_tol=1e-6)

    # порожній кошик → усе нулі, доставка платна
    empty = Order(3, "regular", [])
    assert isclose(compute_totals(empty, p).total, 49.0, abs_tol=1e-6)
