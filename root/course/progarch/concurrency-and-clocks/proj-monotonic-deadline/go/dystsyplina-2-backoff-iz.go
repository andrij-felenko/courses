// Повний джитер (AWS, Marc Brooker): пауза = random(0, min(cap, base·2^attempt)).
func backoff(attempt int, base, cap time.Duration) time.Duration {
	window := base << attempt        // base·2^attempt
	if window <= 0 || window > cap { // <=0 ловить переповнення зсуву на великому attempt
		window = cap
	}
	return time.Duration(rand.Int63n(int64(window))) // рівномірно [0, window)
}

func WithRetry(ctx context.Context, op func(context.Context) error) error {
	const base, cap = 100 * time.Millisecond, 10 * time.Second
	for attempt := 0; ; attempt++ {
		err := op(ctx)
		if err == nil || !retryable(err) {
			return err // успіх або невиправна помилка — не повторюємо
		}
		wait := backoff(attempt, base, cap)

		// КЛЮЧОВЕ: не спати за дедлайн. Якщо пауза довша за залишок бюджету —
		// немає сенсу навіть починати чекати; здаємось зараз.
		if dl, ok := ctx.Deadline(); ok && time.Until(dl) < wait {
			return fmt.Errorf("бюджет вичерпано (лишилось %v < backoff %v): %w",
				time.Until(dl).Round(time.Millisecond), wait, err)
		}
		select {
		case <-time.After(wait): // таймер рантайму — монотонний
		case <-ctx.Done():       // дедлайн або скасування рве паузу негайно
			return ctx.Err()
		}
	}
}
