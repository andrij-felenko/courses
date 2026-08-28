UPDATE jobs
   SET run_at    = now() + make_interval(secs => $2),   -- оренда
       attempts  = attempts + 1,
       locked_by = $3
 WHERE id IN (
       SELECT id FROM jobs
        WHERE status = 'ready'
          AND run_at <= now()
          AND attempts < max_attempts
        ORDER BY run_at, id
        LIMIT $1
        FOR UPDATE SKIP LOCKED
 )
RETURNING id, kind, payload, attempts, max_attempts;
