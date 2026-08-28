# ── ДО: рішення й дія намертво сплетені ──
async def handle_transaction(account_id: str, tx: Transaction) -> None:
    acc = await db.load_account(account_id)             # дія: читання

    # ── а тут, упереміш із діями, ховається все рішення ──
    if tx.amount > acc.daily_limit:
        await db.flag_transaction(tx.id, "over-limit")  # дія: запис
        await notifier.push(acc.user_id, "Транзакцію відкладено на перевірку")

    new_balance = acc.balance - tx.amount
    if new_balance < 0:
        await db.freeze_account(account_id)             # дія: запис
        await notifier.push(acc.user_id, "Рахунок заморожено: недостатньо коштів")
    else:
        await db.set_balance(account_id, new_balance)   # дія: запис

    await audit.log(f"tx {tx.id} on {account_id}: amount={tx.amount}")  # дія: запис
