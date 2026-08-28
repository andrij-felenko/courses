class OrderService {
  constructor(private logger: Logger) {}     // завжди Logger, ніколи null

  place(order: Order): void {
    // ...оформлення замовлення...
    this.logger.write(`замовлення ${order.id} оформлено`);  // без перевірки
  }
}

// логування ввімкнене:
new OrderService(new FileLogger("orders.log"));
// вимкнене — підставляємо ПОРОЖНІЙ об'єкт, а не null:
new OrderService(new NullLogger());
