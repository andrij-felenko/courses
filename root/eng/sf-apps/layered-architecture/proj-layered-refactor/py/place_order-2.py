# application/place_order.py — сценарій під однією транзакцією
from contextlib import contextmanager

class SqlUnitOfWork:
    def __init__(self, conn): self.conn = conn
    @contextmanager
    def atomic(self):
        try:
            yield
            self.conn.commit()        # усе вдалось — фіксуємо
        except Exception:
            self.conn.rollback()      # хоч щось впало — відкат
            raise

class PlaceOrder:
    def __init__(self, products, orders, uow: SqlUnitOfWork):
        self.products, self.orders, self.uow = products, orders, uow
    def run(self, raw_items, promo):
        # ... збір lines і перевірки як раніше ...
        with self.uow.atomic():       # межу транзакції відкриває застосунок
            order_id = self.orders.add(order)
            for l in lines:
                self.orders.reduce_stock(l.sku, l.qty)
        return {"order_id": order_id, "total": order.total()}
