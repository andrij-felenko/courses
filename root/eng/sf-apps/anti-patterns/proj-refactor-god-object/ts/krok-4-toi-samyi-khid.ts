class OrderValidator {
  check(cart: Cart): void {
    if (cart.items.length === 0) throw new Error("порожній кошик");
    for (const it of cart.items)
      if (it.qty <= 0) throw new Error("хибна кількість");
  }
}

test("Validator — порожній кошик", () => {
  assert.throws(() => new OrderValidator().check({ items: [] }), /порожній кошик/);
});

test("Validator — нульова кількість", () => {
  assert.throws(
    () => new OrderValidator().check({ items: [{ price: 19.99, qty: 0 }] }),
    /хибна кількість/);
});
