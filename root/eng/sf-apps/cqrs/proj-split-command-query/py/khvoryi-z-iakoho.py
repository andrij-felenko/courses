# ТОВСТИЙ СЕРВІС: запис і читання в одному класі, на спільній моделі.
class OrderService:
    def __init__(self, db: Db) -> None:
        self._db = db

    # --- запис: тут ЖИВУТЬ правила ---
    def place_order(self, user_id: str, items: list[LineItem]) -> str:
        order = Order.create(user_id, items)   # конструктор боронить інваріанти
        order.reserve_stock()                  # кине, якщо товару бракує
        self._db.insert("orders", order.to_row())
        for li in order.lines:
            self._db.insert("order_lines", li.to_row())
        return order.id

    def cancel_order(self, order_id: str) -> None:
        order = self._load(order_id)   # тягнемо ВЕСЬ агрегат заради одного поля статусу
        order.cancel()                 # правило: не можна скасувати відвантажене
        self._db.update("orders", order.to_row())

    # --- читання: тут правил нема, але шлях той самий, через доменну модель ---
    def get_order_view(self, order_id: str) -> OrderView:
        order = self._load(order_id)   # знову ВЕСЬ агрегат — заради показу трьох полів
        user = self._db.query_one("SELECT name FROM users WHERE id=?", [order.user_id])
        return OrderView(
            id=order.id,
            customer_name=user.name,   # склеюємо дані для екрана ПРЯМО в сервісі запису
            total=order.total(),
            status=order.status,
        )

    def list_orders(self, user_id: str) -> list[OrderView]:
        rows = self._db.query("SELECT id FROM orders WHERE user_id=?", [user_id])
        return [self.get_order_view(r.id) for r in rows]  # N+1: агрегат на кожен рядок

    def _load(self, order_id: str) -> Order:
        row = self._db.query_one("SELECT * FROM orders WHERE id=?", [order_id])
        lines = self._db.query("SELECT * FROM order_lines WHERE order_id=?", [order_id])
        return Order.from_rows(row, lines)
