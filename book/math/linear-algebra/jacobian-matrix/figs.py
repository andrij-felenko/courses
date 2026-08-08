# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Якобіан: локальне лінійне наближення відображення».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)

SOFT_POS = "#fdecea"
SOFT_NEG = "#eaf0fd"
SOFT_FLD = "#e8f6ee"


def polyline(pts, color=MUTED, sw=1.2, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (" ".join("%.1f,%.1f" % (p[0], p[1]) for p in pts), color, sw, d))


def polygon(pts, fill="none", stroke=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>'
            % (" ".join("%.1f,%.1f" % (p[0], p[1]) for p in pts), fill, stroke, sw, d))


def lin(a, b, n):
    return [a + (b - a) * i / float(n - 1) for i in range(n)]


# ── Фігура 1: маленький квадрат → майже паралелограм ─────────────────────────
# Серце теми: криве відображення, узяте на малому клаптику, спрямляється.
# Образ квадратика майже збігається з паралелограмом, сторони якого — стовпці якобіана.
def fig_linearize():
    W, H = 1020, 560
    u0, u1 = 0.50, 1.50
    v0, v1 = 0.20, 1.00
    pu, pv, h = 0.95, 0.52, 0.22

    def F(u, v):
        return (u * u - v * v, 2.0 * u * v)

    # ліва панель — площина (u, v)
    Lx, Ly, Lw, Lh = 80, 110, 350, 330

    def Lp(u, v):
        return (Lx + (u - u0) / (u1 - u0) * Lw, Ly + Lh - (v - v0) / (v1 - v0) * Lh)

    parts = [rect(Lx, Ly, Lw, Lh, fill="#ffffff", stroke=MUTED, sw=1.2, rx=4)]
    for u in lin(u0, u1, 6):
        parts.append(polyline([Lp(u, v0), Lp(u, v1)], color="#c9ced6", sw=1.1))
    for v in lin(v0, v1, 5):
        parts.append(polyline([Lp(u0, v), Lp(u1, v)], color="#c9ced6", sw=1.1))
    sq = [Lp(pu, pv), Lp(pu + h, pv), Lp(pu + h, pv + h), Lp(pu, pv + h)]
    parts.append(polygon(sq, fill=SOFT_POS, stroke=POS, sw=2.2))
    parts.append(text(Lx + Lw / 2, Ly - 24, "вхід: площина (u, v)", size=15, bold=True))
    parts.append(text(sq[0][0] - 12, sq[0][1] + 24, "точка p", size=13, color=POS, anchor="end"))

    # права панель — площина (x, y), образ сітки
    Rx, Ry, Rw, Rh = 590, 110, 350, 330
    xs, ys = [], []
    for u in lin(u0, u1, 9):
        for v in lin(v0, v1, 9):
            x, y = F(u, v)
            xs.append(x)
            ys.append(y)
    xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)
    s = min(Rw / (xmax - xmin), Rh / (ymax - ymin)) * 0.92
    cx0 = Rx + Rw / 2 - (xmin + xmax) / 2 * s
    cy0 = Ry + Rh / 2 + (ymin + ymax) / 2 * s

    def Rp(x, y):
        return (cx0 + x * s, cy0 - y * s)

    parts.append(rect(Rx, Ry, Rw, Rh, fill="#ffffff", stroke=MUTED, sw=1.2, rx=4))
    for u in lin(u0, u1, 6):
        parts.append(polyline([Rp(*F(u, v)) for v in lin(v0, v1, 24)], color="#c9ced6", sw=1.1))
    for v in lin(v0, v1, 5):
        parts.append(polyline([Rp(*F(u, v)) for u in lin(u0, u1, 24)], color="#c9ced6", sw=1.1))

    # образ квадрата — чотири криві сторони
    img = []
    img += [F(u, pv) for u in lin(pu, pu + h, 12)]
    img += [F(pu + h, v) for v in lin(pv, pv + h, 12)]
    img += [F(u, pv + h) for u in lin(pu + h, pu, 12)]
    img += [F(pu, v) for v in lin(pv + h, pv, 12)]
    parts.append(polygon([Rp(*q) for q in img], fill=SOFT_POS, stroke=POS, sw=2.2))

    # паралелограм на стовпцях якобіана
    P = F(pu, pv)
    e1 = (h * 2 * pu, h * 2 * pv)
    e2 = (-h * 2 * pv, h * 2 * pu)
    par = [P, (P[0] + e1[0], P[1] + e1[1]),
           (P[0] + e1[0] + e2[0], P[1] + e1[1] + e2[1]),
           (P[0] + e2[0], P[1] + e2[1])]
    parts.append(polygon([Rp(*q) for q in par], fill="none", stroke=NEG, sw=2.2, dash="6,5"))
    a0 = Rp(*P)
    a1 = Rp(P[0] + e1[0], P[1] + e1[1])
    a2 = Rp(P[0] + e2[0], P[1] + e2[1])
    parts.append(arrow(a0[0], a0[1], a1[0], a1[1], color=NEG, sw=2.2))
    parts.append(arrow(a0[0], a0[1], a2[0], a2[1], color=NEG, sw=2.2))
    parts.append(text(a1[0] + 16, a1[1] + 26, "h · ∂f/∂u", size=13, color=NEG, anchor="start"))
    parts.append(text(a2[0] - 16, a2[1] - 14, "h · ∂f/∂v", size=13, color=NEG, anchor="end"))
    parts.append(text(Rx + Rw / 2, Ry - 24, "вихід: площина (x, y)", size=15, bold=True))

    parts.append(arrow(Lx + Lw + 24, Ly + Lh / 2, Rx - 24, Ly + Lh / 2, color=INK, sw=2.0))
    parts.append(text((Lx + Lw + Rx) / 2, Ly + Lh / 2 - 18, "f", size=17, bold=True, italic=True))

    box, bw, bh = textbox(W / 2, H - 58,
                          ["червоне — справжній образ квадратика, синє пунктирне — паралелограм",
                           "на стовпцях J(p); чим менший квадратик, тим ближче вони збігаються"],
                          size=13, pad=12, fill=FILL)
    parts.append(box)
    render("img/linearize.svg", W, H, *parts,
           title="Мале коло навколо точки: криве відображення спрямляється")


