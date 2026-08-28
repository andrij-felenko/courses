class OrderService {                     // ← більше не Manager
  constructor(                           // усе подано ЗЗОВНІ
    private validator: OrderValidator,
    private pricer: Pricer,
    private repo: OrderRepository,
    private notifier: EmailNotifier,
  ) {}

  placeOrder(cart: Cart, user: User): number {
    this.validator.check(cart);
    const total = this.pricer.total(cart, user);
    this.repo.save(user, total);
    this.notifier.orderPlaced(user, total);
    return total;
  }
}

// ── композиційний корінь: єдине місце, де програма знає справжні залежності ──
export function buildOrderService(): OrderService {
  return new OrderService(
    new OrderValidator(),
    new Pricer(),
    new OrderRepository(() => db.connect()),
    new EmailNotifier(() => new Smtp("mail.local")),
  );
}
