# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GREEN_FILL = "#eafaf0"
RED_FILL   = "#fdecea"
BLUE_FILL  = "#eef4ff"
GREY_FILL  = "#eef1f5"

# Одиниці функції F(A,B,C,D)=Σm(0,4,5,7,8,12,13,15) на карті 4×4.
# рядок i = AB у коді Грея (00,01,11,10); стовпець j = CD у коді Грея (00,01,11,10)
ONES = {(0, 0), (1, 0), (2, 0), (3, 0), (1, 1), (1, 2), (2, 1), (2, 2)}
COLS = ["00", "01", "11", "10"]
ROWS = ["00", "01", "11", "10"]


def cell(x, y, s, w, h, fill=BG, size=15, color=INK):
    out = rect(x, y, w, h, fill=fill, stroke=INK, sw=1.3, rx=0)
    out += text(x + w / 2, y + h / 2 + size * 0.35, s, size=size, color=color, bold=True)
    return out


def draw_map(ox, oy, cw, ones=ONES, size=17):
    """Порожня карта 4×4 з осями в коді Грея; повертає список фрагментів."""
    p = [text(ox + cw * 2, oy - 26, "CD", size=12, color=MUTED, bold=True)]
    for j, c in enumerate(COLS):
        p.append(text(ox + cw * (j + 0.5), oy - 8, c, size=12, color=NEG, bold=True))
    p.append(text(ox - 26, oy + cw * 2, "AB", size=12, color=MUTED, bold=True))
    for i, r in enumerate(ROWS):
        p.append(text(ox - 12, oy + cw * (i + 0.5) + 5, r, size=12, color=NEG, bold=True))
    for i in range(4):
        for j in range(4):
            v, col = ("1", POS) if (i, j) in ones else ("0", MUTED)
            p.append(cell(ox + cw * j, oy + cw * i, v, cw, cw, size=size, color=col))
    return p


# ── Фіг.1: ціна схеми — сира форма проти мінімальної ──────────────────────────
def fig_circuit_cost():
    W, H = 860, 430
    p = []

    def gatebox(x, y, w, h, label, fill=BLUE_FILL, size=13):
        out = rect(x, y, w, h, fill=fill, stroke=INK, sw=1.6, rx=7)
        out += text(x + w / 2, y + h / 2 + size * 0.35, label, size=size, color=INK, bold=True)
        return out

    # ── ліворуч: сира сума добутків — 8 вентилів AND → OR ──
    lx = 70
    p.append(text(lx + 95, 62, "сира форма (з таблиці)", size=14, color=INK, bold=True))
    andx, andw, andh = 60, 60, 22
    ys = [92 + i * 32 for i in range(8)]
    busx = andx + lx + andw + 22          # вертикальна шина-збирач
    for i, yy in enumerate(ys):
        p.append(gatebox(lx + andx, yy, andw, andh, "AND", fill=BLUE_FILL, size=11))
        # чотири короткі входи ліворуч
        for k in range(4):
            iy = yy + 4 + k * (andh - 8) / 3
            p.append(line(lx + andx - 16, iy, lx + andx, iy, color=MUTED, sw=1.0))
        # вихід у шину
        p.append(line(lx + andx + andw, yy + andh / 2, busx, yy + andh / 2, color=LINE, sw=1.2))
    p.append(line(busx, ys[0] + andh / 2, busx, ys[-1] + andh / 2, color=LINE, sw=1.4))
    p.append(text(lx + andx - 30, 92 + 8 * 32 + 6, "входи A,B,C,D", size=10, color=MUTED, anchor="start"))
    # OR
    orcy = (ys[0] + ys[-1] + andh) / 2
    p.append(gatebox(busx + 18, orcy - 26, 60, 52, "OR", fill=GREY_FILL, size=13))
    p.append(line(busx, orcy, busx + 18, orcy, color=LINE, sw=1.4))
    p.append(line(busx + 78, orcy, busx + 108, orcy, color=LINE, sw=1.6))
    p.append(text(busx + 122, orcy + 6, "F", size=18, color=INK, bold=True))
    b, _, _ = textbox(lx + 150, 400, "8 вентилів AND · по 4 входи  =  32 входи", size=12,
                      color=POS, fill=RED_FILL, stroke=POS, sw=1.4)
    p.append(b)

    # ── стрілка мінімізації ──
    p.append(arrow(360, 210, 470, 210, color=INK, sw=2.4))
    p.append(text(415, 196, "мінімізація", size=13, color=INK, bold=True))

    # ── праворуч: мінімальна форма — 2 вентилі AND → OR ──
    rx = 520
    p.append(text(rx + 120, 62, "мінімальна форма", size=14, color=INK, bold=True))
    terms = ["C̄·D̄", "B·D"]
    ry = [150, 250]
    rbusx = rx + 60 + 96 + 22
    for t, yy in zip(terms, ry):
        p.append(gatebox(rx + 60, yy - 18, 96, 40, "AND", fill=BLUE_FILL, size=12))
        p.append(text(rx + 60 + 48, yy + 34, t, size=13, color=INK, bold=True))
        for k in range(2):
            iy = yy - 8 + k * 16
            p.append(line(rx + 60 - 18, iy, rx + 60, iy, color=MUTED, sw=1.1))
        p.append(line(rx + 60 + 96, yy, rbusx, yy, color=LINE, sw=1.3))
    p.append(line(rbusx, ry[0], rbusx, ry[1], color=LINE, sw=1.4))
    orcy2 = (ry[0] + ry[1]) / 2
    p.append(gatebox(rbusx + 18, orcy2 - 26, 60, 52, "OR", fill=GREY_FILL, size=13))
    p.append(line(rbusx, orcy2, rbusx + 18, orcy2, color=LINE, sw=1.4))
    p.append(line(rbusx + 78, orcy2, rbusx + 108, orcy2, color=LINE, sw=1.6))
    p.append(text(rbusx + 122, orcy2 + 6, "F", size=18, color=INK, bold=True))
    b2, _, _ = textbox(rx + 150, 400, "2 вентилі AND · по 2 входи  =  4 входи", size=12,
                       color=FIELD, fill=GREEN_FILL, stroke=FIELD, sw=1.4)
    p.append(b2)

    render(os.path.join(OUT, "circuit-cost.svg"), W, H, *p,
           title="Та сама функція: сира схема з 8 вентилів → мінімальна з 2")


