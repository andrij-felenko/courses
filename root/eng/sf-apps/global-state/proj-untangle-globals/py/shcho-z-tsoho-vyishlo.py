class Billing:
    def __init__(self, cfg: BillingConfig, clock: Clock, metrics: Metrics) -> None:
        self._cfg = cfg
        self._clock = clock
        self._metrics = metrics

    def renew(self, sub: Subscription) -> Renewal:
        now = self._clock.now()
        deadline = sub.paid_until + timedelta(days=self._cfg.grace_days)
        if now > deadline:
            log.warning("sub %s: пільговий строк вичерпано", sub.id)
            self._metrics.bump("renewals_expired")
            return Renewal("expired", 0.0, sub.paid_until)
        amount = round(sub.plan_price * (1 + self._cfg.fee_rate), 2)
        sub.paid_until = sub.paid_until + timedelta(days=self._cfg.period_days)
        self._metrics.bump("renewals_ok")
        log.info("sub %s: продовжено на %.2f", sub.id, amount)
        return Renewal("ok", amount, sub.paid_until)
