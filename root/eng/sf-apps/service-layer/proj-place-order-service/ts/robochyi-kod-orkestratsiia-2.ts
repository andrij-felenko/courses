class OrderService {
  constructor(
    private readonly orders: OrderRepository,
    private readonly payments: PaymentGateway,
    private readonly mailer: Mailer,
    private readonly idempotency: IdempotencyStore,
    private readonly tx: TransactionManager,
  ) {}

  async placeOrder(cmd: PlaceOrderCommand): Promise<OrderDto> {
    // 0. Захист від подвійного кліку: уже робили цей ключ? Віддай старе.
    const seen = await this.idempotency.find(cmd.idempotencyKey);
    if (seen) return seen;                    // ← нічого не виконуємо вдруге

    // 1..4 — усе, що має закріпитися РАЗОМ, усередині однієї транзакції
    const dto = await this.tx.run(async () => {
      const cart = await this.orders.loadCart(cmd.cartId);

      // логіка ПРЕДМЕТА: рішення ухвалює домен, не сервіс
      const order = cart.checkout();          // кине, якщо кошик порожній

      // оплата — зі своїм ключем: якщо шлюз уже бачив ключ, він не спише вдруге
      await this.payments.charge(order.total(), cmd.card, cmd.idempotencyKey);

      await this.orders.save(order);          // запис у сховище
      const result = OrderDto.from(order);    // назовні — DTO, не домен
      await this.idempotency.remember(cmd.idempotencyKey, result);
      return result;
    });
    // ↑ сюди ми дійшли, лише якщо tx.run закріпив усе (COMMIT). Помилка
    //   всередині кинула б виняток, а run зробив би ROLLBACK — до цього рядка
    //   виконання не дійшло б.

    // 5. Лист — ПІСЛЯ коміту й ПОЗА транзакцією: його не можна відкотити.
    //    Впаде пошта — замовлення вже надійно збережене, лист дошлемо окремо.
    await this.mailer.sendConfirmation(dto.order);
    return dto;
  }
}
