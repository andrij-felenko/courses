type Effect =
  | { kind: "email";  to: string; body: string }
  | { kind: "charge"; account: string; amount: number };
type Plan = Effect[];

// Тлумач 1 — СПРАВЖНІ дії: єдине місце, де опис стає дотиком до світу.
async function runReal(plan: Plan): Promise<void> {
  for (const e of plan) {
    if (e.kind === "email")  await mailer.send(e.to, e.body);
    if (e.kind === "charge") await ledger.charge(e.account, e.amount);
  }
}

// Тлумач 2 — СУХИЙ ПРОГІН: нічого не робить, лише каже, що зробив би.
function runDry(plan: Plan): string[] {
  return plan.map(e => e.kind === "email"
    ? `надіслав би лист → ${e.to}`
    : `списав би ${e.amount} з ${e.account}`);
}

// Тлумач 3 — ОЦІНКА: скільки грошей зачепить план, не виконуючи його.
function totalCharged(plan: Plan): number {
  return plan.reduce((s, e) => e.kind === "charge" ? s + e.amount : s, 0);
}