# ── Фіг.2: імпліканта росте до простої (максимальної) ─────────────────────────
def fig_prime_implicant():
    W, H = 900, 340
    cw = 40
    p = []
    stages = [
        ({(0, 0)},                          (0, 0, 1, 1), "Ā·B̄·C̄·D̄", "4 літери",  "1 клітина"),
        ({(0, 0), (1, 0)},                  (0, 0, 2, 1), "Ā·C̄·D̄",   "3 літери",  "2 клітини"),
        ({(0, 0), (1, 0), (2, 0), (3, 0)},  (0, 0, 4, 1), "C̄·D̄",     "2 літери",  "4 клітини"),
    ]
    xs = [70, 360, 650]
    oy = 92
    for k, (grp, box, term, lits, cellcnt) in enumerate(stages):
        ox = xs[k]
        p += draw_map(ox, oy, cw)
        gi, gj, gh, gw = box
        gcol = FIELD if k == 2 else NEG
        p.append(rect(ox + cw * gj - 4, oy + cw * gi - 4, cw * gw + 8, cw * gh + 8,
                      fill="none", stroke=gcol, sw=3, rx=9))
        # підпис знизу
        p.append(text(ox + cw * 2, oy + cw * 4 + 30, cellcnt + "  →  " + lits, size=12,
                      color=INK, bold=True))
        p.append(text(ox + cw * 2, oy + cw * 4 + 52, term, size=15, color=gcol, bold=True))
        if k < 2:
            ax = ox + cw * 4 + 18
            p.append(arrow(ax, oy + cw * 2, ax + 40, oy + cw * 2, color=INK, sw=2.2))
            p.append(text(ax + 20, oy + cw * 2 - 10, "росте", size=10, color=MUTED))
    p.append(text(xs[2] + cw * 2, oy - 52, "проста імпліканта (далі нікуди)", size=12,
                  color=FIELD, bold=True))

    render(os.path.join(OUT, "prime-implicant.svg"), W, H, *p,
           title="Група росте — доданок коротшає; максимальна група = проста імпліканта")


