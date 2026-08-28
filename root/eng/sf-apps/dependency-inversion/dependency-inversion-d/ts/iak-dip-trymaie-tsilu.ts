// --- domain/ (політика): порт оголошено ТУТ, мовою домену ---
export interface Orders {                       // репозиторій як абстракція домену
  save(order: Order): Promise<void>;
  byId(id: OrderId): Promise<Order | null>;
}

export class PlaceOrder {                        // сценарій-політика
  constructor(private readonly orders: Orders) {}

  async run(cmd: NewOrder): Promise<void> {
    const order = Order.create(cmd);
    await this.orders.save(order);               // знає лише обіцянку домену
  }
}
