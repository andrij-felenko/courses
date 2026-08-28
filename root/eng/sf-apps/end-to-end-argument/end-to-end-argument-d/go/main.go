// Клієнт не питає «чи дійшов мій запит», він питає «чи є наслідок».
func Pay(ctx context.Context, gw Gateway, orderID string, amount Money) (Payment, error) {
	key := IdempotencyKey(orderID) // ключ народжується разом з наміром
	var lastErr error
	for attempt := 0; attempt < 5; attempt++ {
		p, err := gw.Charge(ctx, ChargeReq{Key: key, OrderID: orderID, Amount: amount})
		if err == nil {
			return p, nil
		}
		lastErr = err
		if !Retryable(err) {
			break
		}
		time.Sleep(Backoff(attempt))
	}
	// Відповіді немає — але це НЕ означає, що списання не сталося.
	if p, err := gw.FindByKey(ctx, key); err == nil {
		return p, nil // наслідок є: списання відбулося
	}
	return Payment{}, fmt.Errorf("стан платежу %s невідомий: %w", key, lastErr)
}
