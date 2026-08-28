// ЧИСТЕ ядро: усі входи явні, на виході — план намірів (дані)
function decideBonus(user: User, now: number, roll: number, cfg: Config): Effect[] {
  if (now - user.lastClaim < cfg.cooldownMs)
    return [];                                     // на кулдауні — план ПОРОЖНІЙ

  const amount  = roll < cfg.jackpotChance ? cfg.jackpotBonus : cfg.baseBonus;
  const updated = { ...user, balance: user.balance + amount, lastClaim: now };
  const text    = amount === cfg.jackpotBonus ? `Джекпот! +${amount}` : `Бонус +${amount}`;

  return [
    { kind: "saveUser",     user: updated },
    { kind: "appendLedger", userId: user.id, amount, at: now },
    { kind: "notify",       to: user.email, text },
  ];
}
