# -*- coding: utf-8 -*-
"""Фігури до теми «КІХ-фільтр».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

import math

TAP = "#9a4ea8"   # «вікняні» (згладжені) відводи — фіолетова лінія


# ── 1. Будова КІХ: лінія затримки → відводи → суматор ────────────────────────
def fig_structure():
    W, H = 740, 250
    f = [text(W / 2, 26, "Будова КІХ: лінія затримки → відводи → суматор", size=15, bold=True)]

    cells = ["x[n]", "x[n−1]", "x[n−2]", "x[n−3]"]
    cx0, cw, gap, cy = 64, 90, 30, 80
    centers = []
    for i, name in enumerate(cells):
        x = cx0 + i * (cw + gap)
        centers.append(x + cw / 2)
        col = FIELD if i == 0 else NEG
        f.append(rect(x, cy - 18, cw, 36, fill=FILL, stroke=col, sw=1.6))
        f.append(text(x + cw / 2, cy + 5, name, size=12, color=col, bold=True))
        if i < len(cells) - 1:
            ax = x + cw
            f.append(line(ax, cy, ax + gap, cy, color=INK, sw=1.6, ))
            f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
                     % (ax + gap, cy, ax + gap - 7, cy - 4, ax + gap - 7, cy + 4, INK))
            f.append(text(ax + gap / 2, cy - 8, "z⁻¹", size=10, color=MUTED, italic=True))

    # відводи: множники вниз до спільної шини суматора
    bus_y = 192
    sum_cx = centers[-1] + 80
    f.append(line(centers[0], bus_y, sum_cx - 20, bus_y, color=FIELD, sw=1.3))
    for i, c in enumerate(centers):
        f.append(line(c, cy + 18, c, bus_y - 12, color=FIELD, sw=1.4))
        f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
                 % (c, bus_y, c - 4, bus_y - 8, c + 4, bus_y - 8, FIELD))
        f.append(circle(c, 148, 12, fill=BG, stroke=FIELD, sw=1.5))
        f.append(text(c, 152, "×", size=11, color=FIELD, bold=True))
        f.append(text(c + 16, 152, "b%s" % "₀₁₂₃"[i], size=11, color=FIELD, bold=True,
                      anchor="start"))

    # суматор
    f.append(circle(sum_cx, bus_y, 20, fill="#eaf6ef", stroke=INK, sw=1.8))
    f.append(text(sum_cx, bus_y + 6, "Σ", size=17, color=INK, bold=True))
    f.append(line(sum_cx + 20, bus_y, sum_cx + 80, bus_y, color=INK, sw=2))
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
             % (sum_cx + 80, bus_y, sum_cx + 72, bus_y - 4, sum_cx + 72, bus_y + 4, INK))
    f.append(text(sum_cx + 88, bus_y + 5, "y[n]", size=13, color=INK, bold=True, anchor="start"))

    f.append(text(W / 2, 234,
                  "y[n] = b₀·x[n] + b₁·x[n−1] + …  — зважена сума входів, без зворотного зв'язку",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "structure.svg"), W, H, *f)


# ── 2. Імпульс на вході → коефіцієнти на виході, тоді нуль ────────────────────
def _stem(f, x, base, h, color, dot=True):
    f.append(line(x, base, x, base - h, color=color, sw=3))
    if dot and h > 0:
        f.append(circle(x, base - h, 3, fill=color, stroke=color, sw=0))


def fig_impulse():
    W, H = 720, 250
    f = [text(W / 2, 26, "Імпульс на вході → коефіцієнти на виході", size=15, bold=True)]

    base = 150
    # вхід: один ненульовий відлік
    f.append(line(50, base, 290, base, color="#e4e4e4", sw=1.2))
    xs_in = [64 + 30 * i for i in range(8)]
    _stem(f, xs_in[0], base, 88, NEG)
    for x in xs_in[1:]:
        _stem(f, x, base, 0, NEG, dot=False)
    f.append(text(170, base + 34, "вхід: імпульс (1, 0, 0…)", size=10, color=NEG, bold=True))

    # стрілка через фільтр
    f.append(line(312, base - 10, 356, base - 10, color=INK, sw=2))
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
             % (362, base - 10, 354, base - 14, 354, base - 6, INK))
    f.append(text(337, base - 22, "КІХ", size=10, color=MUTED, bold=True))

    # вихід: коефіцієнти, тоді нуль
    f.append(line(384, base, 624, base, color="#e4e4e4", sw=1.2))
    coeffs = [18, 45, 72, 45, 18, 0, 0, 0]
    xs_out = [398 + 30 * i for i in range(8)]
    for x, h in zip(xs_out, coeffs):
        _stem(f, x, base, h, FIELD, dot=(h > 0))
    f.append(text(504, base + 34, "вихід: коефіцієнти b₀…b_M, тоді 0", size=10, color=FIELD, bold=True))

    f.append(text(W / 2, 236,
                  "реакція на імпульс скінченна — рівно M+1 відліків; вони ж і є коефіцієнти",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "impulse.svg"), W, H, *f)


# ── 3. Форма відводів формує характеристику ──────────────────────────────────
def fig_taps_shape():
    W, H = 720, 320
    f = [text(W / 2, 24, "Форма відводів формує характеристику", size=15, bold=True)]

    def panel(x0, label, col, heights, resp):
        f.append(text(x0 + 130, 56, label, size=10, color=col, bold=True))
        # відводи-стовпчики
        sb = 80
        f.append(line(x0, sb, x0 + 260, sb, color="#e4e4e4", sw=1))
        nb = len(heights)
        for i, h in enumerate(heights):
            xx = x0 + 18 + (260 - 36) * i / (nb - 1)
            f.append(line(xx, sb, xx, sb - h, color=col, sw=4))
        # вісь характеристики
        ax_x, ax_yb, ax_yt = x0, 250, 120
        f.append(line(ax_x, ax_yb, ax_x, ax_yt, color=INK, sw=1.4))
        f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
                 % (ax_x, ax_yt - 6, ax_x - 4, ax_yt + 2, ax_x + 4, ax_yt + 2, INK))
        f.append(line(ax_x, ax_yb, ax_x + 268, ax_yb, color=INK, sw=1.4))
        f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
                 % (ax_x + 268 + 6, ax_yb, ax_x + 268 - 2, ax_yb - 4, ax_x + 268 - 2, ax_yb + 4, INK))
        # характеристика
        n = len(resp)
        pts = []
        for i, v in enumerate(resp):
            xx = ax_x + 260 * i / (n - 1)
            yy = ax_yb - v * (ax_yb - 130)
            pts.append((xx, yy))
        poly = " ".join("%.1f,%.1f" % p for p in pts)
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" '
                 'stroke-linejoin="round" stroke-linecap="round"/>' % (poly, col))
        f.append(text(x0 + 130, 266, "характеристика", size=9, color=MUTED, italic=True))

    # ліва панель: рівні відводи → груба характеристика з горбиками
    flat = [26] * 8

    def sinc_mag(t, lobes, ripple):
        # |sin/x|-подібна форма з бічними горбиками; t у [0..1]
        x = (t - 0.0) * lobes * math.pi
        if abs(x) < 1e-6:
            base = 1.0
        else:
            base = abs(math.sin(x) / x)
        return base

    resp_flat = []
    N = 120
    for i in range(N):
        t = i / (N - 1)
        v = sinc_mag(t, 7.5, 1.0)
        # горбики не гаснуть швидко (груба)
        resp_flat.append(min(1.0, v))

    # права панель: дзвоноподібні відводи → чистіша характеристика
    bell = [int(26 * math.exp(-((i - 3.5) ** 2) / 4.5)) + 2 for i in range(8)]
    resp_bell = []
    for i in range(N):
        t = i / (N - 1)
        v = sinc_mag(t, 6.0, 1.0)
        # горбики гасимо вікном (чистіша) — множимо на спадний конверт
        env = math.exp(-3.0 * t)
        main = math.exp(-((t) ** 2) * 16)  # головна пелюстка
        vv = main + 0.12 * v * env
        resp_bell.append(min(1.0, vv))

    panel(40, "рівні відводи (ковзне середнє)", FIELD, flat, resp_flat)
    panel(400, "згладжені відводи (вікно)", TAP, bell, resp_bell)
    render(os.path.join(IMG, "taps-shape.svg"), W, H, *f)


# ── 4. Лінійна фаза: вихід = вхід, лише зсунутий ─────────────────────────────
def fig_linear_phase():
    W, H = 720, 250
    f = [text(W / 2, 26, "Лінійна фаза: вихід = вхід, лише зсунутий", size=15, bold=True)]

    mid = 140
    f.append(line(70, mid, 650, mid, color="#e4e4e4", sw=1.0))

    # складний сигнал: дві гармоніки
    def sig(t):
        return (math.sin(2 * math.pi * 1.3 * t) + 0.5 * math.sin(2 * math.pi * 2.7 * t + 0.6))

    N = 300
    x0, x1 = 70.0, 650.0
    amp = 30.0
    shift_t = 0.18  # зсув у долях вікна (M/2)

    def curve(off, color, dash=None):
        pts = []
        for i in range(N):
            t = i / (N - 1)
            xx = x0 + (x1 - x0) * t
            yy = mid - amp * sig(t - off) / 1.5
            pts.append((xx, yy))
        poly = " ".join("%.1f,%.1f" % p for p in pts)
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0" '
                 'stroke-linejoin="round" stroke-linecap="round"%s/>' % (poly, color, d))

    curve(0.0, NEG)
    curve(shift_t, FIELD, dash="6,3")
    f.append(text(150, 82, "вхід", size=10, color=NEG, bold=True, anchor="start"))
    f.append(text(330, 200, "вихід (зсув M/2, форма ціла)", size=10, color=FIELD, bold=True, anchor="start"))

    # позначка зсуву
    sx0 = x0 + (x1 - x0) * 0.35
    sx1 = sx0 + (x1 - x0) * shift_t
    f.append(line(sx0, 96, sx1, 96, color=POS, sw=1.4))
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
             % (sx1, 96, sx1 - 7, 92, sx1 - 7, 100, POS))
    f.append(text((sx0 + sx1) / 2, 90, "M/2", size=9, color=POS, bold=True))

    f.append(text(W / 2, 236,
                  "симетричні коефіцієнти затримують усі частоти однаково — форма не псується",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "linear-phase.svg"), W, H, *f)


# ── 5. Реалізація: кільцевий буфер + MAC ─────────────────────────────────────
def fig_impl():
    W, H = 720, 250
    f = [text(W / 2, 26, "Реалізація КІХ: кільцевий буфер + MAC", size=14, bold=True)]

    # кільцевий буфер: 6 комірок по колу
    cx, cy, R = 170, 145, 68
    labels = ["x0", "x1", "x2", "x3", "x4", "x5"]
    for i, lab in enumerate(labels):
        a = -math.pi / 2 + i * (2 * math.pi / len(labels))
        px = cx + R * math.cos(a)
        py = cy + R * math.sin(a)
        col = FIELD if i == 0 else NEG
        f.append(circle(px, py, 18, fill=(BG if i == 0 else FILL), stroke=col, sw=1.6))
        f.append(text(px, py + 4, lab, size=9, color=col, bold=True))
    f.append(text(cx, cy + 4, "буфер", size=10, color=INK, bold=True))
    # стрілка «новий» у голову
    hx = cx + R * math.cos(-math.pi / 2)
    hy = cy + R * math.sin(-math.pi / 2)
    f.append(line(hx + 70, hy - 6, hx + 16, hy + 4, color=FIELD, sw=1.4))
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
             % (hx + 12, hy + 6, hx + 22, hy + 2, hx + 19, hy + 11, FIELD))
    f.append(text(hx + 74, hy - 8, "новий", size=9, color=FIELD, bold=True, anchor="start"))
    f.append(text(cx, cy + R + 26, "голова рухається по колу", size=9, color=MUTED, italic=True))

    # код MAC у рамці
    bx, by, bw, bh = 380, 70, 312, 150
    f.append(rect(bx, by, bw, bh, fill="#fbfbfb", stroke=INK, sw=1.4))
    f.append(text(bx + 18, by + 34, "acc = 0", size=12, color=INK, bold=True, anchor="start"))
    f.append(text(bx + 18, by + 62, "for k in 0..M:", size=12, color=NEG, bold=True, anchor="start"))
    f.append(text(bx + 18, by + 90, "    acc += b[k]·buf[k]", size=12, color=FIELD, bold=True, anchor="start"))
    f.append(text(bx + 18, by + 118, "y = acc", size=12, color=INK, bold=True, anchor="start"))
    f.append(text(bx + bw / 2, by + bh - 10, "M+1 множень-додавань на відлік",
                  size=9, color=MUTED, italic=True))
    render(os.path.join(IMG, "impl.svg"), W, H, *f)


# ── 6. Більше відводів → різкіша характеристика ──────────────────────────────
def fig_more_taps():
    W, H = 720, 280
    f = [text(W / 2, 26, "Більше відводів → різкіша характеристика", size=15, bold=True)]

    x0, x1 = 70.0, 650.0
    yb, yt = 230.0, 60.0
    f.append(line(70, yb, 70, 46, color=INK, sw=1.6))
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
             % (70, 40, 66, 48, 74, 48, INK))
    f.append(line(70, yb, 662, yb, color=INK, sw=1.6))
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
             % (668, yb, 660, yb - 4, 660, yb + 4, INK))
    f.append(text(640, yb + 18, "частота →", size=9.5, color=INK, bold=True))
    f.append(text(62, 58, "підсилення", size=10, color=INK, bold=True, anchor="end"))

    cutoff = 0.33  # частка осі, де зріз

    def lp(steep, color, label, lx):
        N = 300
        pts = []
        for i in range(N):
            t = i / (N - 1)
            # гладкий спад біля cutoff; крутість зростає зі steep
            v = 1.0 / (1.0 + math.exp((t - cutoff) * steep))
            xx = x0 + (x1 - x0) * t
            yy = yb - (yb - yt) * v
            pts.append((xx, yy))
        poly = " ".join("%.1f,%.1f" % p for p in pts)
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" '
                 'stroke-linejoin="round" stroke-linecap="round"/>' % (poly, color))
        f.append(text(lx, 73, label, size=9.5, color=color, bold=True, anchor="start"))

    lp(14, "#9a7a1e", "M=8", x0 + (x1 - x0) * 0.5)
    lp(34, NEG, "M=32", x0 + (x1 - x0) * 0.40)
    lp(80, FIELD, "M=64", x0 + (x1 - x0) * 0.27)

    f.append(text(W / 2, 266,
                  "той самий ФНЧ: більше коефіцієнтів — гостріший зріз, але дорожче й повільніше",
                  size=9, color=MUTED, italic=True))
    render(os.path.join(IMG, "more-taps.svg"), W, H, *f)


if __name__ == "__main__":
    fig_structure()
    fig_impulse()
    fig_taps_shape()
    fig_linear_phase()
    fig_impl()
    fig_more_taps()
    print("OK: 6 figures ->", IMG)
