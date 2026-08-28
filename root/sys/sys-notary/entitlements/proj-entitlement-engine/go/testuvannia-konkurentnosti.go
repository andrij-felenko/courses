func TestConcurrentQuotaReservation(t *testing.T) {
	// Ліміт квоти — рівно 10 одиниць
	limit := int64(10)
	var successfulReservations int64

	var wg sync.WaitGroup
	workers := 50 // 50 паралельних запитів одночасно

	for i := 0; i < workers; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			res, err := engine.CheckAndReserveQuota(ctx, "org_test", MetricMonthlyAPICalls, 1, 3600)
			if err == nil && res.Allowed {
				atomic.AddInt64(&successfulReservations, 1)
			}
		}()
	}
	wg.Wait()

	if successfulReservations != limit {
		t.Fatalf("Expected exactly %d successful reservations, got %d (overselling defect!)", limit, successfulReservations)
	}
}
