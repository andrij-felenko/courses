-- Згортка + родовід + ідемпотентний запис — одним рухом, у сховищі.
INSERT INTO daily_kwh
  (home_id, day, kwh, source_from, source_to, pipeline_version, schemas_seen, computed_at)
SELECT c.home_id,
       c.day,
       ROUND(SUM(c.wh) / 1000.0, 1)                          AS kwh,
       :from, :to, :pipeline_version,
       ARRAY_AGG(DISTINCT c.raw_schema ORDER BY c.raw_schema) AS schemas_seen,
       now()
FROM   canon c
WHERE  c.day >= :from AND c.day <= :to
GROUP  BY c.home_id, c.day
ON CONFLICT (home_id, day) DO UPDATE SET
       kwh              = EXCLUDED.kwh,          -- ЗАМІНА рядка, не додавання
       source_from      = EXCLUDED.source_from,
       source_to        = EXCLUDED.source_to,
       pipeline_version = EXCLUDED.pipeline_version,
       schemas_seen     = EXCLUDED.schemas_seen,
       computed_at      = EXCLUDED.computed_at;
