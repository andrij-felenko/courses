package main

import (
	"context"
	"errors"
	"fmt"
	"time"
)

func main() {
	fmt.Println("=== 1. Локальний масштаб: AtomicTokenBucket (sync/atomic) ===")
	// Ємність: 3 токени, поповнення: 1 токен/сек
	localBucket := NewAtomicTokenBucket(3, 1)

	for i := 1; i <= 5; i++ {
		start := time.Now()
		dec, _ := localBucket.Allow(context.Background(), "user-123", 1)
		duration := time.Since(start)

		fmt.Printf("Запит #%d: Дозволено=%-5t | Залишок=%d | Затримка=%-7s | %s\n",
			i, dec.Allowed, dec.Remaining, duration, dec.Reason)
	}

	fmt.Println("\n=== 2. Розподілений масштаб: RedisLimiter (Lua-скрипт) ===")
	mockRedis := NewMockRedisClient()
	mockRedis.SetSimulateLatency(2 * time.Millisecond)

	// Ємність: 5 токенів, поповнення: 2 токени/сек, таймаут: 50мс, Fail-Open
	redisLimiter := NewRedisLimiter(mockRedis, 5, 2, 50*time.Millisecond, FailOpen)

	for i := 1; i <= 3; i++ {
		start := time.Now()
		dec, _ := redisLimiter.Allow(context.Background(), "device-sensor", 2)
		duration := time.Since(start)

		fmt.Printf("Запит #%d: Дозволено=%-5t | Залишок=%d | Затримка=%-7s | %s\n",
			i, dec.Allowed, dec.Remaining, duration, dec.Reason)
	}

	fmt.Println("\n=== 3. Масштаб відмов: реакція на аварію Redis (Fail-Open проти Fail-Closed) ===")
	// Симулюємо мережевий розрив або падіння Redis-сервера
	mockRedis.SetSimulateError(errors.New("connection reset by peer"))

	// 3.1 Стратегія Fail-Open (пріоритет доступності для бізнесу)
	limiterFailOpen := NewRedisLimiter(mockRedis, 5, 2, 50*time.Millisecond, FailOpen)
	decOpen, _ := limiterFailOpen.Allow(context.Background(), "payment-gateway", 1)
	fmt.Printf("[Fail-Open]   Дозволено=%-5t | Fallback=%-5t | %s\n",
		decOpen.Allowed, decOpen.IsFallback, decOpen.Reason)

	// 3.2 Стратегія Fail-Closed (пріоритет захисту від перевантаження)
	limiterFailClosed := NewRedisLimiter(mockRedis, 5, 2, 50*time.Millisecond, FailClosed)
	decClosed, errClosed := limiterFailClosed.Allow(context.Background(), "payment-gateway", 1)
	fmt.Printf("[Fail-Closed] Дозволено=%-5t | Fallback=%-5t | Помилка=%v\n",
		decClosed.Allowed, decClosed.IsFallback, errClosed)

	fmt.Println("\n=== 4. Синтез масштабів: Дворівневий захист (TieredLimiter) ===")
	// Відновлюємо працездатність Redis
	mockRedis.SetSimulateError(nil)
	mockRedis.SetSimulateLatency(1 * time.Millisecond)

	localTier := NewAtomicTokenBucket(2, 1)
	clusterTier := NewRedisLimiter(mockRedis, 10, 5, 50*time.Millisecond, FailOpen)
	tieredLimiter := NewTieredLimiter(localTier, clusterTier)

	// Швидка серія з 4 запитів: перші 2 пройдуть локальний фільтр і Redis, наступні 2 будуть відсічені миттєво в пам'яті
	for i := 1; i <= 4; i++ {
		start := time.Now()
		dec, _ := tieredLimiter.Allow(context.Background(), "smart-lock", 1)
		duration := time.Since(start)

		fmt.Printf("Tiered #%d: Дозволено=%-5t | Затримка=%-7s | %s\n",
			i, dec.Allowed, duration, dec.Reason)
	}
}
