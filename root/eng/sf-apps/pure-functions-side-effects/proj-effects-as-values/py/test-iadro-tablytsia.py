def test_jackpot_plan():
    user = User(id=7, email="a@b.c", balance=300, last_claim=0)
    cfg  = Config(base_bonus=50, jackpot_bonus=500, jackpot_chance=0.05,
                  cooldown_ms=24 * 3_600_000)

    plan = decide_bonus(user, 25 * 3_600_000, 0.03, cfg)      # 25 год, кидок 0.03

    assert plan == [                                          # звіряємо ДАНІ, не поведінку
        SaveUser(User(id=7, email="a@b.c", balance=800, last_claim=25 * 3_600_000)),
        AppendLedger(7, 500, 25 * 3_600_000),
        Notify("a@b.c", "Джекпот! +500"),
    ]

def test_cooldown_empty_plan():
    user = User(id=7, email="a@b.c", balance=300, last_claim=0)
    assert decide_bonus(user, 2 * 3_600_000, 0.9, cfg) == []  # 2 год — ще рано
