export class Billing {
  constructor(
    private readonly cfg: BillingConfig,
    private readonly clock: Clock,
    private readonly metrics: Metrics,
  ) {}

  renew(sub: Subscription): Renewal {
    const now = this.clock.now();
    const deadline = addDays(sub.paidUntil, this.cfg.graceDays);
    if (now.getTime() > deadline.getTime()) {
      log.warn(`sub ${sub.id}: пільговий строк вичерпано`);
      this.metrics.bump("renewals_expired");
      return { status: "expired", amount: 0, paidUntil: sub.paidUntil };
    }
    const amount = Math.round(sub.planPrice * (1 + this.cfg.feeRate) * 100) / 100;
    sub.paidUntil = addDays(sub.paidUntil, this.cfg.periodDays);
    this.metrics.bump("renewals_ok");
    log.info(`sub ${sub.id}: продовжено на ${amount.toFixed(2)}`);
    return { status: "ok", amount, paidUntil: sub.paidUntil };
  }
}
