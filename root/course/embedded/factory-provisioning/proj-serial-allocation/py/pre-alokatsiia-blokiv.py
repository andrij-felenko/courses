def allocate_block(db_path: str, station: str, size: int = 1000) -> tuple[int, int]:
    """Видати станції неперетинний блок із 'size' номерів. Повертає (lo, hi).
       Наступний блок починається одразу за виданим — блоки НЕ перетинаються."""
    conn = sqlite3.connect(db_path, isolation_level=None)
    try:
        conn.execute("BEGIN IMMEDIATE")   # знову: замок одразу, блоки не роздвояться
        # next_block — курсор 'докуди роздано'. Читаємо й пересуваємо атомарно.
        row = conn.execute("SELECT value FROM counters WHERE name='next_block'").fetchone()
        lo = row[0]
        hi = lo + size - 1
        conn.execute("UPDATE counters SET value=? WHERE name='next_block'", (hi + 1,))
        conn.execute("INSERT INTO blocks(station, lo, hi, issued_at) VALUES (?,?,?,?)",
                     (station, lo, hi, int(time.time())))
        conn.execute("COMMIT")
        return (lo, hi)
    finally:
        conn.close()
