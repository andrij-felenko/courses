// --- БІК КОМАНД: сама поведінка, жодного коду під екран ---
type PlaceOrder = { userId: string; items: LineItem[] };
type CancelOrder = { orderId: string };

class PlaceOrderHandler {
  constructor(private orders: OrderRepository) {}
  handle(cmd: PlaceOrder): string {
    const order = Order.create(cmd.userId, cmd.items);
    order.reserveStock();
    this.orders.save(order);          // репозиторій пише нормалізовано
    return order.id;
  }
}

class CancelOrderHandler {
  constructor(private orders: OrderRepository) {}
  handle(cmd: CancelOrder): void {
    const order = this.orders.byId(cmd.orderId); // агрегат вантажимо, бо ТУТ це правда:
    order.cancel();                              // правило справді читає стан замовлення
    this.orders.save(order);
  }
}
