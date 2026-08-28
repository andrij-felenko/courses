# Підроблені джерела: курс і день задаємо ми — вхід під повним контролем.
class FakeRate:
    def rate(self) -> float: return 40.0

class SatClock:
    def is_weekend(self) -> bool: return True

def test_weekend_surcharge():
    order = Order(amount=100.0)
    got = order_total(order, FakeRate(), SatClock())
    # 100 · 40 = 4000, вихідний → ×1.05 = 4200. Точне, відтворюване число.
    assert abs(got - 4200.0) < 1e-9
