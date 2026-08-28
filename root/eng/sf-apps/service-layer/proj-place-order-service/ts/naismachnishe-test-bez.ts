// Підставні порти — усе в пам'яті, жодної бази й жодних грошей
class FakeRepo implements OrderRepository {
  public saved: Order[] = [];
  constructor(private readonly cart: Cart) {}
  async loadCart() { return this.cart; }
  async save(o: Order) { this.saved.push(o); }
}
class FakeGateway implements PaymentGateway {
  public charges: { amount: Money; key: string }[] = [];
  constructor(private readonly fail = false) {}
  async charge(amount: Money, _card: CardToken, key: string) {
    if (this.fail) throw new Error("оплата відхилена");
    this.charges.push({ amount, key });
    return "pay_1" as PaymentId;
  }
}
class FakeMailer implements Mailer {
  public sent = 0;
  async sendConfirmation() { this.sent++; }
}
class MemIdempotency implements IdempotencyStore {
  private map = new Map<string, OrderDto>();
  async find(k: string) { return this.map.get(k) ?? null; }
  async remember(k: string, r: OrderDto) { this.map.set(k, r); }
}
// «Прозора» транзакція: виконує роботу, але виняток чесно проштовхує
class PassThroughTx implements TransactionManager {
  async run<T>(work: () => Promise<T>): Promise<T> { return work(); }
}

// ── Тести ──
test("успішне розміщення: оплата знята раз, замовлення збережене, лист надіслано", async () => {
  const repo = new FakeRepo(cartWith(2, itemsWorth(500)));
  const gw = new FakeGateway();
  const mail = new FakeMailer();
  const svc = new OrderService(repo, gw, mail, new MemIdempotency(), new PassThroughTx());

  const dto = await svc.placeOrder({ cartId: "c1", card: "tok", idempotencyKey: "k-1" });

  expect(repo.saved).toHaveLength(1);          // рівно одне замовлення
  expect(gw.charges).toHaveLength(1);          // рівно одне списання
  expect(mail.sent).toBe(1);                   // один лист
  expect(dto.total).toBe(500);
});

test("подвійний клік: той самий ключ не створює друге замовлення", async () => {
  const repo = new FakeRepo(cartWith(1, itemsWorth(100)));
  const gw = new FakeGateway();
  const svc = new OrderService(repo, gw, new FakeMailer(), new MemIdempotency(), new PassThroughTx());

  const a = await svc.placeOrder({ cartId: "c1", card: "tok", idempotencyKey: "same" });
  const b = await svc.placeOrder({ cartId: "c1", card: "tok", idempotencyKey: "same" });

  expect(b).toEqual(a);                         // той самий результат
  expect(repo.saved).toHaveLength(1);           // а НЕ два замовлення
  expect(gw.charges).toHaveLength(1);           // і НЕ два списання
});

test("збій оплати: замовлення не зберігається (все відкотилось)", async () => {
  const repo = new FakeRepo(cartWith(1, itemsWorth(100)));
  const gw = new FakeGateway(/* fail */ true);
  const svc = new OrderService(repo, gw, new FakeMailer(), new MemIdempotency(), new PassThroughTx());

  await expect(
    svc.placeOrder({ cartId: "c1", card: "tok", idempotencyKey: "k-3" }),
  ).rejects.toThrow("оплата відхилена");
  expect(repo.saved).toHaveLength(0);           // нічого не збережено
});
