from typing import Protocol

class OrderService(Protocol):
    def get_order(self, id: str) -> "Order": ...        # читання: часте, безпечне, кешується
    def place_order(self, order: "Order") -> str: ...   # запис: треба право
    def cancel_order(self, id: str) -> None: ...        # запис: треба право (вище)

# Справжній сервіс: ходить у базу, нічого не знає про права й кеш.
class RealOrderService:
    def get_order(self, id: str) -> "Order":
        return db.query("SELECT ... WHERE id = ?", id)   # дорогий похід у базу

    def place_order(self, order: "Order") -> str:
        return db.insert(order)

    def cancel_order(self, id: str) -> None:
        db.update("UPDATE orders SET state='cancelled' WHERE id = ?", id)
