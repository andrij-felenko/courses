// place-order.test.ts ── СЦЕНАРІЙ-ТЕСТ. Той самий сценарій, але на підробках.
import { PlaceOrder } from "./domain/place-order";
import { InMemoryOrders, InMemoryNotifier } from "./infra/in-memory";

test("оформлення зберігає замовлення І шле рівно одне сповіщення", async () => {
  const orders = new InMemoryOrders();
  const notifier = new InMemoryNotifier();          // шпигун
  let n = 0;
  const placeOrder = new PlaceOrder(orders, notifier, () => String(++n));

  const order = await placeOrder.run({
    email: "kate@example.com",
    lines: [{ sku: "book", price: 200, qty: 2 }],
  });

  // ефект 1 — замовлення справді збережене, і саме те
  expect(await orders.byId("1")).toEqual(order);
  expect(order.total()).toBe(400);

  // ефект 2 — сповіщення надіслане РІВНО раз, на пошту клієнта
  expect(notifier.sent).toHaveLength(1);
  expect(notifier.sent[0].email).toBe("kate@example.com");
});
