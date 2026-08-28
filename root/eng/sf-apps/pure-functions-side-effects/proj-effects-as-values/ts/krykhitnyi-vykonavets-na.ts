// ВИКОНАВЕЦЬ: намір → справжній ефект. Жодних рішень, лише розгалуження за kind.
function run(eff: Effect, db: Db, mailer: Mailer): void {
  switch (eff.kind) {
    case "saveUser":     db.saveUser(eff.user); return;
    case "appendLedger": db.appendLedger(eff.userId, eff.amount, eff.at); return;
    case "notify":       mailer.send(eff.to, eff.text); return;
    default:             const _never: never = eff; return _never;   // забув варіант — не збереться
  }
}

// ОБОЛОНКА: принести дані → спитати ядро → прокрутити план. Три рядки, нуль рішень.
function claimBonus(userId: number, deps: Deps): void {
  const user = deps.db.loadUser(userId);
  const plan = decideBonus(user, deps.clock(), deps.rng(), deps.cfg);
  for (const eff of plan) run(eff, deps.db, deps.mailer);
}
