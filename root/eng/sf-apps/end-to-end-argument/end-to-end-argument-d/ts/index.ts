// Клієнт не питає «чи дійшов мій запит», він питає «чи є наслідок».
async function pay(orderId: string, amount: Money): Promise<Payment> {
  const key = idempotencyKey(orderId);          // ключ народжується разом з наміром
  for (let attempt = 0; attempt < 5; attempt++) {
    try {
      return await gateway.charge({ key, orderId, amount });
    } catch (e) {
      if (!isRetryable(e)) break;
      await sleep(backoff(attempt));
    }
  }
  // Відповіді немає — але це НЕ означає, що списання не сталося.
  const done = await gateway.findByKey(key);    // питаємо кінець про наслідок
  if (done) return done;
  throw new PaymentUnknown(key);                // чесно: стан невідомий, не «помилка»
}
