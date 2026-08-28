// infra/sqlRepos.ts — тут (і лише тут) живе SQL
import type { Database } from "better-sqlite3";
import { Order } from "../domain/order";
import { ProductRepo, OrderRepo } from "../domain/repos";

export class SqlProductRepo implements ProductRepo {
  constructor(private db: Database) {}
  find(sku: string): [number, number] | null {
    const row = this.db.prepare(
      "SELECT price, stock FROM products WHERE sku = ?").get(sku) as
      { price: number; stock: number } | undefined;
    return row ? [row.price, row.stock] : null;
  }
}

export class SqlOrderRepo implements OrderRepo {
  constructor(private db: Database) {}
  add(order: Order): number {
    return Number(this.db.prepare(
      "INSERT INTO orders(total) VALUES (?)").run(order.total()).lastInsertRowid);
  }
  reduceStock(sku: string, qty: number): void {
    this.db.prepare("UPDATE products SET stock = stock - ? WHERE sku = ?")
      .run(qty, sku);
  }
}
