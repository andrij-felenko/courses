def rollback_stale(db_path: str, max_age_s: int = 3600) -> int:
    """Відкотити резерви, що висять 'reserved' довше за max_age_s.
       Завислий номер стає 'skipped' (пропуск), а НЕ 'free' — щоб він
       не дістався другій платі, якщо перша вже могла бути зашита ним.
       Повертає, скільки номерів відкочено."""
    conn = sqlite3.connect(db_path, isolation_level=None)
    try:
        conn.execute("BEGIN IMMEDIATE")
        cutoff = int(time.time()) - max_age_s
        cur = conn.execute("""
            UPDATE serials
               SET state = 'skipped', station = NULL
             WHERE state = 'reserved' AND reserved_at < ?
        """, (cutoff,))
        n = cur.rowcount
        conn.execute("COMMIT")
        return n
    finally:
        conn.close()
