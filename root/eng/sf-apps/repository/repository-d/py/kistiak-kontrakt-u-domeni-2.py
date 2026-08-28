# справжня — над базою: тут дозволено знати про SQL і драйвер
class SqlOrderRepository:
    def __init__(self, db, mapper):
        self._db, self._mapper = db, mapper

    def by_id(self, id):
        row = self._db.query_one("SELECT * FROM orders WHERE id = %s", (id,))
        return self._mapper.to_domain(row) if row else None

    def for_customer(self, id):
        rows = self._db.query("SELECT * FROM orders WHERE customer_id = %s", (id,))
        return [self._mapper.to_domain(r) for r in rows]

    def save(self, o):    self._db.upsert("orders", self._mapper.to_row(o))
    def remove(self, o):  self._db.execute("DELETE FROM orders WHERE id = %s", (o.id,))

# підставна — над звичайним словником у пам'яті: жодної бази
class InMemoryOrderRepository:
    def __init__(self):
        self._store: dict[OrderId, Order] = {}

    def by_id(self, id):        return self._store.get(id)
    def for_customer(self, id): return [o for o in self._store.values() if o.customer_id == id]
    def save(self, o):          self._store[o.id] = o
    def remove(self, o):        self._store.pop(o.id, None)
