class MockNotifier implements Notifier {
  private expected: { email: string; total: Money } | null = null;
  private actual:   { email: string; total: Money } | null = null;

  expectConfirmation(email: string, total: Money): void {
    this.expected = { email, total };            // очікування — НАПЕРЕД
  }
  sendConfirmation(email: string, total: Money): void {
    if (this.actual) throw new Error("сповіщення надіслано двічі"); // падає одразу
    this.actual = { email, total };
  }
  verify(): void {                               // мок звіряє себе сам
    const ok = this.actual && this.expected
      && this.actual.email === this.expected.email
      && this.actual.total === this.expected.total;
    if (!ok) throw new Error(
      `очікували ${JSON.stringify(this.expected)}, дістали ${JSON.stringify(this.actual)}`);
  }
}

function test_confirmation_mock() {
  const mock = new MockNotifier();
  mock.expectConfirmation("olena@shop.ua", 500); // ← спершу озброюємо очікуванням
  placeOrder(
    { orderId: "ORD-3", email: "olena@shop.ua", items: [{ sku: "KAVA-250", qty: 2 }] },
    { catalog: new StubCatalog({ "KAVA-250": 250 }), repo: new InMemoryOrders(),
      notifier: mock, audit: dummyAudit },
  );
  mock.verify();                                  // ← мок сам виносить вирок
}