# ── Фігура 2: як читати матрицю — рядки й стовпці ────────────────────────────
def fig_anatomy():
    W, H = 1000, 470
    cw, ch = 132, 58
    n, m = 4, 3
    x0, y0 = 300, 130
    parts = []

    hi_row, hi_col = 1, 2   # рахуємо з 0
    for i in range(m):
        for j in range(n):
            fill = "#ffffff"
            if i == hi_row and j == hi_col:
                fill = "#efe4f6"
            elif i == hi_row:
                fill = SOFT_POS
            elif j == hi_col:
                fill = SOFT_NEG
            lbl = "∂f%s/∂x%s" % ("₁₂₃"[i], "₁₂₃₄"[j])
            parts.append(fitbox(x0 + j * cw, y0 + i * ch, cw - 6, ch - 6, lbl,
                                size=14, fill=fill, stroke=LINE, sw=1.2))

    parts.append(text(x0 - 24, y0 + hi_row * ch + ch / 2 - 6, "рядок i:", size=13,
                      color=POS, anchor="end", bold=True))
    parts.append(text(x0 - 24, y0 + hi_row * ch + ch / 2 + 12, "градієнт виходу fᵢ", size=13,
                      color=POS, anchor="end"))
    parts.append(text(x0 + hi_col * cw + cw / 2, y0 - 34, "стовпець j:", size=13,
                      color=NEG, bold=True))
    parts.append(text(x0 + hi_col * cw + cw / 2, y0 - 16, "куди їде вихід, коли рухається xⱼ",
                      size=13, color=NEG))

    parts.append(text(x0 + n * cw / 2, y0 + m * ch + 34, "n стовпців = стільки входів", size=13,
                      color=MUTED))
    parts.append(text(x0 - 24, y0 + m * ch + 34, "m рядків = стільки виходів", size=13,
                      color=MUTED, anchor="end"))

    box, bw, bh = textbox(W / 2, H - 52,
                          "Δf ≈ J · Δx  —  тому рядків стільки, скільки виходів, а стовпців стільки, скільки входів",
                          size=13, pad=12, fill=FILL)
    parts.append(box)
    render("img/anatomy.svg", W, H, *parts, title="Що означає кожен рядок і кожен стовпець якобіана")


