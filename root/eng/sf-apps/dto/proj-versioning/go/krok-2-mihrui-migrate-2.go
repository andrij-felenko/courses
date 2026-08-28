type Order struct {
	ID         int64
	Total      float64
	CustomerID string // після міграції — головний ключ
}

func ReadOrder(raw map[string]any) (Order, error) {
	// ЛІБЕРАЛЬНІСТЬ ДО ФОРМИ, правило 1: відсутнє поле → заглушка, не помилка.
	// Під час міграції customer_id може ще не прийти — падаємо назад на email.
	customerID, _ := raw["customer_id"].(string)
	if customerID == "" {
		email, _ := raw["customer_email"].(string)
		customerID = DeriveIDFromEmail(email)
	}

	// ЛІБЕРАЛЬНІСТЬ ДО ФОРМИ, правило 2: незнайомі поля (promo_banner…)
	// просто не читаємо. Їх наявність нас не валить.

	// СУВОРІСТЬ ДО ЗМІСТУ: потрібні поля перевіряємо безжально —
	// це вже не сумісність форми, а захист від зіпсованих даних.
	id, ok := raw["id"].(int64)
	if !ok || id <= 0 {
		return Order{}, fmt.Errorf("зіпсований id: %v", raw["id"])
	}
	total, ok := raw["total"].(float64)
	if !ok || total < 0 {
		return Order{}, fmt.Errorf("неможливий total: %v", raw["total"])
	}

	return Order{ID: id, Total: total, CustomerID: customerID}, nil
}
