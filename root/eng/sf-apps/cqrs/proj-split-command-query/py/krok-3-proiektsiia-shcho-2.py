import time

# проєкція-перечитувач: тягне змінене від контрольної точки й оновлює знімки
class RebuildProjection:
    def __init__(self, db: Db, read: OrderReadStore) -> None:
        self._db = db
        self._read = read
        self._since = 0.0  # контрольна точка: до цього моменту вже спроєктовано

    def tick(self) -> None:
        changed = self._db.query("""
            SELECT o.id, o.user_id, u.name AS customer_name, o.total, o.status
            FROM orders o JOIN users u ON u.id = o.user_id
            WHERE o.updated_at > ?""", [self._since])
        for r in changed:
            self._read.upsert(OrderReadModel(
                id=r.id, user_id=r.user_id, customer_name=r.customer_name,
                total=r.total, status=r.status, updated_at=time.time()))
        self._since = time.time()  # посуваємо контрольну точку вперед
