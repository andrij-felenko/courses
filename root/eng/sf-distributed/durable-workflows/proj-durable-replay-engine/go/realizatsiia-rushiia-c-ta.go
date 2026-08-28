package main

import (
	"errors"
	"fmt"
)

// Типи подій в історії
type EventType int

const (
	EventWorkflowStarted EventType = iota
	EventActivityScheduled
	EventActivityCompleted
)

type WorkflowEvent struct {
	Type         EventType
	ActivityName string
	Input        string
	Result       string
}

var ErrYield = errors.New("execution yielded")

// WorkflowContext керує детермінованим відтворенням
type WorkflowContext struct {
	history     []WorkflowEvent
	newEvents   []WorkflowEvent
	replayIndex int
}

func NewWorkflowContext(history []WorkflowEvent) *WorkflowContext {
	return &WorkflowContext{history: history}
}

// ExecuteActivity перевіряє історію перед реальним виконанням
func (ctx *WorkflowContext) ExecuteActivity(name, input string) (string, error) {
	if ctx.replayIndex < len(ctx.history) {
		event := ctx.history[ctx.replayIndex]
		if event.Type == EventActivityCompleted {
			if event.ActivityName != name {
				return "", fmt.Errorf("non-determinism: expected %s, got %s", event.ActivityName, name)
			}
			ctx.replayIndex++
			return event.Result, nil
		}
		if event.Type == EventActivityScheduled {
			ctx.replayIndex++
			return "", ErrYield
		}
	}

	ctx.newEvents = append(ctx.newEvents, WorkflowEvent{
		Type:         EventActivityScheduled,
		ActivityName: name,
		Input:        input,
	})
	return "", ErrYield
}

// Функція бізнес-процесу
func OrderFulfillmentWorkflow(ctx *WorkflowContext, orderID string) (string, error) {
	payRes, err := ctx.ExecuteActivity("ProcessPayment", orderID+":amount=500")
	if err != nil {
		return "", err
	}

	invRes, err := ctx.ExecuteActivity("ReserveInventory", orderID+":item=SKU-99")
	if err != nil {
		return "", err
	}

	shipRes, err := ctx.ExecuteActivity("CreateShippingLabel", orderID+":addr=Kyiv")
	if err != nil {
		return "", err
	}

	return fmt.Sprintf("Order %s done: %s, %s, %s", orderID, payRes, invRes, shipRes), nil
}
