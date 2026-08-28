// CDC-обробник: пачку нових reading згортаємо локально й доливаємо
// ОДНИМ upsert на (home, day) — замість одного на кожен вимір.
async function onReadingBatch(rows: Reading[]): Promise<void> {
  const bucket = new Map<string, { home: number; day: string; wh: number; n: number }>();
  for (const r of rows) {                          // згорнути пачку в пам'яті
    const day = kyivDay(r.ts);                      // той самий київський день
    const k = `${r.home_id}|${day}`;
    const b = bucket.get(k) ?? { home: r.home_id, day, wh: 0, n: 0 };
    b.wh += r.wh; b.n += 1;
    bucket.set(k, b);
  }
  for (const b of bucket.values()) {               // один долив на партицію
    await db.query(
      `INSERT INTO daily_energy (home_id, day, wh_sum, n_readings, computed_at)
       VALUES ($1, $2, $3, $4, now())
       ON CONFLICT (home_id, day) DO UPDATE
         SET wh_sum     = daily_energy.wh_sum + EXCLUDED.wh_sum,
             n_readings = daily_energy.n_readings + EXCLUDED.n_readings,
             computed_at = now()`,
      [b.home, b.day, b.wh, b.n]);
  }
}
