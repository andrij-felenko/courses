def main():
    # ── листя: ні від кого не залежить ──
    config = Config.from_env()
    logger = FileLogger(config.log_path, level=config.log_level)

    # ── середина: спирається на вже створене ──
    http = HttpClient(timeout=config.http_timeout, logger=logger)
    gateway = StripeGateway(http, api_key=config.stripe_key)

    # ── корінь: заради нього все й збирали ──
    payments = PaymentService(gateway, logger=logger)

    run_app(payments)   # запускаємо — граф готовий, ядро не чуло слова «Stripe»
