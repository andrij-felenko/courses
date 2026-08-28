import crypto from "node:crypto";

export interface CreatePaymentParams {
  orderId: string;
  amountCents: number;
  currency: string;
  paymentMethodId: string;
  customerId: string;
}

export type PaymentIntentStatus =
  | "requires_payment_method"
  | "requires_confirmation"
  | "requires_action"
  | "processing"
  | "requires_capture"
  | "succeeded"
  | "canceled"
  | "failed";

export interface PaymentIntentResult {
  intentId: string;
  status: PaymentIntentStatus;
  clientSecret: string | null;
  requiresAction: boolean;
}

export class PaymentGatewayService {
  constructor(
    private readonly apiKey: string,
    private readonly pspBaseUrl: string = "https://api.stripe.com/v1"
  ) {}

  /**
   * Створює та ідемпотентно підтверджує платіжний намір.
   */
  async processCheckout(params: CreatePaymentParams): Promise<PaymentIntentResult> {
    // Детермінований ключ ідемпотентності для захисту від мережевих повторів
    const idempotencyKey = `checkout_${params.orderId}_${params.amountCents}`;

    const payload = new URLSearchParams({
      amount: params.amountCents.toString(),
      currency: params.currency.toLowerCase(),
      payment_method: params.paymentMethodId,
      confirm: "true", // Спробувати списати негайно
      "metadata[order_id]": params.orderId,
      "metadata[customer_id]": params.customerId,
      capture_method: "automatic",
    });

    const response = await fetch(`${this.pspBaseUrl}/payment_intents`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${this.apiKey}`,
        "Content-Type": "application/x-www-form-urlencoded",
        "Idempotency-Key": idempotencyKey,
      },
      body: payload.toString(),
    });

    if (!response.ok) {
      const errorBody = await response.json();
      throw new Error(`Платіж відхилено: ${errorBody.error?.message ?? "Невідома помилка"}`);
    }

    const data = await response.json();
    return {
      intentId: data.id,
      status: data.status as PaymentIntentStatus,
      clientSecret: data.client_secret ?? null,
      requiresAction: data.status === "requires_action",
    };
  }
}
