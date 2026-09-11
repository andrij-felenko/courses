package checkout

import (
	"context"
	"fmt"
	"time"
)

// CartClient описує мережевий інтерфейс сервісу кошика.
type CartClient interface {
	LockCart(ctx context.Context, cartID string) ([]string, error)
	ClearCart(ctx context.Context, cartID string) error
}

// InventoryClient описує мережевий інтерфейс складського обліку.
type InventoryClient interface {
	ReserveItems(ctx context.Context, itemIDs []string) (string, error)
	CancelReservation(ctx context.Context, reservationID string) error
}

// PaymentClient описує мережевий інтерфейс сервісу платежів.
type PaymentClient interface {
	Charge(ctx context.Context, amount float64, accountID string) (string, error)
	Refund(ctx context.Context, paymentID string) error
}

// DistributedSagaOrchestrator координує розподілену транзакцію через мережу.
type DistributedSagaOrchestrator struct {
	cart      CartClient
	inventory InventoryClient
	payment   PaymentClient
}

func NewDistributedSagaOrchestrator(c CartClient, i InventoryClient, p PaymentClient) *DistributedSagaOrchestrator {
	return &DistributedSagaOrchestrator{
		cart:      c,
		inventory: i,
		payment:   p,
	}
}

// ExecuteCheckout виконує розподілену сагу з компенсаціями при відмовах.
func (o *DistributedSagaOrchestrator) ExecuteCheckout(ctx context.Context, cartID string, accountID string, amount float64) error {
	ctxWithTimeout, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()

	// Крок 1: Блокування кошика через RPC
	itemIDs, err := o.cart.LockCart(ctxWithTimeout, cartID)
	if err != nil {
		return fmt.Errorf("помилка блокування кошика: %w", err)
	}

	// Крок 2: Резервування на складі через RPC
	reservationID, err := o.inventory.ReserveItems(ctxWithTimeout, itemIDs)
	if err != nil {
		return fmt.Errorf("помилка резервування складу: %w", err)
	}

	// Крок 3: Оплата через RPC
	paymentID, err := o.payment.Charge(ctxWithTimeout, amount, accountID)
	if err != nil {
		// Компенсувальна дія для Кроку 2 при відмові оплати
		if rollbackErr := o.inventory.CancelReservation(ctxWithTimeout, reservationID); rollbackErr != nil {
			return fmt.Errorf("критичний збій: не вдалося скасувати резерв %s після помилки оплати: %v", reservationID, rollbackErr)
		}
		return fmt.Errorf("оплата не пройшла, резерв скасовано: %w", err)
	}

	// Крок 4: Очищення кошика через RPC
	if err := o.cart.ClearCart(ctxWithTimeout, cartID); err != nil {
		// Компенсувальні дії для Кроку 3 та Кроку 2
		_ = o.payment.Refund(ctxWithTimeout, paymentID)
		_ = o.inventory.CancelReservation(ctxWithTimeout, reservationID)
		return fmt.Errorf("помилка очищення кошика, виконано повне повернення: %w", err)
	}

	return nil
}
