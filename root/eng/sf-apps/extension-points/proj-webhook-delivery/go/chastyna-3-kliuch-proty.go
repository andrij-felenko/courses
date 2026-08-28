package webhook

import "github.com/google/uuid"

type DeliveryJob struct {
	URL        string
	Payload    any
	DeliveryID string // ← сталий ключ ідемпотентності на всі повтори
	Attempt    int
}

func NewDeliveryJob(url string, payload any) DeliveryJob {
	return DeliveryJob{
		URL:        url,
		Payload:    payload,
		DeliveryID: uuid.NewString(), // один раз — і назавжди для цієї доставки
	}
}

// ── Бік ОДЕРЖУВАЧА: атомарний claim ключа перед роботою ──
func HandleIncoming(key, body string, db DB) int {
	// Атомарно: вставити ключ. Уже був → 0 рядків → це ДУБЛІКАТ.
	tag, _ := db.Exec(
		`INSERT INTO processed_webhooks(key) VALUES ($1)
		   ON CONFLICT (key) DO NOTHING`, key)
	if tag.RowsAffected() == 0 {
		return 200 // вже бачили → нічого не робимо, кажемо OK
	}
	doTheWork(body) // побічний ефект — РІВНО раз
	return 200
}
