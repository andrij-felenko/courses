package boundary

import (
	"context"
	"errors"
	"fmt"
	"time"
)

// BoundaryStatus кодує стан завершення виклику через системну межу.
type BoundaryStatus string

const (
	StatusSuccess          BoundaryStatus = "SUCCESS"
	StatusDeadlineExceeded BoundaryStatus = "DEADLINE_EXCEEDED"
	StatusCancelled        BoundaryStatus = "CANCELLED"
	StatusExecutionFailed  BoundaryStatus = "EXECUTION_FAILED"
)

// BoundaryError описує стандартизовану відмову межі.
type BoundaryError struct {
	Code        BoundaryStatus
	Message     string
	Duration    time.Duration
	IsTransient bool
	Err         error
}

func (e BoundaryError) Error() string {
	return fmt.Sprintf("[%s] %s (тривалість: %v): %v", e.Code, e.Message, e.Duration, e.Err)
}

// Result містить або типізоване значення, або стандартизовану помилку.
type Result[T any] struct {
	Value T
	Error *BoundaryError
}

func (r Result[T]) IsSuccess() bool {
	return r.Error == nil
}

// CallContext несе метадані дедлайну та наскрізного трасування.
type CallContext struct {
	Ctx     context.Context
	TraceID string
	SpanID  string
}

// ResilientExecutor виконує операцію під захистом дедлайну та ізоляції аварій.
type ResilientExecutor struct{}

func NewResilientExecutor() *ResilientExecutor {
	return &ResilientExecutor{}
}

// Execute запускає функцію fn із контролем дедлайну та перехопленням панік.
func (e *ResilientExecutor) Execute(
	callCtx CallContext,
	fn func(ctx context.Context) (any, error),
) Result[any] {
	start := time.Now()

	// Інваріант 1: перевірка дедлайну перед початком виконання
	if err := callCtx.Ctx.Err(); err != nil {
		status := StatusCancelled
		if errors.Is(err, context.DeadlineExceeded) {
			status = StatusDeadlineExceeded
		}
		return Result[any]{
			Error: &BoundaryError{
				Code:        status,
				Message:     "Контекст виклику завершився до запуску дії",
				Duration:    time.Since(start),
				IsTransient: false,
				Err:         err,
			},
		}
	}

	// Канал для отримання результату з окремої горутини
	type execOutcome struct {
		val any
		err error
	}
	ch := make(chan execOutcome, 1)

	go func() {
		defer func() {
			if rec := recover(); rec != nil {
				ch <- execOutcome{
					val: nil,
					err: fmt.Errorf("перехоплено аварійну паніку: %v", rec),
				}
			}
		}()
		val, err := fn(callCtx.Ctx)
		ch <- execOutcome{val: val, err: err}
	}()

	// Очікування результату або вичерпання дедлайну контексту
	select {
	case outcome := <-ch:
		dur := time.Since(start)
		if outcome.err != nil {
			return Result[any]{
				Error: &BoundaryError{
					Code:        StatusExecutionFailed,
					Message:     "Операція завершилася помилкою виконання",
					Duration:    dur,
					IsTransient: true,
					Err:         outcome.err,
				},
			}
		}
		return Result[any]{Value: outcome.val}

	case <-callCtx.Ctx.Done():
		dur := time.Since(start)
		err := callCtx.Ctx.Err()
		status := StatusCancelled
		if errors.Is(err, context.DeadlineExceeded) {
			status = StatusDeadlineExceeded
		}
		return Result[any]{
			Error: &BoundaryError{
				Code:        status,
				Message:     "Перевищено дедлайн під час очікування операції",
				Duration:    dur,
				IsTransient: true,
				Err:         err,
			},
		}
	}
}
