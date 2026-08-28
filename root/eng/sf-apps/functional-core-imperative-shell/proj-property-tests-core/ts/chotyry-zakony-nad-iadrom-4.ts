test("сума частин розбитого повернення = ціле", () => {
  fc.assert(
    fc.property(
      fc.nat({ max: 1_000_000 }),
      fc.integer({ min: 1, max: 100 }),
      (total, n) => {
        const parts = splitRefund(total, n);
        const sum = parts.reduce((a, b) => a + b, 0);
        return sum === total && parts.length === n;
      }),
    { numRuns: 10_000 },
  );
});
