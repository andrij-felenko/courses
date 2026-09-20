package main

import (
	"context"
	"fmt"
	"math"
	"sync/atomic"
	"time"
)

// bucketState зберігає незмінний знімок стану бакета: залишок токенів та час останнього поповнення.
// Незмінність структури унеможливлює стан гонки при паралельному читанні різними горутинами.
type bucketState struct {
	tokens     float64
	lastRefill time.Time
}

// AtomicTokenBucket — процесний обмежувач частоти на базі атомарних покажчиків sync/atomic та циклу CAS.
// Забезпечує наносекундні затримки без використання м'ютексів і важких фонових горутин-таймерів.
type AtomicTokenBucket struct {
	capacity   float64
	refillRate float64 // швидкість поповнення: токенів за секунду
	state      atomic.Pointer[bucketState]
}

// NewAtomicTokenBucket створює новий процесний безблокувальний Token Bucket.
func NewAtomicTokenBucket(capacity float64, refillRate float64) *AtomicTokenBucket {
	b := &AtomicTokenBucket{
		capacity:   capacity,
		refillRate: refillRate,
	}
	initialState := &bucketState{
		tokens:     capacity,
		lastRefill: time.Now(),
	}
	b.state.Store(initialState)
	return b
}

// Allow атомарно перевіряє та списує токени через безблокувальний цикл Compare-And-Swap (CAS).
func (b *AtomicTokenBucket) Allow(ctx context.Context, key string, tokens int64) (Decision, error) {
	start := time.Now()
	reqTokens := float64(tokens)

	for {
		// Підтримка скасування через контекст згідно з уніфікованим інтерфейсом
		if err := ctx.Err(); err != nil {
			return Decision{
				Allowed:     false,
				Remaining:   0,
				WaitTime:    0,
				IsFallback:  false,
				DurationRTT: time.Since(start),
				Reason:      fmt.Sprintf("Контекст скасовано до завершення операції: %v", err),
			}, err
		}

		oldState := b.state.Load()
		now := time.Now()
		elapsed := now.Sub(oldState.lastRefill).Seconds()

		// Ліниве (lazy) поповнення токенів за час, що минув з останнього запиту
		currentTokens := oldState.tokens + (elapsed * b.refillRate)
		if currentTokens > b.capacity {
			currentTokens = b.capacity
		}

		// Перевірка достатності квоти для поточного запиту
		if currentTokens < reqTokens {
			missing := reqTokens - currentTokens
			waitSeconds := missing / b.refillRate
			waitTime := time.Duration(math.Ceil(waitSeconds * float64(time.Second)))

			return Decision{
				Allowed:     false,
				Remaining:   int64(currentTokens),
				WaitTime:    waitTime,
				IsFallback:  false,
				DurationRTT: time.Since(start),
				Reason:      fmt.Sprintf("Локальний ліміт пам'яті вичерпано: доступно %.2f з потрібних %d", currentTokens, tokens),
			}, nil
		}

		// Формування нового незмінного стану після списання
		newState := &bucketState{
			tokens:     currentTokens - reqTokens,
			lastRefill: now,
		}

		// Атомарна підміна покажчика: спрацьовує лише якщо стан не змінювався іншою горутиною
		if b.state.CompareAndSwap(oldState, newState) {
			return Decision{
				Allowed:     true,
				Remaining:   int64(newState.tokens),
				WaitTime:    0,
				IsFallback:  false,
				DurationRTT: time.Since(start),
				Reason:      "Локальну квоту успішно списано в пам'яті процесу за CAS-цикл",
			}, nil
		}
		// При конфлікті гонки цикл негайно повторюється з актуальним станом
	}
}