# ── Фігура 3: полярні координати — чому в інтегралі стоїть r ─────────────────
def fig_polar():
    W, H = 1020, 540
    parts = []

    # ліва панель: прямокутник (r, φ) з двома однаковими комірками
    Lx, Ly, Lw, Lh = 80, 120, 330, 300
    r0, r1 = 0.0, 1.0
    f0, f1 = 0.0, 1.2

    def Lp(r, f):
        return (Lx + (r - r0) / (r1 - r0) * Lw, Ly + Lh - (f - f0) / (f1 - f0) * Lh)

    parts.append(rect(Lx, Ly, Lw, Lh, fill="#ffffff", stroke=MUTED, sw=1.2, rx=4))
    for r in lin(r0, r1, 6):
        parts.append(polyline([Lp(r, f0), Lp(r, f1)], color="#c9ced6", sw=1.1))
    for f in lin(f0, f1, 5):
        parts.append(polyline([Lp(r0, f), Lp(r1, f)], color="#c9ced6", sw=1.1))
    dr, dphi = 0.18, 0.26
    for (rr, ff, col, soft) in ((0.22, 0.30, NEG, SOFT_NEG), (0.72, 0.62, POS, SOFT_POS)):
        cell = [Lp(rr, ff), Lp(rr + dr, ff), Lp(rr + dr, ff + dphi), Lp(rr, ff + dphi)]
        parts.append(polygon(cell, fill=soft, stroke=col, sw=2.2))
    parts.append(text(Lx + Lw / 2, Ly - 24, "площина параметрів (r, φ)", size=15, bold=True))
    parts.append(text(Lx + Lw / 2, Ly + Lh + 30, "комірки dr × dφ однакові", size=13, color=MUTED))

    # права панель: сектор
    Rx, Ry, Rw, Rh = 560, 120, 400, 300
    cx, cy, S = Rx + 26, Ry + Rh - 20, 300.0

    def Rp(r, f):
        return (cx + r * S * math.cos(f), cy - r * S * math.sin(f))

    parts.append(rect(Rx, Ry, Rw, Rh, fill="#ffffff", stroke=MUTED, sw=1.2, rx=4))
    for r in lin(r0, r1, 6):
        if r > 0:
            parts.append(polyline([Rp(r, f) for f in lin(f0, f1, 30)], color="#c9ced6", sw=1.1))
    for f in lin(f0, f1, 5):
        parts.append(polyline([Rp(r0, f), Rp(r1, f)], color="#c9ced6", sw=1.1))
    for (rr, ff, col, soft) in ((0.22, 0.30, NEG, SOFT_NEG), (0.72, 0.62, POS, SOFT_POS)):
        pts = [Rp(rr + t * dr, ff) for t in lin(0, 1, 8)]
        pts += [Rp(rr + dr, ff + t * dphi) for t in lin(0, 1, 8)]
        pts += [Rp(rr + (1 - t) * dr, ff + dphi) for t in lin(0, 1, 8)]
        pts += [Rp(rr, ff + (1 - t) * dphi) for t in lin(0, 1, 8)]
        parts.append(polygon(pts, fill=soft, stroke=col, sw=2.2))
    big = Rp(0.72 + dr / 2, 0.62 + dphi + 0.05)
    parts.append(text(big[0] + 46, big[1] - 12, "довжина дуги = r · dφ", size=13, color=POS,
                      anchor="start"))
    edge = Rp(0.72 + dr / 2, 0.62 - 0.06)
    parts.append(text(edge[0] + 30, edge[1] + 24, "ширина = dr", size=13, color=POS, anchor="start"))
    small = Rp(0.22 + dr / 2, 0.30 + dphi / 2)
    parts.append(text(small[0] - 34, small[1] - 34, "менший r —", size=12, color=NEG, anchor="end"))
    parts.append(text(small[0] - 34, small[1] - 18, "менша площа", size=12, color=NEG, anchor="end"))
    parts.append(text(Rx + Rw / 2, Ry - 24, "площина (x, y)", size=15, bold=True))

    box, bw, bh = textbox(W / 2, H - 52,
                          "площа образу = r · dr · dφ  —  саме det J = r, тому в інтегралі з'являється множник r",
                          size=13, pad=12, fill=SOFT_FLD, stroke=FIELD)
    parts.append(box)
    render("img/polar-cell.svg", W, H, *parts,
           title="Однакові комірки в (r, φ) дають різні площі в (x, y)")


