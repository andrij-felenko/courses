func inboxInsert(ctx context.Context, id, typ string, raw []byte) (bool, error) {
    res, err := db.ExecContext(ctx,
        `INSERT INTO webhook_inbox (event_id, type, payload)
         VALUES ($1, $2, $3)
         ON CONFLICT (event_id) DO NOTHING`,
        id, typ, string(raw))
    if err != nil {
        return false, err
    }
    n, _ := res.RowsAffected()
    return n == 1, nil               // 1 — нова; 0 — дубль
}
