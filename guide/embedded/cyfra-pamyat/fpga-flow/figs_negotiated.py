# -*- coding: utf-8 -*-
"""Фігури до вставки math-negotiated-routing (PathFinder / негоційоване трасування).
Окремий генератор у теці теми (щоб не конфліктувати з паралельним письмом figs.py):
пише SVG у той самий ./img/. Стиль — зі спільного svgkit (НЕ переписувати).
Запуск:  python figs_negotiated.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Локальні відтінки (узгоджені з figs.py цієї теми)
SYN = "#27ae60"     # базова вартість / «зійшлося»
AMBER = "#b9770e"   # історія
SOFT = "#eef4ff"
SOFTG = "#eafaf0"


# ── 1. Анатомія Cn = (bn + hn)·pn: три доданки, три ролі ─────────────────────
def fig_cost_anatomy():
    W, H = 720, 340
    p = []
    cy = 96
    fx = W / 2
    p.append(text(fx - 150, cy, "Cₙ", size=30, color=INK, bold=True))
    p.append(text(fx - 112, cy, "=", size=26, color=MUTED))
    p.append(text(fx - 42, cy, "( bₙ", size=26, color=SYN, bold=True))
    p.append(text(fx + 6, cy, "+", size=22, color=MUTED))
    p.append(text(fx + 54, cy, "hₙ )", size=26, color=AMBER, bold=True))
    p.append(text(fx + 108, cy, "·", size=26, color=MUTED))
    p.append(text(fx + 144, cy, "pₙ", size=26, color=POS, bold=True))

    def note(cx, col, head, body):
        p.append(line(cx, cy + 18, cx, cy + 54, color=col, sw=1.6))
        b, w, h = textbox(cx, cy + 54 + 42, head + "\n" + body, size=10,
                          color=INK, fill="#fbfcff", stroke=col, sw=1.8, min_w=176)
        p.append(b)
        p.append(text(cx, cy + 54 + 42 - h / 2 + 15, head, size=11, color=col, bold=True))

    note(fx - 42, SYN, "базова вартість",
         "ціна ресурсу самого по\nсобі: довжина сегмента,\nзатримка. Стала.")
    note(fx + 54, AMBER, "історія переговорів",
         "росте щоітерації, доки\nресурс перевантажений.\nНакопичується, не спадає.")
    note(fx + 144, POS, "поточний тиск",
         "скільки сигналів претендує\nзараз. Множник > 1, коли\nпретензій більше, ніж місць.")

    render(os.path.join(IMG, "cost-anatomy.svg"), W, H, *p,
           title="Функція вартості PathFinder: три доданки, три ролі")


# ── 2. Лише поточна ціна → сигнали тікають разом і гойдаються вічно ──────────
def fig_oscillation():
    W, H = 720, 360
    p = []
    xL, xR = 250, 470
    ys = [110, 180, 250, 320]
    labs = ["ітер. 1", "ітер. 2", "ітер. 3", "ітер. 4"]
    for x, name in [(xL, "R1"), (xR, "R2")]:
        p.append(line(x, 92, x, 336, color="#c9d6f0", sw=2.4))
        p.append(text(x, 80, name, size=12, color=MUTED, bold=True))
    p.append(text(60, 58, "обидва сигнали бачать однакову ціну → тиснуть у той самий ресурс",
                  size=11, color=INK, anchor="start", bold=True))
    seq = [xL, xR, xL, xR]
    for i, xa in enumerate(seq):
        y = ys[i]
        p.append(text(60, y + 4, labs[i], size=10, color=MUTED, anchor="start", bold=True))
        p.append(circle(xa - 13, y, 13, fill="#eaf0fd", stroke=NEG, sw=2.0))
        p.append(text(xa - 13, y + 4, "A", size=11, color=NEG, bold=True))
        p.append(circle(xa + 13, y, 13, fill="#fdecea", stroke=POS, sw=2.0))
        p.append(text(xa + 13, y + 4, "B", size=11, color=POS, bold=True))
        anc = "start" if xa == xL else "end"
        tx = xa + (46 if xa == xL else -46)
        p.append(text(tx, y + 4, "обидва тут → перевантаження", size=9, color=POS,
                      anchor=anc, bold=True))
    for i in range(3):
        y0, y1 = ys[i] + 15, ys[i + 1] - 15
        xm = (seq[i] + seq[i + 1]) / 2
        p.append(arrow(xm, y0, xm, y1, color=MUTED, sw=1.6))
    render(os.path.join(IMG, "oscillation.svg"), W, H, *p,
           title="Лише поточна ціна: сигнали тікають разом і гойдаються вічно")


# ── 3. Історія росте сходинками, доки ресурс перевантажений ──────────────────
def fig_history_ramp():
    W, H = 720, 340
    p = []
    x0, y0 = 96, 278
    xW, yH = 548, 214
    p.append(line(x0, y0, x0 + xW, y0, color=INK, sw=1.8))
    p.append(line(x0, y0, x0, y0 - yH, color=INK, sw=1.8))
    p.append(text(x0 + xW, y0 + 20, "ітерація →", size=11, color=MUTED, anchor="end", bold=True))
    p.append(text(x0 + 4, y0 - yH - 4, "вартість ресурсу", size=11, color=MUTED, anchor="start", bold=True))
    n = 8
    dx = xW / (n + 1)
    base = 32
    hist_step = 22
    over_until = 6
    prev_x = x0
    prev_y = y0 - base
    for i in range(n):
        xi = x0 + (i + 1) * dx
        h_accum = hist_step * min(i, over_until)
        yi = y0 - base - h_accum
        col = POS if i <= over_until else SYN
        p.append(line(prev_x, prev_y, xi, prev_y, color=col, sw=2.6))
        if 0 < i <= over_until:
            p.append(line(xi, prev_y, xi, yi, color=POS, sw=1.5, dash="3 3"))
        prev_x, prev_y = xi, yi
    p.append(line(prev_x, prev_y, x0 + xW - 10, prev_y, color=SYN, sw=2.6))
    bx = x0 + (over_until + 1) * dx
    by = y0 - base - hist_step * over_until
    p.append(circle(bx, by, 7, fill=BG, stroke=SYN, sw=2.2))
    b, w, h = textbox(bx + 96, by + 34,
                      "ціна переросла обхід —\nслабший сигнал відступає,\nперевантаження зникає",
                      size=10, color=SYN, fill=SOFTG, stroke=SYN, sw=1.8, min_w=182)
    p.append(b)
    p.append(arrow(bx + 6, by + 4, bx + 96, by + 34 - h / 2, color=SYN, sw=1.5))
    p.append(line(x0, y0 - base, x0 - 6, y0 - base, color=MUTED, sw=1.4))
    p.append(text(x0 - 10, y0 - base + 4, "bₙ", size=11, color=SYN, anchor="end", bold=True))
    p.append(text(x0 + 1.6 * dx, y0 - base - hist_step * 2 - 10, "+hₙ щоітерації",
                  size=10, color=POS, anchor="start", bold=True))
    render(os.path.join(IMG, "history-ramp.svg"), W, H, *p,
           title="Історія росте сходинками, доки ресурс перевантажений")


if __name__ == "__main__":
    fig_cost_anatomy()
    fig_oscillation()
    fig_history_ramp()
    print("OK: negotiated-routing figures written to", IMG)
