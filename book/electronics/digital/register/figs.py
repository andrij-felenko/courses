# -*- coding: utf-8 -*-
"""Фігури до вставки «74HC165 — паралельно-послідовний регістр входів».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── Фігура 1: 8 кнопок → 3 лінії МК (навіщо потрібен PISO) ──────────────────
def fig_buttons_to_three_lines():
    W, H = 780, 470
    f = [text(W / 2, 28, "Вісім кнопок крізь 74HC165 — лише три дроти до мікроконтролера",
              size=15, bold=True)]

    # вісім кнопок ліворуч
    bx = 60
    top = 70
    gap = 42
    for i in range(8):
        cy = top + i * gap
        f.append(circle(bx, cy, 9, fill="#eef2f7", stroke=LINE, sw=1.4))
        f.append(text(bx - 22, cy + 4, "D%d" % i, size=11, color=MUTED, anchor="end"))
        f.append(line(bx + 9, cy, 250, cy, color=MUTED, sw=1.3))

    # корпус 74HC165
    cx0, cy0, cw, ch = 250, top - 14, 150, 7 * gap + 28
    f.append(rect(cx0, cy0, cw, ch, fill=FILL, stroke=LINE, sw=1.8))
    f.append(text(cx0 + cw / 2, cy0 + ch / 2 - 8, "74HC165", size=15, bold=True))
    f.append(text(cx0 + cw / 2, cy0 + ch / 2 + 12, "PISO", size=12, color=MUTED))
    f.append(text(cx0 + cw / 2, cy0 - 8, "8 паралельних входів D0..D7", size=10, color=MUTED))

    # три лінії праворуч до МК
    mx = 560
    mcu_y = top + 3 * gap
    sigs = [("PL  (защіпка)", mcu_y - gap, POS),
            ("CP  (такт)",    mcu_y,       INK),
            ("Q7  (дані)",    mcu_y + gap, FIELD)]
    for name, yy, col in sigs:
        f.append(arrow(cx0 + cw, yy, mx, yy, color=col, sw=2.0))
        f.append(text((cx0 + cw + mx) / 2, yy - 8, name, size=11, color=col, bold=True))

    # МК
    f.append(rect(mx, top - 14, 150, 7 * gap + 28, fill="#eef2f7", stroke=LINE, sw=1.8))
    f.append(text(mx + 75, mcu_y - 4, "Мікро-", size=14, bold=True))
    f.append(text(mx + 75, mcu_y + 16, "контролер", size=14, bold=True))
    f.append(text(mx + 75, top + 7 * gap + 6, "3 піни", size=11, color=MUTED))

    # підсумок унизу
    f.append(text(W / 2, H - 18,
                  "8 входів коштують 8 пінів навпростець — або 3 піни через регістр (і так само для 16, 24, 32...).",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "buttons-to-three-lines.svg"), W, H, *f)


# ── Фігура 2: защіпнути, тоді висунути — часова діаграма ─────────────────────
def fig_load_then_shift():
    W, H = 820, 430
    f = [text(W / 2, 28, "Один цикл читання: PL защіпає вісім входів, потім CP висуває їх по одному в Q7",
              size=14, bold=True)]

    # геометрія доріжок
    x0 = 130           # початок осі часу
    x1 = 780           # кінець
    hi = 22            # висота рівня «1» над базовою лінією
    rows = [("PL", 90, POS),
            ("CP", 170, INK),
            ("Q7", 250, FIELD)]
    for name, yb, col in rows:
        f.append(text(x0 - 14, yb - hi / 2 + 4, name, size=13, color=col, bold=True, anchor="end"))
        f.append(line(x0, yb, x1, yb, color=MUTED, sw=1.0))  # базова лінія «0»

    # часові межі: фаза LOAD, тоді 8 тактів SHIFT
    load_w = 90
    n = 8
    clk_w = (x1 - (x0 + load_w) - 20) / n   # ширина одного такту

    # ── PL: спадає в LOW на час завантаження, далі HIGH ──
    yb = 90
    # старт HIGH
    f.append(line(x0, yb - hi, x0 + 16, yb - hi, color=POS, sw=2.4))
    f.append(line(x0 + 16, yb - hi, x0 + 16, yb, color=POS, sw=2.4))      # ↓ в LOW
    f.append(line(x0 + 16, yb, x0 + load_w, yb, color=POS, sw=2.4))       # LOW = load
    f.append(line(x0 + load_w, yb, x0 + load_w, yb - hi, color=POS, sw=2.4))  # ↑ назад
    f.append(line(x0 + load_w, yb - hi, x1, yb - hi, color=POS, sw=2.4))
    f.append(text(x0 + (16 + load_w) / 2, yb + 18, "PL=0: захопити D0..D7", size=10, color=POS))
    f.append(text(x0 + (load_w + x1) / 2, yb - hi - 8, "PL=1: режим зсуву", size=10, color=POS))

    # ── CP: тихо під час load, тоді 8 імпульсів ──
    yb = 170
    cx = x0
    f.append(line(x0, yb, x0 + load_w, yb, color=INK, sw=2.4))  # тихо
    cx = x0 + load_w
    for i in range(n):
        # імпульс: ↑ half, ↓ half
        f.append(line(cx, yb, cx + clk_w * 0.25, yb, color=INK, sw=2.4))
        f.append(line(cx + clk_w * 0.25, yb, cx + clk_w * 0.25, yb - hi, color=INK, sw=2.4))
        f.append(line(cx + clk_w * 0.25, yb - hi, cx + clk_w * 0.75, yb - hi, color=INK, sw=2.4))
        f.append(line(cx + clk_w * 0.75, yb - hi, cx + clk_w * 0.75, yb, color=INK, sw=2.4))
        f.append(line(cx + clk_w * 0.75, yb, cx + clk_w, yb, color=INK, sw=2.4))
        cx += clk_w
    f.append(text(x0 + load_w + (x1 - x0 - load_w) / 2, yb + 18, "8 фронтів CP — по одному на біт", size=10, color=INK))

    # ── Q7: показує D0, потім D1... на кожному фронті ──
    yb = 250
    bits = [1, 0, 1, 1, 0, 0, 1, 0]   # приклад зчитаних бітів
    f.append(line(x0, yb, x0 + load_w, yb, color=FIELD, sw=2.4))  # D0 вже на виході після load? показуємо з 1-го такту
    cx = x0 + load_w
    prev = None
    for i in range(n):
        lvl = yb - hi if bits[i] else yb
        if prev is not None and prev != lvl:
            f.append(line(cx, prev, cx, lvl, color=FIELD, sw=2.4))  # перехід
        f.append(line(cx, lvl, cx + clk_w, lvl, color=FIELD, sw=2.4))
        f.append(text(cx + clk_w / 2, yb + 18, "D%d" % i, size=10, color=FIELD))
        prev = lvl
        cx += clk_w

    # легенда рівнів
    f.append(text(x1 + 0, 90 - hi - 8, "", size=10))
    f.append(text(W / 2, H - 20,
                  "Перший фронт CP виставляє найстарший защіпнутий біт у Q7; кожен наступний фронт зсуває низку далі.",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "load-then-shift.svg"), W, H, *f)


if __name__ == "__main__":
    fig_buttons_to_three_lines()
    fig_load_then_shift()
    print("OK: figures written to", IMG)
