INSERT INTO idempotency_keys AS ik
    (user_id, request_path, key, request_hash, state, expires_at, locked_at)
VALUES ($1, $2, $3, $4, 'in_progress', $5, now())
ON CONFLICT (user_id, request_path, key) DO UPDATE
    SET request_hash = EXCLUDED.request_hash,
        state        = 'in_progress',
        expires_at   = EXCLUDED.expires_at,
        locked_at    = now(),
        response_status = NULL, response_headers = NULL, response_body = NULL
    WHERE ik.expires_at < now()                                  -- ключ протух цілком
       OR (ik.state = 'in_progress'
           AND ik.locked_at < now() - interval '60 seconds')     -- переможець завис
RETURNING (xmax = 0) AS fresh_insert;
