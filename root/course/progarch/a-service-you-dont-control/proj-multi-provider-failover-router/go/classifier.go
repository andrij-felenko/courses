package main

import (
	"context"
	"errors"
	"net"
	"strings"
)

// RetryPolicy визначає стратегію обробки результату операції.
type RetryPolicy int

const (
	RetryDeny               RetryPolicy = iota // Повтор заборонено (ризик дублювання мутації або фатальна помилка)
	RetrySafe                                  // Повтор безпечний (транзитний збій, читання або наявний IdempotencyKey)
	RetryRequiresFallback                      // Потрібно виконати failover на резерв або повернути деградовану відповідь
)

func (p RetryPolicy) String() string {
	switch p {
	case RetryDeny:
		return "DENY"
	case RetrySafe:
		return "SAFE"
	case RetryRequiresFallback:
		return "FALLBACK"
	default:
		return "UNKNOWN"
	}
}

// ErrorClassifier аналізує тип помилки та контекст запиту для захисту від подвійних мутацій.
type ErrorClassifier struct{}

func NewErrorClassifier() *ErrorClassifier {
	return &ErrorClassifier{}
}

// Classify оцінює можливість безпечного повтору для заданого запиту та помилки.
func (c *ErrorClassifier) Classify(req Request, resp Response, err error) RetryPolicy {
	// Успішна відповідь — повтор не потрібен
	if err == nil && resp.StatusCode >= 200 && resp.StatusCode < 300 {
		return RetryDeny
	}

	// 1. Помилки переповнення перебірки або розімкненого контуру — не спамимо провайдера, а йдемо у Fallback
	if errors.Is(err, ErrBulkheadFull) || errors.Is(err, ErrCircuitOpen) {
		return RetryRequiresFallback
	}

	// 2. Скасування контексту з боку викликувача
	if errors.Is(err, context.Canceled) {
		return RetryDeny
	}

	// 3. Аналіз HTTP статус-кодів
	if resp.StatusCode != 0 {
		// Клієнтські помилки (4xx) — детерміністичні, повтор не змінить результат (крім 429 Rate Limit)
		if resp.StatusCode >= 400 && resp.StatusCode < 500 && resp.StatusCode != 429 {
			return RetryDeny
		}
		// Обмеження частоти (429) або транзитні перевантаження сервера (503/504)
		if resp.StatusCode == 429 || resp.StatusCode == 503 || resp.StatusCode == 504 {
			if req.IsIdempotent || req.IdempotencyKey != "" {
				return RetrySafe
			}
			return RetryRequiresFallback
		}
	}

	// 4. Мережеві помилки з'єднання та таймаутів
	if err != nil {
		var netErr net.Error
		if errors.As(err, &netErr) && netErr.Timeout() {
			// Якщо таймаут стався під час мутуючої дії (POST/PUT) без ключа ідемпотентності —
			// неможливо перевірити, чи виконав сервер транзакцію. Повтор КАТЕГОРИЧНО заборонено!
			if !req.IsIdempotent && req.IdempotencyKey == "" {
				return RetryDeny
			}
			return RetrySafe
		}

		errStr := strings.ToLower(err.Error())
		if strings.Contains(errStr, "connection refused") || strings.Contains(errStr, "reset by peer") {
			if req.IsIdempotent || req.IdempotencyKey != "" {
				return RetrySafe
			}
			return RetryRequiresFallback
		}
	}

	// Безпечні ідемпотентні операції (GET) або наявність токена захисту від дублікатів
	if req.IsIdempotent || req.IdempotencyKey != "" {
		return RetrySafe
	}

	return RetryDeny
}\n
