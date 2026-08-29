"""Пошук взаємних блокувань у таблиці правил.

Безпечна таблиця, з якої система ніколи не виходить у робочий режим, — теж
дефект: бойлер, що назавжди лишився вимкненим після одного зникнення протоку,
на об'єкті вимикають запобіжником і більше не вмикають.

Стан — комбінація входів; перехід — зміна ОДНОГО входу. Але не всякий вхід
вільний: протік не з'явиться, поки виходи не наказали помпі крутитись. Саме
ця залежність і робить блокування можливим.
"""

from __future__ import annotations

from collections import deque

from .rules import INPUT_NAMES, Inputs, decide


def successors(x: Inputs) -> list[Inputs]:
    out, _, _ = decide(x)
    result: list[Inputs] = []
    for name in INPUT_NAMES:
        candidate = x.flip(name)
        if not candidate.physically_possible():
            continue
        # Протік може ПОЯВИТИСЬ лише коли помпа отримала команду крутитись;
        # зникнути він може будь-коли (повітряна пробка, закритий клапан).
        if name == "flow_ok" and not x.flow_ok and not out.pump:
            continue
        result.append(candidate)
    return result


def can_reach_heating(start: Inputs) -> bool:
    """Чи існує шлях зі стану `start` до будь-якого стану з увімкненим нагрівом."""
    seen = {start}
    queue = deque([start])
    while queue:
        state = queue.popleft()
        out, _, _ = decide(state)
        if out.heater:
            return True
        for nxt in successors(state):
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return False


def find_deadlocks() -> list[Inputs]:
    """Фізично можливі стани, з яких нагрів недосяжний жодним шляхом."""
    from .sweep import all_states

    return [
        state
        for state in all_states()
        if state.physically_possible() and not can_reach_heating(state)
    ]
