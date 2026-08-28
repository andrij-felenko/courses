-- Атомарне захоплення пакета задач робітником
UPDATE outbound_outbox
SET status = 'PROCESSING',
    updated_at = NOW()
WHERE id IN (
    SELECT id
    FROM outbound_outbox
    WHERE status IN ('PENDING', 'FAILED')
      AND next_retry_at <= NOW()
    ORDER BY created_at ASC
    LIMIT 50
    FOR UPDATE SKIP LOCKED
)
RETURNING id, destination_type, destination_url, payload_json, secret_key, idempotency_key, attempt, max_attempts;
