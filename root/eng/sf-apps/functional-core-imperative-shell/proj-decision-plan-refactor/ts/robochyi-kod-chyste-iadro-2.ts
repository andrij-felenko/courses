// ── ПІСЛЯ, оболонка (1): ВИКОНАВЕЦЬ плану ──
// Єдине місце, де опис стає дією. Сам нічого не вирішує.
async function runPlan(plan: Plan): Promise<void> {
  for (const e of plan) {
    switch (e.kind) {
      case "flag":       await db.flagTransaction(e.txId, e.reason); break;
      case "freeze":     await db.freezeAccount(e.accountId);        break;
      case "setBalance": await db.setBalance(e.accountId, e.amount); break;
      case "notify":     await notifier.push(e.userId, e.message);   break;
      case "audit":      await audit.log(e.line);                    break;
    }
  }
}

// ── ПІСЛЯ, оболонка (2): тонка обгортка ──
// Принести → вирішити (ядром) → виконати. Рішень тут нема.
async function handleTransaction(accountId: string, tx: Transaction): Promise<void> {
  const acc  = await db.loadAccount(accountId);   // принести
  const plan = decide(acc, tx);                    // ← усе рішення тут, у ядрі
  await runPlan(plan);                             // винести
}
