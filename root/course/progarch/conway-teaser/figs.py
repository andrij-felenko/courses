# -*- coding: utf-8 -*-
"""Фігури для кроку «Закон Конвея як анонс» (root/course/progarch, views-and-communication).
1) Дзеркало: структура системи копіює структуру спілкування (з «кривим» стиком там,
   де люди не говорять). 2) DH у часі: скільки команд — стільки в системі швів.
Запуск: python figs.py  → пише у ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Дзеркало: система повторює форму спілкування ───────────────────────────
def fig_mirror():
    W, H = 1080, 470
    frags = []
    # дві панелі
    frags.append(rect(50, 64, 450, 352, fill="#fafbff", stroke=MUTED, sw=1.4, rx=14))
    frags.append(rect(580, 64, 450, 352, fill="#fafbff", stroke=MUTED, sw=1.4, rx=14))
    frags.append(text(275, 98, "Люди: хто з ким говорить", size=15, bold=True, color=NEG))
    frags.append(text(805, 98, "Система: що з чим стикується", size=15, bold=True, color=INK))

    # трикутник вершин (центри) — ліворуч люди, праворуч модулі
    Lp = {"a": (160, 185), "b": (390, 185), "c": (275, 345)}
    Rp = {"a": (690, 185), "b": (920, 185), "c": (805, 345)}

    def edges(P):
        # спершу лінії (їх сховають рамки зверху); кінці лежать у центрах рамок
        frags.append(line(P["a"][0], P["a"][1], P["b"][0], P["b"][1], color=LINE, sw=2))
        frags.append(line(P["b"][0], P["b"][1], P["c"][0], P["c"][1], color=LINE, sw=2))
        frags.append(line(P["a"][0], P["a"][1], P["c"][0], P["c"][1],
                          color=POS, sw=2, dash="7 5"))

    def nodes(P, labels):
        for key, lab in labels.items():
            cx, cy = P[key]
            frags.append(fitbox(cx - 75, cy - 27, 150, 54, lab, size=14))

    edges(Lp)
    edges(Rp)
    nodes(Lp, {"a": "Команда\nапки", "b": "Команда\nхмари", "c": "Команда\nхабу"})
    nodes(Rp, {"a": "Апка", "b": "Хмара", "c": "Хаб"})

    # знак «та сама форма» між панелями
    frags.append(text(540, 200, "≅", size=44, bold=True, color=INK))
    frags.append(text(540, 238, "та сама форма", size=12, color=MUTED))

    # легенда внизу
    frags.append(line(150, 445, 188, 445, color=LINE, sw=2))
    frags.append(text(198, 449, "— напряму говорять → чистий стик",
                      size=13, color=INK, anchor="start"))
    frags.append(line(600, 445, 638, 445, color=POS, sw=2, dash="7 5"))
    frags.append(text(648, 449, "— майже не говорять → кривий стик",
                      size=13, color=POS, anchor="start"))

    render(os.path.join(OUT, "mirror.svg"), W, H, *frags,
           title="Структуру системи задає структура спілкування")


# ── 2. DH у часі: скільки команд, стільки й швів ──────────────────────────────
def fig_teams_seams():
    W, H = 1000, 420
    frags = []
    cols = [170, 500, 830]
    people = [[170], [475, 525], [795, 830, 865]]
    caps = ["1 засновник", "2 команди", "3 команди"]
    counts = ["1 модуль", "2 модулі", "3 модулі"]

    # верх: люди-кружечки
    for group in people:
        for px in group:
            frags.append(circle(px, 95, 13, fill="#eef2ff", stroke=NEG, sw=1.8))
    for cx, cap in zip(cols, caps):
        frags.append(text(cx, 142, cap, size=14, bold=True, color=NEG))
    # стрілка «команди задають форму»
    for cx in cols:
        frags.append(arrow(cx, 160, cx, 198, color=MUTED, sw=1.8))

    # низ: модулі системи — стільки, скільки команд
    def box(cx, w, lab):
        frags.append(fitbox(cx - w / 2, 212, w, 68, lab, size=14))

    box(cols[0], 210, "усе в одному\nфайлі")
    box(440, 116, "дім")
    box(560, 116, "хмара")
    box(745, 84, "апка")
    box(830, 84, "хмара")
    box(915, 84, "хаб")

    for cx, cnt in zip(cols, counts):
        frags.append(text(cx, 312, cnt, size=13, color=MUTED))

    render(os.path.join(OUT, "teams-seams.svg"), W, H, *frags,
           title="Скільки команд — стільки в системі швів")


if __name__ == "__main__":
    fig_mirror()
    fig_teams_seams()
    print("OK: 2 фігури у", OUT)