# ── Фіг.3: суттєві прості імпліканти й зайва третя ────────────────────────────
def fig_essential_cover():
    W, H = 780, 470
    cw = 60
    ox, oy = 210, 78
    p = draw_map(ox, oy, cw, size=18)

    # зелена: увесь лівий стовпець CD=00  → C̄·D̄  (суттєва)
    p.append(rect(ox - 5, oy - 5, cw + 10, cw * 4 + 10, fill="none", stroke=FIELD, sw=3.2, rx=11))
    # червона: центральний квадрат B·D (рядки 1-2, стовпці 1-2)  (суттєва)
    p.append(rect(ox + cw * 1 - 5, oy + cw * 1 - 5, cw * 2 + 10, cw * 2 + 10,
                  fill="none", stroke=POS, sw=3.2, rx=11))
    # сіра пунктирна: B·C̄ (рядки 1-2, стовпці 0-1) — зайва, всередині-інсет
    p.append(rect(ox + cw * 0 + 9, oy + cw * 1 + 9, cw * 2 - 18, cw * 2 - 18,
                  fill="none", stroke=MUTED, sw=2.2, rx=8, ))
    # (пунктир додаємо окремою лінією-рамкою через dash)
    p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="8" fill="none" '
             'stroke="%s" stroke-width="2.2" stroke-dasharray="6 5"/>'
             % (ox + cw * 0 + 9, oy + cw * 1 + 9, cw * 2 - 18, cw * 2 - 18, MUTED))

    # прапорці «лише одна група накриває» — за межами карти
    p.append(text(ox - 20, oy + cw * 0.5 + 4, "лише зелена →", size=10, color=FIELD, anchor="end"))
    p.append(text(ox - 20, oy + cw * 3.5 + 4, "лише зелена →", size=10, color=FIELD, anchor="end"))
    p.append(text(ox + cw * 4 + 20, oy + cw * 1.5 + 4, "← лише червона", size=10, color=POS, anchor="start"))
    p.append(text(ox + cw * 4 + 20, oy + cw * 2.5 + 4, "← лише червона", size=10, color=POS, anchor="start"))

    # легенда знизу
    ly = oy + cw * 4 + 34
    b1, _, _ = textbox(ox + cw * 0.9, ly, "C̄·D̄ — суттєва", size=12, color=FIELD,
                       fill=GREEN_FILL, stroke=FIELD, sw=1.6)
    b2, _, _ = textbox(ox + cw * 2.9, ly, "B·D — суттєва", size=12, color=POS,
                       fill=RED_FILL, stroke=POS, sw=1.6)
    b3, _, _ = textbox(ox + cw * 2, ly + 40, "B·C̄ — теж проста, але зайва (клітини вже накрито)",
                       size=12, color=MUTED, fill=GREY_FILL, stroke=MUTED, sw=1.6)
    res, _, _ = textbox(ox + cw * 2, ly + 84, "F = C̄·D̄ + B·D", size=15, color=INK, bold=True,
                        fill="#f6f4ec", stroke=INK, sw=2)
    p += [b1, b2, b3, res]

    render(os.path.join(OUT, "essential-cover.svg"), W, H, *p,
           title="Дві суттєві прості імпліканти покривають усе; третя — зайва")


# ══ Фігури вставки «Прості імпліканти й задача покриття» ══════════════════════
# Наскрізний приклад вставки: G(A,B,C) = Σm(0,1,2,5,6,7); нулі — m3=011 і m4=100.

G_ON  = {(0, 0, 0): "m0", (0, 0, 1): "m1", (0, 1, 0): "m2",
         (1, 0, 1): "m5", (1, 1, 0): "m6", (1, 1, 1): "m7"}
G_OFF = {(0, 1, 1): "m3", (1, 0, 0): "m4"}


