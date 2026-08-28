test("наївний подвійний запис сиротить кліп, коли enqueue падає", async () => {
  const broker = new FakeBroker();
  broker.failNext();                               // брокер на мить ліг — рівно на нашому enqueue
  const url = "s3://clips/raw/7.mov";

  await expect(uploadClipNaive(pool, broker, 7, url)).rejects.toThrow();

  // Кліп ЗАфіксувався (перший запит пройшов і закомітився сам собою)...
  const clip = await pool.query("SELECT id FROM clips WHERE url = $1", [url]);
  expect(clip.rowCount).toBe(1);                   // кліп ІСНУЄ
  // ...а задача НЕ доправлена. Осиротілий кліп, нуль сліду.
  expect(broker.delivered).toHaveLength(0);        // борг зник — і ніхто не знає
});
