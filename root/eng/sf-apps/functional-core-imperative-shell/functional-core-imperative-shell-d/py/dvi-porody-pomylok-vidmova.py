from dataclasses import dataclass

# ── ЯДРО: бізнес-невалідність — це ДАНІ (відмова з причиною), не виняток ──
@dataclass(frozen=True)
class Ok:   value: float
@dataclass(frozen=True)
class Err:  reason: str
Validated = Ok | Err

def validate_transfer(acc: Account, amount: float) -> Validated:
    if amount <= 0:            return Err("сума ≤ 0")
    if amount > acc.balance:   return Err("недостатньо коштів")
    return Ok(amount)
