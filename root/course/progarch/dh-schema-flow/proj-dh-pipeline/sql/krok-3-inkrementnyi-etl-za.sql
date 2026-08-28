-- Сирі за вікно (EXTRACT):
SELECT home_id, device_id, ts, schema, value
FROM   telemetry
WHERE  ts >= :start_ts AND ts < :end_ts;

-- Carry-in: останній показ лічильника СТРОГО до вікна, на кожен пристрій (schema:2):
SELECT DISTINCT ON (device_id) device_id, value
FROM   telemetry
WHERE  ts < :start_ts AND schema = 2
ORDER  BY device_id, ts DESC;         -- DISTINCT ON бере перший рядок кожної групи
