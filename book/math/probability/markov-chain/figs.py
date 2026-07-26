# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Матриця переходів наскрізного прикладу (Сонячно / Хмарно / Дощ).
P = [[0.7, 0.2, 0.1],
     [0.3, 0.4, 0.3],
     [0.2, 0.4, 0.4]]
LABELS = ["С", "Х", "Д"]
# Кольори станів: сонце — тепле, хмара — сіре, дощ — холодне.
COL = {0: POS, 1: MUTED, 2: NEG}


def step(v):
    return [sum(v[i] * P[i][j] for i in range(3)) for j in range(3)]


# ── Помічники: криві стрілки й петлі з обрізанням до межі кружечка ────────────
def _trim(px, py, cx, cy, r):
    dx, dy = cx - px, cy - py
    L = math.hypot(dx, dy) or 1.0
    return px + dx / L * r, py + dy / L * r


def carrow(a, b, r, bow, color=INK, sw=1.9):
    """Крива стрілка від центра a до центра b, вигнута перпендикулярно на bow.
    Повертає (svg, (lx,ly)) — де lx,ly зручна точка для підпису (біля вигину)."""
    ax, ay = a
    bx, by = b
    mx, my = (ax + bx) / 2, (ay + by) / 2
    dx, dy = bx - ax, by - ay
    L = math.hypot(dx, dy) or 1.0
    perp = (-dy / L, dx / L)
    cx, cy = mx + perp[0] * bow, my + perp[1] * bow
    sx, sy = _trim(ax, ay, cx, cy, r)
    ex, ey = _trim(bx, by, cx, cy, r)
    svg = ('<path d="M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" '
           'stroke-width="%.1f" marker-end="url(#arrow)"/>' % (sx, sy, cx, cy, ex, ey, color, sw))
    # точка підпису — трохи далі за вигин
    lx, ly = mx + perp[0] * (bow * 1.28), my + perp[1] * (bow * 1.28)
    return svg, (lx, ly)


def selfloop(a, r, direction, color=INK, sw=1.9):
    """Петля на кружечку a у напрямі 'up' або 'down'. Повертає (svg, (lx,ly))."""
    cx, cy = a
    s = -1 if direction == "up" else 1
    sx, sy = cx - 13, cy + s * (r - 3)
    ex, ey = cx + 13, cy + s * (r - 3)
    c1x, c1y = cx - 34, cy + s * (r + 46)
    c2x, c2y = cx + 34, cy + s * (r + 46)
    svg = ('<path d="M%.1f,%.1f C%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="none" '
           'stroke="%s" stroke-width="%.1f" marker-end="url(#arrow)"/>'
           % (sx, sy, c1x, c1y, c2x, c2y, ex, ey, color, sw))
    return svg, (cx, cy + s * (r + 58))


def problabel(pt, s, color=INK):
    """Маленька біла плашка з ймовірністю (щоб напис не зливався з лініями)."""
    body, w, h = textbox(pt[0], pt[1], s, size=12.5, pad=4, fill=BG,
                         stroke="#d7dbe0", sw=0.8, color=color, bold=True, rx=4)
    return body


def statecircle(a, idx, r):
    col = COL[idx]
    return (circle(a[0], a[1], r, fill="#ffffff", stroke=col, sw=2.6) +
            text(a[0], a[1] + 6, LABELS[idx], 19, col, "middle", bold=True))


# ── Фігура 1: граф переходів + матриця ───────────────────────────────────────
def fig_transition_graph():
    W, H = 780, 452
    r = 29
    C = (168, 150)
    X = (452, 150)
    D = (310, 348)
    frags = []

    frags.append(text(W / 2, 48, "Ланцюг двома мовами: граф і стохастична матриця",
                      13.5, MUTED, "middle"))

    # ── криві стрілки (обидва напрями пари — однаковий bow → різні боки) ──
    edges = [
        (C, X, P[0][1], 30, 0),   # С→Х
        (X, C, P[1][0], 30, 1),   # Х→С
        (C, D, P[0][2], 30, 0),   # С→Д
        (D, C, P[2][0], 30, 2),   # Д→С
        (X, D, P[1][2], 30, 1),   # Х→Д
        (D, X, P[2][1], 30, 2),   # Д→Х
    ]
    labels = []
    for a, b, prob, bow, ci in edges:
        svg, lp = carrow(a, b, r, bow, color="#5b6472", sw=1.8)
        frags.append(svg)
        labels.append((lp, "%.1f" % prob, COL[ci]))

    # петлі
    lo, lp = selfloop(C, r, "up", color="#5b6472");  frags.append(lo); labels.append((lp, "%.1f" % P[0][0], COL[0]))
    lo, lp = selfloop(X, r, "up", color="#5b6472");  frags.append(lo); labels.append((lp, "%.1f" % P[1][1], COL[1]))
    lo, lp = selfloop(D, r, "down", color="#5b6472"); frags.append(lo); labels.append((lp, "%.1f" % P[2][2], COL[2]))

    # кружечки станів — поверх ліній
    frags.append(statecircle(C, 0, r))
    frags.append(statecircle(X, 1, r))
    frags.append(statecircle(D, 2, r))
    # плашки з ймовірностями — поверх усього
    for lp, s, col in labels:
        frags.append(problabel(lp, s, col))

    # ── матриця праворуч ──
    mx0 = 560
    my0 = 120
    cellw, cellh = 52, 40
    # заголовки стовпців
    for j in range(3):
        frags.append(text(mx0 + 34 + j * cellw + cellw / 2, my0 - 8, LABELS[j],
                          14, COL[j], "middle", bold=True))
    # дужки матриці
    bx0 = mx0 + 28
    bx1 = mx0 + 34 + 3 * cellw + 4
    by0 = my0
    by1 = my0 + 3 * cellh
    for bxx, sgn in ((bx0, 1), (bx1, -1)):
        frags.append(line(bxx, by0, bxx + 8 * sgn, by0, color=INK, sw=2))
        frags.append(line(bxx, by0, bxx, by1, color=INK, sw=2))
        frags.append(line(bxx, by1, bxx + 8 * sgn, by1, color=INK, sw=2))
    for i in range(3):
        # мітка рядка
        frags.append(text(mx0 + 6, my0 + i * cellh + cellh / 2 + 5, LABELS[i],
                          14, COL[i], "middle", bold=True))
        for j in range(3):
            cx = mx0 + 34 + j * cellw + cellw / 2
            cy = my0 + i * cellh + cellh / 2 + 5
            hot = (i == j)
            frags.append(text(cx, cy, "%.1f" % P[i][j], 14.5,
                              INK if not hot else COL[i], "middle", bold=hot))
    # підпис «рядок = 1»
    frags.append(text(mx0 + 34 + 1.5 * cellw, by1 + 30,
                      "кожен рядок → сума = 1", 12, FIELD, "middle", bold=True))

    render(os.path.join(OUT, "transition-graph.svg"), W, H, *frags,
           title="Матриця переходів")


