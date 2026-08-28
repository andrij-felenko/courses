from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional

class Kind(Enum):
    COMPENSATABLE = "compensatable"; PIVOT = "pivot"; RETRIABLE = "retriable"

@dataclass(frozen=True)
class Step:
    name: str
    kind: Kind
    run: Callable[["Handover"], None]              # локальна транзакція у своєму контексті
    compensate: Optional[Callable[["Handover"], None]] = None  # зустрічна дія — лише до півота

# Порядок і є суть: усе зворотне ДО півота, усе обов'язкове — ПІСЛЯ.
HANDOVER = [
    Step("freeze",          Kind.COMPENSATABLE, freeze,          unfreeze),
    Step("revoke_access",   Kind.COMPENSATABLE, revoke_old_keys, restore_old_keys),
    Step("await_claim",     Kind.COMPENSATABLE, wait_for_new_owner, cancel_claim),
    Step("transfer_wipe",   Kind.PIVOT,         transfer_and_shred),   # ← точка неповороту
    Step("rebind_devices",  Kind.RETRIABLE,     reissue_certs),
    Step("open_billing",    Kind.RETRIABLE,     switch_billing),
    Step("welcome",         Kind.RETRIABLE,     notify_new_owner),
]

def drive(h):
    done = []
    for step in HANDOVER:
        try:
            step.run(h)                 # кожен run ідемпотентний: повтор ≠ подвоєння
            done.append(step)
        except Exception:
            if step.kind is Kind.RETRIABLE:
                raise                   # після півота — не скасовуй, повторюй
            for s in reversed(done):    # до півота — задкуй, відкочуючи
                if s.compensate:
                    s.compensate(h)
            return aborted(h)
