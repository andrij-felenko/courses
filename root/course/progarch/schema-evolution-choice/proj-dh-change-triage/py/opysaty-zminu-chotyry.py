from dataclasses import dataclass
from typing import Literal

ChangeKind = Literal["add", "reshape", "remove", "redefine"]
Strategy = Literal[
    "REBUILD", "ADD", "MIGRATE_IN_PLACE", "SCHEMA_ON_READ", "RETIRE", "FORBIDDEN"]
Window = Literal["none", "short", "long", "grows-with-decoder", "may-never-close"]
Compat = Literal["n/a", "backward", "forward", "backward+forward"]


@dataclass(frozen=True)
class DataChange:
    what: str
    derived: bool                # дані — чиста функція джерела правди?
    rewritable: bool             # збережене можна переписати на місці?
    controls_both_sides: bool    # читача й писаря деплоїш РАЗОМ?
    kind: ChangeKind


@dataclass(frozen=True)
class Decision:
    strategy: Strategy
    window: Window
    backfill: bool               # чи треба чіпати старі рядки
    compat: Compat
    note: str
