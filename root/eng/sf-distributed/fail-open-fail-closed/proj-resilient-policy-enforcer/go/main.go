package main

import (
	"context"
	"errors"
	"fmt"
	"sync"
	"sync/atomic"
	"time"
)

// FailureStrategy визначає поведінку під час збою перевірки
type FailureStrategy int

const (
	FailClosed FailureStrategy = iota
	FailOpen
	UseStaleCache
)

type BreakerState int32

const (
	StateClosed BreakerState = iota
	StateOpen
	StateHalfOpen
)

type RequestContext struct {
	RequestID     string
	UserID        string
	Resource      string
	Action        string
	TimeoutBudget time.Duration
}

type PolicyDecision struct {
	Allowed    bool
	Degraded   bool
	Reason     string
	HTTPStatus int
}

type ShadowAuditLog struct {
	RequestID      string
	UserID         string
	Resource       string
	Action         string
	FallbackReason string
	Timestamp      time.Time
}

// ShadowAuditQueue буферизує події для фонової доставки в чергу
type ShadowAuditQueue struct {
	queue chan ShadowAuditLog
}

func NewShadowAuditQueue(capacity int) *ShadowAuditQueue {
	q := &ShadowAuditQueue{
		queue: make(chan ShadowAuditLog, capacity),
	}
	go q.worker()
	return q
}

func (q *ShadowAuditQueue) Push(log ShadowAuditLog) bool {
	select {
	case q.queue <- log:
		return true
	default:
		// Переповнення черги аудиту скидає запис заради збереження пам'яті
		return false
	}
}

func (q *ShadowAuditQueue) worker() {
	for log := range q.queue {
		// Фонова відправка в Kafka або Dead-Letter Queue
		_ = log
	}
}

type RemotePolicyClient interface {
	Evaluate(ctx context.Context, req RequestContext) (bool, error)
}

type cacheEntry struct {
	allowed   bool
	expiresAt time.Time
}

type ResilientPolicyEnforcer struct {
	client          RemotePolicyClient
	strategy        FailureStrategy
	auditQueue      *ShadowAuditQueue
	breakerState    int32
	failureCount    int64
	successCount    int64
	lastStateChange time.Time

	mu    sync.RWMutex
	cache map[string]cacheEntry
}

func NewResilientPolicyEnforcer(
	client RemotePolicyClient,
	strategy FailureStrategy,
	auditQueue *ShadowAuditQueue,
) *ResilientPolicyEnforcer {
	return &ResilientPolicyEnforcer{
		client:          client,
		strategy:        strategy,
		auditQueue:      auditQueue,
		breakerState:    int32(StateClosed),
		lastStateChange: time.Now(),
		cache:           make(map[string]cacheEntry),
	}
}

func (e *ResilientPolicyEnforcer) Enforce(ctx context.Context, req RequestContext) PolicyDecision {
	if e.isBreakerOpen() {
		return e.executeFallback(req, "Circuit breaker is OPEN")
	}

	callCtx, cancel := context.WithTimeout(ctx, req.TimeoutBudget)
	defer cancel()

	decisionChan := make(chan bool, 1)
	errChan := make(chan error, 1)

	go func() {
		allowed, err := e.client.Evaluate(callCtx, req)
		if err != nil {
			errChan <- err
			return
		}
		decisionChan <- allowed
	}()

	select {
	case allowed := <-decisionChan:
		e.recordSuccess()
		e.setCache(req, allowed)
		status := 200
		if !allowed {
			status = 403
		}
		return PolicyDecision{
			Allowed:    allowed,
			Degraded:   false,
			Reason:     "Evaluated by remote engine",
			HTTPStatus: status,
		}

	case err := <-errChan:
		e.recordFailure()
		return e.executeFallback(req, fmt.Sprintf("Engine error: %v", err))

	case <-callCtx.Done():
		e.recordFailure()
		return e.executeFallback(req, "Evaluation deadline exceeded")
	}
}

func (e *ResilientPolicyEnforcer) isBreakerOpen() bool {
	state := BreakerState(atomic.LoadInt32(&e.breakerState))
	if state == StateOpen {
		e.mu.RLock()
		elapsed := time.Since(e.lastStateChange)
		e.mu.RUnlock()

		if elapsed > 15*time.Second {
			atomic.StoreInt32(&e.breakerState, int32(StateHalfOpen))
			return false
		}
		return true
	}
	return false
}

func (e *ResilientPolicyEnforcer) recordFailure() {
	fails := atomic.AddInt64(&e.failureCount, 1)
	state := BreakerState(atomic.LoadInt32(&e.breakerState))

	if fails >= 5 && state == StateClosed {
		atomic.StoreInt32(&e.breakerState, int32(StateOpen))
		e.mu.Lock()
		e.lastStateChange = time.Now()
		e.mu.Unlock()
	} else if state == StateHalfOpen {
		atomic.StoreInt32(&e.breakerState, int32(StateOpen))
		e.mu.Lock()
		e.lastStateChange = time.Now()
		e.mu.Unlock()
	}
}

func (e *ResilientPolicyEnforcer) recordSuccess() {
	state := BreakerState(atomic.LoadInt32(&e.breakerState))
	if state == StateHalfOpen {
		if atomic.AddInt64(&e.successCount, 1) >= 3 {
			atomic.StoreInt32(&e.breakerState, int32(StateClosed))
			atomic.StoreInt64(&e.failureCount, 0)
			atomic.StoreInt64(&e.successCount, 0)
		}
	} else {
		atomic.StoreInt64(&e.failureCount, 0)
	}
}

func (e *ResilientPolicyEnforcer) setCache(req RequestContext, allowed bool) {
	key := fmt.Sprintf("%s:%s:%s", req.UserID, req.Resource, req.Action)
	e.mu.Lock()
	e.cache[key] = cacheEntry{
		allowed:   allowed,
		expiresAt: time.Now().Add(5 * time.Minute),
	}
	e.mu.Unlock()
}

func (e *ResilientPolicyEnforcer) getStaleCache(req RequestContext) (bool, bool) {
	key := fmt.Sprintf("%s:%s:%s", req.UserID, req.Resource, req.Action)
	e.mu.RLock()
	entry, ok := e.cache[key]
	e.mu.RUnlock()
	if ok {
		return entry.allowed, true
	}
	return false, false
}

func (e *ResilientPolicyEnforcer) executeFallback(req RequestContext, reason string) PolicyDecision {
	if e.strategy == UseStaleCache || e.strategy == FailOpen {
		if allowed, ok := e.getStaleCache(req); ok {
			status := 200
			if !allowed {
				status = 403
			}
			return PolicyDecision{
				Allowed:    allowed,
				Degraded:   true,
				Reason:     fmt.Sprintf("Stale cache (%s)", reason),
				HTTPStatus: status,
			}
		}
	}

	if e.strategy == FailOpen {
		e.auditQueue.Push(ShadowAuditLog{
			RequestID:      req.RequestID,
			UserID:         req.UserID,
			Resource:       req.Resource,
			Action:         req.Action,
			FallbackReason: reason,
			Timestamp:      time.Now(),
		})

		return PolicyDecision{
			Allowed:    true,
			Degraded:   true,
			Reason:     fmt.Sprintf("Fail-Open bypass (%s)", reason),
			HTTPStatus: 200,
		}
	}

	return PolicyDecision{
		Allowed:    false,
		Degraded:   true,
		Reason:     fmt.Sprintf("Fail-Closed rejected (%s)", reason),
		HTTPStatus: 503,
	}
}
