package main

import (
	"context"
	"fmt"
	"time"
)

// luaTokenBucketScript — виробничий атомарний скрипт для Redis
const luaTokenBucketScript = `
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

// RedisLimiter — розподілений обмежувач частоти з захистом від мережевих відмов.
type RedisLimiter struct {
	client   RedisCommander
	capacity float64
	rate     float64
	timeout  time.Duration
	fallback FallbackStrategy
}

// NewRedisLimiter створює розподілений обмежувач для Redis.
func NewRedisLimiter(client RedisCommander, capacity float64, rate float64, timeout time.Duration, fallback FallbackStrategy) *RedisLimiter {
	return &RedisLimiter{
		client:   client,
		capacity: capacity,
		rate:     rate,
		timeout:  timeout,
		fallback: fallback,
	}
}

// Allow узгоджує ліміт через Redis і захищає систему аварійною стратегією при мережевих збоях.
func (r *RedisLimiter) Allow(ctx context.Context, key string, tokens int64) (Decision, error) {
	// Ізолюємо мережевий виклик суворим таймаутом
	callCtx, cancel := context.WithTimeout(ctx, r.timeout)
	defer cancel()

	nowSec := float64(time.Now().UnixNano()) / 1e9

	rawRes, err := r.client.Eval(callCtx, luaTokenBucketScript, []string{"ratelimit:" + key},
		r.capacity, r.rate, nowSec, float64(tokens))

	if err != nil {
		// Обробка мережевого збою або вичерпання таймауту
		switch r.fallback {
		case FailOpen:
			return Decision{
				Allowed:    true,
				Remaining:  0,
				WaitTime:   0,
				IsFallback: true,
				Reason:     fmt.Sprintf("Мережевий збій Redis (%v). Аварійна стратегія Fail-Open: запит пропущено", err),
			}, nil
		case FailClosed:
			return Decision{
				Allowed:    false,
				Remaining:  0,
				WaitTime:   r.timeout,
				IsFallback: true,
				Reason:     fmt.Sprintf("Мережевий збій Redis (%v). Аварійна стратегія Fail-Closed: запит заблоковано", err),
			}, ErrRedisUnavailable
		}
	}

	resSlice, ok := rawRes.([]any)
	if !ok || len(resSlice) < 3 {
		return Decision{}, fmt.Errorf("некоректна відповідь Lua-скрипта Redis")
	}

	allowed := resSlice[0].(int64) == 1
	remaining := resSlice[1].(int64)
	waitSec := resSlice[2].(int64)

	reason := "Розподілену квоту узгоджено через кластер Redis"
	if !allowed {
		reason = fmt.Sprintf("Перевищено розподілений ліміт кластера (залишок: %d)", remaining)
	}

	return Decision{
		Allowed:    allowed,
		Remaining:  remaining,
		WaitTime:   time.Duration(waitSec) * time.Second,
		IsFallback: false,
		Reason:     reason,
	}, nil
}
