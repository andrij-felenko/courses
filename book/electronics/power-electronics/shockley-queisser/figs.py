# -*- coding: utf-8 -*-
"""Фігури до статті «Межа Шоклі–Квайссера»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_curve():
    """Гранична ефективність одного переходу як функція Eg: пік від двох втрат."""
    W, H = 780, 470
    L, R, T, B = 90, 730, 70, 390
    eg0, eg1, et1 = 0.5, 3.0, 0.36

    def X(eg): return L + (eg - eg0) / (eg1 - eg0) * (R - L)
    def Y(et): return B - (et / et1) * (B - T)

    f = []
    f.append(text(L, 52, "гранична ефективність η, %", 12, MUTED, anchor="start"))
    # осі
    f.append(line(L, T, L, B, INK, 2))
    f.append(line(L, B, R, B, INK, 2))
    for p in (0.0, 0.1, 0.2, 0.3):
        y = Y(p)
        f.append(line(L - 5, y, L, y, INK, 1.5))
        f.append(text(L - 10, y + 4, "%d" % (p * 100), 12, INK, anchor="end"))
    for e in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0):
        x = X(e)
        f.append(line(x, B, x, B + 5, INK, 1.5))
        f.append(text(x, B + 22, "%.1f" % e, 12, INK))
    f.append(text((L + R) / 2, H - 16, "ширина забороненої зони Eg (еВ)", 13, INK))

    # крива η(Eg) — форма межі детального балансу (AM1.5G, схематично)
    pts = [(0.5, 0.135), (0.6, 0.185), (0.7, 0.235), (0.8, 0.272), (0.9, 0.298),
           (1.0, 0.316), (1.1, 0.328), (1.2, 0.334), (1.34, 0.337), (1.45, 0.335),
           (1.6, 0.322), (1.75, 0.302), (1.9, 0.275), (2.05, 0.245), (2.2, 0.212),
           (2.4, 0.170), (2.6, 0.132), (2.8, 0.100), (3.0, 0.078)]
    poly = " ".join("%.1f,%.1f" % (X(e), Y(v)) for e, v in pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (poly, NEG))

    # пік (оптимум)
    px, py = X(1.34), Y(0.337)
    f.append(line(px, py, px, B, MUTED, 1, "5 4"))
    f.append(circle(px, py, 5, NEG, NEG, 1))
    box, _, _ = textbox(508, 60, "оптимум ≈ 1.34 еВ · 33.7%", 13, fill="#eef2ff", stroke=NEG)
    f.append(box)

    # кремній
    sx, sy = X(1.12), Y(0.329)
    f.append(circle(sx, sy, 4, INK, INK, 1))
    f.append(line(sx, sy + 4, sx, sy + 30, MUTED, 1))
    box, _, _ = textbox(sx, sy + 56, "кремній\n1.12 еВ", 12, fill=BG, stroke=MUTED)
    f.append(box)

    # два режими втрат
    box, _, _ = textbox(180, 305, "малий Eg:\nнадлишок гріє\n(термалізація)", 12,
                        fill="#fdecea", stroke=POS, color=INK)
    f.append(box)
    box, _, _ = textbox(602, 160, "великий Eg:\nмало спійманих\nфотонів (прозорість)", 12,
                        fill="#eaf0fd", stroke=NEG, color=INK)
    f.append(box)

    render(os.path.join(OUT, "efficiency-vs-bandgap.svg"), W, H, *f,
           title="Гранична ефективність одного переходу залежно від Eg")


def fig_photon():
    """Доля фотона за його енергією відносно Eg: прозорість, точна лічба, термалізація."""
    W, H = 820, 460
    xL, xR = 235, 760          # межі зон
    yC, yV = 200, 330          # дно зони провідності / верх валентної
    f = []

    # тло забороненої зони
    f.append(rect(xL, yC, xR - xL, yV - yC, fill="#f4f6f8", stroke="none", sw=0))
    # лінії країв зон
    f.append(line(xL, yC, xR, yC, INK, 2))
    f.append(line(xL, yV, xR, yV, INK, 2))
    f.append(text(xL - 12, yC + 4, "дно зони провідності", 13, INK, anchor="end"))
    f.append(text(xL - 12, yV + 4, "верх валентної зони", 13, INK, anchor="end"))

    # позначка Eg зліва
    gx = 200
    f.append(line(gx, yC, gx, yV, FIELD, 2))
    f.append(line(gx - 6, yC, gx + 6, yC, FIELD, 2))
    f.append(line(gx - 6, yV, gx + 6, yV, FIELD, 2))
    f.append(text(gx - 12, (yC + yV) / 2 + 5, "Eg", 15, FIELD, anchor="end", bold=True))

    # три фотони
    cols = [
        (330, 258, MUTED, "E < Eg"),   # не доходить
        (505, yC, FIELD, "E = Eg"),    # рівно
        (665, 96, POS, "E > Eg"),      # з надлишком
    ]
    for cx, top, col, lab in cols:
        f.append(text(cx, top - 12, lab, 14, col, bold=True))

    # фотон 1 — не доходить до зони провідності
    f.append(line(330, yV, 330, 258, MUTED, 3, "6 5"))
    f.append(arrow(330, 264, 330, 256, MUTED, 3))
    f.append(text(348, 252, "не доходить", 12, MUTED, anchor="start"))

    # фотон 2 — рівно Eg
    f.append(arrow(505, yV, 505, yC, FIELD, 3.2))

    # фотон 3 — з надлишком; надлишок скидається в тепло
    f.append(arrow(665, yV, 665, 96, POS, 3.2))
    f.append(arrow(690, 100, 690, yC - 3, POS, 2.6))
    f.append(text(704, (96 + yC) / 2, "надлишок → тепло", 12, POS, anchor="start"))
    f.append(line(648, yC, 648, yV, FIELD, 2, "3 3"))
    f.append(text(636, (yC + yV) / 2 + 4, "лишається Eg", 11, FIELD, anchor="end"))

    # підсумкові плашки під зонами
    box = fitbox(250, 388, 160, 52, "проходить наскрізь\n(не поглинається)", 12,
                 fill="#f4f6f8", stroke=MUTED)
    f.append(box)
    box = fitbox(430, 388, 150, 52, "уся енергія\n→ струм", 12, fill="#eafaf1", stroke=FIELD)
    f.append(box)
    box = fitbox(600, 388, 175, 52, "Eg → струм,\nнадлишок → тепло", 12, fill="#fdecea", stroke=POS)
    f.append(box)

    render(os.path.join(OUT, "photon-fates.svg"), W, H, *f,
           title="Доля фотона залежно від його енергії")


def fig_two_questions():
    """Історичний злам: чим питання 1961 року відрізнялося від питань 1955-го."""
    W, H = 900, 500
    f = []

    # дві панелі
    f.append(rect(25, 52, 415, 404, fill="#fafbfc", stroke=MUTED, sw=1.4, rx=10))
    f.append(rect(460, 52, 415, 404, fill="#fafbfc", stroke=MUTED, sw=1.4, rx=10))
    f.append(text(232.5, 80, "до 1961: «наскільки добрий наш кристал?»", 14, MUTED, bold=True))
    f.append(text(667.5, 80, "1961: «що взагалі дозволяє фізика?»", 14, INK, bold=True))

    tops = (106, 186, 266, 346)

    left = [
        ("чистота й досконалість кристала", "#e9ecef", MUTED),
        ("звідси — струм насичення j₀", "#e9ecef", MUTED),
        ("Voc = (kT/q)·ln(Jsc/j₀)", "#fdecea", POS),
        ("стеля ККД", "#fdecea", POS),
    ]
    right = [
        ("температура елемента 300 K і Eg", "#eaf0fd", NEG),
        ("потік теплових фотонів над Eg\n(детальний баланс)", "#eaf0fd", NEG),
        ("j₀ не може бути меншим за q·Φ", "#eafaf1", FIELD),
        ("стеля ККД", "#eafaf1", FIELD),
    ]

    for x0, cx, chain in ((55, 232.5, left), (490, 667.5, right)):
        for i, (s, fill, col) in enumerate(chain):
            y = tops[i]
            f.append(fitbox(x0, y, 355, 54, s, 13, fill=fill, stroke=col))
            if i < 3:
                f.append(arrow(cx, y + 54, cx, tops[i + 1] - 3, col, 1.8))

    box, _, _ = textbox(232.5, 428, "у кожного автора — своя", 13,
                        fill=BG, stroke=POS, color=POS, bold=True)
    f.append(box)
    box, _, _ = textbox(667.5, 428, "одна на всі технології", 13,
                        fill=BG, stroke=FIELD, color=FIELD, bold=True)
    f.append(box)

    render(os.path.join(OUT, "two-questions.svg"), W, H, *f,
           title="Дві постановки того самого питання")


def fig_cascade():
    """Розклад ККД на три множники — так, як його подали в праці 1961 року."""
    W, H = 860, 500
    B = 360          # базова лінія
    FULL = 260       # висота стовпця «100%»
    f = []

    f.append(line(40, B, 820, B, INK, 2))

    bars = [
        (120, 1.000, "100%", "#e9ecef", MUTED, "усе сонячне світло,\nщо падає"),
        (320, 0.440, "44%", "#eaf0fd", NEG, "мінус прозорість\nі термалізація"),
        (520, 0.339, "34%", "#fdecea", POS, "мінус неминуче\nвипромінювання"),
        (720, 0.293, "≈30%", "#eafaf1", FIELD, "мінус форма ВАХ\n(робоча точка)"),
    ]
    for cx, frac, lab, fill, col, cap in bars:
        h = FULL * frac
        f.append(rect(cx - 46, B - h, 92, h, fill=fill, stroke=col, sw=2, rx=4))
        f.append(text(cx, B - h - 12, lab, 15, col, bold=True))
        f.append(fitbox(cx - 89, 390, 178, 62, cap, 12, fill=BG, stroke=MUTED))

    for cx, lab in ((220, "×u = 0.44"), (420, "×v = 0.77"), (620, "×m = 0.865")):
        f.append(text(cx, 178, lab, 13, INK, bold=True))

    f.append(text(430, 478,
                  "η = u · v · m ≈ 0.44 · 0.77 · 0.865 ≈ 0.30   "
                  "(Eg = 1.1 еВ, Сонце 6000 K, елемент 300 K)", 12, MUTED))

    render(os.path.join(OUT, "sq-cascade.svg"), W, H, *f,
           title="Звідки взялися 30%: три множники праці 1961 року")


import math

# ── дані до вставки math-detailed-balance-derivation ────────────────────────
kTS = 0.51704          # kTs при Ts = 6000 K, еВ


def _phi(E):
    """Потік фотонів чорного тіла 6000 K на одиницю енергії, у частках від піку."""
    if E <= 0:
        return 0.0
    x = E / kTS
    if x > 60:
        return 0.0
    return (x * x / math.expm1(x)) / kTS / 1.2525168369181205


def fig_marginal():
    """Умова оптимуму спектрального множника: площа хвоста = Eg·φ(Eg)."""
    W, H = 860, 480
    L, R, T, B = 100, 800, 100, 380
    XMAX, YMAX = 4.2, 1.06
    EG, PHI_EG = 1.12, 0.938

    def X(e): return L + e / XMAX * (R - L)
    def Y(v): return B - v / YMAX * (B - T)

    f = []
    f.append(text(W / 2, 56, "потік фотонів Сонця (чорне тіло 6000 K): у найкращому порозі дві площі рівні",
                  13, MUTED))
    f.append(text(L, 84, "φ(E) — фотонів на одиницю енергії", 12, MUTED, anchor="start"))

    curve = [(e / 20.0, _phi(e / 20.0)) for e in range(0, int(XMAX * 20) + 1)]

    # хвіст над порогом — виграш
    tail = ["%.1f,%.1f" % (X(EG), B)]
    tail += ["%.1f,%.1f" % (X(e), Y(v)) for e, v in curve if e >= EG]
    tail.append("%.1f,%.1f" % (X(XMAX), B))
    f.append('<polygon points="%s" fill="#e8eefc" stroke="none"/>' % " ".join(tail))

    # прямокутник Eg·φ(Eg) — втрата
    f.append(rect(L, Y(PHI_EG), X(EG) - L, B - Y(PHI_EG), fill="#fdecea", stroke=POS, sw=1.4, rx=0))

    # сама крива
    poly = " ".join("%.1f,%.1f" % (X(e), Y(v)) for e, v in curve)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (poly, INK))

    # осі
    f.append(line(L, T, L, B, INK, 2))
    f.append(line(L, B, R, B, INK, 2))
    for e in (0, 1, 2, 3, 4):
        f.append(line(X(e), B, X(e), B + 5, INK, 1.5))
        f.append(text(X(e), B + 21, "%d" % e, 12, INK))
    f.append(text((L + R) / 2, H - 14, "енергія фотона E (еВ)", 13, INK))

    # поріг
    f.append(line(X(EG), Y(PHI_EG), X(EG), B, FIELD, 2, "5 4"))
    f.append(circle(X(EG), Y(PHI_EG), 5, FIELD, FIELD, 1))
    f.append(line(X(EG), B, X(EG), B + 5, FIELD, 2))
    f.append(text(X(EG), B + 44, "поріг Eg = 1.12 еВ", 12, FIELD, bold=True))

    box, _, _ = textbox((L + X(EG)) / 2, 256, "втрата: Eg·φ(Eg)\nфотони на самій межі",
                        12, fill=BG, stroke=POS)
    f.append(box)
    box, _, _ = textbox(560, 200, "виграш: Φ(Eg)\nусі фотони над порогом", 12, fill=BG, stroke=NEG)
    f.append(box)
    f.append(line(560, 226, 560, 302, MUTED, 1))

    render(os.path.join(OUT, "marginal-balance.svg"), W, H, *f,
           title="Умова оптимуму: Φ(Eg) = Eg·φ(Eg)")


# (Eg, u, v, m, η) — детальний баланс, Ts = 6000 K, Tc = 300 K
UVM = [(0.80, 0.4070, 0.7367, 0.8252, 0.2474), (0.88, 0.4214, 0.7534, 0.8396, 0.2666),
       (0.96, 0.4313, 0.7677, 0.8517, 0.2820), (1.04, 0.4370, 0.7800, 0.8619, 0.2938),
       (1.12, 0.4388, 0.7908, 0.8708, 0.3021), (1.20, 0.4371, 0.8003, 0.8785, 0.3073),
       (1.28, 0.4323, 0.8087, 0.8852, 0.3095), (1.36, 0.4249, 0.8162, 0.8912, 0.3091),
       (1.44, 0.4151, 0.8229, 0.8966, 0.3063), (1.52, 0.4034, 0.8290, 0.9014, 0.3015),
       (1.60, 0.3901, 0.8346, 0.9058, 0.2949), (1.68, 0.3755, 0.8397, 0.9097, 0.2868),
       (1.76, 0.3599, 0.8443, 0.9134, 0.2776), (1.84, 0.3437, 0.8486, 0.9167, 0.2673),
       (1.92, 0.3270, 0.8525, 0.9197, 0.2564), (2.00, 0.3100, 0.8561, 0.9226, 0.2448),
       (2.08, 0.2929, 0.8595, 0.9252, 0.2330), (2.16, 0.2760, 0.8627, 0.9276, 0.2209),
       (2.24, 0.2593, 0.8656, 0.9299, 0.2087), (2.32, 0.2430, 0.8683, 0.9320, 0.1967),
       (2.40, 0.2271, 0.8709, 0.9340, 0.1847), (2.48, 0.2118, 0.8733, 0.9358, 0.1731),
       (2.56, 0.1970, 0.8756, 0.9376, 0.1617)]


def fig_shift():
    """Три множники ККД і зсув оптимуму: u падає, v і m ростуть."""
    W, H = 860, 500
    L, R, T, B = 100, 790, 100, 400
    E0, E1 = 0.8, 2.6

    def X(e): return L + (e - E0) / (E1 - E0) * (R - L)
    def Y(v): return B - v * (B - T)

    f = []
    f.append(text(W / 2, 56, "усі три множники як функції порога Eg (Ts = 6000 K, Tc = 300 K)",
                  13, MUTED))
    f.append(text(L, 84, "частка (0…1)", 12, MUTED, anchor="start"))

    f.append(line(L, T, L, B, INK, 2))
    f.append(line(L, B, R, B, INK, 2))
    for v in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
        f.append(line(L - 5, Y(v), L, Y(v), INK, 1.5))
        f.append(text(L - 10, Y(v) + 4, "%.1f" % v, 12, INK, anchor="end"))
    for e in (0.8, 1.2, 1.6, 2.0, 2.4):
        f.append(line(X(e), B, X(e), B + 5, INK, 1.5))
        f.append(text(X(e), B + 21, "%.1f" % e, 12, INK))
    f.append(text((L + R) / 2, H - 14, "ширина забороненої зони Eg (еВ)", 13, INK))

    for idx, col, sw in ((3, FIELD, 2.2), (2, NEG, 2.2), (1, POS, 2.2), (4, INK, 3.0)):
        poly = " ".join("%.1f,%.1f" % (X(p[0]), Y(p[idx])) for p in UVM)
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>'
                 % (poly, col, sw))

    # піки
    f.append(line(X(1.12), Y(0.4388), X(1.12), B, MUTED, 1, "5 4"))
    f.append(line(X(1.306), Y(0.3096), X(1.306), B, MUTED, 1, "5 4"))
    f.append(circle(X(1.12), Y(0.4388), 5, POS, POS, 1))
    f.append(circle(X(1.306), Y(0.3096), 5, INK, INK, 1))

    # легенда
    lx, ly, lw, lh = 505, 172, 268, 112
    f.append(rect(lx, ly, lw, lh, fill=BG, stroke=MUTED, sw=1))
    rows = [(POS, "u — спектральний множник"), (NEG, "v = qVoc/Eg — напруга"),
            (FIELD, "m — коефіцієнт заповнення"), (INK, "η = u·v·m")]
    for i, (col, lab) in enumerate(rows):
        yy = ly + 26 + i * 24
        f.append(line(lx + 14, yy - 4, lx + 40, yy - 4, col, 3))
        f.append(text(lx + 50, yy, lab, 12, INK, anchor="start"))

    box, _, _ = textbox(432, 360, "оптимум зсунувся: 1.12 → 1.31 еВ\nu падає, а v·m росте",
                        12, fill=BG, stroke=INK)
    f.append(box)

    render(os.path.join(OUT, "optimum-shift.svg"), W, H, *f,
           title="Чому пік η стоїть правіше за пік спектрального множника")


def fig_notch():
    """Чому поріг вигідно ставити відразу за смугою поглинання (схема)."""
    W, H = 840, 470
    L, R, T, B = 100, 780, 110, 360
    E0, E1, YMAX = 0.85, 1.85, 1.12
    BANDS = ((1.10, 0.55, 0.022), (1.32, 0.48, 0.026), (1.63, 0.33, 0.011))

    def X(e): return L + (e - E0) / (E1 - E0) * (R - L)
    def Y(v): return B - v / YMAX * (B - T)

    def flux(e):
        base = _phi(e)
        tr = 1.0
        for e0, d, s in BANDS:
            tr -= d * math.exp(-((e - e0) ** 2) / (2 * s * s))
        return base * max(tr, 0.02)

    pts = [(E0 + i / 400.0, flux(E0 + i / 400.0)) for i in range(0, 401)]

    f = []
    f.append(text(W / 2, 56, "схема: наземний спектр із провалами поглинання (глибини — умовні)",
                  13, MUTED))
    f.append(text(L, 88, "φ(E) — фотонів на одиницю енергії", 12, MUTED, anchor="start"))

    def slab(a, b, col):
        p = ["%.1f,%.1f" % (X(a), B)]
        p += ["%.1f,%.1f" % (X(e), Y(v)) for e, v in pts if a <= e <= b]
        p.append("%.1f,%.1f" % (X(b), B))
        return '<polygon points="%s" fill="%s" stroke="none"/>' % (" ".join(p), col)

    f.append(slab(1.18, 1.26, "#fdecea"))
    f.append(slab(1.26, 1.34, "#eafaf1"))

    poly = " ".join("%.1f,%.1f" % (X(e), Y(v)) for e, v in pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (poly, INK))

    f.append(line(L, T, L, B, INK, 2))
    f.append(line(L, B, R, B, INK, 2))
    for e in (0.9, 1.1, 1.3, 1.5, 1.7):
        f.append(line(X(e), B, X(e), B + 5, INK, 1.5))
        f.append(text(X(e), B + 21, "%.1f" % e, 12, INK))
    f.append(text((L + R) / 2, H - 14, "енергія фотона E (еВ)", 13, INK))

    for e, col in ((1.18, POS), (1.26, MUTED), (1.34, FIELD)):
        f.append(line(X(e), Y(flux(e)), X(e), B, col, 1.6, "4 4"))
        f.append(text(X(e), B + 42, "%.2f" % e, 12, col, bold=True))

    f.append(text(420, 150, "смуга водяної пари ≈940 нм", 12, NEG))
    f.append(arrow(420, 160, 420, 262, NEG, 1.6))

    box, _, _ = textbox(206, 272, "рівна ділянка:\nкрок 0.08 еВ забирає\nбагато фотонів",
                        12, fill=BG, stroke=POS)
    f.append(box)
    f.append(line(292, 272, 330, 272, MUTED, 1))
    box, _, _ = textbox(614, 288, "через смугу:\nтой самий крок\nмайже без втрат",
                        12, fill=BG, stroke=FIELD)
    f.append(box)
    f.append(line(530, 288, 452, 288, MUTED, 1))

    render(os.path.join(OUT, "spectrum-notch.svg"), W, H, *f,
           title="Поріг вигідно ставити відразу за смугою поглинання")


# ── фізика до вставки proj-sq-curve ─────────────────────────────────────────
_SQ_H, _SQ_C, _SQ_KB, _SQ_Q = 6.62607015e-34, 2.99792458e8, 1.380649e-23, 1.602176634e-19
_SQ_HC = 1239.841984            # еВ·нм
_SQ_VT = _SQ_KB * 300.0 / _SQ_Q  # тепловий потенціал, В


def _sq_blackbody(T=5800.0, half_deg=0.2665, lo=100.0, hi=1.0e5, ratio=1.002):
    om = 2 * math.pi * (1 - math.cos(math.radians(half_deg)))
    rows, lam = [], lo
    while lam <= hi:
        L = lam * 1e-9
        B = 2 * _SQ_H * _SQ_C * _SQ_C / L**5 / (math.exp(_SQ_H * _SQ_C / (L * _SQ_KB * T)) - 1)
        rows.append((lam, B * om * 1e-9))
        lam *= ratio
    return rows


def _sq_ladder(rows):
    lam = [r[0] for r in rows]
    nph = [w * l * 1e-9 / (_SQ_H * _SQ_C) for l, w in rows]
    cum, pin = [0.0], 0.0
    for k in range(1, len(rows)):
        d = lam[k] - lam[k - 1]
        cum.append(cum[-1] + 0.5 * (nph[k] + nph[k - 1]) * d)
        pin += 0.5 * (rows[k][1] + rows[k - 1][1]) * d
    return lam, nph, cum, pin


def _sq_at(x, xs, ys):
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    lo, hi = 0, len(xs) - 1
    while hi - lo > 1:
        m = (lo + hi) // 2
        if xs[m] <= x:
            lo = m
        else:
            hi = m
    t = (x - xs[lo]) / (xs[hi] - xs[lo])
    return ys[lo] + t * (ys[hi] - ys[lo])


def _sq_emitted(Eg, T=300.0, terms=3):
    s = 0.0
    for n in range(1, terms + 1):
        u = _SQ_KB * T / _SQ_Q / n
        s += u * math.exp(-Eg / u) * (Eg * Eg + 2 * Eg * u + 2 * u * u)
    return math.pi * (2.0 / (_SQ_H**3 * _SQ_C**2)) * _SQ_Q**3 * s


def fig_ladder():
    """Один прохід по спектру: кожен поріг Eg — це вибірка з накопиченої драбини."""
    rows = _sq_blackbody()
    lam, nph, cum, _ = _sq_ladder(rows)
    total = cum[-1]

    W, H = 900, 640
    L, R = 120, 800
    A_T, A_B = 116, 282           # верхня панель: густина потоку
    B_T, B_B = 392, 552           # нижня панель: драбина
    l0, l1 = 300.0, 2400.0
    nmax = 5.4e18

    def X(l): return L + (l - l0) / (l1 - l0) * (R - L)
    def YA(n): return A_B - n / nmax * (A_B - A_T)
    def YB(fr): return B_B - fr * (B_B - B_T)

    lg = _SQ_HC / 1.12            # 1107 нм — поріг кремнію
    lp = _SQ_HC / 1.27            # 976 нм — поріг оптимуму
    frac_g = _sq_at(lg, lam, cum) / total
    frac_p = _sq_at(lp, lam, cum) / total

    f = []
    step = 12.0
    pts = [(l0 + step * i) for i in range(int((l1 - l0) / step) + 1)]

    # ── панель A: густина потоку фотонів ────────────────────────────────
    f.append(text(L, A_T - 44, "потік фотонів на нанометр (Сонце як чорне тіло 5800 K)",
                  13, MUTED, anchor="start"))
    shade = ["%.1f,%.1f" % (X(l0), YA(0))]
    shade += ["%.1f,%.1f" % (X(l), YA(_sq_at(l, lam, nph))) for l in pts if l <= lg]
    shade += ["%.1f,%.1f" % (X(lg), YA(_sq_at(lg, lam, nph))), "%.1f,%.1f" % (X(lg), YA(0))]
    f.append('<polygon points="%s" fill="#e6ecfb" stroke="none"/>' % " ".join(shade))
    poly = " ".join("%.1f,%.1f" % (X(l), YA(_sq_at(l, lam, nph))) for l in pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (poly, NEG))
    f.append(line(L, A_B, R, A_B, INK, 2))
    f.append(line(L, A_B, L, A_T, INK, 2))
    f.append(text(L + 60, A_B - 34, "ці фотони поріг 1.12 еВ ловить", 12, NEG, anchor="start"))

    # ── панель B: драбина ───────────────────────────────────────────────
    f.append(text(L, B_T - 30, "драбина: частка всіх фотонів, коротших за λ",
                  13, MUTED, anchor="start"))
    poly = " ".join("%.1f,%.1f" % (X(l), YB(_sq_at(l, lam, cum) / total)) for l in pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (poly, FIELD))
    f.append(line(L, B_B, R, B_B, INK, 2))
    f.append(line(L, B_B, L, B_T, INK, 2))
    for fr in (0.25, 0.5, 0.75):
        y = YB(fr)
        f.append(line(L - 5, y, L, y, INK, 1.5))
        f.append(text(L - 10, y + 4, "%d%%" % (fr * 100), 12, INK, anchor="end"))
    for i in range(8):
        l = l0 + 300 * i
        x = X(l)
        f.append(line(x, B_B, x, B_B + 5, INK, 1.5))
        f.append(text(x, B_B + 23, "%d" % l, 12, INK))
    f.append(text((L + R) / 2, H - 26, "довжина хвилі λ, нм", 13, INK))

    # ── два пороги наскрізь по обох панелях ─────────────────────────────
    for l, fr, col in ((lp, frac_p, MUTED), (lg, frac_g, POS)):
        x = X(l)
        f.append(line(x, A_T - 6, x, A_B, col, 1.6, "5 4"))
        f.append(line(x, B_T - 6, x, YB(fr), col, 1.6, "5 4"))
        f.append(circle(x, YB(fr), 5, col, col, 1))
    f.append(text(X(lp) - 12, A_T - 14, "Eg = 1.27 еВ", 12, MUTED, anchor="end"))
    f.append(text(X(lg) + 12, A_T - 14, "Eg = 1.12 еВ ⇔ λ = 1107 нм", 12, POS, anchor="start"))

    box, _, _ = textbox(X(lg) + 172, YB(frac_g) + 2,
                        "%.1f%% усіх фотонів\nкоротші за 1107 нм" % (frac_g * 100),
                        12, fill="#fdecea", stroke=POS)
    f.append(box)
    f.append(line(X(lg) + 8, YB(frac_g), X(lg) + 82, YB(frac_g), POS, 1.2))

    box, _, _ = textbox(X(lp) - 96, YB(frac_p) - 8, "%.1f%%" % (frac_p * 100),
                        12, fill=BG, stroke=MUTED)
    f.append(box)
    f.append(line(X(lp) - 62, YB(frac_p) - 8, X(lp) - 6, YB(frac_p) - 4, MUTED, 1.2))

    render(os.path.join(OUT, "photon-ladder.svg"), W, H, *f,
           title="Одна протяжка по спектру обслуговує всі пороги одразу")


def fig_mpp():
    """Робоча точка максимуму: що саме знаходить ітерація v = voc − ln(1+v)."""
    rows = _sq_blackbody()
    lam, nph, cum, pin = _sq_ladder(rows)
    Jsc = _SQ_Q * _sq_at(_SQ_HC / 1.12, lam, cum)
    J0 = _SQ_Q * _sq_emitted(1.12)
    voc = math.log(Jsc / J0 + 1.0)
    v, trail = voc, []
    for _ in range(4):
        v = voc - math.log(1.0 + v)
        trail.append(v * _SQ_VT)
    Vmp, Voc = v * _SQ_VT, voc * _SQ_VT
    Pmax = _SQ_VT * (v * v / (1.0 + v)) * (Jsc + J0)
    Jmp = Pmax / Vmp

    W, H = 900, 560
    L, R, T, B = 120, 700, 116, 400
    vmax, jmax, pmax = 0.95, 600.0, 450.0

    def X(V): return L + V / vmax * (R - L)
    def YJ(J): return B - J / jmax * (B - T)
    def YP(P): return B - P / pmax * (B - T)

    f = []
    f.append(text(L - 34, T - 34, "струм J, А/м²", 13, NEG, anchor="start"))
    f.append(text(R + 34, T - 34, "потужність P = J·V, Вт/м²", 13, POS, anchor="end"))

    f.append(rect(X(0), YJ(Jmp), X(Vmp) - X(0), B - YJ(Jmp),
                  fill="#eef2ff", stroke="none", sw=0, rx=0))

    f.append(line(L, B, R, B, INK, 2))
    f.append(line(L, B, L, T, INK, 2))
    f.append(line(R, B, R, T, INK, 2))
    for J in (200, 400, 600):
        y = YJ(J)
        f.append(line(L - 5, y, L, y, NEG, 1.5))
        f.append(text(L - 10, y + 4, "%d" % J, 12, NEG, anchor="end"))
    for P in (150, 300, 450):
        y = YP(P)
        f.append(line(R, y, R + 5, y, POS, 1.5))
        f.append(text(R + 10, y + 4, "%d" % P, 12, POS, anchor="start"))
    for V in (0.0, 0.2, 0.4, 0.6, 0.8):
        x = X(V)
        f.append(line(x, B, x, B + 5, INK, 1.5))
        f.append(text(x, B + 23, "%.1f" % V, 12, INK))
    f.append(text((L + R) / 2, B + 50, "напруга V, В", 13, INK))

    n = 240
    jv, pv = [], []
    for i in range(n + 1):
        V = Voc * i / n
        J = Jsc - J0 * (math.exp(V / _SQ_VT) - 1.0)
        if J < 0:
            break
        jv.append("%.1f,%.1f" % (X(V), YJ(J)))
        pv.append("%.1f,%.1f" % (X(V), YP(J * V)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join(jv), NEG))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
             'stroke-dasharray="7 4"/>' % (" ".join(pv), POS))

    f.append(circle(X(Vmp), YJ(Jmp), 5.5, NEG, NEG, 1))
    f.append(circle(X(Vmp), YP(Pmax), 5.5, POS, POS, 1))
    f.append(circle(X(Voc), YJ(0), 5, BG, NEG, 2))
    f.append(circle(X(0), YJ(Jsc), 5, BG, NEG, 2))

    box, _, _ = textbox(X(0.17), YJ(Jsc) - 40, "Jsc = %.0f А/м²" % Jsc, 12,
                        fill=BG, stroke=NEG)
    f.append(box)
    box, _, _ = textbox(X(0.80), YJ(0) - 42, "Voc = %.3f В" % Voc, 12, fill=BG, stroke=NEG)
    f.append(box)
    box, _, _ = textbox(X(0.30), YP(Pmax) + 62,
                        "MPP:  %.3f В · %.0f А/м²\nPmax = %.0f Вт/м²   FF = %.3f"
                        % (Vmp, Jmp, Pmax, Pmax / (Voc * Jsc)), 12,
                        fill="#fdecea", stroke=POS)
    f.append(box)

    f.append(fitbox(L - 20, H - 76, R - L + 130, 50,
                    "ітерація v = voc − ln(1+v):   %.4f → %.4f → %.5f → %.6f В"
                    % tuple(trail), 13, fill=FILL, stroke=MUTED))

    render(os.path.join(OUT, "mpp-fixed-point.svg"), W, H, *f,
           title="Що знаходить нерухома точка: робоча точка максимуму")


if __name__ == "__main__":
    fig_curve()
    fig_photon()
    fig_two_questions()
    fig_cascade()
    fig_marginal()
    fig_shift()
    fig_notch()
    fig_ladder()
    fig_mpp()
    print("ok:", os.listdir(OUT))
