// Go: Атомарне оформлення замовлення у модульному моноліті
func (s *OrderService) CreateOrderMonolith(ctx context.Context, userID string, itemID string, amount int64) error {
    // Відкриття атомарної транзакції в єдиній СУБД
    tx, err := s.db.BeginTx(ctx, &sql.TxOptions{Isolation: sql.LevelReadCommitted})
    if err != nil {
        return fmt.Errorf("помилка відкриття транзакції: %w", err)
    }
    // RAII-подібний захист: Rollback автоматично ігнорується, якщо вже викликано Commit
    defer tx.Rollback()

    // Крок 1. Перевірка та списання балансу користувача
    res, err := tx.ExecContext(ctx, 
        "UPDATE accounts SET balance = balance - $1 WHERE id = $2 AND balance >= $1", 
        amount, userID)
    if err != nil {
        return fmt.Errorf("помилка виконання SQL списання: %w", err)
    }
    if rows, _ := res.RowsAffected(); rows == 0 {
        return errors.New("недостатньо коштів на балансі користувача")
    }

    // Крок 2. Резервування позиції товару на складі
    res, err = tx.ExecContext(ctx, 
        "UPDATE inventory SET stock = stock - 1 WHERE item_id = $1 AND stock >= 1", 
        itemID)
    if err != nil {
        return fmt.Errorf("помилка виконання SQL резервування: %w", err)
    }
    if rows, _ := res.RowsAffected(); rows == 0 {
        return errors.New("товару немає в наявності на складі")
    }

    // Крок 3. Створення підтвердженого запису замовлення
    _, err = tx.ExecContext(ctx, 
        "INSERT INTO orders (user_id, item_id, amount, status) VALUES ($1, $2, $3, 'COMPLETED')", 
        userID, itemID, amount)
    if err != nil {
        return fmt.Errorf("помилка створення запису замовлення: %w", err)
    }

    // Фіксація всіх трьох оновлень атомарно
    if err := tx.Commit(); err != nil {
        return fmt.Errorf("помилка фіксації транзакції: %w", err)
    }
    return nil
}
