package main

import (
	"context"
	"fmt"
	"sync/atomic"
	"time"
)

// bucketState зберігає знімок стану токенів та мітку часу останнього поповнення.
type bucketState struct {
	tokens     float64
	lastRefill time.Time
}

// AtomicTokenBucket — локальний процесорний обмежувач на базі атомарних операцій без м'ютексів.
type AtomicTokenBucket struct {
	capacity   float64
	refillRate float64 // швидкість генерації токенів за секунду
	state      atomic.Pointer[bucketState]
}

// NewAtomicTokenBucket створює новий безблокувальний Token Bucket.
func NewAtomicTokenBucket(capacity float64, refillRate float64) *AtomicTokenBucket {
	b := &AtomicTokenBucket{
		capacity:   capacity,
		refillRate: refillRate,
	}
	initial := &bucketState{
		tokens:     capacity,
		lastRefill: time.Now(),
	}
	b.state.Store(initial)
	return b
}

// Allow атомарно перевіряє та списує токени через цикл Compare-And-Swap (CAS).
func (b *AtomicTokenBucket) Allow(ctx context.Context, key string, tokens int64) (Decision, error) {
	reqTokens := float64(tokens)
	for {
		oldState := b.state.Load()
		now := time.Now()
		elapsed := now.Sub(oldState.lastRefill).Seconds()

		// Поповнюємо відро пропорційно до часу, що минув
		currentTokens := oldState.tokens + (elapsed * b.refillRate)
		if currentTokens > b.capacity {
			currentTokens = b.capacity
		}

		// Якщо токенів недостатньо для запиту
		if currentTokens < reqTokens {
			missing := reqTokens - currentTokens
			waitTime := time.Duration((missing / b.refillRate) * float64(time.Second))
			return Decision{
				Allowed:    false,
				Remaining:  int64(currentTokens),
				WaitTime:   waitTime,
				IsFallback: false,
				Reason:     fmt.Sprintf("Локальний ліміт вичерпано: доступно %.1f токенів, потрібно %d", currentTokens, tokens),
			}, nil
		}

		// Формуємо новий стан після списання
		newState := &bucketState{
			tokens:     currentTokens - reqTokens,
			lastRefill: now,
		}

		// Атомарна заміна покажчика без блокування потоків
		if b.state.CompareAndSwap(oldState, newState) {
			return Decision{
				Allowed:    true,
				Remaining:  int64(newState.tokens),
				WaitTime:   0,
				IsFallback: false,
				Reason:     "Локальну квоту успішно надано в пам'яті процесу",
			}, nil
		}
		// Якщо інша горутина змінила стан раніше — цикл повторюється без дедлоків
	}
}
