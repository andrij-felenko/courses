// Наївний клієнт: таймаут → повтор. Але err НЕ означає «не сталося».
func Unlock(ctx context.Context, hub *Hub, lockID string) error {
	for attempt := 1; attempt <= 3; attempt++ {
		err := hub.Send(ctx, Cmd{Name: "unlock", LockID: lockID})
		if err == nil {
			return nil // дійшло — виходимо
		}
		// err — це таймаут. Замок не чіпали чи вже відчинили? Невідомо.
		// Якщо відчинили, а загубилось лише підтвердження — повтор
		// віддає команду вдруге.
	}
	return errors.New("не вдалося за 3 спроби")
}
