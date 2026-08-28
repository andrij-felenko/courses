class InMemoryOrderRepository implements OrderRepository {
  private readonly rows = new Map<OrderId, OrderRow>();   // РЯДКИ, не Order

  async byId(id: OrderId): Promise<Order | null> {
    const row = this.rows.get(id);
    return row ? toDomain(row) : null;                     // щоразу новий об'єкт
  }

  async recentPaidOrders(customerId: CustomerId, limit: number): Promise<Order[]> {
    const cmp = (x: string, y: string) => (x < y ? -1 : x > y ? 1 : 0);
    return [...this.rows.values()]
      .filter(r => r.customer_id === customerId && r.status === "paid")   // WHERE
      .sort((a, b) => cmp(b.created_at, a.created_at) || cmp(b.id, a.id)) // ORDER BY … DESC
      .slice(0, limit)                                                    // LIMIT
      .map(toDomain);
  }

  async save(order: Order): Promise<void> {
    this.rows.set(order.id, toRow(order));                 // знімок, не посилання
  }

  async remove(order: Order): Promise<void> {
    this.rows.delete(order.id);
  }
}
