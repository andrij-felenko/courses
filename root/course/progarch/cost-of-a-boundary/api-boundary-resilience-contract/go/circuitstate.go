package boundary

import (
	"errors"
	"sync"
	"sync/atomic"
	"time"
)

// CircuitState представляє можливі стани автомата розривача ланцюга.
type CircuitState int32

const (
	StateClosed CircuitState = iota
	StateOpen
	StateHalfOpen
)

func (s CircuitState) String() string {
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

// CircuitBreakerConfig містить налаштування порогів розривача.
type CircuitBreakerConfig struct {
	FailureRateThreshold float64       // Частка невдач для розриву (наприклад, 0.5)
	MinimumThroughput    int           // Мінімальна кількість запитів у вікні
	SleepWindow          time.Duration // Тривалість очікування в стані Open
	HalfOpenProbeLimit   int           // Кількість пробних викликів у Half-Open
}

// CircuitBreaker реалізує потокобезпечний автомат захисту на межі.
type CircuitBreaker struct {
	cfg            CircuitBreakerConfig
	mu             sync.Mutex
	state          int32 // атомарне поле CircuitState
	openedAt       time.Time
	totalRequests  int
	failedRequests int
	halfOpenProbes int
	halfOpenPassed int
}

func NewCircuitBreaker(cfg CircuitBreakerConfig) *CircuitBreaker {
	return &CircuitBreaker{
		cfg:   cfg,
		state: int32(StateClosed),
	}
}

// State повертає поточний стан автомата з урахуванням часу сну.
func (cb *CircuitBreaker) State() CircuitState {
	cur := CircuitState(atomic.LoadInt32(&cb.state))
	if cur == StateOpen {
		cb.mu.Lock()
		defer cb.mu.Unlock()
		if CircuitState(cb.state) == StateOpen && time.Since(cb.openedAt) >= cb.cfg.SleepWindow {
			cb.state = int32(StateHalfOpen)
			cb.halfOpenProbes = 0
			cb.halfOpenPassed = 0
			return StateHalfOpen
		}
	}
	return cur
}

// AllowExecution перевіряє, чи дозволено пропустити виклик до межі.
func (cb *CircuitBreaker) AllowExecution() bool {
	st := cb.State()
	if st == StateClosed {
		return true
	}
	if st == StateOpen {
		return false
	}

	// У стані Half-Open дозволяємо лише визначену кількість пробних запитів
	cb.mu.Lock()
	defer cb.mu.Unlock()
	if cb.state == int32(StateHalfOpen) {
		if cb.halfOpenProbes < cb.cfg.HalfOpenProbeLimit {
			cb.halfOpenProbes++
			return true
		}
		return false
	}
	return cb.state == int32(StateClosed)
}

// RecordResult фіксує успіх або відмову виконаної операції.
func (cb *CircuitBreaker) RecordResult(success bool) {
	cb.mu.Lock()
	defer cb.mu.Unlock()

	st := CircuitState(cb.state)
	if st == StateHalfOpen {
		if !success {
			// Навіть один збій у Half-Open негайно повертає автомат у стан Open
			cb.state = int32(StateOpen)
			cb.openedAt = time.Now()
			return
		}
		cb.halfOpenPassed++
		if cb.halfOpenPassed >= cb.cfg.HalfOpenProbeLimit {
			// Усі пробні запити успішні — відновлюємо роботу сервісу
			cb.state = int32(StateClosed)
			cb.totalRequests = 0
			cb.failedRequests = 0
		}
		return
	}

	if st == StateClosed {
		cb.totalRequests++
		if !success {
			cb.failedRequests++
		}
		// Перевірка порогів розриву ланцюга
		if cb.totalRequests >= cb.cfg.MinimumThroughput {
			rate := float64(cb.failedRequests) / float64(cb.totalRequests)
			if rate >= cb.cfg.FailureRateThreshold {
				cb.state = int32(StateOpen)
				cb.openedAt = time.Now()
			}
		}
	}
}

// Execute загортає виконання виклику в правила автомату CircuitBreaker.
func (cb *CircuitBreaker) Execute(action func() error) error {
	if !cb.AllowExecution() {
		return errors.New("CIRCUIT_OPEN: виклик відхилено автоматом розриву ланцюга")
	}

	err := action()
	cb.RecordResult(err == nil)
	return err
}