# ── Фігура 4: коли визначник падає до нуля ───────────────────────────────────
def fig_singular():
    W, H = 1020, 460
    parts = []
    cases = [
        ((1.00, 0.15), (0.10, 1.00), "det J = 0.985", "площа майже зберігається", FIELD),
        ((1.00, 0.60), (0.75, 0.55), "det J = 0.10", "стовпці зблизились — майже плоско", POS),
        ((1.00, 0.60), (0.50, 0.30), "det J = 0", "стовпці збіглись — напрям загинув", NEG),
    ]
    S = 118.0
    for k, (c1, c2, lab, note, col) in enumerate(cases):
        ox = 175 + k * 330
        oy = 300
        parts.append(rect(ox - 120, 78, 260, 268, fill="#ffffff", stroke=MUTED, sw=1.2, rx=6))

        def P(a, b):
            return (ox + a * S, oy - b * S)
        quad = [P(0, 0), P(c1[0], c1[1]), P(c1[0] + c2[0], c1[1] + c2[1]), P(c2[0], c2[1])]
        parts.append(polygon(quad, fill="#f0f2f5", stroke=col, sw=2.0))
        parts.append(arrow(P(0, 0)[0], P(0, 0)[1], P(*c1)[0], P(*c1)[1], color=INK, sw=2.2))
        parts.append(arrow(P(0, 0)[0], P(0, 0)[1], P(*c2)[0], P(*c2)[1], color=INK, sw=2.2))
        parts.append(text(ox, 372, lab, size=14, bold=True, color=col))
        parts.append(text(ox, 396, note, size=12, color=MUTED))

    box, bw, bh = textbox(W / 2, H - 32,
                          "що ближче det J до нуля, то сильніше обернене перетворення роздуває похибки",
                          size=13, pad=11, fill=FILL)
    parts.append(box)
    render("img/singular.svg", W, H, *parts,
           title="Площа паралелограма — це визначник; нуль означає втрату виміру")


