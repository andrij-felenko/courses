// Go: Обробка компенсуючої події (повернення коштів) з перевіркою ідемпотентності
func (p *PaymentConsumer) HandleRefundCompensation(ctx context.Context, msg KafkaMessage) error {
    var event CompensatePaymentEvent
    if err := json.Unmarshal(msg.Value, &event); err != nil {
        return fmt.Errorf("помилка десеріалізації події: %w", err)
    }

    tx, err := p.db.BeginTx(ctx, nil)
    if err != nil {
        return err
    }
    defer tx.Rollback()

    // 1. Перевірка на повторну обробку події (Idempotency Key Check)
    var processed bool
    err = tx.QueryRowContext(ctx, 
        "SELECT EXISTS(SELECT 1 FROM processed_events WHERE event_id = $1)", 
        msg.EventID).Scan(&processed)
    if err != nil {
        return fmt.Errorf("помилка перевірки ідемпотентності: %w", err)
    }
    if processed {
        // Подія вже була оброблена раніше — мирно пропускаємо дублікат
        return nil 
    }

    // 2. Виконання компенсуючої операції: Повернення коштів на рахунок
    _, err = tx.ExecContext(ctx, 
        "UPDATE accounts SET balance = balance + $1 WHERE id = $2", 
        event.Amount, event.UserID)
    if err != nil {
        return fmt.Errorf("помилка повернення коштів: %w", err)
    }

    // 3. Реєстрація event_id у таблиці оброблених подій для майбутніх перевірок
    _, err = tx.ExecContext(ctx, 
        "INSERT INTO processed_events (event_id, processed_at) VALUES ($1, NOW())", 
        msg.EventID)
    if err != nil {
        return fmt.Errorf("помилка фіксації event_id: %w", err)
    }

    return tx.Commit()
}
