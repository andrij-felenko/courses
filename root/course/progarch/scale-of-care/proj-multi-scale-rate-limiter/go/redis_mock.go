package main

import (
	"context"
	"errors"
	"math"
	"sync"
	"time"
)

// RedisCommander визначає контракт для виклику команд і Lua-скриптів у Redis.
type RedisCommander interface {
	Eval(ctx context.Context, script string, keys []string, args ...any) (any, error)
	SetSimulateError(err error)
	SetSimulateLatency(d time.Duration)
}

// redisEntry зберігає стан розподіленого ліміту в пам'яті емулятора.
type redisEntry struct {
	tokens      float64
	lastUpdated float64 // unix-час у секундах
}

// MockRedisClient — in-memory емулятор Redis для ізольованого тестування без зовнішнього сервера.
type MockRedisClient struct {
	mu              sync.Mutex
	data            map[string]redisEntry
	simulateErr     error
	simulateLatency time.Duration
}

// NewMockRedisClient створює новий тестовий клієнт Redis.
func NewMockRedisClient() *MockRedisClient {
	return &MockRedisClient{
		data: make(map[string]redisEntry),
	}
}

func (m *MockRedisClient) SetSimulateError(err error) {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.simulateErr = err
}

func (m *MockRedisClient) SetSimulateLatency(d time.Duration) {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.simulateLatency = d
}

// Eval емулює атомарне виконання Lua-скрипта Token Bucket у Redis з перевіркою контексту.
func (m *MockRedisClient) Eval(ctx context.Context, script string, keys []string, args ...any) (any, error) {
	m.mu.Lock()
	simErr := m.simulateErr
	latency := m.simulateLatency
	m.mu.Unlock()

	// Симуляція мережевої затримки з підтримкою скасування через context.Deadline
	if latency > 0 {
		select {
		case <-time.After(latency):
		case <-ctx.Done():
			return nil, ctx.Err()
		}
	}

	// Симуляція збою мережі або аварії вузла Redis
	if simErr != nil {
		return nil, simErr
	}

	if len(keys) == 0 || len(args) < 4 {
		return nil, errors.New("недостатньо аргументів для Lua-скрипта")
	}

	key := keys[0]
	capacity := args[0].(float64)
	refillRate := args[1].(float64)
	now := args[2].(float64)
	requested := args[3].(float64)

	m.mu.Lock()
	defer m.mu.Unlock()

	entry, exists := m.data[key]
	if !exists {
		entry = redisEntry{
			tokens:      capacity,
			lastUpdated: now,
		}
	} else {
		elapsed := math.Max(0, now-entry.lastUpdated)
		entry.tokens = math.Min(capacity, entry.tokens+(elapsed*refillRate))
		entry.lastUpdated = now
	}

	if entry.tokens >= requested {
		entry.tokens -= requested
		m.data[key] = entry
		// Повертаємо [allowed=1, remaining, wait_time=0]
		return []any{int64(1), int64(entry.tokens), int64(0)}, nil
	}

	needed := requested - entry.tokens
	waitTime := math.Ceil(needed / refillRate)
	m.data[key] = entry
	// Повертаємо [allowed=0, remaining, wait_time]
	return []any{int64(0), int64(entry.tokens), int64(waitTime)}, nil
}
