// application/placeOrder.ts — сценарій під однією транзакцією
export class SqlUnitOfWork {
  constructor(private db: import("better-sqlite3").Database) {}
  atomic<T>(work: () => T): T {
    const tx = this.db.transaction(work); // better-sqlite3: усе або нічого
    return tx();                           // commit/rollback — автоматично
  }
}

export class PlaceOrder {
  constructor(
    private products: ProductRepo,
    private orders: OrderRepo,
    private uow: SqlUnitOfWork,
  ) {}
  run(rawItems, promo) {
    // ... збір lines і перевірки як раніше ...
    return this.uow.atomic(() => {         // межу транзакції відкриває застосунок
      const orderId = this.orders.add(order);
      for (const l of lines) this.orders.reduceStock(l.sku, l.qty);
      return { orderId, total: order.total() };
    });
  }
}
