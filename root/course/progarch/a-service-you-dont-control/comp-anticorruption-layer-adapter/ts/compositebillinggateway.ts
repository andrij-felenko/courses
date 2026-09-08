import type { CustomerBillingPort, BillingAccount, Money } from '@domain/billing';

export interface ResilientRoutingOptions {
  readonly primaryAdapter: CustomerBillingPort;
  readonly secondaryAdapter: CustomerBillingPort;
}

export class CompositeBillingGateway implements CustomerBillingPort {
  private readonly primary: CustomerBillingPort;
  private readonly secondary: CustomerBillingPort;

  constructor(options: ResilientRoutingOptions) {
    this.primary = options.primaryAdapter;
    this.secondary = options.secondaryAdapter;
  }

  async registerCustomer(account: BillingAccount): Promise<string> {
    // Реєстрація клієнта виконується в обох системах або за первинним вибором
    try {
      return await this.primary.registerCustomer(account);
    } catch (error) {
      // У разі відмови первинного провайдера реєструємо в резервному
      return await this.secondary.registerCustomer(account);
    }
  }

  async charge(customerId: string, amount: Money, idempotencyKey: string): Promise<void> {
    try {
      // Спроба 1: Звернення до основного провайдера
      await this.primary.charge(customerId, amount, idempotencyKey);
    } catch (error: any) {
      // Перевіряємо, чи помилка є відновлюваною (транспортний збій або недоступність)
      const isRetryable = error?.retryable === true || error?.status === 503;

      if (!isRetryable) {
        // Якщо картку клієнта відхилено за недостатністю коштів — повторювати в іншого марно
        throw error;
      }

      // Спроба 2: Автоматичний failover на резервний адаптер з унікальним ключем ідемпотентності
      const fallbackIdempotencyKey = `${idempotencyKey}_fallback_secondary`;
      await this.secondary.charge(customerId, amount, fallbackIdempotencyKey);
    }
  }
}
