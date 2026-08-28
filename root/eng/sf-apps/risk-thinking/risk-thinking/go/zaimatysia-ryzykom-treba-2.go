// РИЗИК НАЗВАНО Й ЗМЕНШЕНО: таймаут + повтор + запасний хід, і все за швом
type PaymentGateway interface { // шов: логіка знає лише інтерфейс
	Charge(customerID int, amount float64) PayResult
}

func chargeCustomer(gw PaymentGateway, customerID int, amount float64) PayResult {
	for attempt := 0; attempt < 3; attempt++ { // зменшуємо ЙМОВІРНІСТЬ збою
		r := gw.Charge(customerID, amount) // (таймаут — усередині адаптера)
		if r.OK {
			return r
		}
	}
	// запасний хід зменшує ВТРАТУ: не валимо все, а ставимо платіж у чергу
	return QueuedForRetry(customerID, amount)
}

// Постачальник за швом → якщо цей сервіс виявиться поганим, міняємо адаптер,
// а chargeCustomer і виклики не чіпаємо. Це відповідь на «невідоме невідоме».