# ── Фігура 5 (вставка math-volume-scale): сферична клітинка ──────────────────
# Ліворуч — переріз площиною через вісь z: видно, що відстань точки до осі — r·sin θ.
# Праворуч — сама клітинка: три ребра, добуток яких і дає r²·sin θ.
def fig_sphere_cell():
    W, H = 1060, 620
    parts = []

    # ── ліва панель: меридіанний переріз ──
    Lx, Ly, Lw, Lh = 60, 90, 440, 410
    parts.append(rect(Lx, Ly, Lw, Lh, fill="#ffffff", stroke=MUTED, sw=1.2, rx=4))
    ox, oy, R = 170.0, 460.0, 300.0

    def Sp(rr, th):                      # rr у частках R, th у градусах від осі z
        a = math.radians(th)
        return (ox + rr * R * math.sin(a), oy - rr * R * math.cos(a))

    parts.append(arrow(ox, oy, ox, oy - 330, color=INK, sw=1.8))
    parts.append(text(ox + 26, 140, "вісь z", size=13, color=MUTED, anchor="start"))
    parts.append(polyline([Sp(1.0, t) for t in lin(0, 90, 40)], color=MUTED, sw=1.4))

    th0 = 52.0
    P = Sp(0.78, th0)
    parts.append(polyline([(ox, oy), P], color=POS, sw=2.4))
    parts.append(polyline([P, Sp(1.0, th0)], color=POS, sw=1.4, dash="5,5"))
    parts.append(circle(P[0], P[1], 5.5, fill=POS, stroke=POS, sw=1.0))
    parts.append(polyline([(ox, P[1]), P], color=NEG, sw=2.0, dash="6,4"))

    parts.append(text(298, 392, "r", size=15, color=POS, anchor="start", italic=True))
    parts.append(polyline([Sp(0.24, t) for t in lin(0, th0, 20)], color=MUTED, sw=1.2))
    parts.append(text(215, 378, "θ", size=15, color=MUTED, anchor="start", italic=True))
    parts.append(text(250, 340, "r · sin θ", size=14, color=NEG))
    parts.append(text(Lx + Lw / 2, 68, "переріз площиною, що містить вісь z",
                      size=14, bold=True))

    # ── права панель: клітинка як паралелепіпед ──
    Rx, Ry, Rw, Rh = 550, 90, 440, 410
    parts.append(rect(Rx, Ry, Rw, Rh, fill="#ffffff", stroke=MUTED, sw=1.2, rx=4))

    A = (645.0, 415.0)
    ef = (200.0, 50.0)      # уздовж паралелі
    er = (85.0, -48.0)      # уздовж променя
    et = (0.0, -140.0)      # уздовж меридіана

    def add(*vs):
        x, y = A
        for v in vs:
            x, y = x + v[0], y + v[1]
        return (x, y)

    B, C, D = add(ef), add(er), add(et)
    BC, BD, CD, T = add(ef, er), add(ef, et), add(er, et), add(ef, er, et)

    for face in ((A, B, BC, C), (A, B, BD, D), (A, C, CD, D)):
        parts.append(polygon(list(face), fill="#eef1f5", stroke="none", sw=0))
    for e in ((B, BC), (B, BD), (C, BC), (C, CD), (D, BD), (D, CD),
              (T, BC), (T, BD), (T, CD)):
        parts.append(polyline(list(e), color=MUTED, sw=1.3))

    parts.append(arrow(A[0], A[1], B[0], B[1], color=NEG, sw=2.4))
    parts.append(arrow(A[0], A[1], C[0], C[1], color=FIELD, sw=2.4))
    parts.append(arrow(A[0], A[1], D[0], D[1], color=POS, sw=2.4))

    parts.append(text(745, 485, "r · sin θ · dφ", size=14, color=NEG))
    parts.append(text(748, 352, "dr", size=14, color=FIELD, anchor="start"))
    parts.append(text(628, 345, "r · dθ", size=14, color=POS, anchor="end"))
    parts.append(text(Rx + Rw / 2, 68, "клітинка навколо точки: три ребра",
                      size=14, bold=True))

    box, bw, bh = textbox(W / 2, 560,
                          "об'єм = dr · (r · dθ) · (r · sin θ · dφ) = r² · sin θ · dr dθ dφ  "
                          "—  рівно те, що дає визначник 3×3",
                          size=13, pad=12, fill=SOFT_FLD, stroke=FIELD)
    parts.append(box)
    render("img/sphere-cell.svg", W, H, *parts,
           title="Чому у сферичних координатах множник саме r² · sin θ")


# ── Фігура 6 (до вставки proj-numerical-jacobian): похибка проти кроку h ─────
# Дві похибки тягнуть у різні боки: зріз ряду росте з h, втрата цифр — коли h падає.
# Тому крива має мінімум, і він далеко не на «якнайменшому» кроці.
_SUP = {"-": "⁻", "0": "⁰", "1": "¹", "2": "²", "3": "³",
        "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸",
        "9": "⁹"}


def _sup(n):
    return "".join(_SUP[c] for c in str(n))


