package migration

import (
	"net/http"
	"time"
)

// Багата модель замовлення — те, що реально є в системі.
type Money struct {
	Value    int64  `json:"value"`
	Currency string `json:"currency"`
}
type Order struct {
	ID     uint64 `json:"id"`
	Amount Money  `json:"amount"` // {value, currency}
}

func loadOrders(r *http.Request) []Order // спільне джерело даних

// Проста сериалізація у форму, готову до JSON (заради стислості).
func toJSONv2(os []Order) []byte
func toJSONv1(os []Order) []byte

// ── НОВИЙ ШЛЯХ: повна реалізація, джерело правди ────────────────────────────
// GET /api/v2/orders  — формат v2: amount = {value, currency}
func HandleOrdersV2(w http.ResponseWriter, r *http.Request) {
	orders := loadOrders(r) // єдина логіка вибірки
	w.WriteHeader(http.StatusOK)
	w.Write(toJSONv2(orders)) // багатий формат
}

// ── СТАРИЙ ШЛЯХ: тонка обгортка над новим ───────────────────────────────────
// GET /api/v1/orders — формат v1: amount = ціле (копійки), без валюти.
// Делегує в спільну логіку, ЗВУЖУЄ результат, чіпляє попередження й лічить себе.
var ordersV1Meter = NewDeprecationMeter() // телеметрія цього шляху

func HandleOrdersV1(w http.ResponseWriter, r *http.Request) {
	// 1. Спільна логіка — та сама, що в v2. Жодного дубля вибірки даних.
	orders := loadOrders(r)

	// 3. Попередження — відповідь валідна, але чесно каже «переходь».
	//    Заголовки ставимо ДО WriteHeader/Write, інакше вони не потраплять.
	markDeprecated(w.Header(),
		time.Unix(1735689600, 0), // 2025-01-01
		time.Unix(1798761600, 0), // 2027-01-01
		"/api/v2/orders",
		"https://api.example.com/deprecations/orders-v1")

	// 2. ЗВУЖЕННЯ: багатий Order → бідний формат v1.
	//    Валюту відкидаємо (v1 її не має), лишаємо ціле value.
	//    Звузити повне до неповного — завжди можна; тут просто губимо currency.
	w.WriteHeader(http.StatusOK)
	w.Write(toJSONv1(orders))

	// 4. Телеметрія: хтось іще ходить старим шляхом — рахуємо й записуємо, хто.
	ordersV1Meter.Record(identifyCaller(r))
}
