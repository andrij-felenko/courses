class StripeError extends Error { constructor(public code: string) { super(code); } }
class PaymentError extends Error {}                 // ТВІЙ словник помилок

// Найдрібніших одиниць в одиниці валюти — за ISO 4217. Типово 100; винятки — окремо.
const MINOR: Record<string, number> = { JPY: 1, KRW: 1, BHD: 1000, KWD: 1000, OMR: 1000 };
const toMinor = (amount: number, cur: string) =>
  Math.round(amount * (MINOR[cur] ?? 100));         // не «×100», а за валютою

interface PaymentGateway {
  charge(amount: number, currency: string): Promise<string>;
}

class StripeAdapter implements PaymentGateway {
  constructor(private stripe: StripeClient) {}       // адаптований — ПОЛЕМ (композиція)

  async charge(amount: number, currency: string): Promise<string> {
    try {
      const res = await this.stripe.createCharge({
        amountInMinor: toMinor(amount, currency),    // f_in: одиниці за валютою
        currency: currency.toLowerCase(),            // f_in: "UAH" → "uah"
      });
      return res.id;                                 // f_out: { id } → id
    } catch (e) {
      if (e instanceof StripeError)                  // f_out і для ПОМИЛОК:
        throw new PaymentError(`платіж відхилено: ${e.code}`);  // чужа помилка → наша
      throw e;                                       // не наша — не ковтаємо, пускаємо далі
    }
  }
}
