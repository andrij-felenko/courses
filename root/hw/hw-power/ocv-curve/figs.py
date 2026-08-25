# -*- coding: utf-8 -*-
"""Фігури теми «OCV-крива комірки». Запуск із теки теми: python figs.py → ./img/*.svg"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

BLUE = "#2457d6"
RED  = "#c0392b"
GREEN = "#27ae60"


def poly(pts, color=INK, sw=3.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s '
            'stroke-linejoin="round" stroke-linecap="round"/>' % (p, color, sw, d))


def polygon(pts, fill, opacity=1.0):
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return '<polygon points="%s" fill="%s" fill-opacity="%.2f" stroke="none"/>' % (p, fill, opacity)


def catmull(pts, n=20):
    """Гладка крива через контрольні точки (Catmull-Rom)."""
    if len(pts) < 3:
        return list(pts)
    ext = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        for j in range(n):
            t = j / float(n)
            t2, t3 = t * t, t * t * t
            x = 0.5 * (2 * p1[0] + (-p0[0] + p2[0]) * t +
                       (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
                       (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * (2 * p1[1] + (-p0[1] + p2[1]) * t +
                       (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
                       (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    out.append(pts[-1])
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 1 — дві OCV-криві: похила Li-ion vs пласке плато LiFePO4
# ─────────────────────────────────────────────────────────────────────────────
def fig_curves():
    W, H = 660, 430
    L, R, T, B = 76, 616, 74, 356
    vmin, vmax = 2.8, 4.3

    def sx(s):
        return L + (s / 100.0) * (R - L)

    def sy(v):
        return B - (v - vmin) / (vmax - vmin) * (B - T)

    frags = []
    # осі
    frags.append(line(L, T, L, B, color=INK, sw=1.6))
    frags.append(line(L, B, R, B, color=INK, sw=1.6))
    # y-поділки
    for v in (3.0, 3.5, 4.0):
        frags.append(line(L - 5, sy(v), L, sy(v), color=INK, sw=1.4))
        frags.append(text(L - 10, sy(v) + 4, "%.1f" % v, size=13, color=MUTED, anchor="end"))
    frags.append(text(L - 2, T - 14, "OCV, В", size=13, color=MUTED, anchor="start"))
    # x-поділки
    for s in (0, 50, 100):
        frags.append(line(sx(s), B, sx(s), B + 5, color=INK, sw=1.4))
        frags.append(text(sx(s), B + 22, "%d" % s, size=13, color=MUTED))
    frags.append(text((L + R) / 2, B + 46, "заряд (SoC), %", size=13, color=MUTED))

    # Li-ion — похила крива
    li = [(0, 3.0), (6, 3.42), (14, 3.56), (26, 3.66), (45, 3.76),
          (65, 3.86), (80, 3.98), (90, 4.08), (100, 4.2)]
    frags.append(poly(catmull([(sx(s), sy(v)) for s, v in li]), color=BLUE, sw=3.4))
    # LiFePO4 — пласке плато з різкими зламами
    lfp = [(0, 2.6), (2, 3.02), (7, 3.26), (16, 3.31), (50, 3.32),
           (84, 3.33), (93, 3.40), (98, 3.55), (100, 3.66)]
    frags.append(poly(catmull([(sx(s), sy(v)) for s, v in lfp]), color=RED, sw=3.4))

    # підписи-рамки у порожніх кутах + тонкі виноски
    bodyA, wA, hA = textbox(sx(24), sy(4.08), ["Li-ion:", "похила —", "напруга читає заряд"],
                            size=13, stroke=BLUE, fill="#eaf0fd")
    frags.append(line(sx(24), sy(4.08) + hA / 2, sx(40), sy(3.74), color=BLUE, sw=1.2))
    frags.append(bodyA)

    bodyB, wB, hB = textbox(sx(58), sy(2.99), ["LiFePO4:", "пласке плато —", "напруга майже стала"],
                            size=13, stroke=RED, fill="#fdecea")
    frags.append(line(sx(58), sy(2.99) - hB / 2, sx(58), sy(3.32), color=RED, sw=1.2))
    frags.append(bodyB)

    render(os.path.join(IMG, "curves.svg"), W, H, *frags,
           title="OCV-крива: форму задає хімія")


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 2 — напруга на клемах у часі: спокій → навантаження (просадка) → релаксація
# ─────────────────────────────────────────────────────────────────────────────
def fig_rest_vs_load():
    W, H = 660, 410
    Lx, Rx = 84, 604
    axis_y = 350
    ocv_y = 108
    load_y = 250
    recover_y = 162
    t1, t2 = 210, 384

    frags = []
    # вісь часу
    frags.append(arrow(Lx, axis_y, Rx + 6, axis_y, color=INK, sw=1.6))
    frags.append(text(Rx + 2, axis_y + 20, "час", size=13, color=MUTED, anchor="end"))

    # лінія справжньої OCV
    frags.append(line(Lx, ocv_y, Rx, ocv_y, color=GREEN, sw=1.8, dash="7 5"))
    frags.append(text(Rx, ocv_y - 10, "справжня OCV (напруга спокою)",
                      size=13, color=GREEN, anchor="end"))

    # маркери «струм увімк./вимк.»
    for tx, lab in ((t1, "струм увімк."), (t2, "струм вимк.")):
        frags.append(line(tx, ocv_y - 4, tx, axis_y, color=MUTED, sw=1.0, dash="3 4"))
        frags.append(text(tx, 60, lab, size=12, color=MUTED))

    # напруга на клемах: спокій → просадка → під навантаженням → відскок → релаксація
    seg = [(Lx, ocv_y), (t1, ocv_y), (t1, load_y), (t2, load_y + 18), (t2, recover_y)]
    relax = []
    for k in range(0, 61):
        x = t2 + (Rx - t2) * k / 60.0
        y = ocv_y + (recover_y - ocv_y) * math.exp(-3.2 * (x - t2) / (Rx - t2))
        relax.append((x, y))
    frags.append(poly(seg + relax, color=INK, sw=3.2))
    frags.append(circle(Lx + 1, ocv_y, 3.2, fill=INK, stroke=INK))

    # виноска просадки I·Rвн
    bodyD, wD, hD = textbox(t1 - 74, (ocv_y + load_y) / 2, ["I·Rвн", "(просадка)"],
                            size=13, stroke=RED, fill="#fdecea")
    frags.append(line(t1 - 74 + wD / 2, (ocv_y + load_y) / 2, t1, (ocv_y + load_y) / 2,
                      color=RED, sw=1.2))
    frags.append(bodyD)

    # виноска релаксації
    bodyRlx, wRl, hRl = textbox(500, 214, ["релаксація —", "хвилини"],
                                size=13, stroke=GREEN, fill="#eafaf1")
    frags.append(line(500, 214 - hRl / 2, 468, ocv_y + (recover_y - ocv_y) * 0.30,
                      color=GREEN, sw=1.2))
    frags.append(bodyRlx)

    # фази вздовж низу
    frags.append(text((Lx + t1) / 2, axis_y - 12, "спокій", size=13, color=MUTED))
    frags.append(text((t1 + t2) / 2, axis_y - 12, "навантаження", size=13, color=MUTED))
    frags.append(text((t2 + Rx) / 2, axis_y - 12, "спокій", size=13, color=MUTED))

    render(os.path.join(IMG, "rest-vs-load.svg"), W, H, *frags,
           title="OCV видно лише у спокої")


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 3 — гістерезис: за одного заряду напруга спокою — смужка, а не точка
# ─────────────────────────────────────────────────────────────────────────────
def fig_hysteresis():
    W, H = 640, 400
    L, R, T, B = 84, 556, 78, 328

    def hx(s):
        return L + (s / 100.0) * (R - L)

    def base_y(s):
        return (B - 34) - (s / 100.0) * (B - T - 66)

    gap = 15.0  # півширина смужки в px

    frags = []
    # осі
    frags.append(line(L, T, L, B, color=INK, sw=1.6))
    frags.append(line(L, B, R, B, color=INK, sw=1.6))
    frags.append(text(L - 2, T - 14, "напруга спокою", size=13, color=MUTED, anchor="start"))
    for s in (0, 50, 100):
        frags.append(line(hx(s), B, hx(s), B + 5, color=INK, sw=1.4))
        frags.append(text(hx(s), B + 22, "%d" % s, size=13, color=MUTED))
    frags.append(text((L + R) / 2, B + 44, "заряд (SoC), %", size=13, color=MUTED))

    ss = [i for i in range(3, 98, 2)]
    charge = [(hx(s), base_y(s) - gap) for s in ss]      # верхня — після заряду
    disch = [(hx(s), base_y(s) + gap) for s in ss]       # нижня — після розряду
    # заливка смужки
    frags.append(polygon(charge + disch[::-1], fill=GREEN, opacity=0.14))
    frags.append(poly(charge, color=RED, sw=3.0))
    frags.append(poly(disch, color=BLUE, sw=3.0))

    # підписи напрямків біля правих кінців
    frags.append(text(hx(99), base_y(97) - gap - 8, "після заряду", size=13, color=RED, anchor="end"))
    frags.append(text(hx(99), base_y(97) + gap + 18, "після розряду", size=13, color=BLUE, anchor="end"))

    # вертикальний вимір смужки за SoC = 50%
    cx = hx(50)
    frags.append(line(cx, base_y(50) - gap, cx, base_y(50) + gap, color=INK, sw=1.6))
    frags.append(line(cx - 5, base_y(50) - gap, cx + 5, base_y(50) - gap, color=INK, sw=1.6))
    frags.append(line(cx - 5, base_y(50) + gap, cx + 5, base_y(50) + gap, color=INK, sw=1.6))

    bodyN, wN, hN = textbox(hx(24), T + 44, ["за одного заряду —", "смужка, а не точка"],
                            size=13, stroke=INK)
    frags.append(line(hx(24) + wN / 2, T + 44, cx, base_y(50), color=INK, sw=1.2))
    frags.append(bodyN)

    render(os.path.join(IMG, "hysteresis.svg"), W, H, *frags,
           title="Гістерезис: OCV залежить від напрямку")


# ═════════════════════════════════════════════════════════════════════════════
# Фігури вставки «математика форми кривої» (math-curve-shape.md)
# ═════════════════════════════════════════════════════════════════════════════
RTF_MV = 25.693          # RT/F за 25 °C, мВ
ORANGE = "#d97706"
PURPLE = "#7c3aed"
GREY   = "#9aa3af"


def phi_hat(x, w):
    """Симетрична частина вільної енергії на вузол, у одиницях RT."""
    return w * x * (1 - x) + x * math.log(x) + (1 - x) * math.log(1 - x)


def dphi(x, w):
    """Похідна тієї ж вільної енергії — хімічний потенціал у одиницях RT."""
    return w * (1 - 2 * x) + math.log(x / (1 - x))


def binodal(w):
    """Ліва межа щілини незмішуваності (симетрична модель) або None."""
    if w <= 2.0:
        return None
    lo, hi = 1e-12, 0.5 - 1e-12
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if dphi(mid, w) < 0:
            lo = mid
        else:
            hi = mid
    return lo


def v_mv(x, w, cut=True):
    """Напруга відносно плато V₀, мВ (cut=True — з максвелловим зрізом)."""
    if cut:
        x1 = binodal(w)
        if x1 is not None and x1 <= x <= 1 - x1:
            return 0.0
    return -dphi(x, w) * RTF_MV


def _panel(L, R, T, B, ymin, ymax, yticks, ylab, xticks, xlab, yfmt="%g",
           axis_at_zero=False):
    """Осі панелі; повертає (frags, sx, sy)."""
    def sx(x):
        return L + x * (R - L)

    def sy(v):
        return B - (v - ymin) / (ymax - ymin) * (B - T)

    ay = sy(0) if (axis_at_zero and ymin < 0 < ymax) else B
    fr = [line(L, T - 8, L, B, color=INK, sw=1.6),
          line(L, ay, R + 8, ay, color=INK, sw=1.6)]
    for v in yticks:
        fr.append(line(L - 5, sy(v), L, sy(v), color=INK, sw=1.3))
        fr.append(text(L - 9, sy(v) + 4, yfmt % v, size=13, color=MUTED, anchor="end"))
    for x in xticks:
        yb = B + 0
        fr.append(line(sx(x), yb, sx(x), yb + 5, color=INK, sw=1.3))
        fr.append(text(sx(x), yb + 21, ("%g" % x), size=13, color=MUTED))
    fr.append(text(L - 6, T - 18, ylab, size=13, color=MUTED, anchor="start"))
    fr.append(text((L + R) / 2, B + 42, xlab, size=13, color=MUTED))
    return fr, sx, sy


def fig_free_energy_tangent():
    """g(x) і V(x) = −g′(x)/F для опуклої та двоямної вільної енергії."""
    W, H = 940, 700
    cols = [(96, 436, "Ω/RT = −2  (опукла)"), (540, 880, "Ω/RT = +3  (дві ями)")]
    T1, B1 = 108, 300      # верхній ряд — вільна енергія
    T2, B2 = 430, 622      # нижній ряд — напруга
    frags = []

    for (L, R, head), w in zip(cols, (-2.0, 3.0)):
        frags.append(text((L + R) / 2, 74, head, size=15, bold=True,
                          color=(NEG if w < 0 else POS)))

        # ── верх: вільна енергія на вузол, у одиницях RT
        xs = [0.004 + 0.992 * i / 400.0 for i in range(401)]
        gs = [phi_hat(x, w) for x in xs]
        gmin, gmax = min(gs), max(gs)
        pad = 0.16 * (gmax - gmin)
        fr, sx, sy = _panel(L, R, T1, B1, gmin - pad, gmax + pad,
                            [round(gmin, 2), round(gmax, 2)],
                            "g(x)/RT", (0, 0.5, 1.0), "x — заповнення електрода",
                            yfmt="%.2f")
        frags += fr
        frags.append(poly([(sx(x), sy(g)) for x, g in zip(xs, gs)],
                          color=(NEG if w < 0 else POS), sw=3.0))

        x1 = binodal(w)
        if x1 is not None:
            gt = phi_hat(x1, w)
            frags.append(line(sx(x1) - 26, sy(gt), sx(1 - x1) + 26, sy(gt),
                              color=INK, sw=2.0, dash="8 5"))
            for xm in (x1, 1 - x1):
                frags.append(circle(sx(xm), sy(gt), 4.6, fill=BG, stroke=INK, sw=2.0))
                # тонка нитка вниз, до кінця плато — з розривом під підпис x₁/x₂
                frags.append(line(sx(xm), sy(gt) + 8, sx(xm), B1 + 26, color=GREY,
                                  sw=1.1, dash="3 5"))
                frags.append(line(sx(xm), B1 + 54, sx(xm), B2, color=GREY,
                                  sw=1.1, dash="3 5"))
            b1, wb1, hb1 = textbox((L + R) / 2, B1 + 84,
                                   ["спільна дотична — пряма,", "тож нахил на ній сталий"],
                                   size=13, stroke=INK, fill="#f4f6f8")
            frags.append(b1)
            frags.append(text(sx(x1), B1 + 42, "x₁", size=13, color=INK))
            frags.append(text(sx(1 - x1), B1 + 42, "x₂", size=13, color=INK))
        else:
            b1, wb1, hb1 = textbox((L + R) / 2, B1 + 84,
                                   ["опукла всюди —", "жодної прямої ділянки"],
                                   size=13, stroke=INK, fill="#f4f6f8")
            frags.append(b1)

        # ── низ: напруга (мВ від плато) — мінус похідна
        fr, sx2, sy2 = _panel(L, R, T2, B2, -230, 230, [-200, -100, 0, 100, 200],
                              "V − V₀, мВ", (0, 0.5, 1.0), "x — заповнення електрода",
                              yfmt="%d", axis_at_zero=True)
        frags += fr
        pts = [(sx2(x), sy2(max(-228.0, min(228.0, v_mv(x, w))))) for x in xs]
        frags.append(poly(pts, color=(NEG if w < 0 else POS), sw=3.2))
        if x1 is None:
            b2, wb2, hb2 = textbox(L + 100, B2 - 34, ["похила: кожному x —", "своя напруга"],
                                   size=13, stroke=NEG, fill="#eaf0fd")
        else:
            b2, wb2, hb2 = textbox((L + R) / 2, T2 + 46,
                                   ["плато: на всій щілині", "напруга не рухається"],
                                   size=13, stroke=POS, fill="#fdecea")
        frags.append(b2)

    render(os.path.join(IMG, "free-energy-tangent.svg"), W, H, *frags,
           title="Напруга — це нахил вільної енергії: пряма ділянка дає плато")


def fig_omega_family():
    """Родина кривих V(x) за різних Ω/RT — перехід через поріг Ω = 2RT."""
    W, H = 780, 516
    L, R, T, B = 84, 560, 82, 372
    frags = []
    fr, sx, sy = _panel(L, R, T, B, -230, 230, [-200, -100, 0, 100, 200],
                        "V − V₀, мВ", (0, 0.25, 0.5, 0.75, 1.0),
                        "x — заповнення електрода", yfmt="%d")
    frags += fr

    fam = [(-4.0, "−4", NEG), (-2.0, "−2", "#5b8def"), (0.0, "0", MUTED),
           (2.0, "+2", ORANGE), (3.7, "+3.7", POS)]
    xs = [0.02 + 0.96 * i / 300.0 for i in range(301)]
    for w, lab, col in fam:
        pts = [(sx(x), sy(max(-228.0, min(228.0, v_mv(x, w))))) for x in xs]
        frags.append(poly(pts, color=col, sw=3.0 if w in (-4.0, 3.7) else 2.4))

    # легенда у порожньому правому верхньому куті
    lx, ly = R + 26, T + 6
    frags.append(rect(lx, ly, 168, 148, fill="#fbfcfd", stroke=MUTED, sw=1.2))
    frags.append(text(lx + 84, ly + 24, "Ω/RT", size=13, bold=True, color=INK))
    for i, (w, lab, col) in enumerate(fam):
        yy = ly + 46 + i * 21
        frags.append(line(lx + 14, yy - 4, lx + 46, yy - 4, color=col, sw=3.0))
        frags.append(text(lx + 54, yy, lab, size=13, color=INK, anchor="start"))

    b, wb, hb = textbox((L + R) / 2 + 30, B + 90,
                        ["поріг Ω = 2RT: нижче — крива похила по всьому діапазону,",
                         "вище — відкривається плато й далі лише ширшає"],
                        size=13, stroke=INK, fill="#f4f6f8")
    frags.append(b)

    render(os.path.join(IMG, "omega-family.svg"), W, H, *frags,
           title="Одне число Ω/RT веде криву від похилої до пласкої")


def fig_metastable():
    """Петля навколо плато: бінодаль, спінодаль і звідки береться гістерезис."""
    W, H = 780, 500
    L, R, T, B = 92, 596, 92, 356
    w = 3.7
    x1 = binodal(w)
    xs_sp = 0.5 * (1 - math.sqrt(1 - 2.0 / w))
    frags = []
    fr, sx, sy = _panel(L, R, T, B, -52, 52, [-40, -22, 0, 22, 40],
                        "V − V₀, мВ", (0, 0.5, 1.0),
                        "x — заповнення електрода", yfmt="%d")
    frags += fr

    xs = [0.006 + 0.988 * i / 400.0 for i in range(401)]
    raw = [(sx(x), sy(max(-50.0, min(50.0, v_mv(x, w, cut=False))))) for x in xs]
    frags.append(poly(raw, color=GREY, sw=2.0, dash="6 5"))

    # рівноважне плато
    frags.append(poly([(sx(x1), sy(0)), (sx(1 - x1), sy(0))], color=INK, sw=3.6))
    # метастабільні гілки: розряд (x росте) — нижче плато; заряд (x спадає) — вище
    low = [(sx(x), sy(v_mv(x, w, cut=False))) for x in xs if x1 <= x <= xs_sp]
    high = [(sx(x), sy(v_mv(x, w, cut=False))) for x in xs if 1 - xs_sp <= x <= 1 - x1]
    frags.append(poly(low, color=NEG, sw=3.4))
    frags.append(poly(high, color=POS, sw=3.4))

    for xm, lab, dy in ((x1, "x₁ = 0.030", 26), (xs_sp, "спінодаль 0.161", 50),
                        (1 - xs_sp, "спінодаль 0.839", 50), (1 - x1, "x₂ = 0.970", 26)):
        frags.append(line(sx(xm), T + 4, sx(xm), B, color=GREY, sw=1.0, dash="3 5"))
        frags.append(text(sx(xm), B + dy, lab, size=13, color=MUTED))

    for v, lab in ((22, "+22 мВ"), (-22, "−22 мВ")):
        frags.append(line(L, sy(v), R, sy(v), color=GREY, sw=1.0, dash="3 5"))
    frags.append(text(R + 10, sy(22) + 4, "+22 мВ", size=13, color=POS, anchor="start"))
    frags.append(text(R + 10, sy(-22) + 4, "−22 мВ", size=13, color=NEG, anchor="start"))

    bA, wA, hA = textbox(L + 150, T + 40, ["заряд: гілка тримається", "вище плато"],
                         size=13, stroke=POS, fill="#fdecea")
    frags.append(line(L + 150, T + 40 + hA / 2, sx(1 - xs_sp) - 6, sy(20), color=POS, sw=1.2))
    frags.append(bA)
    bB, wB, hB = textbox(R - 148, B - 42, ["розряд: гілка тримається", "нижче плато"],
                         size=13, stroke=NEG, fill="#eaf0fd")
    frags.append(line(R - 148, B - 42 - hB / 2, sx(xs_sp) + 6, sy(-20), color=NEG, sw=1.2))
    frags.append(bB)
    bC, wC, hC = textbox((L + R) / 2, B + 96,
                         ["рівноважне плато (сіре штрихове — та сама формула без зрізу):",
                          "гістерезис — це різниця між гілкою й плато, а не падіння на опорі"],
                         size=13, stroke=INK, fill="#f4f6f8")
    frags.append(bC)

    render(os.path.join(IMG, "metastable-branches.svg"), W, H, *frags,
           title="Звідки на плато береться гістерезис")


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. (вставка proj) — вузли таблиці вгорі, похибка заряду σ = σ_V/нахил унизу
# ─────────────────────────────────────────────────────────────────────────────
def fig_lut_knots_sigma():
    W, H = 700, 560
    L, R = 96, 654
    T1, B1 = 62, 272          # панель OCV
    T2, B2 = 342, 486         # панель σ
    vmin, vmax = 2.45, 3.8
    smax = 20.0               # стеля осі σ, %
    SIG_V = 50.0              # σ вольтметра в одиницях 0.1 мВ (тобто 5 мВ)
    CEIL = 15.0               # стеля довіри, %

    # вузли LFP-таблиці: (напруга в одиницях 0.1 мВ, заряд у проміле)
    kn = [(26000, 0), (30200, 20), (32600, 70), (33100, 160),
          (33200, 500), (33300, 840), (34000, 930), (35500, 980), (36600, 1000)]
    segs = []
    for (v0, s0), (v1, s1) in zip(kn, kn[1:]):
        segs.append((s0, s1, SIG_V * (s1 - s0) / float(v1 - v0) / 10.0))   # σ у %

    def sx(pm):
        return L + (pm / 1000.0) * (R - L)

    def vy(v):
        return B1 - (v - vmin) / (vmax - vmin) * (B1 - T1)

    def gy(s):
        return B2 - (s / smax) * (B2 - T2)

    frags = []
    # 1) смуга «тут таблиця сліпа» — наскрізь через обидві панелі, під усім
    blind = [(s0, s1) for s0, s1, sg in segs if sg > CEIL]
    bx0, bx1 = sx(blind[0][0]), sx(blind[-1][1])
    frags.append(polygon([(bx0, T1 - 8), (bx1, T1 - 8), (bx1, B2), (bx0, B2)],
                         fill=RED, opacity=0.08))

    # 2) верхня панель — крива й вузли
    frags.append(line(L, T1, L, B1, color=INK, sw=1.6))
    frags.append(line(L, B1, R, B1, color=INK, sw=1.6))
    frags.append(text(L - 2, T1 - 16, "OCV, В", size=13, color=MUTED, anchor="start"))
    for v in (2.6, 3.0, 3.4, 3.8):
        frags.append(line(L - 5, vy(v), L, vy(v), color=INK, sw=1.4))
        frags.append(text(L - 10, vy(v) + 4, "%.1f" % v, size=13, color=MUTED, anchor="end"))
    for pm in (0, 250, 500, 750, 1000):
        frags.append(line(sx(pm), B1, sx(pm), B1 + 4, color=INK, sw=1.2))

    pts = [(sx(s), vy(v / 10000.0)) for v, s in kn]
    frags.append(poly(catmull(pts), color="#b9bec7", sw=6.0))     # справжня крива
    frags.append(poly(pts, color=BLUE, sw=2.4))                   # відрізки таблиці
    for x, y in pts:
        frags.append(circle(x, y, 3.6, fill=BLUE, stroke=BLUE, sw=1.0))

    frags.append(text(sx(215), vy(2.80), "справжня крива", size=13,
                      color="#8b9098", anchor="start"))
    frags.append(text(sx(215), vy(2.62), "вузли таблиці й прямі відрізки між ними",
                      size=13, color=BLUE, anchor="start"))

    # 3) нижня панель — σ заряду по відрізках
    frags.append(line(L, T2, L, B2, color=INK, sw=1.6))
    frags.append(line(L, B2, R, B2, color=INK, sw=1.6))
    frags.append(text(L - 2, T2 - 16, "σ заряду, %", size=13, color=MUTED, anchor="start"))
    for s in (0, 5, 10, 15, 20):
        frags.append(line(L - 5, gy(s), L, gy(s), color=INK, sw=1.4))
        frags.append(text(L - 10, gy(s) + 4, "%d" % s, size=13, color=MUTED, anchor="end"))
    for pm in (0, 250, 500, 750, 1000):
        frags.append(line(sx(pm), B2, sx(pm), B2 + 5, color=INK, sw=1.4))
        frags.append(text(sx(pm), B2 + 22, "%d" % (pm // 10), size=13, color=MUTED))
    frags.append(text((L + R) / 2, B2 + 46, "заряд (SoC), %", size=13, color=MUTED))

    prev = None
    for s0, s1, sg in segs:
        col = RED if sg > CEIL else BLUE
        frags.append(line(sx(s0), gy(sg), sx(s1), gy(sg), color=col, sw=3.2))
        if prev is not None:
            frags.append(line(sx(s0), gy(prev), sx(s0), gy(sg),
                              color=RED if max(prev, sg) > CEIL else BLUE, sw=1.6))
        prev = sg

    frags.append(line(L, gy(CEIL), R, gy(CEIL), color=RED, sw=1.5, dash="7 5"))
    frags.append(text(R, gy(CEIL) - 9, "стеля довіри", size=13, color=RED, anchor="end"))

    bodyB, wB, hB = textbox(sx(500), gy(7.2),
                            ["тут таблиця сліпа: σ ≈ 17 % — вище за стелю",
                             "→ відповідь у смітник"],
                            size=13, stroke=RED, fill="#fdecea")
    frags.append(bodyB)

    render(os.path.join(IMG, "lut-knots-sigma.svg"), W, H, *frags,
           title="Нахил відрізка задає довіру до відповіді")


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. (вставка proj) — шлях від напруги спокою до виправленої оцінки заряду
# ─────────────────────────────────────────────────────────────────────────────
def fig_gauge_pipeline():
    W, H = 700, 530
    CX = 300
    S = 13

    frags = []
    boxes = []
    spec = [
        (52,  ["напруга комірки, зміряна у спокої"], INK, FILL),
        (132, ["умова спокою:", "|I| < 30 мА, довше за 10 хв,", "напруга вже не повзе"],
         INK, FILL),
        (232, ["таблиця: знайти відрізок →", "заряд SoC і нахил цього відрізка"],
         BLUE, "#eaf0fd"),
        (326, ["σ = σ_V / нахил", "σ не вища за стелю?"], BLUE, "#eaf0fd"),
        (416, ["злити з лічильником заряду:", "w = σл² / (σл² + σ²)"], GREEN, "#eafaf1"),
        (492, ["SoC уточнено, недовіра до лічильника впала"], GREEN, "#eafaf1"),
    ]
    for cy, lines, col, fill in spec:
        body, w, h = textbox(CX, cy, lines, size=S, stroke=col, fill=fill, min_w=300)
        boxes.append((cy, h, w, body))

    for i in range(len(boxes) - 1):
        y1 = boxes[i][0] + boxes[i][1] / 2
        y2 = boxes[i + 1][0] - boxes[i + 1][1] / 2
        frags.append(arrow(CX, y1, CX, y2 - 2, color=INK, sw=1.8))
    frags.append(text(CX + 10, 190, "так", size=12, color=MUTED, anchor="start"))
    frags.append(text(CX + 10, 378, "так", size=12, color=MUTED, anchor="start"))

    # бічний вихід «ні» — один на два відгалуження
    ex, ey = 586, 236
    bodyE, wE, hE = textbox(ex, ey, ["оцінку", "лишаємо", "як була"],
                            size=S, stroke=MUTED, fill=FILL)
    for i, dy in ((1, 22), (3, -22)):
        cy, h, w, _ = boxes[i]
        frags.append(arrow(CX + w / 2 + 4, cy, ex - wE / 2 - 5, ey + dy, color=MUTED, sw=1.6))
    frags.append(text(CX + 162, 122, "ні", size=12, color=MUTED, anchor="start"))
    frags.append(text(CX + 162, 316, "ні", size=12, color=MUTED, anchor="start"))

    for _, _, _, body in boxes:
        frags.append(body)
    frags.append(bodyE)

    render(os.path.join(IMG, "gauge-pipeline.svg"), W, H, *frags,
           title="Куди в паливомірі влазить таблиця OCV→SoC")


if __name__ == "__main__":
    fig_curves()
    fig_rest_vs_load()
    fig_hysteresis()
    fig_free_energy_tangent()
    fig_omega_family()
    fig_metastable()
    fig_lut_knots_sigma()
    fig_gauge_pipeline()
    print("OK: curves.svg, rest-vs-load.svg, hysteresis.svg, "
          "free-energy-tangent.svg, omega-family.svg, metastable-branches.svg, "
          "lut-knots-sigma.svg, gauge-pipeline.svg")
