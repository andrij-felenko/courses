from dataclasses import dataclass

@dataclass
class Fact:
    claim: str
    evidence: str          # доказ уже на руках

@dataclass
class Assumption:
    claim: str
    p_wrong: float         # 0..1
    loss_if_wrong: float   # людино-дні
    cost_to_check: float

def should_validate_now(b) -> bool:
    if isinstance(b, Fact):
        return False
    return b.cost_to_check < b.p_wrong * b.loss_if_wrong

lock_api = Assumption("модуль замка тримає API ≥ 2 роки", 0.3, 120, 3)
should_validate_now(lock_api)  # True → перевірити до коміту
