async def claim(conn, key, user_id, path, req_hash, expires_at):
    inserted = await conn.fetchrow(
        """
        INSERT INTO idempotency_keys
            (user_id, request_path, key, request_hash, state, expires_at)
        VALUES ($1, $2, $3, $4, 'in_progress', $5)
        ON CONFLICT (user_id, request_path, key) DO NOTHING
        RETURNING key
        """,
        user_id, path, key, req_hash, expires_at,
    )
    if inserted is not None:
        return True, None                     # рядок створено — claim наш

    row = await conn.fetchrow(
        """
        SELECT state, request_hash, response_status, response_headers, response_body
        FROM idempotency_keys
        WHERE user_id = $1 AND request_path = $2 AND key = $3
        """,
        user_id, path, key,
    )
    return False, row                         # ключ уже був — ось він
