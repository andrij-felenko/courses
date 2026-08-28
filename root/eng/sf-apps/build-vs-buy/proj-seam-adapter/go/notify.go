// domain/notify.go — усе у ВАШИХ термінах.
package domain

import "errors"

type Recipient struct {
    Email  string
    Name   string
    Locale string // "uk" | "en" — мову листа знає домен
}

// Подія домену — те, ПРО ЩО сповіщаємо (замкнене об'єднання).
type Event interface{ isEvent() }

type OrderShipped struct {
    OrderID    string
    ETAMinutes int
}
type CourierNear struct {
    OrderID     string
    MinutesAway int
}
type OrderDelivered struct{ OrderID string }

func (OrderShipped) isEvent()   {}
func (CourierNear) isEvent()    {}
func (OrderDelivered) isEvent() {}

// Наслідок домену виражений ідіоматично — помилкою. nil = доставлено;
// обгортка над цими двома = варто повторити / відхилено остаточно.
var (
    ErrRetryable = errors.New("notify: retryable")
    ErrRejected  = errors.New("notify: rejected")
)

// Порт: маленький інтерфейс, названий вашою потребою.
type Notifier interface {
    Notify(to Recipient, event Event) error
}
