// Go: Вихідний HTTP-клієнт з context та exponential backoff
package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

type Gateway struct {
	Client *http.Client
	URL    string
}

func (g *Gateway) ChargeOrder(ctx context.Context, orderID string, amount float64) error {
	idempotencyKey := fmt.Sprintf("charge_%s_v1", orderID)
	payload, _ := json.Marshal(map[string]any{"order_id": orderID, "amount": amount})

	backoff := 500 * time.Millisecond

	for attempt := 1; attempt <= 3; attempt++ {
		reqCtx, cancel := context.WithTimeout(ctx, 3*time.Second)
		req, _ := http.NewRequestWithContext(reqCtx, "POST", g.URL+"/v1/charges", bytes.NewBuffer(payload))
		req.Header.Set("Idempotency-Key", idempotencyKey)
		req.Header.Set("Content-Type", "application/json")

		resp, err := g.Client.Do(req)
		cancel()

		if err != nil || (resp != nil && resp.StatusCode >= 500) || (resp != nil && resp.StatusCode == 409) {
			time.Sleep(backoff)
			backoff *= 2
			continue
		}
		defer resp.Body.Close()

		if resp.StatusCode == 200 || resp.StatusCode == 201 {
			fmt.Printf("[SUCCESS Go] Платіж успішно проведено з ключем %s\n", idempotencyKey)
			return nil
		}

		return fmt.Errorf("фатальна помилка HTTP %d", resp.StatusCode)
	}

	return fmt.Errorf("перевищено кількість спроб")
}
