package main

import (
	"context"
	"errors"
	"fmt"
	"time"
)

func main() {
	ctx := context.Background()

	fmt.Println("================================================================================")
	fmt.Println("АРХІТЕКТУРНЕ РІШЕННЯ: МАСШТАБ ТУРБОТИ В ОБМЕЖЕННІ ЧАСТОТИ (RATE LIMITING)")
	fmt.Println("================================================================================")

	// -------------------------------------------------------------------------
	// СЦЕНАРІЙ 1: Локальний масштаб — AtomicTokenBucket (in-process, lock-free CAS)
	// -------------------------------------------------------------------------
	fmt.Println("\n--- 1. Локальний масштаб: AtomicTokenBucket (sync/atomic, CAS-цикл) ---")
	fmt.Println("Характеристики: ємність=3, поповнення=1 токен/сек. Очікувана затримка: сотні наносекунд.")

	localLimiter := NewAtomicTokenBucket(3.0, 1.0)

	for i := 1; i <= 5; i++ {
		dec, err := localLimiter.Allow(ctx, "user-42", 1)
		if err != nil {
			fmt.Printf("Запит #%d: помилка: %v\n", i, err)
			continue
		}
		fmt.Printf("Запит #%d: Дозволено=%-5t | Залишок=%d | Затримка=%-9s | %s\n",
			i, dec.Allowed, dec.Remaining, dec.DurationRTT, dec.Reason)
	}

	// -------------------------------------------------------------------------
	// СЦЕНАРІЙ 2: Кластерний масштаб — RedisLimiter (координація між вузлами)
	// -------------------------------------------------------------------------
	fmt.Println("\n--- 2. Кластерний масштаб: RedisLimiter (узгодження через спільний Redis) ---")
	fmt.Println("Характеристики: RTT=3мс, ємність=5, поповнення=2 токени/сек. Очікувана затримка: мілісекунди.")

	mockRedis := NewMockRedisClient()
	mockRedis.SetSimulateLatency(3 * time.Millisecond)

	breakerCfg := CircuitBreakerConfig{
		FailureThreshold: 2,                     // Перехід у Open після 2 помилок
		RecoveryTimeout:  300 * time.Millisecond, // Спроба відновлення через 300мс
		SuccessThreshold: 1,                     // Достатньо 1 успішного виклику для повернення в Closed
	}
	sharedBreaker := NewCircuitBreaker(breakerCfg)

	redisLimiter := NewRedisLimiter(
		mockRedis,
		sharedBreaker,
		5.0,
		2.0,
		50*time.Millisecond,
		FailOpen,
	)

	for i := 1; i <= 3; i++ {
		dec, _ := redisLimiter.Allow(ctx, "api-gateway", 2)
		fmt.Printf("Запит #%d: Дозволено=%-5t | Залишок=%d | Затримка=%-9s | %s\n",
			i, dec.Allowed, dec.Remaining, dec.DurationRTT, dec.Reason)
	}

	// -------------------------------------------------------------------------
	// СЦЕНАРІЙ 3: Мережева аварія та захист запобіжником Circuit Breaker
	// -------------------------------------------------------------------------
	fmt.Println("\n--- 3. Мережева аварія: робота Circuit Breaker та ізоляція збою ---")
	fmt.Println("Симулюємо відмову мережі (network timeout / connection refused)...")
	mockRedis.SetSimulateError(errors.New("connection timeout: dial tcp redis:6379 i/o timeout"))

	fmt.Println("\n3.1 Серія викликів під час аварії (поріг помилок запобіжника = 2):")
	for i := 1; i <= 4; i++ {
		stateBefore := sharedBreaker.State()
		dec, _ := redisLimiter.Allow(ctx, "api-gateway", 1)
		stateAfter := sharedBreaker.State()

		fmt.Printf("Запит #%d | Стан CB: %-15s -> %-15s | Затримка=%-9s | %s\n",
			i, stateBefore, stateAfter, dec.DurationRTT, dec.Reason)
	}
	fmt.Println("Зверніть увагу: перші 2 виклики чекали затримки мережі, а виклики #3 і #4")
	fmt.Println("були ізольовані запобіжником миттєво (мікросекунди!), захистивши горутини сервісу.")

	// -------------------------------------------------------------------------
	// СЦЕНАРІЙ 4: Порівняння аварійних політик Fail-Open проти Fail-Closed
	// -------------------------------------------------------------------------
	fmt.Println("\n--- 4. Політики аварійної деградації при розімкненому запобіжнику (Open) ---")

	// 4.1 Fail-Open (пріоритет доступності для клієнтів: каталог товарів, читання публічних даних)
	limiterFailOpen := NewRedisLimiter(mockRedis, sharedBreaker, 5.0, 2.0, 50*time.Millisecond, FailOpen)
	decOpen, errOpen := limiterFailOpen.Allow(ctx, "catalog-browse", 1)
	fmt.Printf("[Fail-Open  ] Дозволено=%-5t | Fallback=%-5t | Помилка=%-5v | %s\n",
		decOpen.Allowed, decOpen.IsFallback, errOpen, decOpen.Reason)

	// 4.2 Fail-Closed (пріоритет захисту ресурсів: транзакції, списання коштів, ресурсомісткі звіти)
	limiterFailClosed := NewRedisLimiter(mockRedis, sharedBreaker, 5.0, 2.0, 50*time.Millisecond, FailClosed)
	decClosed, errClosed := limiterFailClosed.Allow(ctx, "payment-checkout", 1)
	fmt.Printf("[Fail-Closed] Дозволено=%-5t | Fallback=%-5t | Помилка=%-5v | %s\n",
		decClosed.Allowed, decClosed.IsFallback, errClosed != nil, decClosed.Reason)

	// -------------------------------------------------------------------------
	// СЦЕНАРІЙ 5: Відновлення працездатності координатора (Half-Open -> Closed)
	// -------------------------------------------------------------------------
	fmt.Println("\n--- 5. Автоматичне самовідновлення (Half-Open -> Closed) ---")
	fmt.Println("Усуваємо аварію Redis і очікуємо завершення RecoveryTimeout (300мс)...")
	mockRedis.SetSimulateError(nil)
	time.Sleep(350 * time.Millisecond)

	fmt.Printf("Поточний стан запобіжника перед пробним запитом: %s\n", sharedBreaker.State())

	// Перший пробний запит перевірить зв'язок
	decProbe, _ := redisLimiter.Allow(ctx, "api-gateway", 1)
	fmt.Printf("Пробний запит: Дозволено=%-5t | Стан CB: %-15s | Затримка=%-9s | %s\n",
		decProbe.Allowed, sharedBreaker.State(), decProbe.DurationRTT, decProbe.Reason)

	// Наступний запит виконується у повністю відновленому штатному режимі
	decNormal, _ := redisLimiter.Allow(ctx, "api-gateway", 1)
	fmt.Printf("Штатний запит: Дозволено=%-5t | Стан CB: %-15s | Затримка=%-9s | %s\n",
		decNormal.Allowed, sharedBreaker.State(), decNormal.DurationRTT, decNormal.Reason)

	fmt.Println("\nВисновки:")
	fmt.Println("1. Локальний Token Bucket працює за сотні наносекунд без жодного блокування (sync/atomic CAS).")
	fmt.Println("2. Кластерний RedisLimiter забезпечує єдину глобальну квоту, але вносить накладні витрати RTT (мілісекунди).")
	fmt.Println("3. Circuit Breaker захищає систему від каскадних відмов, замінюючи дорогі мережеві таймаути миттєвою ізоляцією.")
	fmt.Println("4. Політики Fail-Open та Fail-Closed дозволяють усвідомлено обирати між доступністю та захистом ресурсів.")
}
