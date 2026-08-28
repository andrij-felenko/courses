-- КЛЕЙМ: атомарно вихопити одну готову задачу й одразу позначити її своєю
UPDATE job
SET state        = 'running',
    attempts     = attempts + 1,                    -- лічимо спробу вже ТУТ, на вході
    locked_until = now() + ($1 * interval '1 second'), -- оренда клейма на $1 секунд
    updated_at   = now()
WHERE id = (
    SELECT id FROM job
    WHERE (state = 'queued'  AND run_after   <= now())   -- готова й час настав
       OR (state = 'running' AND locked_until <  now())  -- АБО загублене клеймо протухло
    ORDER BY run_after
    FOR UPDATE SKIP LOCKED                               -- ← ось воно
    LIMIT 1
)
RETURNING id, key, payload, attempts, max_attempts;
