// application/placeOrder.ts — сценарій; бачить лише інтерфейси домену
import { Order, Line, Promo } from "../domain/order";
import { ProductRepo, OrderRepo } from "../domain/repos";

export class OutOfStock extends Error {}
export class UnknownProduct extends Error {}

const promoOf = (s?: string): Promo =>
  s === "SPRING" ? Promo.Spring : s === "VIP" ? Promo.Vip : Promo.None;

export class PlaceOrder {
  constructor(
    private products: ProductRepo,     // обіцянки, не драйвери
    private orders: OrderRepo,
  ) {}

  run(rawItems: { sku: string; qty: number }[], promo?: string) {
    const lines: Line[] = [];
    for (const it of rawItems) {
      const found = this.products.find(it.sku);
      if (!found) throw new UnknownProduct(it.sku);
      const [price, stock] = found;
      if (stock < it.qty) throw new OutOfStock(it.sku);
      lines.push({ sku: it.sku, qty: it.qty, price });
    }

    const order = new Order(lines, promoOf(promo));
    const orderId = this.orders.add(order);
    for (const l of lines) this.orders.reduceStock(l.sku, l.qty);
    return { orderId, total: order.total() };
  }
}
