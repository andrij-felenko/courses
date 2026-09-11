package checkout

import (
	"context"
	"database/sql"
	"errors"
	"fmt"
	"sync"
	"time"
)

// ErrOutOfStock вказує на недостатню кількість товару на складі.
var ErrOutOfStock = errors.New("недостатньо товару на складі")

// ErrPaymentFailed вказує на відмову платіжного шлюзу або недостатність коштів.
var ErrPaymentFailed = errors.New("платіж не підтверджено")

// CartItem описує позицію в кошику покупця.
type CartItem struct {
	ItemID   string  `json:"item_id"`
	Quantity int     `json:"quantity"`
	Price    float64 `json:"price"`
}

// CheckoutRequest містить вхідні дані для оформлення замовлення.
type CheckoutRequest struct {
	CustomerID string     `json:"customer_id"`
	Items      []CartItem `json:"items"`
}

// CheckoutResult повертає результат успішного оформлення замовлення.
type CheckoutResult struct {
	OrderID     string    `json:"order_id"`
	PaymentID   string    `json:"payment_id"`
	TotalAmount float64   `json:"total_amount"`
	CreatedAt   time.Time `json:"created_at"`
}

// DomainEvent описує базовий інтерфейс внутрішньопроцесної події.
type DomainEvent interface {
	EventName() string
	OccurredOn() time.Time
}

// OrderPlacedEvent генерується після успішної фіксації ACID-транзакції.
type OrderPlacedEvent struct {
	OrderID    string
	CustomerID string
	Amount     float64
	Timestamp  time.Time
}

func (e OrderPlacedEvent) EventName() string   { return "order.placed" }
func (e OrderPlacedEvent) OccurredOn() time.Time { return e.Timestamp }

// EventBus реалізує типізовану внутрішньопроцесну шину подій у пам'яті.
type EventBus struct {
	mu       sync.RWMutex
	handlers map[string][]func(DomainEvent)
}

// NewEventBus створює новий екземпляр шини подій.
func NewEventBus() *EventBus {
	return &EventBus{
		handlers: make(map[string][]func(DomainEvent)),
	}
}

// Subscribe реєструє обробник для конкретного типу події.
func (b *EventBus) Subscribe(eventName string, handler func(DomainEvent)) {
	b.mu.Lock()
	defer b.mu.Unlock()
	b.handlers[eventName] = append(b.handlers[eventName], handler)
}

// Publish розсилає подію всім зареєстрованим обробникам у пам'яті.
func (b *EventBus) Publish(event DomainEvent) {
	b.mu.RLock()
	defer b.mu.RUnlock()
	handlers, exists := b.handlers[event.EventName()]
	if !exists {
		return
	}
	for _, handler := range handlers {
		handler(event)
	}
}

// Service координує оформлення замовлення в межах єдиної БД-транзакції.
type Service struct {
	db       *sql.DB
	eventBus *EventBus
}

// NewService створює сервіс Checkout з підключенням до БД та шиною подій.
func NewService(db *sql.DB, bus *EventBus) *Service {
	return &Service{
		db:       db,
		eventBus: bus,
	}
}

// ExecuteCheckout виконує перевірку залишків, проведення платежу та створення
// замовлення у межах єдиної локальної ACID-транзакції бази даних.
func (s *Service) ExecuteCheckout(ctx context.Context, req CheckoutRequest) (*CheckoutResult, error) {
	if len(req.Items) == 0 {
		return nil, errors.New("кошик порожній")
	}

	// 1. Відкриваємо локальну ACID-транзакцію бази даних
	tx, err := s.db.BeginTx(ctx, &sql.TxOptions{Isolation: sql.LevelReadCommitted})
	if err != nil {
		return nil, fmt.Errorf("помилка відкриття транзакції: %w", err)
	}

	// У разі будь-якої паніки або неперехопленої помилки робимо Rollback.
	// Якщо транзакцію вже закомічено, Rollback поверне sql.ErrTxDone (ігнорується).
	defer tx.Rollback()

	var totalAmount float64

	// 2. Атомарно зменшуємо залишки на складі для кожного товару
	for _, item := range req.Items {
		itemTotal := item.Price * float64(item.Quantity)
		totalAmount += itemTotal

		res, err := tx.ExecContext(ctx,
			"UPDATE inventory SET stock = stock - $1 WHERE item_id = $2 AND stock >= $1",
			item.Quantity, item.ItemID,
		)
		if err != nil {
			return nil, fmt.Errorf("помилка оновлення складу для товару %s: %w", item.ItemID, err)
		}

		rowsAffected, err := res.RowsAffected()
		if err != nil {
			return nil, fmt.Errorf("помилка перевірки оновлених рядків: %w", err)
		}
		if rowsAffected == 0 {
			// Якщо складський залишок менший за запитуваний, транзакція відкочується
			return nil, fmt.Errorf("%w: товар %s", ErrOutOfStock, item.ItemID)
		}
	}

	orderID := fmt.Sprintf("ord_%d", time.Now().UnixNano())
	paymentID := fmt.Sprintf("pay_%d", time.Now().UnixNano())
	now := time.Now().UTC()

	// 3. Фіксуємо платіжну транзакцію в БД
	_, err = tx.ExecContext(ctx,
		"INSERT INTO payments (id, customer_id, amount, status, created_at) VALUES ($1, $2, $3, $4, $5)",
		paymentID, req.CustomerID, totalAmount, "COMPLETED", now,
	)
	if err != nil {
		return nil, fmt.Errorf("помилка запису платежу: %w", err)
	}

	// 4. Створюємо підтверджене замовлення
	_, err = tx.ExecContext(ctx,
		"INSERT INTO orders (id, customer_id, total_amount, status, created_at) VALUES ($1, $2, $3, $4, $5)",
		orderID, req.CustomerID, totalAmount, "PAID", now,
	)
	if err != nil {
		return nil, fmt.Errorf("помилка створення замовлення: %w", err)
	}

	// 5. Атомарне підтвердження (Commit) усіх змін в БД
	if err := tx.Commit(); err != nil {
		return nil, fmt.Errorf("помилка фіксації транзакції: %w", err)
	}

	// 6. Публікуємо вхідну подію в внутрішньопроцесну шину після Commit
	s.eventBus.Publish(OrderPlacedEvent{
		OrderID:    orderID,
		CustomerID: req.CustomerID,
		Amount:     totalAmount,
		Timestamp:  now,
	})

	return &CheckoutResult{
		OrderID:     orderID,
		PaymentID:   paymentID,
		TotalAmount: totalAmount,
		CreatedAt:   now,
	}, nil
}
