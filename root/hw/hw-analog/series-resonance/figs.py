# -*- coding: utf-8 -*-
"""Фігури до статті «Послідовний резонанс» (book/electronics/analog/series-resonance).
Три фігури:
  zdip.svg   — повний опір |Z| від частоти: ГОСТРИЙ ПРОВАЛ до R на f₀ (струм — пік)
  cancel.svg — фазори напруг: U_L і U_C рівні й протифазні гасяться, лишається U_R = вхід
  vmag.svg   — резонанс напруг: на L і C напруга в Q разів більша за вхідну
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Локальні символи схем ───────────────────────────────────────────────────
def cap_h(cx, cy, label=None):
    """Горизонтальний конденсатор — дві вертикальні пластини. Повертає (svg, left, right)."""
    out = []
    out.append(line(cx - 4, cy - 13, cx - 4, cy + 13, color=INK, sw=2.6))
    out.append(line(cx + 4, cy - 13, cx + 4, cy + 13, color=INK, sw=2.6))
    a, b = (cx - 4 - 14, cy), (cx + 4 + 14, cy)
    out.append(line(cx - 4, cy, a[0], a[1], color=INK, sw=1.6))
    out.append(line(cx + 4, cy, b[0], b[1], color=INK, sw=1.6))
    if label:
        out.append(text(cx, cy - 22, label, size=13, color=INK, bold=True))
    return "".join(out), a, b


def coil_h(cx, cy, label=None, n=4, r=8):
    """Горизонтальна котушка — ряд напівдуг. Повертає (svg, left, right)."""
    out = []
    span = n * 2 * r
    x0 = cx - span / 2
    out.append(line(x0 - 14, cy, x0, cy, color=INK, sw=1.6))
    path = 'M %.1f %.1f ' % (x0, cy)
    xx = x0
    for i in range(n):
        path += 'A %d %d 0 0 1 %.1f %.1f ' % (r, r, xx + 2 * r, cy)
        xx += 2 * r
    out.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (path, INK))
    out.append(line(x0 + span, cy, x0 + span + 14, cy, color=INK, sw=1.6))
    if label:
        out.append(text(cx, cy - 18, label, size=13, color=INK, bold=True))
    return "".join(out), (x0 - 14, cy), (x0 + span + 14, cy)


def resistor_h(x0, x1, y, label=None, col=INK, lcol=None):
    """Горизонтальний резистор-зигзаг між (x0,y) і (x1,y)."""
    out = []
    n = 6
    seg = (x1 - x0) / (n + 1)
    amp = 6
    out.append(line(x0, y, x0 + seg, y, color=col, sw=1.6))
    xx = x0 + seg
    prev = y
    for i in range(n):
        ny = y + (amp if i % 2 == 0 else -amp)
        out.append(line(xx, prev, xx + seg, ny, color=col, sw=1.6))
        prev = ny
        xx += seg
    out.append(line(xx, prev, x1, y, color=col, sw=1.6))
    if label:
        out.append(text((x0 + x1) / 2, y - 12, label, size=12, color=lcol or col, bold=True))
    return "".join(out)


def src_ac(cx, cy, label=None):
    """Джерело змінної напруги: кружечок із синусоїдою. Повертає (svg, top, bot)."""
    r = 16
    out = [circle(cx, cy, r, fill="#ffffff", stroke=INK, sw=1.8)]
    out.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f T %.1f %.1f" fill="none" stroke="%s" stroke-width="1.8"/>'
               % (cx - 9, cy, cx - 4.5, cy - 7, cx, cy, cx + 9, cy, INK))
    if label:
        out.append(text(cx - r - 6, cy + 4, label, size=12, color=INK, bold=True, anchor="end"))
    return "".join(out), (cx, cy - r), (cx, cy + r)


# ════════════════════════════════════════════════════════════════════════════
# 1. zdip.svg — повний опір |Z| від частоти: гострий ПРОВАЛ до R на f₀
# ════════════════════════════════════════════════════════════════════════════
def fig_zdip():
    W, H = 640, 400
    f = []
    ox, oy = 84, 312
    axw, axh = 480, 256
    f.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.8))
    f.append(text(ox + axw - 4, oy + 24, "частота f", size=12, color=INK, anchor="end"))
    f.append(text(ox - 10, oy - axh + 10, "|Z|", size=13, color=INK, bold=True, anchor="end"))
    f.append(text(ox - 10, oy - axh + 28, "повний", size=10, color=MUTED, anchor="end"))
    f.append(text(ox - 10, oy - axh + 42, "опір", size=10, color=MUTED, anchor="end"))

    # крива |Z| = sqrt(R^2 + (XL - XC)^2); мінімум = R на f0
    L = 100e-6; C = 250e-12; R = 30.0
    w0 = 1.0 / math.sqrt(L * C)
    wmin, wmax = w0 * 0.30, w0 * 2.0
    Zmax = math.sqrt(R * R + (wmax * L - 1.0 / (wmax * C)) ** 2)
    f0x = ox + axw * (w0 - wmin) / (wmax - wmin)
    ybase = oy - 8
    sc = (axh - 50) / Zmax
    pts = []
    for i in range(0, 241):
        w = wmin + (wmax - wmin) * i / 240.0
        X = w * L - 1.0 / (w * C)
        Z = math.sqrt(R * R + X * X)
        x = ox + axw * (w - wmin) / (wmax - wmin)
        y = ybase - Z * sc
        pts.append("%.1f %.1f" % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(pts), POS))

    # мінімум = R
    ymin = ybase - R * sc
    f.append(line(f0x, oy, f0x, ymin, color=MUTED, sw=1.2, dash="5 5"))
    f.append(text(f0x, oy + 20, "f₀", size=13, color=INK, bold=True))
    f.append(circle(f0x, ymin, 4.5, fill=POS, stroke=POS))
    f.append(line(ox, ymin, f0x, ymin, color=MUTED, sw=1.1, dash="4 4"))
    f.append(text(ox + 6, ymin - 8, "мінімум |Z| = R", size=12, color=POS, bold=True, anchor="start"))

    # боки: нижче — ємнісне (Xc велике), вище — індуктивне (XL велике)
    f.append(text(ox + axw * 0.17, oy - axh + 70, "нижче f₀:", size=11, color=MUTED))
    f.append(text(ox + axw * 0.17, oy - axh + 84, "Xc велике", size=11, color=NEG))
    f.append(text(ox + axw * 0.17, oy - axh + 98, "(ємнісне)", size=10, color=MUTED))
    f.append(text(ox + axw * 0.80, oy - axh + 70, "вище f₀:", size=11, color=MUTED))
    f.append(text(ox + axw * 0.80, oy - axh + 84, "XL велике", size=11, color=POS))
    f.append(text(ox + axw * 0.80, oy - axh + 98, "(індуктивне)", size=10, color=MUTED))

    f.append(text(W / 2, H - 16,
                  "Послідовний контур: повний опір ГОСТРО провалюється до самого R на f₀ — отже струм там максимальний",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "zdip.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. cancel.svg — схема + фазори напруг: U_L і U_C рівні й протифазні гасяться
# ════════════════════════════════════════════════════════════════════════════
def fig_cancel():
    W, H = 700, 380
    f = []
    # --- ліворуч: послідовне коло R-L-C з одним струмом ---
    topy = 70
    lx, rx = 70, 330
    src, st, sb = src_ac(lx, 175, label="U")
    f.append(src)
    f.append(line(lx, st[1], lx, topy, color=INK, sw=1.8))
    # верхня шина: R, L, C послідовно
    f.append(line(lx, topy, 110, topy, color=INK, sw=1.8))
    f.append(resistor_h(110, 175, topy, label="R", lcol=MUTED))
    f.append(line(175, topy, 188, topy, color=INK, sw=1.8))
    sl, ll, lr = coil_h(228, topy, label="L")
    f.append(sl)
    f.append(line(lr[0], topy, 286, topy, color=INK, sw=1.8))
    sc, cl, cr = cap_h(300, topy, label="C")
    f.append(sc)
    f.append(line(cr[0], topy, rx, topy, color=INK, sw=1.8))
    f.append(line(rx, topy, rx, 175, color=INK, sw=1.8))
    f.append(line(rx, 175, lx, 175, color=INK, sw=1.8))
    f.append(line(lx, sb[1], lx, 175, color=INK, sw=1.8))
    # стрілка спільного струму
    f.append(arrow(120, topy - 22, 175, topy - 22, color=FIELD, sw=2.4))
    f.append(text(147, topy - 30, "один струм I", size=11, color=FIELD, bold=True))

    # --- праворуч: фазорна діаграма напруг ---
    cx, cy = 530, 200
    f.append(line(cx - 150, cy, cx + 150, cy, color="#d7dadf", sw=1.2))
    f.append(line(cx, cy - 150, cx, cy + 130, color="#d7dadf", sw=1.2))
    # U_L угору (+90 від струму), U_C униз (−90): рівні й протифазні
    f.append(arrow(cx, cy, cx, cy - 135, color=POS, sw=3))
    f.append(text(cx + 12, cy - 124, "U_L", size=14, color=POS, bold=True, anchor="start"))
    f.append(text(cx + 12, cy - 108, "(випереджає)", size=10, color=MUTED, anchor="start"))
    f.append(arrow(cx, cy, cx, cy + 127, color=NEG, sw=3))
    f.append(text(cx + 12, cy + 120, "U_C", size=14, color=NEG, bold=True, anchor="start"))
    f.append(text(cx + 12, cy + 136, "(відстає)", size=10, color=MUTED, anchor="start"))
    # U_R = вхід, по осі струму (вправо)
    f.append(arrow(cx, cy, cx + 110, cy, color=FIELD, sw=3))
    f.append(text(cx + 116, cy - 8, "U_R = U", size=12, color=FIELD, bold=True, anchor="start"))
    f.append(text(cx + 116, cy + 12, "(уся вхідна)", size=10, color=MUTED, anchor="start"))

    body, w0, h0 = textbox(cx, cy - 150 - 4, "U_L = U_C → гасяться;\nлишається сам R", size=11,
                           color=INK, fill="#f4f6f8", stroke=LINE)
    f.append(body)

    f.append(text(W / 2, H - 14,
                  "На f₀ напруги на L і C рівні й протифазні — у сумі нуль; уся вхідна напруга лягає на R, струм тримає тільки R",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "cancel.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 3. vmag.svg — резонанс напруг: на L і C напруга в Q разів більша за вхідну
# ════════════════════════════════════════════════════════════════════════════
def fig_vmag():
    W, H = 660, 360
    f = []
    ox, oy = 90, 280
    axh = 210
    f.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.8))
    f.append(line(ox, oy, ox + 470, oy, color=INK, sw=1.8))
    f.append(text(ox - 8, oy - axh + 8, "напруга", size=12, color=INK, bold=True, anchor="end"))

    # три стовпчики: вхід U=1, U_L=Q, U_C=Q (Q=8 для прикладу)
    Q = 8.0
    barw = 70
    unit = (axh - 36) / Q
    xs = [ox + 90, ox + 240, ox + 370]
    vals = [1.0, Q, Q]
    cols = [FIELD, POS, NEG]
    labs = ["вхід  U", "на котушці  U_L", "на конд.  U_C"]
    for x, v, c, lb in zip(xs, vals, cols, labs):
        h = v * unit
        f.append(rect(x - barw / 2, oy - h, barw, h, fill="#ffffff", stroke=c, sw=2.2, rx=3))
        f.append(text(x, oy - h - 10, ("U" if v == 1.0 else "Q·U"), size=13, color=c, bold=True))
        f.append(text(x, oy + 18, lb, size=11, color=INK))

    # пунктир рівня входу через усі
    f.append(line(ox, oy - unit, ox + 470, oy - unit, color=MUTED, sw=1.1, dash="5 5"))
    f.append(text(ox + 470, oy - unit - 6, "рівень входу", size=10, color=MUTED, anchor="end"))

    body, bw, bh = textbox(ox + 250, oy - axh + 26,
                           "Q = 8 → на L і на C по 8·U,\nхоч джерело дає лише U.\nГасяться між собою — назовні нуль,\nале нарізно кожна РЕАЛЬНА й небезпечна",
                           size=11, color=INK, fill="#fdecea", stroke=POS)
    f.append(body)

    f.append(text(W / 2, H - 14,
                  "Резонанс напруг: струм-пік на малому R дає на реактивностях напругу в Q разів більшу за вхідну",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "vmag.svg"), W, H, *f)


# ── Фігура до математичної вставки math-series-resonance ──────────────────────
def fig_bandwidth():
    """Крива струму I(f) з позначеною смугою −3 дБ (рівень 0.707·I_max) і Δf = f₀/Q."""
    W, H = 640, 380
    f = []
    ox, oy = 84, 300
    axw, axh = 480, 250
    f.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.8))
    f.append(text(ox + axw - 4, oy + 24, "частота f", size=12, color=INK, anchor="end"))
    f.append(text(ox - 10, oy - axh + 10, "струм I", size=12, color=INK, bold=True, anchor="end"))

    # крива струму = U / |Z|; нормуємо пік на 1
    L = 100e-6; C = 250e-12; R = 18.0
    w0 = 1.0 / math.sqrt(L * C)
    wmin, wmax = w0 * 0.55, w0 * 1.55
    def Imag(w):
        X = w * L - 1.0 / (w * C)
        return 1.0 / math.sqrt(R * R + X * X)
    Ipk = Imag(w0)
    top = axh - 36
    def XW(w): return ox + axw * (w - wmin) / (wmax - wmin)
    pts = []
    for i in range(0, 281):
        w = wmin + (wmax - wmin) * i / 280.0
        y = oy - (Imag(w) / Ipk) * top
        pts.append("%.1f %.1f" % (XW(w), y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(pts), POS))

    f0x = XW(w0)
    ypk = oy - top
    f.append(line(f0x, oy, f0x, ypk, color=MUTED, sw=1.2, dash="5 5"))
    f.append(text(f0x, oy + 20, "f₀", size=13, color=INK, bold=True))
    f.append(circle(f0x, ypk, 4.5, fill=POS, stroke=POS))
    f.append(text(f0x, ypk - 12, "I_max = U/R", size=12, color=POS, bold=True))

    # рівень 0.707 і межі смуги
    ylev = oy - 0.70710678 * top
    f.append(line(ox, ylev, ox + axw, ylev, color=NEG, sw=1.3, dash="6 4"))
    f.append(text(ox + 4, ylev - 8, "0.707·I_max  (−3 дБ)", size=11, color=NEG, anchor="start"))
    # знайдемо f1,f2 де I = 0.707 Ipk
    edges = []
    for i in range(0, 2801):
        w = wmin + (wmax - wmin) * i / 2800.0
        if Imag(w) / Ipk >= 0.70710678:
            edges.append(w)
    w1, w2 = edges[0], edges[-1]
    x1, x2 = XW(w1), XW(w2)
    yL = oy - 0.70710678 * top
    f.append(line(x1, oy, x1, yL, color=NEG, sw=1.1, dash="4 4"))
    f.append(line(x2, oy, x2, yL, color=NEG, sw=1.1, dash="4 4"))
    f.append(text(x1, oy + 18, "f₁", size=12, color=NEG, bold=True))
    f.append(text(x2, oy + 18, "f₂", size=12, color=NEG, bold=True))
    # дужка Δf
    yb = oy - 0.70710678 * top - 16
    f.append(line(x1, yb, x2, yb, color=INK, sw=1.4))
    f.append(line(x1, yb - 4, x1, yb + 4, color=INK, sw=1.4))
    f.append(line(x2, yb - 4, x2, yb + 4, color=INK, sw=1.4))
    f.append(text((x1 + x2) / 2, yb - 8, "Δf = f₀ / Q", size=12, color=INK, bold=True))

    f.append(text(W / 2, H - 14,
                  "Ширина піка струму на рівні 0.707 від максимуму — це смуга Δf; що вища Q, то вужчий пік",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "bandwidth.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 5. zcomplex.svg — комплексна площина: Z = R + j(XL − Xc) рухається з частотою
# ════════════════════════════════════════════════════════════════════════════
def fig_zcomplex():
    """Z як точка/фазор у комплексній площині: дійсна вісь R стала, уявна повзе
    з частотою від −j (ємнісне) через 0 (резонанс) до +j (індуктивне)."""
    W, H = 660, 430
    f = []
    cx, cy = 250, 230          # початок координат (R лежить праворуч від нього)
    axw = 250
    # осі
    f.append(arrow(cx - 40, cy, cx + axw, cy, color=INK, sw=1.6))
    f.append(arrow(cx, cy + 150, cx, cy - 170, color=INK, sw=1.6))
    f.append(text(cx + axw - 4, cy - 8, "Re  (опір R)", size=12, color=INK, anchor="end"))
    f.append(text(cx + 10, cy - 158, "Im  (реактивність X)", size=12, color=INK, anchor="start"))
    f.append(text(cx + 10, cy - 142, "+j: індуктивне", size=10, color=POS, anchor="start"))
    f.append(text(cx + 10, cy + 144, "−j: ємнісне", size=10, color=NEG, anchor="start"))

    Rpx = 150               # R у пікселях (стала дійсна частина)
    f.append(line(cx, cy, cx + Rpx, cy, color="#d7dadf", sw=1.2, dash="4 4"))
    f.append(text(cx + Rpx / 2, cy + 16, "R", size=12, color=MUTED, bold=True))

    # три фазори Z для трьох частот: нижче / на / вище f0
    Xup = 120   # величина реактивності в пікселях для крайніх частот
    cases = [
        ("нижче f₀", -Xup, NEG, "Z = R − jXc", "ємнісне"),
        ("на f₀", 0, FIELD, "Z = R", "чисто R"),
        ("вище f₀", +Xup, POS, "Z = R + jXL", "індуктивне"),
    ]
    for lbl, dy, col, zexpr, note in cases:
        tx, ty = cx + Rpx, cy - dy
        f.append(arrow(cx, cy, tx, ty, color=col, sw=2.6))
        f.append(circle(tx, ty, 4, fill=col, stroke=col))
        if dy == 0:
            f.append(text(tx + 8, ty - 8, zexpr, size=12, color=col, bold=True, anchor="start"))
            f.append(text(tx + 8, ty + 24, "|Z| = R (мінімум)", size=11, color=col, anchor="start"))
        else:
            yo = -6 if dy > 0 else 16
            f.append(text(tx + 8, ty + yo, zexpr, size=12, color=col, bold=True, anchor="start"))
    # вертикальна лінія, по якій ковзає кінець фазора (Re = R стале)
    f.append(line(cx + Rpx, cy - Xup - 8, cx + Rpx, cy + Xup + 8, color="#c7ccd2", sw=1.2, dash="3 4"))
    f.append(text(cx + Rpx, cy - Xup - 16, "кінець Z ковзає тут", size=10, color=MUTED))

    b, bw, bh = textbox(cx - 40, cy - 200,
                        "Частота міняє ЛИШЕ уявну частину; дійсна = R завжди.\n"
                        "Резонанс — мить, коли фазор лягає на дійсну вісь.",
                        size=11, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(b)

    f.append(text(W / 2, H - 14,
                  "Z = R + j(XL − Xc): кінець фазора ковзає вертикаллю Re = R; на f₀ уявна частина нуль — найкоротший фазор",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "zcomplex.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 6. halfpower.svg — геометрія смуги −3 дБ: |Z| = √2·R коли |X| = R
# ════════════════════════════════════════════════════════════════════════════
def fig_halfpower():
    """Дві криві реактивностей XL(f)↑ і Xc(f)↓; де |XL−Xc| = R, там |Z| = √2·R
    і струм 0.707·I_max — це межі смуги f₁, f₂."""
    W, H = 680, 430
    f = []
    ox, oy = 90, 250
    axw, axh = 500, 170
    f.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.6))
    f.append(arrow(ox, oy + 120, ox, oy - axh, color=INK, sw=1.6))
    f.append(text(ox + axw - 4, oy + 132, "частота f", size=12, color=INK, anchor="end"))
    f.append(text(ox - 8, oy - axh + 8, "реактивність", size=11, color=INK, bold=True, anchor="end"))

    L = 100e-6; C = 250e-12
    w0 = 1.0 / math.sqrt(L * C)
    wmin, wmax = w0 * 0.45, w0 * 1.75
    def XW(w): return ox + axw * (w - wmin) / (wmax - wmin)
    Xref = w0 * L            # = XL на f0 = Xc на f0 (масштаб)
    sc = (axh - 30) / (Xref * 2.6)
    # XL = wL (росте), Xc = 1/(wC) (спадає) — у пікселях від осі
    ptsL, ptsC, ptsD = [], [], []
    for i in range(0, 261):
        w = wmin + (wmax - wmin) * i / 260.0
        XL = w * L; XC = 1.0 / (w * C); D = XL - XC
        ptsL.append("%.1f %.1f" % (XW(w), oy - XL * sc))
        ptsC.append("%.1f %.1f" % (XW(w), oy - XC * sc))
        # різниця |X| показуємо нижче, але обмежимо поле
        yd = oy - D * sc
        yd = max(oy - axh + 14, min(oy + 110, yd))
        ptsD.append("%.1f %.1f" % (XW(w), yd))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="6 4"/>' % (" ".join(ptsL), POS))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="6 4"/>' % (" ".join(ptsC), NEG))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(ptsD), INK))
    f.append(text(XW(wmax) - 6, oy - wmax * L * sc + 4, "XL", size=12, color=POS, bold=True, anchor="end"))
    f.append(text(XW(wmin) + 6, oy - (1.0 / (wmin * C)) * sc + 4, "Xc", size=12, color=NEG, bold=True, anchor="start"))
    f.append(text(XW(w0 * 1.45), oy - (w0 * 1.45 * L - 1.0 / (w0 * 1.45 * C)) * sc - 8, "X = XL − Xc", size=11, color=INK, bold=True))

    # f0 — де X = 0
    f0x = XW(w0)
    f.append(line(f0x, oy - axh + 10, f0x, oy + 112, color=MUTED, sw=1.1, dash="5 5"))
    f.append(text(f0x, oy + 128, "f₀ (X=0)", size=12, color=FIELD, bold=True))

    # рівні X = +R і X = −R (R обрано як частка Xref для наочності)
    R = Xref * 0.45
    yPlusR = oy - R * sc
    yMinusR = oy + R * sc
    f.append(line(ox, yPlusR, ox + axw, yPlusR, color="#9aa0a6", sw=1.1, dash="3 4"))
    f.append(line(ox, yMinusR, ox + axw, yMinusR, color="#9aa0a6", sw=1.1, dash="3 4"))
    f.append(text(ox + 4, yPlusR - 6, "X = +R", size=11, color=POS, anchor="start"))
    f.append(text(ox + 4, yMinusR + 14, "X = −R", size=11, color=NEG, anchor="start"))

    # точки перетину X(f) з ±R → f1, f2
    def Dval(w): return w * L - 1.0 / (w * C)
    # f1: D = -R (нижче f0); f2: D = +R (вище f0)
    def solve(target):
        lo, hi = wmin, wmax
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            if Dval(mid) < target: lo = mid
            else: hi = mid
        return 0.5 * (lo + hi)
    w1 = solve(-R); w2 = solve(+R)
    x1, x2 = XW(w1), XW(w2)
    f.append(circle(x1, yMinusR, 4, fill=NEG, stroke=NEG))
    f.append(circle(x2, yPlusR, 4, fill=POS, stroke=POS))
    f.append(line(x1, oy, x1, yMinusR, color="#c7ccd2", sw=1.0, dash="3 3"))
    f.append(line(x2, oy, x2, yPlusR, color="#c7ccd2", sw=1.0, dash="3 3"))
    f.append(text(x1, oy + 128, "f₁", size=12, color=NEG, bold=True))
    f.append(text(x2, oy + 128, "f₂", size=12, color=POS, bold=True))
    # дужка Δf під віссю
    yb = oy + 92
    f.append(line(x1, yb, x2, yb, color=INK, sw=1.4))
    f.append(line(x1, yb - 4, x1, yb + 4, color=INK, sw=1.4))
    f.append(line(x2, yb - 4, x2, yb + 4, color=INK, sw=1.4))
    f.append(text((x1 + x2) / 2, yb - 7, "Δf = f₂ − f₁ = f₀/Q", size=12, color=INK, bold=True))

    b, bw, bh = textbox(ox + axw * 0.62, oy - axh + 40,
                        "Межі смуги — там, де реактивність\n"
                        "за модулем доганяє R: |XL−Xc| = R.\n"
                        "Тоді |Z| = √(R²+R²) = √2·R,\n"
                        "а струм падає до 1/√2 = 0.707 піка.",
                        size=11, color=INK, fill="#f4f6f8", stroke=LINE)
    f.append(b)

    f.append(text(W / 2, H - 12,
                  "Смуга −3 дБ настає там, де реактивність за модулем = R: тоді |Z| = √2·R і струм 0.707·I_max",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "halfpower.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 7. peak-shift.svg — пік струму послідовного РІВНО на f₀; пік |Z| паралельного зсунутий
# ════════════════════════════════════════════════════════════════════════════
def fig_peakshift():
    """Дві панелі. Ліва: струм послідовного контуру — пік точно на f₀ за будь-якого R.
    Права: |Z| паралельного — пік трохи НИЖЧЕ f₀ при відчутному R (різні «резонанси»)."""
    W, H = 720, 380
    f = []
    L = 100e-6; C = 250e-12
    w0 = 1.0 / math.sqrt(L * C)

    # ── ліва панель: послідовний — I(f) для двох R, обидва піки на f0 ──
    ox, oy = 70, 250
    axw, axh = 280, 180
    f.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.5))
    f.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.5))
    f.append(text(ox + axw - 4, oy + 22, "f", size=12, color=INK, anchor="end"))
    f.append(text(ox - 6, oy - axh + 6, "струм I", size=11, color=INK, bold=True, anchor="end"))
    f.append(text(ox + axw / 2, oy - axh - 6, "ПОСЛІДОВНИЙ: пік струму", size=12, color=INK, bold=True))
    wmin, wmax = w0 * 0.6, w0 * 1.5
    def XWl(w): return ox + axw * (w - wmin) / (wmax - wmin)
    top = axh - 28
    for R, col, dash in [(12.0, POS, None), (40.0, NEG, "6 4")]:
        def Im(w):
            X = w * L - 1.0 / (w * C); return 1.0 / math.sqrt(R * R + X * X)
        pk = Im(w0)
        pts = []
        for i in range(0, 241):
            w = wmin + (wmax - wmin) * i / 240.0
            pts.append("%.1f %.1f" % (XWl(w), oy - (Im(w) / pk) * top))
        da = ' stroke-dasharray="%s"' % dash if dash else ''
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"%s/>' % (" ".join(pts), col, da))
    f0xl = XWl(w0)
    f.append(line(f0xl, oy, f0xl, oy - top, color=FIELD, sw=1.4, dash="5 5"))
    f.append(circle(f0xl, oy - top, 4, fill=FIELD, stroke=FIELD))
    f.append(text(f0xl, oy + 20, "f₀", size=12, color=FIELD, bold=True))
    f.append(text(ox + 8, oy - top + 4, "малий R", size=10, color=POS, anchor="start"))
    f.append(text(ox + 8, oy - top * 0.55, "більший R", size=10, color=NEG, anchor="start"))
    f.append(text(f0xl + 6, oy - top - 4, "пік ТОЧНО на f₀", size=11, color=FIELD, bold=True, anchor="start"))

    # ── права панель: паралельний — |Z|(f), пік трохи нижче f0 при великому R ──
    ox2 = 410
    f.append(arrow(ox2, oy, ox2 + axw, oy, color=INK, sw=1.5))
    f.append(arrow(ox2, oy, ox2, oy - axh, color=INK, sw=1.5))
    f.append(text(ox2 + axw - 4, oy + 22, "f", size=12, color=INK, anchor="end"))
    f.append(text(ox2 - 6, oy - axh + 6, "|Z|", size=11, color=INK, bold=True, anchor="end"))
    f.append(text(ox2 + axw / 2, oy - axh - 6, "ПАРАЛЕЛЬНИЙ: пік опору", size=12, color=INK, bold=True))
    def XWr(w): return ox2 + axw * (w - wmin) / (wmax - wmin)
    # паралельний RLC (R послідовно з L — реальна котушка): |Z| має максимум нижче w0.
    # Великий R узято навмисно перебільшеним, щоб зсув піка був видимий оком.
    for Rser, col, dash, lab in [(30.0, NEG, "6 4", "малий R"), (600.0, POS, None, "великий R")]:
        # Z = (R+jwL) || (1/jwC)
        def Zmag(w):
            import cmath
            ZL = complex(Rser, w * L)
            ZC = complex(0, -1.0 / (w * C))
            Z = (ZL * ZC) / (ZL + ZC)
            return abs(Z)
        # знайти максимум чисельно для нормування
        ws = [wmin + (wmax - wmin) * i / 400.0 for i in range(401)]
        zz = [Zmag(w) for w in ws]
        zmaxv = max(zz); wmax_at = ws[zz.index(zmaxv)]
        pts = []
        for i in range(0, 241):
            w = wmin + (wmax - wmin) * i / 240.0
            pts.append("%.1f %.1f" % (XWr(w), oy - (Zmag(w) / zmaxv) * top))
        da = ' stroke-dasharray="%s"' % dash if dash else ''
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"%s/>' % (" ".join(pts), col, da))
        if col == POS:           # позначимо зсунутий пік великого R
            xpk = XWr(wmax_at)
            f.append(circle(xpk, oy - top, 4, fill=POS, stroke=POS))
            f.append(line(xpk, oy, xpk, oy - top, color=POS, sw=1.2, dash="4 4"))
            f.append(text(xpk - 4, oy + 20, "пік", size=11, color=POS, bold=True, anchor="end"))
    f0xr = XWr(w0)
    f.append(line(f0xr, oy, f0xr, oy - top - 6, color=FIELD, sw=1.4, dash="5 5"))
    f.append(text(f0xr + 2, oy + 20, "f₀", size=12, color=FIELD, bold=True, anchor="start"))
    f.append(text(f0xr + 6, oy - top - 4, "пік ЗСУНУТИЙ ←", size=11, color=POS, bold=True, anchor="start"))

    f.append(text(W / 2, H - 12,
                  "У послідовному пік струму стоїть точно на f₀ за будь-якого R; у паралельному відчутний R зсуває пік опору від f₀",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "peak-shift.svg"), W, H, *f)


if __name__ == "__main__":
    fig_zdip()
    fig_cancel()
    fig_vmag()
    fig_bandwidth()
    fig_zcomplex()
    fig_halfpower()
    fig_peakshift()
    print("OK: 7 фігур у", IMG)
