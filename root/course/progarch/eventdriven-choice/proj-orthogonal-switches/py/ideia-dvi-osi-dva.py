from dataclasses import dataclass, replace
from functools import reduce

# ── Спільний домен: команда → факт, і згортка факту в стан ──
@dataclass(frozen=True)
class LockState:
    locked: bool = False
    last_actor: str | None = None
    at: int = 0

INITIAL = LockState()

@dataclass(frozen=True)
class Command:               # kind: "lock" | "unlock"
    kind: str; actor: str; at: int

@dataclass(frozen=True)
class DoorEvent:             # доконаний ФАКТ, а не наказ
    type: str; actor: str; at: int   # type: "DoorLocked" | "DoorUnlocked"

def decide(s: LockState, c: Command) -> DoorEvent:
    if c.kind == "lock"   and s.locked:      raise ValueError("вже зачинено")
    if c.kind == "unlock" and not s.locked:  raise ValueError("вже відчинено")
    typ = "DoorLocked" if c.kind == "lock" else "DoorUnlocked"
    return DoorEvent(typ, c.actor, c.at)

def apply(s: LockState, e: DoorEvent) -> LockState:   # згортка на один крок
    return replace(s, locked=(e.type == "DoorLocked"), last_actor=e.actor, at=e.at)
