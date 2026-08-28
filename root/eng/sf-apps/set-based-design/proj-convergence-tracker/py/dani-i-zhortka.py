from dataclasses import dataclass
from datetime import date, timedelta
from collections.abc import Callable

# ── Варіант: усе, що ми про нього знаємо ─────────────────────────────
@dataclass(frozen=True)
class Option:
    name: str
    max_throughput: int    # повідомлень/с, які тягне без болю
    ops_cost_week: int     # людино-годин експлуатації на тиждень
    exactly_once: bool     # чи дає доставку «точно раз»

# ── Доказовість: головний запобіжник трекера ─────────────────────────
MEASURED = "виміряно"   # цифра з проби на живому навантаженні
QUOTED   = "документ"   # SLA, прайс, специфікація — можна відкрити й перечитати
ASSUMED  = "здогад"     # ніхто не перевіряв
PROVEN   = (MEASURED, QUOTED)

@dataclass(frozen=True)
class Fact:
    id: str
    says: str                        # що встановлено — людською мовою
    evidence: str                    # MEASURED / QUOTED / ASSUMED
    source: str                      # де лежить доказ
    when: date
    holds: Callable[[Option], bool]  # хто ВИЖИВАЄ під цим фактом

# ── Події журналу: усе, що з набором колись сталося ──────────────────
@dataclass(frozen=True)
class Considered:
    when: date
    option: Option
    why: str

@dataclass(frozen=True)
class Learned:
    fact: Fact

@dataclass(frozen=True)
class Retracted:
    when: date
    fact_id: str
    why: str

Event = Considered | Learned | Retracted

def happened(ev: Event) -> date:
    return ev.fact.when if isinstance(ev, Learned) else ev.when

# ── Стан — ЗГОРТКА журналу, а не збережене поле ──────────────────────
@dataclass(frozen=True)
class State:
    alive: list[Option]
    killed_by: dict[str, list[Fact]]
    facts: list[Fact]

def replay(journal: list[Event], upto: date | None = None) -> State:
    considered: list[Option] = []
    facts: list[Fact] = []
    dead: set[str] = set()
    for ev in journal:
        # not break, а continue: журнал може лежати не строго за датами
        if upto is not None and happened(ev) > upto:
            continue
        if isinstance(ev, Considered):
            considered.append(ev.option)
        elif isinstance(ev, Learned):
            facts.append(ev.fact)
        elif isinstance(ev, Retracted):
            dead.add(ev.fact_id)
    live = [f for f in facts if f.id not in dead]
    alive: list[Option] = []
    killed_by: dict[str, list[Fact]] = {}
    for o in considered:
        killers = [f for f in live if not f.holds(o)]
        if killers:
            killed_by[o.name] = killers   # хто саме вбив — уся сила журналу тут
        else:
            alive.append(o)
    return State(alive, killed_by, live)