# ── Фіг.4: імпліканта = підкуб усередині ON-множини; чому Ā·B̄ проста ──────────
def fig_implicant_cube():
    W, H = 900, 640
    OX, OY, S, D = 280, 420, 150, 90
    R = 24                                   # радіус вузла
    TRIM = R + 3                             # ребра спиняються, не заходячи у вузол

    def P(a, b, c):
        return (OX + b * S + a * D, OY - c * S - a * D)

    def poly(pts, fill, stroke, sw=2.4, dash=None, op=0.16):
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        s = " ".join("%.1f,%.1f" % p for p in pts)
        return ('<polygon points="%s" fill="%s" fill-opacity="%.2f" stroke="%s" '
                'stroke-width="%.1f"%s/>' % (s, fill, op, stroke, sw, d))

    def trimmed(u, v):
        (x1, y1), (x2, y2) = P(*u), P(*v)
        dx, dy = x2 - x1, y2 - y1
        L = (dx * dx + dy * dy) ** 0.5
        ux, uy = dx / L, dy / L
        return (x1 + ux * TRIM, y1 + uy * TRIM, x2 - ux * TRIM, y2 - uy * TRIM)

    p = []
    verts = [(a, b, c) for a in (0, 1) for b in (0, 1) for c in (0, 1)]

    # ── дві грані-розширення Ā·B̄, кожну блокує свій нуль ──
    p.append(poly([P(0, 0, 0), P(0, 0, 1), P(0, 1, 1), P(0, 1, 0)],
                  POS, POS, dash="7 5"))            # грань Ā = 0-- , містить m3
    p.append(poly([P(0, 0, 0), P(0, 0, 1), P(1, 0, 1), P(1, 0, 0)],
                  NEG, NEG, dash="7 5"))            # грань B̄ = -0- , містить m4

    # ── ребра куба ──
    for u in verts:
        for i in range(3):
            v = list(u)
            v[i] = 1 - v[i]
            v = tuple(v)
            if u < v:
                x1, y1, x2, y2 = trimmed(u, v)
                green = {u, v} == {(0, 0, 0), (0, 0, 1)}
                p.append(line(x1, y1, x2, y2,
                              color=FIELD if green else MUTED,
                              sw=5.0 if green else 1.4))

    # ── вузли ──
    for v in verts:
        x, y = P(*v)
        on = v in G_ON
        name = G_ON[v] if on else G_OFF[v]
        p.append(circle(x, y, R, fill=BG if on else GREY_FILL,
                        stroke=FIELD if on else POS, sw=2.6))
        p.append(text(x, y - 1, name, size=12, color=INK if on else POS, bold=True))
        p.append(text(x, y + 12, "".join(str(t) for t in v), size=9,
                      color=MUTED if on else POS))

    # ── підписи ──
    p.append(text(225, 350, "Ā·B̄", size=15, color=FIELD, bold=True))
    p.append(text(400, 305, "Ā", size=15, color=POS, bold=True))
    p.append(text(322, 258, "B̄", size=15, color=NEG, bold=True))

    ly = 492
    b1, _, _ = textbox(450, ly, "ребро Ā·B̄ (00−) — обидві вершини = 1 → імпліканта",
                       size=12, color=FIELD, fill=GREEN_FILL, stroke=FIELD, sw=1.6)
    b2, _, _ = textbox(450, ly + 40, "розтягти до грані Ā (0−−) — не можна: усередині m3 = 0",
                       size=12, color=POS, fill=RED_FILL, stroke=POS, sw=1.6)
    b3, _, _ = textbox(450, ly + 80, "розтягти до грані B̄ (−0−) — не можна: усередині m4 = 0",
                       size=12, color=NEG, fill=BLUE_FILL, stroke=NEG, sw=1.6)
    b4, _, _ = textbox(450, ly + 122, "обидва напрямки росту перекрито → Ā·B̄ ПРОСТА",
                       size=13, color=INK, bold=True, fill="#f6f4ec", stroke=INK, sw=2)
    p += [b1, b2, b3, b4]

    render(os.path.join(OUT, "implicant-cube.svg"), W, H, *p,
           title="Імпліканта — підкуб цілком усередині одиниць; проста — якому нікуди рости")


