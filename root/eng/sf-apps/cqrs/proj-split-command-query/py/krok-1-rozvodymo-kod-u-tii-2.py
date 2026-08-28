from dataclasses import dataclass

# --- БІК ЗАПИТІВ: плоскі типи під екран, читання повз доменну модель ---
@dataclass
class OrderView:
    id: str
    customer_name: str
    total: float
    status: str

class OrderQueries:
    def __init__(self, db: Db) -> None:
        self._db = db

    def get_order_view(self, order_id: str) -> OrderView:
        return self._db.query_one("""
            SELECT o.id, u.name AS customer_name, o.total, o.status
            FROM orders o JOIN users u ON u.id = o.user_id
            WHERE o.id = ?""", [order_id])

    # список — ОДИН запит із JOIN, а не агрегат на кожен рядок
    def list_orders(self, user_id: str) -> list[OrderView]:
        return self._db.query("""
            SELECT o.id, u.name AS customer_name, o.total, o.status
            FROM orders o JOIN users u ON u.id = o.user_id
            WHERE o.user_id = ?
            ORDER BY o.created_at DESC""", [user_id])
