# -*- coding: utf-8 -*-
"""Фігури для book/math/real-analysis/sampling-theorem/sampling-theorem-d.md
Генерує SVG у ./img/  Запуск: python figs.py
Імпортує спільний svgkit зі scripts/ (не переписувати примітиви).
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SPEC = "#e8eefc"   # заливка трикутника-спектра
OVER = "#fdecea"   # заливка зони накладання


def polygon(points, fill, stroke, sw=1.6):
    pts = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    return ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>'
            % (pts, fill, stroke, sw))


def polyline(points, stroke, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    pts = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (pts, stroke, sw, d))


# ─────────────────────────────────────────────────────────────────────────────
# F1 — Вибірка тиражує спектр копіями через f_s.
#   (а) смуга < f_Nyq: копії стоять окремо → відновлення точне;
#   (б) смуга > f_Nyq: сусідні копії налазять → aliasing (зона перекриття).
# ─────────────────────────────────────────────────────────────────────────────
def fig_tiling():
    W, H = 680, 452
    frags = []
    frags.append(text(W / 2, 26, "Вибірка тиражує спектр: копії через кожні f_s",
                      size=17, bold=True))

    x0 = 340          # центр базової копії (частота 0)
    FS = 150          # f_s у пікселях
    centers = [x0 - FS, x0, x0 + FS]   # −f_s, 0, +f_s
    axL, axR = 45, 635

    def tri(cx, baseY, halfW, height):
        return [(cx - halfW, baseY), (cx, baseY - height), (cx + halfW, baseY)]

    def marks(baseY, y_lab):
        out = []
        for mx, lab in [(x0 - FS, "−f_s"), (x0 - FS / 2, "−f_s/2"),
                        (x0, "0"), (x0 + FS / 2, "f_s/2"), (x0 + FS, "f_s")]:
            out.append(line(mx, baseY, mx, baseY + 5, color=INK, sw=1.2))
            out.append(text(mx, y_lab, lab, size=11, color=MUTED))
        return out

    # ── Панель А: смуга вужча за Найквіст
    frags.append(text(W / 2, 52, "(а) смуга сигналу < f_Nyq — копії стоять окремо, відновлення точне",
                      size=12, color=INK))
    baseA = 172
    frags.append(line(axL, baseA, axR, baseA, color=INK, sw=1.4))
    frags.append(text(axR + 8, baseA + 4, "f", size=12, color=INK, anchor="start", italic=True))
    frags.append(text(30, baseA + 4, "…", size=13, color=MUTED))
    frags.append(text(650, baseA + 4, "…", size=13, color=MUTED))
    hW_a = 0.35 * FS   # півширина смуги < f_s/2 → між копіями чистий проміжок
    for cx in centers:
        frags.append(polygon(tri(cx, baseA, hW_a, 72), SPEC, NEG))
    frags.append(text(x0, 92, "X(f)", size=12, color=NEG, bold=True))
    frags.append(text(x0 - FS, 92, "копія", size=11, color=MUTED))
    frags.append(text(x0 + FS, 92, "копія", size=11, color=MUTED))
    frags.extend(marks(baseA, 192))

    # ── Панель Б: смуга ширша за Найквіст
    frags.append(text(W / 2, 262, "(б) смуга сигналу > f_Nyq — сусідні копії налазять, це й є aliasing",
                      size=12, color=INK))
    baseB = 382
    hW_b = 0.68 * FS   # півширина > f_s/2 → сусіди перекриваються
    ht = 72
    # спершу трикутники-копії
    for cx in centers:
        frags.append(polygon(tri(cx, baseB, hW_b, ht), SPEC, NEG))
    # зони перекриття (де обидві копії присутні) — маленькі трикутники з вершиною на перетині граней
    slope = ht / hW_b
    dxov = hW_b - FS / 2.0      # горизонтальний «наліз» з кожного боку
    yov = baseB - slope * dxov
    for mid in [x0 - FS / 2, x0 + FS / 2]:
        frags.append(polygon([(mid - dxov, baseB), (mid + dxov, baseB), (mid, yov)],
                             OVER, POS, sw=1.4))
    frags.append(text(x0, 302, "X(f)", size=12, color=NEG, bold=True))
    frags.append(text(x0 - FS, 302, "копія", size=11, color=MUTED))
    frags.append(text(x0 + FS, 302, "копія", size=11, color=MUTED))
    frags.extend(marks(baseB, 402))
    frags.append(text(W / 2, 432,
                      "Червоне — зона накладання: там частоти вже невідрізненні",
                      size=11, color=POS))

    render(os.path.join(OUT, "spectrum-tiling.svg"), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# F2 — Aliasing: швидка синусоїда і її повільний аліас проходять через ТІ САМІ проби.
# true = cos(2π·0.7·n),  alias = cos(2π·0.3·n) — рівні в кожному цілому n.
# ─────────────────────────────────────────────────────────────────────────────
def fig_aliasing():
    W, H = 680, 292
    frags = []
    frags.append(text(W / 2, 26, "Одні проби — дві хвилі: висока частота прикидається низькою",
                      size=16, bold=True))

    # легенда
    frags.append(line(70, 48, 90, 48, color=POS, sw=3))
    frags.append(text(96, 52, "справжня хвиля (частота 0.7)", size=12, color=POS, anchor="start"))
    frags.append(line(400, 48, 420, 48, color=NEG, sw=3))
    frags.append(text(426, 52, "аліас (0.3)", size=12, color=NEG, anchor="start"))

    axis = 150
    x0, dx = 80, 60          # перша проба і крок між пробами
    N = 8                    # проб буде N+1
    A = 55                   # амплітуда в пікселях
    axL, axR = 60, x0 + N * dx + 20

    frags.append(line(axL, axis, axR, axis, color=INK, sw=1.3))
    frags.append(text(axR + 8, axis + 4, "t", size=12, color=INK, anchor="start", italic=True))

    def curve(freq, color):
        pts = []
        steps = 400
        for i in range(steps + 1):
            t = N * i / steps
            x = x0 + t * dx
            y = axis - A * math.cos(2 * math.pi * freq * t)
            pts.append((x, y))
        return polyline(pts, color, sw=2.2)

    frags.append(curve(0.7, POS))
    frags.append(curve(0.3, NEG))

    # проби — спільні точки обох кривих
    for n in range(N + 1):
        x = x0 + n * dx
        y = axis - A * math.cos(2 * math.pi * 0.3 * n)
        frags.append(circle(x, y, 4.2, fill=INK, stroke=BG, sw=1.5))

    # брекет «крок d» під кривими
    by = 232
    frags.append(line(x0, by, x0 + dx, by, color=MUTED, sw=1.4))
    frags.append(line(x0, by - 4, x0, by + 4, color=MUTED, sw=1.4))
    frags.append(line(x0 + dx, by - 4, x0 + dx, by + 4, color=MUTED, sw=1.4))
    frags.append(text(x0 + dx / 2, by - 7, "крок d", size=11, color=MUTED))

    frags.append(text(W / 2, 268,
                      "У кожній пробі значення збігаються — розчепити хвилі за числами вже не можна",
                      size=11, color=MUTED))

    render(os.path.join(OUT, "aliasing.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_tiling()
    fig_aliasing()
    print("Done — 2 SVG written to", OUT)
