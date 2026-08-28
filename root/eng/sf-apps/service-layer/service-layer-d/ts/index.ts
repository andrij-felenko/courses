// Сервісний шар: одна операція = один сценарій. Сам НЕ рахує правил —
// відкриває транзакцію, дістає домен, делегує йому, зберігає, сповіщає.
class OrderService {
  constructor(
    private readonly orders: OrderRepository,   // сховище (інтерфейс, не база)
    private readonly payments: PaymentGateway,  // платіжний шлюз (інтерфейс)
    private readonly mailer: Mailer,            // пошта (інтерфейс)
    private readonly tx: TransactionManager,
  ) {}

  async placeOrder(cmd: PlaceOrderCommand): Promise<OrderDto> {
    return this.tx.run(async () => {
      const cart = await this.orders.loadCart(cmd.cartId);

      // ↓ логіка ПРЕДМЕТА — рішення ухвалює домен, не сервіс
      const order = cart.checkout();          // кине помилку, якщо кошик порожній

      await this.payments.charge(order.total(), cmd.card);  // domain дав суму
      await this.orders.save(order);
      await this.mailer.sendConfirmation(order);            // логіка ЗАСТОСУНКУ
      return OrderDto.from(order);            // назовні — DTO, не голий домен
    });
  }
}
