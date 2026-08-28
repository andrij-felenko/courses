# ── ПІСЛЯ, ядро: чиста функція від даних до ПЛАНУ ──
# Нічого не читає й не пише. Той самий вхід → той самий план, завжди.
def decide(acc: Account, tx: Transaction) -> Plan:
    plan: Plan = []

    if tx.amount > acc.daily_limit:
        plan.append(Flag(tx_id=tx.id, reason="over-limit"))
        plan.append(Notify(user_id=acc.user_id,
                           message="Транзакцію відкладено на перевірку"))

    new_balance = acc.balance - tx.amount
    if new_balance < 0:
        plan.append(Freeze(account_id=acc.id))
        plan.append(Notify(user_id=acc.user_id,
                           message="Рахунок заморожено: недостатньо коштів"))
    else:
        plan.append(SetBalance(account_id=acc.id, amount=new_balance))

    plan.append(Audit(line=f"tx {tx.id} on {acc.id}: amount={tx.amount}"))
    return plan                     # просто дані — досі нічого не сталося
