UPDATE operations
   SET state = 'running',
       attempt = attempt + 1,
       lease_token = gen_random_uuid(),
       lease_until = now() + interval '30 seconds',
       updated_at = now()
 WHERE id = (
     SELECT id FROM operations
      WHERE state = 'pending'
         OR (state = 'running' AND lease_until < now())
      ORDER BY created_at
      LIMIT 1
      FOR UPDATE SKIP LOCKED
 )
RETURNING id, kind, input, attempt, lease_token;
