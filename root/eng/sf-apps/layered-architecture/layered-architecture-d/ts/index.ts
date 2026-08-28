// ── ДОМЕН: правило + обіцянка сховища (жодного слова про SQL) ──
type Item = { name: string; qty: number; price: number };

class Order {
  constructor(readonly items: Item[]) {}
  total(): number {                       // правило предметної області
    return this.items.reduce((s, i) => s + i.qty * i.price, 0);
  }
}

interface OrderRepo {                      // обіцянка, а не реалізація
  save(order: Order): number;
}

// ── ІНФРАСТРУКТУРА: виконує обіцянку (залежить від домену, не навпаки) ──
class SqlOrderRepo implements OrderRepo {
  constructor(private conn: Conn) {}
  save(order: Order): number {
    return this.conn.exec(
      "INSERT INTO orders(total) VALUES (?)", order.total()).lastId;
  }
}

// ── ЗАСТОСУНОК: диригує кроками, дістає repo ззовні ──
class PlaceOrder {
  constructor(private repo: OrderRepo) {}  // бачить лише обіцянку
  run(order: Order): number {
    if (order.items.length === 0) throw new Error("порожнє замовлення");
    return this.repo.save(order);
  }
}