# ── Фігура 2: збіжність до стаціонарного розподілу ───────────────────────────
def fig_convergence():
    W, H = 760, 470
    N = 10
    x0, x1 = 78, 660
    y0, y1 = 66, 392            # верх (prob=1) .. низ (prob=0)
    frags = []

    def X(n): return x0 + (x1 - x0) * n / N
    def Y(p): return y1 - (y1 - y0) * p

    # осі
    frags.append(line(x0, y0 - 6, x0, y1, color=INK, sw=1.6))
    frags.append(line(x0, y1, x1 + 8, y1, color=INK, sw=1.6))
    # сітка й підписи осі y
    for p in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
        yy = Y(p)
        frags.append(line(x0, yy, x1, yy, color="#eef1f4", sw=1.0))
        frags.append(text(x0 - 12, yy + 4, "%.1f" % p, 11, MUTED, "end"))
    # підписи осі x
    for n in range(0, N + 1, 2):
        frags.append(line(X(n), y1, X(n), y1 + 5, color=MUTED, sw=1.0))
        frags.append(text(X(n), y1 + 19, str(n), 11, MUTED, "middle"))
    frags.append(text((x0 + x1) / 2, y1 + 40, "крок (день)", 12, INK, "middle"))
    frags.append(text(x0 - 44, (y0 + y1) / 2, "ймовірність", 12, INK, "middle"))
    # повернути вертикальний підпис осі y
    frags[-1] = ('<text x="%.1f" y="%.1f" font-family="%s" font-size="12" fill="%s" '
                 'text-anchor="middle" transform="rotate(-90 %.1f %.1f)">ймовірність стану</text>'
                 % (x0 - 46, (y0 + y1) / 2, FONT, INK, x0 - 46, (y0 + y1) / 2))

    # стаціонарні рівні
    star = [6 / 13, 4 / 13, 3 / 13]
    for idx in range(3):
        yy = Y(star[idx])
        frags.append(line(x0, yy, x1, yy, color=COL[idx], sw=1.2, dash="2,4"))
        frags.append(text(x1 + 14, yy + 4, "%d/13" % [6, 4, 3][idx], 11.5, COL[idx], "start", bold=True))

    # траєкторії від двох стартів
    def traj(start):
        seq = [start[:]]
        for _ in range(N):
            seq.append(step(seq[-1]))
        return seq

    starts = [([0.0, 0.0, 1.0], None, "старт: дощ"),          # суцільна
              ([1.0, 0.0, 0.0], "5,4", "старт: сонце")]        # пунктирна
    for start, dash, _ in starts:
        seq = traj(start)
        for idx in range(3):
            pts = " ".join("%.1f,%.1f" % (X(n), Y(seq[n][idx])) for n in range(N + 1))
            d = ' stroke-dasharray="%s"' % dash if dash else ''
            frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.3"%s/>'
                         % (pts, COL[idx], d))
            # точки
            for n in range(N + 1):
                frags.append(circle(X(n), Y(seq[n][idx]), 2.4, fill=COL[idx], stroke=COL[idx], sw=0.6))

    # легенда
    ly = y0 + 8
    lx = x1 - 168
    frags.append(rect(lx - 10, ly - 16, 176, 92, fill="#ffffff", stroke="#dfe3e8", sw=1.0, rx=7))
    frags.append(line(lx, ly, lx + 26, ly, color=INK, sw=2.3))
    frags.append(text(lx + 34, ly + 4, "старт: дощ", 11.5, INK, "start"))
    frags.append(line(lx, ly + 20, lx + 26, ly + 20, color=INK, sw=2.3, dash="5,4"))
    frags.append(text(lx + 34, ly + 24, "старт: сонце", 11.5, INK, "start"))
    for k, idx in enumerate((0, 1, 2)):
        yy = ly + 44 + k * 15
        frags.append(rect(lx, yy - 7, 14, 9, fill=COL[idx], stroke=COL[idx], sw=1, rx=2))
        frags.append(text(lx + 22, yy + 1, {0: "Сонячно", 1: "Хмарно", 2: "Дощ"}[idx], 11, INK, "start"))

    render(os.path.join(OUT, "convergence.svg"), W, H, *frags,
           title="Різні старти сходяться в один стаціонарний розподіл")