# ── Фіг.5: таблиця простих імплікант — циклічна, суттєвих нема ────────────────
def fig_pi_chart():
    W, H = 1000, 560
    p = []

    # ── карта Карно 2×4 ліворуч ──
    cw = 64
    ox, oy = 92, 132
    bc = ["00", "01", "11", "10"]
    mt = [[0, 1, 3, 2], [4, 5, 7, 6]]
    p.append(text(ox + cw * 2, oy - 40, "BC", size=12, color=MUTED, bold=True))
    for j, s in enumerate(bc):
        p.append(text(ox + cw * (j + 0.5), oy - 18, s, size=12, color=NEG, bold=True))
    p.append(text(ox - 34, oy + cw, "A", size=12, color=MUTED, bold=True))
    for i in range(2):
        p.append(text(ox - 14, oy + cw * (i + 0.5) + 5, str(i), size=12, color=NEG, bold=True))
        for j in range(4):
            m = mt[i][j]
            one = m in (0, 1, 2, 5, 6, 7)
            p.append(rect(ox + cw * j, oy + cw * i, cw, cw,
                          fill=BG if one else GREY_FILL, stroke=INK, sw=1.3, rx=0))
            p.append(text(ox + cw * (j + 0.5), oy + cw * (i + 0.5) + 4,
                          "1" if one else "0", size=19,
                          color=POS if one else MUTED, bold=True))
            p.append(text(ox + cw * j + 13, oy + cw * i + 15, "m%d" % m, size=9, color=MUTED))
    p.append(text(ox + cw * 2, oy + cw * 2 + 34, "G = Σm(0,1,2,5,6,7)", size=13,
                  color=INK, bold=True))
    p.append(text(ox + cw * 2, oy + cw * 2 + 58, "нулі — лише m3 і m4", size=11, color=MUTED))

    # ── таблиця простих імплікант праворуч ──
    cols = [0, 1, 2, 5, 6, 7]
    rows = [("P1", "Ā·B̄", {0, 1}), ("P2", "B̄·C", {1, 5}), ("P3", "A·C", {5, 7}),
            ("P4", "A·B", {6, 7}), ("P5", "B·C̄", {2, 6}), ("P6", "Ā·C̄", {0, 2})]
    tx, ty = 470, 132
    lw, cwid, rh = 122, 62, 44

    for j, m in enumerate(cols):
        p.append(text(tx + lw + cwid * (j + 0.5), ty - 14, "m%d" % m, size=12,
                      color=INK, bold=True))
    for i, (nm, term, cov) in enumerate(rows):
        yy = ty + rh * i
        p.append(text(tx + 8, yy + rh / 2 + 5, nm, size=12, color=MUTED, bold=True, anchor="start"))
        p.append(text(tx + 46, yy + rh / 2 + 5, term, size=13, color=INK, bold=True, anchor="start"))
        for j, m in enumerate(cols):
            p.append(rect(tx + lw + cwid * j, yy, cwid, rh, fill=BG, stroke=MUTED, sw=1.0, rx=0))
            if m in cov:
                p.append(text(tx + lw + cwid * (j + 0.5), yy + rh / 2 + 6, "×",
                              size=20, color=FIELD, bold=True))
    # рядок-підсумок: скільки × у стовпці
    yy = ty + rh * 6
    p.append(text(tx + 8, yy + 22, "разом ×", size=11, color=MUTED, bold=True, anchor="start"))
    for j, m in enumerate(cols):
        n = sum(1 for _, _, cov in rows if m in cov)
        p.append(text(tx + lw + cwid * (j + 0.5), yy + 24, str(n), size=15, color=POS, bold=True))

    b, _, _ = textbox(tx + lw / 2 + cwid * 3, yy + 78,
                      "у КОЖНОМУ стовпці рівно два × → жодної суттєвої",
                      size=12, color=POS, fill=RED_FILL, stroke=POS, sw=1.6)
    p.append(b)

    render(os.path.join(OUT, "pi-chart-cyclic.svg"), W, H, *p,
           title="Таблиця простих імплікант: шість рядків, шість стовпців, жодного одинокого ×")


# ── Фіг.6: цикл із шести й два рівноцінні покриття ────────────────────────────
def fig_cycle_covers():
    W, H = 980, 560
    import math
    p = []
    ring = [("m0", "P1", "Ā·B̄"), ("m1", "P2", "B̄·C"), ("m5", "P3", "A·C"),
            ("m7", "P4", "A·B"), ("m6", "P5", "B·C̄"), ("m2", "P6", "Ā·C̄")]
    R, NR = 118, 23

    def panel(cx, cy, pick, col, fillc, head, expr):
        q = [text(cx, cy - R - 74, head, size=13, color=col, bold=True)]
        V = []
        for i in range(6):
            a = math.radians(-90 + i * 60)
            V.append((cx + R * math.cos(a), cy + R * math.sin(a)))
        for i in range(6):
            (x1, y1), (x2, y2) = V[i], V[(i + 1) % 6]
            dx, dy = x2 - x1, y2 - y1
            L = math.hypot(dx, dy)
            ux, uy = dx / L, dy / L
            t = NR + 3
            hot = (i + 1) in pick
            q.append(line(x1 + ux * t, y1 + uy * t, x2 - ux * t, y2 - uy * t,
                          color=col if hot else "#c9ced6", sw=5.5 if hot else 1.6))
            # підпис ребра — назовні від центру
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            vx, vy = mx - cx, my - cy
            n = math.hypot(vx, vy)
            lx, ly = mx + vx / n * 34, my + vy / n * 34
            q.append(text(lx, ly + 4, ring[i][2], size=12,
                          color=col if hot else MUTED, bold=hot))
        for i in range(6):
            x, y = V[i]
            q.append(circle(x, y, NR, fill=BG, stroke=INK, sw=2.0))
            q.append(text(x, y + 4, ring[i][0], size=12, color=INK, bold=True))
        b, _, _ = textbox(cx, cy + R + 96, expr, size=13, color=col,
                          fill=fillc, stroke=col, sw=1.8, bold=True)
        q.append(b)
        return q

    p += panel(248, 268, {1, 3, 5}, FIELD, GREEN_FILL,
               "непарні ребра: P1 · P3 · P5", "G = Ā·B̄ + A·C + B·C̄")
    p += panel(732, 268, {2, 4, 6}, NEG, BLUE_FILL,
               "парні ребра: P2 · P4 · P6", "G = B̄·C + A·B + Ā·C̄")
    p.append(text(490, 300, "або", size=14, color=MUTED, bold=True))

    render(os.path.join(OUT, "cycle-two-covers.svg"), W, H, *p,
           title="Шестикутник ON-множини: два досконалі парування = два мінімуми")


