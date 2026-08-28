test("Pricer — знижка для VIP", () => {
  const cart = { items: [{ price: 19.99, qty: 1 }, { price: 4.50, qty: 2 }] };
  assert.equal(new Pricer().total(cart, { id: 42, email: "vip@x", isVip: true }),
               26.090999999999998);
});

test("Pricer — без знижки", () => {
  const cart = { items: [{ price: 19.99, qty: 1 }, { price: 4.50, qty: 2 }] };
  assert.equal(new Pricer().total(cart, { id: 7, email: "bob@x", isVip: false }), 28.99);
});