# ── Фігура 3: коли рівновага існує, а коли ні ────────────────────────────────
def fig_conditions():
    W, H = 800, 356
    pw = 250
    gap = 14
    x0 = 18
    top = 58
    frags = []

    def panel(px, head, sub, subcol):
        frags.append(rect(px, top, pw, 250, fill="#fcfdfe", stroke="#dfe3e8", sw=1.2, rx=10))
        frags.append(text(px + pw / 2, top + 24, head, 13.5, INK, "middle", bold=True))
        frags.append(text(px + pw / 2, top + 232, sub, 11.5, subcol, "middle", bold=True))

    r = 24
    # Панель 1: незвідний + аперіодичний → одна рівновага
    p1 = x0
    panel(p1, "Незвідний, аперіодичний", "сходиться до одного π*", FIELD)
    A = (p1 + 78, top + 108)
    B = (p1 + 172, top + 96)
    Cc = (p1 + 125, top + 176)
    sv, lp = carrow(A, B, r, 22, "#5b6472", 1.7); frags.append(sv)
    sv, lp = carrow(B, Cc, r, 22, "#5b6472", 1.7); frags.append(sv)
    sv, lp = carrow(Cc, A, r, 22, "#5b6472", 1.7); frags.append(sv)
    sv, lp = carrow(B, A, r, 22, "#5b6472", 1.7); frags.append(sv)
    sv, lp = selfloop(A, r, "up", "#5b6472", 1.7); frags.append(sv)  # петля = аперіодичність
    for nd in (A, B, Cc):
        frags.append(circle(nd[0], nd[1], r, fill="#ffffff", stroke=FIELD, sw=2.4))
    frags.append(text(A[0], A[1] + 5, "1", 15, FIELD, "middle", bold=True))
    frags.append(text(B[0], B[1] + 5, "2", 15, FIELD, "middle", bold=True))
    frags.append(text(Cc[0], Cc[1] + 5, "3", 15, FIELD, "middle", bold=True))
    frags.append(text(A[0] - 4, top + 60, "петля", 10.5, FIELD, "middle"))

    # Панель 2: період 2 → вічне коливання
    p2 = x0 + pw + gap
    panel(p2, "Період 2", "коливається, не завмирає", POS)
    A2 = (p2 + 74, top + 132)
    B2 = (p2 + 176, top + 132)
    sv, lp = carrow(A2, B2, r, 30, "#5b6472", 1.9); frags.append(sv)
    frags.append(problabel(lp, "1.0", POS))
    sv, lp = carrow(B2, A2, r, 30, "#5b6472", 1.9); frags.append(sv)
    frags.append(problabel(lp, "1.0", POS))
    for nd, t in ((A2, "L"), (B2, "R")):
        frags.append(circle(nd[0], nd[1], r, fill="#ffffff", stroke=POS, sw=2.4))
        frags.append(text(nd[0], nd[1] + 5, t, 15, POS, "middle", bold=True))
    frags.append(text(p2 + pw / 2, top + 196, "щокроку — обов'язково", 10.5, MUTED, "middle"))
    frags.append(text(p2 + pw / 2, top + 210, "в сусідній стан", 10.5, MUTED, "middle"))

    # Панель 3: поглинальний стан → пастка
    p3 = x0 + 2 * (pw + gap)
    panel(p3, "Поглинальний стан", "старт вирішує долю", NEG)
    S = (p3 + 66, top + 96)
    M = (p3 + 66, top + 168)
    T = (p3 + 176, top + 132)
    sv, lp = carrow(S, M, r, 18, "#5b6472", 1.7); frags.append(sv)
    sv, lp = carrow(M, T, r, 18, "#5b6472", 1.7); frags.append(sv)
    sv, lp = carrow(S, T, r, 18, "#5b6472", 1.7); frags.append(sv)
    sv, lp = selfloop(T, r, "up", NEG, 2.1); frags.append(sv)
    frags.append(problabel((T[0], top + 70), "1.0", NEG))
    for nd, col in ((S, "#5b6472"), (M, "#5b6472")):
        frags.append(circle(nd[0], nd[1], r, fill="#ffffff", stroke=MUTED, sw=2.2))
    frags.append(text(S[0], S[1] + 5, "A", 14, INK, "middle", bold=True))
    frags.append(text(M[0], M[1] + 5, "B", 14, INK, "middle", bold=True))
    frags.append(circle(T[0], T[1], r, fill="#eaf0fd", stroke=NEG, sw=2.6))
    frags.append(text(T[0], T[1] + 5, "пастка", 10.5, NEG, "middle", bold=True))

    render(os.path.join(OUT, "conditions.svg"), W, H, *frags,
           title="Коли рівновага одна, а коли її нема")


# ═══════════════════════════════════════════════════════════════════════════
#  PageRank (вставка proj-pagerank): наскрізний веб-граф із 4 сторінок
#  A→B,C ; B→C,D ; C→A ; D — тупик (жодного виходу).
# ═══════════════════════════════════════════════════════════════════════════
PR_OUT = [[1, 2], [2, 3], [0], []]         # список виходів кожної сторінки
PR_LAB = ["A", "B", "C", "D"]
PR_COL = {0: "#2457d6", 1: "#27ae60", 2: "#d98a00", 3: "#c0392b"}  # A синій, B зелений, C бурштин, D червоний (тупик)


