# -*- coding: utf-8 -*-
"""Генерація SVG-ілюстрацій для теми GJK (Алгоритм Гілберта–Джонсона–Кірті)."""

import sys
import os

# Підключення svgkit із scripts/ у корені репо (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)


def fig1_minkowski():
    """Фігура 1: Перетин тіл та положення початку координат відносно різниці Мінковського."""
    w, h = 860, 360
    frags = []

    # Ліва половина: Розділені тіла (A і B не перетинаються -> O поза A - B)
    frags.append(rect(15, 15, 405, 330, fill="#fbfcfd", stroke="#d0d7de", sw=1, rx=8))
    frags.append(text(217, 42, "Тіла не перетинаються (A ∩ B = ∅)", size=15, color=INK, bold=True))

    # Тіло A (зеленуватий опуклий чотирикутник)
    poly_a = '<polygon points="50,110 110,80 140,140 70,170" fill="#e8f5e9" stroke="#27ae60" stroke-width="2"/>'
    frags.append(poly_a)
    frags.append(text(92, 125, "A", size=15, color="#1b5e20", bold=True))

    # Тіло B (синюватий опуклий трикутник)
    poly_b = '<polygon points="150,110 200,90 190,165" fill="#e3f2fd" stroke="#2457d6" stroke-width="2"/>'
    frags.append(poly_b)
    frags.append(text(180, 125, "B", size=15, color="#0d47a1", bold=True))

    # Стрілка відображення в простір Мінковського
    frags.append(arrow(215, 130, 245, 130, color=MUTED, sw=1.5))
    frags.append(text(230, 118, "A ⊖ B", size=12, color=MUTED, italic=True))

    # Різниця Мінковського A - B (не містить початок координат)
    poly_diff1 = '<polygon points="275,190 335,140 385,160 395,230 345,270 285,250" fill="#fff3e0" stroke="#e67e22" stroke-width="2"/>'
    frags.append(poly_diff1)
    frags.append(text(340, 205, "C = A ⊖ B", size=13, color="#d35400", bold=True))

    # Початок координат O (0,0) поза тілом C
    frags.append(line(265, 80, 265, 150, color="#95a5a6", sw=1, dash="3,3"))
    frags.append(line(230, 115, 300, 115, color="#95a5a6", sw=1, dash="3,3"))
    frags.append(circle(265, 115, 4.5, fill=POS, stroke=POS, sw=1))
    frags.append(text(290, 108, "O (0,0)", size=12, color=POS, bold=True))

    # Пояснювальний підпис зліва
    frags.append(text(217, 318, "Початок координат О лежить ПОЗА різницею A ⊖ B", size=13, color=MUTED, bold=False))


    # Права половина: Тіла перетинаються (A ∩ B ≠ ∅ -> O всередині A - B)
    frags.append(rect(440, 15, 405, 330, fill="#fbfcfd", stroke="#d0d7de", sw=1, rx=8))
    frags.append(text(642, 42, "Тіла перетинаються (A ∩ B ≠ ∅)", size=15, color=INK, bold=True))

    # Тіло A (перекривається з B)
    poly_a2 = '<polygon points="475,120 535,90 565,150 495,180" fill="#e8f5e9" stroke="#27ae60" stroke-width="2" fill-opacity="0.8"/>'
    frags.append(poly_a2)
    frags.append(text(505, 130, "A", size=15, color="#1b5e20", bold=True))

    # Тіло B
    poly_b2 = '<polygon points="530,120 580,100 570,175" fill="#e3f2fd" stroke="#2457d6" stroke-width="2" fill-opacity="0.8"/>'
    frags.append(poly_b2)
    frags.append(text(560, 140, "B", size=15, color="#0d47a1", bold=True))

    # Стрілка відображення
    frags.append(arrow(595, 130, 625, 130, color=MUTED, sw=1.5))
    frags.append(text(610, 118, "A ⊖ B", size=12, color=MUTED, italic=True))

    # Різниця Мінковського A - B (містить початок координат)
    poly_diff2 = '<polygon points="655,160 715,110 765,130 775,200 725,240 665,220" fill="#fff3e0" stroke="#e67e22" stroke-width="2"/>'
    frags.append(poly_diff2)
    frags.append(text(725, 155, "C = A ⊖ B", size=13, color="#d35400", bold=True))

    # Початок координат O (0,0) всередині тіла C
    frags.append(line(710, 145, 710, 215, color="#95a5a6", sw=1, dash="3,3"))
    frags.append(line(675, 180, 745, 180, color="#95a5a6", sw=1, dash="3,3"))
    frags.append(circle(710, 180, 4.5, fill=POS, stroke=POS, sw=1))
    frags.append(text(735, 192, "O (0,0)", size=12, color=POS, bold=True))

    # Пояснювальний підпис справа
    frags.append(text(642, 318, "Початок координат О лежить ВСЕРЕДИНІ різниці A ⊖ B", size=13, color=POS, bold=True))

    render(os.path.join(os.path.dirname(__file__), "img", "minkowski-intersection.svg"), w, h, *frags)