def fig_fd_error():
    import cmath
    W, H = 950, 575
    PX, PY, PW, PH = 118, 82, 762, 396
    K0, K1 = -18.0, -1.0          # межі по log10(h)
    L0, L1 = -17.0, 0.0           # межі по log10(відносної похибки)

    def X(k):
        return PX + (k - K0) / (K1 - K0) * PW

    def Y(l):
        return PY + PH - (l - L0) / (L1 - L0) * PH

    x0 = 1.5

    def f(t):
        return math.exp(t) / math.sqrt(math.sin(t) ** 3 + math.cos(t) ** 3)

    def fz(t):
        return cmath.exp(t) / cmath.sqrt(cmath.sin(t) ** 3 + cmath.cos(t) ** 3)

    g = math.sin(x0) ** 3 + math.cos(x0) ** 3
    gp = 3 * math.sin(x0) ** 2 * math.cos(x0) - 3 * math.cos(x0) ** 2 * math.sin(x0)
    exact = f(x0) * (1 - gp / (2 * g))

    def rel(v):
        e = abs(v - exact) / abs(exact)
        return min(max(e, 1e-17), 1.0)

    fwd, cen, cst = [], [], []
    k = K0
    while k <= K1 + 1e-9:
        h = 10.0 ** k
        fwd.append((X(k), Y(math.log10(rel((f(x0 + h) - f(x0)) / h)))))
        cen.append((X(k), Y(math.log10(rel((f(x0 + h) - f(x0 - h)) / (2 * h))))))
        cst.append((X(k), Y(math.log10(rel(fz(complex(x0, h)).imag / h)))))
        k += 0.2

    parts = [rect(PX, PY, PW, PH, fill="#ffffff", stroke=MUTED, sw=1.2, rx=4)]
    for kk in range(-18, 0, 2):
        parts.append(polyline([(X(kk), PY), (X(kk), PY + PH)], color="#e3e6ea", sw=1.0))
        parts.append(text(X(kk), PY + PH + 22, "10" + _sup(kk), size=13, color=MUTED))
    for ll in range(-16, 1, 2):
        parts.append(polyline([(PX, Y(ll)), (PX + PW, Y(ll))], color="#e3e6ea", sw=1.0))
        lab = "1" if ll == 0 else "10" + _sup(ll)
        parts.append(text(PX - 14, Y(ll) + 5, lab, size=13, color=MUTED, anchor="end"))

    for kk, lab, anc in ((math.log10(math.sqrt(2.220446049250313e-16)), "h = √ε", "end"),
                         (math.log10(2.220446049250313e-16 ** (1.0 / 3.0)), "h = ∛ε", "start")):
        parts.append(polyline([(X(kk), PY), (X(kk), PY + PH)], color=MUTED, sw=1.2, dash="5,4"))
        dx = -8 if anc == "end" else 8
        parts.append(text(X(kk) + dx, Y(-0.45), lab, size=13, color=MUTED, anchor=anc))

    parts.append(polyline(cst, color=FIELD, sw=2.4))
    parts.append(polyline(cen, color=NEG, sw=2.2))
    parts.append(polyline(fwd, color=POS, sw=2.2))

    parts.append(text(X(-2.9), Y(-1.1), "однобічна  ~ h",
                      size=14, color=POS, bold=True))
    parts.append(text(X(-3.0), Y(-4.9), "центральна  ~ h²",
                      size=14, color=NEG, bold=True))
    parts.append(text(X(-13.4), Y(-13.0), "complex-step: віднімання немає",
                      size=14, color=FIELD, bold=True))
    parts.append(polyline([(X(-13.4), Y(-13.7)), (X(-13.4), Y(-15.3))], color=FIELD, sw=1.2))

    parts.append(text(PX, PY - 26, "відносна похибка похідної",
                      size=14, color=MUTED, anchor="start"))
    parts.append(text(PX + PW / 2, PY + PH + 56, "крок  h", size=15, bold=True))
    render("img/fd-step-error.svg", W, H, *parts,
           title="Чому найменший крок — не найкращий")