def pr_iterate(out, d=0.85, steps=40, handle_dangling=True):
    """Степенева ітерація πₙ₊₁ = πₙ·G. Повертає список розподілів по кроках."""
    N = len(out)
    pi = [1.0 / N] * N
    seq = [pi[:]]
    for _ in range(steps):
        new = [(1.0 - d) / N] * N
        dang = 0.0
        for i in range(N):
            if out[i]:
                sh = d * pi[i] / len(out[i])
                for j in out[i]:
                    new[j] += sh
            elif handle_dangling:
                dang += pi[i]
        if handle_dangling:
            add = d * dang / N
            new = [x + add for x in new]
        pi = new
        seq.append(pi[:])
    return seq


def _pr_graph(frags, ox, oy, r=25, dead=True):
    """Малює наскрізний веб-граф із центром-зсувом (ox,oy). Повертає позиції вузлів."""
    A = (ox + 0, oy + 0)
    B = (ox + 150, oy + 0)
    C = (ox + 0, oy + 150)
    D = (ox + 150, oy + 150)
    pos = [A, B, C, D]
    # ребра: A→B, A→C, B→C, B→D, C→A
    for a, b, bow in [(A, B, 18), (A, C, 18), (B, C, 20), (B, D, 18), (C, A, 18)]:
        sv, _ = carrow(a, b, r, bow, "#8a93a0", 1.8)
        frags.append(sv)
    for k, p in enumerate(pos):
        deadk = dead and k == 3
        col = PR_COL[k]
        frags.append(circle(p[0], p[1], r, fill="#ffffff",
                            stroke=col, sw=2.6 if not deadk else 3.0))
        frags.append(text(p[0], p[1] + 6, PR_LAB[k], 17, col, "middle", bold=True))
    if dead:
        frags.append(text(D[0], D[1] + r + 16, "тупик", 11, PR_COL[3], "middle", bold=True))
    return pos


# ── Фігура PR-1: демпфування (телепортація) ──────────────────────────────────
def fig_pr_teleport():
    W, H = 820, 452
    frags = []
    frags.append(text(W / 2, 48, "Із кожної сторінки — або за посиланням, або стрибок навмання",
                      13.5, MUTED, "middle"))

    # ── ліва колонка: два правила блукача ──
    sx = 150                      # центр «джерел» зліва
    lx = 560                      # центр «наслідків» справа
    # правило 1: звичайна сторінка
    b1, w1, h1 = textbox(sx, 118, "Звичайна\nсторінка i", 14, pad=12,
                         fill="#eef2fb", stroke=PR_COL[0], color=PR_COL[0], bold=True)
    frags.append(b1)
    t_link, wl, hl = textbox(lx, 96, "випадкове посилання\nзі сторінки i", 12.5, pad=11,
                             fill=FILL, stroke=LINE)
    frags.append(t_link)
    t_tel, wt, ht = textbox(lx, 190, "будь-яка з усіх N\nсторінок (телепорт)", 12.5, pad=11,
                            fill="#fdf3e7", stroke=PR_COL[2])
    frags.append(t_tel)
    # стрілки з підписами-ймовірностями
    frags.append(arrow(sx + w1 / 2, 110, lx - wl / 2 - 2, 96, color="#5b6472", sw=2.2))
    frags.append(problabel(((sx + w1 / 2 + lx - wl / 2) / 2, 82), "d = 0.85", FIELD))
    frags.append(arrow(sx + w1 / 2, 128, lx - wt / 2 - 2, 186, color="#8a93a0", sw=1.7))
    frags.append(problabel(((sx + w1 / 2 + lx - wt / 2) / 2, 176), "1 − d = 0.15", PR_COL[2]))

    # правило 2: тупик
    b2, w2, h2 = textbox(sx, 300, "Тупик\n(0 виходів)", 14, pad=12,
                         fill="#fdeceb", stroke=PR_COL[3], color=PR_COL[3], bold=True)
    frags.append(b2)
    frags.append(arrow(sx + w2 / 2, 300, lx - wt / 2 - 2, 214, color="#8a93a0", sw=1.7))
    frags.append(problabel(((sx + w2 / 2 + lx - wt / 2) / 2, 268), "завжди (1.0)", PR_COL[3]))
    frags.append(text(sx, 300 + h2 / 2 + 20, "нема куди йти за посиланням", 11, MUTED, "middle"))

    # ── формула Google-матриці внизу ──
    fy = 374
    frags.append(rect(70, fy, W - 140, 58, fill="#f7f9fc", stroke="#dfe3e8", sw=1.2, rx=10))
    frags.append(text(W / 2, fy + 25, "G = d · S′ + (1 − d) · (1/N) · J",
                      17, INK, "middle", bold=True))
    frags.append(text(W / 2, fy + 46,
                      "S′ — посилання, нормовані по рядку (рядки-тупики замінено на 1/N);  J — усі одиниці.  Кожен рядок G → сума 1: незвідна й аперіодична.",
                      10.5, MUTED, "middle"))

    render(os.path.join(OUT, "pagerank-teleport.svg"), W, H, *frags,
           title="Демпфування робить ланцюг вебу ергодичним")


