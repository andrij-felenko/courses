// ПІСЛЯ: кожен виконавець робить одне діло; сервіс тільки диригує.
interface Validator { check(cart: Cart): void; }
interface Pricer    { total(cart: Cart, user: User): number; }
interface Repo      { save(user: User, total: number): void; }
interface Notifier  { orderPlaced(user: User, total: number): void; }

class OrderService {
  constructor(                          // залежності подано ЗЗОВНІ
    private validator: Validator,
    private pricer: Pricer,
    private repo: Repo,
    private notifier: Notifier,
  ) {}

  placeOrder(cart: Cart, user: User): number {
    this.validator.check(cart);
    const total = this.pricer.total(cart, user);
    this.repo.save(user, total);
    this.notifier.orderPlaced(user, total);
    return total;
  }
}
