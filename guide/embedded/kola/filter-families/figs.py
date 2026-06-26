# -*- coding: utf-8 -*-
"""Фігури до «Родини фільтрів: Баттерворт, Чебишов, Бесель».
Генерує SVG у ./img/. Криві рахуються чистим Python (без залежностей)."""
import sys, os, math, cmath
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# Кольори родин
C_BUT = "#2457d6"   # Баттерворт — синій
C_CHE = "#c0392b"   # Чебишов  — червоний
C_BES = "#27ae60"   # Бесель   — зелений


# ── Полюси нормованих фільтрів n-го порядку (ωc = 1) ────────────────────────
def butter_poles(n):
    """Полюси Баттерворта на одиничному колі в лівій півплощині."""
    p = []
    for k in range(n):
        theta = math.pi * (2 * k + 1) / (2 * n) + math.pi / 2
        p.append(cmath.rect(1.0, theta))
    return p


def cheb_poles(n, eps):
    """Полюси Чебишова I роду (еліпс), пульсації задає eps."""
    a = (1.0 / n) * math.asinh(1.0 / eps)
    sh, ch = math.sinh(a), math.cosh(a)
    p = []
    for k in range(n):
        theta = math.pi * (2 * k + 1) / (2 * n)
        re = -sh * math.sin(theta)
        im = ch * math.cos(theta)
        p.append(complex(re, im))
    return p


# Полюси Бесселя 4-го порядку (нормування на ωc за -3 дБ, з таблиць)
BESSEL4 = [complex(-0.9047, 0.2709), complex(-0.9047, -0.2709),
           complex(-0.7426, 0.8377), complex(-0.7426, -0.8377)]


def mag_from_poles(poles, w):
    """|H(jω)| для всечастотного знаменника з даними полюсами, H(0)=1."""
    s = complex(0, w)
    num = 1.0
    den = 1.0
    for pk in poles:
        num *= (-pk)            # щоб H(0)=1
        den *= (s - pk)
    return abs(num / den)


def cheb_mag(n, eps, w):
    """Точна формула амплітуди Чебишова I роду."""
    if w <= 1.0:
        Tn = math.cos(n * math.acos(w))
    else:
        Tn = math.cosh(n * math.acosh(w))
    return 1.0 / math.sqrt(1.0 + (eps * Tn) ** 2)


def db(x):
    return 20.0 * math.log10(max(x, 1e-9))


# ════════════════════════════════════════════════════════════════════════════
# Фігура 1: амплітудні характеристики трьох родин (лінійна шкала)
# ════════════════════════════════════════════════════════════════════════════
def fig_shapes():
    W, H = 720, 430
    L, R, T, B = 70, 540, 60, 350      # поле графіка
    plot_w, plot_h = R - L, B - T
    wmax = 2.5

    def X(w):
        return L + (w / wmax) * plot_w

    def Y(m):                            # m у лінійних одиницях 0..1.05
        return B - (m / 1.05) * plot_h

    bp = butter_poles(4)
    cp = cheb_poles(4, 0.5088)           # ~1 дБ пульсації
    frags = []

    # сітка й осі
    for m in (0, 0.25, 0.5, 0.707, 1.0):
        y = Y(m)
        frags.append(line(L, y, R, y, color="#e3e6ea", sw=1))
        lbl = "0.707" if abs(m - 0.707) < 0.01 else ("%.2f" % m).rstrip("0").rstrip(".")
        frags.append(text(L - 8, y + 4, lbl, size=11, color=MUTED, anchor="end"))
    for w in (0, 0.5, 1.0, 1.5, 2.0, 2.5):
        x = X(w)
        frags.append(line(x, T, x, B, color="#eef0f3", sw=1))
        frags.append(text(x, B + 18, ("%.1f" % w), size=11, color=MUTED))
    frags.append(line(L, T, L, B, color=INK, sw=1.6))
    frags.append(line(L, B, R, B, color=INK, sw=1.6))

    # лінія смуги пропускання -3 дБ (0.707)
    frags.append(line(L, Y(0.707), R, Y(0.707), color=MUTED, sw=1.2, dash="5,4"))
    # вертикаль ωc
    frags.append(line(X(1.0), T, X(1.0), B, color=MUTED, sw=1.2, dash="3,3"))

    def curve(fn, color):
        pts = []
        w = 0.001
        while w <= wmax:
            pts.append("%.1f,%.1f" % (X(w), Y(min(fn(w), 1.05))))
            w += 0.01
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                % (" ".join(pts), color))

    frags.append(curve(lambda w: cheb_mag(4, 0.5088, w), C_CHE))
    frags.append(curve(lambda w: mag_from_poles(bp, w), C_BUT))
    frags.append(curve(lambda w: mag_from_poles(BESSEL4, w), C_BES))

    # підписи осей
    frags.append(text(L - 44, (T + B) / 2, "|H|", size=13, color=INK))
    frags.append(text((L + R) / 2, B + 40, "частота  ω / ωc", size=13, color=INK))
    frags.append(text(X(1.0), T - 8, "ωc", size=12, color=MUTED, bold=True))

    # легенда (textbox -> розпаковка)
    lx, ly = R + 18, 90
    items = [("Баттерворт", C_BUT, "рівна смуга"),
             ("Чебишов", C_CHE, "брижі, крутіше"),
             ("Бесель", C_BES, "пологий спад")]
    frags.append(text(lx + 70, ly - 22, "4-й порядок", size=12, color=INK, bold=True))
    for i, (name, col, note) in enumerate(items):
        yy = ly + i * 56
        frags.append(line(lx, yy, lx + 26, yy, color=col, sw=3))
        frags.append(text(lx + 34, yy + 4, name, size=12.5, color=INK, anchor="start", bold=True))
        frags.append(text(lx, yy + 22, note, size=10.5, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "families-shape.svg"), W, H, *frags,
           title="Три родини, один порядок: на що міняють крутість")


