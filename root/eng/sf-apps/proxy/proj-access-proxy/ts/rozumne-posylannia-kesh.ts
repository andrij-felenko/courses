class LoggingCachingOrderService implements OrderService {
  private cache = new Map<string, Order>();   // id → вже прочитане замовлення
  constructor(private real: OrderService) {}

  getOrder(id: string): Order {
    const hit = this.cache.get(id);
    if (hit !== undefined) {
      log(`getOrder(${id}) — з кешу`);
      return hit;                              // база не чіпається взагалі
    }
    log(`getOrder(${id}) — промах, іду в базу`);
    const order = this.real.getOrder(id);
    this.cache.set(id, order);                 // запам'ятали на майбутнє
    return order;
  }

  placeOrder(order: Order): string {
    log(`placeOrder(...)`);
    const id = this.real.placeOrder(order);
    this.cache.set(id, order);                 // свіже замовлення одразу відоме
    return id;
  }

  cancelOrder(id: string): void {
    log(`cancelOrder(${id})`);
    this.real.cancelOrder(id);
    this.cache.delete(id);   // ← ІНВАЛІДАЦІЯ: кеш більше не відповідає базі
  }
}
