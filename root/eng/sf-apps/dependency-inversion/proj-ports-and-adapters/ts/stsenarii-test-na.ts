test("недійсне замовлення НЕ зберігається й НЕ шле нічого", async () => {
  const orders = new InMemoryOrders();
  const notifier = new InMemoryNotifier();
  const placeOrder = new PlaceOrder(orders, notifier, () => "x");

  await expect(placeOrder.run({ email: "no-at-sign", lines: [] }))
    .rejects.toThrow();                         // правило домену відхилило

  expect(await orders.byId("x")).toBeNull();    // нічого не збережено
  expect(notifier.sent).toHaveLength(0);        // нікого не сповіщено
});
