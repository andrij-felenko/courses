// ЦІЛЬ — інтерфейс, який очікує вся наша система
interface PaymentGateway {
  charge(amountUAH: number, currency: string): Promise<string>; // повертає id платежу
}

// АДАПТОВАНИЙ — чужий SDK; ми його НЕ міняємо, лише використовуємо
class StripeClient {
  createCharge(p: { amountInCents: number; currency: string }): Promise<{ id: string }> {
    /* ... справжній виклик до Stripe ... */
    return Promise.resolve({ id: "ch_123" });
  }
}

// АДАПТЕР — реалізує ЦІЛЬ, усередині тримає АДАПТОВАНОГО і перекладає
class StripeAdapter implements PaymentGateway {
  constructor(private stripe: StripeClient) {}         // тримаємо чужий об'єкт полем

  async charge(amountUAH: number, currency: string): Promise<string> {
    const res = await this.stripe.createCharge({
      amountInCents: Math.round(amountUAH * 100),      // гривні → центи
      currency: currency.toLowerCase(),                // "UAH" → "uah"
    });
    return res.id;                                     // { id } → просто id
  }
}

// Клієнтський код НЕ знає про Stripe — він бачить лише PaymentGateway
async function pay(gateway: PaymentGateway) {
  const id = await gateway.charge(499, "UAH");
  console.log("оплачено, платіж", id);
}

pay(new StripeAdapter(new StripeClient()));
