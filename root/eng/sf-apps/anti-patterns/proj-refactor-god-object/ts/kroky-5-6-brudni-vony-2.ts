class OrderManager {
  private validator = new OrderValidator();                        // ← сам
  private pricer = new Pricer();                                   // ← сам
  private repo = new OrderRepository(() => this.openDb());         // ← сам
  private notifier = new EmailNotifier(() => this.openSmtp());     // ← сам

  placeOrder(cart: Cart, user: User): number {
    this.validator.check(cart);
    const total = this.pricer.total(cart, user);
    this.repo.save(user, total);
    this.notifier.orderPlaced(user, total);
    return total;
  }

  protected openDb(): Conn { return db.connect(); }
  protected openSmtp(): Smtp { return new Smtp("mail.local"); }
}
