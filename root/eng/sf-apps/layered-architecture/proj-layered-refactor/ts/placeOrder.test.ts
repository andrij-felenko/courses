// placeOrder.test.ts — той самий сценарій БЕЗ бази
import { PlaceOrder, OutOfStock } from "../application/placeOrder";
import { Order } from "../domain/order";

class FakeRepo {                      // одна фальшивка на обидві обіцянки
  saved: Order[] = [];
  constructor(private catalog: Record<string, [number, number]>) {}
  find(sku: string): [number, number] | null {
    return this.catalog[sku] ?? null;
  }
  add(order: Order): number {
    this.saved.push(order);
    return this.saved.length;         // «id» = порядковий номер
  }
  reduceStock(sku: string, qty: number): void {
    this.catalog[sku][1] -= qty;
  }
}

test("places and reduces stock", () => {
  const repo = new FakeRepo({ A: [100, 5] });
  const place = new PlaceOrder(repo, repo);
  const res = place.run([{ sku: "A", qty: 2 }], "VIP");

  expect(res.total).toBe(160);        // 200 · 0.8
  expect(repo["catalog"].A[1]).toBe(3); // залишок 5 → 3
  expect(repo.saved).toHaveLength(1);
});

test("rejects when out of stock", () => {
  const repo = new FakeRepo({ A: [100, 1] });
  const place = new PlaceOrder(repo, repo);
  expect(() => place.run([{ sku: "A", qty: 2 }])).toThrow(OutOfStock);
  expect(repo["catalog"].A[1]).toBe(1); // залишок НЕ чіпали
});
