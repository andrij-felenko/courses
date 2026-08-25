# -*- coding: utf-8 -*-
"""Фігури для book/math/real-analysis/convolution/convolution.md
Генерує SVG у ./img/  Запуск: python figs.py
Імпортує спільний svgkit зі scripts/ (не переписувати примітиви).
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# F1 — Механіка згортки: відбий ядро, посунь, перемнож, додай.
# Три вертикальні панелі однієї дії на одному зсуві:
#   (а) сигнал і відбите ядро, накладені;
#   (б) поточкові добутки під накладкою;
#   (в) їх сума → одна точка результату.
# ─────────────────────────────────────────────────────────────────────────────
def fig_mechanics():
    W, H = 680, 430
    frags = []
    frags.append(text(W / 2, 24, "Згортка в одній точці: відбий ядро · посунь · перемнож · додай",
                      size=16, bold=True))

    # дискретні стовпчики сигналу x[n] та ядра h[n]
    xs = [1.0, 3.0, 2.5, 4.0, 2.0, 1.0]          # сигнал
    h  = [0.5, 1.0, 0.25]                          # ядро (буде відбите)
    h_rev = h[::-1]                                # відбите ядро

    bw = 30          # ширина стовпчика
    gap = 8          # зазор
    pitch = bw + gap
    base_x = 70      # лівий край осі n

    def bar_x(i):
        return base_x + i * pitch

    # ── Панель А: накладка сигналу й відбитого ядра на зсуві m=3
    oyA = 150
    hmaxA = 70.0
    sc = hmaxA / 4.0   # 4.0 — макс сигналу
    frags.append(text(base_x - 14, oyA - hmaxA - 14, "значення", size=11, color=MUTED, anchor="start"))
    frags.append(line(base_x - 12, oyA, bar_x(len(xs)) + 4, oyA, color=INK, sw=1.4))
    frags.append(text(bar_x(len(xs)) + 8, oyA + 4, "n", size=12, color=INK, anchor="start"))

    # стовпчики сигналу (сірі/зелені)
    for i, v in enumerate(xs):
        hgt = v * sc
        frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="#d1fae5" stroke="%s" stroke-width="1.3"/>'
                     % (bar_x(i), oyA - hgt, bw, hgt, FIELD))
        frags.append(text(bar_x(i) + bw / 2, oyA + 15, str(i), size=10, color=MUTED))

    # відбите ядро, прикладене вікном до позицій m-2,m-1,m (m=3)
    m = 3
    win = [m - 2, m - 1, m]   # три позиції, які накриває ядро
    for j, pos in enumerate(win):
        hv = h_rev[j]
        hgt = hv * hmaxA   # ядро в [0..1] масштабуємо до тієї ж осі (1.0 → hmaxA/?), нормуємо нижче
    # намалюємо відбите ядро окремими тонкими стовпчиками поверх (синій контур), у своєму масштабі
    ksc = hmaxA / 1.0 * 0.6
    for j, pos in enumerate(win):
        hv = h_rev[j]
        hgt = hv * ksc
        cx = bar_x(pos) + bw / 2
        frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="4,3"/>'
                     % (cx - 9, oyA - hgt, 18, hgt, NEG))
        frags.append(text(cx, oyA - hgt - 5, "%.2g" % hv, size=9, color=NEG))
    frags.append(text(bar_x(win[1]) + bw / 2, oyA - hmaxA - 2, "відбите ядро (ковзає)", size=10, color=NEG))

    # легенда панелі А
    frags.append(text(base_x - 14, oyA + 34, "(а) сигнал × накладене відбите ядро на зсуві m=3",
                      size=11, color=INK, anchor="start"))

    # ── Панель Б: поточкові добутки
    oyB = 300
    frags.append(line(base_x - 12, oyB, bar_x(len(xs)) + 4, oyB, color=INK, sw=1.2))
    prods = []
    for j, pos in enumerate(win):
        p = xs[pos] * h_rev[j]
        prods.append(p)
        hgt = p * (60.0 / 4.0)   # макс добуток ~4
        cx = bar_x(pos)
        frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="#fdecea" stroke="%s" stroke-width="1.3"/>'
                     % (cx, oyB - hgt, bw, hgt, POS))
        frags.append(text(cx + bw / 2, oyB - hgt - 5, "%.2f" % p, size=10, color=POS))
    frags.append(text(base_x - 14, oyB + 22, "(б) поточкові добутки x[k]·h[m−k]",
                      size=11, color=INK, anchor="start"))

    # ── Панель В: сума → одна точка результату
    s = sum(prods)
    bx = bar_x(win[1]) + bw / 2
    box, bwid, bhei = textbox(W - 150, 350,
                              "сума =\n%.2f" % s,
                              size=15, fill="#eef2ff", stroke=NEG, sw=2, min_w=120)
    frags.append(box)
    frags.append(arrow(bar_x(win[2]) + bw + 6, oyB - 20, W - 150 - bwid / 2 - 6, 350, color=MUTED, sw=1.6))
    frags.append(text(W - 150, 350 - bhei / 2 - 8, "y[3]  ←  одна точка результату", size=11, color=NEG))

    render(os.path.join(OUT, "mechanics.svg"), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# F2 — Ковзне накладання даає всю криву результату.
# Зверху сигнал-сходинка, що проходить крізь «розмазувальне» ядро,
# знизу — згладжений результат; вертикальні лінії показують, що кожна
# точка виходу — зважена сума околу входу.
# ─────────────────────────────────────────────────────────────────────────────
def fig_sliding():
    W, H = 680, 360
    frags = []
    frags.append(text(W / 2, 24, "Ковзне зважене накладання: кожна точка виходу — середнє околу входу",
                      size=15, bold=True))

    ox, oy_in = 60, 150
    aw = 540
    # вхід: сходинка з шумом-зубцями
    import random
    random.seed(7)
    N = 120
    def step(i):
        t = i / N
        base = 0.0 if t < 0.35 else (60.0 if t < 0.7 else 25.0)
        return base
    xin = [step(i) for i in range(N + 1)]
    # додамо невеликі зубці
    xin = [v + (8 if (i % 9 == 0) else (-6 if i % 7 == 0 else 0)) for i, v in enumerate(xin)]

    # вісь входу
    frags.append(line(ox, oy_in, ox + aw, oy_in, color=MUTED, sw=1.2))
    frags.append(text(ox - 8, oy_in - 70, "вхід", size=11, color=MUTED, anchor="end"))
    pts_in = " ".join("%.1f,%.1f" % (ox + i * aw / N, oy_in - xin[i]) for i in range(N + 1))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (pts_in, MUTED))

    # ковзне вікно (ядро) — прямокутник шириною w, ковзає; малюємо у двох позиціях
    kw = 14   # півширина у відліках
    def smooth(i):
        lo, hi = max(0, i - kw), min(N, i + kw)
        return sum(xin[lo:hi + 1]) / (hi - lo + 1)
    yout = [smooth(i) for i in range(N + 1)]

    # позначка вікна на одній позиції (біля сходинки)
    pi = 42
    wx0 = ox + (pi - kw) * aw / N
    wx1 = ox + (pi + kw) * aw / N
    frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="#eef2ff" stroke="%s" stroke-width="1.6" stroke-dasharray="4,3"/>'
                 % (wx0, oy_in - 78, wx1 - wx0, 84, NEG))
    frags.append(text((wx0 + wx1) / 2, oy_in - 84, "вікно ядра", size=10, color=NEG))

    # вісь виходу
    oy_out = 300
    frags.append(line(ox, oy_out, ox + aw, oy_out, color=MUTED, sw=1.2))
    frags.append(text(ox - 8, oy_out - 70, "вихід", size=11, color=FIELD, anchor="end"))
    pts_out = " ".join("%.1f,%.1f" % (ox + i * aw / N, oy_out - yout[i]) for i in range(N + 1))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (pts_out, FIELD))

    # стрілка: вікно входу → одна точка виходу
    cx = ox + pi * aw / N
    frags.append(arrow(cx, oy_in + 6, cx, oy_out - yout[pi] - 6, color=POS, sw=1.6))
    frags.append(circle(cx, oy_out - yout[pi], 4, fill=POS, stroke=INK, sw=1))
    frags.append(text(cx + 6, (oy_in + oy_out) / 2, "зважене середнє", size=10, color=POS, anchor="start"))

    frags.append(text(W / 2, H - 8,
                      "Різкі зубці й стрибок згладжено: ядро розмазало кожну точку по сусідах",
                      size=10, color=MUTED))
    render(os.path.join(OUT, "sliding.svg"), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# F3 — Лінійна система: вхід = сума зважених імпульсів,
# вихід = сума зважених копій імпульсної характеристики. Це і є згортка.
# ─────────────────────────────────────────────────────────────────────────────
def fig_impulse():
    W, H = 680, 380
    frags = []
    frags.append(text(W / 2, 24, "Чому згортка: кожен відлік входу запускає копію відгуку системи",
                      size=15, bold=True))

    ox = 55
    oy = 150
    # три вхідні імпульси різної висоти
    imp = [(0, 1.0), (3, 2.0), (5, 0.6)]
    pitch = 26
    frags.append(line(ox, oy, ox + 8 * pitch, oy, color=MUTED, sw=1.2))
    frags.append(text(ox + 8 * pitch + 6, oy + 4, "n", size=11, color=MUTED, anchor="start"))
    frags.append(text(ox, oy - 90, "вхід = окремі імпульси", size=11, color=INK, anchor="start"))
    for k, a in imp:
        hgt = a * 30
        cx = ox + k * pitch + pitch / 2
        frags.append(line(cx, oy, cx, oy - hgt, color=NEG, sw=2.4))
        frags.append(circle(cx, oy - hgt, 3.5, fill=NEG, stroke=INK, sw=1))
        frags.append(text(cx, oy - hgt - 6, "%.1f" % a, size=9, color=NEG))

    # система-рамка
    sysbox, sw_, sh_ = textbox(W / 2, oy + 70, "лінійна система\n(відгук h)", size=12,
                               fill="#fff7ed", stroke="#b45309", sw=1.8, min_w=150)
    frags.append(sysbox)
    frags.append(arrow(ox + 4 * pitch, oy + 28, W / 2 - sw_ / 2 - 6, oy + 70, color=MUTED, sw=1.5))

    # вихід праворуч: три зсунуті масштабовані копії h + їх сума
    ox2 = 370
    oy2 = 150
    frags.append(line(ox2, oy2, ox2 + 11 * pitch, oy2, color=MUTED, sw=1.2))
    frags.append(text(ox2 + 11 * pitch + 6, oy2 + 4, "n", size=11, color=MUTED, anchor="start"))
    frags.append(text(ox2, oy2 - 90, "вихід = сума копій відгуку", size=11, color=INK, anchor="start"))

    # форма відгуку h (нормований сплеск, що згасає)
    hshape = [0.0, 0.8, 1.0, 0.6, 0.3, 0.1]
    def copy_curve(k0, a):
        pts = []
        for j, hv in enumerate(hshape):
            x = ox2 + (k0 + j) * pitch + pitch / 2
            pts.append((x, oy2 - a * hv * 30))
        return pts

    colors = ["#93c5fd", "#86efac", "#fca5a5"]
    # сума у точках
    total = {}
    for (k, a), col in zip(imp, colors):
        cv = copy_curve(k, a)
        pstr = " ".join("%.1f,%.1f" % p for p in cv)
        frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="4,3"/>' % (pstr, col))
        for j, hv in enumerate(hshape):
            total[k + j] = total.get(k + j, 0.0) + a * hv

    # жирна сумарна крива
    keys = sorted(total)
    sumpts = " ".join("%.1f,%.1f" % (ox2 + kk * pitch + pitch / 2, oy2 - total[kk] * 30) for kk in keys)
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (sumpts, INK))
    frags.append(text(ox2 + 95, oy2 - 82, "сума копій", size=10, color=INK))
    frags.append(text(ox2 + 95, oy2 - 68, "= згортка x∗h", size=10, color=INK, bold=True))

    frags.append(arrow(W / 2 + sw_ / 2 + 6, oy + 70, ox2 + 2 * pitch, oy2 + 30, color=MUTED, sw=1.5))

    # підпис-висновок
    frags.append(text(W / 2, H - 12,
                      "Накласти зважені зсунуті копії відгуку — це дослівно операція згортки",
                      size=10, color=MUTED))
    render(os.path.join(OUT, "impulse-response.svg"), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# F4 — Теорема згортки: згортка в часі ⇄ множення спектрів.
# ─────────────────────────────────────────────────────────────────────────────
def fig_theorem():
    W, H = 620, 230
    frags = []
    frags.append(text(W / 2, 26, "Теорема згортки: важка згортка в часі = просте множення у спектрі",
                      size=14, bold=True))

    # верхній ряд — час
    yT = 95
    b1, w1, h1 = textbox(120, yT, "x(t) ∗ h(t)", size=15, fill="#d1fae5", stroke=FIELD, sw=2, min_w=150)
    frags.append(b1)
    b2, w2, h2 = textbox(500, yT, "y(t)", size=15, fill="#d1fae5", stroke=FIELD, sw=2, min_w=150)
    frags.append(b2)
    frags.append(arrow(120 + w1 / 2 + 8, yT, 500 - w2 / 2 - 8, yT, color=INK, sw=2))
    frags.append(text(310, yT - 12, "згортка (дорого)", size=12, color=INK))

    # нижній ряд — частота
    yF = 180
    b3, w3, h3 = textbox(120, yF, "X(f) · H(f)", size=15, fill="#eef2ff", stroke=NEG, sw=2, min_w=150)
    frags.append(b3)
    b4, w4, h4 = textbox(500, yF, "Y(f)", size=15, fill="#eef2ff", stroke=NEG, sw=2, min_w=150)
    frags.append(b4)
    frags.append(arrow(120 + w3 / 2 + 8, yF, 500 - w4 / 2 - 8, yF, color=NEG, sw=2))
    frags.append(text(310, yF - 12, "просте множення", size=12, color=NEG))

    # вертикальні стрілки — перетворення Фур'є
    frags.append(arrow(120, yT + h1 / 2 + 4, 120, yF - h3 / 2 - 4, color=MUTED, sw=1.6))
    frags.append(text(126, (yT + yF) / 2 + 4, "Фур'є", size=10, color=MUTED, anchor="start"))
    frags.append(arrow(500, yF - h4 / 2 - 4, 500, yT + h2 / 2 + 4, color=MUTED, sw=1.6))
    frags.append(text(506, (yT + yF) / 2 + 4, "назад", size=10, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "convolution-theorem.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_mechanics()
    fig_sliding()
    fig_impulse()
    fig_theorem()
    print("Done — 4 SVG written to", OUT)
