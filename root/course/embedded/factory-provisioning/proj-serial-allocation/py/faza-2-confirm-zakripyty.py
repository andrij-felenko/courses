def confirm(db_path: str, serial: int, station: str) -> None:
    """Фаза 2: перевести зарезервований номер у 'used'. Викликати ЛИШЕ
       після успішного зашивання й звірки плати."""
    conn = sqlite3.connect(db_path, isolation_level=None)
    try:
        conn.execute("BEGIN IMMEDIATE")
        # Підтвердити можна тільки СВІЙ резерв, що ще 'reserved'. Це боронить
        # від подвійного підтвердження й від підтвердження чужого/відкоченого номера.
        cur = conn.execute("""
            UPDATE serials
               SET state = 'used', used_at = ?
             WHERE serial = ? AND state = 'reserved' AND station = ?
        """, (int(time.time()), serial, station))
        if cur.rowcount != 1:
            # Резерв уже не 'reserved' (відкочений прибиральником? чужий? уже used?).
            conn.execute("ROLLBACK")
            raise RuntimeError(f"неможливо підтвердити {serial}: резерв недійсний")
        conn.execute("COMMIT")
    finally:
        conn.close()
