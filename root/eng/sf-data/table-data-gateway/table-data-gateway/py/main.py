# Таблиця: orders(id INTEGER PRIMARY KEY, customer_id TEXT, total REAL, status TEXT)

# Один об'єкт на всю таблицю. Тут — увесь SQL до orders і жодного правила.
class OrderTableGateway:
    # пошук: методи беруть КЛЮЧ/КРИТЕРІЙ і повертають сирі рядки (record set)
    def find(self, id):
        return db.execute("SELECT * FROM orders WHERE id = ?", (id,)).fetchone()

    def find_by_status(self, status):
        return db.execute("SELECT * FROM orders WHERE status = ?", (status,)).fetchall()

    # зміни: теж за ключем, для будь-якого рядка таблиці
    def insert(self, customer_id, total, status):
        cur = db.execute(
            "INSERT INTO orders (customer_id, total, status) VALUES (?, ?, ?)",
            (customer_id, total, status),
        )
        return cur.lastrowid

    def update(self, id, total, status):
        db.execute("UPDATE orders SET total = ?, status = ? WHERE id = ?", (total, status, id))

    def delete(self, id):
        db.execute("DELETE FROM orders WHERE id = ?", (id,))


# Виклик: правило живе ЗОВНІ, шлюз лише віддає й приймає рядки.
gw = OrderTableGateway()
for row in gw.find_by_status("paid"):
    if row["total"] > 1000:
        gw.update(row["id"], row["total"], "review")
