package resilience

import (
	"errors"
	"sync/atomic"
	"time"
)

type State uint32

const (
	StateClosed State = iota
	StateOpen
	StateHalfOpen
)

const (
	windowSize = 64
	windowMask = windowSize - 1
)

var (
	ErrCircuitBreakerOpen = errors.New("circuit breaker is open: request rejected")
)

type Config struct {
	FailureRateThreshold   uint32
	MinimumNumberOfCalls   uint64
	WaitDurationInOpen     time.Duration
	PermittedHalfOpenCalls uint32
}

type CircuitBreaker struct {
	config              Config
	state               atomic.Uint32
	headIndex           atomic.Uint64
	ringBuffer          [windowSize]atomic.Bool
	lastStateChangeUnix atomic.Int64
	halfOpenProbes      atomic.Uint32
}

func NewCircuitBreaker(cfg Config) *CircuitBreaker {
	cb := &CircuitBreaker{
		config: cfg,
	}
	cb.state.Store(uint32(StateClosed))
	cb.lastStateChangeUnix.Store(time.Now().UnixNano())
	return cb
}

func (cb *CircuitBreaker) AllowRequest() bool {
	currentState := State(cb.state.Load())

	if currentState == StateClosed {
		return true
	}

	if currentState == StateOpen {
		now := time.Now().UnixNano()
		lastChange := cb.lastStateChangeUnix.Load()
		if time.Duration(now-lastChange) >= cb.config.WaitDurationInOpen {
			if cb.state.CompareAndSwap(uint32(StateOpen), uint32(StateHalfOpen)) {
				cb.lastStateChangeUnix.Store(now)
				cb.halfOpenProbes.Store(0)
			}
			return cb.AllowRequest()
		}
		return false
	}

	if currentState == StateHalfOpen {
		probeID := cb.halfOpenProbes.Add(1)
		return probeID <= cb.config.PermittedHalfOpenCalls
	}

	return false
}

func (cb *CircuitBreaker) RecordResult(isFailure bool) {
	currentState := State(cb.state.Load())

	if currentState == StateHalfOpen {
		if isFailure {
			if cb.state.CompareAndSwap(uint32(StateHalfOpen), uint32(StateOpen)) {
				cb.lastStateChangeUnix.Store(time.Now().UnixNano())
			}
		} else {
			if cb.halfOpenProbes.Load() >= cb.config.PermittedHalfOpenCalls {
				if cb.state.CompareAndSwap(uint32(StateHalfOpen), uint32(StateClosed)) {
					cb.lastStateChangeUnix.Store(time.Now().UnixNano())
					cb.headIndex.Store(0)
					for i := 0; i < windowSize; i++ {
						cb.ringBuffer[i].Store(false)
					}
				}
			}
		}
		return
	}

	if currentState == StateClosed {
		idx := cb.headIndex.Add(1) - 1
		cb.ringBuffer[idx&windowMask].Store(isFailure)

		total := idx + 1
		if total >= cb.config.MinimumNumberOfCalls {
			activeWindow := uint64(windowSize)
			if total < uint64(windowSize) {
				activeWindow = total
			}

			var failures uint64
			for i := uint64(0); i < activeWindow; i++ {
				if cb.ringBuffer[i].Load() {
					failures++
				}
			}

			rate := uint32((failures * 100) / activeWindow)
			if rate >= cb.config.FailureRateThreshold {
				if cb.state.CompareAndSwap(uint32(StateClosed), uint32(StateOpen)) {
					cb.lastStateChangeUnix.Store(time.Now().UnixNano())
				}
			}
		}
	}
}

func (cb *CircuitBreaker) Execute(action func() error, fallback func(err error) error) error {
	if !cb.AllowRequest() {
		return fallback(ErrCircuitBreakerOpen)
	}

	err := action()
	cb.RecordResult(err != nil)
	if err != nil {
		return fallback(err)
	}
	return nil
}
