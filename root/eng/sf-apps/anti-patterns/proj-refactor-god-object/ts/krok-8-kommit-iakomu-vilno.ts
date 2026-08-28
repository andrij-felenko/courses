class Pricer {
  total(cart: Cart, user: User): number {
    const cents = cart.items.reduce((s, it) => s + it.priceCents * it.qty, 0);
    return user.isVip ? Math.round(cents * 9 / 10) : cents;   // явне округлення
  }
}

test("Pricer — знижка для VIP", () => {
  const cart = { items: [{ priceCents: 1999, qty: 1 }, { priceCents: 450, qty: 2 }] };
  assert.equal(new Pricer().total(cart, { id: 42, email: "vip@x", isVip: true }), 2609);
});
