// подія — плоский факт про те, що вже сталося на боці запису
type OrderPlaced = {
  type: "OrderPlaced";
  orderId: string; userId: string; total: number;
};
type OrderCancelled = { type: "OrderCancelled"; orderId: string };
type OrderEvent = OrderPlaced | OrderCancelled;

class OrderProjection {
  constructor(private read: OrderReadStore, private users: UserLookup) {}

  // на КОЖНУ подію оновлюємо denormalized-знімок
  on(ev: OrderEvent): void {
    switch (ev.type) {
      case "OrderPlaced": {
        // ім'я клієнта склеюємо ТУТ, ОДИН раз, а не на кожному читанні
        const name = this.users.nameOf(ev.userId);
        this.read.upsert({
          id: ev.orderId, userId: ev.userId, customerName: name,
          total: ev.total, status: "placed", updatedAt: Date.now(),
        });
        break;
      }
      case "OrderCancelled": {
        const cur = this.read.byId(ev.orderId);
        if (cur) this.read.upsert({ ...cur, status: "cancelled", updatedAt: Date.now() });
        break;
      }
    }
  }
}

// команда тепер, окрім запису, оголошує факт — його підхопить проєкція
class PlaceOrderHandler {
  constructor(private orders: OrderRepository, private bus: EventBus) {}
  handle(cmd: PlaceOrder): string {
    const order = Order.create(cmd.userId, cmd.items);
    order.reserveStock();
    this.orders.save(order);
    this.bus.publish({ type: "OrderPlaced", orderId: order.id,
                       userId: cmd.userId, total: order.total() });
    return order.id;
  }
}
