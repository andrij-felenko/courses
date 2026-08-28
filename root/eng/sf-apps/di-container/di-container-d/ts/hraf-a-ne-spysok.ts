function main() {
  // ── листя: ні від кого не залежить ──
  const config = Config.fromEnv();
  const logger = new FileLogger(config.logPath, config.logLevel);

  // ── середина: спирається на вже створене ──
  const http = new HttpClient(config.httpTimeout, logger);
  const gateway = new StripeGateway(http, config.stripeKey);

  // ── корінь: заради нього все й збирали ──
  const payments = new PaymentService(gateway, logger);

  runApp(payments); // запускаємо — граф готовий, ядро не чуло слова «Stripe»
}
