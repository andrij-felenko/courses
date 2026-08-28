// ── ПІСЛЯ: тест ядра — звіряння списку описів. Нуль моків ──
test("over-limit flags and notifies", () => {
  const acc: Account = { id: "a1", userId: "u1", balance: 500, dailyLimit: 100 };
  const plan = decide(acc, { id: "t1", amount: 150 });

  expect(plan).toContainEqual({ kind: "flag", txId: "t1", reason: "over-limit" });
  expect(plan).toContainEqual({ kind: "notify", userId: "u1",
    message: "Транзакцію відкладено на перевірку" });
});

test("insufficient funds freezes, not sets balance", () => {
  const acc: Account = { id: "a2", userId: "u2", balance: 100, dailyLimit: 9999 };
  const plan = decide(acc, { id: "t2", amount: 150 });   // 100 − 150 < 0

  expect(plan).toContainEqual({ kind: "freeze", accountId: "a2" });
  expect(plan.some(e => e.kind === "setBalance")).toBe(false);  // балансу НЕ чіпає
});
