# -*- coding: utf-8 -*-
"""Фігури для статті «Органайзер кабелів (стрічка)». Вивід — ./img/*.svg."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

HOOK = "#c0392b"   # гачки — гарячий
LOOP = "#2457d6"   # петельки — холодний
TAPE = "#e8edf2"   # тіло стрічки
WIRE = "#8a5a2b"   # умовний джгут дротів


# ── Фігура 1: як тримається гачок-петелька (мікрозчеплення) ──────────────────
def fig_hookloop():
    W, H = 720, 430
    f = []
    f.append(text(W/2, 30, "Зчеплення гачок–петелька: тисячі дрібних застібок замість вузла", size=16, bold=True))

    # Ліворуч: дві розведені стрічки (гачки / петельки) з мікроструктурою
    # Смуга гачків (верхня)
    hx, hy, hw, hh = 60, 90, 300, 46
    f.append(rect(hx, hy, hw, hh, fill="#fdecea", stroke=HOOK, sw=1.5))
    f.append(text(hx-8, hy+hh/2+5, "гачки", size=13, color=HOOK, anchor="end", bold=True))
    # маленькі гачки як дуги вниз
    n = 12
    for i in range(n):
        gx = hx + 16 + i*(hw-24)/(n-1)
        f.append('<path d="M%.1f %.1f q 6 14 12 0" fill="none" stroke="%s" stroke-width="2.2"/>'
                 % (gx, hy+hh, HOOK))

    # Смуга петельок (нижня)
    ly = hy + hh + 60
    f.append(rect(hx, ly, hw, hh, fill="#eaf0fd", stroke=LOOP, sw=1.5))
    f.append(text(hx-8, ly+hh/2+5, "петельки", size=13, color=LOOP, anchor="end", bold=True))
    for i in range(n):
        gx = hx + 16 + i*(hw-24)/(n-1)
        f.append('<path d="M%.1f %.1f a 7 12 0 1 1 0.1 0" fill="none" stroke="%s" stroke-width="2.2"/>'
                 % (gx, ly-2, LOOP))

    # стрілка «притиснув» між ними
    f.append(arrow(hx+hw/2, hy+hh+8, hx+hw/2, ly-16, color=INK, sw=2))
    f.append(text(hx+hw+20, (hy+hh+ly)/2+5, "притиснув →", size=13, color=MUTED, anchor="start"))

    # Праворуч: збільшений один зачеп
    zx = 470
    f.append(circle(zx+110, 210, 96, fill="#ffffff", stroke=MUTED, sw=1.2))
    # петелька (велика)
    f.append('<path d="M%.1f %.1f a 34 54 0 1 1 0.1 0" fill="none" stroke="%s" stroke-width="5"/>'
             % (zx+110, 262, LOOP))
    # гачок, що ввійшов у петельку
    f.append('<path d="M%.1f %.1f q 30 66 58 6" fill="none" stroke="%s" stroke-width="5"/>'
             % (zx+92, 150, HOOK))
    box, bw, bh = textbox(zx+110, 348, "один гачок = одна петелька\nсотні на см² = міцно", size=12, color=INK)
    f.append(box)

    render(os.path.join(OUT, "hook-loop.svg"), W, H, *f)


# ── Фігура 2: обгортання джгута стрічкою (петля крізь проріз) ────────────────
def fig_wrap():
    W, H = 800, 300
    f = []
    f.append(text(W/2, 30, "Як застібається стрічка: обвів джгут → пропустив крізь проріз → притиснув назад", size=15, bold=True))

    cy = 175
    # джгут дротів — пучок кружечків
    bx = 150
    for i, dy in enumerate((-14, -5, 5, 14, 0)):
        f.append(circle(bx, cy+dy, 9, fill="#f6ecd9", stroke=WIRE, sw=1.6))
    f.append(text(bx, cy+56, "джгут дротів", size=12, color=MUTED))

    # тіло стрічки, що обходить джгут і йде до прорізу
    f.append('<path d="M%.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" '
             'fill="none" stroke="%s" stroke-width="18" stroke-linecap="round"/>'
             % (bx+22, cy-30, 300, 70, 380, 70, 470, cy-18, TAPE))
    f.append('<path d="M%.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" '
             'fill="none" stroke="%s" stroke-width="18" stroke-linecap="round"/>'
             % (bx+22, cy+30, 300, 280, 380, 280, 470, cy+18, TAPE))

    # проріз (петелька-вушко) на кінці, крізь який протягують хвіст
    lx, ly = 500, cy
    f.append(rect(lx-16, ly-34, 32, 68, fill="#ffffff", stroke=INK, sw=2, rx=10))
    f.append(rect(lx-7, ly-24, 14, 48, fill=BG, stroke=INK, sw=1.6, rx=6))  # сам проріз
    f.append(text(lx, ly-46, "проріз (вушко)", size=11, color=MUTED))

    # хвіст, протягнутий крізь проріз і загнутий назад — тут працює гачок-петелька
    f.append('<path d="M%.1f %.1f L %.1f %.1f q 60 0 60 -34 q 0 -34 -60 -34 L %.1f %.1f" '
             'fill="none" stroke="%s" stroke-width="16" stroke-linecap="round"/>'
             % (lx+8, cy, 600, cy, 585, cy-40, TAPE))
    f.append(text(628, cy+52, "хвіст загнув назад —\nгачок хапає петельку", size=11, color=INK))

    render(os.path.join(OUT, "wrap.svg"), W, H, *f)


# ── Фігура 3: три способи стягнути джгут (порівняння) ────────────────────────
def fig_compare():
    W, H = 760, 320
    f = []
    f.append(text(W/2, 28, "Три способи стягнути джгут — і коли який", size=16, bold=True))

    col_w = 230
    xs = [30, 30+col_w+20, 30+2*(col_w+20)]
    titles = ["Нейлонова стяжка", "Стрічка гачок-петелька", "Спіральна обмотка"]
    cols = [HOOK, LOOP, FIELD]
    notes = [
        "храповик клацнув —\nзатягнув НАЗАВЖДИ.\nЗняти = різати.\nДешево, тонко, надійно.",
        "багаторазова:\nрозстебнув, додав дріт,\nстебнув знову.\nдля стенду й пучків,\nщо ростуть.",
        "спіраль накрутив —\nдроти можна вводити\nй виводити вздовж.\nзахищає від тертя.",
    ]
    for x, ti, c, nt in zip(xs, titles, cols, notes):
        f.append(rect(x, 46, col_w, 250, fill="#ffffff", stroke=c, sw=1.8))
        f.append(text(x+col_w/2, 72, ti, size=13, color=c, bold=True))
        # маленька іконка джгута
        iy = 108
        for dy in (-10, -3, 4, 11):
            f.append(circle(x+col_w/2, iy+dy, 7, fill="#f6ecd9", stroke=WIRE, sw=1.3))
        # обгортка навколо іконки
        f.append(rect(x+col_w/2-26, iy-20, 52, 40, fill="none", stroke=c, sw=2.4, rx=8))
        f.append(fitbox(x+16, 156, col_w-32, 128, nt, size=12, fill="#fafbfc", stroke="#e5e7eb", color=INK))

    render(os.path.join(OUT, "compare.svg"), W, H, *f)


if __name__ == "__main__":
    fig_hookloop()
    fig_wrap()
    fig_compare()
    print("figs done:", os.listdir(OUT))
