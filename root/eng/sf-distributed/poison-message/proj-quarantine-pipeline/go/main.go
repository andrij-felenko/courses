package main

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"fmt"
	"strings"
	"sync"
	"time"
)

// ── 1. Структури даних карантину ────────────────────────────────────────────

type MessageStatus string

const (
	StatusQuarantined MessageStatus = "QUARANTINED"
	StatusUnderReview MessageStatus = "UNDER_REVIEW"
	StatusMutated     MessageStatus = "MUTATED"
	StatusReplayed    MessageStatus = "REPLAYED"
	StatusDiscarded   MessageStatus = "DISCARDED"
)

type FailureClass string

const (
	FailTransient     FailureClass = "TRANSIENT"
	FailDeterministic FailureClass = "DETERMINISTIC_POISON"
	FailResourceDoS   FailureClass = "RESOURCE_EXHAUSTION"
	FailPanic         FailureClass = "RUNTIME_PANIC"
)

type IngressMessage struct {
	ID            string
	PartitionKey  string
	Payload       []byte
	DeliveryCount int
	Timestamp     time.Time
}

type QuarantineEnvelope struct {
	QuarantineID      string        `json:"quarantine_id"`
	OriginalMessageID string        `json:"original_message_id"`
	PartitionKey      string        `json:"partition_key"`
	PayloadHex        string        `json:"payload_hex"`
	MutatedPayloadHex string        `json:"mutated_payload_hex,omitempty"`
	PayloadSHA256     string        `json:"payload_sha256"`
	FailureReason     string        `json:"failure_reason"`
	ExceptionDetails  string        `json:"exception_details"`
	Category          FailureClass  `json:"category"`
	Status            MessageStatus `json:"status"`
	DeliveryAttempts  int           `json:"delivery_attempts"`
	QuarantinedAt     time.Time     `json:"quarantined_at"`
	HostIdentity      string        `json:"host_identity"`
}

// ── 2. Сховище карантину ───────────────────────────────────────────────────

type QuarantineStore struct {
	mu    sync.RWMutex
	items map[string]QuarantineEnvelope
}

func NewQuarantineStore() *QuarantineStore {
	return &QuarantineStore{items: make(map[string]QuarantineEnvelope)}
}

func (s *QuarantineStore) Put(env QuarantineEnvelope) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.items[env.QuarantineID] = env
	fmt.Printf("[QUARANTINE-STORE] Зафіксовано отруту ID=%s (MsgID=%s, Причина: %s)\n",
		env.QuarantineID, env.OriginalMessageID, env.FailureReason)
}

func (s *QuarantineStore) Get(qid string) (QuarantineEnvelope, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	env, ok := s.items[qid]
	return env, ok
}

func (s *QuarantineStore) Update(env QuarantineEnvelope) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.items[env.QuarantineID] = env
}

// ── 3. Сторожовий супервізор з перехопленням панік ──────────────────────────

type HandlerFunc func(ctx context.Context, msg IngressMessage) error

func ExecuteSupervised(ctx context.Context, msg IngressMessage, handler HandlerFunc, timeout time.Duration) (err error, cat FailureClass) {
	ctxTimeout, cancel := context.WithTimeout(ctx, timeout)
	defer cancel()

	done := make(chan error, 1)

	go func() {
		defer func() {
			if r := recover(); r != nil {
				done <- fmt.Errorf("runtime panic caught: %v", r)
			}
		}()
		done <- handler(ctxTimeout, msg)
	}()

	select {
	case <-ctxTimeout.Done():
		return errors.New("watchdog timeout: execution deadline exceeded"), FailResourceDoS
	case err = <-done:
		if err == nil {
			return nil, ""
		}
		errMsg := err.Error()
		if strings.Contains(errMsg, "panic") {
			return err, FailPanic
		}
		if strings.Contains(errMsg, "schema") || strings.Contains(errMsg, "invariant") {
			return err, FailDeterministic
		}
		return err, FailTransient
	}
}

// ── 4. Консюмер із запобіганням Head-of-Line Blocking ───────────────────────

type QuarantineConsumer struct {
	store      *QuarantineStore
	maxRetries int
}

func NewQuarantineConsumer(store *QuarantineStore, maxRetries int) *QuarantineConsumer {
	return &QuarantineConsumer{store: store, maxRetries: maxRetries}
}

func (c *QuarantineConsumer) HandleIncoming(ctx context.Context, msg IngressMessage, handler HandlerFunc) bool {
	err, category := ExecuteSupervised(ctx, msg, handler, 500*time.Millisecond)
	if err == nil {
		fmt.Printf("[CONSUMER] MsgID=%s успішно оброблено. Commit ACK.\n", msg.ID)
		return true
	}

	fmt.Printf("[CONSUMER-WARN] Збій MsgID=%s: %v (Категорія: %s)\n", msg.ID, err, category)

	shouldQuarantine := category == FailDeterministic ||
		category == FailResourceDoS ||
		category == FailPanic ||
		msg.DeliveryCount >= c.maxRetries

	if shouldQuarantine {
		hash := sha256.Sum256(msg.Payload)
		env := QuarantineEnvelope{
			QuarantineID:      fmt.Sprintf("Q-%s-%d", msg.ID, time.Now().UnixNano()),
			OriginalMessageID: msg.ID,
			PartitionKey:      msg.PartitionKey,
			PayloadHex:        hex.EncodeToString(msg.Payload),
			PayloadSHA256:     hex.EncodeToString(hash[:]),
			FailureReason:     string(category),
			ExceptionDetails:  err.Error(),
			Category:          category,
			Status:            StatusQuarantined,
			DeliveryAttempts:  msg.DeliveryCount,
			QuarantinedAt:     time.Now().UTC(),
			HostIdentity:      "worker-go-01",
		}

		c.store.Put(env)
		// Фіксуємо зміщення: партиція не блокується
		fmt.Printf("[CONSUMER] Повідомлення MsgID=%s ізольовано в карантин. Commit Offset!\n", msg.ID)
		return true
	}

	fmt.Printf("[CONSUMER] Перехідний збій MsgID=%s (Спроба %d/%d). Requeue.\n", msg.ID, msg.DeliveryCount, c.maxRetries)
	return false
}