# ── Фігура PR-2: ранг витікає крізь тупик ────────────────────────────────────
def fig_pr_leak():
    W, H = 840, 430
    x0, x1 = 96, 560
    y0, y1 = 74, 340
    STEPS = 12
    frags = []

    def X(n): return x0 + (x1 - x0) * n / STEPS
    def Y(p): return y1 - (y1 - y0) * (p - 0.4) / 0.65     # шкала 0.40..1.05

    # осі + сітка
    frags.append(line(x0, y0 - 8, x0, y1, INK, 1.6))
    frags.append(line(x0, y1, x1 + 8, y1, INK, 1.6))
    for p in (0.4, 0.6, 0.8, 1.0):
        yy = Y(p)
        frags.append(line(x0, yy, x1, yy, "#eef1f4", 1.0))
        frags.append(text(x0 - 12, yy + 4, "%.1f" % p, 11, MUTED, "end"))
    for n in range(0, STEPS + 1, 2):
        frags.append(line(X(n), y1, X(n), y1 + 5, MUTED, 1.0))
        frags.append(text(X(n), y1 + 20, str(n), 11, MUTED, "middle"))
    frags.append(text((x0 + x1) / 2, y1 + 42, "крок ітерації", 12, INK, "middle"))
    frags.append(('<text x="%.1f" y="%.1f" font-family="%s" font-size="12" fill="%s" '
                  'text-anchor="middle" transform="rotate(-90 %.1f %.1f)">сумарна маса Σπ</text>'
                  % (x0 - 52, (y0 + y1) / 2, FONT, INK, x0 - 52, (y0 + y1) / 2)))

    # з телепортом: маса тримається на 1
    frags.append(line(x0, Y(1.0), x1, Y(1.0), FIELD, 2.6))
    frags.append(text(x1 + 14, Y(1.0) + 4, "1.0", 11.5, FIELD, "start", bold=True))

    # без обробки тупиків: маса стікає
    seq = pr_iterate(PR_OUT, steps=STEPS, handle_dangling=False)
    mass = [sum(v) for v in seq]
    pts = " ".join("%.1f,%.1f" % (X(n), Y(mass[n])) for n in range(STEPS + 1))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (pts, PR_COL[3]))
    for n in range(STEPS + 1):
        frags.append(circle(X(n), Y(mass[n]), 2.6, fill=PR_COL[3], stroke=PR_COL[3], sw=0.6))
    frags.append(text(X(STEPS) + 14, Y(mass[STEPS]) + 4, "%.2f" % mass[STEPS], 11.5, PR_COL[3], "start", bold=True))

    # легенда
    lx, ly = 150, 108
    frags.append(rect(lx - 12, ly - 18, 300, 66, fill="#ffffff", stroke="#dfe3e8", sw=1.0, rx=8))
    frags.append(line(lx, ly, lx + 26, ly, FIELD, 2.6))
    frags.append(text(lx + 34, ly + 4, "телепорт із тупика: маса = 1 завжди", 11.5, INK, "start"))
    frags.append(line(lx, ly + 24, lx + 26, ly + 24, PR_COL[3], 2.8))
    frags.append(text(lx + 34, ly + 28, "без обробки: ранг витікає крізь D", 11.5, INK, "start"))

    # маленький граф-нагадування праворуч
    _pr_graph(frags, 650, 150, r=20)

    render(os.path.join(OUT, "pagerank-leak.svg"), W, H, *frags,
           title="Глухий кут зливає ймовірність, якщо його не полагодити")


