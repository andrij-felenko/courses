-- Контрольна сума ПОНАД тоталі: детермінований відбиток усіх фактів партиції.
-- Рядки сортуємо (щоб порядок не впливав), зшиваємо й хешуємо. Збіжиться,
-- лише якщо збіглася КОЖНА трійка (meter, ts, kwh), а не тільки їх сума.
SELECT home_id,
       (ts AT TIME ZONE 'Europe/Kyiv')::date AS day,
       md5(string_agg(meter_id || '|' || ts || '|' || kwh, ','
                      ORDER BY meter_id, ts)) AS checksum
FROM reading
WHERE ts >= %(from_day)s::date    AT TIME ZONE 'Europe/Kyiv'
  AND ts <  %(seal_before)s::date AT TIME ZONE 'Europe/Kyiv'
GROUP BY home_id, day;
