# -*- coding: utf-8 -*-
"""Фігури до ДЕТАЛЬНОЇ статті «Вибір фільтра» (choosing-a-filter-d.md).
Окремий генератор, щоб не чіпати базовий figs.py; вивід — той самий ./img/,
але імена файлів мають суфікс -d (не перетинаються з базовими).
Запуск:  python figs-d.py
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

import math, random

MED = "#8e44ad"      # медіана
GOLD = "#b9770e"     # калібрування / дрейф


# ── 1. Крива компромісу в числах: шум ÷√N проти затримки ─────────────────────
def fig_cost_frontier():
    """Квадратична ціна тиші: щоб удвічі тихіше — вчетверо довше чекати."""
    W, H = 760, 430
    f = [text(W / 2, 26, "Ціна тиші: шум спадає як 1/√N, затримка росте як N", size=15, bold=True)]

    ox, oy = 100, 360          # початок координат
    aw, ah = 590, 296          # довжина осей
    f.append(line(ox, oy, ox + aw, oy, color=INK, sw=2))      # X: затримка
    f.append(line(ox, oy, ox, oy - ah, color=INK, sw=2))      # Y: рівень шуму
    f.append(text(ox + aw / 2, oy + 38, "групова затримка ≈ N/2 відліків  →", size=11.5, color=MUTED))
    f.append(text(ox - 74, oy - ah / 2 - 6, "залишковий", size=11, color=MUTED, anchor="middle"))
    f.append(text(ox - 74, oy - ah / 2 + 10, "шум (частка)", size=11, color=MUTED, anchor="middle"))

    Ns = [1, 2, 4, 9, 16, 25, 36, 49, 64]
    dmax = (Ns[-1] - 1) / 2
    def X(d): return ox + aw * d / dmax
    def Y(v): return oy - ah * v
    pts = []
    for N in Ns:
        d = (N - 1) / 2
        v = 1.0 / math.sqrt(N)
        pts.append((X(d), Y(v), N, v))
    poly = " ".join("%.1f,%.1f" % (p[0], p[1]) for p in pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
             'stroke-linejoin="round"/>' % (poly, FIELD))
    for x, y, N, v in pts:
        f.append(circle(x, y, 4, fill=BG, stroke=FIELD, sw=2))

    def mark(N, label, dx, dy):
        d = (N - 1) / 2
        x, y = X(d), Y(1.0 / math.sqrt(N))
        f.append(circle(x, y, 5.5, fill=POS, stroke=POS, sw=1))
        f.append(text(x + dx, y + dy, label, size=10.5, color=INK, anchor="start"))
    mark(4, "N=4 → шум ÷2, затримка ≈1.5", 10, -10)
    mark(16, "N=16 → шум ÷4, затримка ≈7.5", 10, -10)
    mark(64, "N=64 → шум ÷8, затримка ≈31.5", -180, 22)

    f.append(text(W / 2, 414,
                  "половина шуму коштує вчетверо довшого чекання — «ще трохи чистіше» дороге",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "cost-frontier-d.svg"), W, H, *f)


# ── Спільна панель-графік ────────────────────────────────────────────────────
def _panel(f, x, y, w, h, color, label, pts, note=None):
    f.append(rect(x, y, w, h, fill="#fcfcfd", stroke="#e6e6ea", sw=1.4))
    f.append(text(x + w / 2, y + 20, label, size=12, color=color, bold=True))
    poly = " ".join("%.1f,%.1f" % p for p in pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" '
             'stroke-linejoin="round" stroke-linecap="round"/>' % (poly, color))
    if note:
        f.append(text(x + w / 2, y + h - 8, note, size=9.5, color=MUTED, italic=True))


# ── 2. Медіана проти середнього на краю й спайку ─────────────────────────────
def fig_median_vs_mean_edge():
    """Крок + спайк: середнє розмиває обидва, медіана(5) береже край і вбиває спайк."""
    W, H = 780, 300
    f = [text(W / 2, 26, "Крок і спайк: середнє розмиває, медіана(5) береже край", size=15, bold=True)]

    n = 40
    def truth(i): return 0.0 if i < n // 2 else 1.0
    raw = []
    for i in range(n):
        v = truth(i)
        if i == 14:
            v += 1.5
        raw.append(v)

    def sma(series, N):
        out = []
        for i in range(len(series)):
            lo = max(0, i - N + 1)
            win = series[lo:i + 1]
            out.append(sum(win) / len(win))
        return out
    def med(series, N):
        out = []
        h = N // 2
        for i in range(len(series)):
            lo, hi = max(0, i - h), min(len(series), i + h + 1)
            win = sorted(series[lo:hi])
            out.append(win[len(win) // 2])
        return out

    ma = sma(raw, 5)
    mo = med(raw, 5)

    py, pw, ph = 46, 232, 214
    def to_pts(series, x0):
        lo, hi = -0.15, 1.7
        out = []
        for i, v in enumerate(series):
            xx = x0 + 14 + (pw - 28) * i / (n - 1)
            yy = (py + ph - 34) - (v - lo) / (hi - lo) * (ph - 66)
            out.append((xx, yy))
        return out

    _panel(f, 30, py, pw, ph, POS, "сирий: крок + спайк", to_pts(raw, 30),
           "спайк 1.5, крок посередині")
    _panel(f, 274, py, pw, ph, FIELD, "ковзне середнє(5)", to_pts(ma, 274),
           "спайк розмазано, край похилий")
    _panel(f, 518, py, pw, ph, MED, "медіана(5)", to_pts(mo, 518),
           "спайк зник, край різкий")

    render(os.path.join(IMG, "median-vs-mean-edge-d.svg"), W, H, *f)


# ── 3. Порядок у каскаді: медіана→середнє проти середнє→медіана ──────────────
def fig_cascade_order():
    """Той самий спайк, дві черги ланок — різний результат."""
    W, H = 780, 310
    f = [text(W / 2, 26, "Порядок ланок важить: медіана має стояти ПЕРШОЮ", size=15, bold=True)]

    n = 34
    raw = [0.5 + (0.02 if i % 2 else -0.02) for i in range(n)]   # рівний дрібний шум
    raw[16] = 3.2                                                # один дикий спайк

    def sma3(series):
        out = []
        for i in range(len(series)):
            lo = max(0, i - 2)
            win = series[lo:i + 1]
            out.append(sum(win) / len(win))
        return out
    def med3(series):
        out = [series[0]]
        for i in range(1, len(series) - 1):
            out.append(sorted(series[i - 1:i + 2])[1])
        out.append(series[-1])
        return out

    good = sma3(med3(raw))      # медіана → середнє (правильно)
    bad = med3(sma3(raw))       # середнє → медіана (спайк уже розмазаний)

    py, pw, ph = 48, 232, 224
    def to_pts(series, x0):
        lo, hi = 0.2, 3.4
        out = []
        for i, v in enumerate(series):
            xx = x0 + 14 + (pw - 28) * i / (n - 1)
            yy = (py + ph - 34) - (v - lo) / (hi - lo) * (ph - 66)
            out.append((xx, yy))
        return out

    _panel(f, 30, py, pw, ph, POS, "сирий: спайк 3.2", to_pts(raw, 30),
           "один дикий викид")
    _panel(f, 274, py, pw, ph, FIELD, "медіана(3) → середнє(3)", to_pts(good, 274),
           "спайк вибито ДО усереднення — чисто")
    _panel(f, 518, py, pw, ph, GOLD, "середнє(3) → медіана(3)", to_pts(bad, 518),
           "спайк розмазало — горб лишився")

    render(os.path.join(IMG, "cascade-order-d.svg"), W, H, *f)


# ── 4. Пастка цілочислової EMA: округлення до нуля «підвисає» ─────────────────
def fig_fixedpoint_ema():
    """int-EMA `y += (x−y)>>k`: різниця <2^k дає 0 → вихід застрягає, не доходить."""
    W, H = 760, 340
    f = [text(W / 2, 26, "Пастка цілочислової EMA: округлення вниз «підвисає»", size=15, bold=True)]

    ox, oy = 70, 280
    aw, ah = 620, 220
    f.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.8))
    f.append(line(ox, oy, ox, oy - ah, color=INK, sw=1.8))
    f.append(text(ox + aw / 2, oy + 36, "відлік  →", size=11, color=MUTED))
    f.append(text(ox - 42, oy - ah / 2, "значення", size=11, color=MUTED, anchor="middle"))

    n = 60
    target = 100.0
    lo, hi = 0.0, 110.0
    def X(i): return ox + aw * i / (n - 1)
    def Y(v): return oy - ah * (v - lo) / (hi - lo)

    # ціль (сходинка на 100)
    f.append(line(X(0), Y(target), X(n - 1), Y(target), color=MUTED, sw=1.4, dash="4 4"))
    f.append(text(X(n - 1) - 6, Y(target) - 8, "ціль = 100", size=10, color=MUTED, anchor="end"))

    # правильна (float) EMA, α = 1/8
    yf = 0.0
    pf = []
    for i in range(n):
        yf += (target - yf) / 8.0
        pf.append((X(i), Y(yf)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
             % (" ".join("%.1f,%.1f" % p for p in pf), FIELD))

    # наївна ціла EMA: y += (x−y)>>3  (ділення з відкиданням дробу)
    yi = 0
    pi = []
    stuck_at = None
    for i in range(n):
        diff = int(target) - yi
        step = diff >> 3 if diff >= 0 else -((-diff) >> 3)
        yi += step
        pi.append((X(i), Y(yi)))
        if step == 0 and stuck_at is None:
            stuck_at = yi
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join("%.1f,%.1f" % p for p in pi), POS))

    # позначити стелю застрягання
    if stuck_at is not None:
        f.append(line(X(0), Y(stuck_at), X(n - 1), Y(stuck_at), color=POS, sw=1.1, dash="2 3"))
        f.append(text(X(n - 1) - 6, Y(stuck_at) + 16, "ціла EMA застрягла на %d" % stuck_at,
                      size=10, color=POS, anchor="end"))

    # легенда
    f.append(line(ox + 20, 60, ox + 46, 60, color=FIELD, sw=2.2))
    f.append(text(ox + 52, 64, "float EMA — доходить до 100", size=10.5, color=INK, anchor="start"))
    f.append(line(ox + 20, 78, ox + 46, 78, color=POS, sw=2.4))
    f.append(text(ox + 52, 82, "наївна ціла EMA (>>3) — не доходить", size=10.5, color=INK, anchor="start"))

    f.append(text(W / 2, 326,
                  "коли (x−y) < 2ᵏ, зсув дає 0 — вихід стоїть; лік дробу в стані рятує це",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "fixedpoint-ema-d.svg"), W, H, *f)


if __name__ == "__main__":
    fig_cost_frontier()
    fig_median_vs_mean_edge()
    fig_cascade_order()
    fig_fixedpoint_ema()
    print("OK: 4 figures ->", IMG)
