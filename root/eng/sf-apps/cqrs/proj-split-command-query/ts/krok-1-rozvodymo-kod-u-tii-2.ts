// --- БІК ЗАПИТІВ: плоскі типи під екран, читання повз доменну модель ---
type OrderView = { id: string; customerName: string; total: number; status: string };

class OrderQueries {
  constructor(private db: Db) {}

  getOrderView(id: string): OrderView {
    return this.db.queryOne(`
      SELECT o.id, u.name AS customerName, o.total, o.status
      FROM orders o JOIN users u ON u.id = o.user_id
      WHERE o.id = ?`, [id]);
  }

  // список — ОДИН запит із JOIN, а не агрегат на кожен рядок
  listOrders(userId: string): OrderView[] {
    return this.db.query(`
      SELECT o.id, u.name AS customerName, o.total, o.status
      FROM orders o JOIN users u ON u.id = o.user_id
      WHERE o.user_id = ?
      ORDER BY o.created_at DESC`, [userId]);
  }
}
