const maxAttempts = 8

// повертає true — прибрати з черги (ack); false — повернути в чергу (retry)
func handle(ctx context.Context, eventID string) bool {
    tx, err := db.BeginTx(ctx, nil)
    if err != nil {
        return false                                   // не почали — назад у чергу
    }
    defer tx.Rollback()                                // no-op після Commit; підстрахує будь-який вихід

    var status string
    var payload []byte
    err = tx.QueryRowContext(ctx,
        `SELECT status, payload FROM webhook_inbox
         WHERE event_id = $1 FOR UPDATE`, eventID).Scan(&status, &payload)  // замок на рядок
    switch {
    case err == sql.ErrNoRows:
        tx.Commit(); return true                       // рядка нема — нічого гасити
    case err != nil:
        return onFailure(ctx, eventID, err)
    case status == "done" || status == "dead":
        tx.Commit(); return true                       // уже зроблено/відкладено — тихо
    }

    if err := applySideEffect(ctx, tx, payload); err != nil {   // у ТІЙ САМІЙ транзакції
        return onFailure(ctx, eventID, err)
    }
    if _, err := tx.ExecContext(ctx,
        `UPDATE webhook_inbox SET status='done', processed_at=now()
         WHERE event_id = $1`, eventID); err != nil {
        return onFailure(ctx, eventID, err)
    }
    if err := tx.Commit(); err != nil {                // ефект і 'done' лягають РАЗОМ
        return onFailure(ctx, eventID, err)
    }
    return true
}

func applySideEffect(ctx context.Context, tx *sql.Tx, payload []byte) error {
    var ev struct{ Data struct{ InvoiceID string `json:"invoice_id"` } }
    if err := json.Unmarshal(payload, &ev); err != nil {
        return err
    }
    // Умова paid=false робить повтор нічим — сам ефект теж ідемпотентний.
    _, err := tx.ExecContext(ctx,
        `UPDATE invoices SET paid = true, paid_at = now()
         WHERE id = $1 AND paid = false`, ev.Data.InvoiceID)
    return err
}

func onFailure(ctx context.Context, eventID string, cause error) bool {
    var attempts int
    db.QueryRowContext(ctx,
        `UPDATE webhook_inbox SET attempts = attempts + 1
         WHERE event_id = $1 RETURNING attempts`, eventID).Scan(&attempts)
    if attempts >= maxAttempts {
        db.ExecContext(ctx, `UPDATE webhook_inbox SET status='dead' WHERE event_id = $1`, eventID)
        alertHuman(eventID, cause)                      // отруйна подія — хай гляне людина
        return true                                     // прибрати з живої черги
    }
    return false                                        // назад у чергу, з наростанням паузи
}
