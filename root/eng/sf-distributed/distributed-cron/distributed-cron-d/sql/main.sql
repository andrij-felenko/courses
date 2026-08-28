UPDATE cron_jobs
SET status = 'RUNNING',
    locked_by = 'worker-pod-4',
    locked_until = NOW() + INTERVAL '5 minutes'
WHERE id IN (
    SELECT id
    FROM cron_jobs
    WHERE next_run_at <= NOW()
      AND (status = 'IDLE' OR locked_until < NOW())
    ORDER BY next_run_at ASC
    LIMIT 50
    FOR UPDATE SKIP LOCKED
)
RETURNING *;
