from dataclasses import dataclass
from enum import Enum

class Kind(str, Enum):
    COMPENSATABLE = "compensatable"; PIVOT = "pivot"; RETRIABLE = "retriable"

@dataclass
class Step:
    name: str; kind: Kind
    run: object                    # async fn(ctx)
    compensate: object = None      # async fn(ctx) — тільки у зворотних

@dataclass
class Saga:                        # ВЕСЬ стан саги — персистентний рядок
    id: str; home_id: str
    cursor: int = 0                # індекс кроку, на якому стоїмо
    dir: str = "forward"           # "forward" | "back"
    status: str = "running"        # running|waiting|aborted|done|stuck
    attempts: int = 0              # повтори поточного повторюваного кроку
    deadline: float | None = None  # строк людського очікування

# Порти у світ: усе, що машина пише, — через ці методи (у тесті підмінимо).
class Ports:
    async def load(self, i): ...
    async def persist(self, s): ...          # звичайний тривкий запис
    def txn(self): ...                        # async-контекст: ОДНА транзакція
    async def seen(self, tx, key): ...        # ключ уже застосовували?
    async def mark(self, tx, key): ...
    async def save_in(self, tx, s): ...       # стан саги В ЦІЙ транзакції
    async def outbox(self, tx, ev): ...       # подія в outbox В ЦІЙ транзакції
    async def alert(self, s, step, err): ...  # сигнал людині (DLQ)

# freeze, unfreeze, revoke_keys … — тонкі клієнти відповідних контекстів.
STEPS = [
    Step("freeze",          Kind.COMPENSATABLE, freeze,          unfreeze),
    Step("revoke_access",   Kind.COMPENSATABLE, revoke_keys,     restore_keys),
    Step("await_claim",     Kind.COMPENSATABLE, wait_for_owner,  cancel_claim),
    Step("transfer_wipe",   Kind.PIVOT,         transfer_shred),   # без compensate
    Step("rebind_devices",  Kind.RETRIABLE,     reissue_certs),
    Step("open_billing",    Kind.RETRIABLE,     switch_billing),
    Step("welcome",         Kind.RETRIABLE,     notify_owner),
]
MAX_ATTEMPTS = 12
