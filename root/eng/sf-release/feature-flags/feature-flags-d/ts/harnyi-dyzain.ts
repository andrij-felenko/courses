// ГАРНО: Бізнес-сервіс не знає про прапорці
interface PaymentGateway {
  charge(amount: number): Promise<void>;
  refund(amount: number): Promise<void>;
}

class FeatureFlaggedPaymentGateway implements PaymentGateway {
  constructor(
    private legacy: PaymentGateway,
    private modern: PaymentGateway,
    private flags: FlagEngine,
    private context: EvaluationContext
  ) {}

  private get active(): PaymentGateway {
    const enabled = this.flags.evaluate("payment-gateway-v2", this.context).value;
    return enabled ? this.modern : this.legacy;
  }

  charge(amount: number) { return this.active.charge(amount); }
  refund(amount: number) { return this.active.refund(amount); }
}
