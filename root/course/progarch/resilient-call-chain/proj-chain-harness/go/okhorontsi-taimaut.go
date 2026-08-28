// ТАЙМАУТ: спрацьовує на витраченому ЧАСІ, байдуже, ok спроба чи ні.
func WithTimeout(inner Call, limit int) Call {
	return func(cl *Clock) (Result, error) {
		res, err := inner(cl)
		if res.Latency > limit {
			cl.Now += limit // прочекали рівно стелю
			return Result{Latency: limit}, &Failure{Kind: "timeout", Retryable: true}
		}
		cl.Now += res.Latency // встигли — платимо реальну ціну
		return res, err
	}
}

// ЗАПОБІЖНИК: автомат closed → open → half. Мьютекс — бо в бою кличуть з багатьох горутин.
type Breaker struct {
	mu                    sync.Mutex
	state                 string // "closed" | "open" | "half"
	fails, openedAt       int
	failsToOpen, cooldown int
}

func (b *Breaker) Wrap(inner Call) Call {
	return func(cl *Clock) (Result, error) {
		b.mu.Lock()
		if b.state == "open" {
			if cl.Now-b.openedAt < b.cooldown { // ще кулдаун — КОРОТИМО
				b.mu.Unlock()
				return Result{}, &Failure{Kind: "circuit-open", Retryable: false}
			}
			b.state = "half" // час на одну пробу
		}
		b.mu.Unlock()

		res, err := inner(cl) // лок НЕ тримаємо під час виклику

		b.mu.Lock()
		defer b.mu.Unlock()
		if err == nil {
			b.state, b.fails = "closed", 0 // одужав
			return res, nil
		}
		b.fails++
		if b.state == "half" || b.fails >= b.failsToOpen {
			b.state, b.openedAt, b.fails = "open", cl.Now, 0
		}
		return res, err
	}
}

// ПОВТОР ПІД БЮДЖЕТОМ, свідомий дедлайну й сигналу «не повторюй».
type Budget struct {
	mu             sync.Mutex
	ratio          float64
	calls, retries int
}

func (b *Budget) allow() bool {
	b.mu.Lock(); defer b.mu.Unlock()
	return float64(b.retries) < b.ratio*float64(b.calls) // ≤10% трафіку
}
func (b *Budget) record(isRetry bool) {
	b.mu.Lock(); defer b.mu.Unlock()
	b.calls++
	if isRetry {
		b.retries++
	}
}

func WithRetry(inner Call, tries, minWork int, b *Budget) Call {
	return func(cl *Clock) (Result, error) {
		if cl.Deadline-cl.Now < minWork { // приречена робота
			return Result{}, &Failure{Kind: "deadline", Retryable: false}
		}
		res, err := inner(cl)
		b.record(false)
		for a := 1; a < tries && err != nil && retryable(err) &&
			cl.Deadline-cl.Now >= minWork && b.allow(); a++ {
			b.record(true)
			res, err = inner(cl)
		}
		return res, err
	}
}
