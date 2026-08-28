-- БЕЗПЕЧНА КОНКУРЕНТНА ВИБІРКА ПАЧКИ ПОДІЙ
BEGIN;

SELECT id, aggregate_type, aggregate_id, payload
FROM outbox
ORDER BY created_at ASC
LIMIT 50
FOR UPDATE SKIP LOCKED;

-- [Воркер надсилає вибрані 50 подій у брокер Kafka і чекає ACK]

DELETE FROM outbox 
WHERE id = ANY(ARRAY['f47ac10b-58cc-4372-a567-0e02b2c3d479'::uuid, ...]);

COMMIT;
