class SqliteDeviceRepository:                  # за тим самим портом DeviceRepository з v2
    def __init__(self, conn):
        self._conn = conn

    def save_home(self, home: Home) -> None:
        # увесь агрегат — в ОДНІЙ транзакції: дім і його пристрої або лягають разом, або ніяк
        with self._conn:                        # commit на виході, rollback на будь-якому винятку
            self._conn.execute(
                "INSERT INTO home(id, owner_id, plan, device_cap, threshold) VALUES(?,?,?,?,?) "
                "ON CONFLICT(id) DO UPDATE SET plan=excluded.plan, threshold=excluded.threshold",
                (home.id, home.owner_id, home.plan, home.device_cap, home.threshold))
            for d in home.devices:
                self._conn.execute(
                    "INSERT INTO device(id, home_id, kind, room, state, paired_at) VALUES(?,?,?,?,?,?) "
                    "ON CONFLICT(id) DO UPDATE SET room=excluded.room, state=excluded.state",
                    (d.id, home.id, d.kind, d.room, d.state, d.paired_at))
