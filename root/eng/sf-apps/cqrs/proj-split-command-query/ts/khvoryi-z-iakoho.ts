// ТОВСТИЙ СЕРВІС: запис і читання в одному класі, на спільній моделі.
class OrderService {
  constructor(private db: Db) {}

  // --- запис: тут ЖИВУТЬ правила ---
  placeOrder(userId: string, items: LineItem[]): string {
    const order = Order.create(userId, items); // конструктор боронить інваріанти
    order.reserveStock();                       // кине, якщо товару бракує
    this.db.insert("orders", order.toRow());
    for (const li of order.lines) this.db.insert("order_lines", li.toRow());
    return order.id;
  }

  cancelOrder(id: string): void {
    const order = this.load(id);      // тягнемо ВЕСЬ агрегат заради одного поля статусу
    order.cancel();                   // правило: не можна скасувати відвантажене
    this.db.update("orders", order.toRow());
  }

  // --- читання: тут правил нема, але шлях той самий, через доменну модель ---
  getOrderView(id: string): OrderView {
    const order = this.load(id);      // знову ВЕСЬ агрегат — заради показу трьох полів
    const user = this.db.queryOne("SELECT name FROM users WHERE id=?", [order.userId]);
    return {
      id: order.id,
      customerName: user.name,        // склеюємо дані для екрана ПРЯМО в сервісі запису
      total: order.total(),
      status: order.status,
    };
  }

  listOrders(userId: string): OrderView[] {
    const rows = this.db.query("SELECT id FROM orders WHERE user_id=?", [userId]);
    return rows.map(r => this.getOrderView(r.id)); // N+1: по агрегату на кожен рядок
  }

  private load(id: string): Order {
    const row = this.db.queryOne("SELECT * FROM orders WHERE id=?", [id]);
    const lines = this.db.query("SELECT * FROM order_lines WHERE order_id=?", [id]);
    return Order.fromRows(row, lines);
  }
}