# ════════════════════════════════════════════════════════════════════════════
# Фігура 2: компроміс Чебишова — пульсації проти крутості (лог-шкала)
# ════════════════════════════════════════════════════════════════════════════
def fig_tradeoff():
    W, H = 720, 420
    L, R, T, B = 72, 560, 56, 330
    plot_w, plot_h = R - L, B - T
    wmin, wmax = 0.2, 5.0          # лог-вісь частоти
    dbmin, dbmax = -60.0, 6.0

    lw = math.log10(wmin)
    lwspan = math.log10(wmax) - lw

    def X(w):
        return L + (math.log10(w) - lw) / lwspan * plot_w

    def Y(d):
        return T + (dbmax - d) / (dbmax - dbmin) * plot_h

    bp = butter_poles(5)
    cp1 = cheb_poles(5, 0.1526)       # 0.1 дБ
    cp3 = cheb_poles(5, 0.9976)       # 3 дБ
    frags = []

    # сітка дБ
    for d in range(0, -61, -10):
        y = Y(d)
        frags.append(line(L, y, R, y, color="#e3e6ea", sw=1))
        frags.append(text(L - 8, y + 4, "%d" % d, size=11, color=MUTED, anchor="end"))
    # сітка частоти (декади)
    for w in (0.2, 0.5, 1.0, 2.0, 5.0):
        x = X(w)
        frags.append(line(x, T, x, B, color="#eef0f3", sw=1))
        frags.append(text(x, B + 18, ("%g" % w), size=11, color=MUTED))
    frags.append(line(L, T, L, B, color=INK, sw=1.6))
    frags.append(line(L, B, R, B, color=INK, sw=1.6))
    frags.append(line(X(1.0), T, X(1.0), B, color=MUTED, sw=1.2, dash="3,3"))

    def curve(fn, color, sw=2.6, dash=None):
        pts = []
        # рівномірно по логарифму частоти
        steps = 480
        for i in range(steps + 1):
            lwv = lw + lwspan * i / steps
            w = 10 ** lwv
            d = max(db(fn(w)), dbmin)
            pts.append("%.1f,%.1f" % (X(w), Y(d)))
        da = ' stroke-dasharray="%s"' % dash if dash else ''
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
                % (" ".join(pts), color, sw, da))

    frags.append(curve(lambda w: mag_from_poles(bp, w), C_BUT))
    frags.append(curve(lambda w: cheb_mag(5, 0.1526, w), C_CHE, dash="6,4"))
    frags.append(curve(lambda w: cheb_mag(5, 0.9976, w), C_CHE))

    # підписи осей
    frags.append(text((L + R) / 2, B + 40, "частота  ω / ωc  (лог)", size=13, color=INK))
    frags.append(text(L - 50, (T + B) / 2, "дБ", size=13, color=INK))
    frags.append(text(X(1.0), T - 6, "ωc", size=12, color=MUTED, bold=True))

    # легенда
    lx, ly = R + 16, 96
    rows = [("Баттерворт", C_BUT, None, "0 дБ брижів"),
            ("Чебишов 0.1 дБ", C_CHE, "6,4", "майже рівний"),
            ("Чебишов 3 дБ", C_CHE, None, "найкрутіший")]
    frags.append(text(lx + 60, ly - 24, "5-й порядок", size=12, color=INK, bold=True))
    for i, (name, col, dash, note) in enumerate(rows):
        yy = ly + i * 54
        frags.append(line(lx, yy, lx + 26, yy, color=col, sw=3,
                          dash=dash))
        frags.append(text(lx + 32, yy + 4, name, size=11.5, color=INK, anchor="start", bold=True))
        frags.append(text(lx, yy + 21, note, size=10, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "cheb-tradeoff.svg"), W, H, *frags,
           title="Чебишов: глибші брижі — крутіший зріз")


