import { test } from "vitest";

test("підсумок ніколи не від'ємний", () => {
  fc.assert(
    fc.property(
      fc.array(itemGen),
      fc.double({ min: 0, max: 0.3, noNaN: true }),
      (items, taxRate) => {
        const o = priceOrder(items, taxRate);
        return o.preDiscount >= 0 && o.total >= 0;
      }),
    { numRuns: 10_000 },
  );
});
