package saga

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"time"
)

type SagaStatus string

const (
	StatusPending     SagaStatus = "PENDING"
	StatusSucceeded   SagaStatus = "SUCCEEDED"
	StatusFailed      SagaStatus = "FAILED"
	StatusCompensated SagaStatus = "COMPENSATED"
)

// ChargeSagaState описує поточний стан транзакції саги
type ChargeSagaState struct {
	ChargeID       string     `json:"charge_id"`
	MerchantID     string     `json:"merchant_id"`
	IdempotencyKey string     `json:"idempotency_key"`
	AmountCents    int64      `json:"amount_cents"`
	Currency       string     `json:"currency"`
	Status         SagaStatus `json:"status"`
}

type OutboxEvent struct {
	ID        string    `json:"id"`
	EventType string    `json:"event_type"`
	Payload   []byte    `json:"payload"`
	CreatedAt time.Time `json:"created_at"`
}

type PaymentSagaOrchestrator struct {
	db *sql.DB
}

func NewOrchestrator(db *sql.DB) *PaymentSagaOrchestrator {
	return &PaymentSagaOrchestrator{db: db}
}

// CommitSagaWithOutbox виконує атомарну локальну ACID транзакцію
func (o *PaymentSagaOrchestrator) CommitSagaWithOutbox(ctx context.Context, saga *ChargeSagaState) error {
	// Встановлюємо таймаут транзакції на рівні контексту (2 секунди)
	ctx, cancel := context.WithTimeout(ctx, 2*time.Second)
	defer cancel()

	tx, err := o.db.BeginTx(ctx, &sql.TxOptions{Isolation: sql.LevelReadCommitted})
	if err != nil {
		return fmt.Errorf("failed to begin database transaction: %w", err)
	}
	// Захисний механізм: у разі паніки або помилки робимо Rollback
	defer tx.Rollback()

	// 1. Збереження або оновлення стану платежу (Upsert)
	sagaQuery := `
		INSERT INTO charges (id, merchant_id, idempotency_key, amount_cents, currency, status, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6, NOW())
		ON CONFLICT (merchant_id, idempotency_key) 
		DO UPDATE SET status = EXCLUDED.status, updated_at = NOW()
	`
	_, err = tx.ExecContext(ctx, sagaQuery, saga.ChargeID, saga.MerchantID, saga.IdempotencyKey, saga.AmountCents, saga.Currency, saga.Status)
	if err != nil {
		return fmt.Errorf("failed to record charge state: %w", err)
	}

	// 2. Серіалізація об'єкта саги у JSON для Outbox
	eventPayload, err := json.Marshal(saga)
	if err != nil {
		return fmt.Errorf("failed to marshal outbox event payload: %w", err)
	}

	// 3. Запис події у таблицю outbox_events у межах ТІЄЇ Ж транзакції
	outboxQuery := `
		INSERT INTO outbox_events (id, event_type, payload, created_at, processed)
		VALUES (gen_random_uuid(), $1, $2, NOW(), false)
	`
	eventType := "charge.succeeded"
	if saga.Status == StatusFailed {
		eventType = "charge.failed"
	}

	_, err = tx.ExecContext(ctx, outboxQuery, eventType, eventPayload)
	if err != nil {
		return fmt.Errorf("failed to insert outbox event record: %w", err)
	}

	// 4. Успішна фіксація транзакції
	if err := tx.Commit(); err != nil {
		return fmt.Errorf("failed to commit saga transaction: %w", err)
	}

	return nil
}

// ProcessOutboxBatch зчитує невідправлені події з підтримкою паралельного блокування FOR UPDATE SKIP LOCKED
func (o *PaymentSagaOrchestrator) ProcessOutboxBatch(ctx context.Context, batchSize int) ([]OutboxEvent, error) {
	tx, err := o.db.BeginTx(ctx, nil)
	if err != nil {
		return nil, err
	}
	defer tx.Rollback()

	// FOR UPDATE SKIP LOCKED дозволяє декільком воркерам читати таблицю outbox без взаємного блокування
	query := `
		SELECT id, event_type, payload, created_at
		FROM outbox_events
		WHERE processed = FALSE
		ORDER BY created_at ASC
		LIMIT $1
		FOR UPDATE SKIP LOCKED
	`
	rows, err := tx.QueryContext(ctx, query, batchSize)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var events []OutboxEvent
	var eventIDs []string

	for rows.Next() {
		var evt OutboxEvent
		if err := rows.Scan(&evt.ID, &evt.EventType, &evt.Payload, &evt.CreatedAt); err != nil {
			return nil, err
		}
		events = append(events, evt)
		eventIDs = append(eventIDs, evt.ID)
	}

	// Позначаємо вичитані події як оброблені
	if len(eventIDs) > 0 {
		updateQuery := `UPDATE outbox_events SET processed = TRUE, processed_at = NOW() WHERE id = ANY($1)`
		if _, err := tx.ExecContext(ctx, updateQuery, eventIDs); err != nil {
			return nil, err
		}
	}

	if err := tx.Commit(); err != nil {
		return nil, err
	}

	log.Printf("[OUTBOX] Successfully fetched and marked %d events", len(events))
	return events, nil
}
