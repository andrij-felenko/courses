BEGIN;
SELECT id, aggregate_id, event_type, payload
FROM outbox_events
WHERE status = 'PENDING'
ORDER BY created_at ASC
LIMIT 100
FOR UPDATE SKIP LOCKED;

-- Після успішної публікації в Kafka:
UPDATE outbox_events
SET status = 'PUBLISHED', published_at = NOW()
WHERE id IN (...);
COMMIT;
