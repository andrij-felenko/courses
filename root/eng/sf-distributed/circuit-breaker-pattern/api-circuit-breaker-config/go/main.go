package resilience

import (
	"context"
	"time"
)

type ICircuitBreaker interface {
	// Основний цикл перевірки та запису
	AllowRequest() bool
	RecordSuccess(duration time.Duration)
	RecordError(duration time.Duration, err error)

	// Запит стану та метрик
	GetState() State
	GetMetrics() Metrics

	// Операційне управління
	TransitionToDisabled()
	TransitionToForcedOpen()
	Reset()

	// Обгортка для виконання функцій
	Execute(ctx context.Context, action func(ctx context.Context) error) error
}
