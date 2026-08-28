// domain/dispatch.go — ЯДРО. Приймає інтерфейс Notifier ("accept interfaces").
package domain

import "errors"

type Dispatch struct {
    Notifier Notifier // впровадження залежності — інтерфейс, не конкретика
}

func (d Dispatch) OnCourierAssigned(order Order, customer Recipient) {
    err := d.Notifier.Notify(customer, CourierNear{
        OrderID: order.ID, MinutesAway: order.ETAMinutes,
    })
    // рішення домену — без знання, це 429 чи 421
    if errors.Is(err, ErrRetryable) {
        d.scheduleRetry(order)
    }
}

// main.go — КОМПОЗИЦІЙНИЙ КОРІНЬ: єдине місце вибору постачальника.
func main() {
    var notifier domain.Notifier
    if os.Getenv("MAIL") == "smtp" {
        notifier = adapters.SMTP{Addr: "mail.example.com:587", From: "no-reply@food.app"}
    } else {
        notifier = adapters.SendGrid{
            APIKey: os.Getenv("SENDGRID_KEY"), From: "no-reply@food.app", HTTP: http.DefaultClient,
        }
    }
    dispatch := domain.Dispatch{Notifier: notifier} // ядро дістає порт, не знаючи адаптера
    _ = dispatch
}
