// ── ЯДРО: бізнес-невалідність — це ДАНІ (відмова з причиною), не виняток ──
type Validated<T> =
  | { ok: true;  value: T }
  | { ok: false; reason: string };

function validateTransfer(acc: Account, amount: number): Validated<number> {
  if (amount <= 0)          return { ok: false, reason: "сума ≤ 0" };
  if (amount > acc.balance) return { ok: false, reason: "недостатньо коштів" };
  return { ok: true, value: amount };
}
