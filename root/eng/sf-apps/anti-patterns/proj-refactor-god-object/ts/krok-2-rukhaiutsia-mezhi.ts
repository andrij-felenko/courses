class OrderManager {
  placeOrder(cart: Cart, user: User): number {
    this.validate(cart);
    const total = this.computeTotal(cart, user);
    this.save(user, total);
    this.notify(user, total);
    return total;
  }

  private validate(cart: Cart): void {
    if (cart.items.length === 0) throw new Error("порожній кошик");
    for (const it of cart.items)
      if (it.qty <= 0) throw new Error("хибна кількість");
  }

  private computeTotal(cart: Cart, user: User): number {
    let total = cart.items.reduce((s, it) => s + it.price * it.qty, 0);
    if (user.isVip) total *= 0.9;
    return total;
  }

  private save(user: User, total: number): void {
    this.openDb().execute(
      "INSERT INTO orders(user_id, total) VALUES(?, ?)", user.id, total);
  }

  private notify(user: User, total: number): void {
    this.openSmtp().send(
      "shop@x", user.email, `Замовлення на ${total} прийнято`);
  }
}
