interface OrderService {
  getOrder(id: string): Order;           // читання: часте, безпечне, добре кешується
  placeOrder(order: Order): string;      // запис: створює замовлення, треба право
  cancelOrder(id: string): void;         // запис: скасовує, треба право (та ще й вище)
}

// Справжній сервіс: ходить у базу, нічого не знає про права й кеш.
class RealOrderService implements OrderService {
  getOrder(id: string): Order {
    return db.query("SELECT ... WHERE id = ?", id);   // дорогий похід у базу
  }
  placeOrder(order: Order): string {
    return db.insert(order);
  }
  cancelOrder(id: string): void {
    db.update("UPDATE orders SET state='cancelled' WHERE id = ?", id);
  }
}
