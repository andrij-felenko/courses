# -*- coding: utf-8 -*-
"""Фігури до статті «Метод гілкових струмів» (book/electronics/analog/branch-current-method).
Фігури статті:
  branch-count.svg  — рахунок рівнянь: b гілок → (n−1) KCL + (b−n+1) KVL = b рівнянь = b невідомих
  branch-recipe.svg — рецептура методу гілкових струмів у п'ять кроків
  branch-solve.svg  — робочий приклад: дводжерельне коло, три гілкові струми, від'ємний I₂
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def dot(cx, cy, r=4, col=INK):
    return circle(cx, cy, r, fill=col, stroke=col)


def battery(cx, cy, label=None, vert=True):
    """Гальванічний елемент: довга риска (+) і коротка (−). Вертикальний."""
    out = []
    if vert:
        out.append(line(cx - 11, cy - 4, cx + 11, cy - 4, color=INK, sw=2.6))   # довга (+)
        out.append(line(cx - 6, cy + 4, cx + 6, cy + 4, color=INK, sw=4.2))     # коротка (−)
    if label:
        out.append(text(cx + 24, cy + 4, label, size=13, color=INK, bold=True, anchor="start"))
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
# 1. branch-count.svg — рахунок рівнянь
#    b гілок → (n−1) KCL + (b−n+1) KVL = b рівнянь = b невідомих
# ════════════════════════════════════════════════════════════════════════════
def fig_branch_count():
    W, H = 700, 380
    f = []
    f.append(text(W / 2, 30, "Скільки рівнянь потрібно — точно стільки, скільки гілок", size=15, bold=True))

    # ── схема-граф: 2 вузли, 3 гілки (b=3, n=2) ──
    Ax, Ay = 210, 130     # вузол A (верх)
    Bx, By = 210, 300     # вузол B (низ)
    # три гілки між A і B: ліва, середня, права
    lx, mx, rx = 110, 210, 310
    # ліва гілка
    f.append(line(Ax, Ay, lx, Ay, color=INK, sw=1.8))
    f.append(line(lx, Ay, lx, By, color=INK, sw=1.8))
    f.append(line(lx, By, Bx, By, color=INK, sw=1.8))
    # права гілка
    f.append(line(Ax, Ay, rx, Ay, color=INK, sw=1.8))
    f.append(line(rx, Ay, rx, By, color=INK, sw=1.8))
    f.append(line(rx, By, Bx, By, color=INK, sw=1.8))
    # середня гілка
    f.append(line(mx, Ay, mx, By, color=INK, sw=1.8))
    # елементи на гілках (щоб гілки читалися як окремі)
    f.append(rect(lx - 9, (Ay + By) / 2 - 24, 18, 48, fill=BG, stroke=BG, sw=0))
    f.append(resistor_v(lx, (Ay + By) / 2 - 24, (Ay + By) / 2 + 24, side="left", col=INK))
    f.append(rect(mx - 9, (Ay + By) / 2 - 24, 18, 48, fill=BG, stroke=BG, sw=0))
    f.append(resistor_v(mx, (Ay + By) / 2 - 24, (Ay + By) / 2 + 24, side="right", col=INK))
    f.append(rect(rx - 9, (Ay + By) / 2 - 24, 18, 48, fill=BG, stroke=BG, sw=0))
    f.append(resistor_v(rx, (Ay + By) / 2 - 24, (Ay + By) / 2 + 24, side="right", col=INK))
    # вузли
    f.append(dot(Ax, Ay, 6, NEG))
    f.append(dot(Bx, By, 6, NEG))
    f.append(text(Ax + 108, Ay - 4, "вузол A", size=12, color=NEG, bold=True, anchor="start"))
    f.append(text(Bx + 108, By + 4, "вузол B", size=12, color=NEG, bold=True, anchor="start"))
    f.append(text(mx + 108, (Ay + By) / 2, "n = 2 вузли", size=12, color=MUTED, anchor="start"))
    # підписи гілок (струми)
    f.append(text(lx - 16, (Ay + By) / 2 + 4, "I₁", size=13, color=POS, bold=True, anchor="end"))
    f.append(text(mx + 16, (Ay + By) / 2 + 4, "I₂", size=13, color=POS, bold=True, anchor="start"))
    f.append(text(rx + 16, (Ay + By) / 2 + 4, "I₃", size=13, color=POS, bold=True, anchor="start"))
    f.append(text(210, By + 40, "b = 3 гілки  →  3 невідомі струми", size=12, color=INK))

    # ── права колонка: рахунок ──
    cx = 500
    f.append(fitbox(cx - 90, 90, 200, 52,
                    "n − 1 = 1\nрівняння KCL", size=13, color=NEG, bold=True,
                    fill="#eaf0fd", stroke=NEG))
    f.append(text(cx + 10, 158, "(по одному на кожен", size=10, color=MUTED, anchor="middle"))
    f.append(text(cx + 10, 172, "вузол, крім останнього)", size=10, color=MUTED, anchor="middle"))

    f.append(fitbox(cx - 90, 190, 200, 52,
                    "b − n + 1 = 2\nрівняння KVL", size=13, color=POS, bold=True,
                    fill="#fdecea", stroke=POS))
    f.append(text(cx + 10, 258, "(по одному на кожну", size=10, color=MUTED, anchor="middle"))
    f.append(text(cx + 10, 272, "незалежну петлю)", size=10, color=MUTED, anchor="middle"))

    f.append(fitbox(cx - 90, 296, 200, 44,
                    "разом  1 + 2 = 3 = b", size=13, color=INK, bold=True,
                    fill="#eef7f0", stroke=FIELD))

    f.append(line(360, 70, 360, H - 20, color="#e3e6ea", sw=1.4))
    f.append(text(W / 2, H - 14, "рівнянь рівно стільки, скільки невідомих струмів — розв'язок єдиний", size=11, color=MUTED))
    render(os.path.join(IMG, "branch-count.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. branch-recipe.svg — п'ять кроків методу гілкових струмів
# ════════════════════════════════════════════════════════════════════════════
def fig_branch_recipe():
    W, H = 560, 430
    f = []
    f.append(text(W / 2, 30, "Метод гілкових струмів: п'ять кроків", size=16, bold=True))

    steps = [
        ("1", "Признач по струму кожній гілці — напрям бери довільно.", NEG),
        ("2", "Запиши KCL у (n−1) вузлах: втікання = витікання.", NEG),
        ("3", "Запиши KVL у (b−n+1) незалежних петлях.", POS),
        ("4", "Спади в KVL заміни на I·R за законом Ома.", POS),
        ("5", "Розв'яжи систему; мінус у відповіді — струм тече навпаки.", FIELD),
    ]
    y = 66
    bx, bw = 70, 430
    bh = 56
    gap = 14
    for num, txt, col in steps:
        # номер-кружок
        f.append(circle(bx, y + bh / 2, 17, fill="#fff", stroke=col, sw=2.4))
        f.append(text(bx, y + bh / 2 + 6, num, size=18, color=col, bold=True))
        # текст-рамка
        f.append(fitbox(bx + 30, y, bw, bh, txt, size=13, color=INK,
                        fill=FILL, stroke=col, sw=1.6))
        # стрілка вниз
        if num != "5":
            f.append(arrow(bx, y + bh + 2, bx, y + bh + gap - 1, color=MUTED, sw=2))
        y += bh + gap

    f.append(text(W / 2, H - 12, "перші три кроки дають рівно b рівнянь на b невідомих", size=11, color=MUTED))
    render(os.path.join(IMG, "branch-recipe.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 3. branch-solve.svg — робочий приклад: дводжерельне коло, від'ємний I₂
# ════════════════════════════════════════════════════════════════════════════
def fig_branch_solve():
    W, H = 700, 430
    f = []
    f.append(text(W / 2, 28, "Робочий приклад: два джерела, три гілки", size=16, bold=True))

    # прямокутне коло: два вузли A (верх-центр), B (низ-центр); три вертикальні гілки
    Lx, Mx, Rx = 130, 350, 570
    T, B = 90, 300
    Ay, By = T, B
    # верхня й нижня шини до вузлів
    f.append(line(Lx, T, Rx, T, color=INK, sw=1.8))
    f.append(line(Lx, B, Rx, B, color=INK, sw=1.8))

    # ── ліва гілка: E1 + R1 (струм I1 донизу, у вузол A зверху) ──
    f.append(line(Lx, T, Lx, T + 34, color=INK, sw=1.8))
    f.append(battery(Lx, T + 50, vert=True))
    f.append(text(Lx - 20, T + 54, "E₁ = 12 В", size=12, color=POS, bold=True, anchor="end"))
    f.append(text(Lx - 20, T + 34, "+", size=14, color=POS, bold=True, anchor="end"))
    f.append(line(Lx, T + 60, Lx, T + 96, color=INK, sw=1.8))
    f.append(rect(Lx - 9, T + 96, 18, 60, fill=BG, stroke=BG, sw=0))
    f.append(resistor_v(Lx, T + 96, T + 156, label="R₁ = 100 Ω", side="left", col=INK))
    f.append(line(Lx, T + 156, Lx, B, color=INK, sw=1.8))
    f.append(arrow(Lx, T + 168, Lx, T + 196, color=POS, sw=2.4))
    f.append(text(Lx + 14, T + 186, "I₁", size=13, color=POS, bold=True, anchor="start"))

    # ── права гілка: E2 + R2 (струм I2 донизу, у вузол A) ──
    f.append(line(Rx, T, Rx, T + 34, color=INK, sw=1.8))
    f.append(battery(Rx, T + 50, vert=True))
    f.append(text(Rx + 20, T + 54, "E₂ = 6 В", size=12, color=POS, bold=True, anchor="start"))
    f.append(text(Rx + 20, T + 34, "+", size=14, color=POS, bold=True, anchor="start"))
    f.append(line(Rx, T + 60, Rx, T + 96, color=INK, sw=1.8))
    f.append(rect(Rx - 9, T + 96, 18, 60, fill=BG, stroke=BG, sw=0))
    f.append(resistor_v(Rx, T + 96, T + 156, label="R₂ = 100 Ω", side="right", col=INK))
    f.append(line(Rx, T + 156, Rx, B, color=INK, sw=1.8))
    f.append(arrow(Rx, T + 168, Rx, T + 196, color=POS, sw=2.4))
    f.append(text(Rx - 14, T + 186, "I₂", size=13, color=POS, bold=True, anchor="end"))
    f.append(text(Rx - 14, T + 208, "(вийде −)", size=10, color=MUTED, anchor="end"))

    # ── середня гілка: R3 між вузлами A і B (струм I3 донизу) ──
    f.append(dot(Mx, Ay, 6, NEG))
    f.append(dot(Mx, By, 6, NEG))
    f.append(text(Mx + 12, Ay - 8, "A", size=13, color=NEG, bold=True, anchor="start"))
    f.append(text(Mx + 12, By + 18, "B", size=13, color=NEG, bold=True, anchor="start"))
    f.append(rect(Mx - 9, (Ay + By) / 2 - 30, 18, 60, fill=BG, stroke=BG, sw=0))
    f.append(resistor_v(Mx, (Ay + By) / 2 - 30, (Ay + By) / 2 + 30, label="R₃ = 200 Ω", side="right", col=NEG))
    f.append(arrow(Mx - 22, (Ay + By) / 2 - 12, Mx - 22, (Ay + By) / 2 + 16, color=FIELD, sw=2.4))
    f.append(text(Mx - 28, (Ay + By) / 2 + 4, "I₃", size=13, color=FIELD, bold=True, anchor="end"))

    # позначки петель
    f.append(text((Lx + Mx) / 2, (T + B) / 2 + 4, "петля I", size=12, color=MUTED, anchor="middle"))
    f.append(text((Mx + Rx) / 2, (T + B) / 2 + 4, "петля II", size=12, color=MUTED, anchor="middle"))

    # результати (окрема смуга під схемою)
    f.append(fitbox(140, 335, 420, 46,
                    "розв'язок:   I₁ = 48 мА     I₂ = −12 мА     I₃ = 36 мА",
                    size=14, color=INK, bold=True, fill="#eef7f0", stroke=FIELD))

    f.append(text(W / 2, H - 14, "перевірка KCL у вузлі A:  I₁ + I₂ = I₃  →  48 + (−12) = 36 мА  ✓", size=12, color=INK))
    render(os.path.join(IMG, "branch-solve.svg"), W, H, *f)


if __name__ == "__main__":
    fig_branch_count()
    fig_branch_recipe()
    fig_branch_solve()
    print("OK: 3 фігури у", IMG)
