package main

import (
	"context"
	"crypto/sha256"
	"database/sql"
	"encoding/hex"
	"errors"
	"fmt"
	"net/http"
	"sync"
	"time"

	_ "github.com/lib/pq"
)

// Message представляє подію з черги брокера
type Message struct {
	ID        string
	Topic     string
	Partition int
	Offset    int64
	Payload   []byte
	Attempt   int
}

// ConsumerEngine реалізує трифазний ідемпотентний обробник
type ConsumerEngine struct {
	db          *sql.DB
	httpClient  *http.Client
	memCache    map[string]time.Time
	cacheMu     sync.RWMutex
	leaseTTL    time.Duration
	maxAttempts int
}

func NewConsumerEngine(db *sql.DB) *ConsumerEngine {
	return &ConsumerEngine{
		db:          db,
		httpClient:  &http.Client{Timeout: 5 * time.Second},
		memCache:    make(map[string]time.Time),
		leaseTTL:    30 * time.Second,
		maxAttempts: 3,
	}
}

// DeriveOutboundKey обчислює стабільний детермінований токен для стороннього сервісу
func (c *ConsumerEngine) DeriveOutboundKey(msgID, action string) string {
	h := sha256.New()
	h.Write([]byte(fmt.Sprintf("%s:%s", msgID, action)))
	return "idemp_" + hex.EncodeToString(h.Sum(nil))[:32]
}

// ProcessMessage виконує повний життєвий цикл обробки повідомлення
func (c *ConsumerEngine) ProcessMessage(ctx context.Context, msg Message) error {
	// 0. Швидка перевірка в кеші пам'яті (L1 дедуплікація)
	c.cacheMu.RLock()
	if _, found := c.memCache[msg.ID]; found {
		c.cacheMu.RUnlock()
		return nil // Вже успішно оброблено, пропускаємо
	}
	c.cacheMu.RUnlock()

	outboundKey := c.DeriveOutboundKey(msg.ID, "charge_payment")
	leaseExpiry := time.Now().Add(c.leaseTTL)

	// ФАЗА 1: Чисте транзакційне рішення (Бронювання наміру в Inbox)
	tx, err := c.db.BeginTx(ctx, &sql.TxOptions{Isolation: sql.LevelReadCommitted})
	if err != nil {
		return fmt.Errorf("помилка відкриття транзакції: %w", err)
	}
	defer tx.Rollback()

	var status string
	var attempts int
	query := `
		INSERT INTO consumer_inbox (
			message_id, consumer_group, topic, partition_id, message_offset,
			status, outbound_idempotency_key, delivery_attempts, lease_expires_at
		) VALUES ($1, 'payments_group', $2, $3, $4, 'IN_PROGRESS', $5, 1, $6)
		ON CONFLICT (consumer_group, message_id) DO UPDATE SET
			delivery_attempts = consumer_inbox.delivery_attempts + 1,
			lease_expires_at = EXCLUDED.lease_expires_at
		RETURNING status, delivery_attempts;
	`
	err = tx.QueryRowContext(ctx, query, msg.ID, msg.Topic, msg.Partition, msg.Offset, outboundKey, leaseExpiry).Scan(&status, &attempts)
	if err != nil {
		return fmt.Errorf("помилка резервування в inbox: %w", err)
	}

	// Якщо повідомлення вже було завершено раніше
	if status == "COMPLETED" {
		tx.Rollback()
		c.cacheMu.Lock()
		c.memCache[msg.ID] = time.Now()
		c.cacheMu.Unlock()
		return nil // Ідемпотентний пропуск
	}

	// Захист від отруйної петлі (Poison Loop Break)
	if attempts > c.maxAttempts {
		_, _ = tx.ExecContext(ctx, "UPDATE consumer_inbox SET status = 'QUARANTINED' WHERE message_id = $1", msg.ID)
		_ = tx.Commit()
		c.routeToDeadLetterQueue(msg, "перевищено ліміт спроб (отруйне повідомлення)")
		return nil // Підтверджуємо зсув брокеру, щоб розблокувати чергу
	}

	if err := tx.Commit(); err != nil {
		return fmt.Errorf("помилка фіксації Фази 1: %w", err)
	}

	// ФАЗА 2: Мережевий сайд-ефект із детермінованим токеном ідемпотентності
	externalRef, err := c.executeExternalSideEffect(ctx, outboundKey, msg.Payload)
	if err != nil {
		// Тимчасовий збій мережі: залишаємо статус IN_PROGRESS, оренду вичерпає таймаут
		return fmt.Errorf("збій виклику стороннього API: %w", err)
	}

	// ФАЗА 3: Фіналізація стану в базі даних
	txFin, err := c.db.BeginTx(ctx, nil)
	if err != nil {
		return fmt.Errorf("помилка транзакції фіналізації: %w", err)
	}
	defer txFin.Rollback()

	updateQuery := `
		UPDATE consumer_inbox
		SET status = 'COMPLETED',
		    external_reference = $1,
		    completed_at = NOW()
		WHERE message_id = $2;
	`
	if _, err := txFin.ExecContext(ctx, updateQuery, externalRef, msg.ID); err != nil {
		return fmt.Errorf("помилка оновлення статусу COMPLETED: %w", err)
	}

	// Застосування доменної бізнес-зміни
	if _, err := txFin.ExecContext(ctx, "UPDATE orders SET is_paid = true WHERE id = $1", msg.ID); err != nil {
		return fmt.Errorf("помилка оновлення замовлення: %w", err)
	}

	if err := txFin.Commit(); err != nil {
		return fmt.Errorf("помилка фіксації Фази 3: %w", err)
	}

	// Оновлюємо локальний кеш пам'яті
	c.cacheMu.Lock()
	c.memCache[msg.ID] = time.Now()
	c.cacheMu.Unlock()

	return nil
}

func (c *ConsumerEngine) executeExternalSideEffect(ctx context.Context, idempKey string, payload []byte) (string, error) {
	req, err := http.NewRequestWithContext(ctx, "POST", "https://api.payment-gateway.internal/v1/charges", nil)
	if err != nil {
		return "", err
	}
	// Передаємо детермінований токен ідемпотентності
	req.Header.Set("Idempotency-Key", idempKey)
	req.Header.Set("Content-Type", "application/json")

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 500 {
		return "", errors.New("тимчасова помилка сервера платежів (5xx)")
	}
	return "charge_ref_99412", nil
}

func (c *ConsumerEngine) routeToDeadLetterQueue(msg Message, reason string) {
	fmt.Printf("[DLQ] Повідомлення ID=%s евакуйовано в Dead Letter Queue. Причина: %s\n", msg.ID, reason)
}
