// РИЗИК НАЗВАНО Й ЗМЕНШЕНО: таймаут + повтор + запасний хід, і все за швом
struct PaymentGateway {                 // шов: логіка знає лише інтерфейс
    virtual PayResult charge(int customer_id, double amount) = 0;
    virtual ~PaymentGateway() = default;
};

PayResult charge_customer(PaymentGateway& gw, int customer_id, double amount) {
    for (int attempt = 0; attempt < 3; ++attempt) {   // зменшуємо ЙМОВІРНІСТЬ збою
        PayResult r = gw.charge(customer_id, amount);  // (таймаут — усередині адаптера)
        if (r.ok) return r;
    }
    // запасний хід зменшує ВТРАТУ: не валимо все, а ставимо платіж у чергу
    return PayResult::queued_for_retry(customer_id, amount);
}
// Постачальник за швом → якщо цей сервіс виявиться поганим, міняємо адаптер,
// а charge_customer і виклики не чіпаємо. Це відповідь на «невідоме невідоме».
