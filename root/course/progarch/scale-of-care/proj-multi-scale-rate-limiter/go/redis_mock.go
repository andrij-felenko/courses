package main

import (
	"context"
	"errors"
	"math"
	"sync"
	"time"
)

// RedisClient визначає мінімальний контракт взаємодії з розподіленим сервером Redis.
type RedisClient interface {
	// Eval виконує атомарний Lua-скрипт із передачею ключів і аргументів у контексті виклику.
	Eval(ctx context.Context, script string, keys []string, args ...any) (any, error)
}

// redisEntry зберігає збережений стан ліміту в пам'яті емулятора.
type redisEntry struct {
	tokens      float64
	lastUpdated float64 // Unix-час у секундах із плаваючою комою
}

// MockRedisClient — in-memory емулятор Redis для автономного запуску прикладів
// без потреби розгортання окремого фізичного сервера або Docker-контейнера.
type MockRedisClient struct {
	mu              sync.Mutex
	data            map[string]redisEntry
	simulateLatency time.Duration // Симуляція мережевого RTT
	simulateErr     error         // Симуляція мережевого обриву або падіння вузла
	callsCount      int           // Лічильник фактично виконаних звернень до емулятора
}

// NewMockRedisClient створює новий екземпляр емулятора Redis.
func NewMockRedisClient() *MockRedisClient {
	return &MockRedisClient{
		data: make(map[string]redisEntry),
	}
}

// SetSimulateLatency встановлює затримку обробки (імітація мережевого RTT).
func (m *MockRedisClient) SetSimulateLatency(d time.Duration) {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.simulateLatency = d
}

// SetSimulateError вмикає або вимикає симуляцію апаратної/мережевої аварії.
func (m *MockRedisClient) SetSimulateError(err error) {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.simulateErr = err
}

// CallsCount повертає кількість фактично виконаних запитів до емулятора.
func (m *MockRedisClient) CallsCount() int {
	m.mu.Lock()
	defer m.mu.Unlock()
	return m.callsCount
}

// Eval емулює виконання Lua-скрипта Token Bucket у Redis з урахуванням таймауту контексту та мережевого RTT.
func (m *MockRedisClient) Eval(ctx context.Context, script string, keys []string, args ...any) (any, error) {
	m.mu.Lock()
	latency := m.simulateLatency
	simErr := m.simulateErr
	m.callsCount++
	m.mu.Unlock()

	// Симуляція затримки передачі пакетів по мережі (RTT) з обробкою таймауту контексту
	if latency > 0 {
		select {
		case <-time.After(latency):
		case <-ctx.Done():
			return nil, ctx.Err()
		}
	}

	// Симуляція збою з'єднання (падіння сокета, скидання TCP з'єднання)
	if simErr != nil {
		return nil, simErr
	}

	if len(keys) == 0 || len(args) < 4 {
		return nil, errors.New("недостатньо аргументів для виконання Lua-скрипта лімітера")
	}

	key := keys[0]
	capacity := args[0].(float64)
	refillRate := args[1].(float64)
	nowSec := args[2].(float64)
	requested := args[3].(float64)

	m.mu.Lock()
	defer m.mu.Unlock()

	entry, exists := m.data[key]
	if !exists {
		entry = redisEntry{
			tokens:      capacity,
			lastUpdated: nowSec,
		}
	} else {
		elapsed := math.Max(0, nowSec-entry.lastUpdated)
		entry.tokens = math.Min(capacity, entry.tokens+(elapsed*refillRate))
		entry.lastUpdated = nowSec
	}

	if entry.tokens >= requested {
		entry.tokens -= requested
		m.data[key] = entry
		// Повертаємо [allowed=1, remaining, wait_time=0]
		return []any{int64(1), int64(entry.tokens), int64(0)}, nil
	}

	needed := requested - entry.tokens
	waitSeconds := math.Ceil(needed / refillRate)
	m.data[key] = entry
	// Повертаємо [allowed=0, remaining, wait_time]
	return []any{int64(0), int64(entry.tokens), int64(waitSeconds)}, nil
}
