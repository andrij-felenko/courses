// 1. Доменний інтерфейс (Port) та чисті типи нашого бізнес-ядра
export interface PaymentPort {
  charge(command: ChargeCommand): Promise<PaymentResult>;
}

export interface ChargeCommand {
  orderId: string;
  amountCents: number;
  currency: string;
  paymentToken: string;
}

export type PaymentResult =
  | { success: true; transactionId: string }
  | { success: false; error: PaymentDomainError };

export type PaymentDomainError =
  | { kind: 'INSUFFICIENT_FUNDS'; message: string }
  | { kind: 'INVALID_CREDENTIALS'; message: string }
  | { kind: 'TRANSIENT_NETWORK_FAILURE'; message: string; retryable: true };

// 2. Реалізація адаптера антикорупційного шару
export class ExternalPaymentAclAdapter implements PaymentPort {
  constructor(
    private readonly client: VendorTransportClient,
    private readonly mapper: VendorDataMapper,
    private readonly errorClassifier: VendorErrorClassifier,
  ) {}

  async charge(command: ChargeCommand): Promise<PaymentResult> {
    // Етап 1: Трансляція доменної команди у вендорний запит
    const vendorPayload = this.mapper.toVendorRequest(command);

    try {
      // Етап 2: Виконання мережевого протоколу (транспорт, підписи, заголовки)
      const rawResponse = await this.client.post('/v1/transactions', vendorPayload);

      // Етап 3: Зворотна трансляція та нормалізація успішної відповіді
      return this.mapper.toDomainResult(rawResponse);
    } catch (error: unknown) {
      // Етап 4: Перехоплення й переклад чужих винятків на мову домену
      const domainError = this.errorClassifier.classify(error);
      return { success: false, error: domainError };
    }
  }
}
