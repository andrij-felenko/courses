// Go: Idiomatic Transactional Outbox Handler
package main

import (
	"context"
	"database/sql"
	"fmt"
)

type OutboxEvent struct {
	EventID       string
	AggregateType string
	AggregateID   string
	EventType     string
	PayloadJSON   string
}

func TransferWithOutbox(ctx context.Context, db *sql.DB, senderID, receiverID string, amountCents int64, event OutboxEvent) error {
	tx, err := db.BeginTx(ctx, &sql.TxOptions{Isolation: sql.LevelSerializable})
	if err != nil {
		return fmt.Errorf("failed to begin tx: %w", err)
	}
	defer tx.Rollback()

	// 1. Списання коштів
	_, err = tx.ExecContext(ctx, "UPDATE wallet_accounts SET balance_cents = balance_cents - $1 WHERE account_id = $2", amountCents, senderID)
	if err != nil {
		return fmt.Errorf("sender debit failed: %w", err)
	}

	// 2. Поповнення коштів
	_, err = tx.ExecContext(ctx, "UPDATE wallet_accounts SET balance_cents = balance_cents + $1 WHERE account_id = $2", receiverID)
	if err != nil {
		return fmt.Errorf("receiver credit failed: %w", err)
	}

	// 3. Запис у outbox_events
	outboxSQL := `INSERT INTO outbox_events (event_id, aggregate_type, aggregate_id, event_type, payload_json) VALUES ($1, $2, $3, $4, $5)`
	_, err = tx.ExecContext(ctx, outboxSQL, event.EventID, event.AggregateType, event.AggregateID, event.EventType, event.PayloadJSON)
	if err != nil {
		return fmt.Errorf("outbox insert failed: %w", err)
	}

	return tx.Commit()
}
