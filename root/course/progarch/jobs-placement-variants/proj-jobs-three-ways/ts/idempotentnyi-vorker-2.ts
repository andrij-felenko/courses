test("воркер ідемпотентний: та сама задача двічі — перекодування одне", async () => {
  const clipId = await insertClip(pool, "s3://clips/raw/42.mov");
  let encodes = 0;
  const encode: Encode = async () => { encodes++; return `s3://clips/out/${clipId}.mp4`; };

  await transcode(pool, clipId, encode);   // перша доставка
  await transcode(pool, clipId, encode);   // ДУБЛЬ (жнець повернув, relay доправив двічі — байдуже)

  expect(encodes).toBe(1);                 // кодек смикнувся РІВНО раз
  const r = await pool.query(
    "SELECT count(*) FROM renditions WHERE clip_id = $1", [clipId]);
  expect(Number(r.rows[0].count)).toBe(1); // один результат, не два
});
