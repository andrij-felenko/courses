class SpyNotifier implements Notifier {
  readonly calls: Array<{ email: string; total: Money }> = [];
  sendConfirmation(email: string, total: Money): void {
    this.calls.push({ email, total });
  }
}

function test_confirmation_sent() {
  const spy = new SpyNotifier();
  placeOrder(
    { orderId: "ORD-2", email: "olena@shop.ua", items: [{ sku: "KAVA-250", qty: 2 }] },
    { catalog: new StubCatalog({ "KAVA-250": 250 }), repo: new InMemoryOrders(),
      notifier: spy, audit: dummyAudit },
  );

  // перевірка ВЗАЄМОДІЇ: рівно одне сповіщення, з тими даними
  assert.equal(spy.calls.length, 1);
  assert.deepEqual(spy.calls[0], { email: "olena@shop.ua", total: 500 }); // 2·250
}
