WITH next_task AS (
    SELECT id
      FROM operations
     WHERE state = 'pending'
        OR (state = 'running' AND lease_until < NOW())
     ORDER BY priority DESC, created_at ASC
     LIMIT 1
       FOR UPDATE SKIP LOCKED
)
UPDATE operations o
   SET state = 'running',
       attempt = o.attempt + 1,
       lease_token = gen_random_uuid(),
       lease_until = NOW() + INTERVAL '30 seconds',
       updated_at = NOW()
  FROM next_task
 WHERE o.id = next_task.id
RETURNING o.id, o.kind, o.attempt, o.lease_token, o.checkpoint_data;
