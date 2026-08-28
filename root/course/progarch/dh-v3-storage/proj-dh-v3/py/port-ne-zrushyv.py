from dataclasses import dataclass, field
from typing import Protocol

@dataclass(frozen=True)
class Device:                         # дитина агрегату (значення на межі сховища)
    id: str; kind: str; room: str; state: str; paired_at: str

@dataclass
class Home:                           # корінь агрегату
    id: str; owner_id: str; plan: str; device_cap: int; threshold: float
    used_slots: int = 0              # лічильник READ-ONLY для застосунку: пише його лише вартовий
    devices: list[Device] = field(default_factory=list)

class DeviceRepository(Protocol):     # ТОЙ САМИЙ порт із v2, тепер зернистістю агрегату
    def save_home(self, home: Home) -> None: ...
    def load(self, home_id: str) -> Home | None: ...
    def add_device(self, home_id: str, d: Device) -> bool: ...   # повертає False, якщо тариф вичерпано


class SqliteDeviceRepository:         # реалізація за портом DeviceRepository
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def save_home(self, home: Home) -> None:
        """Увесь агрегат — в ОДНІЙ транзакції: дім і його пристрої або разом, або ніяк."""
        self._conn.execute("BEGIN IMMEDIATE")            # межа агрегату = межа транзакції
        try:
            self._conn.execute(
                "INSERT INTO home(id, owner_id, plan, device_cap, used_slots, threshold) "
                "VALUES(?,?,?,?,?,?) "
                "ON CONFLICT(id) DO UPDATE SET "         # поклади АБО онови…
                "  plan = excluded.plan, threshold = excluded.threshold",   # …та used_slots НЕ чіпай
                (home.id, home.owner_id, home.plan, home.device_cap, len(home.devices), home.threshold))
            for d in home.devices:                        # ← збій на будь-якому витку відкотить УСЕ
                self._conn.execute(
                    "INSERT INTO device(id, home_id, kind, room, state, paired_at) "
                    "VALUES(?,?,?,?,?,?) "
                    "ON CONFLICT(id) DO UPDATE SET room = excluded.room, state = excluded.state",
                    (d.id, home.id, d.kind, d.room, d.state, d.paired_at))
            self._conn.execute("COMMIT")                  # ОДНА мить, у яку весь дім стає видимим
        except Exception:
            self._conn.execute("ROLLBACK")
            raise

    def load(self, home_id: str) -> "Home | None":
        row = self._conn.execute(
            "SELECT owner_id, plan, device_cap, used_slots, threshold FROM home WHERE id=?",
            (home_id,)).fetchone()
        if row is None:
            return None
        devs = [Device(r[0], r[1], r[2], r[3], r[4]) for r in self._conn.execute(
            "SELECT id, kind, room, state, paired_at FROM device WHERE home_id=?", (home_id,))]
        return Home(id=home_id, owner_id=row[0], plan=row[1], device_cap=row[2],
                    used_slots=row[3], threshold=row[4], devices=devs)

    def add_device(self, home_id: str, d: Device) -> bool:
        """Займає слот тарифу Й вписує пристрій — атомарно. False → тариф вичерпано."""
        self._conn.execute("BEGIN IMMEDIATE")            # замок писаря одразу — без гонки на підвищенні
        try:
            cur = self._conn.execute(
                "UPDATE home SET used_slots = used_slots + 1 "
                "WHERE id = ? AND used_slots < device_cap",   # ← вартовий: не перевищити тариф
                (home_id,))
            if cur.rowcount != 1:                         # 0 змінено → межу вже досягнуто
                self._conn.execute("ROLLBACK")
                return False
            self._conn.execute(
                "INSERT INTO device(id, home_id, kind, room, state, paired_at) VALUES(?,?,?,?,?,?)",
                (d.id, home_id, d.kind, d.room, d.state, d.paired_at))
            self._conn.execute("COMMIT")                  # слот і пристрій стають видимі РАЗОМ
            return True
        except Exception:
            self._conn.execute("ROLLBACK")
            raise
