// Заднє заповнення пакетами: багато коротких транзакцій, а не одна довга.
// Ідемпотентно й відновлювано: умова amount_minor IS NULL означає, що
// повторний запуск просто продовжить з місця, де спинилися.
async function backfill(db: Db, batch = 5000, pauseMs = 200): Promise<void> {
  const { rows } = await db.query("SELECT COALESCE(max(id), 0) AS m FROM orders");
  const maxId = Number(rows[0].m);
  for (let lo = 0; lo <= maxId; lo += batch) {
    await db.query(
      `UPDATE orders SET amount_minor = ROUND(total * 100)::BIGINT
        WHERE id >= $1 AND id < $2 AND amount_minor IS NULL`,
      [lo, lo + batch],
    );                          // кожен пакет — окрема коротка транзакція
    await new Promise((r) => setTimeout(r, pauseMs)); // віддати такт проду
  }
}
