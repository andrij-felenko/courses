// РИЗИК НАЗВАНО Й ЗМЕНШЕНО: таймаут + повтор + запасний хід, і все за швом
interface PaymentGateway {              // шов: логіка знає лише інтерфейс
  charge(customerId: number, amount: number): Promise<PayResult>;
}

async function chargeCustomer(
  gw: PaymentGateway, customerId: number, amount: number,
): Promise<PayResult> {
  for (let attempt = 0; attempt < 3; attempt++) { // зменшуємо ЙМОВІРНІСТЬ збою
    const r = await gw.charge(customerId, amount); // (таймаут — усередині адаптера)
    if (r.ok) return r;
  }
  // запасний хід зменшує ВТРАТУ: не валимо все, а ставимо платіж у чергу
  return PayResult.queuedForRetry(customerId, amount);
}
// Постачальник за швом → якщо цей сервіс виявиться поганим, міняємо адаптер,
// а chargeCustomer і виклики не чіпаємо. Це відповідь на «невідоме невідоме».
