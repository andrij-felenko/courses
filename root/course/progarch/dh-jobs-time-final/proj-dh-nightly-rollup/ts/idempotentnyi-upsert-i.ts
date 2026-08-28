type AggTask = { homeId: string; zone: string; day: string;
                 fromUtc: string; toUtc: string; fence: number; policy: MissPolicy };

async function aggregate(db: Pool, t: AggTask): Promise<void> {
  const { rows } = await db.query(
    `SELECT value, watts FROM telemetry
      WHERE home_id = $1 AND at >= $2 AND at < $3`,   // напіввідкрите [from, to)
    [t.homeId, t.fromUtc, t.toUtc]);
  const s = rollUp(rows);                             // { kwh, peakW, samples }

  await db.query("BEGIN");
  try {
    // 1) підсумок — ідемпотентний за (дім, доба): дубль перепише той самий рядок
    await db.query(
      `INSERT INTO daily_summary (home_id, day, kwh, peak_w, samples, zone)
       VALUES ($1,$2,$3,$4,$5,$6)
       ON CONFLICT (home_id, day) DO UPDATE
          SET kwh=EXCLUDED.kwh, peak_w=EXCLUDED.peak_w,
              samples=EXCLUDED.samples, computed_at=now()`,
      [t.homeId, t.day, s.kwh, s.peakW, s.samples, t.zone]);
    // 2) mark — після підсумку, свіжим фенсом, і на добу $2 ЛИШЕ якщо вона
    //    БЕЗПОСЕРЕДНЬО наступна (last_done_day = $2 − 1) — АБО політика skip,
    //    якій дозволено навмисне перестрибнути дірку. Тоді доба, що дозріла
    //    поперед сусідів у пулі наздоганяння, mark не зрушить (інакше вона
    //    перестрибнула б ще не зроблену добу — і та зникла б назавжди).
    await db.query(
      `UPDATE home_cron
          SET last_done_day = GREATEST(last_done_day, $2), seen_fence = $3
        WHERE home_id = $1 AND seen_fence <= $3
          AND (last_done_day = $2::date - 1 OR $4 = 'skip')`,
      [t.homeId, t.day, t.fence, t.policy]);
    await db.query("COMMIT");
  } catch (e) {
    await db.query("ROLLBACK");                       // впав до коміту → доба лишилась due
    throw e;
  }
}
