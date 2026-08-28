test("placeOrder — зафіксовано як є", () => {
  const m = new TestableOrderManager();
  const cart = { items: [{ price: 19.99, qty: 1 }, { price: 4.50, qty: 2 }] };
  const user = { id: 42, email: "vip@x", isVip: true };

  const total = m.placeOrder(cart, user);

  // ЗАФІКСОВАНО ЯК Є. Хвіст ...0999999999998 — майже напевно баг (тікет #123),
  // але ЗАРАЗ ми його не чіпаємо: тест стереже поведінку, а не правильність.
  assert.equal(total, 26.090999999999998);
  assert.deepEqual(m.conn.calls, [
    ["INSERT INTO orders(user_id, total) VALUES(?, ?)", [42, 26.090999999999998]],
  ]);
  assert.deepEqual(m.smtp.sent, [
    ["shop@x", "vip@x", "Замовлення на 26.090999999999998 прийнято"],
  ]);
});
