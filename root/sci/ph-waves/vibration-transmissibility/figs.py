# -*- coding: utf-8 -*-
"""Фігури до теми «Передавання вібрації (transmissibility)».
Запуск із теки теми:  python figs.py   → SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

ORANGE = "#e08e0b"
PURPLE = "#7d3c98"


def frange(a, b, n):
    return [a + (b - a) * i / (n - 1) for i in range(n)]


def logsp(a, b, n):
    return [a * (b / a) ** (i / (n - 1)) for i in range(n)]


def polyline(pts, color=INK, sw=2.6, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" '
            'stroke-width="%.1f"%s/>' % (p, color, sw, d))


def darrow_v(x, ytop, ybot, color=INK, sw=2.6):
    mid = (ytop + ybot) / 2
    return arrow(x, mid, x, ytop, color=color, sw=sw) + arrow(x, mid, x, ybot, color=color, sw=sw)


def ground(x1, x2, y, color=INK, sw=2):
    out = [line(x1, y, x2, y, color=color, sw=sw)]
    n = 9
    for i in range(n):
        xx = x1 + (x2 - x1) * i / (n - 1)
        out.append(line(xx, y, xx - 10, y + 12, color=color, sw=1.3))
    return "".join(out)


def vspring(x, y1, y2, coils=6, w=12, color=INK, sw=2):
    lead = (y2 - y1) * 0.13
    a, b = y1 + lead, y2 - lead
    pts = [(x, y1), (x, a)]
    for i in range(1, 2 * coils):
        yy = a + (b - a) * i / (2 * coils)
        xx = x + (w if i % 2 == 1 else -w)
        pts.append((xx, yy))
    pts += [(x, b), (x, y2)]
    return polyline(pts, color=color, sw=sw)


def vdamper(x, y1, y2, w=12, color=INK, sw=2):
    out = []
    cyl_t = y1 + (y2 - y1) * 0.40
    py = y1 + (y2 - y1) * 0.55
    out.append(line(x, y1, x, py, color=color, sw=sw))               # шток
    out.append(line(x - w, cyl_t, x - w, y2, color=color, sw=sw))    # ліва стінка
    out.append(line(x + w, cyl_t, x + w, y2, color=color, sw=sw))    # права стінка
    out.append(line(x - w, y2, x + w, y2, color=color, sw=sw))       # дно
    out.append(line(x - w * 0.78, py, x + w * 0.78, py, color=color, sw=sw + 1.2))  # поршень
    return "".join(out)


# ── Фігура 1: дві дзеркальні задачі, один T ─────────────────────────────────
def fig_two_problems():
    W, H = 840, 470
    F = []

    # роздільник
    F.append(line(425, 66, 425, 388, color="#d0d5db", sw=1.5, dash="4 5"))

    # ── ЛІВОРУЧ: сило-передавання ──
    F.append(darrow_v(205, 108, 146, color=POS, sw=3))
    F.append(text(205, 98, "коливна сила F", size=14, color=POS, bold=True))
    F.append(fitbox(145, 150, 120, 64, "машина\n(маса m)", size=14, bold=True))
    F.append(vspring(185, 214, 318))
    F.append(vdamper(232, 214, 318))
    F.append(ground(120, 292, 318))
    F.append(arrow(205, 324, 205, 356, color=POS, sw=3))
    F.append(text(205, 374, "Fₜ → у підлогу", size=14, color=POS, bold=True))
    F.append(text(205, 410, "сило-передавання:  T = Fₜ / F", size=15, bold=True))

    # ── ПРАВОРУЧ: рухо-передавання ──
    F.append(darrow_v(620, 108, 146, color=NEG, sw=3))
    F.append(text(620, 98, "X (вихід)", size=14, color=NEG, bold=True))
    F.append(fitbox(560, 150, 120, 64, "прилад\n(маса m)", size=14, bold=True))
    F.append(vspring(600, 214, 300))
    F.append(vdamper(647, 214, 300))
    F.append(ground(553, 690, 300))
    F.append(darrow_v(545, 286, 322, color=NEG, sw=3))
    F.append(text(545, 342, "Y (вхід)", size=14, color=NEG, bold=True))
    F.append(text(620, 374, "основа трясеться", size=13, color=MUTED))
    F.append(text(620, 410, "рухо-передавання:  T = X / Y", size=15, bold=True))

    # спільний висновок
    F.append(textbox(425, 444, "той самий T — одна формула", size=14, bold=True,
                     fill="#eafaf0", stroke=FIELD, pad=11)[0])

    render(os.path.join(IMG, "two-problems.svg"), W, H, *F,
           title="Два боки однієї задачі — і той самий коефіцієнт передавання")


# ── Фігура 2: сімейство кривих T(r) для різних ζ ────────────────────────────
def fig_transmissibility_curve():
    W, H = 870, 545
    F = []
    x0, x1 = 115, 760
    yt, yb = 84, 430
    rmin, rmax = 0.2, 10.0
    tmin, tmax = 0.008, 20.0
    lrmin, lrmax = math.log10(rmin), math.log10(rmax)
    ltmin, ltmax = math.log10(tmin), math.log10(tmax)

    def X(r):
        return x0 + (math.log10(r) - lrmin) / (lrmax - lrmin) * (x1 - x0)

    def Y(t):
        return yb - (math.log10(t) - ltmin) / (ltmax - ltmin) * (yb - yt)

    def T(r, z):
        return math.sqrt((1 + (2 * z * r) ** 2) / ((1 - r * r) ** 2 + (2 * z * r) ** 2))

    r2 = math.sqrt(2)

    # зона ізоляції (світло-зелена підкладка): r > √2 і T < 1
    F.append(rect(X(r2), Y(1.0), x1 - X(r2), yb - Y(1.0),
                  fill="#eafaf0", stroke="none", sw=0, rx=0))

    # позначки на осях (короткі — не перетинають написів усередині поля)
    for r in [0.2, 0.5, 1, 2, 5, 10]:
        F.append(line(X(r), yb, X(r), yb + 6, color=INK, sw=1.4))
        F.append(text(X(r), yb + 22, ("%g" % r), size=12, color=MUTED))
    for t in [0.01, 0.1, 1, 10]:
        F.append(line(x0 - 6, Y(t), x0, Y(t), color=INK, sw=1.4))
        lbl = ("%g" % t) if t >= 1 else ("%.2g" % t)
        F.append(text(x0 - 10, Y(t) + 4, lbl, size=12, color=MUTED, anchor="end"))

    # осі
    F.append(line(x0, yt, x0, yb, color=INK, sw=1.8))
    F.append(line(x0, yb, x1, yb, color=INK, sw=1.8))
    F.append(text((x0 + x1) / 2, yb + 52, "відношення частот  r = f / fₙ  →", size=14, color=INK))
    F.append(text(x0 - 4, yt - 16, "коефіцієнт передавання  T", size=13, color=MUTED, anchor="start"))

    # лінія T = 1
    F.append(line(x0, Y(1.0), x1, Y(1.0), color=MUTED, sw=1.4, dash="6 5"))
    F.append(text(x1 + 6, Y(1.0) + 4, "T = 1", size=12.5, color=MUTED, anchor="start"))

    # вертикаль r = √2
    F.append(line(X(r2), yt, X(r2), yb, color=FIELD, sw=1.8, dash="5 4"))
    F.append(text(X(r2), yt - 8, "r = √2", size=13, color=FIELD, bold=True))

    # криві
    curves = [(0.05, NEG, "ζ = 0.05"), (0.15, PURPLE, "ζ = 0.15"),
              (0.4, ORANGE, "ζ = 0.4"), (1.0, POS, "ζ = 1.0")]
    for z, col, lab in curves:
        pts = [(X(r), Y(min(max(T(r, z), tmin), tmax))) for r in logsp(rmin, rmax, 160)]
        F.append(polyline(pts, color=col, sw=2.8))
        te = T(rmax, z)
        F.append(text(x1 + 6, Y(te) + 4, lab, size=12.5, color=col, anchor="start", bold=True))

    # точка сходження й підпис
    F.append(circle(X(r2), Y(1.0), 5, fill=FIELD, stroke=FIELD))
    F.append(text(X(2.7), Y(6.2), "при r = √2 усі криві → T = 1", size=13, color=FIELD, bold=True))
    F.append(line(X(2.35), Y(4.6), X(1.6), Y(2.4), color=FIELD, sw=1.2, dash="3 3"))

    # пік резонансу
    F.append(text(X(0.42), Y(5.5), "пік резонансу", size=13, color=INK))
    F.append(text(X(0.42), Y(3.9), "≈ 1/(2ζ)", size=13, color=INK))
    F.append(line(X(0.72), Y(4.4), X(0.97), Y(7.6), color=MUTED, sw=1.2, dash="3 3"))

    # зони
    F.append(text(X(0.63), yt + 20, "зона підсилення", size=13, color=MUTED, italic=True))
    F.append(text(X(3.2), Y(0.018), "зона ізоляції", size=13, color=FIELD, italic=True, bold=True))

    render(os.path.join(IMG, "transmissibility-curve.svg"), W, H, *F,
           title="Крива передавання: підсилення ліворуч від √2, ізоляція праворуч")


# ── Фігура 3: власна частота від статичного прогину ─────────────────────────
def fig_static_deflection():
    W, H = 820, 470
    F = []
    x0, x1 = 118, 742
    yt, yb = 82, 372
    dmin, dmax = 0.1, 100.0
    fmin, fmax = 1.0, 60.0
    ldmin, ldmax = math.log10(dmin), math.log10(dmax)
    lfmin, lfmax = math.log10(fmin), math.log10(fmax)

    def X(d):
        return x0 + (math.log10(d) - ldmin) / (ldmax - ldmin) * (x1 - x0)

    def Y(f):
        return yb - (math.log10(f) - lfmin) / (lfmax - lfmin) * (yb - yt)

    def fn(d):
        return 15.8 / math.sqrt(d)

    # позначки на осях (короткі — не перетинають написів усередині поля)
    for d in [0.1, 0.3, 1, 3, 10, 30, 100]:
        F.append(line(X(d), yb, X(d), yb + 6, color=INK, sw=1.4))
        F.append(text(X(d), yb + 22, ("%g" % d), size=12, color=MUTED))
    for f in [1, 2, 5, 10, 20, 50]:
        F.append(line(x0 - 6, Y(f), x0, Y(f), color=INK, sw=1.4))
        F.append(text(x0 - 10, Y(f) + 4, ("%g" % f), size=12, color=MUTED, anchor="end"))

    # осі
    F.append(line(x0, yt, x0, yb, color=INK, sw=1.8))
    F.append(line(x0, yb, x1, yb, color=INK, sw=1.8))
    F.append(text((x0 + x1) / 2, yb + 52, "статичний прогин опори  δ, мм  →", size=14, color=INK))
    F.append(text(x0 - 4, yt - 16, "власна частота  fₙ, Гц", size=13, color=MUTED, anchor="start"))

    # крива fₙ = 15.8/√δ
    pts = [(X(d), Y(fn(d))) for d in logsp(dmin, dmax, 140)]
    F.append(polyline(pts, color=FIELD, sw=3.2))
    F.append(text(X(1.3), Y(34), "fₙ ≈ 15.8 / √δ", size=14, color=FIELD, bold=True))

    # робоча точка прикладу: δ = 3.1 мм → fₙ ≈ 9 Гц
    dx, fy = 3.1, fn(3.1)
    F.append(line(x0, Y(fy), X(dx), Y(fy), color=NEG, sw=1.4, dash="4 4"))
    F.append(line(X(dx), yb, X(dx), Y(fy), color=NEG, sw=1.4, dash="4 4"))
    F.append(circle(X(dx), Y(fy), 5.5, fill=NEG, stroke=NEG))
    F.append(text(X(dx) + 13, Y(fy) - 15, "3 мм → 9 Гц", size=13, color=NEG, bold=True, anchor="start"))

    # напрям «м'якше = краще»
    F.append(fitbox(X(8.5), Y(31), 208, 54,
                    "м'якша опора → більший прогин\n→ нижча fₙ → краща ізоляція",
                    size=12.5, fill="#fff8ec", stroke=ORANGE))

    render(os.path.join(IMG, "static-deflection.svg"), W, H, *F,
           title="Прогин опори задає власну частоту — маси знати не треба")


# ── Фігура 4: розгін крізь резонанс (для проєктувальника опори) ──────────────
def fig_spinup_resonance():
    W, H = 880, 500
    F = []
    x0, x1 = 120, 762
    yt, yb = 84, 398
    rpm_max = 1900.0
    tmin, tmax = 0.05, 14.0
    fn, zeta = 8.83, 0.05          # опора з наскрізного прикладу (30 Гц, T=0.1)
    ltmin, ltmax = math.log10(tmin), math.log10(tmax)

    def X(rpm):
        return x0 + rpm / rpm_max * (x1 - x0)

    def Y(t):
        t = min(max(t, tmin), tmax)
        return yb - (math.log10(t) - ltmin) / (ltmax - ltmin) * (yb - yt)

    def Tf(rpm):
        r = (rpm / 60.0) / fn
        return math.sqrt((1 + (2*zeta*r)**2) / ((1 - r*r)**2 + (2*zeta*r)**2))

    rpm_peak = fn * (math.sqrt(math.sqrt(1 + 8*zeta*zeta) - 1) / (2*zeta)) * 60.0
    rpm_thr = fn * math.sqrt(2) * 60.0
    tp = Tf(rpm_peak)

    # зона ізоляції (T<1, праворуч від r=√2)
    F.append(rect(X(rpm_thr), Y(1.0), x1 - X(rpm_thr), yb - Y(1.0),
                  fill="#eafaf0", stroke="none", sw=0, rx=0))

    # позначки осей
    for rpm in [0, 500, 1000, 1500, 1800]:
        F.append(line(X(rpm), yb, X(rpm), yb + 6, color=INK, sw=1.4))
        F.append(text(X(rpm), yb + 22, "%g" % rpm, size=12, color=MUTED))
    for t in [0.05, 0.1, 1, 10]:
        F.append(line(x0 - 6, Y(t), x0, Y(t), color=INK, sw=1.4))
        lbl = ("%g" % t) if t >= 1 else ("%.2g" % t)
        F.append(text(x0 - 10, Y(t) + 4, lbl, size=12, color=MUTED, anchor="end"))

    # осі
    F.append(line(x0, yt, x0, yb, color=INK, sw=1.8))
    F.append(line(x0, yb, x1, yb, color=INK, sw=1.8))
    F.append(text((x0 + x1) / 2, yb + 50, "оберти двигуна на розгоні, об/хв  →", size=14, color=INK))
    F.append(text(x0 - 4, yt - 16, "коефіцієнт передавання  T (миттєвий)", size=13, color=MUTED, anchor="start"))

    # T = 1
    F.append(line(x0, Y(1.0), x1, Y(1.0), color=MUTED, sw=1.4, dash="6 5"))
    F.append(text(x1 + 4, Y(1.0) + 4, "T = 1", size=12.5, color=MUTED, anchor="start"))

    # вертикаль r = √2
    F.append(line(X(rpm_thr), yt, X(rpm_thr), yb, color=FIELD, sw=1.6, dash="5 4"))
    F.append(text(X(rpm_thr), yt - 6, "r = √2", size=12.5, color=FIELD, bold=True))

    # крива T(rpm) на розгоні
    pts = [(X(rpm), Y(Tf(rpm))) for rpm in frange(3, rpm_max, 280)]
    F.append(polyline(pts, color=NEG, sw=3.0))

    # пік резонансу
    F.append(line(X(rpm_peak), Y(tp), X(rpm_peak), yb, color=POS, sw=1.3, dash="4 4"))
    F.append(circle(X(rpm_peak), Y(tp), 6, fill=POS, stroke=POS))
    F.append(fitbox(X(1195) - 128, Y(4.2) - 26, 256, 52,
                    "пік ≈ %d× коло %d об/хв\nпройти цю зону швидко" % (round(tp), round(rpm_peak)),
                    size=12.5, fill="#fdecea", stroke=POS))
    F.append(line(X(rpm_peak) + 6, Y(tp), X(1195) - 128, Y(4.2) - 6, color=POS, sw=1.1, dash="3 3"))

    # робоча точка
    F.append(circle(X(1800), Y(0.10), 6, fill=FIELD, stroke=FIELD))
    F.append(text(x1, Y(0.10) - 13, "робоча точка  T = 0.10", size=12.5, color=FIELD, bold=True, anchor="end"))
    F.append(text(X(1500), Y(0.066), "зона ізоляції", size=13, color=FIELD, italic=True, bold=True))

    render(os.path.join(IMG, "spinup-resonance.svg"), W, H, *F,
           title="Розгін крізь резонанс: короткий пік ×10, далі — тиша")


def arc_poly(cx, cy, rad, a0deg, a1deg, color=INK, sw=1.8, n=48):
    """Дуга кола як полілінія (кути в градусах, math-конвенція, екран з віссю вниз)."""
    pts = []
    for i in range(n + 1):
        a = math.radians(a0deg + (a1deg - a0deg) * i / n)
        pts.append((cx + rad * math.cos(a), cy - rad * math.sin(a)))
    return polyline(pts, color=color, sw=sw)


# ── Фігура 5: фазорна побудова T і φ у комплексній площині ───────────────────
def fig_phasor_construction():
    W, H = 820, 500
    F = []
    ox, oy, sc = 380, 380, 140.0
    z, r = 0.2, 1.5
    im = 2 * z * r          # 0.6  — спільна уявна частина
    reN = 1.0
    reD = 1 - r * r         # −1.25
    Nx, Ny = ox + sc * reN, oy - sc * im
    Dx, Dy = ox + sc * reD, oy - sc * im

    # осі Re, Im
    F.append(arrow(ox - 250, oy, ox + 258, oy, color=MUTED, sw=1.8))
    F.append(arrow(ox, oy + 22, ox, oy - 210, color=MUTED, sw=1.8))
    F.append(text(ox + 264, oy + 4, "Re", size=13, color=MUTED, anchor="start"))
    F.append(text(ox + 12, oy - 200, "Im", size=13, color=MUTED, anchor="start"))

    # спільна уявна висота 2ζr
    F.append(line(Dx, Ny, Nx, Ny, color="#c9ced6", sw=1.4, dash="4 5"))
    F.append(text(ox + 8, Ny - 7, "2ζr", size=12, color=MUTED, anchor="start"))

    # дуги кутів
    aN = math.degrees(math.atan2(im, reN))
    aD = math.degrees(math.atan2(im, reD))
    F.append(arc_poly(ox, oy, 60, 0, aN, color=FIELD, sw=2))
    F.append(arc_poly(ox, oy, 42, 0, aD, color=NEG, sw=2))
    F.append(text(ox + 74, oy - 15, "α", size=15, color=FIELD, bold=True))
    F.append(text(ox - 34, oy - 30, "β", size=15, color=NEG, bold=True))

    # фазори
    F.append(arrow(ox, oy, Nx, Ny, color=FIELD, sw=3.2))
    F.append(arrow(ox, oy, Dx, Dy, color=NEG, sw=3.2))

    # підписи фазорів (над вершинами, по центру — не вилазять)
    F.append(text(Nx, Ny - 30, "чисельник", size=12, color=MUTED))
    F.append(text(Nx, Ny - 14, "N = 1 + j·2ζr", size=13.5, color=FIELD, bold=True))
    F.append(text(Dx, Dy - 30, "знаменник", size=12, color=MUTED))
    F.append(text(Dx, Dy - 14, "D = (1−r²) + j·2ζr", size=13.5, color=NEG, bold=True))

    # мітки довжин уздовж фазорів
    F.append(text(ox + 0.72 * (Nx - ox) + 12, oy + 0.72 * (Ny - oy) + 4, "|N|",
                  size=13, color=FIELD, bold=True, anchor="start"))
    F.append(text(ox + 0.72 * (Dx - ox) - 12, oy + 0.72 * (Dy - oy) + 4, "|D|",
                  size=13, color=NEG, bold=True, anchor="end"))

    # висновок
    b, _, _ = textbox(600, 92, "T = |N| / |D|\nφ = α − β   (вихід відстає)",
                      size=13.5, bold=True, fill="#eafaf0", stroke=FIELD, pad=11)
    F.append(b)

    # приклад
    F.append(text(ox, oy + 96,
                  "приклад: r = 1.5, ζ = 0.2  →  T ≈ 0.84 (ізоляція),  φ ≈ −123°",
                  size=12.5, color=MUTED))

    render(os.path.join(IMG, "phasor-construction.svg"), W, H, *F,
           title="Фазорна побудова: T — відношення довжин, φ — різниця кутів")


# ── Фігура 6: фаза виходу φ(r) для різних ζ ──────────────────────────────────
def fig_transmissibility_phase():
    W, H = 880, 520
    F = []
    x0, x1 = 120, 730
    yt, yb = 80, 430
    rmin, rmax = 0.2, 10.0
    lrmin, lrmax = math.log10(rmin), math.log10(rmax)
    ptop, pbot = 10.0, -190.0     # запас, щоб 0 і −180 не лягли на межу

    def X(r):
        return x0 + (math.log10(r) - lrmin) / (lrmax - lrmin) * (x1 - x0)

    def Y(phi):
        return yt + (ptop - phi) / (ptop - pbot) * (yb - yt)

    def phase(r, z):
        return math.degrees(math.atan(2 * z * r) - math.atan2(2 * z * r, 1 - r * r))

    r2 = math.sqrt(2)

    # позначки осей
    for r in [0.2, 0.5, 1, 2, 5, 10]:
        F.append(line(X(r), yb, X(r), yb + 6, color=INK, sw=1.4))
        F.append(text(X(r), yb + 22, ("%g" % r), size=12, color=MUTED))
    for p in [0, -45, -90, -135, -180]:
        F.append(line(x0 - 6, Y(p), x0, Y(p), color=INK, sw=1.4))
        F.append(text(x0 - 10, Y(p) + 4, ("%d°" % p), size=12, color=MUTED, anchor="end"))

    # осі
    F.append(line(x0, yt, x0, yb, color=INK, sw=1.8))
    F.append(line(x0, yb, x1, yb, color=INK, sw=1.8))
    F.append(text((x0 + x1) / 2, yb + 52, "відношення частот  r = f / fₙ  →", size=14, color=INK))
    F.append(text(x0 - 4, yt - 16, "фаза виходу  φ", size=13, color=MUTED, anchor="start"))

    # лінія −90°
    F.append(line(x0, Y(-90), x1, Y(-90), color=MUTED, sw=1.3, dash="6 5"))
    F.append(text(x1 + 6, Y(-90) + 4, "−90°", size=12, color=MUTED, anchor="start"))

    # r = 1 і r = √2
    F.append(line(X(1), yt, X(1), yb, color="#c9ced6", sw=1.4, dash="4 4"))
    F.append(text(X(1) - 5, yt - 8, "r = 1", size=12.5, color=MUTED, anchor="end"))
    F.append(line(X(r2), yt, X(r2), yb, color=FIELD, sw=1.6, dash="5 4"))
    F.append(text(X(r2) + 5, yt - 8, "r = √2", size=12.5, color=FIELD, bold=True, anchor="start"))

    # недемпфований крок 0 → −180°
    F.append(polyline([(x0, Y(0)), (X(1), Y(0)), (X(1), Y(-180)), (x1, Y(-180))],
                      color="#b8bec8", sw=1.8, dash="2 4"))
    F.append(text(X(0.42), Y(-170), "ζ = 0:  крок 0 → −180°", size=12, color=MUTED, anchor="start"))

    # криві фази
    curves = [(0.05, NEG, "ζ = 0.05"), (0.15, PURPLE, "ζ = 0.15"),
              (0.4, ORANGE, "ζ = 0.4"), (1.0, POS, "ζ = 1.0")]
    for z, col, lab in curves:
        pts = [(X(r), Y(max(pbot, min(ptop, phase(r, z))))) for r in logsp(rmin, rmax, 240)]
        F.append(polyline(pts, color=col, sw=2.6))
        F.append(text(x1 + 6, Y(phase(rmax, z)) + 4, lab, size=12.5, color=col, bold=True, anchor="start"))

    render(os.path.join(IMG, "transmissibility-phase.svg"), W, H, *F,
           title="Фаза виходу: у фазі на малих r, чверть періоду на резонансі")


# ── Фігура 7 (hist): три поверхи однієї ідеї на осі часу ─────────────────────
def fig_hist_timeline():
    W, H = 940, 384
    F = []

    ax_y = 296
    x_left, x_right = 96, 872
    y0, y1 = 1870, 1940

    def X(yr):
        return x_left + (yr - y0) / (y1 - y0) * (x_right - x_left)

    # підзаголовок
    F.append(text(W / 2, 56, "Три поверхи переходу від «кріпи жорстко» до «кріпи м'яко»",
                  size=14, color=MUTED))

    # вісь часу з десятковими позначками
    F.append(line(x_left, ax_y, x_right, ax_y, color=INK, sw=2.2))
    F.append(arrow(x_right - 28, ax_y, x_right + 4, ax_y, color=INK, sw=2.2))
    F.append(text(x_right + 2, ax_y + 26, "час", size=13, color=MUTED, anchor="end"))
    for yr in range(1870, 1941, 10):
        F.append(line(X(yr), ax_y - 5, X(yr), ax_y + 5, color=MUTED, sw=1.2))

    milestones = [
        (1877, PURPLE, "ТЕОРІЯ",
         "Лорд Релей\n«Теорія звуку», 1877\nрівняння коливань"),
        (1909, ORANGE, "ІДЕЯ · ПРИСТРІЙ",
         "Германн Фрам\nпатент US 989958, 1909\nгасник тюнінгом"),
        (1934, FIELD, "СИСТЕМАТИЗАЦІЯ",
         "Ден Гартог\n«Mechanical Vibrations»\n1934 · криві й правила"),
    ]

    cw, ch, card_top = 236, 104, 96
    for yr, col, role, body in milestones:
        x = X(yr)
        F.append(text(x, card_top - 10, role, size=13, color=col, bold=True))
        F.append(fitbox(x - cw / 2, card_top, cw, ch, body, size=13,
                        stroke=col, sw=2, fill=BG))
        F.append(line(x, card_top + ch, x, ax_y - 8, color=col, sw=1.6, dash="4 4"))
        F.append(circle(x, ax_y, 7, fill=col, stroke=col))
        F.append(text(x, ax_y + 26, str(yr), size=15, color=INK, bold=True))

    render(os.path.join(IMG, "hist-timeline.svg"), W, H, *F,
           title="Три поверхи однієї ідеї — м'який підвіс")


if __name__ == "__main__":
    fig_two_problems()
    fig_transmissibility_curve()
    fig_static_deflection()
    fig_spinup_resonance()
    fig_phasor_construction()
    fig_transmissibility_phase()
    fig_hist_timeline()
    print("OK: 7 SVG ->", IMG)
