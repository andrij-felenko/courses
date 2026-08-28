import sqlite3

class SqliteDeviceRepository:                      # ТОЙ САМИЙ порт DeviceRepository
    def __init__(self, path: str = "dh.db"):
        self._db = sqlite3.connect(path)
        self._db.execute("PRAGMA journal_mode=WAL")   # читачі не блокують писаря
        self._db.execute("""
            CREATE TABLE IF NOT EXISTS devices (
                id    TEXT PRIMARY KEY,             # ключ реєстру — на рівні схеми
                kind  TEXT NOT NULL,
                room  TEXT NOT NULL,
                state TEXT NOT NULL
            )""")
        self._db.commit()

    def save(self, d: Device) -> None:
        self._db.execute(
            "INSERT INTO devices (id, kind, room, state) VALUES (?, ?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET "        # поклади АБО онови за id — одним рухом
            "  kind=excluded.kind, room=excluded.room, state=excluded.state",
            (d.id, d.kind, d.room, d.state))
        self._db.commit()                          # ← межа тривкості: тут база робить fsync

    def get(self, id: str) -> Device | None:
        row = self._db.execute(
            "SELECT id, kind, room, state FROM devices WHERE id = ?", (id,)
        ).fetchone()                               # частковий пошук: один рядок за ключем
        return Device(*row) if row else None

    def all(self) -> list[Device]:
        rows = self._db.execute(
            "SELECT id, kind, room, state FROM devices").fetchall()
        return [Device(*r) for r in rows]
