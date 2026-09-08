// ============================================================================
// ДОМЕННІ ТИПИ ПОМИЛОК
// ============================================================================

export type DomainPaymentError =
  | { kind: 'NETWORK_TIMEOUT'; message: string; retryable: true }
  | { kind: 'SERVICE_UNAVAILABLE'; message: string; retryable: true }
  | { kind: 'RATE_LIMIT_EXCEEDED'; message: string; retryable: true; retryAfterMs?: number }
  | { kind: 'INSUFFICIENT_FUNDS'; message: string; retryable: false }
  | { kind: 'CARD_EXPIRED'; message: string; retryable: false }
  | { kind: 'FRAUD_REJECTED'; message: string; retryable: false }
  | { kind: 'CONFIGURATION_ERROR'; message: string; retryable: false }
  | { kind: 'UNKNOWN_FAILURE'; message: string; retryable: false };

export type Result<T, E> =
  | { readonly success: true; readonly value: T }
  | { readonly success: false; readonly error: E };

// ============================================================================
// КЛАСИФІКАТОР ТА ПЕРЕКЛАДАЧ ПОМИЛОК АДАПТЕРА
// ============================================================================

export class StripeErrorClassifier {
  classify(error: unknown): DomainPaymentError {
    // 1. Аналіз помилок мережевого рівня (таймаути, скидання з'єднання)
    if (this.isNetworkError(error)) {
      if (error.code === 'ETIMEDOUT' || error.message.includes('timeout')) {
        return { kind: 'NETWORK_TIMEOUT', message: 'Мережевий таймаут запиту до провайдера', retryable: true };
      }
      return { kind: 'SERVICE_UNAVAILABLE', message: 'З'єднання з сервером провайдера розірвано', retryable: true };
    }

    // 2. Аналіз типізованих помилок стороннього SDK
    if (this.isStripeError(error)) {
      switch (error.type) {
        case 'StripeRateLimitError':
          return {
            kind: 'RATE_LIMIT_EXCEEDED',
            message: 'Перевищено ліміт запитів до API',
            retryable: true,
            retryAfterMs: 1000,
          };

        case 'StripeCardError':
          return this.mapCardDeclineCode(error.decline_code || error.code, error.message);

        case 'StripeAuthenticationError':
          return {
            kind: 'CONFIGURATION_ERROR',
            message: 'Недійсні облікові дані API провайдера',
            retryable: false,
          };

        case 'StripeAPIError':
        case 'StripeConnectionError':
          return {
            kind: 'SERVICE_UNAVAILABLE',
            message: 'Тимчасовий внутрішній збій на серверах вендора',
            retryable: true,
          };

        default:
          return {
            kind: 'UNKNOWN_FAILURE',
            message: `Невідомий код помилки провайдера: ${error.type}`,
            retryable: false,
          };
      }
    }

    // 3. Невідомий нетипізований збій
    return {
      kind: 'UNKNOWN_FAILURE',
      message: error instanceof Error ? error.message : 'Непередбачений збій виконання операції',
      retryable: false,
    };
  }

  private isNetworkError(error: unknown): error is { code?: string; message: string } {
    return typeof error === 'object' && error !== null && 'message' in error && !('type' in error);
  }

  private isStripeError(error: unknown): error is { type: string; code?: string; decline_code?: string; message: string } {
    return typeof error === 'object' && error !== null && 'type' in error && typeof (error as any).type === 'string';
  }

  private mapCardDeclineCode(code: string | undefined, originalMessage: string): DomainPaymentError {
    switch (code) {
      case 'insufficient_funds':
        return { kind: 'INSUFFICIENT_FUNDS', message: 'Недостатньо коштів на рахунку клієнта', retryable: false };
      case 'expired_card':
        return { kind: 'CARD_EXPIRED', message: 'Термін дії картки закінчився', retryable: false };
      case 'fraudulent':
      case 'card_velocity_exceeded':
        return { kind: 'FRAUD_REJECTED', message: 'Операцію заблоковано системою безпеки', retryable: false };
      default:
        return { kind: 'UNKNOWN_FAILURE', message: originalMessage, retryable: false };
    }
  }
}
