package main

import (
	"context"
	"errors"
	"fmt"
	"math/rand"
	"time"
)

var (
	// ErrAllProvidersFailed повертається, коли обидва провайдери недоступні.
	ErrAllProvidersFailed = errors.New("dispatcher: вичерпано всі резервні провайдери та захисні контури")
)

// ProtectedProvider поєднує зовнішнього провайдера, семафорний Bulkhead та Circuit Breaker.
type ProtectedProvider struct {
	Provider       Provider
	Bulkhead       *Bulkhead
	CircuitBreaker *CircuitBreaker
}

// Dispatcher реалізує патерн Active-Passive маршрутизатора з керованою деградацією.
type Dispatcher struct {
	primary    ProtectedProvider
	secondary  ProtectedProvider
	classifier *ErrorClassifier
	maxRetries int
	baseDelay  time.Duration
}

// NewDispatcher ініціалізує маршрутизатор з основним та резервним провайдерами.
func NewDispatcher(
	primary ProtectedProvider,
	secondary ProtectedProvider,
	classifier *ErrorClassifier,
	maxRetries int,
	baseDelay time.Duration,
) *Dispatcher {
	return &Dispatcher{
		primary:    primary,
		secondary:  secondary,
		classifier: classifier,
		maxRetries: maxRetries,
		baseDelay:  baseDelay,
	}
}

// Execute спрямовує запит через основний провайдер, а при збої виконує прозорий failover на резервного.
func (d *Dispatcher) Execute(ctx context.Context, req Request) (Response, error) {
	// Спроба 1: звернення до основного (Active) провайдера з політикою ретраїв
	resp, err := d.executeWithResilience(ctx, d.primary, req)
	if err == nil {
		return resp, nil
	}

	policy := d.classifier.Classify(req, resp, err)
	// Якщо класифікатор блокує повтор через ризик подвійної мутації — failover заборонено!
	if policy == RetryDeny {
		return Response{}, fmt.Errorf("dispatcher: первинний збій, перемикання заборонено через ризик дублювання: %w", err)
	}

	// Failover: автоматичне перемикання на резервного (Passive) провайдера
	respSec, errSec := d.executeWithResilience(ctx, d.secondary, req)
	if errSec == nil {
		return respSec, nil
	}

	return Response{}, fmt.Errorf("%w: первинний [%v], резервний [%v]", ErrAllProvidersFailed, err, errSec)
}

func (d *Dispatcher) executeWithResilience(ctx context.Context, target ProtectedProvider, req Request) (Response, error) {
	var lastErr error
	var lastResp Response

	for attempt := 0; attempt <= d.maxRetries; attempt++ {
		if attempt > 0 {
			// Розрахунок затримки за схемою Full Jitter: rand(0, baseDelay * 2^(attempt-1))
			jitterWait := d.computeFullJitter(attempt)
			select {
			case <-time.After(jitterWait):
			case <-ctx.Done():
				return Response{}, ctx.Err()
			}
		}

		// Захищений виклик: спочатку Bulkhead (семафор), всередині — CircuitBreaker
		resp, err := target.Bulkhead.Execute(ctx, func(bCtx context.Context) (Response, error) {
			return target.CircuitBreaker.Execute(bCtx, func(cbCtx context.Context) (Response, error) {
				return target.Provider.Execute(cbCtx, req)
			})
		})

		if err == nil {
			return resp, nil
		}

		lastResp = resp
		lastErr = err

		// Перевірка класифікатора: чи дозволено повторювати цей виклик
		policy := d.classifier.Classify(req, resp, err)
		if policy != RetrySafe {
			break
		}
	}

	return lastResp, lastErr
}

// computeFullJitter обчислює випадкову експоненційну затримку за алгоритмом Full Jitter.
func (d *Dispatcher) computeFullJitter(attempt int) time.Duration {
	maxWait := d.baseDelay * (1 << (attempt - 1))
	if maxWait <= 0 {
		return d.baseDelay
	}
	r := rand.New(rand.NewSource(time.Now().UnixNano()))
	return time.Duration(r.Int63n(int64(maxWait)))
}\n
