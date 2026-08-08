# -*- coding: utf-8 -*-
"""Фігури до теми «Міжмолекулярні сили»
(book/chemistry/supramolecular-chemistry/intermolecular-forces)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def bond(x1, y1, r1, x2, y2, r2, sw=2.0, color=LINE):
    """Лінія зв'язку, що обривається на межах кружків — не лізе на літери."""
    d = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / d, (y2 - y1) / d
    return line(x1 + ux * (r1 + 1.5), y1 + uy * (r1 + 1.5),
                x2 - ux * (r2 + 1.5), y2 - uy * (r2 + 1.5), color=color, sw=sw)


def atom(cx, cy, label, r=26, color=INK, size=19):
    return (circle(cx, cy, r, fill="#ffffff", stroke=color, sw=2) +
            text(cx, cy + size * 0.35, label, size=size, bold=True, color=color))


# ── Фігура 1: три способи зчеплення ────────────────────────────────────────
def fig_three_ways():
    W, H = 980, 760
    PANEL_X, PANEL_W, PANEL_H, PITCH = 30, 920, 195, 215
    TX, TW = 590, 350

    frags = [text(W / 2, 34, "Чим молекули чіпляються одна за одну",
                  size=19, bold=True)]

    def panel(i, title, explain):
        y0 = 60 + i * PITCH
        out = [rect(PANEL_X, y0, PANEL_W, PANEL_H, fill="#ffffff", sw=1.2),
               text(PANEL_X + 20, y0 + 27, title, size=16, bold=True, anchor="start"),
               fitbox(TX, y0 + 52, TW, 100, explain, size=14, fill=FILL)]
        return y0, out

    # ── 1. Полярні молекули ────────────────────────────────────────────────
    y0, out = panel(0, "1. Полярні молекули",
                    "Один бік молекули злегка мінусовий,\n"
                    "другий злегка плюсовий. Сусіди\n"
                    "повертаються протилежними боками\n"
                    "й злипаються.")
    yc = y0 + 120
    for x_left in (70, 310):
        out.append(rect(x_left, yc - 30, 170, 60, fill="#ffffff", sw=1.8, rx=30))
        out.append(minus(x_left + 35, yc, 16))
        out.append(plus(x_left + 135, yc, 16))
    out.append(line(245, yc, 305, yc, color=FIELD, sw=2.2, dash="6 5"))
    out.append(text(275, yc - 44, "притягання", size=13, color=FIELD))
    out.append(text(155, yc + 50, "молекула води", size=12, color=MUTED))
    out.append(text(395, yc + 50, "молекула води", size=12, color=MUTED))
    frags += out

    # ── 2. Водневий зв'язок ────────────────────────────────────────────────
    y0, out = panel(1, "2. Водневий зв'язок",
                    "Гідроген біля Оксигену лишається\n"
                    "майже голим протоном — і впивається\n"
                    "в Оксиген сусіда набагато міцніше\n"
                    "за звичайне злипання.")
    yc = y0 + 120
    # ліва молекула: Оксиген праворуч, Гідрогени ліворуч
    out.append(bond(200, yc, 26, 157, yc - 38, 15))
    out.append(bond(200, yc, 26, 157, yc + 38, 15))
    out.append(atom(200, yc, "O", r=26, color=NEG))
    out.append(atom(157, yc - 38, "H", r=15, color=MUTED, size=13))
    out.append(atom(157, yc + 38, "H", r=15, color=MUTED, size=13))
    # права молекула: один Гідроген дивиться вліво, на чужий Оксиген
    out.append(bond(400, yc, 26, 348, yc, 15))
    out.append(bond(400, yc, 26, 441, yc - 40, 15))
    out.append(atom(400, yc, "O", r=26, color=NEG))
    out.append(atom(348, yc, "H", r=15, color=POS, size=13))
    out.append(atom(441, yc - 40, "H", r=15, color=MUTED, size=13))
    out.append(line(228, yc, 330, yc, color=FIELD, sw=2.6, dash="7 5"))
    out.append(text(272, yc - 26, "водневий зв'язок", size=13, color=FIELD))
    frags += out

    # ── 3. Дисперсійне притягання ──────────────────────────────────────────
    y0, out = panel(2, "3. Дисперсійне притягання",
                    "Навіть у симетричної частинки\n"
                    "електрони на мить збиваються набік.\n"
                    "Сусід одразу підлаштовується —\n"
                    "і вони притягуються.")
    yc = y0 + 118
    for cx in (150, 350):
        out.append(circle(cx, yc, 45, fill="#ffffff", stroke=INK, sw=1.8))
        out.append(circle(cx - 22, yc, 30, fill="#dde6fb", stroke="#dde6fb", sw=0))
        out.append(minus(cx - 34, yc, 13))
        out.append(plus(cx + 30, yc, 13))
    out.append(line(197, yc, 296, yc, color=FIELD, sw=2.2, dash="6 5"))
    out.append(text(246, yc - 26, "притягання", size=13, color=FIELD))
    out.append(text(250, yc + 68, "хмара електронів збилася вліво", size=12, color=MUTED))
    frags += out

    render(os.path.join(IMG, "three-ways.svg"), W, H, *frags,
           title="Три способи зчеплення молекул")


# ── Фігура 2: температура кипіння проти ваги ───────────────────────────────
def fig_boiling_scale():
    W, H = 960, 400
    AX_Y = 250
    T0, T1, X0, X1 = -200.0, 120.0, 90.0, 870.0
    k = (X1 - X0) / (T1 - T0)

    def X(t):
        return X0 + (t - T0) * k

    frags = [text(W / 2, 34, "Вага майже однакова — а кипіння розходиться на 260 градусів",
                  size=19, bold=True)]

    # вісь
    frags.append(line(X0, AX_Y, X1, AX_Y, color=INK, sw=2))
    for t in (-200, -150, -100, -50, 0, 50, 100):
        frags.append(line(X(t), AX_Y - 6, X(t), AX_Y + 6, color=INK, sw=1.6))
        frags.append(text(X(t), AX_Y + 28, "%+d" % t if t else "0", size=13, color=MUTED))
    frags.append(text(X1 - 10, AX_Y - 18, "°C", size=14, color=MUTED, anchor="end"))

    items = [(-162, "метан CH₄\nмаса 16\n−162 °C\nтримає майже ніщо", MUTED),
             (-60, "сірководень H₂S\nмаса 34\n−60 °C\nслабке злипання", INK),
             (100, "вода H₂O\nмаса 18\n+100 °C\nводневий зв'язок", POS)]
    for t, label, color in items:
        body, w, h = textbox(X(t), 140, label, size=13, color=color,
                             stroke=color, fill="#ffffff", pad=11)
        frags.append(line(X(t), 140 + h / 2, X(t), AX_Y - 8, color=color, sw=1.8, dash="5 4"))
        frags.append(body)
        frags.append(circle(X(t), AX_Y, 6, fill=color, stroke=color, sw=1))

    frags.append(text(W / 2, 340,
                      "Вирішує не вага молекули, а те, наскільки міцно молекули "
                      "чіпляються одна за одну",
                      size=15, color=INK))

    render(os.path.join(IMG, "boiling-scale.svg"), W, H, *frags,
           title="Температура кипіння проти ваги молекули")


if __name__ == "__main__":
    fig_three_ways()
    fig_boiling_scale()
    print("готово:", IMG)
