class PaymentService {
  constructor(
    private readonly orders: OrderRepository,
    private readonly gateway: PaymentGateway,
  ) {}

  async pay(orderId: OrderId): Promise<void> {
    const order = await this.orders.byId(orderId);
    if (!order) throw new Error(`немає замовлення ${orderId}`);
    await this.gateway.charge(order.total);
    order.markPaid();
    // ← і тут забули: await this.orders.save(order);
  }
}
