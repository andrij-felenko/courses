package main

import (
	"sync"
	"time"
)

// CircuitState визначає стан автомата запобіжника.
type CircuitState int

const (
	// StateClosed — нормальний стан: виклики безперешкодно надсилаються до координатора.
	StateClosed CircuitState = iota

	// StateOpen — стан аварії: виклики відсікаються миттєво для збереження ресурсів і запобігання підвисанню горутин.
	StateOpen

	// StateHalfOpen — стан зондування: один пробний запит для перевірки доступності координатора після паузи.
	StateHalfOpen
)

// String повертає текстову назву стану запобіжника.
func (s CircuitState) String() string {
	switch s {
	case StateClosed:
		return "Closed (Норма)"
	case StateOpen:
		return "Open (Розімкнено)"
	case StateHalfOpen:
		return "Half-Open (Пробний)"
	default:
		return "Unknown"
	}
}

// CircuitBreakerConfig містить порогові параметри роботи запобіжника.
type CircuitBreakerConfig struct {
	FailureThreshold int           // Кількість послідовних помилок для переходу в стан Open
	RecoveryTimeout  time.Duration // Час перебування у стані Open перед спробою Half-Open
	SuccessThreshold int           // Кількість успішних пробних викликів для повного повернення в Closed
}

// CircuitBreaker ізолює збої зовнішнього координатора, захищаючи пул горутин від зависання на мережевих таймаутах.
type CircuitBreaker struct {
	mu                sync.Mutex
	state             CircuitState
	consecutiveErrors int
	successfulProbes  int
	lastStateChange   time.Time
	config            CircuitBreakerConfig
}

// NewCircuitBreaker створює запобіжник із заданою конфігурацією у стані Closed.
func NewCircuitBreaker(cfg CircuitBreakerConfig) *CircuitBreaker {
	if cfg.FailureThreshold <= 0 {
		cfg.FailureThreshold = 3
	}
	if cfg.RecoveryTimeout <= 0 {
		cfg.RecoveryTimeout = 1 * time.Second
	}
	if cfg.SuccessThreshold <= 0 {
		cfg.SuccessThreshold = 1
	}

	return &CircuitBreaker{
		state:           StateClosed,
		lastStateChange: time.Now(),
		config:          cfg,
	}
}

// State повертає поточний стан запобіжника з урахуванням часу очікування відновлення.
func (cb *CircuitBreaker) State() CircuitState {
	cb.mu.Lock()
	defer cb.mu.Unlock()

	if cb.state == StateOpen && time.Since(cb.lastStateChange) >= cb.config.RecoveryTimeout {
		cb.state = StateHalfOpen
		cb.successfulProbes = 0
		cb.lastStateChange = time.Now()
	}

	return cb.state
}

// Execute огортає виклик зовнішнього ресурсу автоматом запобіжника.
func (cb *CircuitBreaker) Execute(fn func() error) error {
	cb.mu.Lock()

	// Перевіряємо, чи настав час перевести автомат з Open у Half-Open
	if cb.state == StateOpen {
		if time.Since(cb.lastStateChange) >= cb.config.RecoveryTimeout {
			cb.state = StateHalfOpen
			cb.successfulProbes = 0
			cb.lastStateChange = time.Now()
		} else {
			cb.mu.Unlock()
			// Швидка відмова: не марнуємо час на мережевий виклик, миттєво повертаємо помилку ізоляції
			return ErrCircuitBreakerOpen
		}
	}

	cb.mu.Unlock()

	// Виконуємо безпосередній виклик (наприклад, звернення до Redis)
	err := fn()

	cb.mu.Lock()
	defer cb.mu.Unlock()

	if err != nil {
		cb.handleFailure()
		return err
	}

	cb.handleSuccess()
	return nil
}

func (cb *CircuitBreaker) handleFailure() {
	switch cb.state {
	case StateClosed:
		cb.consecutiveErrors++
		if cb.consecutiveErrors >= cb.config.FailureThreshold {
			cb.state = StateOpen
			cb.lastStateChange = time.Now()
			cb.consecutiveErrors = 0
		}
	case StateHalfOpen:
		// Невдача під час зондування негайно повертає ланцюг у стан Open
		cb.state = StateOpen
		cb.lastStateChange = time.Now()
		cb.successfulProbes = 0
	}
}

func (cb *CircuitBreaker) handleSuccess() {
	switch cb.state {
	case StateClosed:
		cb.consecutiveErrors = 0
	case StateHalfOpen:
		cb.successfulProbes++
		if cb.successfulProbes >= cb.config.SuccessThreshold {
			cb.state = StateClosed
			cb.lastStateChange = time.Now()
			cb.consecutiveErrors = 0
			cb.successfulProbes = 0
		}
	}
}
