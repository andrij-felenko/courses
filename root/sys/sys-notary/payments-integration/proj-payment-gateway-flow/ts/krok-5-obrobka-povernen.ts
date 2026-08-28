export interface RefundRequestParams {
  paymentIntentId: string;
  amountCents?: number; // Необов'язково для повного повернення
  reason?: "duplicate" | "fraudulent" | "requested_by_customer";
}

export class PaymentRefundService {
  constructor(
    private readonly apiKey: string,
    private readonly pspBaseUrl: string = "https://api.stripe.com/v1"
  ) {}

  /**
   * Ініціює повне або часткове повернення коштів за платіжним наміром.
   */
  async processRefund(params: RefundRequestParams): Promise<{ refundId: string; status: string }> {
    const payloadData: Record<string, string> = {
      payment_intent: params.paymentIntentId,
    };
    if (params.amountCents) {
      payloadData.amount = params.amountCents.toString();
    }
    if (params.reason) {
      payloadData.reason = params.reason;
    }

    const payload = new URLSearchParams(payloadData);
    const idempotencyKey = `refund_${params.paymentIntentId}_${params.amountCents ?? "full"}`;

    const response = await fetch(`${this.pspBaseUrl}/refunds`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${this.apiKey}`,
        "Content-Type": "application/x-www-form-urlencoded",
        "Idempotency-Key": idempotencyKey,
      },
      body: payload.toString(),
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(`Помилка повернення: ${err.error?.message ?? "Невідома помилка"}`);
    }

    const data = await response.json();
    return {
      refundId: data.id,
      status: data.status,
    };
  }
}
