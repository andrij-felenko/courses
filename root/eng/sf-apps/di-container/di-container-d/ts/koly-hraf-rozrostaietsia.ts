const c = new Container();
// ── реєстрація: таблиця «обіцянка → реалізація» ──
c.bind(Logger,         FileLogger);
c.bind(HttpClient,     HttpClient);
c.bind(PaymentGateway, StripeGateway);
c.bind(PaymentService, PaymentService);

// ── один запит на верхівку — контейнер сам обійде весь граф ──
const payments = c.resolve(PaymentService); // створив Logger, HttpClient, StripeGateway, PaymentService
runApp(payments);