# ── Фіг.7 (вставка hist): дві доріжки — логіка й схемотехніка — і де вони сплелися ──
def fig_two_lanes():
    W, H = 1150, 430
    p = []

    Y_LOG, Y_ENG, Y_MIX = 150, 360, 255

    def node(cx, cy, year, what, col, fillc, size=13):
        b, w, h = textbox(cx, cy, [year, what], size=size, pad=10,
                          fill=fillc, stroke=col, sw=1.8, color=col, bold=True)
        p.append(b)
        return cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2

    # ── доріжка «логіка» ──
    bl_l, bl_r, _, bl_b = node(280, Y_LOG, "1937", "форма без назви", MUTED, BG)
    q52_l, q52_r, _, q52_b = node(490, Y_LOG, "1952", "простий імплікант", NEG, BLUE_FILL)
    q55_l, q55_r, _, _ = node(676, Y_LOG, "1955", "консенсус", NEG, BLUE_FILL)
    q59_l, q59_r, _, q59_b = node(862, Y_LOG, "1959", "ядро без каталогу", NEG, BLUE_FILL)

    # ── доріжка «схемотехніка» ──
    _, sh_r, _, _ = node(290, Y_ENG, "1938", "ціна за літеру", POS, RED_FILL)
    mc_l, mc_r, mc_t, _ = node(676, Y_ENG, "1956", "0 / 1 / –  і d-терми", POS, RED_FILL)

    # ── вузол-сплетіння ──
    chu_l, _, chu_t, chu_b = node(1050, Y_MIX, "1961", "ядро + d-терми", FIELD, GREEN_FILL)

    # стрілки вздовж доріжок (лише в проміжках між рамками)
    p.append(arrow(bl_r + 8, Y_LOG, q52_l - 8, Y_LOG, color=MUTED))
    p.append(arrow(q52_r + 8, Y_LOG, q55_l - 8, Y_LOG, color=NEG))
    p.append(arrow(q55_r + 8, Y_LOG, q59_l - 8, Y_LOG, color=NEG))
    p.append(arrow(sh_r + 8, Y_ENG, mc_l - 8, Y_ENG, color=POS))

    # стрілки-перехрестя: назва йде в залізо, ядро й d-терми сходяться
    p.append(arrow(490, q52_b + 6, 640, mc_t - 6, color=INK, sw=2.0))
    p.append(arrow(862, q59_b + 6, chu_l - 6, chu_t - 4, color=FIELD, sw=2.0))
    p.append(arrow(mc_r + 8, Y_ENG - 6, chu_l - 6, chu_b + 4, color=FIELD, sw=2.0))

    # підписи доріжок — ліворуч, далеко від рамок
    p.append(text(40, Y_LOG + 5, "ЛОГІКА", size=12, color=NEG, anchor="start", bold=True))
    p.append(text(40, Y_ENG + 5, "СХЕМОТЕХНІКА", size=12, color=POS, anchor="start", bold=True))

    render(os.path.join(OUT, "two-lanes.svg"), W, H, *p,
           title="Дві доріжки й місце, де вони сплелися")


if __name__ == "__main__":
    fig_circuit_cost()
    fig_prime_implicant()
    fig_essential_cover()
    fig_implicant_cube()
    fig_pi_chart()
    fig_cycle_covers()
    fig_two_lanes()
    print("OK: figures written to", OUT)
