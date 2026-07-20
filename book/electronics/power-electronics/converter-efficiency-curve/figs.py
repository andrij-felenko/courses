# -*- coding: utf-8 -*-
"""Фігури до статті «Крива ефективності перетворювача».
Запуск із теки теми:  python figs.py   →  ./img/*.svg
Модель втрат спільна з прозою: Vout=3.3 В, Pfix=0.03 Вт, ksw=0.05 Вт/А, R=0.20 Ом."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

# ── спільна модель втрат ────────────────────────────────────────────────────
Vout = 3.3
Pfix = 0.03      # Вт  — не залежить від навантаження (спокій + затвор + осердя)
KSW  = 0.05      # Вт/А — росте лінійно (перекриття струм·напруга при комутації)
R    = 0.20      # Ом  — провідні втрати I²·R
Ipk  = math.sqrt(Pfix / R)          # 0.387 А: тут фіксовані = провідні

def ploss(I): return Pfix + KSW * I + R * I * I
def pout(I):  return Vout * I
def eff(I):   return 100.0 * pout(I) / (pout(I) + ploss(I))

SW  = "#2457d6"   # синій — комутаційні
CON = "#c0392b"   # червоний — провідні
FIX = "#6b7280"   # сірий — фіксовані
TOT = "#1a1a1a"   # чорний — сумарні / крива


def polyline(pts, color, sw=2.6, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.2f,%.2f" % (x, y) for x, y in pts)
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (p, color, sw, d)


def logspace(a, b, n):
    la, lb = math.log10(a), math.log10(b)
    return [10 ** (la + (lb - la) * i / (n - 1)) for i in range(n)]


# ── Фігура 1: крива ККД проти навантаження ──────────────────────────────────
def fig_curve():
    W, H = 760, 480
    x0, x1, y0, y1 = 100, 610, 74, 372
    Imin, Imax, emin, emax = 0.01, 3.0, 40.0, 100.0

    def X(I): return x0 + (math.log10(I) - math.log10(Imin)) / (math.log10(Imax) - math.log10(Imin)) * (x1 - x0)
    def Y(e): return y1 - (e - emin) / (emax - emin) * (y1 - y0)

    s = []
    # сітка по η
    for e in range(40, 101, 10):
        s.append(line(x0, Y(e), x1, Y(e), color="#e6e8ec", sw=1))
        s.append(text(x0 - 10, Y(e) + 4, "%d" % e, size=12, color=MUTED, anchor="end"))
    s.append(text(x0 - 40, (y0 + y1) / 2, "ККД, %", size=13, color=INK, anchor="middle"))
    # осі й підписи x
    s.append(line(x0, y1, x1, y1, color=INK, sw=1.6))
    s.append(line(x0, y0, x0, y1, color=INK, sw=1.6))
    for I, lab in [(0.01, "10 мА"), (0.03, "30 мА"), (0.1, "100 мА"),
                   (0.3, "300 мА"), (1.0, "1 А"), (3.0, "3 А")]:
        s.append(line(X(I), y1, X(I), y1 + 5, color=INK, sw=1.4))
        s.append(text(X(I), y1 + 22, lab, size=12, color=MUTED))
    s.append(text((x0 + x1) / 2, y1 + 46, "струм навантаження (логарифмічна шкала)", size=13, color=INK))

    # межі зон (орієнтовні) + номери
    for Ib in (0.09, 0.9):
        s.append(line(X(Ib), y0, X(Ib), y1, color="#c9ccd2", sw=1.2, dash="4 4"))
    for I, num in [(0.03, "1"), (0.3, "2"), (1.7, "3")]:
        s.append(circle(X(I), y0 + 16, 12, fill="#eef1f5", stroke=MUTED, sw=1.4))
        s.append(text(X(I), y0 + 21, num, size=13, color=INK, bold=True))

    # крива
    pts = [(X(I), Y(eff(I))) for I in logspace(Imin, Imax, 120)]
    s.append(polyline(pts, TOT, sw=3.0))

    # пік
    s.append(line(X(Ipk), Y(eff(Ipk)), X(Ipk), y1, color=CON, sw=1.4, dash="5 4"))
    s.append(circle(X(Ipk), Y(eff(Ipk)), 5, fill=CON, stroke=CON, sw=1))
    s.append(text(X(Ipk), Y(eff(Ipk)) - 14, "пік ≈ 94 %", size=13, color=CON, bold=True))

    # легенда зон унизу
    ly = 452
    zones = [("1", "фіксовані втрати панують"),
             ("2", "пік: фіксовані = I²·R"),
             ("3", "провідні I²·R панують")]
    zx = 60
    for num, txt in zones:
        s.append(circle(zx, ly, 11, fill="#eef1f5", stroke=MUTED, sw=1.3))
        s.append(text(zx, ly + 4, num, size=12, color=INK, bold=True))
        s.append(text(zx + 20, ly + 4, txt, size=13, color=INK, anchor="start"))
        zx += 240

    render(os.path.join(OUT, 'efficiency-curve.svg'), W, H, *s,
           title="Крива ККД: низько й високо погано, добре — посередині")


# ── Фігура 2: складові втрат (лог-лог) ──────────────────────────────────────
def fig_losses():
    W, H = 760, 480
    x0, x1, y0, y1 = 110, 590, 74, 384
    Imin, Imax, Pmin, Pmax = 0.01, 3.0, 1e-4, 3.0

    def X(I): return x0 + (math.log10(I) - math.log10(Imin)) / (math.log10(Imax) - math.log10(Imin)) * (x1 - x0)
    def Y(P): return y1 - (math.log10(P) - math.log10(Pmin)) / (math.log10(Pmax) - math.log10(Pmin)) * (y1 - y0)

    s = []
    # сітка по P (декади)
    for k in range(-4, 1):
        P = 10.0 ** k
        s.append(line(x0, Y(P), x1, Y(P), color="#e6e8ec", sw=1))
        lab = {(-4): "0.1 мВт", (-3): "1 мВт", (-2): "10 мВт", (-1): "0.1 Вт", 0: "1 Вт"}[k]
        s.append(text(x0 - 10, Y(P) + 4, lab, size=11, color=MUTED, anchor="end"))
    s.append(line(x0, y1, x1, y1, color=INK, sw=1.6))
    s.append(line(x0, y0, x0, y1, color=INK, sw=1.6))
    for I, lab in [(0.01, "10 мА"), (0.1, "100 мА"), (1.0, "1 А"), (3.0, "3 А")]:
        s.append(line(X(I), y1, X(I), y1 + 5, color=INK, sw=1.4))
        s.append(text(X(I), y1 + 22, lab, size=12, color=MUTED))
    s.append(text((x0 + x1) / 2, y1 + 46, "струм навантаження (лог)", size=13, color=INK))

    II = logspace(Imin, Imax, 120)
    s.append(polyline([(X(I), Y(Pfix)) for I in II], FIX, sw=2.6))
    s.append(polyline([(X(I), Y(KSW * I)) for I in II], SW, sw=2.6))
    s.append(polyline([(X(I), Y(R * I * I)) for I in II], CON, sw=2.6))
    s.append(polyline([(X(I), Y(ploss(I))) for I in II], TOT, sw=2.8, dash="6 4"))

    # точка перетину фіксованих і провідних = пік ККД
    s.append(circle(X(Ipk), Y(Pfix), 5.5, fill=FIELD, stroke=FIELD, sw=1))
    s.append(line(X(Ipk), Y(Pfix), X(Ipk), y1, color=FIELD, sw=1.3, dash="5 4"))
    s.append(text(X(Ipk) + 8, y1 - 8, "тут пік ККД", size=12, color=FIELD, bold=True, anchor="start"))

    # легенда — праворуч, у вільному куті
    lx, ly = 612, 96
    items = [(FIX, "фіксовані (сталі)"), (SW, "комутаційні ∝ I"),
             (CON, "провідні ∝ I²"), (TOT, "сума")]
    for i, (col, lab) in enumerate(items):
        yy = ly + i * 30
        dash = ' stroke-dasharray="6 4"' if col == TOT else ''
        s.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="3"%s/>'
                 % (lx, yy, lx + 30, yy, col, dash))
        s.append(text(lx + 38, yy + 4, lab, size=12, color=INK, anchor="start"))

    render(os.path.join(OUT, 'loss-components.svg'), W, H, *s,
           title="Три родини втрат: чому крива має пік")


# ── Фігура 3: куди йде вхідна потужність у трьох точках ──────────────────────
def fig_split():
    W, H = 760, 360
    barx, barw = 210, 400
    ys = [96, 176, 256]
    cases = [(0.03, "легке\n30 мА"), (Ipk, "пік\n0.39 А"), (3.0, "повне\n3 А")]
    s = []
    s.append(text(barx, 66, "корисне (вихід)", size=12, color=FIELD, bold=True, anchor="start"))
    s.append(text(barx + barw, 66, "втрати (тепло)", size=12, color=CON, bold=True, anchor="end"))
    for (I, lab), y in zip(cases, ys):
        e = eff(I) / 100.0
        wg = barw * e
        s.append(rect(barx, y, wg, 46, fill="#e7f6ee", stroke=FIELD, sw=1.6, rx=4))
        s.append(rect(barx + wg, y, barw - wg, 46, fill="#fdecea", stroke=CON, sw=1.6, rx=4))
        for ln, dy in zip(lab.split("\n"), (-6, 12)):
            s.append(text(barx - 24, y + 23 + dy, ln, size=13, color=INK, anchor="end"))
        s.append(text(barx + wg / 2, y + 29, "%.0f %%" % (e * 100), size=15, color="#1e7a48", bold=True))
        lossp = 100 - e * 100
        s.append(text(barx + wg + (barw - wg) / 2, y + 29, "%.0f %%" % lossp,
                      size=13, color="#8a2d22", bold=True))
    s.append(text(W / 2, 330, "однакова довжина = вся вхідна потужність; зелена частка і є ККД",
                  size=13, color=MUTED))
    render(os.path.join(OUT, 'power-split.svg'), W, H, *s,
           title="Куди дівається вхідна потужність")


# ── Фігура 4 (виноска math): розклад відношення ρ = P_втрат/P_вих ────────────
def fig_ratio():
    W, H = 760, 500
    x0, x1, y0, y1 = 110, 590, 78, 380
    Imin, Imax, rmin, rmax = 0.05, 3.0, 0.0, 0.22

    def X(I): return x0 + (math.log10(I) - math.log10(Imin)) / (math.log10(Imax) - math.log10(Imin)) * (x1 - x0)
    def Y(r): return y1 - (r - rmin) / (rmax - rmin) * (y1 - y0)

    a = Pfix / Vout        # спадний доданок:  a/I
    c = KSW / Vout         # сталий доданок
    b = R / Vout           # висхідний доданок: b·I
    def rho(I): return a / I + c + b * I

    s = []
    for r in [0.0, 0.05, 0.10, 0.15, 0.20]:
        s.append(line(x0, Y(r), x1, Y(r), color="#e6e8ec", sw=1))
        s.append(text(x0 - 10, Y(r) + 4, "%.2f" % r, size=12, color=MUTED, anchor="end"))
    s.append(text(x0 - 52, (y0 + y1) / 2, "ρ = P_втрат / P_вих", size=13, color=INK, anchor="middle"))
    s.append(line(x0, y1, x1, y1, color=INK, sw=1.6))
    s.append(line(x0, y0, x0, y1, color=INK, sw=1.6))
    for I, lab in [(0.05, "50 мА"), (0.1, "100 мА"), (0.387, "0.39 А"), (1.0, "1 А"), (3.0, "3 А")]:
        s.append(line(X(I), y1, X(I), y1 + 5, color=INK, sw=1.4))
        s.append(text(X(I), y1 + 22, lab, size=12, color=MUTED))
    s.append(text((x0 + x1) / 2, y1 + 46, "струм навантаження (логарифмічна шкала)", size=13, color=INK))

    II = logspace(Imin, Imax, 140)
    s.append(polyline([(X(I), Y(a / I)) for I in II], FIX, sw=2.4))          # спадний
    s.append(polyline([(X(I), Y(b * I)) for I in II], CON, sw=2.4))          # висхідний
    s.append(line(X(Imin), Y(c), X(Imax), Y(c), color=SW, sw=2.4))          # сталий
    s.append(polyline([(X(I), Y(rho(I))) for I in II], TOT, sw=3.0))        # сума

    # пік: спадний = висхідний, рівно під дном суми
    s.append(line(X(Ipk), y0, X(Ipk), y1, color=MUTED, sw=1.3, dash="5 4"))
    s.append(circle(X(Ipk), Y(a / Ipk), 4.5, fill=BG, stroke=INK, sw=1.6))   # перетин долей
    s.append(circle(X(Ipk), Y(rho(Ipk)), 5.5, fill=TOT, stroke=TOT, sw=1))   # дно суми
    s.append(text(X(Ipk) + 9, Y(rho(Ipk)) - 6, "ρ_мін ≈ 0.062", size=12, color=TOT, bold=True, anchor="start"))
    s.append(text(X(Ipk), y1 + 40, "I_пік = √(P_фікс/R) = 0.387 А", size=12, color=INK, bold=True))

    # легенда — у вільному верхньо-середньому куті
    lx, ly = 312, 120
    items = [(FIX, "P_фікс/(V·I) — спадає як 1/I"),
             (SW,  "k/V — стала (комутаційні)"),
             (CON, "R·I/V — росте як I"),
             (TOT, "ρ — сума (те, що мінімізуємо)")]
    for i, (col, lab) in enumerate(items):
        yy = ly + i * 24
        s.append(line(lx, yy, lx + 28, yy, color=col, sw=3))
        s.append(text(lx + 36, yy + 4, lab, size=12, color=INK, anchor="start"))

    render(os.path.join(OUT, 'ratio-decompose.svg'), W, H, *s,
           title="Відношення втрат до виходу: стала + спад + ріст")


# ── Фігура 5 (виноска math): пік не залежить від k ──────────────────────────
def fig_peak_invariant():
    W, H = 760, 470
    x0, x1, y0, y1 = 100, 610, 74, 372
    Imin, Imax, emin, emax = 0.05, 3.0, 78.0, 98.0

    def X(I): return x0 + (math.log10(I) - math.log10(Imin)) / (math.log10(Imax) - math.log10(Imin)) * (x1 - x0)
    def Y(e): return y1 - (e - emin) / (emax - emin) * (y1 - y0)
    def effk(I, kk): return 100.0 * (Vout * I) / (Vout * I + Pfix + kk * I + R * I * I)

    s = []
    for e in range(80, 99, 5):
        s.append(line(x0, Y(e), x1, Y(e), color="#e6e8ec", sw=1))
        s.append(text(x0 - 10, Y(e) + 4, "%d" % e, size=12, color=MUTED, anchor="end"))
    s.append(text(x0 - 40, (y0 + y1) / 2, "ККД, %", size=13, color=INK, anchor="middle"))
    s.append(line(x0, y1, x1, y1, color=INK, sw=1.6))
    s.append(line(x0, y0, x0, y1, color=INK, sw=1.6))
    for I, lab in [(0.05, "50 мА"), (0.1, "100 мА"), (0.387, "0.39 А"), (1.0, "1 А"), (3.0, "3 А")]:
        s.append(line(X(I), y1, X(I), y1 + 5, color=INK, sw=1.4))
        s.append(text(X(I), y1 + 22, lab, size=12, color=MUTED))
    s.append(text((x0 + x1) / 2, y1 + 46, "струм навантаження (логарифмічна шкала)", size=13, color=INK))

    # спільна вертикаль піка — торкається вершини всіх трьох кривих
    s.append(line(X(Ipk), y0, X(Ipk), y1, color=MUTED, sw=1.4, dash="5 4"))

    II = logspace(Imin, Imax, 140)
    curves = [(0.0, FIELD, "k = 0 (без комутації)"),
              (0.05, TOT, "k = 0.05 (наша модель)"),
              (0.15, CON, "k = 0.15 (вища частота)")]
    for kk, col, _ in curves:
        s.append(polyline([(X(I), Y(effk(I, kk))) for I in II], col, sw=2.8))
        ep = effk(Ipk, kk)
        s.append(circle(X(Ipk), Y(ep), 4.5, fill=col, stroke=col, sw=1))
        s.append(text(X(Ipk) + 10, Y(ep) - 5, "%.1f %%" % ep, size=12, color=col, bold=True, anchor="start"))

    # легенда — унизу зліва, у проміжку між сітковими лініями 85% і 80%
    # (щоб не перетинати ані Y(85)=267.7, ані Y(80)=342.2 — див. свгчек §5)
    lx, ly = 128, 284
    for i, (kk, col, lab) in enumerate(curves):
        yy = ly + i * 22
        s.append(line(lx, yy, lx + 28, yy, color=col, sw=3))
        s.append(text(lx + 36, yy + 4, lab, size=12, color=INK, anchor="start"))
    s.append(text(X(Ipk), y1 + 40, "вершина в усіх — над 0.387 А", size=12, color=INK, bold=True))

    render(os.path.join(OUT, 'peak-invariant-k.svg'), W, H, *s,
           title="Пік не рухається з k — рухається лише його висота")


if __name__ == "__main__":
    fig_curve()
    fig_losses()
    fig_split()
    fig_ratio()
    fig_peak_invariant()
    print("Ipk = %.3f A, eff(pk) = %.1f%%" % (Ipk, eff(Ipk)))
    print("eff(30mA)=%.1f  eff(3A)=%.1f" % (eff(0.03), eff(3.0)))
    print("OK ->", OUT)
