def recompute_partition(cur, conn, p):
    # Перерахунок ОДНІЄЇ партиції: згорнути її reading і ВПИСАТИ поверх (upsert).
    # Межа дня — той самий київський настінний годинник, що й у звірці.
    cur.execute("""
        INSERT INTO daily_energy AS d (home_id, day, n_readings, kwh_sum, computed_at)
        SELECT %(home)s, %(day)s::date, count(*), sum(kwh), now()
        FROM reading
        WHERE home_id = %(home)s
          AND ts >= %(day)s::date            AT TIME ZONE 'Europe/Kyiv'
          AND ts <  (%(day)s::date + 1)      AT TIME ZONE 'Europe/Kyiv'
        ON CONFLICT (home_id, day) DO UPDATE
          SET n_readings  = EXCLUDED.n_readings,
              kwh_sum     = EXCLUDED.kwh_sum,
              computed_at = EXCLUDED.computed_at;
    """, {"home": p.home_id, "day": p.day})
    conn.commit()