# ── Фігура 7: чому біля det J → 0 крок Ньютона вилітає ───────────────────────
# Ньютон перетинає дві прямі — лінеаризації рівнянь. Що ближче до det J = 0,
# то паралельніші ці прямі й то далі відлітає їхній перетин.
def fig_newton_degenerate():
    W, H = 980, 578
    xa, xb, ya, yb = 0.20, 3.00, 0.20, 3.00

    def panel(px, py, s, p, caps):
        def P(x, y):
            return (px + (x - xa) / (xb - xa) * s, py + s - (y - ya) / (yb - ya) * s)

        out = [rect(px, py, s, s, fill="#ffffff", stroke=MUTED, sw=1.2, rx=4)]

        def curve(pts, color, sw, dash=None):
            run = []
            for (x, y) in pts:
                if xa <= x <= xb and ya <= y <= yb:
                    run.append(P(x, y))
                elif len(run) > 1:
                    out.append(polyline(run, color=color, sw=sw, dash=dash)); run = []
                else:
                    run = []
            if len(run) > 1:
                out.append(polyline(run, color=color, sw=sw, dash=dash))

        curve([(2 * math.cos(t), 2 * math.sin(t)) for t in lin(0.0, math.pi / 2, 160)],
              "#aab0b8", 2.0)
        curve([(t, 1.0 / t) for t in lin(0.30, 3.0, 160)], "#aab0b8", 2.0)
        curve([(t, t) for t in lin(xa, xb, 40)], "#cfd4da", 1.6, dash="6,5")

        x0, y0 = p
        # лінеаризації: 2x₀·x + 2y₀·y = x₀²+y₀²+4   і   y₀·x + x₀·y = x₀·y₀+1
        for (a, b, c, col) in ((2 * x0, 2 * y0, x0 * x0 + y0 * y0 + 4.0, POS),
                               (y0, x0, x0 * y0 + 1.0, NEG)):
            curve([(t, (c - a * t) / b) for t in lin(xa, xb, 200)], col, 2.4)

        for (rx, ry) in ((2 * math.cos(math.pi / 12), 2 * math.sin(math.pi / 12)),
                         (2 * math.sin(math.pi / 12), 2 * math.cos(math.pi / 12))):
            q = P(rx, ry)
            out.append(circle(q[0], q[1], 5.5, fill="#ffffff", stroke=FIELD, sw=2.4))

        det = 2 * (x0 * x0 - y0 * y0)
        nx = ((x0 * x0 + y0 * y0 + 4.0) * x0 - 2 * y0 * (x0 * y0 + 1.0)) / det
        ny = (2 * x0 * (x0 * y0 + 1.0) - y0 * (x0 * x0 + y0 * y0 + 4.0)) / det
        if xa <= nx <= xb and ya <= ny <= yb:
            q = P(nx, ny)
            out.append(circle(q[0], q[1], 6.0, fill=INK, stroke=INK, sw=1.0))
        else:
            a0 = P(x0, y0)
            d = math.hypot(nx - x0, ny - y0)
            ux, uy = (nx - x0) / d, (ny - y0) / d
            a1 = (a0[0] + ux * s / (xb - xa) * 1.55, a0[1] - uy * s / (yb - ya) * 1.55)
            out.append(arrow(a0[0], a0[1], a1[0], a1[1], color=INK, sw=2.6))

        q = P(x0, y0)
        out.append(circle(q[0], q[1], 6.0, fill=POS, stroke="#ffffff", sw=2.0))
        out.append(mtext(px + s / 2, py - 62, caps, size=14, lh=1.35))
        return out

    parts = []
    parts += panel(72, 130, 380, (2.2, 0.8),
                   ["p = (2.2, 0.8),   det J = 8.4",
                    "прямі перетинаються під великим кутом",
                    "наступне наближення — поруч із коренем"])
    parts += panel(530, 130, 380, (1.42, 1.41),
                   ["p = (1.42, 1.41),   det J = 0.057",
                    "прямі майже паралельні",
                    "наступне наближення — за 70 одиниць"])

    ly = 548
    items = ((POS, "лінеаризація  x² + y² = 4", 92),
             (NEG, "лінеаризація  x·y = 1", 350),
             ("#cfd4da", "y = x:  тут det J = 0", 596),
             (FIELD, "корені системи", 790))
    for (col, lab, lx) in items:
        parts.append(polyline([(lx, ly), (lx + 26, ly)], color=col, sw=2.6))
        parts.append(text(lx + 34, ly + 5, lab, size=13, color=INK, anchor="start"))
    parts.append(circle(78, ly, 5.5, fill=POS, stroke="#ffffff", sw=1.5))
    parts.append(circle(898, ly, 5.5, fill=INK, stroke=INK, sw=1.0))
    parts.append(text(898, ly - 18, "наступна", size=12, color=MUTED))
    parts.append(text(78, ly - 18, "p", size=12, color=MUTED))
    render("img/newton-degenerate.svg", W, H, *parts,
           title="Крок Ньютона — це перетин двох прямих")


fig_linearize()
fig_anatomy()
fig_polar()
fig_singular()
fig_sphere_cell()
fig_fd_error()
fig_newton_degenerate()
print("ok")
