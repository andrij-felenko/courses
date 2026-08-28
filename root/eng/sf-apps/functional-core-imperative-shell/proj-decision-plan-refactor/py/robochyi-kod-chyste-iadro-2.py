# ── ПІСЛЯ, оболонка (1): ВИКОНАВЕЦЬ плану ──
# Єдине місце, де опис стає дією. Сам нічого не вирішує.
async def run_plan(plan: Plan) -> None:
    for e in plan:
        match e:
            case Flag(tx_id, reason):       await db.flag_transaction(tx_id, reason)
            case Freeze(account_id):        await db.freeze_account(account_id)
            case SetBalance(account_id, a): await db.set_balance(account_id, a)
            case Notify(user_id, message):  await notifier.push(user_id, message)
            case Audit(line):               await audit.log(line)

# ── ПІСЛЯ, оболонка (2): тонка обгортка ──
# Принести → вирішити (ядром) → виконати. Рішень тут нема.
async def handle_transaction(account_id: str, tx: Transaction) -> None:
    acc  = await db.load_account(account_id)    # принести
    plan = decide(acc, tx)                       # ← усе рішення тут, у ядрі
    await run_plan(plan)                         # винести