# ════════════════════════════════════════════════════════════════════════════
# Фігура 3: перехідна характеристика (відгук на сходинку) — дзвін проти чистоти
# ════════════════════════════════════════════════════════════════════════════
def step_response(poles, t):
    """Відгук H(s) (усі полюси, H(0)=1, лише прості полюси) на одиничну сходинку.
    y(t) = 1 + Σ_k Res_k/p_k · e^{p_k t}, де Res — лишок H у полюсі p_k."""
    # H(s) = K / Π(s-p_k),  K = Π(-p_k)  (щоб H(0)=1)
    K = 1.0
    for pk in poles:
        K *= (-pk)
    y = 1.0 + 0j
    for j, pj in enumerate(poles):
        denom = 1.0 + 0j
        for k, pk in enumerate(poles):
            if k != j:
                denom *= (pj - pk)
        # лишок H/s у полюсі pj:  K/(pj·Π_{k≠j}(pj-pk))
        res = K / (pj * denom)
        y += res * cmath.exp(pj * t)
    return y.real


def fig_step():
    W, H = 720, 410
    L, R, T, B = 70, 545, 56, 320
    plot_w, plot_h = R - L, B - T
    tmax = 16.0
    ymin, ymax = 0.0, 1.35

    def X(t):
        return L + (t / tmax) * plot_w

    def Y(v):
        return B - (v - ymin) / (ymax - ymin) * plot_h

    bp = butter_poles(4)
    cp = cheb_poles(4, 0.5088)        # 1 дБ
    frags = []

    for v in (0.0, 0.5, 1.0):
        y = Y(v)
        frags.append(line(L, y, R, y, color="#e3e6ea", sw=1))
        frags.append(text(L - 8, y + 4, ("%.1f" % v), size=11, color=MUTED, anchor="end"))
    frags.append(line(L, Y(1.0), R, Y(1.0), color=MUTED, sw=1.2, dash="5,4"))
    for t in (0, 4, 8, 12, 16):
        x = X(t)
        frags.append(line(x, T, x, B, color="#eef0f3", sw=1))
        frags.append(text(x, B + 18, "%d" % t, size=11, color=MUTED))
    frags.append(line(L, T, L, B, color=INK, sw=1.6))
    frags.append(line(L, B, R, B, color=INK, sw=1.6))

    # вхідна сходинка
    frags.append(line(X(0), Y(1.0), X(0), Y(0.0), color=MUTED, sw=1.4))

    def curve(poles, color, dash=None):
        pts = []
        steps = 420
        for i in range(steps + 1):
            t = tmax * i / steps
            v = step_response(poles, t)
            v = max(min(v, ymax), ymin)
            pts.append("%.1f,%.1f" % (X(t), Y(v)))
        da = ' stroke-dasharray="%s"' % dash if dash else ''
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"%s/>'
                % (" ".join(pts), color, da))

    frags.append(curve(cp, C_CHE))
    frags.append(curve(bp, C_BUT))
    frags.append(curve(BESSEL4, C_BES))

    frags.append(text((L + R) / 2, B + 40, "час  (умовні одиниці)", size=13, color=INK))
    frags.append(text(L - 46, (T + B) / 2, "вихід", size=13, color=INK))

    # легенда
    lx, ly = R + 16, 92
    rows = [("Бесель", C_BES, "без викиду"),
            ("Баттерворт", C_BUT, "малий викид"),
            ("Чебишов 1 дБ", C_CHE, "дзвін, викид")]
    frags.append(text(lx + 55, ly - 22, "відгук на", size=12, color=INK, bold=True))
    frags.append(text(lx + 55, ly - 6, "сходинку", size=12, color=INK, bold=True))
    for i, (name, col, note) in enumerate(rows):
        yy = ly + 22 + i * 52
        frags.append(line(lx, yy, lx + 26, yy, color=col, sw=3))
        frags.append(text(lx + 32, yy + 4, name, size=11.5, color=INK, anchor="start", bold=True))
        frags.append(text(lx, yy + 21, note, size=10, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "step-response.svg"), W, H, *frags,
           title="Та сама смуга — різний характер у часі")


if __name__ == "__main__":
    fig_shapes()
    fig_tradeoff()
    fig_step()
    print("OK figs")
