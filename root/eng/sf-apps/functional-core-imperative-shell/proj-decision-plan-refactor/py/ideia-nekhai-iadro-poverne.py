from dataclasses import dataclass

# ── Ефект як дані: опис дії, а не сама дія ──
@dataclass(frozen=True)
class Flag:       tx_id: str; reason: str
@dataclass(frozen=True)
class Freeze:     account_id: str
@dataclass(frozen=True)
class SetBalance: account_id: str; amount: float
@dataclass(frozen=True)
class Notify:     user_id: str; message: str
@dataclass(frozen=True)
class Audit:      line: str

# План — просто список описів. Це чисті дані, у них нічого не «діється».
Effect = Flag | Freeze | SetBalance | Notify | Audit
Plan = list[Effect]
