// ── ДВА чистих рішення, кожне повертає план/вирок ──
type Verdict =
  | { ok: true;  amount: number }             // можна знімати стільки
  | { ok: false; plan: Plan };                // не можна — ось що зробити

// Рішення 1: чи взагалі дозволити зняття (чисте).
function decideWithdraw(acc: Account, req: WithdrawReq): Verdict {
  if (acc.frozen)
    return { ok: false, plan: [{ kind: "notify", userId: acc.userId,
                                 message: "Рахунок заморожено" }] };
  if (req.amount > acc.balance)
    return { ok: false, plan: [{ kind: "notify", userId: acc.userId,
                                 message: "Недостатньо коштів" }] };
  return { ok: true, amount: req.amount };
}

// Рішення 2: що робити ПІСЛЯ зняття, знаючи фактично списану суму (чисте).
function afterWithdraw(acc: Account, requested: number, settled: number): Plan {
  if (settled < requested)                    // банк списав менше, ніж просили
    return [{ kind: "notify", userId: acc.userId,
              message: `Списано частково: ${settled}` },
            { kind: "audit", line: `partial withdraw ${acc.id}: ${settled}` }];
  return [{ kind: "notify", userId: acc.userId, message: `Видано: ${settled}` },
          { kind: "audit", line: `withdraw ${acc.id}: ${settled}` }];
}

// ── ОБОЛОНКА: чергує читання/дію з двома чистими рішеннями ──
async function withdraw(accountId: string, req: WithdrawReq): Promise<void> {
  const acc = await db.loadAccount(accountId);        // читати
  const v = decideWithdraw(acc, req);                  // вирішити (1)
  if (!v.ok) { await runPlan(v.plan); return; }        // діяти (відмова) і вийти

  const settled = await bank.withdraw(accountId, v.amount);  // діяти + читати результат
  const plan = afterWithdraw(acc, v.amount, settled);  // вирішити (2)
  await runPlan(plan);                                 // діяти
}
