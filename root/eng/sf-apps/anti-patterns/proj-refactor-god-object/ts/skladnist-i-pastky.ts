test("OrderService — порядок кроків", () => {
  const seen: string[] = [];
  const svc = new OrderService(
    { check: () => { seen.push("check"); } } as OrderValidator,
    { total: () => { seen.push("total"); return 100; } } as unknown as Pricer,
    { save: () => { seen.push("save"); } } as unknown as OrderRepository,
    { orderPlaced: () => { seen.push("notify"); } } as unknown as EmailNotifier,
  );
  svc.placeOrder({ items: [{ priceCents: 1999, qty: 1 }] },
                 { id: 42, email: "vip@x", isVip: true });
  assert.deepEqual(seen, ["check", "total", "save", "notify"]);
});
