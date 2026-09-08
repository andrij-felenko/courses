package main

import (
	"context"
	"errors"
	"fmt"
	"math/rand"
	"sync"
	"sync/atomic"
	"time"
)

// ChaosSimulator (MockProvider) реалізує Provider із контрольованою латентністю та відмовами.
type ChaosSimulator struct {
	id          string
	latency     time.Duration
	failPercent int
	mu          sync.Mutex
}

func NewChaosSimulator(id string, latency time.Duration, failPercent int) *ChaosSimulator {
	return &ChaosSimulator{
		id:          id,
		latency:     latency,
		failPercent: failPercent,
	}
}

func (m *ChaosSimulator) ID() string {
	return m.id
}

func (m *ChaosSimulator) SetBehavior(latency time.Duration, failPercent int) {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.latency = latency
	m.failPercent = failPercent
}

func (m *ChaosSimulator) Execute(ctx context.Context, req Request) (Response, error) {
	m.mu.Lock()
	lat := m.latency
	failPct := m.failPercent
	m.mu.Unlock()

	select {
	case <-time.After(lat):
	case <-ctx.Done():
		return Response{ProviderID: m.id}, ctx.Err()
	}

	// Емуляція відмови віддаленого сервісу
	if rand.Intn(100) < failPct {
		return Response{
			StatusCode: 503,
			Duration:   lat,
			ProviderID: m.id,
		}, errors.New("chaos: провайдер повернув 503 Service Unavailable")
	}

	return Response{
		StatusCode: 200,
		Body:       []byte(`{"status":"SUCCESS","tx_id":"tx_` + req.ID + `"}`),
		Duration:   lat,
		ProviderID: m.id,
	}, nil
}

func main() {
	fmt.Println("=== ВІДМОВОСТІЙКИЙ КЛІЄНТСЬКИЙ ШЛЮЗ НА GO (RESILIENT GATEWAY) ===")
	fmt.Println("Ініціалізація захисного контуру: Bulkhead + Circuit Breaker + ErrorClassifier + Active-Passive")

	// 1. Створення провайдерів з хаос-симуляцією
	primaryMock := NewChaosSimulator("PrimaryPay", 10*time.Millisecond, 0)
	secondaryMock := NewChaosSimulator("BackupPay", 15*time.Millisecond, 0)

	// 2. Налаштування семафорних перебірок (Bulkhead: 10 паралельних слотів, черга 5)
	primaryBH := NewBulkhead(BulkheadConfig{
		MaxConcurrent: 10,
		MaxQueueSize:  5,
		QueueTimeout:  50 * time.Millisecond,
	})
	secondaryBH := NewBulkhead(BulkheadConfig{
		MaxConcurrent: 10,
		MaxQueueSize:  5,
		QueueTimeout:  50 * time.Millisecond,
	})

	// 3. Налаштування вимикачів навантаження (Circuit Breaker: вікно 10, поріг збоїв 50%, таймаут 200 мс)
	primaryCB := NewCircuitBreaker(CircuitBreakerConfig{
		WindowSize:         10,
		FailureThreshold:   0.5,
		SlowCallDuration:   50 * time.Millisecond,
		SlowCallThreshold:  0.5,
		OpenTimeout:        200 * time.Millisecond,
		HalfOpenProbeCount: 3,
	})
	secondaryCB := NewCircuitBreaker(CircuitBreakerConfig{
		WindowSize:         10,
		FailureThreshold:   0.5,
		SlowCallDuration:   50 * time.Millisecond,
		SlowCallThreshold:  0.5,
		OpenTimeout:        200 * time.Millisecond,
		HalfOpenProbeCount: 3,
	})

	primaryTarget := ProtectedProvider{
		Provider:       primaryMock,
		Bulkhead:       primaryBH,
		CircuitBreaker: primaryCB,
	}
	secondaryTarget := ProtectedProvider{
		Provider:       secondaryMock,
		Bulkhead:       secondaryBH,
		CircuitBreaker: secondaryCB,
	}

	classifier := NewErrorClassifier()
	dispatcher := NewDispatcher(primaryTarget, secondaryTarget, classifier, 2, 20*time.Millisecond)

	// ФАЗА 1: Нормальний робочий потік через основний провайдер
	fmt.Println("\n--- ФАЗА 1: Нормальний стан системи (PrimaryPay здоровий) ---")
	for i := 1; i <= 5; i++ {
		req := Request{
			ID:             fmt.Sprintf("req-%03d", i),
			Method:         "POST",
			Endpoint:       "/api/charge",
			IdempotencyKey: fmt.Sprintf("idem-key-%d", i),
			IsIdempotent:   true,
		}
		resp, err := dispatcher.Execute(context.Background(), req)
		if err != nil {
			fmt.Printf("Запит %s: помилка: %v\n", req.ID, err)
		} else {
			fmt.Printf("Запит %s: УСПІХ [%s] за %v (код %d)\n", req.ID, resp.ProviderID, resp.Duration, resp.StatusCode)
		}
	}

	// ФАЗА 2: Хаос-інжекція (PrimaryPay деградує, 100% збоїв 503)
	fmt.Println("\n--- ФАЗА 2: Хаос-інжекція (PrimaryPay деградує, 100% збоїв 503) ---")
	primaryMock.SetBehavior(20*time.Millisecond, 100)

	var successCount, failoverCount, failedCount int32
	var wg sync.WaitGroup

	// Хвиля з 15 паралельних запитів для тестування Bulkhead та Circuit Breaker
	for i := 6; i <= 20; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			req := Request{
				ID:             fmt.Sprintf("req-%03d", idx),
				Method:         "POST",
				Endpoint:       "/api/charge",
				IdempotencyKey: fmt.Sprintf("idem-key-%d", idx),
				IsIdempotent:   true,
			}
			ctx, cancel := context.WithTimeout(context.Background(), 500*time.Millisecond)
			defer cancel()

			resp, err := dispatcher.Execute(ctx, req)
			if err == nil {
				atomic.AddInt32(&successCount, 1)
				if resp.ProviderID == secondaryMock.ID() {
					atomic.AddInt32(&failoverCount, 1)
				}
			} else {
				atomic.AddInt32(&failedCount, 1)
			}
		}(i)
	}
	wg.Wait()

	fmt.Printf("Результати хаос-тесту під навантаженням:\n")
	fmt.Printf("  Всього запитів:         15\n")
	fmt.Printf("  Успішно опрацьовано:    %d\n", successCount)
	fmt.Printf("  Перемикань на Backup:   %d (Active-Passive failover)\n", failoverCount)
	fmt.Printf("  Відхилено (fail-fast):  %d\n", failedCount)
	fmt.Printf("  Стан CircuitBreaker Primary: %s\n", primaryCB.GetState())

	// ФАЗА 3: Захист від подвійних мутацій
	fmt.Println("\n--- ФАЗА 3: Захист від подвійних мутацій (Non-Idempotent запит) ---")
	unsafeReq := Request{
		ID:             "req-unsafe-001",
		Method:         "POST",
		Endpoint:       "/api/transfer",
		IdempotencyKey: "", // Відсутній ключ ідемпотентності!
		IsIdempotent:   false,
	}
	_, err := dispatcher.Execute(context.Background(), unsafeReq)
	if err != nil {
		fmt.Printf("Запит без ідемпотентності безпечно заблоковано від повторного списання: %v\n", err)
	}

	fmt.Println("\n=== РОБОТУ ШЛЮЗУ ЗАВЕРШЕНО: Всі інженерні рубежі захисту перевірено ===")
}\n
