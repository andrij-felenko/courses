// Підробка замість мережі: тест ядра БЕЗ Stripe і без інтернету
struct FakeGateway : PaymentGateway {
    Money lastAmount{};
    ChargeResult charge(const Money& a, const Card&) override {
        lastAmount = a;                   // просто запам'ятали, що просили
        return { true, "" };              // і вдали успіх
    }
};

// PaymentService payments(fake); charge(order);
// перевіряємо: fake.lastAmount == order.total()  — за мілісекунди, без мережі
