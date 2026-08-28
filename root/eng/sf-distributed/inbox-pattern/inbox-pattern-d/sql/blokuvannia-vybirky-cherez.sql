WITH target_batch AS (
    SELECT message_id
    FROM inbox_messages
    WHERE status = 'RECEIVED'
    ORDER BY created_at ASC
    LIMIT 10
    FOR UPDATE SKIP LOCKED
)
UPDATE inbox_messages m
SET status = 'PROCESSING',
    locked_until = NOW() + INTERVAL '30 seconds',
    locked_by = 'worker-pod-4'
FROM target_batch b
WHERE m.message_id = b.message_id
RETURNING m.message_id, m.payload;
