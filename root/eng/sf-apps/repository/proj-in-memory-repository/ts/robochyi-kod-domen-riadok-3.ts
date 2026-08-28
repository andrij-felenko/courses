interface OrderRepository {
  byId(id: OrderId): Promise<Order | null>;

  /** Оплачені замовлення клієнта: найновіші перші, не більше за limit.
   *  За однакового часу — старшим вважається більший id. */
  recentPaidOrders(customerId: CustomerId, limit: number): Promise<Order[]>;

  save(order: Order): Promise<void>;
  remove(order: Order): Promise<void>;
}

class LoyaltyService {
  constructor(private readonly orders: OrderRepository) {}

  async isLoyal(customerId: CustomerId): Promise<boolean> {
    const recent = await this.orders.recentPaidOrders(customerId, 3);
    return recent.length === 3 && recent.every(o => o.total > 500);
  }
}
