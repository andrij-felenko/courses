// проєкція-перечитувач: тягне змінене від контрольної точки й оновлює знімки
class RebuildProjection {
  constructor(private db: Db, private read: OrderReadStore) {}
  private since = 0;  // контрольна точка: до цього моменту вже спроєктовано

  tick(): void {
    const changed = this.db.query(`
      SELECT o.id, o.user_id, u.name AS customerName, o.total, o.status
      FROM orders o JOIN users u ON u.id = o.user_id
      WHERE o.updated_at > ?`, [this.since]);
    for (const r of changed) {
      this.read.upsert({ id: r.id, userId: r.user_id, customerName: r.customerName,
                         total: r.total, status: r.status, updatedAt: Date.now() });
    }
    this.since = Date.now();  // посуваємо контрольну точку вперед
  }
}
