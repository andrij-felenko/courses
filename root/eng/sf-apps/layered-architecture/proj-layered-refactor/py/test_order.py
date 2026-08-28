# tests/test_order.py — правило перевіряється за мілісекунди
from domain.order import Order, Line, Promo

def test_vip_discount():
    order = Order([Line("A", 2, 100.0)], promo=Promo.VIP)
    assert order.total() == 160.0     # 200 · 0.8

def test_no_promo():
    order = Order([Line("A", 1, 33.3), Line("B", 3, 10.0)], Promo.NONE)
    assert order.total() == 63.3
