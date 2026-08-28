# ── ДО: одна функція говорить зі світом п'ятьма голосами ──
clock = lambda: now_ms()          # глобальний годинник
rng   = lambda: random.random()   # глобальний генератор
cfg   = load_config()             # глобальний конфіг

def claim_bonus(user_id: int) -> int:
    user = db.load_user(user_id)                     # читання з БД
    now  = clock()                                   # прихований вхід: час
    if now - user.last_claim < cfg.cooldown_ms:      # ще рано
        return 0
    roll   = rng()                                   # прихований вхід: випадковість
    amount = cfg.jackpot_bonus if roll < cfg.jackpot_chance else cfg.base_bonus

    user.balance  += amount                          # мутація входу
    user.last_claim = now
    db.save_user(user)                               # запис у БД
    db.append_ledger(user_id, amount, now)           # ще запис у БД
    mailer.send(user.email, f"Бонус +{amount}")      # посилка листа
    return amount
