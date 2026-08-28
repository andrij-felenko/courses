class OrderService {
  private gateway = Locator.get<PaymentGateway>("gateway");
  private clock = Locator.get<Clock>("clock");
  private log = Locator.get<AuditLog>("audit");
  private receipts = new ReceiptBuilder();

  checkout(order: Order): string {
    const chargeId = this.gateway.charge(order.total());
    const receipt = this.receipts.build(order, chargeId);
    this.log.write(`${this.clock.now()} order=${order.id} charge=${chargeId}`);
    return receipt;
  }
}
