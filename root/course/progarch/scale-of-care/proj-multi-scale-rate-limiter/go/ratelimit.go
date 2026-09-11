package main

import (
	"context"
	"errors"
	"time"
)

// FallbackStrategy визначає поведінку системи у разі відмови розподіленого координатора.
type FallbackStrategy int

const (
	// FailOpen дозволяє запити під час аварії зовнішнього сховища (пріоритет доступності).
	FailOpen FallbackStrategy = iota
	// FailClosed блокує запити під час аварії зовнішнього сховища (пріоритет захисту ресурсів).
	FailClosed
)

var (
	// ErrRedisUnavailable сигналізує про мережеву помилку або таймаут зв'язку з Redis.
	ErrRedisUnavailable = errors.New("redis недоступний або перевищено таймаут з'єднання")
	// ErrRateLimitExceeded сигналізує про вичерпання ліміту запитів.
	ErrRateLimitExceeded = errors.New("перевищено допустиму частоту запитів")
)

// Decision містить вердикт перевірки ліміту та метадані для клієнта.
type Decision struct {
	Allowed    bool          // Чи дозволено виконання запиту
	Remaining  int64         // Залишок доступних токенів
	WaitTime   time.Duration // Рекомендований час очікування до появи квоти
	IsFallback bool          // Чи прийнято рішення аварійною стратегією при збої
	Reason     string        // Інженерне пояснення рішення
}

// Limiter — єдиний інтерфейс для обмежувачів частоти запитів різного масштабу.
type Limiter interface {
	// Allow перевіряє можливість списання вказаної кількості токенів за ключем.
	Allow(ctx context.Context, key string, tokens int64) (Decision, error)
}
