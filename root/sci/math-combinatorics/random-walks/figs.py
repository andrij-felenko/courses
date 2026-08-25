# -*- coding: utf-8 -*-
"""Фігури для теми «Випадкові блукання у графах (Random Walks)»
(book/algorithms/complexity-computability/random-walks)."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

FIELD_F, FIELD_S = "#e9f7ef", "#27ae60"
POS_F, POS_S = "#fdecea", "#e74c3c"
BLUE_F, BLUE_S = "#ebf5fb", "#2980b9"
PURPLE_F, PURPLE_S = "#f5eeef", "#8e44ad"
AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"


def fig_transition_matrix():
    """Фігура 1: Граф та відповідна матриця стохастичних переходів P = D^-1 A."""
    W, H = 1020, 480
    frags = []

    # Заголовок розділів
    frags.append(textbox(230, 45, "1. Структура графа G = (V, E)", size=15, bold=True, fill=BLUE_F, stroke=BLUE_S, sw=2, pad=10)[0])
    frags.append(textbox(710, 45, "2. Стохастична матриця переходів P = D⁻¹ A", size=15, bold=True, fill=PURPLE_F, stroke=PURPLE_S, sw=2, pad=10)[0])

    # Лівий блок: Граф з 4 вершинами
    nodes = {
        "v1": (120, 180, "v₁ (d=3)"),
        "v2": (340, 180, "v₂ (d=2)"),
        "v3": (120, 360, "v₃ (d=2)"),
        "v4": (340, 360, "v₄ (d=1)")
    }

    edges = [
        (120, 180, 340, 180, "1/3"),
        (120, 180, 120, 360, "1/3"),
        (120, 180, 340, 360, "1/3"),
        (340, 180, 120, 360, "1/2"),
    ]

    for x1, y1, x2, y2, label in edges:
        frags.append(line(x1, y1, x2, y2, color="#7f8c8d", sw=2))
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        frags.append(rect(mx - 18, my - 12, 36, 24, rx=4, fill="#ffffff", stroke="#bdc3c7", sw=1))
        frags.append(mtext(mx, my + 4, [label], size=11, bold=True, color="#2c3e50"))

    for k, (x, y, lbl) in nodes.items():
        frags.append(circle(x, y, 32, fill=BLUE_F, stroke=BLUE_S, sw=2.5))
        frags.append(mtext(x, y + 4, [lbl], size=12, bold=True, color=BLUE_S))

    # Правий блок: Матриця P
    headers = ["v₁", "v₂", "v₃", "v₄"]
    for i, h in enumerate(headers):
        frags.append(mtext(600 + i * 90, 105, [h], size=14, bold=True, color=PURPLE_S))
        frags.append(mtext(520, 150 + i * 65, [h], size=14, bold=True, color=PURPLE_S))

    frags.append(line(565, 120, 565, 390, color="#2c3e50", sw=3))
    frags.append(line(565, 120, 580, 120, color="#2c3e50", sw=3))
    frags.append(line(565, 390, 580, 390, color="#2c3e50", sw=3))

    frags.append(line(945, 120, 945, 390, color="#2c3e50", sw=3))
    frags.append(line(945, 120, 930, 120, color="#2c3e50", sw=3))
    frags.append(line(945, 390, 930, 390, color="#2c3e50", sw=3))

    matrix_vals = [
        ["0", "1/3", "1/3", "1/3"],
        ["1/2", "0", "1/2", "0"],
        ["1/2", "1/2", "0", "0"],
        ["1", "0", "0", "0"]
    ]

    for r in range(4):
        for c in range(4):
            val = matrix_vals[r][c]
            bg = FIELD_F if val != "0" else "#f8f9f9"
            border = FIELD_S if val != "0" else "#e5e7e9"
            cx, cy = 600 + c * 90, 150 + r * 65
            frags.append(rect(cx - 30, cy - 18, 60, 36, rx=4, fill=bg, stroke=border, sw=1.5))
            frags.append(mtext(cx, cy + 4, [val], size=13, bold=True, color="#2c3e50"))

    frags.append(textbox(710, 440, "Властивість: Сума елементів у кожному рядку дорівнює 1 (∑_j P_ij = 1)", size=13, bold=True, fill=AMBER_F, stroke=AMBER_S, sw=1.5, pad=8)[0])

    render(os.path.join(IMG, "random-walk-transition-matrix.svg"), W, H, *frags)
    print("Згенеровано random-walk-transition-matrix.svg")


def fig_spectral_gap():
    """Фігура 2: Спектральний зазор γ = 1 - λ₂ та швидкість перемішування."""
    W, H = 1000, 480
    frags = []

    frags.append(textbox(500, 45, "Спектр власних значень матриці P та зазор γ = 1 - λ₂", size=16, bold=True, fill=PURPLE_F, stroke=PURPLE_S, sw=2, pad=10)[0])

    # Спектральна вісь
    frags.append(line(100, 150, 900, 150, color="#2c3e50", sw=3))

    ticks = [
        (100, "-1", POS_S),
        (300, "-λₙ", "#7f8c8d"),
        (500, "0", "#2c3e50"),
        (750, "λ₂", PURPLE_S),
        (900, "λ₁ = 1", FIELD_S)
    ]

    for x, lbl, col in ticks:
        frags.append(line(x, 135, x, 165, color=col, sw=2.5))
        frags.append(mtext(x, 115, [lbl], size=13, bold=True, color=col))

    frags.append(rect(750, 140, 150, 20, rx=3, fill=AMBER_F, stroke=AMBER_S, sw=2))
    frags.append(mtext(825, 185, ["Спектральний зазор γ = 1 - λ₂"], size=12, bold=True, color=AMBER_S))

    frags.append(textbox(500, 235, "Швидкість збіжності розподілу: ||π⁽ᵗ⁾ - π||₂ ≤ exp(-γ · t)", size=15, bold=True, fill=BLUE_F, stroke=BLUE_S, sw=2, pad=10)[0])

    frags.append(line(100, 430, 900, 430, color="#2c3e50", sw=2))
    frags.append(line(100, 430, 100, 270, color="#2c3e50", sw=2))

    frags.append(mtext(930, 435, ["t (кроки)"], size=12, bold=True))
    frags.append(mtext(100, 260, ["d_TV(π⁽ᵗ⁾, π)"], size=12, bold=True))

    curve_fast = [(100, 280), (200, 330), (300, 380), (400, 415), (500, 428), (600, 430)]
    for i in range(len(curve_fast) - 1):
        x1, y1 = curve_fast[i]
        x2, y2 = curve_fast[i+1]
        frags.append(line(x1, y1, x2, y2, color=FIELD_S, sw=3))

    frags.append(mtext(380, 370, ["Великий γ (Експандер): t_mix = O(log n)"], size=12, bold=True, color=FIELD_S))

    curve_slow = [(100, 280), (250, 300), (400, 330), (550, 365), (700, 400), (850, 422)]
    for i in range(len(curve_slow) - 1):
        x1, y1 = curve_slow[i]
        x2, y2 = curve_slow[i+1]
        frags.append(line(x1, y1, x2, y2, color=POS_S, sw=3, dash="4 4"))

    frags.append(mtext(650, 340, ["Малий γ (Вузька шийка): t_mix = O(n²)"], size=12, bold=True, color=POS_S))

    render(os.path.join(IMG, "spectral-gap-mixing.svg"), W, H, *frags)
    print("Згенеровано spectral-gap-mixing.svg")


def fig_cover_time():
    """Фігура 3: Порівняння часу покриття (Cover Time) для різних топологій графів."""
    W, H = 1000, 480
    frags = []

    frags.append(textbox(500, 45, "Залежність Cover Time від топології графа G = (V, E)", size=16, bold=True, fill=BLUE_F, stroke=BLUE_S, sw=2, pad=10)[0])

    topologies = [
        {
            "x": 40, "y": 95, "w": 280, "h": 350,
            "title": "1. Повний граф Kₙ",
            "bound": "C(G) = Θ(n log n)",
            "color": FIELD_S, "bg": FIELD_F,
            "desc": ["Висока зв'язність,", "рівномірні ступені", "d = n - 1"]
        },
        {
            "x": 360, "y": 95, "w": 280, "h": 350,
            "title": "2. Простий шлях Pₙ",
            "bound": "C(G) = Θ(n²)",
            "color": AMBER_S, "bg": AMBER_F,
            "desc": ["Одновимірне блукання,", "поворотний процес,", "вузький діаметр"]
        },
        {
            "x": 680, "y": 95, "w": 280, "h": 350,
            "title": "3. Граф Леденець Lₙ",
            "bound": "C(G) = Θ(n³)",
            "color": POS_S, "bg": POS_F,
            "desc": ["Кліка K_(n/2) + шлях P_(n/2).", "Найгірший випадок", "покриття у графах"]
        }
    ]

    for top in topologies:
        x, y, w, h = top["x"], top["y"], top["w"], top["h"]
        frags.append(rect(x, y, w, h, rx=8, fill="#ffffff", stroke="#bdc3c7", sw=1.5))
        frags.append(textbox(x + w / 2, y + 30, top["title"], size=15, bold=True, fill=top["bg"], stroke=top["color"], sw=2, pad=8)[0])

        frags.append(rect(x + 20, y + 75, w - 40, 50, rx=6, fill=top["bg"], stroke=top["color"], sw=1.5))
        frags.append(mtext(x + w / 2, y + 107, [top["bound"]], size=15, bold=True, color=top["color"]))

        cx, cy = x + w / 2, y + 200
        if top["title"].startswith("1"):
            pts = [(cx - 40, cy - 30), (cx + 40, cy - 30), (cx, cy + 40), (cx - 30, cy + 20), (cx + 30, cy + 20)]
            for i in range(len(pts)):
                for j in range(i + 1, len(pts)):
                    frags.append(line(pts[i][0], pts[i][1], pts[j][0], pts[j][1], color="#bdc3c7", sw=1))
            for px, py in pts:
                frags.append(circle(px, py, 8, fill=FIELD_F, stroke=FIELD_S, sw=2))
        elif top["title"].startswith("2"):
            pts = [(cx - 80, cy), (cx - 30, cy), (cx + 20, cy), (cx + 70, cy)]
            for i in range(len(pts) - 1):
                frags.append(line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], color="#2c3e50", sw=2))
            for px, py in pts:
                frags.append(circle(px, py, 8, fill=AMBER_F, stroke=AMBER_S, sw=2))
        else:
            frags.append(circle(cx - 30, cy, 35, fill=POS_F, stroke=POS_S, sw=1.5))
            frags.append(line(cx - 30, cy, cx + 70, cy, color="#2c3e50", sw=2))
            frags.append(circle(cx + 20, cy, 8, fill=POS_F, stroke=POS_S, sw=2))
            frags.append(circle(cx + 70, cy, 8, fill=POS_F, stroke=POS_S, sw=2))

        for idx, line_txt in enumerate(top["desc"]):
            frags.append(mtext(cx, y + 270 + idx * 22, [line_txt], size=12, color="#34495e"))

    render(os.path.join(IMG, "cover-time-comparison.svg"), W, H, *frags)
    print("Згенеровано cover-time-comparison.svg")


def fig_electric_duality():
    """Фігура 4: Дуальність випадкових блукань та електричних кіл опорів."""
    W, H = 1000, 480
    frags = []

    frags.append(textbox(500, 45, "Дуальність: Випадкові блукання ↔ Електричні кола (Теорема Тетта — Дойч-Снелла)", size=15, bold=True, fill=PURPLE_F, stroke=PURPLE_S, sw=2, pad=10)[0])

    # Ліва частина: Стохастичний світ
    frags.append(rect(40, 90, 430, 360, rx=8, fill="#ffffff", stroke=BLUE_S, sw=2))
    frags.append(textbox(255, 115, "Стохастичний світ (Random Walk)", size=14, bold=True, fill=BLUE_F, stroke=BLUE_S, sw=1.5, pad=8)[0])

    walk_props = [
        ("Початкова вершина u", "Джерело блукача"),
        ("Цільова вершина v", "Стік / Поглинач"),
        ("Ймовірність P_uv = 1/d(u)", "Провідність w_uv / c(u)"),
        ("Commute Time C(u, v)", "Очікуваний час виходу і повернення"),
        ("Формула Тетта", "C(u, v) = 2 |E| · R_eff(u, v)")
    ]

    for idx, (p1, p2) in enumerate(walk_props):
        y_pos = 160 + idx * 52
        frags.append(rect(60, y_pos, 390, 42, rx=4, fill=BLUE_F, stroke="#a9cce3", sw=1))
        frags.append(mtext(75, y_pos + 26, [p1], size=12, bold=True, color=BLUE_S, anchor="start"))
        frags.append(mtext(435, y_pos + 26, [p2], size=11, color="#2c3e50", anchor="end"))

    # Стрілка еквівалентності по центру
    frags.append(line(480, 270, 520, 270, color=PURPLE_S, sw=4))
    frags.append(mtext(500, 245, ["1 : 1"], size=14, bold=True, color=PURPLE_S))

    # Права частина: Електричне коло
    frags.append(rect(530, 90, 430, 360, rx=8, fill="#ffffff", stroke=FIELD_S, sw=2))
    frags.append(textbox(745, 115, "Фізичний світ (Електричне коло)", size=14, bold=True, fill=FIELD_F, stroke=FIELD_S, sw=1.5, pad=8)[0])

    elec_props = [
        ("Вхідний струм I_in = 1 A", "Подача струму в u"),
        ("Вихідний струм I_out = 1 A", "Відбір струму з v"),
        ("Опір ребра R_uv = 1 Ом", "Закон Ома I = ΔV / R"),
        ("Потенціал V(x)", "Гармонічна функція h(x)"),
        ("Ефективний опір R_eff", "V(u) - V(v) при I = 1 A")
    ]

    for idx, (p1, p2) in enumerate(elec_props):
        y_pos = 160 + idx * 52
        frags.append(rect(550, y_pos, 390, 42, rx=4, fill=FIELD_F, stroke="#a9dfbf", sw=1))
        frags.append(mtext(565, y_pos + 26, [p1], size=12, bold=True, color=FIELD_S, anchor="start"))
        frags.append(mtext(925, y_pos + 26, [p2], size=11, color="#2c3e50", anchor="end"))

    render(os.path.join(IMG, "electric-network-duality.svg"), W, H, *frags)
    print("Згенеровано electric-network-duality.svg")


if __name__ == "__main__":
    fig_transition_matrix()
    fig_spectral_gap()
    fig_cover_time()
    fig_electric_duality()
