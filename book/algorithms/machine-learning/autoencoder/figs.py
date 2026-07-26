# -*- coding: utf-8 -*-
"""Фігури до статті «Автокодер». Запуск із теки теми:  python figs.py
Виводить SVG у ./img/. Стиль — svgkit (єдина палітра репозиторію)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

CODEFILL = "#eafaf1"   # світло-зелена заливка вузлів коду


def column(cx, cy, n, spacing=42, r=13, fill=FILL, stroke=LINE):
    ys = [cy + (i - (n - 1) / 2.0) * spacing for i in range(n)]
    s = "".join(circle(cx, y, r, fill=fill, stroke=stroke) for y in ys)
    return s, ys


def connect(x1, ys1, x2, ys2, color=MUTED, sw=0.8, r=13):
    return "".join(line(x1 + r, y1, x2 - r, y2, color=color, sw=sw)
                   for y1 in ys1 for y2 in ys2)


# ── Фігура 1: пісочний годинник автокодера ──────────────────────────────────
def fig_hourglass():
    W, H = 840, 480
    cy = 220
    xs = [110, 250, 410, 570, 710]
    ns = [6, 4, 2, 4, 6]
    frags = []
    cols = []
    for x, n in zip(xs, ns):
        if x == 410:
            s, ys = column(x, cy, n, spacing=44, fill=CODEFILL, stroke=FIELD)
        else:
            s, ys = column(x, cy, n)
        cols.append((x, ys, s))
    # з'єднання між сусідніми колонками (тонкі, світлі) — під вузлами
    for i in range(len(cols) - 1):
        x1, ys1, _ = cols[i]
        x2, ys2, _ = cols[i + 1]
        frags.append(connect(x1, ys1, x2, ys2, color="#d7dbe0", sw=0.7))
    for _, _, s in cols:
        frags.append(s)
    # підписи колонок
    frags.append(text(110, 360, "вхід  x", size=15, bold=True))
    frags.append(text(410, 300, "код  z", size=15, bold=True, color=FIELD))
    frags.append(text(710, 360, "відновлення  x̂", size=15, bold=True))
    # підписи половин
    b1, w1, h1 = textbox(250, 96, "кодувальник", size=14, fill="#eef1f4")
    b2, w2, h2 = textbox(570, 96, "декодувальник", size=14, fill="#eef1f4")
    frags.append(b1); frags.append(b2)
    # нижня дужка похибки
    yb = 440
    frags.append(line(110, 380, 110, yb, color=MUTED, sw=1.2))
    frags.append(line(710, 380, 710, yb, color=MUTED, sw=1.2))
    frags.append(line(110, yb, 300, yb, color=MUTED, sw=1.2, dash="5 4"))
    frags.append(line(520, yb, 710, yb, color=MUTED, sw=1.2, dash="5 4"))
    bb, wb, hb = textbox(410, yb, "похибка відновлення   L = ‖x − x̂‖²",
                         size=14, fill="#fff6ec", stroke=POS)
    frags.append(bb)
    render(os.path.join(IMG, "hourglass.svg"), W, H, *frags)


# ── Фігура 2: многовид, код-координата й пласке наближення ───────────────────
def fig_manifold():
    W, H = 800, 450
    P0 = (140.0, 360.0); P1 = (410.0, 80.0); P2 = (670.0, 320.0)

    def q(t):
        mt = 1 - t
        x = mt * mt * P0[0] + 2 * mt * t * P1[0] + t * t * P2[0]
        y = mt * mt * P0[1] + 2 * mt * t * P1[1] + t * t * P2[1]
        return x, y

    def tangent(t):
        # B'(t) = 2[(1-t)(P1-P0) + t(P2-P1)]
        tx = 2 * ((1 - t) * (P1[0] - P0[0]) + t * (P2[0] - P1[0]))
        ty = 2 * ((1 - t) * (P1[1] - P0[1]) + t * (P2[1] - P1[1]))
        n = (tx * tx + ty * ty) ** 0.5
        return tx / n, ty / n

    frags = []
    # зелений маркер-стрілка для кривої-координати
    gmarker = ('<defs><marker id="garrow" viewBox="0 0 10 10" refX="9" refY="5" '
               'markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
               '<path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker></defs>' % FIELD)
    frags.append(gmarker)
    # пласке наближення (PCA) — штрихова пряма, проходить нижче горба
    frags.append(line(150, 352, 660, 312, color=NEG, sw=2.2, dash="7 5"))
    # точки даних поблизу многовида
    ts = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90]
    jit = [10, -12, 9, -8, 12, -10, 8, -13, 9]
    for t, j in zip(ts, jit):
        x, y = q(t)
        tx, ty = tangent(t)
        nx, ny = -ty, tx           # нормаль до кривої
        frags.append(circle(x + nx * j, y + ny * j, 5, fill=INK, stroke=INK))
    # сам многовид = координата коду (зелена крива зі стрілкою)
    frags.append('<path d="M%.0f,%.0f Q%.0f,%.0f %.0f,%.0f" fill="none" '
                 'stroke="%s" stroke-width="3.2" marker-end="url(#garrow)"/>'
                 % (P0[0], P0[1], P1[0], P1[1], P2[0], P2[1], FIELD))
    # підписи
    b1, w1, h1 = textbox(408, 52, "многовид даних  —  код z уздовж нього",
                         size=14, fill=CODEFILL, stroke=FIELD)
    frags.append(b1)
    b2, w2, h2 = textbox(405, 410, "пласке наближення (PCA) зрізає криву",
                         size=14, fill="#eef2fd", stroke=NEG)
    frags.append(b2)
    render(os.path.join(IMG, "manifold.svg"), W, H, *frags)


# ── Фігура 3: пастка тотожності vs знешумлювальний ──────────────────────────
def fig_identity_denoise():
    W, H = 880, 440
    cy = 215
    frags = []
    # роздільник
    frags.append(line(444, 70, 444, 390, color="#d7dbe0", sw=1.4, dash="4 5"))

    # ── ЛІВА панель: надповний код (тотожність) ──
    xi, xc, xo = 120, 240, 360
    si, yi = column(xi, cy, 4, spacing=48)
    sc, yc = column(xc, cy, 6, spacing=38, fill=CODEFILL, stroke=FIELD)
    so, yo = column(xo, cy, 4, spacing=48)
    # усі можливі зв'язки — тьмяні
    frags.append(connect(xi, yi, xc, yc, color="#e2e5e9", sw=0.6))
    frags.append(connect(xc, yc, xo, yo, color="#e2e5e9", sw=0.6))
    frags.append(si); frags.append(sc); frags.append(so)
    # виділені канали «один-в-один» — тотожність (перші 4 вузли коду)
    for k in range(4):
        frags.append(arrow(xi + 13, yi[k], xc - 13, yc[k], color=INK, sw=2.2))
        frags.append(arrow(xc + 13, yc[k], xo - 13, yo[k], color=INK, sw=2.2))
    b1, w1, h1 = textbox(240, 80, "надповний код (широкий)", size=14, fill="#eef1f4")
    frags.append(b1)
    b2, w2, h2 = textbox(240, 372, "тотожність: 0 похибки, 0 знань",
                         size=13.5, fill="#fdecea", stroke=POS)
    frags.append(b2)

    # ── ПРАВА панель: знешумлювальний (вузький код) ──
    xi2, xc2, xo2 = 560, 680, 800
    si2, yi2 = column(xi2, cy, 4, spacing=48)
    sc2, yc2 = column(xc2, cy, 2, spacing=48, fill=CODEFILL, stroke=FIELD)
    so2, yo2 = column(xo2, cy, 4, spacing=48)
    frags.append(connect(xi2, yi2, xc2, yc2, color="#d7dbe0", sw=0.8))
    frags.append(connect(xc2, yc2, xo2, yo2, color="#d7dbe0", sw=0.8))
    frags.append(si2); frags.append(sc2); frags.append(so2)
    # шум-хрестики на вході
    for k in (0, 2, 3):
        frags.append(text(xi2 - 22, yi2[k] + 5, "×", size=18, color=POS, bold=True))
    frags.append(text(xi2 - 26, yi2[0] - 30, "шум", size=12, color=POS))
    b3, w3, h3 = textbox(680, 80, "знешумлювальний (вузький код)", size=14, fill="#eef1f4")
    frags.append(b3)
    b4, w4, h4 = textbox(680, 372, "зіпсоване → чисте: мусить вчити структуру",
                         size=13.5, fill="#eafaf1", stroke=FIELD)
    frags.append(b4)

    render(os.path.join(IMG, "identity-denoise.svg"), W, H, *frags)


# ── Фігура 4 (вставка math-linear-pca): розкид = утримане + відкинуте ─────────
def fig_pca_variance():
    import math
    W, H = 940, 440
    frags = []
    frags.append(line(478, 70, 478, 400, color="#d7dbe0", sw=1.4, dash="4 5"))

    # ── ЛІВА панель: еліпс коваріації, проєкція, залишок ──
    C = (215.0, 232.0)
    th = -20.0 * math.pi / 180.0
    e1 = (math.cos(th), math.sin(th))          # старша вісь (вгору-праворуч)
    e2 = (-math.sin(th), math.cos(th))         # молодша вісь
    a, b = 128.0, 60.0                          # півосі ∝ √λ₁, √λ₂

    def pt(al, be):
        return (C[0] + al * e1[0] + be * e2[0], C[1] + al * e1[1] + be * e2[1])

    # сам еліпс (рівень коваріації)
    frags.append('<g transform="rotate(%.2f %.1f %.1f)">%s</g>'
                 % (-20.0, C[0], C[1],
                    '<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" '
                    'stroke="%s" stroke-width="1.6" opacity="0.9"/>'
                    % (C[0], C[1], a, b, "#eafaf1", FIELD)))
    # хмара точок
    cloud = [(-100, 18), (-78, -22), (-52, 30), (-30, -14), (-8, 22),
             (18, -26), (40, 14), (66, -18), (92, 10), (24, -40), (-60, 44)]
    for al, be in cloud:
        x, y = pt(al, be)
        frags.append(circle(x, y, 4, fill=INK, stroke=INK))
    # осі e1 (зелена), e2 (синя) з центра
    x1p, y1p = pt(a * 0.98, 0); x1m, y1m = pt(-a * 0.98, 0)
    x2p, y2p = pt(0, b * 0.98); x2m, y2m = pt(0, -b * 0.98)
    frags.append(line(x1m, y1m, x1p, y1p, color=FIELD, sw=2.4))
    frags.append(line(x2m, y2m, x2p, y2p, color=NEG, sw=2.0))
    frags.append(text(x1p + 18, y1p - 6, "e₁", size=15, bold=True, color=FIELD))
    e2lx, e2ly = pt(0, b * 0.98 + 26)
    frags.append(text(e2lx + 14, e2ly, "e₂", size=15, bold=True, color=NEG))
    # точка P, її проєкція Q на старшу вісь і залишок P→Q
    Px, Py = pt(64, 46); Qx, Qy = pt(64, 0)
    frags.append(line(Px, Py, Qx, Qy, color=POS, sw=2.0, dash="5 4"))
    frags.append(circle(Qx, Qy, 4.5, fill=BG, stroke=FIELD, sw=2))
    frags.append(circle(Px, Py, 5.5, fill=POS, stroke=POS))
    frags.append(text(Px + 14, Py + 4, "x", size=14, bold=True, italic=True))
    frags.append(text(Qx + 30, Qy + 22, "x̂ = проєкція", size=12.5, color=FIELD))
    bb, _, _ = textbox(Px + 74, Py + 2, "залишок ∝ √λ₂", size=12.5,
                       fill="#fdecea", stroke=POS)
    frags.append(bb)
    t1, _, _ = textbox(215, 44, "розкид точок = утримане + відкинуте",
                       size=13.5, fill="#eef1f4")
    frags.append(t1)

    # ── ПРАВА панель: спектр власних значень, зріз на k ──
    vals = [156, 100, 44, 24, 12, 6]
    k = 2
    x0, bw, gap, yB = 540, 42, 15, 352
    labels = ["λ₁", "λ₂", "λ₃", "λ₄", "λ₅", "λ₆"]
    frags.append(line(x0 - 16, yB, x0 + len(vals) * (bw + gap) + 2, yB,
                      color=MUTED, sw=1.4))
    for i, (v, lb) in enumerate(zip(vals, labels)):
        x = x0 + i * (bw + gap)
        kept = i < k
        col = FIELD if kept else POS
        fillc = "#eafaf1" if kept else "#fdecea"
        frags.append(rect(x, yB - v, bw, v, fill=fillc, stroke=col, sw=1.8, rx=3))
        frags.append(text(x + bw / 2, yB + 20, lb, size=13, bold=True, color=col))
    # дужки-підписи над утриманими й відкинутими
    xk = x0 + k * (bw + gap) - gap
    frags.append(line(x0, 92, xk, 92, color=FIELD, sw=1.6))
    frags.append(text((x0 + xk) / 2, 84, "лишаємо: λ₁+λ₂", size=12.5,
                      bold=True, color=FIELD))
    xr0 = x0 + k * (bw + gap); xr1 = x0 + len(vals) * (bw + gap) - gap
    frags.append(line(xr0, 250, xr1, 250, color=POS, sw=1.6))
    br, _, _ = textbox((xr0 + xr1) / 2, 232, "викидаємо:  J* = λ₃+λ₄+…",
                       size=12.5, fill="#fdecea", stroke=POS)
    frags.append(br)
    t2, _, _ = textbox(700, 44, "власні значення Σ (спадають)",
                       size=13.5, fill="#eef1f4")
    frags.append(t2)

    render(os.path.join(IMG, "pca-variance.svg"), W, H, *frags)


# ── Фігура 5 (вставка hist-birth): часова смуга народження автокодера ────────
def fig_timeline():
    W, H = 1000, 520
    axis_y = 270
    frags = []
    # (x на осі, бік, рік, короткий підпис)
    events = [
        (110, "below", "1985–86", "задача-\nкодувальник"),
        (230, "above", "1987", "образи\n(Коттрелл)"),
        (350, "below", "1988", "= SVD\n(Бурлар–Камп)"),
        (470, "above", "1989", "= PCA\n(Балді–Горнік)"),
        (680, "below", "2006", "глибокий, RBM\n(Гінтон, Science)"),
        (800, "above", "2008", "знешумлення\n(Венсан)"),
        (915, "below", "2013", "варіаційний\n(VAE)"),
    ]
    # вісь часу: суцільна — розрив «зими» штрихом — суцільна зі стрілкою
    frags.append(line(60, axis_y, 486, axis_y, color=INK, sw=2))
    frags.append(line(486, axis_y, 612, axis_y, color=MUTED, sw=2, dash="6 6"))
    frags.append(arrow(612, axis_y, 950, axis_y, color=INK, sw=2))
    frags.append(text(946, axis_y + 26, "час", size=13, color=MUTED,
                      anchor="end", italic=True))
    # маркер «зими» над розривом
    bwin, _, _ = textbox(549, axis_y - 44, "тиша ~15 років", size=12,
                         fill="#eef1f4", stroke=MUTED, color=MUTED)
    # події: конектор до краю рамки, вузол на осі, рамка зверху всього
    for x, side, year, label in events:
        b, w, h = textbox(x, 150 if side == "above" else 392,
                          year + "\n" + label, size=13)
        if side == "above":
            frags.append(line(x, axis_y - 7, x, 150 + h / 2, color=MUTED, sw=1))
        else:
            frags.append(line(x, axis_y + 7, x, 392 - h / 2, color=MUTED, sw=1))
        frags.append(circle(x, axis_y, 7, fill=CODEFILL, stroke=FIELD, sw=2))
        frags.append(b)
    frags.append(bwin)
    render(os.path.join(IMG, "timeline.svg"), W, H, *frags,
           title="Народження автокодера")


# ── Фігури вставки proj-autoencoder-c ────────────────────────────────────────

# Реальні криві навчання 8→3→8 (вузьке горло) і 8→8→8 (надповний = тотожність),
# lr=1.0, ½MSE, онлайн-SGD, seed=1 — обчислені один раз у numpy, тут зашиті
# як (епоха, середня ½MSE на приклад), щоб figs.py лишався без залежностей.
CURVE_H3 = [
    (0, 1.0942), (171, 0.1485), (343, 0.0357), (514, 0.0180), (686, 0.0119),
    (857, 0.0088), (1029, 0.0069), (1200, 0.0057), (1371, 0.0049), (1543, 0.0042),
    (1714, 0.0037), (1886, 0.0033), (2057, 0.0030), (2229, 0.0027), (2400, 0.0025),
    (2571, 0.0023), (2743, 0.0022), (2914, 0.0020), (3086, 0.0019), (3257, 0.0018),
    (3429, 0.0017), (3600, 0.0016), (3771, 0.0015), (3943, 0.0014), (4286, 0.0013),
    (4629, 0.0012), (4971, 0.0011), (5314, 0.0010), (5657, 0.0010), (6000, 0.0009),
]
CURVE_H8 = [
    (0, 1.0112), (171, 0.0126), (343, 0.0039), (514, 0.0023), (686, 0.0016),
    (857, 0.0012), (1029, 0.0010), (1200, 0.0008), (1371, 0.0007), (1543, 0.0006),
    (1714, 0.0005), (1886, 0.0005), (2057, 0.0004), (2229, 0.0004), (2571, 0.0003),
    (2914, 0.0003), (3257, 0.0003), (3600, 0.0002), (3943, 0.0002), (4286, 0.0002),
    (4629, 0.0002), (4971, 0.0002), (5314, 0.0002), (5657, 0.0001), (6000, 0.0001),
]


def fig_838():
    """Конкретна архітектура 8→3→8 з розмірами масивів — карта до C-коду."""
    W, H = 820, 380
    cy = 196
    xi, xc, xo = 150, 410, 670
    si, yi = column(xi, cy, 8, spacing=34)
    sc, yc = column(xc, cy, 3, spacing=50, fill=CODEFILL, stroke=FIELD)
    so, yo = column(xo, cy, 8, spacing=34)
    frags = []
    frags.append(connect(xi, yi, xc, yc, color="#d7dbe0", sw=0.6))
    frags.append(connect(xc, yc, xo, yo, color="#d7dbe0", sw=0.6))
    frags.append(si); frags.append(sc); frags.append(so)
    yb = cy + 7 * 34 / 2 + 26
    frags.append(text(xi, yb, "вхід  x[8]", size=14, bold=True))
    frags.append(text(xc, cy + 78, "код  z[3]", size=14, bold=True, color=FIELD))
    frags.append(text(xo, yb, "відновлення  x̂[8]", size=14, bold=True))
    # ваги на ребрах
    b1, _, _ = textbox(280, 92, "W1 : 3×8", size=14, fill="#eef1f4")
    b2, _, _ = textbox(540, 92, "W2 : 8×3", size=14, fill="#eef1f4")
    frags.append(b1); frags.append(b2)
    # напрям потоку
    frags.append(arrow(xi + 74, 54, xc - 74, 54, color=MUTED, sw=1.6))
    frags.append(arrow(xc + 74, 54, xo - 74, 54, color=MUTED, sw=1.6))
    frags.append(text(410, 352, "стиснути 8 → 3, тоді відновити 3 → 8",
                      size=13.5, color=MUTED))
    render(os.path.join(IMG, "arch-838.svg"), W, H, *frags)


def fig_losscurve():
    """Реальні криві навчання: вузьке горло виходить на підлогу,
    надповний код сповзає в нуль (тотожність). Вісь L — логарифмічна."""
    import math
    W, H = 840, 470
    L, R, T, B = 96, 770, 66, 372           # межі поля графіка
    EPMAX = 6000
    LTOP, LBOT = math.log10(1.2), math.log10(1e-4)

    def xp(ep):
        return L + ep / EPMAX * (R - L)

    def yp(v):
        v = min(1.2, max(1e-4, v))
        return T + (LTOP - math.log10(v)) / (LTOP - LBOT) * (B - T)

    frags = []
    frags.append(line(L, T, L, B, color=MUTED, sw=1.4))
    frags.append(line(L, B, R, B, color=MUTED, sw=1.4))
    # горизонтальні лінії-декади з підписами
    for dec, lab in [(1.0, "1"), (0.1, "0.1"), (0.01, "0.01"),
                     (0.001, "0.001"), (0.0001, "0.0001")]:
        y = yp(dec)
        frags.append(line(L, y, R, y, color="#e8ebee", sw=1.0))
        frags.append(text(L - 12, y + 4, lab, size=12, color=MUTED, anchor="end"))
    # мітки епох по осі x
    for ep in [0, 1000, 2000, 3000, 4000, 5000, 6000]:
        x = xp(ep)
        frags.append(line(x, B, x, B + 5, color=MUTED, sw=1.2))
        frags.append(text(x, B + 20, str(ep), size=11.5, color=MUTED))
    frags.append(text((L + R) / 2, B + 40, "епоха", size=13, bold=True))
    frags.append(text(L - 60, (T + B) / 2, "похибка  L", size=13, bold=True))

    def poly(curve, color):
        pts = " ".join("%.1f,%.1f" % (xp(e), yp(v)) for (e, v) in curve)
        return ('<polyline points="%s" fill="none" stroke="%s" '
                'stroke-width="2.6"/>' % (pts, color))

    frags.append(poly(CURVE_H8, NEG))
    frags.append(poly(CURVE_H3, FIELD))
    # підписи-виноски біля хвостів (рознесені по вертикалі, щоб не накластись)
    b1, _, _ = textbox(575, 250, "вузьке горло 8→3→8:\nпідлога ≈ 0.001",
                       size=12.5, fill="#eafaf1", stroke=FIELD)
    b2, _, _ = textbox(575, 325, "надповний 8→8→8:\nсповзає в тотожність",
                       size=12.5, fill="#eef2fd", stroke=NEG)
    frags.append(b1); frags.append(b2)
    frags.append(text((L + R) / 2, 40,
                      "похибка відновлення падає епоха за епохою",
                      size=15, bold=True))
    render(os.path.join(IMG, "loss-curve.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_hourglass()
    fig_manifold()
    fig_identity_denoise()
    fig_pca_variance()
    fig_timeline()
    fig_838()
    fig_losscurve()
    print("OK: hourglass, manifold, identity-denoise, pca-variance, timeline, arch-838, loss-curve")
