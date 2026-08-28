#!/usr/bin/env python3
"""Оргсхема -> передбачений граф модулів за законом Конвея.
Вхід: команди й канали спілкування. Вихід: шви (інтерфейси) та компоненти
зв'язності (майбутні автономні частини системи)."""
from __future__ import annotations
from collections import deque

# ── ВХІД: граф організації як дані ────────────────────────────────────────
# team -> module: у базовому випадку "одна команда — один модуль" це те саме,
# лише під іншим іменем (команда «замовлення» -> модуль «замовлення»).
TEAMS = ["ord", "pay", "shp", "rep", "anl"]

# Канал спілкування = пара команд, які РЕАЛЬНО регулярно узгоджують роботу.
# Саме ці пари закон Конвея відіб'є як стики між модулями.
CHANNELS = [
    ("ord", "pay"),   # замовлення ↔ оплата
    ("ord", "shp"),   # замовлення ↔ доставка
    ("rep", "anl"),   # звіти ↔ аналітика (окрема пара)
]


def adjacency(teams: list[str], channels: list[tuple[str, str]]) -> dict[str, set[str]]:
    """Матриця суміжності модулів як словник сусідств. Симетрична:
    канал двобічний, тож ребро додаємо в обидва боки."""
    adj: dict[str, set[str]] = {t: set() for t in teams}
    for a, b in channels:
        adj[a].add(b)
        adj[b].add(a)          # «говорити» — взаємне: (a,b) і (b,a) — той самий стик
    return adj


def seams(channels: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Передбачені інтерфейси = усі канали, нормалізовані як (менший, більший),
    щоб (ord,pay) і (pay,ord) не рахувались двічі."""
    return sorted({tuple(sorted(c)) for c in channels})


def components(teams: list[str], adj: dict[str, set[str]]) -> list[list[str]]:
    """Компоненти зв'язності = майбутні автономні частини системи.
    Кожна — максимальна група модулів, зчеплених прямо чи ланцюжком."""
    seen: set[str] = set()
    result: list[list[str]] = []
    for start in teams:
        if start in seen:
            continue
        # обхід завширшки від непозначеного вузла — збираємо весь досяжний шматок
        group, queue = [], deque([start])
        seen.add(start)
        while queue:
            node = queue.popleft()
            group.append(node)
            for nb in adj[node]:
                if nb not in seen:
                    seen.add(nb)
                    queue.append(nb)
        result.append(sorted(group))
    return result


def predict(teams: list[str], channels: list[tuple[str, str]]) -> None:
    adj = adjacency(teams, channels)
    ss = seams(channels)
    cc = components(teams, adj)
    print(f"Передбачені шви (інтерфейси): {len(ss)}")
    for a, b in ss:
        print(f"  {a} <-> {b}")
    print(f"\nАвтономні частини (компоненти зв'язності): {len(cc)}")
    for i, group in enumerate(cc, 1):
        print(f"  #{i}: {{{', '.join(group)}}}")


if __name__ == "__main__":
    predict(TEAMS, CHANNELS)
