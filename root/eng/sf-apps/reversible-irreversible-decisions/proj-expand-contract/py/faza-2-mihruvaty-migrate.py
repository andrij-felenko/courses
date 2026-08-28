import time

# Заднє заповнення пакетами: багато коротких транзакцій, а не одна довга.
# Ідемпотентно й відновлювано: умова amount_minor IS NULL означає, що
# повторний запуск просто продовжить з місця, де спинилися.
def backfill(conn, batch: int = 5000, pause: float = 0.2) -> None:
    max_id = conn.execute("SELECT max(id) FROM orders").scalar() or 0
    lo = 0
    while lo <= max_id:
        conn.execute(
            "UPDATE orders SET amount_minor = ROUND(total * 100)::BIGINT "
            "WHERE id >= %s AND id < %s AND amount_minor IS NULL",
            (lo, lo + batch),
        )
        conn.commit()          # кожен пакет — окрема коротка транзакція
        lo += batch
        time.sleep(pause)      # віддати такт проду й реплікам
