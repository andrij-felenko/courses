import sqlite3

class SqliteDeviceRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, d: Device) -> None:
        cur = self.conn.execute(
            "INSERT INTO devices (type, room, state, last_seen) VALUES (?,?,?,?)",
            (d.type, d.room, d.state, d.last_seen))
        d.id = cur.lastrowid            # новий id — назад в об'єкт
        self.conn.commit()

    def find(self, id: int) -> Device | None:
        row = self.conn.execute(
            "SELECT id, type, room, state, last_seen FROM devices WHERE id=?",
            (id,)).fetchone()
        return self._to_device(row) if row else None

    def _to_device(self, row) -> Device:            # збірка об'єкта з рядка — РУКАМИ
        id_, type_, room, state, last_seen = row
        return Device(type_, room, state, last_seen, id=id_)
