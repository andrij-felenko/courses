"""Повний перебір 2^N комбінацій дискретних входів."""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field

from .rules import INPUT_NAMES, RULES, UNSPECIFIED, Inputs, Outputs, decide


@dataclass(frozen=True)
class Finding:
    state: Inputs
    rule: str
    detail: str


@dataclass
class SweepReport:
    total: int = 0
    impossible: int = 0
    unsafe: list[Finding] = field(default_factory=list)
    unspecified: list[Finding] = field(default_factory=list)
    conflicts: list[Finding] = field(default_factory=list)
    fired: dict[str, int] = field(default_factory=dict)

    @property
    def dead_rules(self) -> list[str]:
        """Правила, що не виграли жодного стану, — мертвий текст у таблиці."""
        return [name for name, count in self.fired.items() if count == 0]

    @property
    def ok(self) -> bool:
        return not (self.unsafe or self.unspecified or self.conflicts or self.dead_rules)


def unsafe_reason(x: Inputs, out: Outputs) -> str | None:
    """Інваріанти безпеки — окремо від таблиці, інакше вони її не перевіряють."""
    if out.heater:
        if not out.pump:
            return "нагрів без помпи — сухий ТЕН"
        if not x.level_low:
            return "нагрів порожнього бака"
        if not x.flow_ok:
            return "нагрів без протоку"
        if not x.pressure_ok:
            return "нагрів без тиску в контурі"
        if x.e_stop:
            return "нагрів попри натиснутий аварійний стоп"
        if not x.physically_possible():
            return "нагрів за суперечливих показів рівня"
    if out.pump and x.e_stop:
        return "помпа працює попри натиснутий аварійний стоп"
    return None


def all_states() -> list[Inputs]:
    return [
        Inputs(**dict(zip(INPUT_NAMES, combo)))
        for combo in itertools.product((False, True), repeat=len(INPUT_NAMES))
    ]


def run_sweep() -> SweepReport:
    report = SweepReport(fired={rule.name: 0 for rule in RULES})

    for state in all_states():
        report.total += 1
        if not state.physically_possible():
            report.impossible += 1

        out, winner, matched = decide(state)

        if winner == UNSPECIFIED:
            report.unspecified.append(
                Finding(state, UNSPECIFIED, "жодне правило не описує цей стан")
            )
        else:
            report.fired[winner] += 1

        # Кілька правил однакового найвищого пріоритету, що наказують різне,
        # роблять результат залежним від порядку рядків у таблиці.
        if matched:
            top = min(rule.priority for rule in matched)
            rivals = [rule for rule in matched if rule.priority == top]
            if len({rule.outputs for rule in rivals}) > 1:
                report.conflicts.append(
                    Finding(
                        state,
                        " / ".join(rule.name for rule in rivals),
                        "правила рівного пріоритету наказують різне",
                    )
                )

        reason = unsafe_reason(state, out)
        if reason:
            report.unsafe.append(Finding(state, winner, reason))

    return report
