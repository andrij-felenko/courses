class ReceiptBuilder {
  constructor(private templates: TemplateStore = Locator.get<TemplateStore>("templates")) {}

  build(order: Order, chargeId: string): string {
    return this.templates.render("receipt", { order: order.id, charge: chargeId });
  }
}

class OrderService {
  constructor(
    private gateway: PaymentGateway = Locator.get<PaymentGateway>("gateway"),
    private clock: Clock = Locator.get<Clock>("clock"),
    private log: AuditLog = Locator.get<AuditLog>("audit"),
    private receipts: ReceiptBuilder = new ReceiptBuilder(),
  ) {}

  checkout(order: Order): string {
    const chargeId = this.gateway.charge(order.total());
    const receipt = this.receipts.build(order, chargeId);
    this.log.write(`${this.clock.now()} order=${order.id} charge=${chargeId}`);
    return receipt;
  }
}
