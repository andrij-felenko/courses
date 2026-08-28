// ── ДО: одна функція говорить зі світом п'ятьма голосами ──
long   nowMs();                 // глобальний годинник
double rng();                   // глобальний генератор
Config cfg = loadConfig();      // глобальний конфіг

long claimBonus(int userId) {
    User user = db.loadUser(userId);                 // читання з БД
    long now  = nowMs();                             // прихований вхід: час
    if (now - user.lastClaim < cfg.cooldownMs)       // ще рано
        return 0;
    double roll = rng();                             // прихований вхід: випадковість
    long amount = (roll < cfg.jackpotChance) ? cfg.jackpotBonus : cfg.baseBonus;

    user.balance  += amount;                         // мутація входу
    user.lastClaim = now;
    db.saveUser(user);                               // запис у БД
    db.appendLedger(userId, amount, now);            // ще запис у БД
    mailer.send(user.email, "Бонус +" + std::to_string(amount));  // лист
    return amount;
}
