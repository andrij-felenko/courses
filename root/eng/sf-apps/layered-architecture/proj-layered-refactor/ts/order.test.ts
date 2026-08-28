// order.test.ts — правило перевіряється за мілісекунди
import { Order, Promo } from "../domain/order";

test("vip discount", () => {
  const order = new Order([{ sku: "A", qty: 2, price: 100 }], Promo.Vip);
  expect(order.total()).toBe(160);   // 200 · 0.8
});

test("no promo", () => {
  const order = new Order(
    [{ sku: "A", qty: 1, price: 33.3 }, { sku: "B", qty: 3, price: 10 }]);
  expect(order.total()).toBe(63.3);
});
