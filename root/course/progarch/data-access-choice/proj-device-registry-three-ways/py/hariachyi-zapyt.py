class SqliteDeviceRepository:
    # ... save, find, _to_device — як вище ...
    def find_silent_over(self, minutes: int) -> list[Device]:
        rows = self.conn.execute("""
            SELECT d.id, d.type, d.room, d.state, d.last_seen
            FROM devices d
            LEFT JOIN (
                SELECT device_id, MAX(at) AS last_at
                FROM telemetry GROUP BY device_id
            ) t ON t.device_id = d.id
            WHERE t.last_at IS NULL
               OR t.last_at < CAST(strftime('%s','now') AS INTEGER) - ? * 60
        """, (minutes,)).fetchall()
        return [self._to_device(r) for r in rows]     # один запит — і збірка руками
