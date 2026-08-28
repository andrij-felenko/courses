from dataclasses import dataclass

@dataclass(frozen=True)
class Email:  to: str; body: str
@dataclass(frozen=True)
class Charge: account: str; amount: float
Effect = Email | Charge
Plan = list[Effect]

# Тлумач 1 — СПРАВЖНІ дії: єдине місце, де опис стає дотиком до світу.
async def run_real(plan: Plan) -> None:
    for e in plan:
        match e:
            case Email(to, body):    await mailer.send(to, body)
            case Charge(acc, amt):   await ledger.charge(acc, amt)

# Тлумач 2 — СУХИЙ ПРОГІН: нічого не робить, лише каже, що зробив би.
def run_dry(plan: Plan) -> list[str]:
    return [f"надіслав би лист → {e.to}" if isinstance(e, Email)
            else f"списав би {e.amount} з {e.account}" for e in plan]

# Тлумач 3 — ОЦІНКА: скільки грошей зачепить план, не виконуючи його.
def total_charged(plan: Plan) -> float:
    return sum(e.amount for e in plan if isinstance(e, Charge))
