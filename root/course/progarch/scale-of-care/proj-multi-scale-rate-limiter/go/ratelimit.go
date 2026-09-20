package main

import (
	"context"
	"errors"
	"time"
)

// FallbackStrategy визначає поведінку системи у разі відмови або недоступності розподіленого координатора.
type FallbackStrategy int

const (
	// FailOpen дозволяє запити під час аварії зовнішнього сховища (пріоритет доступності для клієнтів).
	FailOpen FallbackStrategy = iota

	// FailClosed блокує запити під час аварії зовнішнього сховища (пріоритет захисту внутрішніх ресурсів).
	FailClosed
)

// String повертає людиночитабельну назву стратегії аварійної деградації.
func (s FallbackStrategy) String() string {
	switch s {
	case FailOpen:
		return "Fail-Open (пріоритет доступності)"
	case FailClosed:
		return "Fail-Closed (пріоритет захисту)"
	default:
		return "Невідома стратегія"
	}
}

var (
	// ErrRedisUnavailable сигналізує про мережеву помилку або таймаут зв'язку з Redis.
	ErrRedisUnavailable = errors.New("redis координатор недоступний або перевищено таймаут з'єднання")

	// ErrCircuitBreakerOpen сигналізує про те, що ланцюг запобіжника розімкнено для ізоляції збою.
	ErrCircuitBreakerOpen = errors.New("ланцюг circuit breaker розімкнено: виклики тимчасово ізольовано")

	// ErrRateLimitExceeded сигналізує про вичерпання допустимої квоти запитів.
	ErrRateLimitExceeded = errors.New("перевищено допустиму частоту запитів (rate limit exceeded)")
)

// Decision містить вердикт перевірки ліміту та супутні інженерні метрики для аналізу системи.
type Decision struct {
	Allowed     bool          // Чи дозволено виконання запиту
	Remaining   int64         // Залишок доступних токенів у бакеті
	WaitTime    time.Duration // Рекомендований час очікування до появи достатньої квоти
	IsFallback  bool          // Чи прийнято вердикт аварійною стратегією при відмові координатора
	DurationRTT time.Duration // Затримка на перевірку квоти (наносекунди для пам'яті, RTT для мережі)
	Reason      string        // Інженерне пояснення прийнятого вердикту
}

// Limiter — уніфікований інтерфейсний контракт обмежувача частоти запитів.
// Приховує масштаб реалізації (локальний безблокувальний чи мережевий кластерний) за однаковою сигнатурою.
type Limiter interface {
	// Allow перевіряє можливість списання вказаної кількості токенів за ключем.
	Allow(ctx context.Context, key string, tokens int64) (Decision, error)
}