def fig2_support_function():
    """Фігура 2: Опорне відображення для окремих тіл та побудова точки різниці Мінковського."""
    w, h = 820, 320
    frags = []

    frags.append(rect(15, 15, 790, 290, fill="#fbfcfd", stroke="#d0d7de", sw=1, rx=8))

    # 1. Тіло A та опорна точка у напрямку d
    frags.append(text(140, 45, "Опорна точка s_A(d)", size=14, color=INK, bold=True))
    poly_a = '<polygon points="60,140 100,80 170,90 200,160 130,200" fill="#e8f5e9" stroke="#27ae60" stroke-width="2"/>'
    frags.append(poly_a)
    frags.append(text(125, 145, "A", size=15, color="#1b5e20", bold=True))

    # Напрямок d для A
    frags.append(arrow(170, 90, 225, 60, color=POS, sw=2))
    frags.append(text(235, 55, "d", size=14, color=POS, bold=True))
    frags.append(circle(170, 90, 5, fill=POS, stroke=POS, sw=1))
    frags.append(text(175, 110, "s_A(d)", size=12, color=POS, bold=True))

    # Дотична опорна пряма
    frags.append(line(135, 30, 205, 150, color=MUTED, sw=1.2, dash="4,4"))


    # 2. Тіло B та опорна точка у напрямку -d
    frags.append(text(410, 45, "Опорна точка s_B(−d)", size=14, color=INK, bold=True))
    poly_b = '<polygon points="340,150 380,95 450,110 470,180 400,210" fill="#e3f2fd" stroke="#2457d6" stroke-width="2"/>'
    frags.append(poly_b)
    frags.append(text(410, 155, "B", size=15, color="#0d47a1", bold=True))

    # Напрямок -d для B
    frags.append(arrow(340, 150, 285, 180, color=NEG, sw=2))
    frags.append(text(275, 195, "−d", size=14, color=NEG, bold=True))
    frags.append(circle(340, 150, 5, fill=NEG, stroke=NEG, sw=1))
    frags.append(text(355, 140, "s_B(−d)", size=12, color=NEG, bold=True))

    # Дотична опорна пряма
    frags.append(line(305, 90, 375, 210, color=MUTED, sw=1.2, dash="4,4"))


    # 3. Результуюча опорна точка C = s_A(d) - s_B(-d)
    frags.append(text(670, 45, "Опорна точка s_{A⊖B}(d)", size=14, color=INK, bold=True))
    poly_c = '<polygon points="580,180 630,110 710,95 760,170 710,240 610,230" fill="#fff3e0" stroke="#e67e22" stroke-width="2"/>'
    frags.append(poly_c)
    frags.append(text(660, 175, "A ⊖ B", size=14, color="#d35400", bold=True))

    # Напрямок d для C
    frags.append(arrow(710, 95, 765, 65, color=POS, sw=2))
    frags.append(text(775, 60, "d", size=14, color=POS, bold=True))
    frags.append(circle(710, 95, 5, fill="#d35400", stroke="#d35400", sw=1))
    frags.append(text(700, 115, "P = s_A(d) − s_B(−d)", size=12, color="#d35400", bold=True))

    # Підсумок лінійності
    frags.append(text(410, 275, "Властивість екстремуму:  s_{A⊖B}(d) = s_A(d) − s_B(−d)", size=14, color=INK, bold=True))

    render(os.path.join(os.path.dirname(__file__), "img", "support-mapping.svg"), w, h, *frags)


