WITH candidate_batch AS (
    SELECT message_id, consumer_group
    FROM inbox_messages
    WHERE consumer_group = :consumer_group
      AND (
          status = 'RECEIVED'
          OR (status = 'PROCESSING' AND locked_until < NOW())
      )
    ORDER BY created_at ASC
    LIMIT :batch_size
    FOR UPDATE SKIP LOCKED
)
UPDATE inbox_messages m
SET status = 'PROCESSING',
    locked_until = NOW() + (:lease_seconds || ' seconds')::INTERVAL,
    locked_by = :worker_instance_id
FROM candidate_batch c
WHERE m.message_id = c.message_id
  AND m.consumer_group = c.consumer_group
RETURNING m.message_id, m.event_type, m.payload, m.retry_count;
