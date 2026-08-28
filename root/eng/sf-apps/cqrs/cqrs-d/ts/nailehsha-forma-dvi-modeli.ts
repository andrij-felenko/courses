// КОМАНДА — намір змінити стан. Проста структура: що зробити й з чим.
type PlaceOrder = { userId: string; items: LineItem[] };

class PlaceOrderHandler {
  constructor(private orders: OrderRepository) {}

  handle(cmd: PlaceOrder): void {
    // доменна модель із правилами: конструктор боронить інваріанти
    const order = Order.create(cmd.userId, cmd.items);
    order.reserveStock();          // кине помилку, якщо товару бракує
    this.orders.save(order);       // зберігаємо нормалізовано
  }
}
