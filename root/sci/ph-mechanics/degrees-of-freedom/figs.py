# -*- coding: utf-8 -*-
"""Фігури до теми «Ступені вільності».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

FREE = FIELD        # вільний напрямок / підрахунок — зелене
TRANS = NEG         # переміщення — холодне синє
ROT = POS           # оберт — гаряче червоне


def dot(cx, cy, r=6, col=INK, fill=BG):
    return circle(cx, cy, r, fill=fill, stroke=col, sw=2)


def head(x, y, dx, dy, col=INK, s=9):
    """Наконечник стрілки у точці (x,y), напрямлений уздовж (dx,dy)."""
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    px, py = -uy, ux
    x1, y1 = x - ux * s + px * s * 0.55, y - uy * s + py * s * 0.55
    x2, y2 = x - ux * s - px * s * 0.55, y - uy * s - py * s * 0.55
    return ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="%s" stroke="none"/>'
            % (x, y, x1, y1, x2, y2, col))


def ellipse(cx, cy, rx, ry, col=MUTED, sw=1.5, dash="5,6", fill="none"):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" '
            'stroke="%s" stroke-width="%.1f"%s/>' % (cx, cy, rx, ry, fill, col, sw, d))


def arc_pts(cx, cy, rx, ry, a0, a1, steps=26):
    """Точки дуги еліпса (кути в градусах; екранний y — вниз)."""
    pts = []
    for i in range(steps + 1):
        t = math.radians(a0 + (a1 - a0) * i / steps)
        pts.append((cx + rx * math.cos(t), cy + ry * math.sin(t)))
    return pts


def arc_arrow(cx, cy, rx, ry, a0, a1, col=ROT, sw=2.4):
    """Дуга-стрілка (оберт): полілінія + наконечник на кінці."""
    pts = arc_pts(cx, cy, rx, ry, a0, a1)
    s = '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (
        " ".join("%.1f,%.1f" % p for p in pts), col, sw)
    ex, ey = pts[-1]
    px, py = pts[-2]
    return s + head(ex, ey, ex - px, ey - py, col=col, s=9)


def iso_box(cx, cy, w=120, h=82, dx=44, dy=-30, fill="#eef2f7"):
    """Ізометричний брусок; повертає (список фрагментів, центр)."""
    fbl = (cx - w / 2, cy + h / 2)
    fbr = (cx + w / 2, cy + h / 2)
    ftr = (cx + w / 2, cy - h / 2)
    ftl = (cx - w / 2, cy - h / 2)
    def sh(p): return (p[0] + dx, p[1] + dy)
    bbr, btr, btl = sh(fbr), sh(ftr), sh(ftl)
    frags = []
    # верхня грань
    frags.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f Z" '
                 'fill="%s" stroke="%s" stroke-width="1.6"/>'
                 % (ftl[0], ftl[1], ftr[0], ftr[1], btr[0], btr[1], btl[0], btl[1],
                    "#e3e9f1", INK))
    # права грань
    frags.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f Z" '
                 'fill="%s" stroke="%s" stroke-width="1.6"/>'
                 % (fbr[0], fbr[1], bbr[0], bbr[1], btr[0], btr[1], ftr[0], ftr[1],
                    "#d7dfea", INK))
    # передня грань
    frags.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f Z" '
                 'fill="%s" stroke="%s" stroke-width="1.8"/>'
                 % (fbl[0], fbl[1], fbr[0], fbr[1], ftr[0], ftr[1], ftl[0], ftl[1],
                    fill, INK))
    return frags, (cx + dx / 2, cy + dy / 2)


# ── Фігура 1: в'язь забирає ступінь (3 → 2 → 1) ────────────────────────────────
def fig_constraints_subtract():
    W, H = 900, 390
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "В'язь забирає ступінь вільності:  3 → 2 → 1",
                  size=16, bold=True))

    # ── панель A: вільна точка (3) ──
    ax, ay = 175, 205
    f.append(text(ax, 92, "вільна в просторі", size=13.5, bold=True))
    for (tx, ty) in [(ax + 78, ay), (ax, ay - 62), (ax - 52, ay + 44)]:
        f.append(line(ax, ay, tx, ty, color=FREE, sw=3))
        f.append(head(tx, ty, tx - ax, ty - ay, col=FREE, s=9))
    f.append(dot(ax, ay, 7, col=INK, fill="#eafaf0"))
    f.append(text(ax, 320, "3 ступені", size=16, bold=True, color=FREE))

    # ── панель B: на поверхні (2) ──
    bx, by = 465, 195
    quad = [(bx - 92, by + 34), (bx + 74, by + 34), (bx + 104, by - 20), (bx - 62, by - 20)]
    f.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f Z" '
             'fill="#f1f3f6" stroke="%s" stroke-width="1.6"/>'
             % (quad[0][0], quad[0][1], quad[1][0], quad[1][1],
                quad[2][0], quad[2][1], quad[3][0], quad[3][1], MUTED))
    f.append(text(bx, 92, "на поверхні", size=13.5, bold=True))
    for (tx, ty) in [(bx + 84, by + 10), (bx + 24, by - 34)]:
        f.append(line(bx, by, tx, ty, color=FREE, sw=3))
        f.append(head(tx, ty, tx - bx, ty - by, col=FREE, s=9))
    f.append(dot(bx, by, 7, col=INK, fill="#eafaf0"))
    f.append(text(bx, 320, "2 ступені", size=16, bold=True, color=FREE))

    # ── панель C: на дроті (1) ──
    cx, cy = 728, 200
    wire = [(cx - 78, cy - 46), (cx - 30, cy + 6), (cx + 26, cy - 4), (cx + 84, cy + 52)]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
             % (" ".join("%.1f,%.1f" % p for p in wire), MUTED))
    f.append(text(cx, 92, "на дроті", size=13.5, bold=True))
    # дотичний напрямок у точці на дроті
    f.append(line(cx - 34, cy + 30, cx + 40, cy - 24, color=FREE, sw=3))
    f.append(head(cx + 40, cy - 24, 74, -54, col=FREE, s=9))
    f.append(head(cx - 34, cy + 30, -74, 54, col=FREE, s=9))
    f.append(dot(cx + 2, cy + 3, 7, col=INK, fill="#eafaf0"))
    f.append(text(cx, 320, "1 ступінь", size=16, bold=True, color=FREE))

    b, bw, bh = textbox(W / 2, 362,
                        ["Кожна в'язь — стільниця чи дротина — прибирає один незалежний напрямок руху."],
                        size=13, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "constraints-subtract.svg"), W, H, *f)


# ── Фігура 2: три точки закріплюють тіло (3 + 2 + 1 = 6) ───────────────────────
def fig_three_points():
    W, H = 880, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Три точки закріплюють тверде тіло",
                  size=16, bold=True))

    A = (210, 300)
    B = (430, 232)
    C = (650, 300)

    # локус B: дуга сфери навколо A (радіус |AB|) — праворуч від A через B
    rAB = math.hypot(B[0] - A[0], B[1] - A[1])
    angB = math.degrees(math.atan2(B[1] - A[1], B[0] - A[0]))
    arcB = arc_pts(A[0], A[1], rAB, rAB, angB - 22, angB + 16)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6" '
             'stroke-dasharray="5,6"/>' % (" ".join("%.1f,%.1f" % p for p in arcB), MUTED))

    # локус C: мале коло перетину (еліпс)
    f.append(ellipse(C[0], C[1], 30, 46, col=MUTED, sw=1.6, dash="5,6"))

    # жорсткі стрижні (трикутник)
    f.append(line(A[0], A[1], B[0], B[1], color=INK, sw=3))
    f.append(line(A[0], A[1], C[0], C[1], color=INK, sw=3))
    f.append(line(B[0], B[1], C[0], C[1], color=INK, sw=3))

    # точки
    f.append(dot(A[0], A[1], 8, col=INK, fill="#eafaf0"))
    f.append(dot(B[0], B[1], 8, col=INK, fill="#eafaf0"))
    f.append(dot(C[0], C[1], 8, col=INK, fill="#eafaf0"))

    # підписи з підрахунком (осторонь від локусів)
    f.append(text(A[0], A[1] + 36, "A — будь-де", size=13, bold=True))
    f.append(text(A[0], A[1] + 56, "3 числа", size=14, bold=True, color=FREE))
    f.append(text(B[0] + 22, B[1] - 20, "B — на сфері", size=13, bold=True, anchor="start"))
    f.append(text(B[0] + 22, B[1] - 1, "2 числа", size=14, bold=True, color=FREE,
                  anchor="start"))
    f.append(text(C[0], C[1] + 64, "C — на колі", size=13, bold=True))
    f.append(text(C[0], C[1] + 84, "1 число", size=14, bold=True, color=FREE))

    # підсумок
    b2, w2, h2 = textbox(760, 152, ["3 + 2 + 1", "= 6"], size=17, pad=12,
                         fill="#eafaf0", stroke=FREE, sw=1.8, color=FREE, bold=True)
    f.append(b2)

    b, bw, bh = textbox(W / 2, 440,
                        ["Закріпили три точки тіла — і решта вже нерухома відносно них: усього шість чисел."],
                        size=13, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "three-points.svg"), W, H, *f)


# ── Фігура 3: шість ступенів твердого тіла (3 переміщення + 3 оберти) ──────────
def fig_rigid_body_six():
    W, H = 880, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Шість ступенів вільності твердого тіла",
                  size=16, bold=True))

    # роздільник
    f.append(line(440, 78, 440, 370, color=MUTED, sw=1.3, dash="3,7"))

    # ── ЛІВОРУЧ: 3 переміщення ──
    box1, c1 = iso_box(215, 232, fill="#eef2f7")
    f += box1
    axes = [((c1[0] + 118, c1[1]), "X"),        # праворуч
            ((c1[0], c1[1] - 118), "Y"),        # угору
            ((c1[0] + 66, c1[1] - 46), "Z")]    # у глибину
    for (tx, ty), lab in axes:
        f.append(line(c1[0], c1[1], tx, ty, color=TRANS, sw=3))
        f.append(head(tx, ty, tx - c1[0], ty - c1[1], col=TRANS, s=10))
    f.append(text(c1[0] + 128, c1[1] + 4, "X", size=13, bold=True, italic=True,
                  color=TRANS, anchor="start"))
    f.append(text(c1[0] - 2, c1[1] - 128, "Y", size=13, bold=True, italic=True,
                  color=TRANS))
    f.append(text(c1[0] + 74, c1[1] - 50, "Z", size=13, bold=True, italic=True,
                  color=TRANS, anchor="start"))
    f.append(text(215, 368, "3 переміщення", size=15, bold=True, color=TRANS))

    # ── ПРАВОРУЧ: 3 оберти ──
    box2, c2 = iso_box(640, 232, fill="#eef2f7")
    f += box2
    # тонкі осі-натяки
    for (tx, ty) in [(c2[0] + 104, c2[1]), (c2[0], c2[1] - 104), (c2[0] + 60, c2[1] - 42)]:
        f.append(line(c2[0], c2[1], tx, ty, color=MUTED, sw=1.3))
    # оберт навколо Y (нишпорення) — горизонтальний еліпс-дуга зверху
    f.append(arc_arrow(c2[0], c2[1] - 104, 40, 15, -200, 20, col=ROT, sw=2.6))
    # оберт навколо X (крен) — вертикальний еліпс-дуга праворуч
    f.append(arc_arrow(c2[0] + 104, c2[1], 15, 40, -110, 130, col=ROT, sw=2.6))
    # оберт навколо Z (тангаж) — нахилений еліпс-дуга у глибину
    f.append(arc_arrow(c2[0] + 60, c2[1] - 42, 34, 20, 150, 400, col=ROT, sw=2.6))
    f.append(text(c2[0] + 2, c2[1] - 150, "навколо Y", size=11.5, color=ROT, anchor="middle"))
    f.append(text(c2[0] + 150, c2[1] + 4, "навколо X", size=11.5, color=ROT, anchor="start"))
    f.append(text(c2[0] + 96, c2[1] - 58, "навколо Z", size=11.5, color=ROT, anchor="start"))
    f.append(text(640, 368, "3 оберти", size=15, bold=True, color=ROT))

    b, bw, bh = textbox(W / 2, 412,
                        ["Три переміщення (куди зсунувся центр) плюс три оберти (як тіло повернуте) — разом шість."],
                        size=13, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "rigid-body-six.svg"), W, H, *f)


# ══════════════════════════════════════════════════════════════════════════════
# Фігури до вставки math-counting-constraints.md
# ══════════════════════════════════════════════════════════════════════════════

# ── Фігура 4: наївний підрахунок проти правди ─────────────────────────────────
def fig_naive_count_fails():
    W, H = 940, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "N точок на жорстких стрижнях: наївний підрахунок і правда",
                  size=16.5, bold=True))

    X0, X1 = 150, 800          # поле графіка по горизонталі
    Y0, Y1 = 100, 380          # верх (значення VMAX) і низ (значення VMIN)
    VMAX, VMIN = 8.0, -6.0
    NS = list(range(2, 9))

    def px(n): return X0 + (X1 - X0) * (n - NS[0]) / (NS[-1] - NS[0])
    def py(v): return Y0 + (Y1 - Y0) * (VMAX - v) / (VMAX - VMIN)

    # вісь нуля і сітка
    f.append(line(X0 - 40, py(0), X1 + 60, py(0), color=MUTED, sw=1.2, dash="4,6"))
    f.append(text(X0 - 50, py(0) + 5, "0", size=12, color=MUTED, anchor="end"))

    # зелена пряма «справжні ступені = 6»
    f.append(line(X0 - 40, py(6), X1 + 60, py(6), color=FIELD, sw=3))
    f.append(text(X1 + 62, py(6) - 12, "справжні ступені вільності = 6",
                  size=13.5, bold=True, color=FIELD, anchor="end"))

    # наївна крива 3N − N(N−1)/2
    naive = [(n, 3 * n - n * (n - 1) // 2) for n in NS]
    pts = [(px(n), py(v)) for n, v in naive]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join("%.1f,%.1f" % p for p in pts), POS))

    # вертикальні стрілки-надлишок між правдою і наївним значенням
    for n, v in naive:
        if n >= 5:
            x = px(n)
            f.append(line(x, py(6) + 4, x, py(v) - 4, color=NEG, sw=1.6, dash="3,4"))
            f.append(head(x, py(v) - 4, 0, 1, col=NEG, s=7))
            f.append(text(x + 9, (py(6) + py(v)) / 2 + 5, "%d" % (6 - v),
                          size=13, bold=True, color=NEG, anchor="start"))

    # точки й підписи наївних значень
    for n, v in naive:
        x, y = px(n), py(v)
        f.append(circle(x, y, 6, fill="#fdecea", stroke=POS, sw=2.2))
        f.append(text(x - 11, y + 5, "%d" % v, size=13, bold=True, color=POS, anchor="end"))
        f.append(text(x, Y1 + 42, "N = %d" % n, size=12.5, color=INK))

    f.append(text(px(4), py(6) - 46, "останнє чесне N",
                  size=12.5, color=MUTED))
    f.append(line(px(4), py(6) - 38, px(4), py(6) - 8, color=MUTED, sw=1.2))

    f.append(text(X0 - 50, Y0 + 18, "3N − усі", size=12.5, color=POS, anchor="end"))
    f.append(text(X0 - 50, Y0 + 36, "відстані", size=12.5, color=POS, anchor="end"))

    f.append(fitbox(210, 424, 520, 52,
                    ["Синій розрив — це кількість надлишкових в'язей: (N−3)(N−4)/2."],
                    size=13.5, pad=10, fill="#eaf0fd", stroke=NEG, sw=1.4, color=NEG, bold=True))
    return render(os.path.join(IMG, "naive-count-fails.svg"), W, H, *f)


# ── Фігура 5: що саме забороняє стрижень ──────────────────────────────────────
def fig_rod_velocity():
    W, H = 900, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Що саме забороняє жорсткий стрижень",
                  size=16.5, bold=True))

    A = (250, 300)
    B = (640, 190)
    ux, uy = B[0] - A[0], B[1] - A[1]
    L = math.hypot(ux, uy)
    ux, uy = ux / L, uy / L          # одиничний уздовж стрижня

    f.append(line(A[0], A[1], B[0], B[1], color=INK, sw=4))
    f.append(text((A[0] + B[0]) / 2 + 8, (A[1] + B[1]) / 2 + 30,
                  "довжина стала", size=13, color=MUTED))

    def velocity(P, vx, vy, name):
        g = []
        T = (P[0] + vx, P[1] + vy)
        # повна швидкість
        g.append(line(P[0], P[1], T[0], T[1], color=ROT, sw=3))
        g.append(head(T[0], T[1], vx, vy, col=ROT, s=10))
        # складова вздовж стрижня
        s = vx * ux + vy * uy
        Q = (P[0] + ux * s, P[1] + uy * s)
        g.append(line(P[0], P[1], Q[0], Q[1], color=FIELD, sw=5))
        g.append(head(Q[0], Q[1], ux * s, uy * s, col=FIELD, s=9))
        # пунктир від кінця швидкості до кінця проєкції
        g.append(line(T[0], T[1], Q[0], Q[1], color=MUTED, sw=1.3, dash="4,5"))
        g.append(dot(P[0], P[1], 8, col=INK, fill="#eafaf0"))
        g.append(text(T[0] + 14, T[1] - 6, name, size=14, bold=True, italic=True,
                      color=ROT, anchor="start"))
        return g, s

    gA, sA = velocity(A, 96, -132, "vᵢ")
    gB, sB = velocity(B, 150, -34, "vⱼ")
    f += gA
    f += gB

    f.append(text(A[0] - 16, A[1] + 30, "точка i", size=13, bold=True, anchor="end"))
    f.append(text(B[0] + 16, B[1] + 34, "точка j", size=13, bold=True, anchor="start"))

    f.append(text(300, 372, "зелені частини — уздовж стрижня — мусять бути однакові",
                  size=13.5, bold=True, color=FIELD, anchor="start"))
    f.append(text(300, 396, "решта швидкості (пунктир) — вільна",
                  size=13, color=MUTED, anchor="start"))

    box, bw, bh = textbox(150, 386, ["(vᵢ − vⱼ)·(rᵢ − rⱼ) = 0"], size=15, pad=12,
                          fill="#eafaf0", stroke=FIELD, sw=1.8, color=FIELD, bold=True)
    f.append(box)
    return render(os.path.join(IMG, "rod-velocity.svg"), W, H, *f)


# ── Фігура 6: п'ята точка і два корені ────────────────────────────────────────
def fig_fifth_point():
    W, H = 940, 520
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Десята відстань не вільна: два корені замість свободи",
                  size=16.5, bold=True))

    S = 46.0
    CX, CY = 300, 300

    def pr(p):
        x, y, z = p
        X = CX + (x - y) * 0.866 * S
        Y = CY + (x + y) * 0.30 * S - z * S * 0.86
        return (X, Y)

    P1, P2, P3, P4 = (0, 0, 0), (4, 0, 0), (0, 3, 0), (0, 0, 5)
    P5, P5m = (2, 1, 1), (2, 1, -1)

    # площина точок 1,2,3
    quad = [pr((-1.4, -1.4, 0)), pr((5.4, -1.4, 0)), pr((5.4, 4.4, 0)), pr((-1.4, 4.4, 0))]
    f.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f Z" '
             'fill="#f1f3f6" stroke="%s" stroke-width="1.4"/>'
             % (quad[0][0], quad[0][1], quad[1][0], quad[1][1],
                quad[2][0], quad[2][1], quad[3][0], quad[3][1], MUTED))

    # ребра тетраедра
    for a, b in [(P1, P2), (P1, P3), (P2, P3), (P1, P4), (P2, P4), (P3, P4)]:
        f.append(line(pr(a)[0], pr(a)[1], pr(b)[0], pr(b)[1], color=INK, sw=2.4))

    # три задані відстані до 5 і до дзеркального 5′
    for q in (P5, P5m):
        for b in (P1, P2, P3):
            f.append(line(pr(q)[0], pr(q)[1], pr(b)[0], pr(b)[1],
                          color=FIELD, sw=1.8, dash="5,5"))

    # шукані відстані від 4
    f.append(line(pr(P4)[0], pr(P4)[1], pr(P5)[0], pr(P5)[1], color=NEG, sw=3.2))
    f.append(line(pr(P4)[0], pr(P4)[1], pr(P5m)[0], pr(P5m)[1], color=POS, sw=3.2))

    for p, lab, dx, dy in [(P1, "1", -18, 16), (P2, "2", 14, 18), (P3, "3", 16, 14),
                           (P4, "4", 0, -18), (P5, "5", 18, -8), (P5m, "5′", 18, 14)]:
        X, Y = pr(p)
        f.append(dot(X, Y, 7, col=INK, fill="#eafaf0"))
        f.append(text(X + dx, Y + dy, lab, size=14, bold=True))

    # підписи на шуканих відрізках
    mx, my = (pr(P4)[0] + pr(P5)[0]) / 2, (pr(P4)[1] + pr(P5)[1]) / 2
    f.append(text(mx + 30, my - 22, "√21", size=13.5, bold=True, color=NEG, anchor="start"))
    mx, my = (pr(P4)[0] + pr(P5m)[0]) / 2, (pr(P4)[1] + pr(P5m)[1]) / 2
    f.append(text(mx + 34, my + 34, "√41", size=13.5, bold=True, color=POS, anchor="start"))

    f.append(text(700, 132, "три зелені відстані —", size=13, color=FIELD, anchor="start"))
    f.append(text(700, 152, "однакові для 5 і 5′", size=13, color=FIELD, anchor="start"))

    box, bw, bh = textbox(715, 262,
                          ["дев'ять відстаней задано,",
                           "десята x = d₄₅² — з рівняння",
                           "x² − 62x + 861 = 0",
                           "x = 21  або  x = 41"],
                          size=14.5, pad=14, fill="#eef2f7", stroke=LINE, sw=1.6)
    f.append(box)

    f.append(fitbox(250, 452, 620, 50,
                    ["Два корені — це точка та її дзеркало: вибір із двох, а не новий вимір."],
                    size=13.5, pad=10, fill=FILL, stroke=LINE, sw=1.3))
    return render(os.path.join(IMG, "fifth-point.svg"), W, H, *f)


# ── Фігура 7: формула рухливості — де працює і де бреше ───────────────────────
def fig_mobility():
    W, H = 1000, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Формула рухливості: один влучний підрахунок і два промахи",
                  size=16.5, bold=True))

    colw = W / 3.0
    for i in (1, 2):
        f.append(line(colw * i, 66, colw * i, 392, color=MUTED, sw=1.2, dash="3,7"))

    # ── панель 1: послідовна рука 6R ──
    cx = colw * 0.5
    f.append(text(cx, 92, "рука з шести шарнірів", size=14, bold=True))
    chain = [(cx - 92, 250), (cx - 44, 196), (cx + 4, 232), (cx + 52, 178),
             (cx + 88, 214), (cx + 60, 262), (cx + 6, 288)]
    for a, b in zip(chain, chain[1:]):
        f.append(line(a[0], a[1], b[0], b[1], color=INK, sw=3.4))
    for p in chain[:-1]:
        f.append(circle(p[0], p[1], 8, fill="#fdecea", stroke=POS, sw=2.2))
    f.append(circle(chain[-1][0], chain[-1][1], 6, fill=BG, stroke=MUTED, sw=2))
    f.append(rect(cx - 118, 246, 52, 14, fill="#dfe5ec", stroke=MUTED, sw=1.4, rx=3))
    f.append(fitbox(cx - 148, 322, 296, 62,
                    ["n = 7,  j = 6,  Σfᵢ = 6",
                     "M = 6·(7 − 1 − 6) + 6 = 6  ✓"],
                    size=14, pad=10, fill="#eafaf0", stroke=FIELD, sw=1.6, color=FIELD, bold=True))

    # ── панель 2: двері на двох співвісних завісах ──
    cx = colw * 1.5
    f.append(text(cx, 92, "двері на двох завісах", size=14, bold=True))
    f.append(line(cx - 74, 130, cx - 74, 300, color=MUTED, sw=1.4, dash="6,6"))
    f.append(text(cx - 80, 320, "спільна вісь", size=12, color=MUTED, anchor="end"))
    f.append(rect(cx - 74, 152, 128, 132, fill="#eef2f7", stroke=INK, sw=2, rx=4))
    for y in (176, 262):
        f.append(circle(cx - 74, y, 9, fill="#fdecea", stroke=POS, sw=2.2))
    f.append(arc_arrow(cx - 74, 218, 108, 62, -34, 26, col=NEG, sw=2.4))
    f.append(fitbox(cx - 148, 322, 296, 62,
                    ["n = 2,  j = 2,  Σfᵢ = 2   →   M = −4",
                     "а двері крутяться:  1  (надлишок r = 5)"],
                    size=13.5, pad=10, fill="#fdecea", stroke=POS, sw=1.6, color=POS, bold=True))

    # ── панель 3: плаский чотириланковик у просторі ──
    cx = colw * 2.5
    f.append(text(cx, 92, "плаский чотириланковик", size=14, bold=True))
    quad = [(cx - 96, 268), (cx + 82, 268), (cx + 44, 172), (cx - 54, 200)]
    for a, b in zip(quad, quad[1:] + quad[:1]):
        f.append(line(a[0], a[1], b[0], b[1], color=INK, sw=3.4))
    for p in quad:
        f.append(circle(p[0], p[1], 8, fill="#fdecea", stroke=POS, sw=2.2))
        f.append(line(p[0] - 16, p[1] - 24, p[0] + 16, p[1] + 24, color=MUTED, sw=1.2, dash="4,5"))
    f.append(text(cx, 140, "чотири осі паралельні", size=12, color=MUTED))
    f.append(rect(cx - 106, 274, 198, 12, fill="#dfe5ec", stroke=MUTED, sw=1.4, rx=3))
    f.append(fitbox(cx - 148, 322, 296, 62,
                    ["n = 4,  j = 4,  Σfᵢ = 4   →   M = −2",
                     "а він рухається:  1  (надлишок r = 3)"],
                    size=13.5, pad=10, fill="#fdecea", stroke=POS, sw=1.6, color=POS, bold=True))

    f.append(fitbox(180, 404, 640, 48,
                    ["M = 6·(n − 1 − j) + Σfᵢ + r,  де r — скільки в'язей повторюють одна одну"],
                    size=13.5, pad=10, fill=FILL, stroke=LINE, sw=1.3))
    return render(os.path.join(IMG, "mobility-count.svg"), W, H, *f)


# ── Фігури до вставки «Як ступені вільності замерзли» ───────────────────────

def fig_freeze_price():
    """Ціна першого щабля кожного ступеня вільності проти теплової мірки kT."""
    W, H = 990, 480
    X0, X1 = 300.0, 930.0          # вісь: 10⁻⁶ … 10⁶ К
    DEC = (X1 - X0) / 12.0

    def xx(E):
        return X0 + (math.log10(E) + 6.0) * DEC

    rows = [
        ("поступальний рух (будь-який газ)", 1e-5, "≈ 10⁻⁵ К", TRANS),
        ("оберт молекули N₂, O₂",            6.0,   "≈ 6 К",     FREE),
        ("оберт молекули H₂",                175.0, "≈ 175 К",   FREE),
        ("коливання N₂",                     3390.0, "≈ 3400 К", ROT),
        ("коливання H₂",                     6330.0, "≈ 6300 К", ROT),
        ("оберт навколо осі молекули",       9e4,   "≈ 10⁵ К",   ROT),
    ]
    f = []
    bx0, bx1 = xx(35.0), xx(300.0)
    f.append('<rect x="%.1f" y="100" width="%.1f" height="290" rx="4" '
             'fill="#e8f6ec" stroke="%s" stroke-width="1.2"/>' % (bx0, bx1 - bx0, FIELD))
    f.append(text((bx0 + bx1) / 2, 90, "мірка тепла kT: 35–300 К", size=13, color=FIELD, bold=True))

    for i, (name, val, lab, col) in enumerate(rows):
        y = 125.0 + i * 48.0
        f.append(text(290, y + 4.5, name, size=13, anchor="end"))
        f.append(line(X0 + 2, y, xx(val), y, color=col, sw=4.0))
        f.append(circle(xx(val), y, 5.5, fill=BG, stroke=col, sw=2.4))
        f.append(text(968, y + 4.5, lab, size=13, color=col, bold=True, anchor="end"))

    f.append(line(X0, 400, X1, 400, color=INK, sw=1.6))
    for k in range(-6, 7, 2):
        x = X0 + (k + 6) * DEC
        f.append(line(x, 400, x, 407, color=INK, sw=1.4))
        if k == 0:
            lb = "1"
        else:
            lb = "10" + ("⁻" if k < 0 else "") + "".join("⁰¹²³⁴⁵⁶⁷⁸⁹"[int(d)] for d in str(abs(k)))
        f.append(text(x, 424, lb, size=13, color=MUTED))
    f.append(text((X0 + X1) / 2, 456, "ціна першого щабля, виражена в градусах (ΔE/k)",
                  size=13.5, color=INK))
    return render(os.path.join(IMG, "freeze-price.svg"), W, H, *f,
                  title="Скільки коштує розворушити ступінь вільності")


def _c_rot(T, parity=None, theta=85.4, lmax=90):
    """Обертова теплоємність жорсткого ротатора у частках R (сума за щаблями).
    parity=None — усі щаблі (рівноважна суміш); 0 — лише парні (пара-H₂); 1 — лише непарні (орто-H₂)."""
    def U(t):
        z = s = 0.0
        for l in range(lmax + 1):
            if parity is not None and l % 2 != parity:
                continue
            e = l * (l + 1) * theta
            w = (2 * l + 1) * math.exp(-e / t)
            z += w
            s += w * e
        return s / z
    h = T * 0.01
    return (U(T + h) - U(T - h)) / (2 * h)


def _c_rot_normal(T):
    """Заморожена суміш 3 частини орто (непарні щаблі) : 1 частина пара (парні) — «звичайний» водень."""
    return 0.25 * _c_rot(T, 0) + 0.75 * _c_rot(T, 1)


def _c_vib(T, theta=6332.0):
    x = theta / T
    if x > 60:
        return 0.0
    ex = math.exp(x)
    return x * x * ex / (ex - 1.0) ** 2


def fig_h2_staircase():
    """Сходинки теплоємності водню: 3/2 R → 5/2 R → 7/2 R."""
    W, H = 940, 520
    X0, X1, Y0, Y1 = 130.0, 880.0, 400.0, 90.0    # T: 10…20000 К, C/R: 1…4
    KX = (X1 - X0) / 3.30103

    def xx(T):
        return X0 + (math.log10(T) - 1.0) * KX

    def yy(c):
        return Y0 - (c - 1.0) * (Y0 - Y1) / 3.0

    f = []
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="4" fill="#e8f6ec" '
             'stroke="none"/>' % (xx(35), Y1, xx(273) - xx(35), Y0 - Y1))
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="4" fill="#fdeeec" '
             'stroke="none"/>' % (xx(2500), Y1, X1 - xx(2500), Y0 - Y1))

    for c, lab in ((1.5, "1.5"), (2.5, "2.5"), (3.5, "3.5")):
        f.append(line(X0, yy(c), X1, yy(c), color=MUTED, sw=1.2, dash="6,7"))
        f.append(text(122, yy(c) + 4.5, lab, size=13, color=MUTED, anchor="end"))

    def curve(fn):
        pts, T = [], 10.0
        while T <= 20000.0:
            pts.append((xx(T), yy(1.5 + fn(T) + _c_vib(T))))
            T *= 1.06
        return " ".join("%.1f,%.1f" % p for p in pts)

    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0" '
             'stroke-dasharray="8,7"/>' % (curve(_c_rot), MUTED))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.2"/>'
             % (curve(_c_rot_normal), NEG))

    for T, c in ((35.0, 1.50), (273.0, 2.44)):
        f.append(circle(xx(T), yy(c), 6, fill=POS, stroke=POS, sw=2))

    # легенда (штрихи-зразки ліворуч, підписи праворуч — лінії не заходять у текст)
    f.append(line(150, 108, 185, 108, color=NEG, sw=3.2))
    f.append(text(192, 112, "заморожена суміш 3:1 — Деннісон, 1927",
                  size=12.5, color=NEG, anchor="start"))
    f.append(line(150, 132, 185, 132, color=MUTED, sw=2.0, dash="8,7"))
    f.append(text(192, 136, "рівноважна суміш — так рахували до 1927",
                  size=12.5, color=MUTED, anchor="start"))

    f.append(text(215, 372, "3/2 R — тільки політ", size=13, color=INK))
    f.append(text(460, 292, "5/2 R — політ і оберт", size=13, color=INK))
    f.append(text(788, 176, "7/2 R — ще й коливання", size=13, color=INK))
    f.append(text(355, 80, "виміряв Ойкен, 1912", size=13, color=FIELD, bold=True))
    f.append(text(775, 116, "вище ≈2500 К H₂ розпадається на атоми", size=12.5, color=POS))
    f.append(text(56, 60, "теплоємність при сталому об'ємі, у частках R",
                  size=13, color=INK, anchor="start"))

    f.append(line(X0, Y1 - 4, X0, Y0, color=INK, sw=1.6))
    f.append(line(X0, Y0, X1, Y0, color=INK, sw=1.6))
    for T, lab in ((10, "10 К"), (100, "100 К"), (1000, "1000 К"), (10000, "10000 К")):
        f.append(line(xx(T), Y0, xx(T), Y0 + 7, color=INK, sw=1.4))
        f.append(text(xx(T), Y0 + 26, lab, size=13, color=MUTED))
    f.append(text((X0 + X1) / 2, 452, "температура (логарифмічна шкала)", size=13.5, color=INK))
    return render(os.path.join(IMG, "h2-staircase.svg"), W, H, *f,
                  title="Теплоємність водню: ступені вільності вмикаються сходинками")


if __name__ == "__main__":
    fig_freeze_price()
    fig_h2_staircase()
    fig_constraints_subtract()
    fig_three_points()
    fig_rigid_body_six()
    fig_naive_count_fails()
    fig_rod_velocity()
    fig_fifth_point()
    fig_mobility()
    print("OK: 7 фігур у", IMG)
