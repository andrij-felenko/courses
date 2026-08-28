test("заморожений рахунок ніколи не списують", () => {
  fc.assert(
    fc.property(
      frozenAccGen,
      fc.record({ amount: fc.nat({ max: 2_000_000 }) }),
      (acc, req) => {
        const effects = decideWithdraw(acc, req);
        return effects.every(e => e.kind !== "debit");   // жодного списання
      }),
    { numRuns: 10_000 },
  );
});
