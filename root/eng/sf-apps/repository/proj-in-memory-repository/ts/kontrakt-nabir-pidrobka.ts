function orderRepositoryContract(
  name: string,
  make: () => Promise<{ repo: OrderRepository; dispose: () => Promise<void> }>,
) {
  describe(`OrderRepository · контракт · ${name}`, () => {
    let repo: OrderRepository;
    let dispose: () => Promise<void>;

    beforeEach(async () => {
      const made = await make();
      repo = made.repo;
      dispose = made.dispose;
    });
    afterEach(() => dispose());

    it("збережене дістається рівним", async () => {
      const o = paidOrder("o-1", "c-19", 600, 1);
      await repo.save(o);
      const got = await repo.byId("o-1");
      expect(got).not.toBeNull();
      expect(got!.total).toBe(600);
      expect(got!.isPaid()).toBe(true);
      expect(got!.createdAt.toISOString()).toBe(o.createdAt.toISOString());
    });

    it("мутація ПІСЛЯ save не видима без повторного save", async () => {
      const o = new Order("o-1", "c-19", 600, day(1));   // «new»
      await repo.save(o);
      o.markPaid();                                      // ← без save
      expect((await repo.byId("o-1"))!.isPaid()).toBe(false);
    });

    it("recentPaidOrders: найновіші перші, не більше за limit", async () => {
      await repo.save(paidOrder("o-1", "c-19", 100, 1));
      await repo.save(paidOrder("o-3", "c-19", 300, 3));
      await repo.save(paidOrder("o-2", "c-19", 200, 2));   // навмисно не по черзі
      const got = await repo.recentPaidOrders("c-19", 2);
      expect(got.map(o => o.id)).toEqual(["o-3", "o-2"]);
    });

    it("recentPaidOrders: нічию за часом розв'язує більший id", async () => {
      await repo.save(paidOrder("o-1", "c-19", 100, 5));
      await repo.save(paidOrder("o-9", "c-19", 200, 5));   // той самий час
      const got = await repo.recentPaidOrders("c-19", 1);
      expect(got.map(o => o.id)).toEqual(["o-9"]);
    });

    it("recentPaidOrders: чужих і неоплачених нема", async () => {
      await repo.save(paidOrder("x-1", "c-77", 100, 1));
      await repo.save(new Order("o-2", "c-19", 200, day(2)));
      expect(await repo.recentPaidOrders("c-19", 10)).toEqual([]);
    });

    it("після remove byId дає null", async () => {
      const o = paidOrder("o-1", "c-19", 600, 1);
      await repo.save(o);
      await repo.remove(o);
      expect(await repo.byId("o-1")).toBeNull();
    });
  });
}

// швидка колонка — на кожен коміт
orderRepositoryContract("InMemory", async () => ({
  repo: new InMemoryOrderRepository(),
  dispose: async () => {},
}));

// повільна колонка — той САМИЙ набір, але вже проти живої бази; у CI
orderRepositoryContract("Postgres", async () => {
  const db = await openTestDb();
  await db.exec("TRUNCATE orders");
  return { repo: new SqlOrderRepository(db, mapper), dispose: () => db.close() };
});
