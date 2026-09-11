package boundary

import (
	"context"
	"errors"
	"math/rand"
	"sync"
	"time"
)

// PolicyBuilder конструює політики стійкості через плавний інтерфейс.
type PolicyBuilder[T any] struct {
	perAttemptTimeout time.Duration
	overallTimeout    time.Duration
	maxRetries        int
	initialBackoff    time.Duration
	circuitThreshold  int
	circuitResetTime  time.Duration
	fallbackFn        FallbackFunc[T]
}

func NewPolicy[T any]() *PolicyBuilder[T] {
	return &PolicyBuilder[T]{
		perAttemptTimeout: 500 * time.Millisecond,
		overallTimeout:    2 * time.Second,
		maxRetries:        2,
		initialBackoff:    50 * time.Millisecond,
		circuitThreshold:  5,
		circuitResetTime:  10 * time.Second,
	}
}

func (b *PolicyBuilder[T]) WithTimeouts(perAttempt, overall time.Duration) *PolicyBuilder[T] {
	b.perAttemptTimeout = perAttempt
	b.overallTimeout = overall
	return b
}

func (b *PolicyBuilder[T]) WithRetry(maxRetries int, initialBackoff time.Duration) *PolicyBuilder[T] {
	b.maxRetries = maxRetries
	b.initialBackoff = initialBackoff
	return b
}

func (b *PolicyBuilder[T]) WithFallback(fn FallbackFunc[T]) *PolicyBuilder[T] {
	b.fallbackFn = fn
	return b
}

// ResilientExecutor виконує операції відповідно до скомпільованого ланцюга захисту.
type ResilientExecutor[T any] struct {
	cfg PolicyBuilder[T]
	mu  sync.Mutex
	// Тут ініціалізується внутрішній стан автомата Circuit Breaker
	consecutiveFailures int
	circuitOpenUntil    time.Time
}

func (b *PolicyBuilder[T]) Build() *ResilientExecutor[T] {
	return &ResilientExecutor[T]{cfg: *b}
}

// Execute запускає операцію крізь сформований ланцюг захисту.
func (e *ResilientExecutor[T]) Execute(
	ctx context.Context,
	action func(ctx context.Context) (T, error),
) ResilientResult[T] {
	start := time.Now()

	// 1. Перевірка Circuit Breaker
	e.mu.Lock()
	if time.Now().Before(e.circuitOpenUntil) {
		e.mu.Unlock()
		return e.applyFallback(ctx, errors.New("circuit breaker is OPEN"), StatusCircuitOpen, 0, start)
	}
	e.mu.Unlock()

	// 2. Встановлення загального таймауту
	overallCtx, cancelOverall := context.WithTimeout(ctx, e.cfg.overallTimeout)
	defer cancelOverall()

	var lastErr error
	attempts := 0

	// 3. Цикл повторних спроб
	for attempts <= e.cfg.maxRetries {
		attempts++

		// 4. Встановлення таймауту на окрему спробу
		attemptCtx, cancelAttempt := context.WithTimeout(overallCtx, e.cfg.perAttemptTimeout)
		val, err := action(attemptCtx)
		cancelAttempt()

		if err == nil {
			e.onSuccess()
			return ResilientResult[T]{
				Value:         val,
				IsFallback:    false,
				Status:        StatusSuccess,
				Attempts:      attempts,
				ExecutionTime: time.Since(start),
			}
		}

		lastErr = err

		// Якщо загальний дедлайн вичерпано — припиняємо ретраї
		if overallCtx.Err() != nil {
			break
		}

		// Пауза між спробами з дрижанням (Decorrelated Jitter)
		if attempts <= e.cfg.maxRetries {
			backoff := e.cfg.initialBackoff * time.Duration(1<<attempts)
			jitter := time.Duration(rand.Int63n(int64(backoff / 2)))
			select {
			case <-overallCtx.Done():
				break
			case <-time.After(backoff/2 + jitter):
			}
		}
	}

	// Фіксація збою для автомата розриву
	e.onFailure()

	status := StatusRetriesExceeded
	if overallCtx.Err() != nil {
		status = StatusTimeout
	}

	return e.applyFallback(ctx, lastErr, status, attempts, start)
}

func (e *ResilientExecutor[T]) onSuccess() {
	e.mu.Lock()
	defer e.mu.Unlock()
	e.consecutiveFailures = 0
}

func (e *ResilientExecutor[T]) onFailure() {
	e.mu.Lock()
	defer e.mu.Unlock()
	e.consecutiveFailures++
	if e.consecutiveFailures >= e.cfg.circuitThreshold {
		e.circuitOpenUntil = time.Now().Add(e.cfg.circuitResetTime)
	}
}

func (e *ResilientExecutor[T]) applyFallback(
	ctx context.Context,
	origErr error,
	status BoundaryStatus,
	attempts int,
	start time.Time,
) ResilientResult[T] {
	if e.cfg.fallbackFn != nil {
		val, fbErr := e.cfg.fallbackFn(ctx, origErr)
		if fbErr == nil {
			return ResilientResult[T]{
				Value:         val,
				IsFallback:    true,
				Status:        StatusFallbackApplied,
				Attempts:      attempts,
				ExecutionTime: time.Since(start),
				OriginalErr:   origErr,
			}
		}
	}

	var zero T
	return ResilientResult[T]{
		Value:         zero,
		IsFallback:    false,
		Status:        status,
		Attempts:      attempts,
		ExecutionTime: time.Since(start),
		OriginalErr:   origErr,
	}
}
