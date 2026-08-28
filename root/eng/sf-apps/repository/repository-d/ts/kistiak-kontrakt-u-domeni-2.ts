// справжня — над базою: тут дозволено знати про SQL і драйвер
class SqlOrderRepository implements OrderRepository {
  constructor(private db: Db, private mapper: OrderMapper) {}

  async byId(id: OrderId): Promise<Order | null> {
    const row = await this.db.queryOne("SELECT * FROM orders WHERE id = ?", [id]);
    return row ? this.mapper.toDomain(row) : null;
  }
  async forCustomer(id: CustomerId): Promise<Order[]> {
    const rows = await this.db.query("SELECT * FROM orders WHERE customer_id = ?", [id]);
    return rows.map(r => this.mapper.toDomain(r));
  }
  async save(o: Order): Promise<void> { await this.db.upsert("orders", this.mapper.toRow(o)); }
  async remove(o: Order): Promise<void> { await this.db.exec("DELETE FROM orders WHERE id = ?", [o.id]); }
}

// підставна — над звичайною мапою в пам'яті: жодної бази
class InMemoryOrderRepository implements OrderRepository {
  private store = new Map<OrderId, Order>();

  async byId(id: OrderId) { return this.store.get(id) ?? null; }
  async forCustomer(id: CustomerId) {
    return [...this.store.values()].filter(o => o.customerId === id);
  }
  async save(o: Order) { this.store.set(o.id, o); }
  async remove(o: Order) { this.store.delete(o.id); }
}
