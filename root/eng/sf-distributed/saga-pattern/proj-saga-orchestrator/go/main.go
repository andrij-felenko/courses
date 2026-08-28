package main

import (
	"context"
	"fmt"
	"time"
)

type StepKind int

const (
	Compensable StepKind = iota
	Pivot
	Retryable
)

type StepState string

const (
	StateExecuting    StepState = "EXECUTING"
	StateCompleted    StepState = "COMPLETED"
	StateFailed       StepState = "FAILED"
	StateCompensating StepState = "COMPENSATING"
	StateCompensated  StepState = "COMPENSATED"
)

type StepContext struct {
	SagaID  string
	Payload string
}

type ISagaLog interface {
	LogState(sagaID string, stepIdx int, stepName string, state StepState)
}

type ConsoleSagaLog struct{}

func (l *ConsoleSagaLog) LogState(sagaID string, stepIdx int, stepName string, state StepState) {
	fmt.Printf(" [SEC-LOG] Saga=%s Step[%d]=%s -> State=%s\n", sagaID, stepIdx, stepName, state)
}

type ActionFunc func(ctx context.Context, sCtx *StepContext) error

type SagaStep struct {
	Name       string
	Kind       StepKind
	Action     ActionFunc
	Compensate ActionFunc
}

type SagaOrchestrator struct {
	sagaID string
	steps  []SagaStep
	log    ISagaLog
}

func NewSagaOrchestrator(id string, log ISagaLog) *SagaOrchestrator {
	return &SagaOrchestrator{
		sagaID: id,
		steps:  make([]SagaStep, 0),
		log:    log,
	}
}

func (s *SagaOrchestrator) AddStep(step SagaStep) {
	s.steps = append(s.steps, step)
}

func (s *SagaOrchestrator) Execute(ctx context.Context, sCtx *StepContext) bool {
	fmt.Printf("\n=== Запуск Саги: %s ===\n", s.sagaID)
	sCtx.SagaID = s.sagaID
	lastExecuted := -1
	forwardSuccess := true

	// 1. Прямий хід
	for i, step := range s.steps {
		s.log.LogState(s.sagaID, i, step.Name, StateExecuting)
		var err error
		maxRetries := 1
		if step.Kind == Retryable {
			maxRetries = 3
		}

		for attempt := 1; attempt <= maxRetries; attempt++ {
			if attempt > 1 {
				fmt.Printf("  -> Повтор кроку %s (спроба %d)...\n", step.Name, attempt)
				time.Sleep(50 * time.Millisecond)
			}
			err = step.Action(ctx, sCtx)
			if err == nil {
				break
			}
		}

		if err == nil {
			s.log.LogState(s.sagaID, i, step.Name, StateCompleted)
			lastExecuted = i
		} else {
			s.log.LogState(s.sagaID, i, step.Name, StateFailed)
			fmt.Printf(" [ERROR] Крок %s завершився помилкою: %v\n", step.Name, err)
			forwardSuccess = false
			break
		}
	}

	if forwardSuccess {
		fmt.Printf("=== Сага %s успішно завершена ===\n", s.sagaID)
		return true
	}

	// 2. Зворотний хід (компенсація)
	fmt.Printf("\n--- Запуск каскаду компенсацій для Саги %s ---\n", s.sagaID)
	for i := lastExecuted; i >= 0; i-- {
		step := s.steps[i]
		if step.Compensate != nil {
			s.log.LogState(s.sagaID, i, step.Name, StateCompensating)
			for attempt := 1; attempt <= 5; attempt++ {
				cErr := step.Compensate(ctx, sCtx)
				if cErr == nil {
					break
				}
				fmt.Printf("  [WARN] Збій компенсації %s, спроба %d...\n", step.Name, attempt)
				time.Sleep(50 * time.Millisecond)
			}
			s.log.LogState(s.sagaID, i, step.Name, StateCompensated)
		}
	}

	fmt.Printf("=== Сага %s компенсована (стан узгоджено) ===\n", s.sagaID)
	return false
}

func main() {
	log := &ConsoleSagaLog{}
	ctx := context.Background()

	// Сценарій 1: Успіх
	s1 := NewSagaOrchestrator("ORD-2001", log)
	s1.AddStep(SagaStep{
		Name: "Payment",
		Kind: Compensable,
		Action: func(c context.Context, sc *StepContext) error {
			fmt.Printf("  [Billing] Списано 1500 грн для %s\n", sc.SagaID)
			return nil
		},
		Compensate: func(c context.Context, sc *StepContext) error {
			fmt.Printf("  [Billing-Comp] Повернуто 1500 грн для %s\n", sc.SagaID)
			return nil
		},
	})
	s1.AddStep(SagaStep{
		Name: "Inventory",
		Kind: Pivot,
		Action: func(c context.Context, sc *StepContext) error {
			fmt.Println("  [Warehouse] Товар зарезервовано на складі")
			return nil
		},
	})
	s1.AddStep(SagaStep{
		Name: "Notification",
		Kind: Retryable,
		Action: func(c context.Context, sc *StepContext) error {
			fmt.Println("  [Notifier] Чек надіслано покупцю")
			return nil
		},
	})
	s1.Execute(ctx, &StepContext{Payload: "ok"})

	// Сценарій 2: Відмова складу
	s2 := NewSagaOrchestrator("ORD-2002", log)
	s2.AddStep(SagaStep{
		Name: "Payment",
		Kind: Compensable,
		Action: func(c context.Context, sc *StepContext) error {
			fmt.Printf("  [Billing] Списано 1500 грн для %s\n", sc.SagaID)
			return nil
		},
		Compensate: func(c context.Context, sc *StepContext) error {
			fmt.Printf("  [Billing-Comp] Повернуто 1500 грн для %s\n", sc.SagaID)
			return nil
		},
	})
	s2.AddStep(SagaStep{
		Name: "Inventory",
		Kind: Pivot,
		Action: func(c context.Context, sc *StepContext) error {
			return fmt.Errorf("товару немає в наявності")
		},
	})
	s2.Execute(ctx, &StepContext{Payload: "fail"})
}
