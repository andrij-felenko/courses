// Каркас створює ЦЕЙ клас сам — тут смикнути можна, бо іншого входу нема
class CheckoutController {
  private core = new OrderService(              // єдиний смик — на самій межі
    Locator.get<PaymentGateway>("gateway"),
    Locator.get<Clock>("clock"),
    Locator.get<AuditLog>("audit"),
    new ReceiptBuilder(Locator.get<TemplateStore>("templates")),
  );

  handle(req: Request): Response {
    return ok(this.core.checkout(toOrder(req)));   // уся логіка — у чесному ядрі
  }
}
