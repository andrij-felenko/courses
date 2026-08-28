// ── ЯДРО повертає ОПИС дій (дані), а не виконує їх ──
type Effect =
  | { kind: "email"; to: string; template: "welcome" }
  | { kind: "credit"; account: string; amount: number };

function onSignup(user: User): Effect[] {
  const effects: Effect[] = [{ kind: "email", to: user.email, template: "welcome" }];
  if (user.referred)                                     // рішення — тут, у ядрі
    effects.push({ kind: "credit", account: user.id, amount: 100 });
  return effects;                                        // просто дані, нічого не сталося
}

// ── ОБОЛОНКА виконує описи; сама нічого не вирішує ──
async function runSignup(user: User): Promise<void> {
  for (const e of onSignup(user)) {
    if (e.kind === "email")  await mailer.send(e.to, e.template);
    if (e.kind === "credit") await ledger.credit(e.account, e.amount);
  }
}
