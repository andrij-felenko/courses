# -*- coding: utf-8 -*-
"""Фігури до теми «Похибки вимірювань».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: прилад спотворює коло (вольтметр занижує, амперметр зменшує струм) ──
def fig_loading():
    W, H = 820, 330
    f = [text(W / 2, 30, "Прилад завжди трохи спотворює те, що міряє", size=17, bold=True),
         text(W / 2, 52, "вольтметр відбирає крихту струму; амперметр додає крихту опору",
              size=11, color=MUTED, italic=True),
         line(W / 2, 78, W / 2, 270, color="#dcdcdc", sw=1.4, dash="4,5")]

    # ── ліворуч: вольтметр паралельно навантаженню ──
    f.append(text(210, 100, "Вольтметр трохи ЗАНИЖУЄ", size=12.5, color=NEG, bold=True))
    # джерело (батарея)
    f.append(line(90, 135, 90, 245, color=INK, sw=2.2))
    f.append(line(74, 182, 106, 182, color=INK, sw=3))
    f.append(line(81, 198, 99, 198, color=INK, sw=5))
    # верхній і нижній дроти до резистора
    f.append(line(90, 135, 228, 135, color="#cf8b5e", sw=2.2))
    f.append(rect(216, 158, 24, 62, fill=BG, stroke=INK, sw=2, rx=3))
    f.append(text(248, 194, "R", size=12, color=INK, bold=True, italic=True, anchor="start"))
    f.append(line(228, 135, 228, 158, color="#cf8b5e", sw=2.2))
    f.append(line(228, 220, 228, 245, color="#cf8b5e", sw=2.2))
    f.append(line(90, 245, 228, 245, color="#cf8b5e", sw=2.2))
    # вольтметр паралельно
    f.append(circle(330, 190, 20, fill=BG, stroke=NEG, sw=2.4))
    f.append(text(330, 196, "V", size=19, color=NEG, bold=True))
    f.append(line(312, 180, 234, 144, color=NEG, sw=2))
    f.append(line(312, 200, 234, 236, color=NEG, sw=2))
    f.append(text(210, 285, "відбирає краплю струму → читає трохи менше",
                  size=10, color=MUTED, italic=True))

    # ── праворуч: амперметр у розриві кола ──
    f.append(text(620, 100, "Амперметр трохи ЗМЕНШУЄ струм", size=12, color=FIELD, bold=True))
    f.append(line(490, 135, 490, 245, color=INK, sw=2.2))
    f.append(line(474, 182, 506, 182, color=INK, sw=3))
    f.append(line(481, 198, 499, 198, color=INK, sw=5))
    f.append(line(490, 135, 560, 135, color="#cf8b5e", sw=2.2))
    # амперметр у розриві верхнього дроту
    f.append(circle(595, 135, 18, fill=BG, stroke=FIELD, sw=2.4))
    f.append(text(595, 141, "A", size=17, color=FIELD, bold=True))
    f.append(line(613, 135, 700, 135, color="#cf8b5e", sw=2.2))
    f.append(rect(688, 158, 24, 62, fill=BG, stroke=INK, sw=2, rx=3))
    f.append(text(682, 194, "R", size=12, color=INK, bold=True, italic=True, anchor="end"))
    f.append(line(700, 135, 700, 158, color="#cf8b5e", sw=2.2))
    f.append(line(700, 220, 700, 245, color="#cf8b5e", sw=2.2))
    f.append(line(490, 245, 700, 245, color="#cf8b5e", sw=2.2))
    f.append(text(620, 285, "додає краплю опору → струм трохи менший",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(IMG, "loading.svg"), W, H, *f)


# ── Фігура 2: точність / правильність / влучність + роздільність (мішені) ──
def _target(cx, cy, dots, dot_color):
    f = [circle(cx, cy, 56, fill="none", stroke="#bbbbbb", sw=1.4),
         circle(cx, cy, 35, fill="none", stroke="#bbbbbb", sw=1.2),
         circle(cx, cy, 15, fill="none", stroke=POS, sw=1.6)]
    for (dx, dy) in dots:
        f.append(circle(cx + dx, cy + dy, 3.3, fill=dot_color, stroke=dot_color, sw=1))
    return f


def fig_accuracy_precision():
    W, H = 860, 330
    f = [text(W / 2, 30, "Точність = правильність + влучність; роздільність — окреме", size=17, bold=True),
         text(W / 2, 52, "влучний ≠ правильний; а роздільність — лише дрібність поділки, не правдивість",
              size=11, color=MUTED, italic=True)]

    cy = 150
    # 1) точно й влучно: купно й у центрі
    f += _target(150, cy, [(-4, 3), (5, -2), (2, 6), (-2, -4)], FIELD)
    f.append(text(150, 228, "Точно", size=12, color=FIELD, bold=True))
    f.append(text(150, 246, "купно і в ціль", size=9.5, color=MUTED))
    # 2) влучно, та не правильно: купно, але зсунуто (зсув = систематична)
    f += _target(370, cy, [(28, -20), (33, -16), (30, -24), (26, -18)], "#e08030")
    f.append(text(370, 228, "Влучно, та зсув", size=12, color="#e08030", bold=True))
    f.append(text(370, 246, "купно, але збоку", size=9.5, color=MUTED))
    # 3) розкидано: ні те, ні те (випадкова велика)
    f += _target(590, cy, [(-30, 10), (25, -28), (5, 30), (-20, -25), (33, 12)], NEG)
    f.append(text(590, 228, "Розкидано", size=12, color=NEG, bold=True))
    f.append(text(590, 246, "ні купно, ні в ціль", size=9.5, color=MUTED))

    # роздільність — окрема панель
    f.append(rect(712, 92, 130, 152, fill=FILL, stroke=INK, sw=1.5, rx=10))
    f.append(text(777, 116, "Роздільність", size=11.5, color=INK, bold=True))
    f.append(text(777, 146, "5.0 В", size=13, color=MUTED))
    f.append(text(777, 172, "5.000 В", size=15, color=INK, bold=True))
    f.append(text(777, 198, "більше цифр —", size=9, color=MUTED))
    f.append(text(777, 212, "дрібніша поділка,", size=9, color=MUTED))
    f.append(text(777, 228, "та НЕ правда", size=9.5, color=POS, bold=True))

    render(os.path.join(IMG, "accuracy-precision.svg"), W, H, *f)


# ── Фігура 3: систематична (зсув) vs випадкова (розкид) похибка ──
def fig_error_types():
    W, H = 820, 320
    f = [text(W / 2, 30, "Дві природи похибок", size=18, bold=True),
         text(W / 2, 52, "систематична — сталий зсув (лікує калібрування); випадкова — розкид (лікує усереднення)",
              size=10.5, color=MUTED, italic=True)]

    # лінія істини в обох панелях
    # ── ліворуч: систематична — стовпчик точок, зсунутий від істини ──
    f.append(text(215, 96, "Систематична", size=12.5, color="#e08030", bold=True))
    f.append(line(215, 116, 215, 250, color=FIELD, sw=1.6, dash="4,3"))
    f.append(text(215, 268, "істина", size=9.5, color=FIELD, bold=True))
    sx = [300, 308, 316, 300, 308, 316, 300]
    for i, x in enumerate(sx):
        f.append(circle(x, 140 + i * 14, 3.4, fill="#e08330", stroke="#e08330", sw=1))
    f.append(arrow(252, 200, 296, 200, color="#e08330", sw=1.8))
    f.append(text(320, 286, "усі зсунуті в один бік → калібрування", size=9.5, color=MUTED))

    # ── праворуч: випадкова — хмара навколо істини ──
    f.append(text(615, 96, "Випадкова", size=12.5, color=NEG, bold=True))
    f.append(line(615, 116, 615, 250, color=FIELD, sw=1.6, dash="4,3"))
    f.append(text(615, 268, "істина", size=9.5, color=FIELD, bold=True))
    cloud = [(-22, 8), (18, -18), (-8, 22), (12, 6), (-16, -20),
             (24, 16), (-2, -10), (8, 26)]
    for (dx, dy) in cloud:
        f.append(circle(615 + dx, 183 + dy, 3.4, fill=NEG, stroke=NEG, sw=1))
    f.append(text(615, 286, "розкид навколо істини → усереднення", size=9.5, color=MUTED))

    render(os.path.join(IMG, "error-types.svg"), W, H, *f)


if __name__ == "__main__":
    fig_loading()
    fig_accuracy_precision()
    fig_error_types()
    print("ok: loading.svg, accuracy-precision.svg, error-types.svg ->", IMG)
