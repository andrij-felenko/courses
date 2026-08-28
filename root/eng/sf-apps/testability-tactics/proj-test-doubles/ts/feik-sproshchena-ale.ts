import assert from "node:assert/strict";

function test_total_and_persisted() {
  const catalog = new StubCatalog({ "KAVA-250": 250, "CUKOR-1": 90 }); // заглушка
  const repo = new InMemoryOrders();                                    // фейк
  const spy = new SpyNotifier();                                        // тут байдужий
  const cmd: PlaceOrderCmd = {
    orderId: "ORD-1", email: "olena@shop.ua",
    items: [{ sku: "KAVA-250", qty: 2 }, { sku: "CUKOR-1", qty: 1 }],
  };

  const order = placeOrder(cmd, { catalog, repo, notifier: spy, audit: dummyAudit });

  // перевірка СТАНУ: сума порахована й замовлення справді збережене
  assert.equal(order.total, 590);              // 2·250 + 1·90 = 590
  assert.deepEqual(repo.find("ORD-1"), order); // фейк повертає те, що поклали
}
