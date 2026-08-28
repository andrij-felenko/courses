// Go: Створення замовлення та збереження події в Outbox у межах однієї локальної транзакції
func (s *OrderService) CreateOrderOutbox(ctx context.Context, orderID, userID, itemID string, amount int64) error {
    tx, err := s.db.BeginTx(ctx, nil)
    if err != nil {
        return fmt.Errorf("помилка відкриття транзакції: %w", err)
    }
    defer tx.Rollback()

    // 1. Запис замовлення у тимчасовому статусі PENDING
    _, err = tx.ExecContext(ctx, 
        "INSERT INTO orders (id, user_id, item_id, amount, status) VALUES ($1, $2, $3, $4, 'PENDING')",
        orderID, userID, itemID, amount)
    if err != nil {
        return fmt.Errorf("помилка створення PENDING замовлення: %w", err)
    }

    // 2. Атомарний запис події у локальну таблицю Outbox у ТІЙ СМІЙ транзакції БД
    eventPayload := fmt.Sprintf(`{"order_id":"%s","user_id":"%s","item_id":"%s","amount":%d}`, 
        orderID, userID, itemID, amount)
    
    _, err = tx.ExecContext(ctx, 
        "INSERT INTO outbox (id, aggregate_type, aggregate_id, type, payload, created_at) VALUES ($1, 'Order', $2, 'OrderCreated', $3, NOW())",
        uuid.New().String(), orderID, eventPayload)
    if err != nil {
        return fmt.Errorf("помилка запису в outbox: %w", err)
    }

    // Коміт гарантує: подія в Outbox з'явиться ТІЛЬКИ якщо замовлення збережено в БД
    return tx.Commit()
}
