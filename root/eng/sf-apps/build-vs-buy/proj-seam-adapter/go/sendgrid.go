// adapters/sendgrid.go — єдине місце зі словом "SendGrid".
package adapters

import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"

    "example.com/app/domain"
)

const sendGridEndpoint = "https://api.sendgrid.com/v3/mail/send"

type SendGrid struct {
    APIKey string
    From   string
    HTTP   *http.Client
}

func (s SendGrid) Notify(to domain.Recipient, event domain.Event) error {
    subject, html := domain.RenderEvent(event, to.Locale) // ТЕКСТ — рішення домену

    // Переклад ДОМЕН → чужий формат тіла живе тут і тільки тут.
    payload := map[string]any{
        "personalizations": []any{map[string]any{
            "to": []any{map[string]string{"email": to.Email, "name": to.Name}},
        }},
        "from":    map[string]string{"email": s.From},
        "subject": subject,
        "content": []any{map[string]string{"type": "text/html", "value": html}},
    }
    buf, _ := json.Marshal(payload)

    req, _ := http.NewRequest(http.MethodPost, sendGridEndpoint, bytes.NewReader(buf))
    req.Header.Set("Authorization", "Bearer "+s.APIKey)
    req.Header.Set("Content-Type", "application/json")

    resp, err := s.HTTP.Do(req)
    if err != nil {
        return fmt.Errorf("network: %v: %w", err, domain.ErrRetryable)
    }
    defer resp.Body.Close()

    // Переклад чужих КОДІВ → доменний наслідок. 202/429/5xx назовні не йдуть.
    switch {
    case resp.StatusCode == 202:
        return nil // доставлено
    case resp.StatusCode == 429, resp.StatusCode >= 500:
        return fmt.Errorf("sendgrid %d: %w", resp.StatusCode, domain.ErrRetryable)
    default:
        return fmt.Errorf("sendgrid %d: %w", resp.StatusCode, domain.ErrRejected)
    }
}