# ── Фігура PR-3: степенева ітерація сходиться, ранжування проступає ───────────
def fig_pr_converge():
    W, H = 820, 440
    x0, x1 = 82, 520
    y0, y1 = 72, 350
    STEPS = 14
    frags = []

    def X(n): return x0 + (x1 - x0) * n / STEPS
    def Y(p): return y1 - (y1 - y0) * p / 0.40      # шкала 0..0.40

    frags.append(line(x0, y0 - 8, x0, y1, INK, 1.6))
    frags.append(line(x0, y1, x1 + 8, y1, INK, 1.6))
    for p in (0.0, 0.1, 0.2, 0.3, 0.4):
        yy = Y(p)
        frags.append(line(x0, yy, x1, yy, "#eef1f4", 1.0))
        frags.append(text(x0 - 12, yy + 4, "%.1f" % p, 11, MUTED, "end"))
    for n in range(0, STEPS + 1, 2):
        frags.append(line(X(n), y1, X(n), y1 + 5, MUTED, 1.0))
        frags.append(text(X(n), y1 + 20, str(n), 11, MUTED, "middle"))
    frags.append(text((x0 + x1) / 2, y1 + 42, "крок ітерації", 12, INK, "middle"))
    frags.append(('<text x="%.1f" y="%.1f" font-family="%s" font-size="12" fill="%s" '
                  'text-anchor="middle" transform="rotate(-90 %.1f %.1f)">PageRank сторінки</text>'
                  % (x0 - 50, (y0 + y1) / 2, FONT, INK, x0 - 50, (y0 + y1) / 2)))

    seq = pr_iterate(PR_OUT, steps=STEPS, handle_dangling=True)
    final = seq[-1]
    # криві по сторінках
    for k in range(4):
        pts = " ".join("%.1f,%.1f" % (X(n), Y(seq[n][k])) for n in range(STEPS + 1))
        frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (pts, PR_COL[k]))
        for n in range(STEPS + 1):
            frags.append(circle(X(n), Y(seq[n][k]), 2.2, fill=PR_COL[k], stroke=PR_COL[k], sw=0.5))
        frags.append(text(x1 + 13, Y(final[k]) + 4, PR_LAB[k], 12.5, PR_COL[k], "start", bold=True))

    # анотація швидкості (над сіткою, щоб лінії не перетинали напис)
    frags.append(text((x0 + x1) / 2, y0 - 18,
                      "похибка ×0.85 щокроку  (λ₂ = d)", 12, MUTED, "middle", italic=True))

    # ── праворуч: підсумкове ранжування стовпчиками ──
    rx0 = 596
    bw = 150
    order = sorted(range(4), key=lambda i: -final[i])
    frags.append(text(rx0 + bw / 2, y0 - 4, "усталене ранжування", 12, INK, "middle", bold=True))
    top = final[order[0]]
    for rank, k in enumerate(order):
        by = y0 + 26 + rank * 62
        frags.append(text(rx0 - 6, by + 20, PR_LAB[k], 15, PR_COL[k], "end", bold=True))
        full = bw * final[k] / top
        frags.append(rect(rx0, by, full, 30, fill=PR_COL[k], stroke=PR_COL[k], sw=1, rx=5))
        frags.append(text(rx0 + full + 8, by + 20, "%.3f" % final[k], 12, INK, "start", bold=True))
    frags.append(text(rx0 + bw / 2, y0 + 26 + 4 * 62 + 2,
                      "A > C > B > D", 13, INK, "middle", bold=True))
    frags.append(text(rx0 + bw / 2, y0 + 26 + 4 * 62 + 22,
                      "не «хто має більше посилань»,", 10.5, MUTED, "middle"))
    frags.append(text(rx0 + bw / 2, y0 + 26 + 4 * 62 + 37,
                      "а «звідки вони приходять»", 10.5, MUTED, "middle"))

    render(os.path.join(OUT, "pagerank-converge.svg"), W, H, *frags,
           title="Женемо πₙ₊₁ = πₙ·G, поки не завмре")


# ── Фігура (вставка hist-markov): Онєгін — розрив, якого «незалежність» не дає ─
def fig_onegin():
    W, H = 820, 452
    frags = []
    frags.append(text(W / 2, 50,
                      "Шанс, що наступна літера — голосна, залежно від попередньої",
                      13, MUTED, "middle"))

    COLV = NEG   # після голосної — холодний синій
    COLC = POS   # після приголосної — гарячий червоний

    top = 78
    baseY = 372
    pmax = 0.75
    plotH = baseY - (top + 60)
    def Y(p): return baseY - (p / pmax) * plotH

    pw = 336
    panels = [
        (46,  "Якби літери були незалежні", "(гіпотеза Некрасова)",
         0.432, 0.432, "однакові — минуле не важить", FIELD),
        (438, "Що Марков полічив у Пушкіна", "(20 000 літер, вручну)",
         0.128, 0.663, "різні вп'ятеро — літери залежні", POS),
    ]
    for px, head, sub, va, vc, note, ncol in panels:
        frags.append(rect(px, top, pw, baseY - top + 58, fill="#fcfdfe",
                          stroke="#dfe3e8", sw=1.1, rx=10))
        frags.append(text(px + pw / 2, top + 22, head, 13.5, INK, "middle", bold=True))
        frags.append(text(px + pw / 2, top + 40, sub, 11, MUTED, "middle"))
        # базова лінія та орієнтир 0.432 (узагалі частка голосних)
        frags.append(line(px + 22, baseY, px + pw - 22, baseY, INK, 1.6))
        yref = Y(0.432)
        frags.append(line(px + 22, yref, px + pw - 22, yref, MUTED, 1.1, dash="4,4"))
        frags.append(text(px + pw - 26, yref - 7, "0.432", 10.5, MUTED, "end"))
        # два стовпчики
        bw = 84
        cols = [(px + 96, va, COLV, "після\nголосної"),
                (px + 240, vc, COLC, "після\nприголосної")]
        for cx, v, col, lab in cols:
            yv = Y(v)
            frags.append(rect(cx - bw / 2, yv, bw, baseY - yv, fill=col, stroke=col, sw=1, rx=3))
            frags.append(text(cx, yv - 9, "%.3f" % v, 13, col, "middle", bold=True))
            frags.append(mtext(cx, baseY + 18, lab, 11, INK, "middle", lh=1.15))
        frags.append(text(px + pw / 2, baseY + 52, note, 11.5, ncol, "middle", bold=True))

    render(os.path.join(OUT, "onegin-dependence.svg"), W, H, *frags,
           title="Онєгін: розрив, якого «незалежність» не передбачає")


# ═══════════════════════════════════════════════════════════════════════════
#  Вставка math-stationary: Перрон–Фробеніус, спектральна щілина, симплекс
# ═══════════════════════════════════════════════════════════════════════════

