async def aggregate(pool, t: dict) -> None:
    rows = await pool.fetch(
        """SELECT value, watts FROM telemetry
            WHERE home_id = $1 AND at >= $2 AND at < $3""",   # напіввідкрите [from, to)
        t["home_id"], t["from_utc"], t["to_utc"])
    s = roll_up(rows)                                          # {'kwh','peak_w','samples'}

    async with pool.acquire() as conn:
        async with conn.transaction():                        # обидва записи — одним комітом
            # 1) підсумок — ідемпотентний за (дім, доба): дубль перепише той самий рядок
            await conn.execute(
                """INSERT INTO daily_summary (home_id, day, kwh, peak_w, samples, zone)
                   VALUES ($1,$2,$3,$4,$5,$6)
                   ON CONFLICT (home_id, day) DO UPDATE
                      SET kwh=EXCLUDED.kwh, peak_w=EXCLUDED.peak_w,
                          samples=EXCLUDED.samples, computed_at=now()""",
                t["home_id"], t["day"], s["kwh"], s["peak_w"], s["samples"], t["zone"])
            # 2) mark — після підсумку, свіжим фенсом, і на добу $2 ЛИШЕ якщо вона
            #    БЕЗПОСЕРЕДНЬО наступна (last_done_day = $2 − 1) — АБО політика skip,
            #    якій дозволено навмисне перестрибнути дірку. Доба, що дозріла поперед
            #    сусідів у пулі наздоганяння, mark не зрушить — інакше перестрибнула б
            #    ще не зроблену добу, і та зникла б назавжди.
            await conn.execute(
                """UPDATE home_cron
                      SET last_done_day = GREATEST(last_done_day, $2), seen_fence = $3
                    WHERE home_id = $1 AND seen_fence <= $3
                      AND (last_done_day = $2::date - 1 OR $4 = 'skip')""",
                t["home_id"], t["day"], t["fence"], t["policy"])
