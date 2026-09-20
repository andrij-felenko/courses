package main

import (
	"context"
	"fmt"
	"sync"
	"time"
)

// luaRateLimiterScript — виробничий атомарний Lua-скрипт для Redis.
// Виконує поповнення та списання токенів безпосередньо в рушії Redis за один мережевий RTT.
const luaRateLimiterScript = `
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local requested = tonumber(ARGV[4])

local data = redis.call('HMGET', key, 'tokens', 'last_updated')
local tokens = tonumber(data[1])
local last_updated = tonumber(data[2])

if tokens == nil then
    tokens = capacity
    last_updated = now
else
    local elapsed = math.max(0, now - last_updated)
    tokens = math.min(capacity, tokens + elapsed * refill_rate)
    last_updated = now
end

if tokens >= requested then
    tokens = tokens - requested
    redis.call('HMSET', key, 'tokens', tokens, 'last_updated', last_updated)
    redis.call('EXPIRE', key, math.ceil(capacity / refill_rate) * 2)
    return {1, math.floor(tokens), 0}
else
    local needed = requested - tokens
    local wait_time = math.ceil(needed / refill_rate)
    return {0, math.floor(tokens), wait_time}
end
`

// RedisLimiter — кластерний обмежувач частоти, що координує квоти через спільний Redis.
// Захищений запобіжником Circuit Breaker для швидкої ізоляції збоїв та підтримує
// аварійні політики Fail-Open та Fail-Closed.
type RedisLimiter struct {
	client          RedisClient
	breaker         *CircuitBreaker
	capacity        float64
	refillRate      float64
	timeout         time.Duration
	fallback        FallbackStrategy
	mu              sync.RWMutex
	lastMeasuredRTT time.Duration
}

// NewRedisLimiter створює екземпляр розподіленого обмежувача частоти для Redis.
func NewRedisLimiter(
	client RedisClient,
	breaker *CircuitBreaker,
	capacity float64,
	refillRate float64,
	timeout time.Duration,
	fallback FallbackStrategy,
) *RedisLimiter {
	if breaker == nil {
		breaker = NewCircuitBreaker(CircuitBreakerConfig{
			FailureThreshold: 3,
			RecoveryTimeout:  500 * time.Millisecond,
			SuccessThreshold: 1,
		})
	}

	return &RedisLimiter{
		client:     client,
		breaker:    breaker,
		capacity:   capacity,
		refillRate: refillRate,
		timeout:    timeout,
		fallback:   fallback,
	}
}

// LastMeasuredRTT повертає затримку останнього мережевого звернення до Redis.
func (r *RedisLimiter) LastMeasuredRTT() time.Duration {
	r.mu.RLock()
	defer r.mu.RUnlock()
	return r.lastMeasuredRTT
}

// Breaker повертає підключений запобіжник обмежувача.
func (r *RedisLimiter) Breaker() *CircuitBreaker {
	return r.breaker
}

// Allow узгоджує квоту через спільний координатор Redis із захистом від каскадних збоїв.
func (r *RedisLimiter) Allow(ctx context.Context, key string, tokens int64) (Decision, error) {
	start := time.Now()
	nowSec := float64(time.Now().UnixNano()) / 1e9

	var rawResult any

	// Виконуємо виклик через автомат станів запобіжника (Circuit Breaker)
	execErr := r.breaker.Execute(func() error {
		// Обмежуємо час очікування відповіді суворим таймаутом контексту
		callCtx, cancel := context.WithTimeout(ctx, r.timeout)
		defer cancel()

		var err error
		rawResult, err = r.client.Eval(
			callCtx,
			luaRateLimiterScript,
			[]string{"ratelimit:" + key},
			r.capacity,
			r.refillRate,
			nowSec,
			float64(tokens),
		)
		return err
	})

	rttDuration := time.Since(start)
	r.mu.Lock()
	r.lastMeasuredRTT = rttDuration
	r.mu.Unlock()

	// Якщо виник збій мережі, перевищено таймаут або розімкнено запобіжник
	if execErr != nil {
		switch r.fallback {
		case FailOpen:
			// Пріоритет доступності: пропускаємо запит клієнта, фіксуючи прапорець деградації
			return Decision{
				Allowed:     true,
				Remaining:   0,
				WaitTime:    0,
				IsFallback:  true,
				DurationRTT: rttDuration,
				Reason:      fmt.Sprintf("Аварія координатора (%v). Fail-Open: запит пропущено для збереження доступності", execErr),
			}, nil

		case FailClosed:
			// Пріоритет захисту ресурсів: блокуємо запит, захищаючи внутрішні бази від сплеску
			return Decision{
				Allowed:     false,
				Remaining:   0,
				WaitTime:    r.timeout,
				IsFallback:  true,
				DurationRTT: rttDuration,
				Reason:      fmt.Sprintf("Аварія координатора (%v). Fail-Closed: запит заблоковано задля захисту системи", execErr),
			}, execErr
		}
	}

	// Парсимо результат атомарного Lua-скрипта Redis
	resSlice, ok := rawResult.([]any)
	if !ok || len(resSlice) < 3 {
		return Decision{
			Allowed:     false,
			Remaining:   0,
			WaitTime:    0,
			IsFallback:  false,
			DurationRTT: rttDuration,
			Reason:      "Некоректний формат відповіді від Lua-скрипта Redis",
		}, fmt.Errorf("некоректна відповідь Redis: %v", rawResult)
	}

	allowed := resSlice[0].(int64) == 1
	remaining := resSlice[1].(int64)
	waitSec := resSlice[2].(int64)

	reason := fmt.Sprintf("Кластерний ліміт Redis успішно узгоджено (RTT: %s)", rttDuration)
	if !allowed {
		reason = fmt.Sprintf("Перевищено кластерний ліміт Redis: залишок %d токенів, повторити через %dс", remaining, waitSec)
	}

	return Decision{
		Allowed:     allowed,
		Remaining:   remaining,
		WaitTime:    time.Duration(waitSec) * time.Second,
		IsFallback:  false,
		DurationRTT: rttDuration,
		Reason:      reason,
	}, nil
}
