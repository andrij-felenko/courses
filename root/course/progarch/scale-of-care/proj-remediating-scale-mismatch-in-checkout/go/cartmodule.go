package checkout

import (
	"context"
	"database/sql"
	"fmt"
)

// CartModule визначає внутрішній інтерфейс модуля кошика.
type CartModule interface {
	LockAndFetchItems(ctx context.Context, tx *sql.Tx, cartID string) ([]string, error)
	ClearCart(ctx context.Context, tx *sql.Tx, cartID string) error
}

// InventoryModule визначає внутрішній інтерфейс модуля складу.
type InventoryModule interface {
	ReserveItems(ctx context.Context, tx *sql.Tx, itemIDs []string) error
}

// EventBus визначає внутрішній шинний інтерфейс для асинхронних подій.
type EventBus interface {
	Publish(eventType string, payload any)
}

// MonolithicCheckoutService об'єднує модулі під захистом єдиного SQL-транзакційного контексту.
type MonolithicCheckoutService struct {
	db        *sql.DB
	cart      CartModule
	inventory InventoryModule
	eventBus  EventBus
}

func NewMonolithicCheckoutService(db *sql.DB, c CartModule, i InventoryModule, eb EventBus) *MonolithicCheckoutService {
	return &MonolithicCheckoutService{
		db:        db,
		cart:      c,
		inventory: i,
		eventBus:  eb,
	}
}

// ExecuteCheckout виконує атомарну локальну ACID-транзакцію для всього процесу оформлення.
func (s *MonolithicCheckoutService) ExecuteCheckout(ctx context.Context, cartID string, accountID string, amount float64) error {
	// Відкриваємо єдину локальну транзакцію бази даних
	tx, err := s.db.BeginTx(ctx, &sql.TxOptions{Isolation: sql.LevelReadCommitted})
	if err != nil {
		return fmt.Errorf("помилка відкриття транзакції: %w", err)
	}

	// Автоматичний ROLLBACK при будь-якій паніці або помилці
	defer func() {
		_ = tx.Rollback()
	}()

	// Крок 1: Блокування кошика в межах транзакції
	items, err := s.cart.LockAndFetchItems(ctx, tx, cartID)
	if err != nil {
		return fmt.Errorf("помилка кошика: %w", err)
	}

	// Крок 2: Резервування товарів у тій самій транзакції
	if err := s.inventory.ReserveItems(ctx, tx, items); err != nil {
		return fmt.Errorf("нестача товарів на складі: %w", err)
	}

	// Крок 3: Очищення кошика в тій самій транзакції
	if err := s.cart.ClearCart(ctx, tx, cartID); err != nil {
		return fmt.Errorf("помилка очищення кошика: %w", err)
	}

	// Фіксація атомарної транзакції
	if err := tx.Commit(); err != nil {
		return fmt.Errorf("помилка фіксації транзакції: %w", err)
	}

	// Асинхронний побічний ефект запускається ТІЛЬКИ після успішного COMMIT
	s.eventBus.Publish("OrderCompleted", map[string]any{
		"cartID":    cartID,
		"accountID": accountID,
		"amount":    amount,
	})

	return nil
}
