// ============================================================================
// ДОМЕННІ ТИПИ: чисті сутності та значення ядра
// ============================================================================

export type DomainPaymentStatus = 'PENDING' | 'SUCCEEDED' | 'FAILED';

export interface DomainPayment {
  readonly internalPaymentId: string;
  readonly externalReferenceId: string;
  readonly amountCents: number;
  readonly currency: string;
  readonly status: DomainPaymentStatus;
  readonly settledAt: Date;
}

export interface CreatePaymentCommand {
  readonly internalPaymentId: string;
  readonly amountCents: number;
  readonly currency: string;
  readonly customerEmail: string;
}

// ============================================================================
// ВЕНДОРНІ ТИПИ: специфічні структури зовнішнього постачальника
// ============================================================================

export interface VendorPaymentRequest {
  amount: number;
  currency: string;
  receipt_email: string;
  metadata: {
    internal_id: string;
  };
}

export interface VendorPaymentRawResponse {
  id: string;
  object: string;
  amount: number;
  currency: string;
  status: 'requires_payment_method' | 'requires_action' | 'processing' | 'succeeded' | 'canceled' | string;
  created: number; // Unix timestamp у секундах
  // Поля вендора, які підлягають агресивному відсіканню (shedding):
  client_secret: string;
  livemode: boolean;
  payment_method_types: string[];
  charges?: {
    data: Array<{
      balance_transaction: string;
      risk_score: number;
      network_status: string;
    }>;
  };
  metadata?: Record<string, string>;
}

// ============================================================================
// DATA MAPPER: транслятор онтологій та санітизатор даних
// ============================================================================

export class StripePaymentDataMapper {
  /**
   * Пряма трансляція: доменна команда перетворюється у вендорний запит
   */
  toVendorRequest(command: CreatePaymentCommand): VendorPaymentRequest {
    return {
      amount: command.amountCents,
      currency: command.currency.toLowerCase(),
      receipt_email: command.customerEmail,
      metadata: {
        internal_id: command.internalPaymentId,
      },
    };
  }

  /**
   * Зворотна трансляція: відсікання зайвого, нормалізація типів і статусів
   */
  toDomainPayment(raw: VendorPaymentRawResponse, fallbackInternalId: string): DomainPayment {
    // 1. Відсікання надлишкових полів: ігноруємо client_secret, livemode,
    // risk_score, telemetry, network_status та інший вендорний шум.

    // 2. Безпечне відновлення внутрішнього ідентифікатора
    const internalId = raw.metadata?.internal_id || fallbackInternalId;

    // 3. Нормалізація часової мітки з Unix-секунд у системний Date (UTC)
    const settledAt = new Date(raw.created * 1000);

    // 4. Редукція зовнішнього статусу до суворого доменного скінченного автомата
    const status = this.mapStatus(raw.status);

    return {
      internalPaymentId: internalId,
      externalReferenceId: raw.id,
      amountCents: raw.amount,
      currency: raw.currency.toUpperCase(),
      status,
      settledAt,
    };
  }

  private mapStatus(vendorStatus: string): DomainPaymentStatus {
    switch (vendorStatus) {
      case 'succeeded':
        return 'SUCCEEDED';
      case 'processing':
      case 'requires_action':
        return 'PENDING';
      case 'requires_payment_method':
      case 'canceled':
        return 'FAILED';
      default:
        // Якщо вендор додав новий невідомий статус, переводимо його в контрольований
        // стан очікування з попередженням для системи спостереження, захищаючи домен від краху.
        return 'PENDING';
    }
  }
}
