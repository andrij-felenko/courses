import fc from "fast-check";

// товар: ціна — невід'ємне ціле (копійки), кількість — 0..100
const itemGen = fc.record({
  price: fc.nat({ max: 100_000 }),
  qty:   fc.integer({ min: 0, max: 100 }),
});

// заморожений рахунок: усе випадкове, але frozen ЗАВЖДИ true
const frozenAccGen = fc.record({
  id:      fc.string(),
  userId:  fc.string(),
  balance: fc.nat({ max: 1_000_000 }),
  frozen:  fc.constant(true),
});
