class ReceiptBuilder {
  build(order: Order, chargeId: string): string {
    const t = Locator.get<TemplateStore>("templates");     // смик усередині дитини
    return t.render("receipt", { order: order.id, charge: chargeId });
  }
}

class OrderService {
  checkout(order: Order): string {
    const gateway = Locator.get<PaymentGateway>("gateway");   // смик 1
    const clock = Locator.get<Clock>("clock");                // смик 2
    const chargeId = gateway.charge(order.total());
    const receipt = new ReceiptBuilder().build(order, chargeId);
    this.audit(order, chargeId, clock);
    return receipt;
  }
  private audit(order: Order, chargeId: string, clock: Clock): void {
    Locator.get<AuditLog>("audit")                             // смик 3, у надрах
      .write(`${clock.now()} order=${order.id} charge=${chargeId}`);
  }
}
