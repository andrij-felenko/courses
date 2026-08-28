export interface SetupCardParams {
  customerId: string;
  paymentMethodId: string;
}

export class SubscriptionSetupService {
  constructor(
    private readonly apiKey: string,
    private readonly pspBaseUrl: string = "https://api.stripe.com/v1"
  ) {}

  /**
   * Створює SetupIntent для прив'язки картки до клієнта під майбутні підписки.
   */
  async attachPaymentMethod(params: SetupCardParams): Promise<{ setupIntentId: string; status: string }> {
    const payload = new URLSearchParams({
      customer: params.customerId,
      payment_method: params.paymentMethodId,
      usage: "off_session", // Дозвіл на списання у фоні
      confirm: "true",
    });

    const response = await fetch(`${this.pspBaseUrl}/setup_intents`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${this.apiKey}`,
        "Content-Type": "application/x-www-form-urlencoded",
        "Idempotency-Key": `setup_${params.customerId}_${params.paymentMethodId}`,
      },
      body: payload.toString(),
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(`Помилка прив'язки картки: ${err.error?.message ?? "Невідома помилка"}`);
    }

    const data = await response.json();
    return {
      setupIntentId: data.id,
      status: data.status,
    };
  }
}
