from dataclasses import dataclass

# ── ДВА чистих рішення, кожне повертає план/вирок ──
@dataclass(frozen=True)
class Allow:  amount: float           # можна знімати стільки
@dataclass(frozen=True)
class Deny:   plan: Plan              # не можна — ось що зробити
Verdict = Allow | Deny

# Рішення 1: чи взагалі дозволити зняття (чисте).
def decide_withdraw(acc: Account, req: WithdrawReq) -> Verdict:
    if acc.frozen:
        return Deny([Notify(user_id=acc.user_id, message="Рахунок заморожено")])
    if req.amount > acc.balance:
        return Deny([Notify(user_id=acc.user_id, message="Недостатньо коштів")])
    return Allow(amount=req.amount)

# Рішення 2: що робити ПІСЛЯ зняття, знаючи фактично списану суму (чисте).
def after_withdraw(acc: Account, requested: float, settled: float) -> Plan:
    if settled < requested:            # банк списав менше, ніж просили
        return [Notify(user_id=acc.user_id, message=f"Списано частково: {settled}"),
                Audit(line=f"partial withdraw {acc.id}: {settled}")]
    return [Notify(user_id=acc.user_id, message=f"Видано: {settled}"),
            Audit(line=f"withdraw {acc.id}: {settled}")]

# ── ОБОЛОНКА: чергує читання/дію з двома чистими рішеннями ──
async def withdraw(account_id: str, req: WithdrawReq) -> None:
    acc = await db.load_account(account_id)             # читати
    v = decide_withdraw(acc, req)                        # вирішити (1)
    if isinstance(v, Deny):
        await run_plan(v.plan); return                   # діяти (відмова) і вийти

    settled = await bank.withdraw(account_id, v.amount)  # діяти + читати результат
    plan = after_withdraw(acc, v.amount, settled)        # вирішити (2)
    await run_plan(plan)                                 # діяти
