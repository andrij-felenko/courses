test("джекпот на щасливому кидку → повний план", () => {
  const user: User = { id: 7, email: "a@b.c", balance: 300, lastClaim: 0 };
  const cfg: Config = { baseBonus: 50, jackpotBonus: 500, jackpotChance: 0.05,
                        cooldownMs: 24 * 3600_000 };

  const plan = decideBonus(user, 25 * 3600_000, 0.03, cfg);   // 25 год, кидок 0.03

  expect(plan).toEqual([                                       // звіряємо ДАНІ, не поведінку
    { kind: "saveUser",     user: { id: 7, email: "a@b.c", balance: 800, lastClaim: 25*3600_000 } },
    { kind: "appendLedger", userId: 7, amount: 500, at: 25 * 3600_000 },
    { kind: "notify",       to: "a@b.c", text: "Джекпот! +500" },
  ]);
});

test("на кулдауні → план порожній", () => {
  const user: User = { id: 7, email: "a@b.c", balance: 300, lastClaim: 0 };
  expect(decideBonus(user, 2 * 3600_000, 0.9, cfg)).toEqual([]);   // 2 год — ще рано
});