# ── Фігура MS-1: спектр стохастичної матриці в одиничному крузі ───────────────
def fig_spectrum():
    W, H = 820, 424
    cy = 246
    R = 104
    frags = [text(W / 2, 30, "Де живуть власні значення стохастичної матриці",
                  15, INK, "middle", bold=True)]

    def axes(cx):
        f = [line(cx - R - 26, cy, cx + R + 26, cy, MUTED, 1.1),
             line(cx, cy - R - 22, cx, cy + R + 22, MUTED, 1.1),
             text(cx + R + 32, cy + 4, "Re", 11, MUTED, "start"),
             text(cx + 11, cy - R - 24, "Im", 11, MUTED, "start")]
        return f

    def eig_dot(cx, frac, col):
        return circle(cx + frac * R, cy, 6, fill=col, stroke=col, sw=1)

    # ── ліва панель: погода (примітивна) ──
    lc = 224
    frags.append(text(lc, cy - R - 40, "Погода — примітивна", 13.5, INK, "middle", bold=True))
    # спектральна щілина: кільце між λ₂·R і R
    frags.append(circle(lc, cy, R, fill="#e8f0fb", stroke="none"))
    frags.append(circle(lc, cy, 0.456 * R, fill=BG, stroke="none"))
    frags.extend(axes(lc))
    frags.append(circle(lc, cy, R, fill="none", stroke=INK, sw=1.8))
    # брекет щілини над віссю
    gx0, gx1, gy = lc + 0.456 * R, lc + R, cy - 22
    frags.append(line(gx0, gy, gx1, gy, MUTED, 1.2))
    frags.append(line(gx0, gy - 4, gx0, gy + 4, MUTED, 1.2))
    frags.append(line(gx1, gy - 4, gx1, gy + 4, MUTED, 1.2))
    frags.append(text((gx0 + gx1) / 2, gy - 8, "щілина 1−|λ₂| = 0.544", 10.5, MUTED, "middle"))
    # власні значення
    frags.append(eig_dot(lc, 1.0, FIELD))
    frags.append(eig_dot(lc, 0.456, NEG))
    frags.append(eig_dot(lc, 0.044, NEG))
    frags.append(text(lc + R + 4, cy + 20, "λ₁=1", 11.5, FIELD, "middle", bold=True))
    frags.append(text(lc + 0.456 * R, cy + 26, "λ₂=0.456", 11, NEG, "middle", bold=True))
    frags.append(line(lc + 0.044 * R, cy + 6, lc - 0.16 * R, cy + 30, MUTED, 0.9))
    frags.append(text(lc - 0.30 * R, cy + 38, "λ₃=0.044", 11, NEG, "middle", bold=True))
    frags.append(text(lc, cy + R + 26, "1 на межі, решта строго всередині → сходиться",
                      11, FIELD, "middle", bold=True))

    # ── права панель: дві кімнати (період 2) ──
    rc = 600
    frags.append(text(rc, cy - R - 40, "Дві кімнати — період 2", 13.5, INK, "middle", bold=True))
    frags.extend(axes(rc))
    frags.append(circle(rc, cy, R, fill="none", stroke=INK, sw=1.8))
    frags.append(eig_dot(rc, 1.0, FIELD))
    frags.append(eig_dot(rc, -1.0, POS))
    frags.append(text(rc + R + 2, cy + 20, "+1", 11.5, FIELD, "middle", bold=True))
    frags.append(text(rc - R - 2, cy + 20, "−1", 11.5, POS, "middle", bold=True))
    frags.append(text(rc, cy - R - 6, "|−1|ⁿ = 1 — не згасає", 11, POS, "middle", bold=True))
    frags.append(text(rc, cy + R + 26, "друге значення на колі → вічне коливання",
                      11, POS, "middle", bold=True))

    render(os.path.join(OUT, "spectrum.svg"), W, H, *frags)


# ── Фігура MS-2: геометрична збіжність на напівлогарифмічній шкалі ────────────
def fig_geometric_decay():
    W, H = 760, 430
    x0, x1 = 96, 636
    y0, y1 = 74, 350                      # y0: похибка 1 ; y1: похибка 0.001
    N = 10
    frags = [text(W / 2, 30, "Геометричне згасання — пряма на логарифмічній шкалі",
                  15, INK, "middle", bold=True)]

    def X(n): return x0 + (x1 - x0) * n / N
    def Y(e): return y0 + (y1 - y0) * min(1.0, (-math.log10(e)) / 3.0)

    # осі
    frags.append(line(x0, y0 - 6, x0, y1, INK, 1.6))
    frags.append(line(x0, y1, x1 + 8, y1, INK, 1.6))
    # сітка по декадах
    for e, lab in [(1.0, "1"), (0.1, "0.1"), (0.01, "0.01"), (0.001, "0.001")]:
        yy = Y(e)
        frags.append(line(x0, yy, x1, yy, "#eef1f4", 1.0))
        frags.append(text(x0 - 12, yy + 4, lab, 11, MUTED, "end"))
    for n in range(0, N + 1, 2):
        frags.append(line(X(n), y1, X(n), y1 + 5, MUTED, 1.0))
        frags.append(text(X(n), y1 + 19, str(n), 11, MUTED, "middle"))
    frags.append(text((x0 + x1) / 2, y1 + 40, "крок n", 12, INK, "middle"))
    frags.append(('<text x="%.1f" y="%.1f" font-family="%s" font-size="12" fill="%s" '
                  'text-anchor="middle" transform="rotate(-90 %.1f %.1f)">'
                  'відхилення ‖πₙ − π*‖ (лог. шкала)</text>'
                  % (x0 - 52, (y0 + y1) / 2, FONT, INK, x0 - 52, (y0 + y1) / 2)))

    # похибки наскрізного прикладу від дощового старту
    star = [6 / 13, 4 / 13, 3 / 13]
    we, v = [], [0.0, 0.0, 1.0]
    for _ in range(N + 1):
        we.append(abs(v[0] - star[0])); v = step(v)
    # ланцюг із вужчою щілиною (λ₂ = 0.9) для контрасту
    sl = [we[0] * 0.9 ** n for n in range(N + 1)]

    def plot(vals, upto, col, dash=None, sw=2.6):
        pts = " ".join("%.1f,%.1f" % (X(n), Y(vals[n])) for n in range(upto + 1))
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
                     % (pts, col, sw, d))
        for n in range(upto + 1):
            frags.append(circle(X(n), Y(vals[n]), 2.6, fill=col, stroke=col, sw=0.6))

    plot(sl, N, MUTED, dash="6,5", sw=2.2)         # пологий: λ₂ = 0.9
    plot(we, 8, POS)                                # крутий: погода λ₂ = 0.456

    # підписи ліній
    frags.append(text(X(9) + 6, Y(sl[9]) + 4, "λ₂ = 0.9", 11.5, MUTED, "start", bold=True))
    frags.append(text(X(9) + 6, Y(sl[9]) + 18, "(вужча щілина)", 10, MUTED, "start"))
    frags.append(text(X(5.4), Y(we[5]) - 12, "погода: λ₂ = 0.456", 11.5, POS, "middle", bold=True))
    frags.append(text(X(5.4), Y(we[5]) + 4, "нахил = log|λ₂|", 10.5, POS, "middle"))
    # орієнтир «×1000 за ~9 кроків»
    frags.append(text(X(8.6), y1 - 8, "×1000 за ~9 кроків", 10, INK, "middle", italic=True))

    render(os.path.join(OUT, "geometric-decay.svg"), W, H, *frags)


