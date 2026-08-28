// ── ПІСЛЯ, ядро: чиста функція від даних до ПЛАНУ ──
// Нічого не читає й не пише. Той самий вхід → той самий план, завжди.
function decide(acc: Account, tx: Transaction): Plan {
  const plan: Plan = [];

  if (tx.amount > acc.dailyLimit) {
    plan.push({ kind: "flag", txId: tx.id, reason: "over-limit" });
    plan.push({ kind: "notify", userId: acc.userId,
                message: "Транзакцію відкладено на перевірку" });
  }

  const newBalance = acc.balance - tx.amount;
  if (newBalance < 0) {
    plan.push({ kind: "freeze", accountId: acc.id });
    plan.push({ kind: "notify", userId: acc.userId,
                message: "Рахунок заморожено: недостатньо коштів" });
  } else {
    plan.push({ kind: "setBalance", accountId: acc.id, amount: newBalance });
  }

  plan.push({ kind: "audit", line: `tx ${tx.id} on ${acc.id}: amount=${tx.amount}` });
  return plan;                     // просто дані — досі нічого не сталося
}
