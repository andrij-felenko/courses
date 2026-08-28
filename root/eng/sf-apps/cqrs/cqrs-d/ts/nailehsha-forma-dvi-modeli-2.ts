// ЗАПИТ повертає плоский тип рівно під потребу екрана — не доменний Order.
type OrderView = {
  id: string; customerName: string; total: number; status: string;
};

class OrderQueries {
  constructor(private db: Db) {}

  // читаємо коротким шляхом; жодних правил, жодних агрегатів
  getOrderView(id: string): OrderView {
    return this.db.queryOne(`
      SELECT o.id, u.name AS customerName, o.total, o.status
      FROM orders o JOIN users u ON u.id = o.user_id
      WHERE o.id = ?`, [id]);
  }
}
