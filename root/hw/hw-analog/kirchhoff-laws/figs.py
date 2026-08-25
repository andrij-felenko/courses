# -*- coding: utf-8 -*-
"""Фігури до статті «Закони Кірхгофа» (book/electronics/analog/kirchhoff-laws).
Фігури статті:
  conserve.svg — інтуїція збереження: вузол не накопичує заряд; контур повертає рівно стільки, скільки забрав
  kcl.svg      — закон струмів: сума втікань = сума витікань у вузлі (з числами)
  kvl.svg      — закон напруг: сума підйомів = сума спадів уздовж замкненого контуру (з числами)
  solve.svg    — два закони + Ом разом дають систему, що однозначно розв'язує коло
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def dot(cx, cy, r=4, col=INK):
    return circle(cx, cy, r, fill=col, stroke=col)


def gnd(cx, y):
    return "".join([line(cx, y, cx, y + 7, color=INK, sw=1.8),
                    line(cx - 12, y + 7, cx + 12, y + 7, color=INK, sw=2.4),
                    line(cx - 7, y + 12, cx + 7, y + 12, color=INK, sw=2.0),
                    line(cx - 3, y + 17, cx + 3, y + 17, color=INK, sw=1.8)])


def battery(cx, cy, label=None, vert=True):
    """Гальванічний елемент: довга риска (+) і коротка (−). Вертикальний."""
    out = []
    if vert:
        out.append(line(cx - 11, cy - 4, cx + 11, cy - 4, color=INK, sw=2.6))   # довга (+)
        out.append(line(cx - 6, cy + 4, cx + 6, cy + 4, color=INK, sw=4.2))     # коротка (−)
    if label:
        out.append(text(cx + 24, cy + 4, label, size=13, color=INK, bold=True, anchor="start"))
    return "".join(out)


def resistor_h(x0, x1, y, label=None, col=INK):
    """Горизонтальний резистор-зигзаг між (x0,y) та (x1,y)."""
    out = []
    n = 6
    seg = (x1 - x0) / (n + 1)
    amp = 7
    out.append(line(x0, y, x0 + seg, y, color=col, sw=1.6))
    xx = x0 + seg
    up = True
    for i in range(n):
        ny = y - amp if up else y + amp
        out.append(line(xx, y if i == 0 else (y - amp if not up else y + amp), xx + seg, ny, color=col, sw=1.6))
        xx += seg
        up = not up
    out.append(line(xx, y - amp if not up else y + amp, x1, y, color=col, sw=1.6))
    if label:
        out.append(text((x0 + x1) / 2, y - 16, label, size=12, color=col, bold=True))
    return "".join(out)


def resistor_v(x, y0, y1, label=None, side="right", col=INK):
    out = []
    n = 6
    seg = (y1 - y0) / (n + 1)
    amp = 7
    out.append(line(x, y0, x, y0 + seg, color=col, sw=1.6))
    yy = y0 + seg
    rt = True
    for i in range(n):
        nx = x + amp if rt else x - amp
        out.append(line(x if i == 0 else (x + amp if not rt else x - amp), yy, nx, yy + seg, color=col, sw=1.6))
        yy += seg
        rt = not rt
    out.append(line(x + amp if not rt else x - amp, yy, x, y1, color=col, sw=1.6))
    if label:
        lx = x + 14 if side == "right" else x - 14
        an = "start" if side == "right" else "end"
        out.append(text(lx, (y0 + y1) / 2 + 4, label, size=12, color=col, bold=True, anchor=an))
    return "".join(out)


# ════════════════════════════════════════════════════════════════════════════
# 1. conserve.svg — інтуїція: що саме зберігається
# ════════════════════════════════════════════════════════════════════════════
def fig_conserve():
    W, H = 680, 330
    f = []
    f.append(text(W / 2, 30, "Два закони — два збереження", size=16, bold=True))

    # ── ліва панель: вузол не накопичує заряд (труба-розгалуження) ──
    lx = 175
    ny = 150
    f.append(textbox(lx, 70, "ЗАРЯД нікуди не дівається", size=12, color=NEG, bold=True,
                     fill="#eaf0fd", stroke=NEG)[0])
    # вузол
    f.append(dot(lx, ny, 6, INK))
    # вхідна труба
    f.append(arrow(lx - 95, ny, lx - 8, ny, color=POS, sw=3))
    f.append(text(lx - 60, ny - 12, "втікає", size=11, color=POS, anchor="middle"))
    # дві вихідні
    f.append(arrow(lx + 8, ny - 4, lx + 80, ny - 55, color=FIELD, sw=3))
    f.append(arrow(lx + 8, ny + 4, lx + 80, ny + 55, color=FIELD, sw=3))
    f.append(text(lx + 80, ny - 62, "витікає", size=11, color=FIELD, anchor="middle"))
    f.append(text(lx + 80, ny + 78, "витікає", size=11, color=FIELD, anchor="middle"))
    f.append(textbox(lx, ny + 118, "скільки втекло —\nстільки й витекло", size=11, color=INK,
                     fill="#eef7f0", stroke=FIELD)[0])

    # ── права панель: контур повертає рівно стільки, скільки забрав (енергія) ──
    rx = 505
    cy = 165
    f.append(textbox(rx, 70, "ЕНЕРГІЯ повертається до нуля", size=12, color=POS, bold=True,
                     fill="#fdecea", stroke=POS)[0])
    # замкнене кільце-контур зі сходинками висоти (потенціал)
    ring_x = [rx - 90, rx - 30, rx + 30, rx + 90, rx + 90, rx - 90]
    ring_y = [cy + 40, cy - 40, cy - 40, cy + 40, cy + 90, cy + 90]
    # підйом джерела
    f.append(line(rx - 90, cy + 40, rx - 30, cy - 40, color=POS, sw=2.6))
    f.append(text(rx - 78, cy, "+", size=15, color=POS, bold=True, anchor="end"))
    # верхня полиця
    f.append(line(rx - 30, cy - 40, rx + 30, cy - 40, color=INK, sw=2.0))
    # спад на елементах
    f.append(line(rx + 30, cy - 40, rx + 90, cy + 40, color=NEG, sw=2.6))
    f.append(text(rx + 80, cy, "−", size=15, color=NEG, bold=True, anchor="start"))
    # повернення на дно
    f.append(line(rx + 90, cy + 40, rx - 90, cy + 40, color=INK, sw=2.0))
    f.append(dot(rx - 90, cy + 40, 4, INK))
    # стрілка-«обхід»
    f.append(arrow(rx - 60, cy + 12, rx - 42, cy - 12, color=MUTED, sw=2))
    f.append(arrow(rx + 60, cy - 12, rx + 78, cy + 12, color=MUTED, sw=2))
    f.append(textbox(rx, cy + 78, "піднявся й опустився —\nповернувся на той самий рівень", size=11, color=INK,
                     fill="#fdecea", stroke=POS)[0])

    # розділова лінія
    f.append(line(W / 2, 56, W / 2, H - 20, color="#e3e6ea", sw=1.4))
    render(os.path.join(IMG, "conserve.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. kcl.svg — закон струмів із числами
# ════════════════════════════════════════════════════════════════════════════
def fig_kcl():
    W, H = 600, 340
    f = []
    f.append(text(W / 2, 30, "Закон струмів: вузол нічого не накопичує", size=15, bold=True))

    nx, ny = 300, 175
    f.append(dot(nx, ny, 7, INK))
    f.append(text(nx + 16, ny - 12, "вузол", size=12, color=MUTED, anchor="start"))

    # два втікання
    f.append(arrow(nx - 150, ny - 70, nx - 10, ny - 6, color=POS, sw=3))
    f.append(text(nx - 150, ny - 80, "I₁ = 3 A", size=13, color=POS, bold=True, anchor="middle"))
    f.append(arrow(nx - 150, ny + 70, nx - 10, ny + 6, color=POS, sw=3))
    f.append(text(nx - 150, ny + 92, "I₂ = 2 A", size=13, color=POS, bold=True, anchor="middle"))

    # три витікання
    f.append(arrow(nx + 10, ny - 6, nx + 150, ny - 80, color=FIELD, sw=3))
    f.append(text(nx + 150, ny - 90, "I₃ = 4 A", size=13, color=FIELD, bold=True, anchor="middle"))
    f.append(arrow(nx + 10, ny + 2, nx + 155, ny + 8, color=FIELD, sw=3))
    f.append(text(nx + 165, ny + 12, "I₄ = 1 A", size=13, color=FIELD, bold=True, anchor="start"))

    # підпис балансу
    body, _, _ = textbox(W / 2, ny + 120,
                         "втікло  I₁ + I₂ = 3 + 2 = 5 A     =     витекло  I₃ + I₄ = 4 + 1 = 5 A",
                         size=12, color=INK, fill=FILL, stroke=INK)
    f.append(body)
    f.append(text(W / 2, H - 16, "у вузлі нема куди зникнути заряду — баланс точний у кожну мить", size=11, color=MUTED))
    render(os.path.join(IMG, "kcl.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 3. kvl.svg — закон напруг із числами (один контур)
# ════════════════════════════════════════════════════════════════════════════
def fig_kvl():
    W, H = 600, 380
    f = []
    f.append(text(W / 2, 30, "Закон напруг: обійшов контур — повернувся на той самий рівень", size=14, bold=True))

    # прямокутний контур
    L, R, T, B = 150, 450, 90, 300
    f.append(line(L, T, R, T, color=INK, sw=1.8))   # верх
    f.append(line(R, T, R, B, color=INK, sw=1.8))   # право (тимчасово, перекриється елементами)
    f.append(line(L, B, R, B, color=INK, sw=1.8))   # низ
    f.append(line(L, T, L, B, color=INK, sw=1.8))   # ліво

    # джерело 12 В ліворуч
    f.append(rect(L - 1.5, 170, 3, 0))  # noop spacing
    f.append(battery(L, (T + B) / 2, vert=True))
    f.append(text(L - 18, (T + B) / 2 + 4, "12 В", size=13, color=POS, bold=True, anchor="end"))
    f.append(text(L - 18, T + 18, "+", size=15, color=POS, bold=True, anchor="end"))
    f.append(text(L - 18, B - 8, "−", size=15, color=NEG, bold=True, anchor="end"))

    # R1 згори (спад 7 В), R2 справа (спад 5 В)
    f.append(rect(L + 70, T - 9, 160, 18, fill=BG, stroke=BG, sw=0))  # сховати лінію під резистором
    f.append(resistor_h(L + 70, R - 70, T, label="R₁", col=INK))
    f.append(text((L + R) / 2, T + 22, "спад 7 В", size=12, color=NEG, anchor="middle"))

    f.append(rect(R - 9, 150, 18, 100, fill=BG, stroke=BG, sw=0))
    f.append(resistor_v(R, T + 60, B - 60, label="R₂", side="right", col=INK))
    f.append(text(R - 14, (T + B) / 2 + 4, "спад 5 В", size=12, color=NEG, anchor="end"))

    # стрілка обходу
    f.append(arrow((L + R) / 2 - 22, (T + B) / 2 + 40, (L + R) / 2 + 22, (T + B) / 2 + 40, color=MUTED, sw=2))
    f.append(text((L + R) / 2, (T + B) / 2 + 62, "обходимо контур", size=11, color=MUTED))

    # баланс
    body, _, _ = textbox(W / 2, B + 50,
                         "підйом  +12 В     −     спади  (7 + 5) В   =   0",
                         size=13, color=INK, fill=FILL, stroke=INK, bold=True)
    f.append(body)
    f.append(text(W / 2, H - 14, "джерело піднімає на 12 В — рівно стільки розкладається на резисторах", size=11, color=MUTED))
    render(os.path.join(IMG, "kvl.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 4. solve.svg — два закони + Ом = система, що розв'язує коло
# ════════════════════════════════════════════════════════════════════════════
def fig_solve():
    W, H = 700, 380
    f = []
    f.append(text(W / 2, 30, "Три інструменти, що замикають коло на однозначний розв'язок", size=15, bold=True))

    # схема ліворуч: два контури, спільна гілка
    Lx, Mx, Rx = 110, 330, 470
    T, B = 95, 290
    # рамка-зона схеми
    # вузли A (верх-середина) і B (низ-середина)
    Ay, By = T, B
    # ліва петля: джерело + R1 згори
    f.append(battery(Lx, (T + B) / 2, vert=True))
    f.append(text(Lx - 16, (T + B) / 2 + 4, "E", size=13, color=POS, bold=True, anchor="end"))
    f.append(line(Lx, T, Mx, T, color=INK, sw=1.8))            # верх ліва
    f.append(line(Lx, B, Mx, B, color=INK, sw=1.8))            # низ ліва
    f.append(line(Lx, T, Lx, (T + B) / 2 - 8, color=INK, sw=1.8))
    f.append(line(Lx, (T + B) / 2 + 8, Lx, B, color=INK, sw=1.8))
    f.append(rect(Lx + 55, T - 9, 130, 18, fill=BG, stroke=BG, sw=0))
    f.append(resistor_h(Lx + 55, Mx - 30, T, label="R₁", col=INK))

    # спільна середня гілка R3 (між вузлами A і B)
    f.append(dot(Mx, Ay, 5, NEG))
    f.append(dot(Mx, By, 5, NEG))
    f.append(text(Mx + 10, Ay - 8, "A", size=13, color=NEG, bold=True, anchor="start"))
    f.append(text(Mx + 10, By + 16, "B", size=13, color=NEG, bold=True, anchor="start"))
    f.append(rect(Mx - 9, Ay + 30, 18, (By - Ay) - 60, fill=BG, stroke=BG, sw=0))
    f.append(resistor_v(Mx, Ay + 30, By - 30, label="R₃", side="left", col=NEG))

    # права петля: R2 згори, провід праворуч
    f.append(line(Mx, T, Rx, T, color=INK, sw=1.8))
    f.append(line(Mx, B, Rx, B, color=INK, sw=1.8))
    f.append(line(Rx, T, Rx, B, color=INK, sw=1.8))
    f.append(rect(Mx + 30, T - 9, 120, 18, fill=BG, stroke=BG, sw=0))
    f.append(resistor_h(Mx + 30, Rx - 10, T, label="R₂", col=INK))

    # струми
    f.append(text(Lx + 95, T - 18, "I₁ →", size=12, color=POS, bold=True, anchor="middle"))
    f.append(text(Mx + 90, T - 18, "← I₂", size=12, color=POS, bold=True, anchor="middle"))
    f.append(text(Mx - 20, (Ay + By) / 2 + 4, "I₃", size=12, color=FIELD, bold=True, anchor="end"))
    f.append(arrow(Mx + 22, (Ay + By) / 2 - 10, Mx + 22, (Ay + By) / 2 + 14, color=FIELD, sw=2))

    # права колонка: три рівняння
    bx = 520
    f.append(textbox(bx + 78, 110, "вузол A:\nI₁ = I₂ + I₃", size=12, color=NEG, bold=True,
                     fill="#eaf0fd", stroke=NEG)[0])
    f.append(text(bx + 78, 138, "закон струмів", size=10, color=MUTED))

    f.append(textbox(bx + 78, 195, "ліва петля:\nE = I₁R₁ + I₃R₃", size=12, color=POS, bold=True,
                     fill="#fdecea", stroke=POS)[0])
    f.append(text(bx + 78, 223, "закон напруг", size=10, color=MUTED))

    f.append(textbox(bx + 78, 280, "права петля:\nI₃R₃ = I₂R₂", size=12, color=POS, bold=True,
                     fill="#fdecea", stroke=POS)[0])
    f.append(text(bx + 78, 308, "закон напруг", size=10, color=MUTED))

    f.append(textbox(W / 2, H - 22,
                     "три невідомі струми  →  три рівняння  →  єдиний розв'язок (спади U = I·R дає закон Ома)",
                     size=12, color=INK, fill=FILL, stroke=FIELD)[0])
    render(os.path.join(IMG, "solve.svg"), W, H, *f)


if __name__ == "__main__":
    fig_conserve()
    fig_kcl()
    fig_kvl()
    fig_solve()
    print("OK: 4 фігури у", IMG)
