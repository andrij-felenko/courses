// adapters/smtp.go — інший постачальник, ТОЙ САМИЙ порт.
package adapters

import (
    "errors"
    "fmt"
    "net/smtp"
    "net/textproto"

    "example.com/app/domain"
)

type SMTP struct {
    Addr string // "mail.example.com:587"
    From string
    Auth smtp.Auth
}

func (m SMTP) Notify(to domain.Recipient, event domain.Event) error {
    subject, html := domain.RenderEvent(event, to.Locale)

    msg := "From: " + m.From + "\r\n" +
        fmt.Sprintf("To: %s <%s>\r\n", to.Name, to.Email) +
        "Subject: " + subject + "\r\n" +
        "MIME-Version: 1.0\r\n" +
        "Content-Type: text/html; charset=UTF-8\r\n\r\n" + html

    err := smtp.SendMail(m.Addr, m.Auth, m.From, []string{to.Email}, []byte(msg))
    if err == nil {
        return nil // доставлено
    }

    // Чужі коди SMTP перекладаємо в доменний наслідок — назовні йде лише він.
    var proto *textproto.Error
    if errors.As(err, &proto) {
        // 4xx SMTP → тимчасово; 5xx → остаточно. Ті самі два кошики домену.
        if proto.Code >= 400 && proto.Code < 500 {
            return fmt.Errorf("smtp %d: %w", proto.Code, domain.ErrRetryable)
        }
        return fmt.Errorf("smtp %d: %w", proto.Code, domain.ErrRejected)
    }
    return fmt.Errorf("smtp io: %v: %w", err, domain.ErrRetryable) // мережа
}
