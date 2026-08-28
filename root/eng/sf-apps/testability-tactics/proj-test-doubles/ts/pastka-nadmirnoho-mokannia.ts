// КРИХКИЙ тест: заморожує внутрішню структуру виконання
function test_place_order_fragile() {
  const seq: string[] = [];
  const catalog: PriceCatalog = { priceOf: (s) => { seq.push(`price:${s}`); return 250; } };
  const repo:    OrderRepository = { save: () => { seq.push("save"); }, find: () => undefined };
  const notify:  Notifier  = { sendConfirmation: () => { seq.push("notify"); } };
  const audit:   AuditLog  = { record: () => { seq.push("audit"); } };

  placeOrder(
    { orderId: "ORD-4", email: "o@x", items: [{ sku: "KAVA-250", qty: 2 }] },
    { catalog, repo, notifier: notify, audit },
  );

  // припущення про ТОЧНУ структуру, а не про поведінку:
  assert.deepEqual(seq, ["price:KAVA-250", "save", "notify", "audit"]);
}
