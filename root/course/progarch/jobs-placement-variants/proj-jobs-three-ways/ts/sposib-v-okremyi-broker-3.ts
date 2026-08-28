test("outbox доправляє задачу, навіть коли relay спершу падає", async () => {
  const broker = new FakeBroker();
  const url = "s3://clips/raw/8.mov";
  await uploadClipOutbox(pool, 7, url);            // кліп + рядок outbox — одна транзакція

  broker.failNext();                               // перша спроба relay падає — ТА САМА мить збою
  await expect(relayOnce(pool, broker)).rejects.toThrow();
  expect(broker.delivered).toHaveLength(0);        // ще нічого не доправлено...

  // ...але намір ЦІЛИЙ в outbox, тож повторний прогін relay доводить справу:
  await relayOnce(pool, broker);                   // брокер ожив
  expect(broker.delivered).toEqual([
    { topic: "transcode", payload: { clipId: expect.any(Number) } },
  ]);
  const stuck = await pool.query(
    "SELECT count(*) FROM outbox WHERE delivered_at IS NULL");
  expect(Number(stuck.rows[0].count)).toBe(0);     // жодної сироти не лишилось
});
