-- Відбудова агрегата з джерела: ідемпотентно (ПЕРЕЗАПИС, не долив).
-- Скільки не запускай — той самий результат: свіжа згортка тих самих фактів.
INSERT INTO daily_energy (home_id, day, wh_sum, n_readings, computed_at)
SELECT home_id,
       (ts AT TIME ZONE 'Europe/Kyiv')::date AS day,
       sum(wh), count(*), now()
FROM reading
WHERE ts >= :from AND ts < :to
GROUP BY home_id, day
ON CONFLICT (home_id, day) DO UPDATE
  SET wh_sum     = EXCLUDED.wh_sum,        -- ПЕРЕЗАПИС, а не += :  ідемпотентно
      n_readings = EXCLUDED.n_readings,
      computed_at = now();
