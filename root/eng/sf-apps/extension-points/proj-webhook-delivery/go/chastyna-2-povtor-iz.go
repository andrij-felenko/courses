package webhook

import (
	"context"
	"math"
	"math/rand"
	"net/http"
	"strings"
	"time"
)

const (
	baseMS      = 1_000   // база: 1 секунда
	capMS       = 300_000 // стеля: 5 хвилин
	maxAttempts = 10      // далі — здаємося (dead-letter)
)

// Скільки чекати перед спробою №attempt (0-based): повне тремтіння.
func backoffDelay(attempt int) time.Duration {
	window := math.Min(capMS, baseMS*math.Pow(2, float64(attempt)))
	return time.Duration(rand.Float64()*window) * time.Millisecond // random(0, window)
}

func DeliverWithRetry(url string, d SignedDelivery, deliveryID string) bool {
	client := &http.Client{Timeout: 10 * time.Second} // жорсткий тайм-аут
	for attempt := 0; attempt < maxAttempts; attempt++ {
		if attempt > 0 {
			time.Sleep(backoffDelay(attempt - 1))
		}
		req, _ := http.NewRequest("POST", url, strings.NewReader(d.Body))
		for k, v := range d.Headers {
			req.Header.Set(k, v)
		}
		req.Header.Set("Idempotency-Key", deliveryID)

		res, err := client.Do(req)
		if err != nil {
			continue // мережа/тайм-аут — тимчасово, повторюємо
		}
		res.Body.Close()
		if res.StatusCode >= 200 && res.StatusCode < 300 {
			return true // доставлено
		}
		if res.StatusCode >= 400 && res.StatusCode < 500 && res.StatusCode != 429 {
			return false // 4xx (крім 429) — наша помилка, повтор дарма
		}
		// 5xx / 429 — тимчасово, наступна ітерація
	}
	return false // спроби вичерпано
}
_ = context.Background
