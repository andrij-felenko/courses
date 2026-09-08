package main

import (
	"context"
	"errors"
	"sync"
	"sync/atomic"
	"time"
)

var (
	// ErrCircuitOpen повертається, коли контур розімкнено й запити відхиляються.
	ErrCircuitOpen = errors.New("circuit breaker: контур розімкнено (OPEN), провайдер недоступний")
)

// State позначає поточний стан вимикача навантаження.
type State int32

const (
	StateClosed State = iota
	StateOpen
	StateHalfOpen
)

func (s State) String() string {
	switch s {
	case StateClosed:
		return "CLOSED"
	case StateOpen:
		return "OPEN"
	case StateHalfOpen:
		return "HALF_OPEN"
	default:
		return "UNKNOWN"
	}
}

// CircuitBreakerConfig визначає параметри ковзного вікна та переходів станів.
type CircuitBreakerConfig struct {
	WindowSize         int           // Розмір ковзного вікна викликів
	FailureThreshold   float64       // Поріг частки збоїв для розмикання (наприклад, 0.5 = 50%)
	SlowCallDuration   time.Duration // Поріг визнання виклику повільним
	SlowCallThreshold  float64       // Поріг частки повільних викликів для розмикання
	OpenTimeout        time.Duration // Час перебування у стані OPEN перед спробою HALF_OPEN
	HalfOpenProbeCount int           // Кількість тестових зондів Бернуллі в HALF_OPEN
}

// SlidingWindow — кільцевий буфер викликів для фіксації статистики.
type SlidingWindow struct {
	size       int
	slots      []bool // true = успіх, false = відмова або повільний виклик
	head       int
	count      int
	failureCnt int
	mu         sync.Mutex
}

func NewSlidingWindow(size int) *SlidingWindow {
	return &SlidingWindow{
		size:  size,
		slots: make([]bool, size),
	}
}

func (w *SlidingWindow) Record(success bool) {
	w.mu.Lock()
	defer w.mu.Unlock()

	if w.count >= w.size {
		oldest := w.slots[w.head]
		if !oldest {
			w.failureCnt--
		}
	} else {
		w.count++
	}

	w.slots[w.head] = success
	if !success {
		w.failureCnt++
	}

	w.head = (w.head + 1) % w.size
}

func (w *SlidingWindow) FailureRate() float64 {
	w.mu.Lock()
	defer w.mu.Unlock()
	// Закон великих чисел: вимагаємо мінімальний обсяг спостережень для усунення дисперсії
	if w.count < w.size/2 {
		return 0.0
	}
	return float64(w.failureCnt) / float64(w.count)
}

func (w *SlidingWindow) Reset() {
	w.mu.Lock()
	defer w.mu.Unlock()
	w.head = 0
	w.count = 0
	w.failureCnt = 0
	for i := range w.slots {
		w.slots[i] = false
	}
}

// CircuitBreaker реалізує автомат станів вимикача навантаження на ковзному вікні.
type CircuitBreaker struct {
	config          CircuitBreakerConfig
	state           int32 // атомарний State
	window          *SlidingWindow
	openedAt        time.Time
	halfOpenProbes  int32
	halfOpenSuccess int32
	mu              sync.RWMutex
}

// NewCircuitBreaker створює новий екземпляр вимикача навантаження.
func NewCircuitBreaker(cfg CircuitBreakerConfig) *CircuitBreaker {
	return &CircuitBreaker{
		config: cfg,
		state:  int32(StateClosed),
		window: NewSlidingWindow(cfg.WindowSize),
	}
}

// GetState повертає поточний стан автомата з урахуванням таймера відновлення.
func (cb *CircuitBreaker) GetState() State {
	cur := State(atomic.LoadInt32(&cb.state))
	if cur == StateOpen {
		cb.mu.RLock()
		openedAt := cb.openedAt
		cb.mu.RUnlock()

		if time.Since(openedAt) >= cb.config.OpenTimeout {
			// Час очікування минув — переводимо в HALF_OPEN для тестового зондування
			if atomic.CompareAndSwapInt32(&cb.state, int32(StateOpen), int32(StateHalfOpen)) {
				atomic.StoreInt32(&cb.halfOpenProbes, 0)
				atomic.StoreInt32(&cb.halfOpenSuccess, 0)
				return StateHalfOpen
			}
		}
	}
	return State(atomic.LoadInt32(&cb.state))
}

// Execute пропускає дію fn крізь захисний фільтр станів контуру.
func (cb *CircuitBreaker) Execute(ctx context.Context, fn func(ctx context.Context) (Response, error)) (Response, error) {
	st := cb.GetState()

	switch st {
	case StateOpen:
		return Response{}, ErrCircuitOpen

	case StateHalfOpen:
		probes := atomic.AddInt32(&cb.halfOpenProbes, 1)
		if int(probes) > cb.config.HalfOpenProbeCount {
			return Response{}, ErrCircuitOpen
		}

		start := time.Now()
		resp, err := fn(ctx)
		dur := time.Since(start)

		isSuccess := (err == nil && dur <= cb.config.SlowCallDuration)
		cb.recordHalfOpenResult(isSuccess)
		return resp, err

	default: // StateClosed
		start := time.Now()
		resp, err := fn(ctx)
		dur := time.Since(start)

		isSuccess := (err == nil && dur <= cb.config.SlowCallDuration)
		cb.window.Record(isSuccess)

		if cb.window.FailureRate() >= cb.config.FailureThreshold {
			cb.tripToOpen()
		}
		return resp, err
	}
}

func (cb *CircuitBreaker) tripToOpen() {
	if atomic.CompareAndSwapInt32(&cb.state, int32(StateClosed), int32(StateOpen)) {
		cb.mu.Lock()
		cb.openedAt = time.Now()
		cb.mu.Unlock()
	}
}

func (cb *CircuitBreaker) recordHalfOpenResult(success bool) {
	if !success {
		// Будь-який одиничний збій тестового зонда миттєво повертає контур у стан OPEN
		atomic.StoreInt32(&cb.state, int32(StateOpen))
		cb.mu.Lock()
		cb.openedAt = time.Now()
		cb.mu.Unlock()
		return
	}

	succ := atomic.AddInt32(&cb.halfOpenSuccess, 1)
	if int(succ) >= cb.config.HalfOpenProbeCount {
		// Усі зонди схеми Бернуллі успішні — відновлюємо стан CLOSED
		cb.window.Reset()
		atomic.StoreInt32(&cb.state, int32(StateClosed))
	}
}\n
