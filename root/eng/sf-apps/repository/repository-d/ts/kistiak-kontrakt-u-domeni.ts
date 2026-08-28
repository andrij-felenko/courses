// контракт — біля домену; названий доменною мовою, не мовою таблиць
interface OrderRepository {
  byId(id: OrderId): Promise<Order | null>;
  forCustomer(id: CustomerId): Promise<Order[]>;
  save(order: Order): Promise<void>;
  remove(order: Order): Promise<void>;
}

// сервіс залежить ЛИШЕ від контракту — жодного натяку на сховище
class LoyaltyService {
  constructor(private orders: OrderRepository) {}

  async isLoyal(customerId: CustomerId): Promise<boolean> {
    const paid = (await this.orders.forCustomer(customerId))
      .filter(o => o.isPaid());
    return paid.length >= 3 && paid.every(o => o.total > 500);
  }
}
