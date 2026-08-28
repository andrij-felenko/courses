from dataclasses import dataclass
from functools import reduce

# Подія — доконаний факт. Проста незмінна структура: що сталося і на скільки.
@dataclass(frozen=True)
class Deposited:
    amount: float

@dataclass(frozen=True)
class Withdrawn:
    amount: float

@dataclass(frozen=True)
class Account:
    balance: float = 0.0                       # нульовий стан — з нього все починається

# apply: узяти стан і ОДНУ подію, повернути НАСТУПНИЙ стан. Без побічних ефектів.
def apply(state: Account, e) -> Account:
    if isinstance(e, Deposited):
        return Account(state.balance + e.amount)
    if isinstance(e, Withdrawn):
        return Account(state.balance - e.amount)
    raise ValueError(f"невідома подія: {e!r}")

# Поточний стан = згортка ВСІХ подій від порожнього. Ось і вся «база».
def replay(events) -> Account:
    return reduce(apply, events, Account())
