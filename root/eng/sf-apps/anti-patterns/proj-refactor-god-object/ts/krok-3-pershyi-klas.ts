class Pricer {
  total(cart: Cart, user: User): number {
    let total = cart.items.reduce((s, it) => s + it.price * it.qty, 0);
    if (user.isVip) total *= 0.9;
    return total;
  }
}

class OrderManager {
  private pricer = new Pricer();         // поки що створює сам — це тимчасово

  private computeTotal(cart: Cart, user: User): number {
    return this.pricer.total(cart, user);   // старе ім'я лишилось, тіло переїхало
  }
}
