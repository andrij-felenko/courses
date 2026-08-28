-- 1. показання одного давача за вікно часу
SELECT ts, value FROM telemetry
 WHERE device_id = $1 AND ts >= $2 AND ts < $3
 ORDER BY ts;

-- 2. звести дім за місяць — перемолоти й викинути
SELECT date_trunc('hour', ts) AS h, avg(value)
  FROM telemetry
 WHERE home_id = $1 AND ts >= now() - interval '30 days'
 GROUP BY h;
