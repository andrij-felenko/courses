// ============================================================================
// МОДУЛЬ: @domain/billing (повністю ізольований від зовнішнього світу)
// Маніфест залежностей не містить жодних сторонніх SDK або мережевих бібліотек
// ============================================================================

export interface BillingAccount {
  readonly id: string;
  readonly email: string;
}

export interface Money {
  readonly amountCents: number;
  readonly currency: string;
}

// Доменний порт: ядро диктує операцію мовою своїх бізнес-потреб
export interface CustomerBillingPort {
  registerCustomer(account: BillingAccount): Promise<string>;
  charge(customerId: string, amount: Money, idempotencyKey: string): Promise<void>;
}

// Доменний сервіс оперує виключно власним портом:
export class SubscriptionRenewalService {
  constructor(private readonly billingPort: CustomerBillingPort) {}

  async renewMonthlySubscription(account: BillingAccount, fee: Money): Promise<void> {
    // Бізнес-логіка не має уявлення, який провайдер виконує списання
    const idempotencyKey = `renew_${account.id}_${Date.now()}`;
    await this.billingPort.charge(account.id, fee, idempotencyKey);
  }
}

// ============================================================================
// МОДУЛЬ: @infrastructure/billing-stripe
// Лише цей модуль має залежність від стороннього вендорного SDK: 'stripe'
// ============================================================================

import type { CustomerBillingPort, BillingAccount, Money } from '@domain/billing';
// Вендорний SDK імпортується виключно на периферії інфраструктури:
import Stripe from 'stripe';

export class StripeAclAdapter implements CustomerBillingPort {
  private readonly stripeClient: Stripe;

  constructor(apiKey: string) {
    this.stripeClient = new Stripe(apiKey, {
      apiVersion: '2023-10-16',
      maxNetworkRetries: 3,
      timeout: 5000,
    });
  }

  async registerCustomer(account: BillingAccount): Promise<string> {
    const customer = await this.stripeClient.customers.create({
      email: account.email,
      metadata: { internalAccountId: account.id },
    });
    return customer.id;
  }

  async charge(customerId: string, amount: Money, idempotencyKey: string): Promise<void> {
    await this.stripeClient.paymentIntents.create(
      {
        customer: customerId,
        amount: amount.amountCents,
        currency: amount.currency.toLowerCase(),
        confirm: true,
        off_session: true,
      },
      { idempotencyKey },
    );
  }
}
