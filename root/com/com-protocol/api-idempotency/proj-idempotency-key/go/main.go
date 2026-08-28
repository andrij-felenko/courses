func claim(ctx context.Context, db *sql.DB, k keyID, hash []byte, exp time.Time) (bool, *keyRow, error) {
    var scanned string
    err := db.QueryRowContext(ctx,
        `INSERT INTO idempotency_keys
            (user_id, request_path, key, request_hash, state, expires_at)
         VALUES ($1, $2, $3, $4, 'in_progress', $5)
         ON CONFLICT (user_id, request_path, key) DO NOTHING
         RETURNING key`,
        k.userID, k.path, k.key, hash, exp,
    ).Scan(&scanned)
    switch {
    case err == nil:
        return true, nil, nil                 // рядок створено — claim наш
    case !errors.Is(err, sql.ErrNoRows):
        return false, nil, err                // справжня помилка БД
    }
    // ErrNoRows == конфлікт: ключ уже є, читаємо його
    row := &keyRow{}
    err = db.QueryRowContext(ctx,
        `SELECT state, request_hash, response_status, response_headers, response_body
           FROM idempotency_keys
          WHERE user_id = $1 AND request_path = $2 AND key = $3`,
        k.userID, k.path, k.key,
    ).Scan(&row.state, &row.hash, &row.status, &row.headers, &row.body)
    return false, row, err
}
