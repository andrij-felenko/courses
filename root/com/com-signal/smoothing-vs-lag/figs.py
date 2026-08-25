# -*- coding: utf-8 -*-
"""Фігури до теми «Згладжування й затримка».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

import math, random

# Локальні відтінки понад палітру svgkit
GOLD = "#b9770e"     # «середній» фільтр / тепле виділення
PURP = "#8e44ad"     # передбачення (Калман)


def _polyline(pts, color, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    poly = " ".join("%.1f,%.1f" % p for p in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"%s/>' % (poly, color, sw, d))


# ── 1. Головна шкала компромісу: чистота ↑ тягне затримку ─────────────────────
def fig_tradeoff_curve():
    W, H = 660, 300
    f = [text(W / 2, 26, "Головна шкала: за гладкість платять затримкою", size=15, bold=True)]

    ox, oy, top, right = 90, 252, 46, 588
    f.append(arrow(ox, oy, ox, top, color=INK, sw=1.6))
    f.append(arrow(ox, oy, right, oy, color=INK, sw=1.6))
    f.append(text(W / 2, 278, "згладжування (чистота) →", size=11, bold=True))
    f.append(text(ox - 8, 52, "затримка", size=11, anchor="end", bold=True))

    # висхідна крива y = накопичена «ціна» (опукла вгору-праворуч)
    pts = []
    for i in range(31):
        t = i / 30.0
        xx = ox + (right - 24 - ox) * t
        yy = oy - (oy - top - 6) * (t ** 1.9)
        pts.append((xx, yy))
    f.append(_polyline(pts, FIELD, sw=2.8))

    # три робочі точки на кривій
    def at(t):
        x = ox + (right - 24 - ox) * t
        y = oy - (oy - top - 6) * (t ** 1.9)
        return x, y
    for t, lab, col in ((0.30, "легкий", NEG), (0.58, "середній", GOLD), (0.85, "важкий", POS)):
        x, y = at(t)
        f.append(circle(x, y, 5, fill=col, stroke=col, sw=1))
        f.append(text(x + 7, y + 4, lab, size=10, color=col, anchor="start", bold=True))

    f.append(text(right - 150, oy - 38, "«чисто й швидко» — порожньо",
                  size=10, color=MUTED, anchor="start", italic=True))
    render(os.path.join(IMG, "tradeoff-curve.svg"), W, H, *f)


# ── 2. Щоб відрізнити зміну від шуму, фільтр мусить зачекати ──────────────────
def fig_need_time():
    W, H = 680, 272
    f = [text(W / 2, 26, "Щоб відрізнити зміну від шуму, фільтр мусить зачекати", size=14, bold=True)]

    ox, oy, top, right = 70, 230, 48, 642
    f.append(arrow(ox, oy, ox, top, color=INK, sw=1.6))
    f.append(arrow(ox, oy, right, oy, color=INK, sw=1.6))
    f.append(text(right - 6, 248, "час →", size=11, bold=True))

    random.seed(11)
    n = 31
    lo_y, hi_y = 170.5, 111.0       # рівень «до» і «після» сходинки
    step = 15                        # індекс сходинки
    xs = [ox + (right - 24 - ox) * i / (n - 1) for i in range(n)]
    truth = [lo_y if i < step else hi_y for i in range(n)]
    f.append(_polyline(list(zip(xs, truth)), FIELD, sw=2.0))
    for i in range(n):
        jit = random.uniform(-6, 6)
        f.append(circle(xs[i], truth[i] + jit, 2.6, fill=NEG, stroke=NEG, sw=0.8))

    # межі рішення: +1 відлік (неясно) і +кілька (ясно)
    x1 = xs[step + 1]
    f.append(line(x1, oy, x1, 60, color=MUTED, sw=1.0, dash="3,3"))
    f.append(text(x1, 56, "+1 відлік: спайк чи зміна?", size=9.5, color=POS, bold=True))
    x2 = xs[step + 10]
    f.append(line(x2, oy, x2, 60, color=MUTED, sw=1.0, dash="3,3"))
    f.append(text(x2, 56, "+кілька: ясно, що зміна", size=9.5, color=FIELD, bold=True))

    f.append(text(W / 2, 262, "чекання на впевненість = затримка — звідси й закон",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "need-time.svg"), W, H, *f)


# ── 3. Робоче вікно: між смугою сигналу й смугою шуму ─────────────────────────
def fig_operating_window():
    W, H = 680, 250
    f = [text(W / 2, 26, "Робоча точка — між смугою сигналу й смугою шуму", size=14, bold=True)]

    axis_y = 150
    f.append(arrow(80, axis_y, 624, axis_y, color=INK, sw=2))
    f.append(text(620, 174, "частота →", size=11, bold=True))

    f.append(rect(80, 110, 180, 40, fill="#d8efd8", stroke=FIELD, sw=1.2, rx=0))
    f.append(text(170, 102, "сигнал (повільне)", size=10.5, color=FIELD, bold=True))
    f.append(rect(380, 110, 240, 40, fill="#cfd9f3", stroke=NEG, sw=1.2, rx=0))
    f.append(text(500, 102, "шум (швидке)", size=10.5, color=NEG, bold=True))

    f.append(line(300, 90, 300, 166, color=POS, sw=2.4, dash="5,3"))
    f.append(text(300, 190, "зріз фільтра", size=11, color=POS, bold=True))

    f.append(arrow(292, 158, 110, 158, color=FIELD, sw=1.6))
    f.append(text(190, 162, "пропустити", size=9.5, color=FIELD))
    f.append(arrow(308, 158, 590, 158, color=NEG, sw=1.6))
    f.append(text(470, 162, "відрізати", size=9.5, color=NEG))

    f.append(text(W / 2, 226, "смуги перекрилися — простий фільтр безсилий, треба хитріше",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "operating-window.svg"), W, H, *f)


# ── 4. Перефільтрування розгойдує контур керування ───────────────────────────
def fig_overfilter():
    W, H = 680, 290
    f = [text(W / 2, 26, "Перефільтрування: велика затримка розгойдує керування", size=13.5, bold=True)]

    ox, oy, top, right = 70, 250, 46, 642
    f.append(arrow(ox, oy, ox, top, color=INK, sw=1.6))
    f.append(arrow(ox, oy, right, oy, color=INK, sw=1.6))
    f.append(text(right - 6, 268, "час →", size=11, bold=True))

    target = 152.5
    f.append(_polyline([(ox, target), (630, target)], "#e4e4e4", sw=1.4, dash="6,4"))
    f.append(text(ox + 11, target - 8, "ціль", size=10, color=MUTED, anchor="start", italic=True))

    xs = [ox + i for i in range(0, right - 12 - ox, 7)]

    # мала затримка: швидке загасання до цілі (зелене)
    green = []
    for k, x in enumerate(xs):
        t = k * 0.16
        v = target - 62 * math.exp(-0.30 * t) * math.cos(0.9 * t)
        green.append((x, v))
    f.append(_polyline(green, FIELD, sw=2.0))
    f.append(text(ox + 308, 133, "мала затримка → сходиться", size=10, color=FIELD, anchor="start", bold=True))

    # велика затримка: наростаюче розгойдування (червоне)
    red = []
    for k, x in enumerate(xs):
        t = k * 0.16
        v = target - 35 * math.exp(0.085 * t) * math.cos(1.15 * t + 0.5)
        v = max(top + 4, min(oy - 4, v))
        red.append((x, v))
    f.append(_polyline(red, POS, sw=2.2))
    f.append(text(ox + 280, 70, "велика затримка → розгойдування", size=10, color=POS, anchor="start", bold=True))

    render(os.path.join(IMG, "overfilter.svg"), W, H, *f)


# ── 5. Та сама зміна крізь легкий / середній / важкий фільтри ─────────────────
def fig_filter_strength_comparison():
    W, H = 700, 290
    f = [text(W / 2, 26, "Та сама зміна крізь легкий, середній, важкий фільтри", size=14, bold=True)]

    ox, oy, top, right = 70, 250, 46, 642
    f.append(arrow(ox, oy, ox, top, color=INK, sw=1.6))
    f.append(arrow(ox, oy, right, oy, color=INK, sw=1.6))
    f.append(text(right - 6, 268, "час →", size=11, bold=True))

    random.seed(5)
    n = 81
    step = 30
    lo_y, hi_y = 191.5, 103.8
    xs = [ox + i * 7 for i in range(n)]
    truth = [lo_y if i < step else hi_y for i in range(n)]
    raw_v = [truth[i] + random.uniform(-4.5, 4.5) for i in range(n)]

    f.append(_polyline(list(zip(xs, truth)), "#e4e4e4", sw=1.4, dash="5,3"))

    def ema(series, a):
        out, s = [], series[0]
        for v in series:
            s = a * v + (1 - a) * s
            out.append(s)
        return out

    light = ema(raw_v, 0.5)     # N≈4
    mid = ema(raw_v, 0.12)      # N≈16
    heavy = ema(raw_v, 0.05)    # N≈40
    f.append(_polyline(list(zip(xs, light)), NEG, sw=2.0))
    f.append(_polyline(list(zip(xs, mid)), GOLD, sw=2.0))
    f.append(_polyline(list(zip(xs, heavy)), POS, sw=2.0))

    f.append(text(xs[44], light[44] - 9, "N=4", size=10, color=NEG, anchor="start", bold=True))
    f.append(text(xs[50], mid[50] - 6, "N=16", size=10, color="#9a7a1e", anchor="start", bold=True))
    f.append(text(xs[58], heavy[58] + 14, "N=40", size=10, color=POS, anchor="start", bold=True))

    f.append(text(W / 2, 280, "чистіше = пізніше: важкий доходить останнім",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "filter-strength-comparison.svg"), W, H, *f)


# ── 6. Чотири способи обійти компроміс ────────────────────────────────────────
def fig_escape_routes():
    W, H = 720, 260
    f = [text(W / 2, 26, "Як обійти компроміс: додати інформацію", size=15, bold=True)]

    cards = [
        ("нелінійність", "медіана б'є викид", "без плати затримкою", FIELD),
        ("адаптивність", "α більша на події", "рух по кривій", NEG),
        ("передбачення", "модель руху (Калман)", "прогноз гасить затримку", PURP),
        ("частіша вибірка", "більше відліків/с", "та сама тиша, менше мс", GOLD),
    ]
    x = 14
    for title_, mid, note, col in cards:
        f.append(rect(x, 54, 166, 178, fill="#fbfbfb", stroke=col, sw=1.5))
        f.append(text(x + 83, 80, title_, size=12, color=col, bold=True))
        f.append(fitbox(x + 10, 134, 146, 26, mid, size=10.5, color=INK, bold=True,
                        fill="#fbfbfb", stroke="none", sw=0))
        f.append(text(x + 83, 194, note, size=9.5, color=MUTED, italic=True))
        x += 176

    f.append(text(W / 2, 250,
                  "кожна вносить щось понад сирий потік — без нової інформації компромісу не обійти",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "escape-routes.svg"), W, H, *f)


if __name__ == "__main__":
    fig_tradeoff_curve()
    fig_need_time()
    fig_operating_window()
    fig_overfilter()
    fig_filter_strength_comparison()
    fig_escape_routes()
    print("OK: 6 figures ->", IMG)
