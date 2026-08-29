#!/usr/bin/env python3
"""Повний перебір таблиці правил: інваріанти, неврахований стан, блокування.

Запуск із теки проєкту:  python main.py
Код повернення 0 — таблиця чиста, 1 — знайдено дефекти.
"""

from __future__ import annotations

from ruletable.reachability import find_deadlocks
from ruletable.rules import INPUT_NAMES
from ruletable.sweep import run_sweep


def main() -> int:
    report = run_sweep()

    print(f"Перебрано станів: {report.total} (2^{len(INPUT_NAMES)})")
    print(f"  фізично неможливих (парадокс поплавців): {report.impossible}")
    print(f"  станів без жодного правила: {len(report.unspecified)}")
    print(f"  конфліктів рівного пріоритету: {len(report.conflicts)}")
    print(f"  порушень інваріантів безпеки: {len(report.unsafe)}")

    print("  спрацювань правил:")
    for name, count in report.fired.items():
        print(f"    {name:<22} {count:>3}")

    for finding in report.unspecified:
        print(f"  [ПРОГАЛИНА] {finding.state}: {finding.detail}")
    for finding in report.conflicts:
        print(f"  [КОНФЛІКТ]  {finding.state} -> {finding.rule}: {finding.detail}")
    for finding in report.unsafe:
        print(f"  [НЕБЕЗПЕКА] {finding.state} -> {finding.rule}: {finding.detail}")
    for name in report.dead_rules:
        print(f"  [МЕРТВЕ ПРАВИЛО] {name}: не виграє жодного стану")

    deadlocks = find_deadlocks()
    print(f"\nВзаємних блокувань (нагрів недосяжний): {len(deadlocks)}")
    for state in deadlocks:
        print(f"  [БЛОКУВАННЯ] {state}")

    ok = report.ok and not deadlocks
    print("\nПідсумок:", "таблиця чиста" if ok else "таблицю треба правити")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
