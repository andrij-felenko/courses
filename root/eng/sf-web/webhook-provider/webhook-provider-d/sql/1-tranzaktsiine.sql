UPDATE outbox_events
SET status = 'processing',
    locked_by = 'worker-node-1',
    locked_at = NOW()
WHERE id IN (
    SELECT id FROM outbox_events
    WHERE (status = 'pending' OR status = 'failed')
      AND next_retry_at <= NOW()
    ORDER BY next_retry_at ASC
    LIMIT 100
    FOR UPDATE SKIP LOCKED
)
RETURNING *;
