test("знижку видно в підсумку ⟺ до-знижковий > 1000", () => {
  fc.assert(
    fc.property(
      fc.array(itemGen),
      fc.double({ min: 0, max: 0.3, noNaN: true }),
      (items, taxRate) => {
        const o = priceOrder(items, taxRate);
        const expected = o.preDiscount > 1000 ? o.preDiscount * 0.95 : o.preDiscount;
        return o.discounted === (o.preDiscount > 1000)
            && Math.abs(o.total - expected) < 1e-6;
      }),
    { numRuns: 10_000 },
  );
});
