@dataclass(frozen=True)
class Account:     id: str; user_id: str; balance: int; frozen: bool
@dataclass(frozen=True)
class WithdrawReq: amount: int
@dataclass(frozen=True)
class Debit:       account_id: str; amount: int
@dataclass(frozen=True)
class Notify:      user_id: str; message: str

def decide_withdraw(acc: Account, req: WithdrawReq) -> list:
    if acc.frozen:                                       # заморожено — тільки сповістити
        return [Notify(user_id=acc.user_id, message="Рахунок заморожено")]
    if req.amount > acc.balance:                         # не вистачає — тільки сповістити
        return [Notify(user_id=acc.user_id, message="Недостатньо коштів")]
    return [Debit(account_id=acc.id, amount=req.amount),
            Notify(user_id=acc.user_id, message=f"Видано {req.amount}")]
