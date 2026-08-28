type Claim = { won: true } | { won: false; row: KeyRow };

async function claim(
  db: Pool, key: string, userId: string, path: string,
  hash: Buffer, expiresAt: Date,
): Promise<Claim> {
  const ins = await db.query(
    `INSERT INTO idempotency_keys
        (user_id, request_path, key, request_hash, state, expires_at)
     VALUES ($1, $2, $3, $4, 'in_progress', $5)
     ON CONFLICT (user_id, request_path, key) DO NOTHING
     RETURNING key`,
    [userId, path, key, hash, expiresAt],
  );
  if (ins.rowCount === 1) return { won: true };   // рядок створено — claim наш

  const sel = await db.query(
    `SELECT state, request_hash, response_status, response_headers, response_body
       FROM idempotency_keys
      WHERE user_id = $1 AND request_path = $2 AND key = $3`,
    [userId, path, key],
  );
  return { won: false, row: sel.rows[0] };        // ключ уже був — ось він
}
