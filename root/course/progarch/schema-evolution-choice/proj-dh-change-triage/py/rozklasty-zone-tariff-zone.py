BATCH = 5_000

def backfill_tariff_zone(conn) -> None:
    last_id = 0
    while True:
        cur = conn.execute("""
            WITH batch AS (
                SELECT id FROM home
                WHERE id > %s AND tariff_zone IS NULL
                ORDER BY id
                LIMIT %s
            )
            UPDATE home h
            SET tariff_zone = zone_to_code(h.zone)
            FROM batch
            WHERE h.id = batch.id
            RETURNING h.id
        """, (last_id, BATCH))
        ids = [r[0] for r in cur.fetchall()]
        conn.commit()             # ← лок відпускається ЩОБАТЧУ, не в кінці всього
        if not ids:               # NULL-рядків більше нема — усе
            break
        last_id = max(ids)        # keyset-курсор: наступний батч продовжує з місця
        time.sleep(0.05)          # крапля між батчами: вакуум і реплікація дихають
