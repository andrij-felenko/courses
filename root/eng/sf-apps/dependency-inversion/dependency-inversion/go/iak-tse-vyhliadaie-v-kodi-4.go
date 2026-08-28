// Підробка замість мережі: тест ядра БЕЗ Stripe і без інтернету
type FakeGateway struct {
    lastAmount Money
}

func (g *FakeGateway) Charge(a Money, _ Card) ChargeResult {
    g.lastAmount = a                      // просто запам'ятали, що просили
    return ChargeResult{OK: true, Reason: ""} // і вдали успіх
}

// NewPaymentService(fake).Charge(order)
// перевіряємо: fake.lastAmount == order.Total()  — за мілісекунди, без мережі