def fig3_simplex_evolution():
    """Фігура 3: Еволюція симплекса в алгоритмі GJK (Крок 1 -> Крок 2 -> Крок 3)."""
    w, h = 880, 310
    frags = []

    # Крок 1: Точка A (1-симплекс), напрямок d = -A до O
    frags.append(rect(15, 15, 270, 280, fill="#fbfcfd", stroke="#d0d7de", sw=1, rx=8))
    frags.append(text(150, 40, "Крок 1: 0-симплекс (Точка)", size=14, color=INK, bold=True))

    # Тіло C = A - B
    poly_c1 = '<polygon points="50,160 110,90 200,80 250,170 200,240 80,230" fill="#fff8e1" stroke="#ffb300" stroke-width="1.5" stroke-dasharray="3,3"/>'
    frags.append(poly_c1)

    # Початок O
    frags.append(circle(130, 160, 4.5, fill=POS, stroke=POS, sw=1))
    frags.append(text(145, 155, "O", size=13, color=POS, bold=True))

    # Перша точка A
    frags.append(circle(200, 80, 5, fill=NEG, stroke=NEG, sw=1))
    frags.append(text(205, 70, "A", size=13, color=NEG, bold=True))

    # Напрямок до O
    frags.append(arrow(200, 80, 135, 155, color=POS, sw=1.8))
    frags.append(text(185, 135, "d₁ = O − A", size=12, color=POS, bold=True))

    frags.append(text(150, 270, "Пошук нової точки вздовж d₁", size=12, color=MUTED))


    # Крок 2: Відрізок AB (1-симплекс), напрямок d перпендикулярний до AB у бік O
    frags.append(rect(305, 15, 270, 280, fill="#fbfcfd", stroke="#d0d7de", sw=1, rx=8))
    frags.append(text(440, 40, "Крок 2: 1-симплекс (Відрізок)", size=14, color=INK, bold=True))

    # Тіло C = A - B
    poly_c2 = '<polygon points="340,160 400,90 490,80 540,170 490,240 370,230" fill="#fff8e1" stroke="#ffb300" stroke-width="1.5" stroke-dasharray="3,3"/>'
    frags.append(poly_c2)

    # Початок O
    frags.append(circle(420, 160, 4.5, fill=POS, stroke=POS, sw=1))
    frags.append(text(435, 155, "O", size=13, color=POS, bold=True))

    # Точки B і нова A
    frags.append(circle(490, 80, 4, fill=MUTED, stroke=MUTED, sw=1))
    frags.append(text(500, 75, "B", size=12, color=MUTED))
    frags.append(circle(370, 230, 5, fill=NEG, stroke=NEG, sw=1))
    frags.append(text(355, 245, "A", size=13, color=NEG, bold=True))

    # Відрізок AB
    frags.append(line(490, 80, 370, 230, color=NEG, sw=2.5))

    # Нормаль до відрізка в бік O
    frags.append(arrow(430, 155, 410, 140, color=POS, sw=2))
    frags.append(text(475, 195, "d₂ ⊥ AB", size=12, color=POS, bold=True))

    frags.append(text(440, 270, "Пошук третьої точки вздовж d₂", size=12, color=MUTED))


    # Крок 3: Трикутник ABC (2-симплекс), що містить початок O -> Перетин!
    frags.append(rect(595, 15, 270, 280, fill="#fbfcfd", stroke="#d0d7de", sw=1, rx=8))
    frags.append(text(730, 40, "Крок 3: 2-симплекс (Трикутник)", size=14, color=INK, bold=True))

    # Тіло C = A - B
    poly_c3 = '<polygon points="630,160 690,90 780,80 830,170 780,240 660,230" fill="#fff8e1" stroke="#ffb300" stroke-width="1.5" stroke-dasharray="3,3"/>'
    frags.append(poly_c3)

    # Точки трикутника: C, B, нова A
    frags.append(circle(780, 80, 4, fill=MUTED, stroke=MUTED, sw=1))
    frags.append(text(790, 75, "C", size=12, color=MUTED))
    frags.append(circle(660, 230, 4, fill=MUTED, stroke=MUTED, sw=1))
    frags.append(text(645, 245, "B", size=12, color=MUTED))
    frags.append(circle(630, 140, 5, fill=NEG, stroke=NEG, sw=1))
    frags.append(text(615, 135, "A", size=13, color=NEG, bold=True))

    # Трикутник ABC
    poly_tri = '<polygon points="780,80 660,230 630,140" fill="#e8f5e9" stroke="#27ae60" stroke-width="2.5" fill-opacity="0.6"/>'
    frags.append(poly_tri)

    # Початок O всередині трикутника
    frags.append(circle(710, 160, 5, fill=POS, stroke=POS, sw=1))
    frags.append(text(730, 165, "O ∈ ABC", size=13, color=POS, bold=True))

    frags.append(text(730, 270, "O всередині -> КОЛІЗІЯ", size=13, color=FIELD, bold=True))

    render(os.path.join(os.path.dirname(__file__), "img", "simplex-evolution.svg"), w, h, *frags)


