// НАЇВНО — не робіть так. Два віддалені записи без спільної транзакції.
class OrderService {
  constructor(
    private orders: OrderRepository,   // приватна база замовлень
    private stock: StockClient,        // HTTP-клієнт до сервісу складу
  ) {}

  async placeOrder(cmd: PlaceOrder): Promise<string> {
    const order = Order.create(cmd.customerId, cmd.items);

    // КРОК 1: віддалений виклик — склад списує товар у СВОЇЙ базі
    await this.stock.reserve(order.items);   // склад списав ✓

    // ── ⟵ якщо процес упаде рівно ТУТ, товар уже списаний, а рядок нижче не виконається ──

    // КРОК 2: записуємо замовлення у ВЛАСНУ базу
    await this.orders.save(order);           // а сюди вже не дійшли ✗

    return order.id;
  }
}
