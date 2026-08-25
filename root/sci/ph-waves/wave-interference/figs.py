# -*- coding: utf-8 -*-
"""Фігури до теми «Інтерференція хвиль».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

W1 = "#c0392b"    # хвиля 1 / максимум — гаряче червоне
W2 = "#2457d6"    # хвиля 2 / мінімум — холодне синє
SUM = "#1a1a1a"   # сума — чорне, товсте
GREEN = "#27ae60" # різниця ходу / «гучно»
GRID = "#e6e9ee"


def poly(pts, color=INK, sw=2.0, dash=None, fill="none"):
    d = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts)
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>' % (d, fill, color, sw, da)


def cell(x, y, w, h, fill):
    return '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" shape-rendering="crispEdges"/>' % (x, y, w, h, fill)


def blend(v, c0=(255, 255, 255), c1=(36, 87, 214)):
    """v∈[0,1]: білий (тихо) → синій (гучно). Повертає hex."""
    v = max(0.0, min(1.0, v))
    r = int(c0[0] + (c1[0] - c0[0]) * v)
    g = int(c0[1] + (c1[1] - c0[1]) * v)
    b = int(c0[2] + (c1[2] - c0[2]) * v)
    return "#%02x%02x%02x" % (r, g, b)


def sine_pts(x0, x1, yb, amp, cycles, phase=0.0, n=240):
    pts = []
    for i in range(n + 1):
        u = i / n
        x = x0 + u * (x1 - x0)
        y = yb - amp * math.sin(2 * math.pi * cycles * u + phase)
        pts.append((x, y))
    return pts


# ── Фігура 1: різниця ходу задає фазу — підсилення чи гасіння ─────────────────
def fig_path_difference():
    W, H = 1040, 520
    f = [text(W / 2, 30, "Різниця ходу задає різницю фаз — а та вирішує: гучно чи тихо", size=16, bold=True)]

    # ── ліва частина: геометрія двох дорiг у точку P ──
    S1 = (120, 200)
    S2 = (120, 360)
    P = (470, 150)
    r1 = math.hypot(P[0] - S1[0], P[1] - S1[1])
    r2 = math.hypot(P[0] - S2[0], P[1] - S2[1])
    # точка Q на промені S2→P на відстані r1 від P (звідси відрізок Q..S2 = Δr)
    ux, uy = (P[0] - S2[0]) / r2, (P[1] - S2[1]) / r2
    Q = (P[0] - ux * r1, P[1] - uy * r1)

    f.append(line(S1[0], S1[1], P[0], P[1], color=W1, sw=2.6))
    f.append(line(S2[0], S2[1], P[0], P[1], color=W2, sw=2.6))
    # відрізок Δr — зелений товстий
    f.append(line(Q[0], Q[1], S2[0], S2[1], color=GREEN, sw=5.0))
    # дуга «однакова відстань r1» від S1-променя до Q (пунктир)
    arc = []
    a0 = math.atan2(S1[1] - P[1], S1[0] - P[0])
    a1 = math.atan2(Q[1] - P[1], Q[0] - P[0])
    for i in range(41):
        a = a0 + (a1 - a0) * i / 40
        arc.append((P[0] + r1 * math.cos(a), P[1] + r1 * math.sin(a)))
    f.append(poly(arc, color=MUTED, sw=1.4, dash="4,5"))

    f.append(circle(S1[0], S1[1], 6, fill=W1, stroke=W1, sw=1))
    f.append(circle(S2[0], S2[1], 6, fill=W2, stroke=W2, sw=1))
    f.append(circle(P[0], P[1], 5, fill=SUM, stroke=SUM, sw=1))
    f.append(text(S1[0] - 14, S1[1] + 5, "джерело 1", size=12.5, color=W1, anchor="end"))
    f.append(text(S2[0] - 14, S2[1] + 5, "джерело 2", size=12.5, color=W2, anchor="end"))
    f.append(text(P[0] + 14, P[1] - 4, "точка P", size=12.5, bold=True, anchor="start"))
    f.append(text((S1[0] + P[0]) / 2 - 6, (S1[1] + P[1]) / 2 - 12, "r₁", size=13, color=W1, bold=True))
    f.append(text((S2[0] + P[0]) / 2 + 8, (S2[1] + P[1]) / 2 + 20, "r₂", size=13, color=W2, bold=True))
    # підпис Δr — збоку від зеленого відрізка, з коротким виноском
    mid = ((Q[0] + S2[0]) / 2, (Q[1] + S2[1]) / 2)
    f.append(text(mid[0] - 92, mid[1] + 34, "Δr — зайва дорога", size=12.5, bold=True, color=GREEN, anchor="start"))
    f.append(line(mid[0] - 20, mid[1] + 26, mid[0] - 2, mid[1] + 4, color=GREEN, sw=1.3))

    # формула під геометрією
    box, bw, bh = textbox(285, 460, "Δφ = 2π · Δr / λ", size=15, pad=11, fill="#eef7f0", stroke=GREEN, sw=1.5)
    f.append(box)

    # ── права частина: два наслiдки ──
    xL, xR = 610, 1010
    # роздільник
    f.append(line(560, 70, 560, 500, color=GRID, sw=1.6))

    def wave_case(yb, ph2, title_s, tcol, verdict, vcol):
        fr = [text(xL, yb - 66, title_s, size=13.5, bold=True, color=tcol, anchor="start")]
        fr.append(line(xL, yb, xR, yb, color=GRID, sw=1.2))
        fr.append(poly(sine_pts(xL, xR, yb, 18, 3.0, 0.0), color=W1, sw=2.2))
        fr.append(poly(sine_pts(xL, xR, yb, 18, 3.0, ph2), color=W2, sw=2.2))
        # сума
        summ = []
        for i in range(241):
            u = i / 240.0
            x = xL + u * (xR - xL)
            y = yb - 18 * (math.sin(2 * math.pi * 3.0 * u) + math.sin(2 * math.pi * 3.0 * u + ph2))
            summ.append((x, y))
        fr.append(poly(summ, color=SUM, sw=3.2))
        fr.append(text((xL + xR) / 2, yb + 62, verdict, size=13, bold=True, color=vcol))
        return fr

    f += wave_case(170, 0.0, "Δr = m·λ  (ціле число хвиль) → у фазі", W1,
                   "сума подвоюється → гучно (максимум)", GREEN)
    f += wave_case(360, math.pi, "Δr = (m + ½)·λ → протифаза", W2,
                   "сума гасне в нуль → тихо (мінімум)", W2)
    render(os.path.join(IMG, "path-difference.svg"), W, H, *f)


# ── Фігура 2: карта гучності двох джерел — нерухомий візерунок ────────────────
def fig_two_source_pattern():
    W, H = 980, 700
    f = [text(W / 2, 30, "Два синфазні джерела: нерухома карта гучних і тихих смуг", size=16, bold=True)]

    S1 = (150, 280)
    S2 = (150, 430)
    LAM = 52.0                 # довжина хвилі в пікселях
    x0, y0, x1, y1 = 150, 70, 905, 640
    cs = 15                    # розмір комірки

    y = y0
    while y < y1:
        x = x0
        while x < x1:
            cx, cy = x + cs / 2, y + cs / 2
            r1 = math.hypot(cx - S1[0], cy - S1[1])
            r2 = math.hypot(cx - S2[0], cy - S2[1])
            v = math.cos(math.pi * (r1 - r2) / LAM) ** 2
            f.append(cell(x, y, cs, cs, blend(v)))
            x += cs
        y += cs

    # джерела поверх карти
    for S, col, lab in [(S1, W1, "S₁"), (S2, W2, "S₂")]:
        f.append(circle(S[0], S[1], 7, fill="#ffffff", stroke=SUM, sw=2.2))
        f.append(circle(S[0], S[1], 3, fill=SUM, stroke=SUM, sw=1))
        f.append(text(S[0] - 16, S[1] + 5, lab, size=14, bold=True, color=col, anchor="end"))
    f.append(text(120, 250, "два", size=12, color=MUTED, anchor="end"))
    f.append(text(120, 266, "синфазні", size=12, color=MUTED, anchor="end"))
    f.append(text(120, 282, "джерела", size=12, color=MUTED, anchor="end"))

    # підпис максимуму (згори, у поле над картою) з виноском на темну смугу
    f.append(text(700, 56, "лінія максимумів — гучно", size=12.5, bold=True, color=W1))
    f.append(line(700, 62, 700, 72, color=W1, sw=1.6))
    # центральна максимальна смуга — горизонталь-бісектриса (y ≈ 355): позначимо збоку
    ymid = (S1[1] + S2[1]) / 2
    f.append(text(918, ymid + 4, "Δr = 0", size=11.5, color=MUTED, anchor="start"))
    f.append(line(905, ymid, 916, ymid, color=MUTED, sw=1.2))

    # підпис мінімуму (знизу, у поле під картою) з виноском на світлий проміжок
    f.append(text(560, 682, "лінія мінімумів — тихо (різниця ходу зсунута на пів-хвилі)",
                  size=12.5, bold=True, color=W2))
    f.append(line(430, 668, 430, 646, color=W2, sw=1.6))

    # легенда шкали гучності (справа згори, у полі)
    lx, ly, lw = 720, 44, 150
    for i in range(lw):
        f.append(cell(lx + i, ly, 1.2, 14, blend(i / (lw - 1))))
    f.append(text(lx, ly - 6, "тихо", size=11, color=MUTED, anchor="start"))
    f.append(text(lx + lw, ly - 6, "гучно", size=11, color=MUTED, anchor="end"))
    render(os.path.join(IMG, "two-source-pattern.svg"), W, H, *f)


# ── Фігура 3: когерентні дають смуги, незалежні — сіре середнє ────────────────
def fig_coherence():
    W, H = 1000, 470
    f = [text(W / 2, 30, "Смуги видно лише від злагоджених (когерентних) джерел", size=16, bold=True)]
    x0, x1 = 90, 910
    span = x1 - x0
    K = 9.0                    # число смуг у вікні

    # ── верх: когерентні — чіткі смуги ──
    yt, ht = 90, 46
    n = 320
    for i in range(n):
        u = i / n
        v = math.cos(math.pi * K * u) ** 2
        f.append(cell(x0 + u * span, yt, span / n + 0.6, ht, blend(v)))
    f.append(text(x0, yt - 12, "КОГЕРЕНТНІ  (різниця фаз стала)", size=13, bold=True, color=SUM, anchor="start"))
    f.append(text(x0, yt + ht + 22, "смуги стоять на місці — гучне й тихе чітко видно",
                  size=12.5, color=INK, anchor="start"))

    # ── низ: незалежні — кілька зсунутих картин + рівне середнє ──
    yb, hb = 250, 46
    f.append(text(x0, yb - 12, "НЕЗАЛЕЖНІ  (різниця фаз хаотично пливе)", size=13, bold=True, color=SUM, anchor="start"))
    # три «примарні» миттєвi картини з різними зсувами (бліді)
    ghosts = [(0.0, "#cfd6e6"), (0.9, "#dbe0ec"), (1.9, "#e6e9f2")]
    for j, (ph, gcol) in enumerate(ghosts):
        yy = yb + j * 6
        prev = None
        for i in range(n + 1):
            u = i / n
            v = math.cos(math.pi * K * u + ph) ** 2
            x = x0 + u * span
            y = yy + hb * 0.5 - v * hb * 0.5
            if prev:
                f.append(line(prev[0], prev[1], x, y, color=gcol, sw=1.4))
            prev = (x, y)
    f.append(text(x0 + span + 8, yb + hb / 2, "миттєві", size=11, color=MUTED, anchor="start"))
    f.append(text(x0 + span + 8, yb + hb / 2 + 15, "картини", size=11, color=MUTED, anchor="start"))

    # стрілка «усереднюється» до сірої смуги
    ya, ha = 360, 40
    f.append(text(x0, ya - 12, "око усереднює за часом →", size=12.5, bold=True, color=INK, anchor="start"))
    for i in range(n):
        u = i / n
        f.append(cell(x0 + u * span, ya, span / n + 0.6, ha, blend(0.5)))
    f.append(text(W / 2, ya + ha + 22, "рівна сіра гучність — жодних смуг", size=12.5, color=INK))
    render(os.path.join(IMG, "coherence.svg"), W, H, *f)


# ══ Фігури до вставки math-fringe-spacing.md ═════════════════════════════════

PURPLE = "#8e44ad"


def arc_pts(cx, cy, r, a0, a1, n=36):
    """Точки дуги (кути в радіанах, система SVG: y вниз)."""
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / n),
             cy + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def right_angle(px, py, u, v, s=13, color=INK, sw=1.4):
    """Значок прямого кута в (px,py) між одиничними напрямками u і v."""
    a = (px + u[0] * s, py + u[1] * s)
    b = (px + (u[0] + v[0]) * s, py + (u[1] + v[1]) * s)
    c = (px + v[0] * s, py + v[1] * s)
    return (line(a[0], a[1], b[0], b[1], color=color, sw=sw) +
            line(b[0], b[1], c[0], c[1], color=color, sw=sw))


# ── Фігура 4: три панелі — геометрія, d·sin θ, малий кут ──────────────────────
def fig_fringe_geometry():
    W, H = 1180, 730
    f = [text(W / 2, 28, "Дві сходинки наближення: від точних коренів до λ·L/d", size=16.5, bold=True)]

    # ── панель 1: уся геометрія ──
    f.append(rect(50, 46, 1080, 300, fill="#fbfcfe", stroke="#dfe4ea", sw=1.2, rx=10))
    f.append(text(66, 70, "1 · Уся геометрія: база d, екран за L, точка P на висоті x",
                  size=13.5, bold=True, anchor="start"))

    Ox, Oy, dpx, SCR = 170, 230, 60, 1010
    Sp, Sm = (Ox, Oy - dpx / 2), (Ox, Oy + dpx / 2)
    P = (SCR, 130)

    f.append(line(SCR, 90, SCR, 330, color=INK, sw=3.4))
    f.append(text(SCR - 12, 324, "екран", size=12, color=MUTED, anchor="end"))
    f.append(line(Ox, Oy, SCR, Oy, color=MUTED, sw=1.3, dash="6,5"))
    f.append(line(Sp[0], Sp[1], P[0], P[1], color=W1, sw=2.4))
    f.append(line(Sm[0], Sm[1], P[0], P[1], color=W2, sw=2.4))
    f.append(circle(Sp[0], Sp[1], 5.5, fill=W1, stroke=W1, sw=1))
    f.append(circle(Sm[0], Sm[1], 5.5, fill=W2, stroke=W2, sw=1))
    f.append(text(Ox, Sp[1] - 12, "S₊", size=13, bold=True, color=W1))
    f.append(text(Ox, Sm[1] + 20, "S₋", size=13, bold=True, color=W2))
    # база d
    f.append(line(Ox - 26, Sp[1], Ox - 26, Sm[1], color=INK, sw=1.4))
    f.append(line(Ox - 31, Sp[1], Ox - 21, Sp[1], color=INK, sw=1.4))
    f.append(line(Ox - 31, Sm[1], Ox - 21, Sm[1], color=INK, sw=1.4))
    f.append(text(Ox - 36, Oy + 5, "d", size=13.5, bold=True, anchor="end"))
    # L
    f.append(line(Ox, 320, Ox, 332, color=MUTED, sw=1.2))
    f.append(line(SCR, 320, SCR, 332, color=MUTED, sw=1.2))
    f.append(line(Ox, 326, 566, 326, color=MUTED, sw=1.3))
    f.append(line(614, 326, SCR, 326, color=MUTED, sw=1.3))
    f.append(text(590, 331, "L", size=13.5, bold=True, color=MUTED))
    # x
    f.append(line(SCR + 16, Oy, SCR + 16, P[1], color=MUTED, sw=1.3))
    f.append(line(SCR + 11, Oy, SCR + 21, Oy, color=MUTED, sw=1.2))
    f.append(line(SCR + 11, P[1], SCR + 21, P[1], color=MUTED, sw=1.2))
    f.append(text(SCR + 30, (Oy + P[1]) / 2 + 5, "x", size=13.5, bold=True, color=MUTED, anchor="start"))
    # кут θ і точка P
    aP = math.atan2(P[1] - Oy, P[0] - Ox)
    f.append(poly(arc_pts(Ox, Oy, 74, 0.0, aP), color=INK, sw=1.4))
    f.append(text(Ox + 88, Oy - 5, "θ", size=13.5, bold=True))
    f.append(circle(P[0], P[1], 5, fill=INK, stroke=INK, sw=1))
    f.append(text(P[0] - 12, P[1] - 10, "P", size=13.5, bold=True, anchor="end"))
    # підказка про збільшення
    f.append(poly(arc_pts(Ox + 6, Oy, 64, 0, 2 * math.pi), color=GREEN, sw=1.6, dash="6,5"))
    f.append(text(330, 292, "збільшено на панелі 2", size=11.5, color=GREEN, anchor="start"))

    # ── панель 2: звідки d·sin θ ──
    f.append(rect(50, 370, 555, 340, fill="#fbfcfe", stroke="#dfe4ea", sw=1.2, rx=10))
    f.append(text(66, 394, "2 · Збільшено: чому Δr = d·sin θ", size=13.5, bold=True, anchor="start"))

    A = (150, 500)          # S₊
    B = (150, 660)          # S₋
    th = math.radians(20)
    u = (math.cos(th), -math.sin(th))
    f.append(line(A[0], A[1], B[0], B[1], color=INK, sw=2.6))
    f.append(line(A[0], A[1], A[0] + u[0] * 330, A[1] + u[1] * 330, color=W1, sw=2.4))
    f.append(line(B[0], B[1], B[0] + u[0] * 400, B[1] + u[1] * 400, color=W2, sw=2.4))
    t = (A[0] - B[0]) * u[0] + (A[1] - B[1]) * u[1]
    N = (B[0] + u[0] * t, B[1] + u[1] * t)
    f.append(line(A[0], A[1], N[0], N[1], color=MUTED, sw=1.5, dash="5,4"))
    f.append(line(N[0], N[1], B[0], B[1], color=GREEN, sw=5.0))
    w = ((A[0] - N[0]) / t, (A[1] - N[1]) / t)
    f.append(right_angle(N[0], N[1], u, w, s=13, color=MUTED))
    f.append(circle(A[0], A[1], 5.5, fill=W1, stroke=W1, sw=1))
    f.append(circle(B[0], B[1], 5.5, fill=W2, stroke=W2, sw=1))
    f.append(text(A[0], A[1] - 13, "S₊", size=13, bold=True, color=W1))
    f.append(text(B[0], B[1] + 22, "S₋", size=13, bold=True, color=W2))
    f.append(text(135, 584, "d", size=13.5, bold=True, anchor="end"))
    f.append(poly(arc_pts(A[0], A[1], 66, math.pi / 2, math.pi / 2 - th), color=INK, sw=1.4))
    f.append(text(163, 578, "θ", size=13))
    f.append(text(300, 694, "Δr = d·sin θ", size=13.5, bold=True, color=GREEN, anchor="start"))
    f.append(line(296, 688, 188, 658, color=GREEN, sw=1.3))
    f.append(text(330, 470, "промені майже паралельні", size=11.5, color=MUTED, anchor="start"))
    f.append(text(470, 383, "до P", size=11.5, color=MUTED, anchor="start"))
    f.append(text(536, 517, "до P", size=11.5, color=MUTED, anchor="start"))

    # ── панель 3: малий кут ──
    f.append(rect(625, 370, 505, 340, fill="#fbfcfe", stroke="#dfe4ea", sw=1.2, rx=10))
    f.append(text(641, 394, "3 · Малий кут: sin θ ≈ tan θ = x / L", size=13.5, bold=True, anchor="start"))
    O3, F3, P3 = (700, 640), (1040, 640), (1040, 470)
    f.append(line(O3[0], O3[1], F3[0], F3[1], color=MUTED, sw=2.0))
    f.append(line(F3[0], F3[1], P3[0], P3[1], color=INK, sw=2.6))
    f.append(line(O3[0], O3[1], P3[0], P3[1], color=W1, sw=2.4))
    f.append(right_angle(F3[0], F3[1], (-1, 0), (0, -1), s=13, color=MUTED))
    f.append(circle(O3[0], O3[1], 5, fill=INK, stroke=INK, sw=1))
    f.append(circle(P3[0], P3[1], 5, fill=INK, stroke=INK, sw=1))
    f.append(text(870, 666, "L", size=13.5, bold=True, color=MUTED))
    f.append(text(1056, 560, "x", size=13.5, bold=True, anchor="start"))
    f.append(text(866, 544, "R", size=13.5, bold=True, color=W1))
    aP3 = math.atan2(P3[1] - O3[1], P3[0] - O3[0])
    f.append(poly(arc_pts(O3[0], O3[1], 52, 0.0, aP3), color=INK, sw=1.4))
    f.append(text(764, 624, "θ", size=13.5, bold=True))
    box, _, _ = textbox(880, 432, "sin θ = x / R        tan θ = x / L\n"
                                  "x ≪ L  →  R ≈ L  →  sin θ ≈ tan θ",
                        size=13, pad=10, fill="#eef7f0", stroke=GREEN, sw=1.4)
    f.append(box)
    render(os.path.join(IMG, "fringe-geometry.svg"), W, H, *f)


# ── Фігура 5: точні смуги — гіперболи; драбина λL/d проти них ─────────────────
def fig_fringe_hyperbolas():
    W, H = 1180, 700
    f = [text(W / 2, 28, "Точні лінії максимумів — гіперболи; асимптоти дають sin θ = mλ/d",
              size=16.5, bold=True)]

    Ox, Oy, dpx, SCR, XM = 150, 590, 140, 900, 750
    LAM = 0.18 * dpx                      # λ/d = 0.18
    c = dpx / 2
    HC = [INK, W2, PURPLE, W1]

    f.append(text(SCR, 52, "точні максимуми", size=12.5, bold=True))
    f.append(text(SCR, 70, "на екрані", size=12.5, bold=True))
    f.append(text(1070, 52, "драбина", size=12.5, bold=True, color=MUTED))
    f.append(text(1070, 70, "m·λL/d", size=12.5, bold=True, color=MUTED))

    f.append(line(SCR, 88, SCR, 650, color=INK, sw=3.4))
    f.append(line(Ox, Oy, SCR, Oy, color=HC[0], sw=2.4))
    f.append(text(580, 582, "m = 0", size=12.5, bold=True, color=HC[0]))

    exact = [0.0]
    for m in (1, 2, 3):
        a = m * LAM / 2
        b = math.sqrt(c * c - a * a)
        pts = [(Ox + X, Oy - a * math.sqrt(1 + (X / b) ** 2)) for X in range(0, XM + 1, 5)]
        f.append(poly(pts, color=HC[m], sw=2.6))
        f.append(line(Ox, Oy, Ox + XM, Oy - a / b * XM, color=MUTED, sw=1.2, dash="7,6"))
        yl = a * math.sqrt(1 + (430.0 / b) ** 2)
        f.append(text(580, Oy - yl - 8, "m = %d" % m, size=12.5, bold=True, color=HC[m]))
        f.append(circle(Ox, Oy - a, 2.8, fill=INK, stroke=INK, sw=1))
        exact.append(a * math.sqrt(1 + (float(XM) / b) ** 2))

    step = LAM * XM / dpx                 # λL/d у пікселях
    for m in range(4):
        ye = Oy - exact[m]
        yl = Oy - step * m
        f.append(circle(SCR, ye, 5.5, fill=HC[m], stroke=HC[m], sw=1))
        f.append(line(1058, yl, 1082, yl, color=MUTED, sw=2.4))
        f.append(line(SCR + 8, ye, 1054, yl, color=MUTED, sw=1.0, dash="3,4"))
    f.append(line(1070, Oy - step * 3 - 14, 1070, Oy + 14, color=MUTED, sw=1.2))

    # джерела й база
    f.append(circle(Ox, Oy - dpx / 2, 6, fill=W1, stroke=W1, sw=1))
    f.append(circle(Ox, Oy + dpx / 2, 6, fill=W2, stroke=W2, sw=1))
    f.append(text(Ox, Oy - dpx / 2 - 14, "S₊", size=13, bold=True, color=W1))
    f.append(text(Ox, Oy + dpx / 2 + 22, "S₋", size=13, bold=True, color=W2))
    f.append(line(Ox - 26, Oy - dpx / 2, Ox - 26, Oy + dpx / 2, color=INK, sw=1.4))
    f.append(line(Ox - 31, Oy - dpx / 2, Ox - 21, Oy - dpx / 2, color=INK, sw=1.4))
    f.append(line(Ox - 31, Oy + dpx / 2, Ox - 21, Oy + dpx / 2, color=INK, sw=1.4))
    f.append(text(Ox - 36, Oy + 5, "d", size=13.5, bold=True, anchor="end"))
    f.append(text(300, 648, "вершини гілок: y = mλ/2", size=12, color=MUTED, anchor="start"))
    f.append(line(296, 642, 164, 574, color=MUTED, sw=1.1))

    box, _, _ = textbox(700, 635, "Δr = m·λ  —  гілка гіперболи з фокусами S₊, S₋\n"
                                  "a = mλ/2      c = d/2      b² = (d² − m²λ²)/4\n"
                                  "асимптота (пунктир):  sin θ = mλ/d",
                        size=13, pad=10, fill="#f2f6fc", stroke=W2, sw=1.4)
    f.append(box)
    f.append(mtext(1070, 646, ["крок росте:", "1.02 · 1.13 · 1.42 × λL/d"], size=11.5, color=MUTED))
    render(os.path.join(IMG, "fringe-hyperbolas.svg"), W, H, *f)


# ── Фігура 6: ціна підміни sin θ → tan θ ─────────────────────────────────────
def fig_fringe_error():
    W, H = 1020, 560
    f = [text(W / 2, 28, "Ціна другої поступки: наскільки драбина m·λL/d занижує смугу",
              size=16.5, bold=True)]
    x0, x1, y0, y1 = 150, 900, 100, 460
    UM, EM = 0.5, 14.0

    def px(u): return x0 + u / UM * (x1 - x0)
    def py(e): return y1 - e / EM * (y1 - y0)

    for k in range(6):
        u = 0.1 * k
        if u > UM + 1e-9: break
        f.append(line(px(u), y0, px(u), y1, color=GRID, sw=1.0))
        f.append(text(px(u), y1 + 22, ("%.1f" % u), size=12, color=MUTED))
    for e in range(0, 15, 2):
        f.append(line(x0, py(e), x1, py(e), color=GRID, sw=1.0))
        f.append(text(x0 - 12, py(e) + 4, "%d" % e, size=12, color=MUTED, anchor="end"))
    f.append(line(x0, y0, x0, y1, color=INK, sw=1.8))
    f.append(line(x0, y1, x1, y1, color=INK, sw=1.8))

    ex = [(px(i / 200.0 * UM), py(100 * (1 - math.sqrt(1 - (i / 200.0 * UM) ** 2)))) for i in range(201)]
    ap = [(px(i / 200.0 * UM), py(100 * (i / 200.0 * UM) ** 2 / 2)) for i in range(201)]
    f.append(poly(ap, color=MUTED, sw=2.0, dash="7,5"))
    f.append(poly(ex, color=W1, sw=2.8))

    u1 = math.sqrt(1 - 0.99 ** 2)
    f.append(line(x0, py(1), px(u1), py(1), color=W2, sw=1.4, dash="5,4"))
    f.append(line(px(u1), py(1), px(u1), y1, color=W2, sw=1.4, dash="5,4"))

    f.append(text(525, 508, "sin θ = m·λ / d", size=13.5, bold=True))
    f.append(mtext(74, 250, ["похибка", "драбини", "m·λL/d, %"], size=12, color=MUTED))

    f.append(line(174, 118, 200, 118, color=W1, sw=2.8))
    f.append(text(208, 123, "точно: 1 − √(1 − sin²θ)", size=12, anchor="start"))
    f.append(line(174, 142, 200, 142, color=MUTED, sw=2.0, dash="7,5"))
    f.append(text(208, 147, "наближено: sin²θ / 2", size=12, color=MUTED, anchor="start"))

    f.append(text(200, 226, "оптика Юнга: sin θ ≈ 0.0025 — отут, біля нуля",
                  size=12.5, color=W2, anchor="start"))
    f.append(line(196, 232, 156, 452, color=W2, sw=1.1))
    f.append(text(520, 396, "до sin θ ≈ 0.14 похибка драбини менша за 1 %",
                  size=12.5, color=W2, anchor="start"))
    f.append(line(516, 390, 368, 432, color=W2, sw=1.1))
    f.append(text(640, 168, "у кімнаті: sin θ = 0.5 → 13 %", size=12.5, color=W1, anchor="start"))
    f.append(line(856, 162, 894, 120, color=W1, sw=1.1))
    f.append(circle(px(0.5), py(13.397), 5, fill=W1, stroke=W1, sw=1))
    render(os.path.join(IMG, "fringe-error.svg"), W, H, *f)


# ══ Фігури до вставки hist-young-interference.md ══════════════════════════════

# ── Дослід Юнга 1803 року: смужка картону в сонячному промені ────────────────
def fig_young_card():
    W, H = 1140, 700
    f = [text(W / 2, 32, "Дослід Юнга 1803 року: смужка картону в сонячному промені",
              size=17, bold=True)]

    SRC = (168, 224)                 # отвір-джерело у віконниці
    CARD_X = 500                     # смужка картону
    CARD_T = 16                      # її «товщина» на схемі (перебільшена)
    WALL_X = 930

    # конус світла з отвору
    f.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="#fdf6e3"/>'
             % (SRC[0], SRC[1], WALL_X, 118, WALL_X, 330))
    f.append(line(SRC[0], SRC[1], WALL_X, 118, color="#e8c46a", sw=1.4))
    f.append(line(SRC[0], SRC[1], WALL_X, 330, color="#e8c46a", sw=1.4))

    # дзеркальце за вікном + сонячний промінь
    f.append(line(70, 172, 112, 214, color=MUTED, sw=6))
    f.append(arrow(46, 124, 84, 166, color="#d69e00", sw=2.0))
    f.append(text(60, 112, "сонце → дзеркальце за вікном", size=12.5, color=MUTED, anchor="start"))

    # віконниця з голковим отвором
    f.append('<rect x="126" y="112" width="14" height="228" fill="#7a8290"/>')
    f.append(circle(133, SRC[1], 4.5, fill="#ffffff", stroke=INK, sw=1.4))
    f.append(text(133, 366, "віконниця з отвором від голки", size=12.5, anchor="middle"))

    # смужка картону
    f.append('<rect x="%.1f" y="198" width="%.1f" height="52" fill="#1a1a1a"/>'
             % (CARD_X - CARD_T / 2, CARD_T))
    f.append(text(CARD_X, 136, "смужка картону", size=13, bold=True, anchor="middle"))
    f.append(text(CARD_X, 156, "≈ 1/30 дюйма (0.85 мм)", size=12.5, color=MUTED, anchor="middle"))
    f.append(line(CARD_X, 164, CARD_X, 194, color=MUTED, sw=1.3))

    # два «обхідні» пучки
    t = (WALL_X - SRC[0]) / (CARD_X - SRC[0])
    yT = SRC[1] + (198.0 - SRC[1]) * t
    yB = SRC[1] + (250.0 - SRC[1]) * t
    ymid = (yT + yB) / 2
    f.append(line(SRC[0], SRC[1], WALL_X, yT, color=W1, sw=2.4))
    f.append(line(SRC[0], SRC[1], WALL_X, yB, color=W2, sw=2.4))
    f.append(line(CARD_X + 8, 198, WALL_X, ymid + 12, color=W1, sw=1.6, dash="5,5"))
    f.append(line(CARD_X + 8, 250, WALL_X, ymid - 12, color=W2, sw=1.6, dash="5,5"))
    f.append(text(700, 166, "світло, що обходить картку зверху", size=12.5, color=W1, anchor="middle"))
    f.append(text(700, 322, "світло, що обходить картку знизу", size=12.5, color=W2, anchor="middle"))

    # стіна й смуга тіні на ній
    f.append('<rect x="%.1f" y="70" width="13" height="308" fill="#7a8290"/>' % WALL_X)
    f.append(text(WALL_X + 26, 62, "стіна", size=13, bold=True, anchor="start"))
    f.append('<rect x="%.1f" y="%.1f" width="9" height="%.1f" fill="#3a3f4a"/>'
             % (WALL_X + 13, yT, yB - yT))
    f.append(text(WALL_X + 30, ymid - 4, "тінь картки —", size=12.5, anchor="start"))
    f.append(text(WALL_X + 30, ymid + 16, "а в ній смуги", size=12.5, color=MUTED, anchor="start"))

    # ── нижня панель: два зрізи яскравості поперек тіні ──
    f.append(line(60, 408, W - 60, 408, color=GRID, sw=1.6))
    f.append(text(W / 2, 440, "Що видно на стіні впоперек тіні", size=15, bold=True))

    BW, BH = 420, 92
    def strip(x0, y0, fringes, head, verdict, vcol):
        out = [text(x0 + BW / 2, y0 - 12, head, size=13, bold=True)]
        n = 210
        for i in range(n):
            u = (i / (n - 1.0)) * 2 - 1          # −1 … +1 упоперек кадру
            if abs(u) > 0.46:
                v = 1.0
            elif fringes:
                v = math.cos(math.pi * 3.2 * u / 0.46) ** 2
            else:
                v = 0.06
            g = int(26 + 216 * v)
            out.append(cell(x0 + i * BW / n, y0, BW / n + 0.7, BH, "#%02x%02x%02x" % (g, g, g)))
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" '
                   'stroke="#9aa2ad" stroke-width="1.4"/>' % (x0, y0, BW, BH))
        out.append(text(x0 + BW / 2, y0 + BH + 28, verdict, size=13, bold=True, color=vcol))
        return out

    f += strip(80, 480, True,
               "світло обходить картку з ОБОХ боків",
               "у тіні смуги, посередині світло", GREEN)
    f += strip(640, 480, False,
               "екранчик перекрив світло з ОДНОГО боку",
               "смуги зникли — рівна тінь", W2)
    f.append(text(W / 2, 652, "Один пучок сам по собі смуг не дає: темні лінії в тіні народжуються "
                              "тільки там, де сходяться обидва.", size=13.5, bold=True))
    render(os.path.join(IMG, "young-card-1803.svg"), W, H, *f)


# ── Пляма Пуассона—Араго: заперечення, що обернулося доказом ─────────────────
def fig_arago_spot():
    W, H = 1140, 580
    f = [text(W / 2, 32, "Пляма, якої не мало бути: заперечення Пуассона (1818) і перевірка Араго (1819)",
              size=16, bold=True)]
    f.append(line(572, 76, 572, 478, color=GRID, sw=1.6))

    # ── ліворуч: чому хвиля мусить дати світло в центрі тіні ──
    f.append(text(286, 100, "Чому хвиля мусить дати світлу цятку", size=14, bold=True))
    S = (96, 268)
    DX, DR, PX = 300, 74, 486
    f.append(circle(S[0], S[1], 6, fill=INK, stroke=INK, sw=1))
    f.append(text(S[0], S[1] + 32, "джерело", size=12.5, color=MUTED))
    f.append(circle(DX, S[1], DR, fill="#3a3f4a", stroke="#3a3f4a", sw=1))
    f.append(text(DX, S[1] + DR + 26, "круглий диск", size=13, bold=True))
    f.append('<rect x="%.1f" y="150" width="11" height="240" fill="#7a8290"/>' % PX)
    f.append(text(PX - 16, 144, "екран", size=13, bold=True, anchor="end"))

    for sgn in (-1, 1):
        E = (DX, S[1] + sgn * DR)
        f.append(line(S[0], S[1], E[0], E[1], color="#e8c46a", sw=1.8))
        f.append(line(E[0], E[1], PX, S[1], color=GREEN, sw=2.4))
    f.append(circle(PX, S[1], 5, fill=GREEN, stroke=GREEN, sw=1))
    f.append(mtext(286, 138, ["усі точки краю диска однаково далекі",
                              "від осьової точки, тож у центр тіні",
                              "хвилі приходять у фазі"],
                   size=12.5, color=GREEN))
    f.append(mtext(286, 428, ["Теорія Френеля рахує це неминуче:",
                              "у самому центрі тіні — підсилення."], size=12.5, bold=True))

    # ── праворуч: що на екрані ──
    f.append(text(856, 100, "Що показує екран", size=14, bold=True))
    for cx, lab, spot, col in [(716, "за теорією частинок", False, W2),
                               (996, "насправді (Араго, 1819)", True, GREEN)]:
        f.append('<rect x="%.1f" y="146" width="196" height="196" fill="#e9edf2" '
                 'stroke="#9aa2ad" stroke-width="1.4"/>' % (cx - 98))
        f.append(circle(cx, 244, 70, fill="#20242b", stroke="#20242b", sw=1))
        if spot:
            for r, op in ((28, 0.10), (20, 0.16), (13, 0.32)):
                f.append('<circle cx="%.1f" cy="244" r="%.1f" fill="#ffffff" opacity="%.2f"/>' % (cx, r, op))
            f.append(circle(cx, 244, 6.5, fill="#ffffff", stroke="#ffffff", sw=1))
        f.append(text(cx, 370, lab, size=13, bold=True, color=col))
    f.append(text(716, 394, "суцільна темрява", size=12.5))
    f.append(text(996, 394, "світла цятка в центрі", size=12.5))

    box, bw, bh = textbox(W / 2, 522,
                          "Пуассон навів цей висновок як безглуздя, що поховає теорію Френеля.\n"
                          "Араго поставив дослід — і цятка була на місці.",
                          size=13.5, pad=13, fill="#eef7f0", stroke=GREEN, sw=1.6)
    f.append(box)
    render(os.path.join(IMG, "arago-spot.svg"), W, H, *f)


if __name__ == "__main__":
    fig_path_difference()
    fig_two_source_pattern()
    fig_coherence()
    fig_fringe_geometry()
    fig_fringe_hyperbolas()
    fig_fringe_error()
    fig_young_card()
    fig_arago_spot()
    print("OK: figs written to", IMG)
