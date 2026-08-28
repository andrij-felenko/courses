from dataclasses import replace

# ЧИСТЕ ядро: усі входи явні, на виході — план намірів (дані)
def decide_bonus(user: User, now: int, roll: float, cfg: Config) -> list[Effect]:
    if now - user.last_claim < cfg.cooldown_ms:
        return []                                  # на кулдауні — план ПОРОЖНІЙ

    amount  = cfg.jackpot_bonus if roll < cfg.jackpot_chance else cfg.base_bonus
    updated = replace(user, balance=user.balance + amount, last_claim=now)
    text    = f"Джекпот! +{amount}" if amount == cfg.jackpot_bonus else f"Бонус +{amount}"

    return [
        SaveUser(updated),
        AppendLedger(user.id, amount, now),
        Notify(user.email, text),
    ]
