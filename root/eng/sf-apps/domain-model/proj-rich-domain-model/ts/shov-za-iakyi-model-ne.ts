// ── порти: інтерфейси сховища, названі мовою предмета, не мовою SQL ──
interface OrderRepository {
  byId(id: string): Promise<Order | null>;
  save(order: Order): Promise<void>;
}
interface CustomerRepository {
  byId(id: string): Promise<Customer | null>;
}

// ── сервіс: тонка оркестрація — дістати, сказати одне слово, зберегти ──
class PlaceOrderService {
  constructor(
    private readonly orders: OrderRepository,
    private readonly customers: CustomerRepository,
  ) {}

  async place(orderId: string, customerId: string): Promise<void> {
    const order = await this.orders.byId(orderId);
    if (!order) throw new DomainError(`немає замовлення ${orderId}`);
    const customer = await this.customers.byId(customerId);
    if (!customer) throw new DomainError(`немає клієнта ${customerId}`);

    order.place(customer);              // домен вирішує все — сервіс лише передав слово
    await this.orders.save(order);      // збереження живе ЗЗОВНІ моделі
  }
}
