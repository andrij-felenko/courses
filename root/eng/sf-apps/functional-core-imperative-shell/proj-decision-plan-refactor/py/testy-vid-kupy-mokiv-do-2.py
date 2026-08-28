# ── ПІСЛЯ: тест ядра — звіряння списку описів. Нуль моків ──
def test_over_limit_flags_and_notifies():
    acc = Account(id="a1", user_id="u1", balance=500, daily_limit=100)
    plan = decide(acc, Transaction(id="t1", amount=150))

    assert Flag(tx_id="t1", reason="over-limit") in plan
    assert Notify(user_id="u1",
                  message="Транзакцію відкладено на перевірку") in plan

def test_insufficient_funds_freezes_not_sets_balance():
    acc = Account(id="a2", user_id="u2", balance=100, daily_limit=9999)
    plan = decide(acc, Transaction(id="t2", amount=150))   # 100 − 150 < 0

    assert Freeze(account_id="a2") in plan
    assert not any(isinstance(e, SetBalance) for e in plan)  # балансу НЕ чіпає
