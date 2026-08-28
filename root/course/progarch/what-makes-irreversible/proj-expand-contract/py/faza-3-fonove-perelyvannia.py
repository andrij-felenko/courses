import time

BATCH = 5000

def backfill(conn, replica_lag_seconds) -> None:
    last_id = 0
    while True:
        with conn.cursor() as cur:
            # Порція ще не перелитих рядків за зростанням id (keyset-пагінація).
            # WHERE temp_mc IS NULL — не чіпаємо те, що вже наповнив живий трафік:
            # свіже значення не можна перетерти старою копією.
            cur.execute(
                "SELECT id, temp_c FROM readings "
                "WHERE id > %s AND temp_mc IS NULL "
                "ORDER BY id LIMIT %s",
                (last_id, BATCH),
            )
            rows = cur.fetchall()
            if not rows:
                break                                    # усе перелито — кінець
            cur.executemany(
                "UPDATE readings SET temp_mc = %s "
                "WHERE id = %s AND temp_mc IS NULL",      # ідемпотентно
                [(to_milli_c(t), rid) for rid, t in rows],
            )
        conn.commit()                                    # КОЖНА порція — своя транзакція
        last_id = rows[-1][0]                            # звідки продовжити після рестарту

        # ТРОТЛІНГ: не женемо базу на межу.
        while replica_lag_seconds() > 5.0:               # репліка відстала — чекаємо
            time.sleep(1.0)
        time.sleep(BATCH / 20_000)                       # темп ≈ 20 000 рядків/с
