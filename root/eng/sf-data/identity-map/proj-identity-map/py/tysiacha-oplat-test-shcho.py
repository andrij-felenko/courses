class FullIdentityMap(IdentityMap):
    """Мапа на сильних посиланнях — так тримає сесія Hibernate."""

    def _new_bucket(self):
        return {}


class NoIdentityMap(IdentityMap):
    """Мапа, яка нічого не пам'ятає, — так поводиться шар без карти тотожності.
    Це не вигадка: у EclipseLink такий режим є під цим самим ім'ям."""

    def get(self, cls, pk):
        return None

    def add(self, obj):
        return obj

    def values(self):
        return []

    def __len__(self):
        return 0


import sqlite3


class Db:
    """Найтонший шар над sqlite3 — і лічильники запитів, вони знадобляться."""

    def __init__(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute(
            "CREATE TABLE orders (id INTEGER PRIMARY KEY, status TEXT, discount INTEGER)")
        self.selects = self.writes = 0

    def select_one(self, table, pk):          # ім'я таблиці — з класу, не з вводу
        self.selects += 1
        return self.conn.execute(f"SELECT * FROM {table} WHERE id = ?", (pk,)).fetchone()

    def insert(self, table, pk, values):
        self.writes += 1
        cols = ", ".join(["id", *values])
        marks = ", ".join("?" * (len(values) + 1))
        self.conn.execute(f"INSERT INTO {table} ({cols}) VALUES ({marks})",
                          (pk, *values.values()))

    def update(self, table, pk, values):
        self.writes += 1
        sets = ", ".join(f"{c} = ?" for c in values)
        self.conn.execute(f"UPDATE {table} SET {sets} WHERE id = ?",
                          (*values.values(), pk))

    def delete(self, table, pk):
        self.writes += 1
        self.conn.execute(f"DELETE FROM {table} WHERE id = ?", (pk,))

    def seed(self, rows):
        self.conn.executemany(
            "INSERT INTO orders (id, status, discount) VALUES (?, 'new', 0)",
            [(i,) for i in range(1, rows + 1)])
        self.conn.commit()
        self.selects = self.writes = 0        # засів — не робота застосунку
