function fill(): { gw: FakeGateway; log: FakeLog } {
  const gw = new FakeGateway(), log = new FakeLog();
  Locator.reset();
  Locator.register("gateway", gw);
  Locator.register("clock", new FakeClock());
  Locator.register("audit", log);
  Locator.register("templates", new TemplateStore());
  return { gw, log };
}

test("checkout — зліпок сьогоднішньої поведінки", () => {
  const { gw, log } = fill();
  const receipt = new OrderService().checkout(new Order("A-1", 1999));
  expect(receipt).toBe("[receipt] charge=ch_1 order=A-1");
  expect(gw.charges).toEqual([1999]);
  expect(log.lines).toEqual(["2026-07-16T10:00:00Z order=A-1 charge=ch_1"]);
});
