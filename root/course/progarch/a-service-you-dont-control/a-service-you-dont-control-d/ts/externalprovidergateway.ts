// Приклад чистого доменного шлюзу, захищеного антикорупційним шаром
interface PaymentGateway {
  charge(orderId: OrderId, amount: Money): Promise<PaymentResult>;
}

class ExternalProviderGateway implements PaymentGateway {
  constructor(private readonly client: HttpClient, private readonly apiKey: string) {}

  async charge(orderId: OrderId, amount: Money): Promise<PaymentResult> {
    try {
      const rawResponse = await this.client.post("/v2/transactions", {
        external_id: orderId.value,
        val: amount.cents,
        curr: amount.currency
      });
      return this.translateSuccess(rawResponse.data);
    } catch (err) {
      throw this.translateError(err);
    }
  }

  private translateSuccess(data: any): PaymentResult {
    // Антикорупційний шар: ізоляція чужої моделі в одній функції
    return new PaymentResult(data.tx_id, data.state === "OK" ? Status.SUCCESS : Status.REJECTED);
  }

  private translateError(err: unknown): DomainError {
    return new DomainPaymentFailure("Провайдер відхилив транзакцію або недоступний");
  }
}