# ── Фігура MS-3: симплекс розподілів стискається до нерухомої точки ───────────
def fig_simplex():
    W, H = 640, 452
    Vc, Vx, Vd = (300, 82), (72, 360), (528, 360)
    frags = [text(W / 2, 32, "Крок ланцюга стискає трикутник розподілів до π*",
                  15, INK, "middle", bold=True)]

    def xy(b):
        return (b[0] * Vc[0] + b[1] * Vx[0] + b[2] * Vd[0],
                b[0] * Vc[1] + b[1] * Vx[1] + b[2] * Vd[1])

    # ребра трикутника
    for a, b in [(Vc, Vx), (Vx, Vd), (Vd, Vc)]:
        frags.append(line(a[0], a[1], b[0], b[1], "#c9ced6", 1.6))

    star = [6 / 13, 4 / 13, 3 / 13]
    ps = xy(star)

    # повільний власний напрям u₂: емпірично як відхилення після кількох кроків
    v = [1.0, 0.0, 0.0]
    for _ in range(5):
        v = step(v)
    d = [v[i] - star[i] for i in range(3)]
    m = max(abs(x) for x in d) or 1.0
    d = [x / m for x in d]
    a_plus = xy([star[i] + 0.42 * d[i] for i in range(3)])
    a_minus = xy([star[i] - 0.42 * d[i] for i in range(3)])
    frags.append(line(a_minus[0], a_minus[1], a_plus[0], a_plus[1], POS, 1.6, dash="6,5"))
    frags.append(text(a_plus[0] + 6, a_plus[1] + 4, "u₂", 12.5, POS, "start", bold=True))

    # траєкторії з кількох стартів
    starts = [[1, 0, 0], [0, 1, 0], [0, 0, 1],
              [0.5, 0.5, 0], [0.5, 0, 0.5], [0, 0.5, 0.5]]
    for s in starts:
        seq = [s[:]]
        for _ in range(9):
            seq.append(step(seq[-1]))
        pts = " ".join("%.1f,%.1f" % xy(p) for p in seq)
        frags.append('<polyline points="%s" fill="none" stroke="#95a0b0" stroke-width="1.7"/>' % pts)
        for p in seq[1:]:
            q = xy(p)
            frags.append(circle(q[0], q[1], 1.8, fill="#95a0b0", stroke="#95a0b0", sw=0.4))
        q0 = xy(s)
        frags.append(circle(q0[0], q0[1], 3.4, fill=BG, stroke="#5b6472", sw=1.6))

    # нерухома точка π*
    frags.append(circle(ps[0], ps[1], 7, fill=FIELD, stroke="#ffffff", sw=1.8))
    frags.append(text(ps[0] + 12, ps[1] - 8, "π*", 14, FIELD, "start", bold=True))
    frags.append(text(ps[0] + 12, ps[1] + 8, "(6/13, 4/13, 3/13)", 10.5, MUTED, "start"))

    # вершини = чисті стани
    for V, idx, dx, dy, anch in [(Vc, 0, 0, -16, "middle"), (Vx, 1, -18, 6, "end"), (Vd, 2, 18, 6, "start")]:
        frags.append(circle(V[0], V[1], 6, fill="#ffffff", stroke=COL[idx], sw=2.4))
        frags.append(text(V[0] + dx, V[1] + dy, LABELS[idx], 14, COL[idx], anch, bold=True))
    frags.append(text(W / 2, 430, "кожен старт (порожні кружечки) сповзає до π*, вирівнюючись на повільний напрям u₂",
                      11, MUTED, "middle"))

    render(os.path.join(OUT, "simplex.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_transition_graph()
    fig_convergence()
    fig_conditions()
    fig_pr_teleport()
    fig_pr_leak()
    fig_pr_converge()
    fig_onegin()
    fig_spectrum()
    fig_geometric_decay()
    fig_simplex()
    print("Done.")
