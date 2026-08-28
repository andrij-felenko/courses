# application/place_order.py — сценарій; бачить лише інтерфейси домену
from domain.order import Order, Line, Promo
from domain.repos import ProductRepo, OrderRepo

class OutOfStock(Exception): ...
class UnknownProduct(Exception): ...

class PlaceOrder:
    def __init__(self, products: ProductRepo, orders: OrderRepo):
        self.products = products      # обіцянки, не драйвери
        self.orders = orders

    def run(self, raw_items: list[dict], promo: str | None) -> dict:
        lines = []
        for it in raw_items:
            found = self.products.find(it["sku"])
            if found is None:
                raise UnknownProduct(it["sku"])
            price, stock = found
            if stock < it["qty"]:
                raise OutOfStock(it["sku"])
            lines.append(Line(it["sku"], it["qty"], price))

        order = Order(lines, Promo[promo] if promo else Promo.NONE)
        order_id = self.orders.add(order)
        for l in lines:
            self.orders.reduce_stock(l.sku, l.qty)
        return {"order_id": order_id, "total": order.total()}
