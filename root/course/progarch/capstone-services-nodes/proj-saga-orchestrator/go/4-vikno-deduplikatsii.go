func (w *WebhookWorker) ProcessEvent(ctx context.Context, evt OutboxEvent) error {
	key := fmt.Sprintf("dedup:event:%s", evt.ID)
	ok, err := w.redisClient.SetNX(ctx, key, "1", 24*time.Hour).Result()
	if err != nil {
		return fmt.Errorf("redis dedup check failed: %w", err)
	}
	if !ok {
		log.Printf("[DEDUP] Skipping duplicate event %s", evt.ID)
		return nil // Дублікат пропущено
	}

	return w.sendWebhookHTTP(ctx, evt)
}
