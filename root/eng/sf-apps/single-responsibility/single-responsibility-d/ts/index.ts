type Handler = (order: Order) => string;

// Ядро: тільки бізнес-правило замовлення.
const placeOrder = (repo: Repo): Handler => (order) => {
  repo.save(order);
  return order.id;
};

// Кожна наскрізна турбота — обгортка над Handler.
const withLogging = (next: Handler): Handler => (order) => {
  log.info(`place order ${order.id}`);
  const result = next(order);
  log.info(`order placed: ${result}`);
  return result;
};

const withTiming = (next: Handler): Handler => (order) => {
  const started = performance.now();
  try {
    return next(order);
  } finally {
    metrics.observe("place_order", performance.now() - started);
  }
};

// Збірка ланцюга: ядро не знає ні про журнал, ні про заміри.
const handler = withLogging(withTiming(placeOrder(repo)));
const orderId = handler(order);
