// ЧИСТЕ ядро: усі входи явні, на виході — план намірів (дані)
std::vector<Effect> decideBonus(const User& user, long now, double roll, const Config& cfg) {
    if (now - user.lastClaim < cfg.cooldownMs)
        return {};                                 // на кулдауні — план ПОРОЖНІЙ

    long amount   = (roll < cfg.jackpotChance) ? cfg.jackpotBonus : cfg.baseBonus;
    User updated  = user;                          // копія, вхід не чіпаємо
    updated.balance  += amount;
    updated.lastClaim = now;
    std::string text = (amount == cfg.jackpotBonus)
        ? "Джекпот! +" + std::to_string(amount)
        : "Бонус +"    + std::to_string(amount);

    return {
        SaveUser{updated},
        AppendLedger{user.id, amount, now},
        Notify{user.email, text},
    };
}
