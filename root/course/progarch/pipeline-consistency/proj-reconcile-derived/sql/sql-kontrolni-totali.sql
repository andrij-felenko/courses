-- Тоталі ДЖЕРЕЛА: згортаємо сирі reading у (home, day) → COUNT + SUM.
-- Межі партиції рахуємо в ОДНОМУ поясі (Europe/Kyiv), той самий і в похідному.
SELECT home_id,
       (ts AT TIME ZONE 'Europe/Kyiv')::date          AS day,
       count(*)                                        AS n_src,
       sum(kwh)                                        AS kwh_src
FROM reading
WHERE ts >= %(from_day)s::date    AT TIME ZONE 'Europe/Kyiv'   -- нижня межа вікна
  AND ts <  %(seal_before)s::date AT TIME ZONE 'Europe/Kyiv'   -- лише ЗАПЕЧАТАНЕ
GROUP BY home_id, day;