def fig4_voronoi_regions():
    """Фігура 4: Області Вороного для трикутного симплекса ABC (вибір найближчого симплекса)."""
    w, h = 820, 360
    frags = []

    frags.append(rect(15, 15, 790, 330, fill="#fbfcfd", stroke="#d0d7de", sw=1, rx=8))
    frags.append(text(410, 42, "Області Вороного для трикутника ABC (точка A додана останньою)", size=15, color=INK, bold=True))

    # Вершини трикутника
    ax, ay = 340, 110
    bx, by = 500, 250
    cx, cy = 240, 250

    # Заливка самого трикутника (Область ABC)
    poly_tri = '<polygon points="340,110 500,250 240,250" fill="#e8f5e9" stroke="#27ae60" stroke-width="2.5"/>'
    frags.append(poly_tri)
    frags.append(text(360, 210, "Область ABC", size=13, color="#1b5e20", bold=True))
    frags.append(text(360, 226, "(О всередині)", size=11, color="#2e7d32"))

    # Вершини
    frags.append(circle(ax, ay, 5.5, fill=POS, stroke=POS, sw=1))
    frags.append(text(ax, ay - 12, "A (нова)", size=13, color=POS, bold=True))

    frags.append(circle(bx, by, 5, fill=INK, stroke=INK, sw=1))
    frags.append(text(bx + 15, by + 5, "B", size=13, color=INK, bold=True))

    frags.append(circle(cx, cy, 5, fill=INK, stroke=INK, sw=1))
    frags.append(text(cx - 15, cy + 5, "C", size=13, color=INK, bold=True))

    # Розділові лінії областей Вороного
    # Зовнішня нормаль до AB:
    frags.append(line(420, 180, 560, 80, color=NEG, sw=1.5, dash="4,4"))
    frags.append(arrow(420, 180, 480, 130, color=NEG, sw=1.8))
    frags.append(text(545, 140, "Область ребра AB", size=13, color=NEG, bold=True))
    frags.append(text(545, 156, "Лишаємо {A, B}, d ⊥ AB", size=11, color=NEG))

    # Зовнішня нормаль до AC:
    frags.append(line(290, 180, 150, 80, color=NEG, sw=1.5, dash="4,4"))
    frags.append(arrow(290, 180, 230, 130, color=NEG, sw=1.8))
    frags.append(text(145, 140, "Область ребра AC", size=13, color=NEG, bold=True))
    frags.append(text(145, 156, "Лишаємо {A, C}, d ⊥ AC", size=11, color=NEG))

    # Область вершини A (попереду A):
    frags.append(line(ax, ay, ax + 70, ay - 60, color=MUTED, sw=1.2, dash="3,3"))
    frags.append(line(ax, ay, ax - 70, ay - 60, color=MUTED, sw=1.2, dash="3,3"))
    frags.append(arrow(ax, ay, ax, ay - 55, color=POS, sw=1.8))
    frags.append(text(ax, ay - 65, "Область вершини A (рідкісна: лишаємо {A}, d = O − A)", size=12, color=POS, bold=True))

    # Пояснення внизу
    frags.append(text(410, 310, "Оскільки точка A перетнула O у напрямку пошуку, позаду ребра BC початок координат лежати не може", size=13, color=MUTED))

    render(os.path.join(os.path.dirname(__file__), "img", "voronoi-regions.svg"), w, h, *frags)


if __name__ == "__main__":
    fig1_minkowski()
    fig2_support_function()
    fig3_simplex_evolution()
    fig4_voronoi_regions()
    print("All figures successfully generated in ./img/")
