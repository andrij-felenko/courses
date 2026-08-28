class OrderService {
  constructor(private gateway: PaymentGateway) {}   // просимо ззовні, не створюємо

  checkout(order: Order): void {
    this.gateway.charge(order.total());
  }
}

// хтось зовні вирішує, ЩО саме подати:
const service = new OrderService(new StripeGateway());
