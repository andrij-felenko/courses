# -*- coding: utf-8 -*-
"""Матриця рішення, яка звітує про власну хиткість."""
from collections import Counter
from dataclasses import dataclass, replace
from itertools import product


@dataclass(frozen=True)
class Criterion:
    name: str
    weight: float           # ×1..×5; «зарубка» незгоди = 1


@dataclass(frozen=True)
class Option:
    name: str
    scores: tuple           # 1..5 за кожним критерієм
    meets: tuple            # так/ні за кожною ВИМОГОЮ — не оцінка, а вирок


def total(opt, crits):
    return sum(c.weight * s for c, s in zip(crits, opt.scores))


def rejected(opt, reqs):
    """Вимоги, які варіант провалив. Непорожньо → це не суперник, а відмова."""
    return [r for r, ok in zip(reqs, opt.meets) if not ok]


def duel(winner, rival, crits):
    """Скільки зарубок незгоди витримує перемога winner над rival."""
    d = [a - b for a, b in zip(winner.scores, rival.scores)]
    margin = sum(c.weight * di for c, di in zip(crits, d))
    swing = sum(abs(di) for di in d)              # Σ|dᵢ| — падіння запасу за зарубку
    notches = margin / swing if swing else float('inf')
    stance = [c.weight - (1 if di > 0 else -1 if di < 0 else 0)
              for c, di in zip(crits, d)]         # найгірша УЗГОДЖЕНА незгода
    return margin, swing, notches, stance


def oat(winner, rival, crits, lo=1.0, hi=5.0):
    """Класика: совати ОДНУ вагу, решту тримати. Вага нічиєї для кожного критерію."""
    d = [a - b for a, b in zip(winner.scores, rival.scores)]
    margin = sum(c.weight * di for c, di in zip(crits, d))
    out = []
    for c, di in zip(crits, d):
        if di == 0:
            out.append((c.name, None, "не розрізняє варіанти"))
            continue
        tie = c.weight - margin / di
        note = ("зміна %+.0f%%" % ((tie - c.weight) / c.weight * 100)
                if lo <= tie <= hi else "поза шкалою ×%g..×%g" % (lo, hi))
        out.append((c.name, tie, note))
    return out


def sweep(opts, crits, lo=1.0, hi=5.0):
    """Груба сила: увесь окіл ±1 зарубка. Перевірка формули, а не заміна їй."""
    grids = [[w for w in (c.weight - 1, c.weight, c.weight + 1) if lo <= w <= hi]
             for c in crits]
    wins, ties, n = Counter(), 0, 0
    for ws in product(*grids):
        variant = [replace(c, weight=w) for c, w in zip(crits, ws)]
        tot = [(total(o, variant), o.name) for o in opts]
        best = max(t for t, _ in tot)
        leaders = [nm for t, nm in tot if t == best]
        n += 1
        if len(leaders) == 1:
            wins[leaders[0]] += 1
        else:
            ties += 1
    return wins, ties, n


CRITS = [Criterion("зчеплення служб", 3),
         Criterion("затримка", 2),
         Criterion("проста експлуатація", 2),
         Criterion("стійкість до збою", 3)]

# Вимога з розділу «Контекст»: оформлення НЕ має падати, коли склад недоступний.
REQS = ["оформлення живе, коли склад недоступний"]

OPTS = [#                       зчепл. затр. експл. стійк.      вимога
        Option("синхр. виклик", (2,     5,    5,     2),        (False,)),
        Option("черга подій",   (5,     3,    2,     5),        (True,)),
        Option("спільна табл.", (1,     4,    4,     2),        (True,))]
