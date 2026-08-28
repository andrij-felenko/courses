from dataclasses import dataclass

# ЗАПИТ повертає плоский тип рівно під потребу екрана — не доменний Order.
@dataclass
class OrderView:
    id: str
    customer_name: str
    total: float
    status: str

class OrderQueries:
    def __init__(self, db: Db) -> None:
        self._db = db

    # читаємо коротким шляхом; жодних правил, жодних агрегатів
    def get_order_view(self, order_id: str) -> OrderView:
        return self._db.query_one("""
            SELECT o.id, u.name AS customer_name, o.total, o.status
            FROM orders o JOIN users u ON u.id = o.user_id
            WHERE o.id = ?""", [order_id])
