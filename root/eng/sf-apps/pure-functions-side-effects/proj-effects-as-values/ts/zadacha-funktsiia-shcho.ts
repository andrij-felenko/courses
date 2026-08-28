// ── ДО: одна функція говорить зі світом п'ятьма голосами ──
let clock = () => Date.now();          // глобальний годинник
let rng   = () => Math.random();       // глобальний генератор
let cfg   = loadConfig();              // глобальний конфіг

function claimBonus(userId: number): number {
  const user = db.loadUser(userId);              // читання з БД
  const now  = clock();                          // прихований вхід: час
  if (now - user.lastClaim < cfg.cooldownMs) {   // ще рано
    return 0;
  }
  const roll   = rng();                          // прихований вхід: випадковість
  const amount = roll < cfg.jackpotChance ? cfg.jackpotBonus : cfg.baseBonus;

  user.balance  += amount;                        // мутація входу
  user.lastClaim = now;
  db.saveUser(user);                              // запис у БД
  db.appendLedger(userId, amount, now);           // ще запис у БД
  mailer.send(user.email, `Бонус +${amount}`);    // посилка листа
  return amount;
}
