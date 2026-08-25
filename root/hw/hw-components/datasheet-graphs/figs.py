# -*- coding: utf-8 -*-
"""Фігури до теми «Графіки даташита» та її вставок (math-derating, math-thermal-resistance,
proj-log-graph-reading). svgkit імпортуємо зі scripts/, НЕ переписуємо (AUTHORING §5).

Усі підписи в SVG — без номерів і без «Рис.» (нумерації в book/ немає). Імена файлів —
slug-описові (не fig-XX). Запуск:  python figs.py  → пише в ./img/.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── спільні дрібні помічники для графіків (поверх svgkit) ────────────────────
def polyline(pts, color=INK, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (" ".join("%.1f,%.1f" % (x, y) for x, y in pts), color, sw, d))


def dot(cx, cy, r=4.0, fill=INK):
    return circle(cx, cy, r, fill=fill, stroke=BG, sw=1.5)


# ════════════════════════════════════════════════════════════════════════════
# СТАТТЯ
# ════════════════════════════════════════════════════════════════════════════

def fig_why_graphs():
    """Таблиця (3 дискретні точки) проти кривої (неперервна лінія) — опір від темп."""
    W, H = 720, 380
    L, R, T, B = 250, 660, 70, 300        # поле графіка
    Tmin, Tmax = 0.0, 150.0
    Rmin, Rmax = 0.0, 12.0

    def px(t): return L + (t - Tmin) / (Tmax - Tmin) * (R - L)
    def py(r): return B - (r - Rmin) / (Rmax - Rmin) * (B - T)

    # модельна крива опору (умовний NTC-подібний спад, лише для ілюстрації форми)
    def rval(t): return 2.0 + 9.0 * math.exp(-t / 60.0)

    f = []
    # ── ліворуч: таблиця з трьох рядків ──
    tab = [("25 °C", "8.6 Ом"), ("85 °C", "4.1 Ом"), ("125 °C", "3.2 Ом")]
    f.append(text(120, 56, "Таблиця", size=14, bold=True))
    ty = 80
    f.append(fitbox(40, ty, 160, 30, "темп.        опір", size=12, fill="#eef1f4", stroke=LINE))
    for i, (a, b) in enumerate(tab):
        yy = ty + 34 + i * 34
        f.append(fitbox(40, yy, 78, 30, a, size=12, fill=FILL, stroke=LINE))
        f.append(fitbox(122, yy, 78, 30, b, size=12, fill=FILL, stroke=LINE))
    f.append(text(120, ty + 34 + 3 * 34 + 26, "а при 60 °C — ?", size=12, color=POS, bold=True))

    # ── праворуч: графік ──
    f.append(line(L, T, L, B, color=INK, sw=2))
    f.append(line(L, B, R, B, color=INK, sw=2))
    for t in range(0, 151, 25):
        x = px(t)
        f.append(line(x, B, x, B + 5, color=INK, sw=1.2))
        f.append(text(x, B + 20, "%d" % t, size=11, color=MUTED))
    for r in range(0, 13, 3):
        y = py(r)
        f.append(line(L - 5, y, L, y, color=INK, sw=1.2))
        f.append(text(L - 12, y + 4, "%d" % r, size=11, color=MUTED, anchor="end"))
    f.append(text((L + R) / 2, B + 40, "температура, °C", size=12, color=INK))
    f.append(text(L - 30, T - 14, "опір, Ом", size=12, color=INK))

    # неперервна крива
    pts = []
    n = 90
    for k in range(n + 1):
        t = Tmin + (Tmax - Tmin) * k / n
        pts.append((px(t), py(rval(t))))
    f.append(polyline(pts, color=POS, sw=2.6))

    # три «табличні» точки на кривій
    for t in (25, 85, 125):
        f.append(dot(px(t), py(rval(t)), 4.2, fill=POS))
    # шукана точка 60 °C — зелена з пунктиром
    t0 = 60.0
    f.append(line(px(t0), B, px(t0), py(rval(t0)), color=FIELD, sw=1.4, dash="4,3"))
    f.append(line(L, py(rval(t0)), px(t0), py(rval(t0)), color=FIELD, sw=1.4, dash="4,3"))
    f.append(dot(px(t0), py(rval(t0)), 4.5, fill=FIELD))
    f.append(text(px(t0) + 6, py(rval(t0)) - 10, "60 °C → є число", size=11, color=FIELD, bold=True, anchor="start"))

    render(os.path.join(OUT, "table-vs-curve.svg"), W, H, *f,
           title="Таблиця дає три точки; крива — будь-яку температуру")


def fig_derating():
    """Derating потужності: плато до зламу, далі пряма до нуля при Tj(max)."""
    W, H = 720, 360
    L, R, T, B = 90, 650, 64, 288
    Tmin, Tmax = 0.0, 160.0
    Pmin, Pmax = 0.0, 2.2
    Tknee, Tjmax, Pfull = 25.0, 150.0, 2.0

    def px(t): return L + (t - Tmin) / (Tmax - Tmin) * (R - L)
    def py(p): return B - (p - Pmin) / (Pmax - Pmin) * (B - T)

    def allowed(t):
        if t <= Tknee: return Pfull
        if t >= Tjmax: return 0.0
        return Pfull * (Tjmax - t) / (Tjmax - Tknee)

    f = []
    f.append(line(L, T, L, B, color=INK, sw=2))
    f.append(line(L, B, R, B, color=INK, sw=2))
    for t in range(0, 161, 25):
        x = px(t)
        f.append(line(x, B, x, B + 5, color=INK, sw=1.2))
        f.append(text(x, B + 20, "%d" % t, size=11, color=MUTED))
    for p in [0.0, 0.5, 1.0, 1.5, 2.0]:
        y = py(p)
        f.append(line(L - 5, y, L, y, color=INK, sw=1.2))
        f.append(text(L - 12, y + 4, "%.1f" % p, size=11, color=MUTED, anchor="end"))
    f.append(text((L + R) / 2, B + 40, "температура корпусу, °C", size=12, color=INK))
    f.append(text(L - 22, T - 14, "потужність, Вт", size=12, color=INK, anchor="start"))

    # крива: плато + спад
    f.append(polyline([(px(0), py(Pfull)), (px(Tknee), py(Pfull)),
                       (px(Tjmax), py(0.0))], color=FIELD, sw=3.0))
    f.append(text(px(12), py(Pfull) - 10, "плато 2 Вт", size=11, color=FIELD, bold=True, anchor="start"))

    # точка зламу
    f.append(line(px(Tknee), B, px(Tknee), py(Pfull), color=MUTED, sw=1.2, dash="4,3"))
    f.append(text(px(Tknee), B + 36, "точка зламу", size=10.5, color=MUTED))

    # робоча точка 100 °C → 0.8 Вт
    t0 = 100.0; p0 = allowed(t0)
    f.append(line(px(t0), B, px(t0), py(p0), color=POS, sw=1.6, dash="5,4"))
    f.append(line(L, py(p0), px(t0), py(p0), color=POS, sw=1.6, dash="5,4"))
    f.append(dot(px(t0), py(p0), 4.6, fill=POS))
    f.append(text(px(t0) + 8, py(p0) - 8, "при 100 °C — лише 0.8 Вт", size=11, color=POS, bold=True, anchor="start"))

    # нахил
    f.append(text(px(92), py(1.35), "нахил −1/Rθ", size=10.5, color=INK, anchor="start"))

    render(os.path.join(OUT, "derating.svg"), W, H, *f,
           title="Дозволена потужність падає з нагрівом")


def _iv_axes(f, L, R, T, B, vmax, label_y):
    f.append(line(L, T, L, B, color=INK, sw=2))
    f.append(line(L, B, R, B, color=INK, sw=2))
    f.append(text((L + R) / 2, B + 34, "напруга, В", size=11, color=INK))
    f.append(text(L, T - 12, label_y, size=11, color=INK, anchor="start"))


def fig_iv_curve():
    """ВАХ діода: ліворуч лінійна вісь струму (різке коліно), праворуч лог-вісь (пряма)."""
    W, H = 760, 360
    I0 = 1e-12
    nVt = 0.045        # ефективне n·Vt для гарної картинки коліна ~0.7 В
    Vmax = 0.85

    def idiode(v): return I0 * (math.exp(v / nVt) - 1.0)

    f = []
    # ── ЛІВА панель: лінійна вісь струму ──
    L, R, T, B = 70, 360, 70, 290
    Imax = 0.02
    def pxL(v): return L + v / Vmax * (R - L)
    def pyL(i): return B - min(i, Imax) / Imax * (B - T)
    _iv_axes(f, L, R, T, B, Vmax, "струм (лінійно)")
    for v in [0.0, 0.2, 0.4, 0.6, 0.8]:
        x = pxL(v); f.append(line(x, B, x, B + 5, color=INK, sw=1)); f.append(text(x, B + 18, "%.1f" % v, size=10, color=MUTED))
    pts = []
    v = 0.0
    while v <= Vmax + 1e-9:
        pts.append((pxL(v), pyL(idiode(v)))); v += 0.004
    f.append(polyline(pts, color=POS, sw=2.6))
    f.append(text(pxL(0.55), T + 16, "коліно ≈0.7 В", size=11, color=POS, bold=True))
    f.append(text((L + R) / 2, T - 34, "лінійна вісь", size=12, bold=True))

    # ── ПРАВА панель: логарифмічна вісь струму ──
    L2, R2, T2, B2 = 450, 730, 70, 290
    decades = [-9, -6, -3, 0]   # від 1 нА до 1 А (10^-9..10^0), показуємо A
    lo, hi = decades[0], decades[-1]
    def pxR(v): return L2 + v / Vmax * (R2 - L2)
    def pyR(i):
        e = math.log10(max(i, 10 ** lo))
        e = max(lo, min(hi, e))
        return B2 - (e - lo) / (hi - lo) * (B2 - T2)
    _iv_axes(f, L2, R2, T2, B2, Vmax, "струм (лог)")
    for v in [0.0, 0.2, 0.4, 0.6, 0.8]:
        x = pxR(v); f.append(line(x, B2, x, B2 + 5, color=INK, sw=1)); f.append(text(x, B2 + 18, "%.1f" % v, size=10, color=MUTED))
    labs = {-9: "1н", -6: "1мк", -3: "1м", 0: "1"}
    for e in decades:
        y = B2 - (e - lo) / (hi - lo) * (B2 - T2)
        f.append(line(L2 - 5, y, L2, y, color=INK, sw=1)); f.append(text(L2 - 9, y + 4, labs[e], size=9.5, color=MUTED, anchor="end"))
    pts = []
    v = 0.06
    while v <= Vmax + 1e-9:
        pts.append((pxR(v), pyR(idiode(v)))); v += 0.004
    f.append(polyline(pts, color=NEG, sw=2.6))
    f.append(text((L2 + R2) / 2, T2 - 34, "логарифмічна вісь", size=12, bold=True))
    f.append(text(pxR(0.42), pyR(idiode(0.42)) - 10, "пряма!", size=11, color=NEG, bold=True, anchor="start"))

    render(os.path.join(OUT, "diode-iv-lin-log.svg"), W, H, *f,
           title="Та сама ВАХ діода: лінійна вісь vs логарифмічна")


def _log_axis_h(f, x0, x1, y, lo_dec, hi_dec, big_labels):
    """Горизонтальна лог-вісь від 10^lo_dec до 10^hi_dec з проміжними поділками."""
    span = hi_dec - lo_dec
    def xof(e): return x0 + (e - lo_dec) / span * (x1 - x0)
    f.append(line(x0, y, x1, y, color=INK, sw=2))
    e = lo_dec
    while e <= hi_dec:
        x = xof(e)
        f.append(line(x, y - 8, x, y + 8, color=INK, sw=2))
        f.append(text(x, y - 14, big_labels.get(e, "10^%d" % e), size=12, color=INK, bold=True))
        if e < hi_dec:
            for m in range(2, 10):
                xm = xof(e + math.log10(m))
                f.append(line(xm, y - 5, xm, y + 5, color=MUTED, sw=1))
                if m in (2, 5):
                    f.append(text(xm, y + 18, str(m * 10 ** e if e >= 0 else m), size=9, color=MUTED))
        e += 1
    return xof


def fig_log_axis():
    """Лог-вісь: нерівномірна сітка; середина між 1 і 10 = √10 ≈ 3.16, не 5."""
    W, H = 720, 300
    x0, x1, y = 70, 650, 140
    f = []
    xof = _log_axis_h(f, x0, x1, y, 0, 3, {0: "1", 1: "10", 2: "100", 3: "1k"})

    # відмітка «густо» / «рідко»
    f.append(text(xof(0.3), y - 40, "тут поділки густі", size=10.5, color=POS, anchor="middle"))
    f.append(text(xof(2.7), y - 40, "тут — рідкі", size=10.5, color=POS, bold=True, anchor="middle"))

    # середина між 1 і 10
    xmid = xof(0.5)         # геометрична середина = √10
    f.append(line(xmid, y - 26, xmid, y + 26, color=FIELD, sw=2))
    f.append(text(xmid, y + 46, "середина = √10 ≈ 3.16", size=11, color=FIELD, bold=True))
    # хибна «5»
    x5 = xof(math.log10(5))
    f.append(line(x5, y - 18, x5, y + 18, color=POS, sw=1.6, dash="4,3"))
    f.append(text(x5, y - 58, "«5»", size=10, color=POS))

    f.append(text(W / 2, 240, "Рівний крок = множення на 10, а не додавання.", size=12, color=INK))
    f.append(text(W / 2, 262, "Між 1 і 2 широко, між 9 і 10 вузько.", size=12, color=INK))

    render(os.path.join(OUT, "log-axis-grid.svg"), W, H, *f,
           title="Логарифмічна вісь: сітка нерівномірна")


def fig_read_point():
    """Ритуал зчитування: вгору до кривої, вбік на вісь."""
    W, H = 700, 360
    L, R, T, B = 90, 640, 70, 290

    def px(x): return L + x * (R - L)        # x у частках 0..1
    def py(y): return B - y * (B - T)

    f = []
    f.append(line(L, T, L, B, color=INK, sw=2))
    f.append(line(L, B, R, B, color=INK, sw=2))
    f.append(text((L + R) / 2, B + 30, "своя умова (температура, струм, напруга)", size=11, color=INK))
    f.append(text(L, T - 12, "шукане значення", size=11, color=INK, anchor="start"))

    # умовна спадна крива
    pts = []
    n = 60
    for k in range(n + 1):
        x = k / n
        y = 0.92 - 0.7 * x ** 1.3
        pts.append((px(x), py(y)))
    f.append(polyline(pts, color=INK, sw=2.6))

    # точка зчитування при x0
    x0 = 0.42
    y0 = 0.92 - 0.7 * x0 ** 1.3
    # рух 1: вгору
    f.append(line(px(x0), B, px(x0), py(y0), color=POS, sw=2.2, dash="5,4"))
    f.append(text(px(x0) + 6, (B + py(y0)) / 2, "1 ↑ до кривої", size=11, color=POS, bold=True, anchor="start"))
    # рух 2: вбік
    f.append(line(px(x0), py(y0), L, py(y0), color=NEG, sw=2.2, dash="5,4"))
    f.append(text((L + px(x0)) / 2, py(y0) - 8, "2 ← на вісь", size=11, color=NEG, bold=True))
    f.append(dot(px(x0), py(y0), 5.0, fill=INK))
    f.append(dot(px(x0), B, 3.6, fill=POS))
    f.append(dot(L, py(y0), 3.6, fill=NEG))

    render(os.path.join(OUT, "read-point.svg"), W, H, *f,
           title="Зняти число: вгору до кривої — вбік на вісь")


def fig_curve_zoo():
    """Шість типових форм кривих даташита у сітці 3×2."""
    W, H = 760, 470
    cells = [
        ("derating потужності", "plateau"),
        ("Rds(on) від температури", "rise"),
        ("ВАХ діода (коліно)", "knee"),
        ("підсилення від частоти", "rolloff"),
        ("β від струму (горб)", "hump"),
        ("струм спокою від напруги", "slowrise"),
    ]
    cw, ch = 230, 180
    gx0, gy0 = 30, 56
    padx, pady = 14, 28

    f = []
    for idx, (title_s, kind) in enumerate(cells):
        cxi = idx % 3
        cyi = idx // 3
        ox = gx0 + cxi * (cw + 8)
        oy = gy0 + cyi * (ch + 30)
        # рамка-комірка
        f.append(rect(ox, oy, cw, ch, fill="#fbfcfd", stroke=LINE, sw=1.2))
        L, R = ox + padx, ox + cw - padx
        T, B = oy + pady, oy + ch - 20
        f.append(line(L, T, L, B, color=INK, sw=1.4))
        f.append(line(L, B, R, B, color=INK, sw=1.4))
        f.append(text(ox + cw / 2, oy + 18, title_s, size=11.5, bold=True))

        def X(t): return L + t * (R - L)
        def Y(v): return B - v * (B - T)
        pts = []
        n = 60
        for k in range(n + 1):
            t = k / n
            if kind == "plateau":
                v = 1.0 if t < 0.3 else max(0.0, 1.0 - (t - 0.3) / 0.7)
            elif kind == "rise":
                v = 0.25 + 0.7 * t ** 1.4
            elif kind == "knee":
                v = 0.02 * (math.exp(3.2 * t) - 1) / (math.exp(3.2) - 1) * 0 + (0.0 if t < 0.55 else (t - 0.55) / 0.45)
            elif kind == "rolloff":
                v = 0.9 if t < 0.35 else max(0.05, 0.9 - 1.3 * (t - 0.35))
            elif kind == "hump":
                v = 0.2 + 0.75 * math.exp(-((t - 0.5) ** 2) / 0.045)
            else:  # slowrise
                v = 0.3 + 0.45 * t
            pts.append((X(t), Y(max(0.0, min(1.0, v)))))
        col = {"plateau": FIELD, "rise": POS, "knee": NEG, "rolloff": NEG, "hump": POS, "slowrise": MUTED}[kind]
        f.append(polyline(pts, color=col, sw=2.4))

    render(os.path.join(OUT, "curve-zoo.svg"), W, H, *f,
           title="Звіринець типових кривих даташита")


# ════════════════════════════════════════════════════════════════════════════
# ВСТАВКА math-derating
# ════════════════════════════════════════════════════════════════════════════

def fig_derating_interp():
    """Derating-крива зі зламом + дві відомі точки + лінійна інтерполяція проміжної."""
    W, H = 720, 380
    L, R, T, B = 90, 650, 64, 300
    Tmin, Tmax = 0.0, 160.0
    Ymin, Ymax = 0.0, 110.0
    Tknee, Tjmax = 25.0, 150.0

    def px(t): return L + (t - Tmin) / (Tmax - Tmin) * (R - L)
    def py(y): return B - (y - Ymin) / (Ymax - Ymin) * (B - T)

    def allowed(t):
        if t <= Tknee: return 100.0
        if t >= Tjmax: return 0.0
        return 100.0 * (Tjmax - t) / (Tjmax - Tknee)

    f = []
    f.append(line(L, T, L, B, color=INK, sw=2))
    f.append(line(L, B, R, B, color=INK, sw=2))
    for t in range(0, 161, 25):
        x = px(t); f.append(line(x, B, x, B + 5, color=INK, sw=1.2)); f.append(text(x, B + 20, "%d" % t, size=11, color=MUTED))
    for y in range(0, 101, 25):
        yy = py(y); f.append(line(L - 5, yy, L, yy, color=INK, sw=1.2)); f.append(text(L - 12, yy + 4, "%d" % y, size=11, color=MUTED, anchor="end"))
    f.append(text((L + R) / 2, B + 40, "температура корпусу, °C", size=12, color=INK))
    f.append(text(L - 22, T - 14, "дозволено, % від номіналу", size=12, color=INK, anchor="start"))

    f.append(polyline([(px(0), py(100)), (px(Tknee), py(100)), (px(Tjmax), py(0))], color=FIELD, sw=3.0))

    # дві відомі точки 85→52 %, 100→40 %
    for t, y in [(85, allowed(85)), (100, allowed(100))]:
        f.append(dot(px(t), py(y), 4.6, fill=NEG))
        f.append(text(px(t), py(y) - 12, "%d°→%.0f%%" % (t, y), size=10.5, color=NEG, bold=True))
    # проміжна 92 → ~46 %
    t0 = 92.0; y0 = allowed(t0)
    f.append(line(px(t0), B, px(t0), py(y0), color=POS, sw=1.6, dash="5,4"))
    f.append(line(L, py(y0), px(t0), py(y0), color=POS, sw=1.6, dash="5,4"))
    f.append(dot(px(t0), py(y0), 4.8, fill=POS))
    f.append(text(px(t0) + 8, py(y0) + 18, "92° → 46 % (інтерполяція)", size=11, color=POS, bold=True, anchor="start"))

    render(os.path.join(OUT, "derating-interp.svg"), W, H, *f,
           title="Derating-крива: зняти проміжне значення інтерполяцією")


def fig_derating_margin():
    """Стеля (derating) і робоча межа 70 % від неї; робоча точка нижче обох."""
    W, H = 720, 380
    L, R, T, B = 90, 650, 64, 300
    Tmin, Tmax = 0.0, 160.0
    Ymin, Ymax = 0.0, 110.0
    Tknee, Tjmax, k = 25.0, 150.0, 0.7

    def px(t): return L + (t - Tmin) / (Tmax - Tmin) * (R - L)
    def py(y): return B - (y - Ymin) / (Ymax - Ymin) * (B - T)

    def ceil_(t):
        if t <= Tknee: return 100.0
        if t >= Tjmax: return 0.0
        return 100.0 * (Tjmax - t) / (Tjmax - Tknee)

    f = []
    f.append(line(L, T, L, B, color=INK, sw=2))
    f.append(line(L, B, R, B, color=INK, sw=2))
    for t in range(0, 161, 25):
        x = px(t); f.append(line(x, B, x, B + 5, color=INK, sw=1.2)); f.append(text(x, B + 20, "%d" % t, size=11, color=MUTED))
    for y in range(0, 101, 25):
        yy = py(y); f.append(line(L - 5, yy, L, yy, color=INK, sw=1.2)); f.append(text(L - 12, yy + 4, "%d" % y, size=11, color=MUTED, anchor="end"))
    f.append(text((L + R) / 2, B + 40, "температура корпусу, °C", size=12, color=INK))
    f.append(text(L - 22, T - 14, "% від номіналу", size=12, color=INK, anchor="start"))

    # стеля
    f.append(polyline([(px(0), py(100)), (px(Tknee), py(100)), (px(Tjmax), py(0))], color=POS, sw=2.8))
    f.append(text(px(120), py(ceil_(120)) + 16, "стеля (derating)", size=11, color=POS, bold=True, anchor="start"))
    # робоча межа = k·стеля
    f.append(polyline([(px(0), py(100 * k)), (px(Tknee), py(100 * k)), (px(Tjmax), py(0))], color=FIELD, sw=2.8))
    f.append(text(px(40), py(100 * k) - 10, "робоча межа = 70 % стелі", size=11, color=FIELD, bold=True, anchor="start"))

    # робоча точка 92 °C
    t0 = 92.0; y0 = ceil_(t0) * k
    f.append(line(px(t0), B, px(t0), py(y0), color=NEG, sw=1.6, dash="5,4"))
    f.append(dot(px(t0), py(y0), 4.8, fill=NEG))
    f.append(text(px(t0) + 8, py(y0) - 8, "робоча точка", size=10.5, color=NEG, bold=True, anchor="start"))

    render(os.path.join(OUT, "derating-margin.svg"), W, H, *f,
           title="Правило запасу: робоча точка нижче derating-кривої")


# ════════════════════════════════════════════════════════════════════════════
# ВСТАВКА math-thermal-resistance
# ════════════════════════════════════════════════════════════════════════════

def fig_thermal_rc():
    """Еквівалентна теплова схема + словник аналогій тепло↔електрика."""
    W, H = 740, 360
    f = []
    # ── ліва половина: схема ──
    cx = 200
    # джерело струму P (коло)
    f.append(circle(cx, 250, 26, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(cx, 256, "P", size=16, color=POS, bold=True))
    f.append(text(cx, 296, "виділене тепло", size=10.5, color=MUTED))
    # провід угору до вузла Tj
    f.append(line(cx, 224, cx, 120, color=INK, sw=2))
    f.append(dot(cx, 120, 4, fill=INK))
    f.append(text(cx + 10, 116, "Tj (кристал)", size=11, color=INK, anchor="start"))
    # резистор Rθ угорі праворуч
    f.append(line(cx, 120, cx + 140, 120, color=INK, sw=2))
    f.append(rect(cx + 140, 108, 70, 24, fill=FILL, stroke=INK, sw=1.6))
    f.append(text(cx + 175, 124, "Rθ", size=13, color=INK, bold=True))
    f.append(line(cx + 210, 120, cx + 210, 250, color=INK, sw=2))
    # земля = повітря Tamb
    gy = 250
    f.append(line(cx + 170, gy, cx + 250, gy, color=INK, sw=2))
    f.append(line(cx + 182, gy + 8, cx + 238, gy + 8, color=INK, sw=2))
    f.append(line(cx + 196, gy + 16, cx + 224, gy + 16, color=INK, sw=2))
    f.append(text(cx + 210, gy + 36, "Tamb (повітря)", size=10.5, color=MUTED))
    # нижній провід назад до джерела
    f.append(line(cx, 276, cx, gy, color=INK, sw=2))
    f.append(line(cx, gy, cx + 210, gy, color=INK, sw=2))

    # ── права половина: словник ──
    bx = 540
    f.append(text(bx, 70, "Словник аналогій", size=13, bold=True))
    rows = [("потужність P", "струм I"),
            ("перепад ΔT", "напруга U"),
            ("тепловий опір Rθ", "опір R"),
            ("теплоємність Cθ", "ємність C")]
    yy = 92
    f.append(fitbox(bx - 110, yy, 220, 28, "тепло            ↔   електрика", size=11, fill="#eef1f4", stroke=LINE))
    for i, (a, b) in enumerate(rows):
        y = yy + 32 + i * 32
        f.append(fitbox(bx - 110, y, 130, 28, a, size=10.5, fill=FILL, stroke=LINE))
        f.append(fitbox(bx + 24, y, 86, 28, b, size=10.5, fill="#eef7f0", stroke=FIELD))
    f.append(text(bx, yy + 32 + 4 * 32 + 22, "ΔT = P·Rθ — закон Ома для тепла", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, "thermal-rc-analogy.svg"), W, H, *f,
           title="Теплова модель: Rθ як опір, ΔT як напруга")


def fig_thermal_derating():
    """Та сама derating-пряма як графік P=(Tjmax−Tamb)/Rθ; зчитування для Tamb=85."""
    W, H = 720, 360
    L, R, T, B = 90, 650, 64, 290
    Tmin, Tmax = 0.0, 160.0
    Pmin, Pmax = 0.0, 2.6
    Tknee, Tjmax, Pfull = 25.0, 150.0, 2.5

    def px(t): return L + (t - Tmin) / (Tmax - Tmin) * (R - L)
    def py(p): return B - (p - Pmin) / (Pmax - Pmin) * (B - T)

    def allowed(t):
        if t <= Tknee: return Pfull
        if t >= Tjmax: return 0.0
        return Pfull * (Tjmax - t) / (Tjmax - Tknee)

    f = []
    f.append(line(L, T, L, B, color=INK, sw=2))
    f.append(line(L, B, R, B, color=INK, sw=2))
    for t in range(0, 161, 25):
        x = px(t); f.append(line(x, B, x, B + 5, color=INK, sw=1.2)); f.append(text(x, B + 20, "%d" % t, size=11, color=MUTED))
    for p in [0.0, 0.5, 1.0, 1.5, 2.0, 2.5]:
        yy = py(p); f.append(line(L - 5, yy, L, yy, color=INK, sw=1.2)); f.append(text(L - 12, yy + 4, "%.1f" % p, size=10.5, color=MUTED, anchor="end"))
    f.append(text((L + R) / 2, B + 40, "температура повітря Tamb, °C", size=12, color=INK))
    f.append(text(L - 22, T - 14, "дозволена потужність, Вт", size=12, color=INK, anchor="start"))

    f.append(polyline([(px(0), py(Pfull)), (px(Tknee), py(Pfull)), (px(Tjmax), py(0))], color=FIELD, sw=3.0))
    f.append(text(px(10), py(Pfull) - 10, "поличка", size=11, color=FIELD, bold=True, anchor="start"))
    f.append(text(px(95), py(1.6), "нахил −1/Rθ", size=10.5, color=INK, anchor="start"))
    f.append(text(px(132), py(0.08) - 14, "0 при Tj(max)", size=10, color=MUTED, anchor="middle"))

    # зчитування для Tamb=85
    t0 = 85.0; p0 = allowed(t0)
    f.append(line(px(t0), B, px(t0), py(p0), color=NEG, sw=1.8, dash="5,4"))
    f.append(line(L, py(p0), px(t0), py(p0), color=NEG, sw=1.8, dash="5,4"))
    f.append(dot(px(t0), py(p0), 4.8, fill=NEG))
    f.append(text(px(t0) + 8, py(p0) - 8, "Tamb 85 °C → дозволено стільки", size=11, color=NEG, bold=True, anchor="start"))

    render(os.path.join(OUT, "thermal-derating-line.svg"), W, H, *f,
           title="Derating — це графік закону Tj = Tamb + P·Rθ")


# ════════════════════════════════════════════════════════════════════════════
# ВСТАВКА proj-log-graph-reading
# ════════════════════════════════════════════════════════════════════════════

def fig_decade_grid():
    """Дві декади 1..100: геометрична середина = 10 (а не 50); проміжні поділки нерівні."""
    W, H = 720, 360
    # вертикальна лог-вісь
    x = 220
    y0, y1 = 300, 70           # низ (1) .. верх (100)
    lo, hi = 0, 2              # 10^0..10^2
    def yof(e): return y0 + (e - lo) / (hi - lo) * (y1 - y0)

    f = []
    f.append(line(x, y0, x, y1, color=INK, sw=2))
    # головні поділки
    for e, lab in [(0, "1"), (1, "10"), (2, "100")]:
        yy = yof(e)
        f.append(line(x - 8, yy, x + 8, yy, color=INK, sw=2))
        f.append(text(x - 14, yy + 4, lab, size=13, color=INK, bold=True, anchor="end"))
    # проміжні
    for e in (0, 1):
        for m in range(2, 10):
            yy = yof(e + math.log10(m))
            f.append(line(x - 5, yy, x + 5, yy, color=MUTED, sw=1))

    # геометрична середина (рівно посередині осі) = 10
    ymid = (y0 + y1) / 2
    f.append(line(x - 60, ymid, x + 120, ymid, color=FIELD, sw=2))
    f.append(text(x + 126, ymid + 4, "геом. середина = 10", size=12, color=FIELD, bold=True, anchor="start"))
    # хибна «50»
    y50 = yof(math.log10(50))
    f.append(line(x - 40, y50, x + 100, y50, color=POS, sw=1.6, dash="5,4"))
    f.append(text(x + 106, y50 + 4, "«50» — набагато вище центру", size=11, color=POS, anchor="start"))

    f.append(text(x, 40, "Між 1 і 100 посередині осі стоїть 10, не 50", size=12, bold=True))
    f.append(text(x - 90, (yof(0) + yof(1)) / 2, "поділки", size=10, color=MUTED, anchor="middle"))
    f.append(text(x - 90, (yof(0) + yof(1)) / 2 + 14, "знизу широкі", size=10, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, "decade-grid.svg"), W, H, *f,
           title="Сітка декад: «на око посередині» бреше")


def fig_read_algorithm():
    """Знаходимо точку перпендикулярами, міряємо частку p декади, підносимо 10^p."""
    W, H = 720, 380
    L, R, T, B = 100, 640, 70, 300
    # x — лінійна умовна вісь; y — логарифмічна (1..1000)
    lo, hi = 0, 3
    def px(t): return L + t * (R - L)         # t 0..1
    def py_dec(e): return B - (e - lo) / (hi - lo) * (B - T)

    f = []
    f.append(line(L, T, L, B, color=INK, sw=2))
    f.append(line(L, B, R, B, color=INK, sw=2))
    f.append(text((L + R) / 2, B + 30, "відома вісь (напр. температура)", size=11, color=INK))
    f.append(text(L, T - 12, "шукана вісь (лог)", size=11, color=INK, anchor="start"))
    for e, lab in [(0, "1"), (1, "10"), (2, "100"), (3, "1k")]:
        yy = py_dec(e); f.append(line(L - 6, yy, L, yy, color=INK, sw=1.5)); f.append(text(L - 11, yy + 4, lab, size=11, color=INK, bold=True, anchor="end"))
        if e < hi:
            for m in range(2, 10):
                ym = py_dec(e + math.log10(m)); f.append(line(L - 4, ym, L, ym, color=MUTED, sw=1))

    # крива (зростає)
    pts = []
    n = 60
    for k in range(n + 1):
        t = k / n
        e = 0.4 + 2.0 * t            # лог-значення росте 0.4..2.4
        pts.append((px(t), py_dec(e)))
    f.append(polyline(pts, color=INK, sw=2.4))

    # точка при t0
    t0 = 0.5
    e0 = 0.4 + 2.0 * t0             # = 1.4 → у декаді 10..100, p=0.4
    f.append(line(px(t0), B, px(t0), py_dec(e0), color=POS, sw=1.8, dash="5,4"))
    f.append(line(L, py_dec(e0), px(t0), py_dec(e0), color=NEG, sw=1.8, dash="5,4"))
    f.append(dot(px(t0), py_dec(e0), 5.0, fill=INK))

    # позначити декаду 10..100 і частку p
    yL, yH = py_dec(1), py_dec(2)
    f.append(line(R - 30, yL, R - 30, yH, color=FIELD, sw=2))
    f.append(line(R - 36, yL, R - 24, yL, color=FIELD, sw=2))
    f.append(line(R - 36, yH, R - 24, yH, color=FIELD, sw=2))
    yp = py_dec(e0)
    f.append(line(R - 30, yL, R - 30, yp, color=POS, sw=3))
    f.append(text(R - 20, (yL + yp) / 2, "p ≈ 0.4", size=11, color=POS, bold=True, anchor="start"))
    f.append(text(R - 20, (yL + yH) / 2 + 16, "декада", size=10, color=FIELD, anchor="start"))

    box = fitbox(px(0.16), py_dec(2.55), 230, 30,
                 "значення = низ·10^p = 10·10^0.4 ≈ 25", size=11, fill="#eef7f0", stroke=FIELD)
    f.append(box)

    render(os.path.join(OUT, "read-algorithm.svg"), W, H, *f,
           title="Зчитування: позиція → частка p декади → 10^p")


# ── запуск усіх ──────────────────────────────────────────────────────────────
ALL = [
    fig_why_graphs, fig_derating, fig_iv_curve, fig_log_axis, fig_read_point, fig_curve_zoo,
    fig_derating_interp, fig_derating_margin,
    fig_thermal_rc, fig_thermal_derating,
    fig_decade_grid, fig_read_algorithm,
]

if __name__ == "__main__":
    for fn in ALL:
        fn()
    print("OK figs: %d" % len(ALL))
