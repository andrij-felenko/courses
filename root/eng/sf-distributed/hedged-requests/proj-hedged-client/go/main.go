package main

import (
	"context"
	"errors"
	"fmt"
	"sync"
	"sync/atomic"
	"time"
)

// TokenBucket забезпечує атомарний ліміт частки геджування
type TokenBucket struct {
	maxTokens   float64
	refillRatio float64
	tokens      uint64 // зберігається як помножене на 1000 ціле для атомарності
}

func NewTokenBucket(maxTokens, refillRatio float64) *TokenBucket {
	tb := &TokenBucket{
		maxTokens:   maxTokens,
		refillRatio: refillRatio,
	}
	atomic.StoreUint64(&tb.tokens, uint64(maxTokens*1000))
	return tb
}

func (tb *TokenBucket) TryConsume() bool {
	for {
		curr := atomic.LoadUint64(&tb.tokens)
		if curr < 1000 {
			return false // менше 1.0 токена
		}
		next := curr - 1000
		if atomic.CompareAndSwapUint64(&tb.tokens, curr, next) {
			return true
		}
	}
}

func (tb *TokenBucket) RecordSuccess() {
	add := uint64(tb.refillRatio * 1000)
	max := uint64(tb.maxTokens * 1000)
	for {
		curr := atomic.LoadUint64(&tb.tokens)
		next := curr + add
		if next > max {
			next = max
		}
		if atomic.CompareAndSwapUint64(&tb.tokens, curr, next) {
			return
		}
	}
}

// CallReplica симулює клієнтський RPC із підтримкою Context Cancellation
func CallReplica(ctx context.Context, endpoint string, delay time.Duration) (string, error) {
	select {
	case <-time.After(delay):
		return fmt.Sprintf("Response from %s", endpoint), nil
	case <-ctx.Done():
		return "", ctx.Err()
	}
}

// ExecuteHedgedRequest виконує виклик із відкладеним геджуванням і бюджетом
func ExecuteHedgedRequest(
	ctx context.Context,
	replicas []string,
	hedgeDelay time.Duration,
	budget *TokenBucket,
) (string, error) {
	if len(replicas) == 0 {
		return "", errors.New("empty replicas list")
	}

	// Створюємо контекст скасування для другорядних гілок
	reqCtx, cancel := context.WithCancel(ctx)
	defer cancel()

	type result struct {
		val string
		err error
	}
	resChan := make(chan result, len(replicas))
	var once sync.Once

	sendRPC := func(endpoint string, simulatedDelay time.Duration) {
		val, err := CallReplica(reqCtx, endpoint, simulatedDelay)
		if err == nil {
			once.Do(func() {
				resChan <- result{val: val}
				cancel() // миттєво скасовуємо іншу спробу
			})
		}
	}

	// 1. Старт основного запиту
	go sendRPC(replicas[0], 80*time.Millisecond)

	// 2. Таймер відкладеного геджу
	hedgeTimer := time.NewTimer(hedgeDelay)
	defer hedgeTimer.Stop()

	// Очікуємо або відповіді, або таймера P95
	select {
	case res := <-resChan:
		budget.RecordSuccess()
		return res.val, nil
	case <-hedgeTimer.C:
		// Таймер сплив — перевіряємо бюджет
		if len(replicas) > 1 && budget.TryConsume() {
			go sendRPC(replicas[1], 10*time.Millisecond)
		}
	case <-ctx.Done():
		return "", ctx.Err()
	}

	// 3. Очікування фінальної відповіді від будь-якої репліки
	select {
	case res := <-resChan:
		return res.val, nil
	case <-ctx.Done():
		return "", ctx.Err()
	}
}

func main() {
	budget := NewTokenBucket(10.0, 0.1)
	replicas := []string{"replica-1.internal:50051", "replica-2.internal:50051"}

	ctx, cancel := context.WithTimeout(context.Background(), 200*time.Millisecond)
	defer cancel()

	res, err := ExecuteHedgedRequest(ctx, replicas, 25*time.Millisecond, budget)
	if err != nil {
		fmt.Printf("Помилка (Go): %v\n", err)
	} else {
		fmt.Printf("Успіх (Go): %s\n", res)
	}
}
