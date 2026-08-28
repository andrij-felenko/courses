describe("LoyaltyService.isLoyal", () => {
  let orders: InMemoryOrderRepository;
  let loyalty: LoyaltyService;

  beforeEach(() => {
    orders = new InMemoryOrderRepository();   // ← свіжий на КОЖЕН тест
    loyalty = new LoyaltyService(orders);
  });

  it("три останні оплачені понад 500 — постійний", async () => {
    await orders.save(paidOrder("o-1", "c-19", 600, 1));
    await orders.save(paidOrder("o-2", "c-19", 700, 2));
    await orders.save(paidOrder("o-3", "c-19", 800, 3));
    expect(await loyalty.isLoyal("c-19")).toBe(true);
  });

  it("оплачених лише два — ще не постійний", async () => {
    await orders.save(paidOrder("o-1", "c-19", 600, 1));
    await orders.save(paidOrder("o-2", "c-19", 700, 2));
    expect(await loyalty.isLoyal("c-19")).toBe(false);
  });

  it("рівно 500 — це не «понад 500»", async () => {
    await orders.save(paidOrder("o-1", "c-19", 600, 1));
    await orders.save(paidOrder("o-2", "c-19", 500, 2));   // ← межа
    await orders.save(paidOrder("o-3", "c-19", 700, 3));
    expect(await loyalty.isLoyal("c-19")).toBe(false);
  });

  it("старе дешеве не тягне вниз — дивимось лише три останні", async () => {
    await orders.save(paidOrder("o-0", "c-19", 10, 0));    // ← найстаріше й дешеве
    await orders.save(paidOrder("o-1", "c-19", 600, 1));
    await orders.save(paidOrder("o-2", "c-19", 700, 2));
    await orders.save(paidOrder("o-3", "c-19", 800, 3));
    expect(await loyalty.isLoyal("c-19")).toBe(true);
  });

  it("неоплачене не рахується, хай яке дороге", async () => {
    await orders.save(paidOrder("o-1", "c-19", 600, 1));
    await orders.save(paidOrder("o-2", "c-19", 700, 2));
    await orders.save(new Order("o-3", "c-19", 9000, day(3)));   // ← лишилось «new»
    expect(await loyalty.isLoyal("c-19")).toBe(false);
  });

  it("чужі замовлення не рахуються", async () => {
    await orders.save(paidOrder("o-1", "c-19", 600, 1));
    await orders.save(paidOrder("o-2", "c-19", 700, 2));
    await orders.save(paidOrder("x-1", "c-77", 800, 3));         // ← інший клієнт
    expect(await loyalty.isLoyal("c-19")).toBe(false);
  });
});
