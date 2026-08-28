import sqlite3

class SqliteStore:
    def __init__(self) -> None:
        self._db = sqlite3.connect(":memory:")
        # стовпець at — INTEGER: сховище тримає ЦІЛІ мілісекунди
        self._db.execute("CREATE TABLE readings (at INTEGER NOT NULL, celsius REAL NOT NULL)")
    def save(self, r: Reading) -> None:
        self._db.execute("INSERT INTO readings (at, celsius) VALUES (?, ?)",
                         (round(r.at), r.celsius))   # округлюємо на вході — стовпець цілий
    def recent(self, limit: int) -> list[Reading]:
        rows = self._db.execute(
            "SELECT at, celsius FROM readings ORDER BY at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [Reading(at, celsius) for at, celsius in rows]
