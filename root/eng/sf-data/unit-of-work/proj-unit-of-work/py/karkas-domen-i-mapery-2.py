class CustomerMapper:
    entity = Customer
    depends_on = ()                                     # ні на кого не вказує

    def load(self, id, cur):
        row = cur.execute("SELECT id, name, points FROM customer WHERE id=?",
                          (id,)).fetchone()
        if row is None: return None
        o = Customer(row[1], row[2]); o.id = row[0]; return o

    def insert(self, o, cur):
        cur.execute("INSERT INTO customer(name, points) VALUES (?, ?)",
                    (o.name, o.points))
        o.id = cur.lastrowid                            # база призначила ключ
    def update(self, o, cur):
        cur.execute("UPDATE customer SET name=?, points=? WHERE id=?",
                    (o.name, o.points, o.id))
    def delete(self, o, cur):
        cur.execute("DELETE FROM customer WHERE id=?", (o.id,))
    def fields(self, o):
        return {"name": o.name, "points": o.points}

class OrderMapper:
    entity = Order
    depends_on = (Customer,)                            # order.customer → потрібен спершу

    def load(self, id, cur):
        row = cur.execute('SELECT id, customer_id, total FROM "order" WHERE id=?',
                          (id,)).fetchone()
        if row is None: return None
        o = Order.__new__(Order); o.id = row[0]
        o.customer = None; o.total = row[2]; return o   # клієнта підтягне окремо
    def insert(self, o, cur):
        cur.execute('INSERT INTO "order"(customer_id, total) VALUES (?, ?)',
                    (o.customer.id, o.total))            # ЧИТАЄ o.customer.id — має вже бути!
        o.id = cur.lastrowid
    def update(self, o, cur):
        cur.execute('UPDATE "order" SET total=? WHERE id=?', (o.total, o.id))
    def delete(self, o, cur):
        cur.execute('DELETE FROM "order" WHERE id=?', (o.id,))
    def fields(self, o):
        return {"customer_id": o.customer.id if o.customer else None, "total": o.total}
