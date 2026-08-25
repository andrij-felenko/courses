# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Палітра за значенням підзадачі fib(k): однакові k — однаковий колір,
# щоб повторення в дереві було видно оком.
KCOL = {
    0: "#9ca3af",  # сірий
    1: "#f59e0b",  # бурштин
    2: "#c0392b",  # червоний (тричі!)
    3: "#2457d6",  # синій (двічі)
    4: "#27ae60",  # зелений
    5: "#7c3aed",  # фіолет
}
HIT   = "#27ae60"   # швидкий шлях / кеш-влучання
MISS  = "#c0392b"   # обчислення / кеш-схиблення
NAIVE = "#c0392b"
MEMO  = "#27ae60"


def node(cx, cy, k, r=17):
    """Кружечок-виклик fib(k), колір за значенням k."""
    col = KCOL.get(k, INK)
    out = circle(cx, cy, r, fill="#ffffff", stroke=col, sw=2.6)
    out += text(cx, cy + 5, "F%d" % k, size=14, color=col, bold=True)
    return out


# ── ФІГУРА 1: вибух повторних обчислень vs один раз кожне ────────────────────
def fig_explosion():
    W, H = 940, 470
    p = [rect(0, 0, W, H, fill=BG, stroke="none", sw=0)]

    # ── ліва панель: наївне дерево викликів fib(5) ──
    lx, lw = 30, 540
    p.append(rect(lx, 54, lw, H - 84, fill="#fbfbfd", stroke=NAIVE, sw=1.8, rx=12))
    p.append(text(lx + lw / 2, 44, "Наївно: 15 викликів на одне число", size=15, color=NAIVE, bold=True))

    # координати вузлів дерева (локальні), рівні за глибиною
    #                       F5
    #              F4                 F3
    #        F3         F2       F2       F1
    #     F2    F1   F1   F0   F1  F0
    #   F1  F0
    x0 = lx + lw / 2
    ys = [86, 152, 218, 284, 350]
    # рівень 0
    n5 = (x0, ys[0], 5)
    # рівень 1
    n4 = (x0 - 130, ys[1], 4)
    n3a = (x0 + 130, ys[1], 3)
    # рівень 2 (під F4: F3,F2 ; під F3: F2,F1)
    n3b = (x0 - 200, ys[2], 3)
    n2a = (x0 - 60, ys[2], 2)
    n2b = (x0 + 70, ys[2], 2)
    n1a = (x0 + 200, ys[2], 1)
    # рівень 3 (під лівим F3: F2,F1 ; під лівим F2: F1,F0 ; під F2b: F1,F0)
    n2c = (x0 - 250, ys[3], 2)
    n1b = (x0 - 165, ys[3], 1)
    n1c = (x0 - 95, ys[3], 1)
    n0a = (x0 - 25, ys[3], 0)
    n1d = (x0 + 35, ys[3], 1)
    n0b = (x0 + 105, ys[3], 0)
    # рівень 4 (під F2c: F1,F0)
    n1e = (x0 - 285, ys[4], 1)
    n0c = (x0 - 215, ys[4], 0)

    edges = [
        (n5, n4), (n5, n3a),
        (n4, n3b), (n4, n2a),
        (n3a, n2b), (n3a, n1a),
        (n3b, n2c), (n3b, n1b),
        (n2a, n1c), (n2a, n0a),
        (n2b, n1d), (n2b, n0b),
        (n2c, n1e), (n2c, n0c),
    ]
    for a, b in edges:
        p.append(line(a[0], a[1] + 17, b[0], b[1] - 17, color="#c8ccd2", sw=1.6))
    for nd in [n5, n4, n3a, n3b, n2a, n2b, n1a, n2c, n1b, n1c, n0a, n1d, n0b, n1e, n0c]:
        p.append(node(nd[0], nd[1], nd[2]))

    # підпис-нотатка: скільки разів
    p.append(text(lx + lw / 2, H - 16,
                  "F2 рахується тричі,  F1 — п'ять разів  (той самий колір = повтор)",
                  size=12.5, color=MUTED))

    # ── права панель: кожне число один раз ──
    rx0, rw = lx + lw + 40, W - (lx + lw + 40) - 30
    p.append(rect(rx0, 54, rw, H - 84, fill="#fbfbfd", stroke=MEMO, sw=1.8, rx=12))
    p.append(text(rx0 + rw / 2, 44, "З пам'яттю: 6 обчислень", size=15, color=MEMO, bold=True))

    cxs = rx0 + rw / 2
    vals = [0, 1, 1, 2, 3, 5]
    yy = 100
    step = 56
    cells = []
    for k in range(6):
        cy = yy + k * step
        cells.append((cxs, cy, k, vals[k]))
    # тонкий ланцюг залежності «кожне спирається на попереднє» (ліворуч від чисел)
    for k in range(1, 6):
        y_up = cells[k - 1][1]
        y_dn = cells[k][1]
        p.append(line(cxs - 34, y_dn - 18, cxs - 34, y_up + 18, color="#c8ccd2", sw=1.6))
    for (cx, cy, k, v) in cells:
        col = KCOL.get(k, INK)
        p.append(circle(cx, cy, 20, fill="#ffffff", stroke=col, sw=2.6))
        p.append(text(cx, cy + 5, "F%d" % k, size=13, color=col, bold=True))
        p.append(text(cx + 40, cy + 5, "= %d" % v, size=14, color=INK, bold=True, anchor="start"))
    p.append(text(rx0 + rw / 2, H - 16,
                  "кожне Fk обчислено рівно раз, далі — з кеша",
                  size=12.5, color=MUTED))

    render(os.path.join(OUT, "recompute-explosion.svg"), W, H, *p)


# ── ФІГУРА 2: механізм обгортки (перевір → віддай / порахуй+збережи) ─────────
def fig_mechanism():
    W, H = 860, 340
    p = [rect(0, 0, W, H, fill=BG, stroke="none", sw=0)]
    p.append(text(W / 2, 30, "Обгортка мемоізації: один погляд у кеш", size=16, bold=True))

    cy = 150
    # 1. виклик
    b1, w1, h1 = textbox(120, cy, "виклик\nf(x)", size=15, pad=16, fill="#eef2ff", stroke=NEG, bold=True)
    p.append(b1)
    # 2. ромб-рішення «x у кеші?»
    dcx, dcy = 320, cy
    dr = 60
    diamond = ('<polygon points="%.0f,%.0f %.0f,%.0f %.0f,%.0f %.0f,%.0f" '
               'fill="#fff8e6" stroke="#f59e0b" stroke-width="2"/>'
               % (dcx, dcy - dr, dcx + dr + 14, dcy, dcx, dcy + dr, dcx - dr - 14, dcy))
    p.append(diamond)
    p.append(text(dcx, dcy - 4, "x у кеші?", size=13.5, bold=True))
    # 3. так → повернути cache[x]
    by, bw, bh = textbox(660, cy - 66, "влучив →\nповернути cache[x]", size=13.5, pad=13,
                         fill="#e9f7ef", stroke=HIT, bold=True, color="#1e7a43")
    p.append(by)
    # 4. ні → порахувати → зберегти → повернути
    bn, bnw, bnh = textbox(600, cy + 78, "порахувати f(x)", size=13.5, pad=13,
                           fill="#fdecea", stroke=MISS, bold=True, color="#a5281b")
    p.append(bn)
    bs, bsw, bsh = textbox(600, cy + 78 + 74, "зберегти cache[x] → повернути", size=12.5, pad=12,
                           fill="#f4f6f8", stroke=LINE)
    p.append(bs)

    # стрілки
    p.append(arrow(120 + w1 / 2, cy, dcx - dr - 14, cy, color=INK, sw=2))
    # так (угору-праворуч)
    p.append(arrow(dcx + dr + 14, dcy - 6, 660 - bw / 2, cy - 66 + 10, color=HIT, sw=2))
    p.append(text(500, cy - 58, "так", size=13, color=HIT, bold=True))
    # ні (вниз)
    p.append(arrow(dcx + dr + 6, dcy + 22, 600 - bnw / 2, cy + 78 - 6, color=MISS, sw=2))
    p.append(text(455, cy + 44, "ні", size=13, color=MISS, bold=True))
    # порахувати → зберегти
    p.append(arrow(600, cy + 78 + bnh / 2, 600, cy + 78 + 74 - bsh / 2, color=INK, sw=1.8))

    render(os.path.join(OUT, "memo-mechanism.svg"), W, H, *p)


# ── ФІГУРА 3: згори вниз (мемоізація) vs знизу вгору (табуляція) ─────────────
def fig_topdown_bottomup():
    W, H = 900, 430
    p = [rect(0, 0, W, H, fill=BG, stroke="none", sw=0)]

    # ── ліва панель: згори вниз ──
    lx, lw = 30, 400
    p.append(rect(lx, 56, lw, H - 92, fill="#fbfbfd", stroke=NEG, sw=1.8, rx=12))
    p.append(text(lx + lw / 2, 40, "Згори вниз — мемоізація", size=15, color=NEG, bold=True))
    cxs = lx + lw / 2
    top = 96
    step = 52
    labels = [5, 4, 3, 2, 1, 0]
    ys = [top + i * step for i in range(6)]
    for i, k in enumerate(labels):
        col = KCOL.get(k, INK)
        p.append(circle(cxs, ys[i], 19, fill="#ffffff", stroke=col, sw=2.4))
        p.append(text(cxs, ys[i] + 5, "F%d" % k, size=13, color=col, bold=True))
    # рекурсія вниз (суцільна, ліворуч від осі)
    for i in range(5):
        p.append(arrow(cxs - 22, ys[i] + 8, cxs - 22, ys[i + 1] - 8, color=INK, sw=1.8))
    p.append(text(lx + 30, top + 2 * step, "рекурсія", size=11.5, color=INK, anchor="start"))
    p.append(text(lx + 30, top + 2 * step + 15, "вниз", size=11.5, color=INK, anchor="start"))
    # кеш заповнюється на зворотному шляху (пунктир, праворуч)
    for i in range(5, 0, -1):
        p.append(arrow(cxs + 22, ys[i] - 8, cxs + 22, ys[i - 1] + 8, color=HIT, sw=1.8))
    p.append(text(lx + lw - 24, top + 2 * step, "кеш —", size=11.5, color=HIT, anchor="end"))
    p.append(text(lx + lw - 24, top + 2 * step + 15, "нагору", size=11.5, color=HIT, anchor="end"))
    p.append(text(lx + lw / 2, H - 46, "рахуємо лише потрібні клітини", size=12, color=MUTED))

    # ── права панель: знизу вгору ──
    rx0, rw = lx + lw + 40, W - (lx + lw + 40) - 30
    p.append(rect(rx0, 56, rw, H - 92, fill="#fbfbfd", stroke=FIELD, sw=1.8, rx=12))
    p.append(text(rx0 + rw / 2, 40, "Знизу вгору — табуляція", size=15, color=FIELD, bold=True))
    # рядок таблиці fib[0..5]
    cells = [0, 1, 1, 2, 3, 5]
    cw = 56
    gap = 6
    total = 6 * cw + 5 * gap
    startx = rx0 + (rw - total) / 2
    ty = 150
    for i, v in enumerate(cells):
        x = startx + i * (cw + gap)
        col = KCOL.get(i, INK)
        p.append(rect(x, ty, cw, cw, fill="#ffffff", stroke=col, sw=2.2, rx=8))
        p.append(text(x + cw / 2, ty + 24, "F%d" % i, size=12.5, color=col, bold=True))
        p.append(text(x + cw / 2, ty + 46, str(v), size=16, color=INK, bold=True))
    # стрілка порядку заповнення
    p.append(arrow(startx - 6, ty + cw + 34, startx + total + 6, ty + cw + 34, color=INK, sw=2))
    p.append(text(rx0 + rw / 2, ty + cw + 58, "заповнюємо зліва направо, циклом", size=12, color=INK))
    p.append(text(rx0 + rw / 2, H - 46, "без рекурсії; досить пам'ятати два останні", size=12, color=MUTED))

    p.append(text(W / 2, H - 20, "Обидва — динамічне програмування, різниця лише в напрямку.",
                  size=12.5, color=INK, bold=True))
    render(os.path.join(OUT, "topdown-vs-bottomup.svg"), W, H, *p)


# ── ФІГУРА 4: експоненційне vs лінійне зростання роботи ──────────────────────
def fig_growth():
    W, H = 780, 440
    p = [rect(0, 0, W, H, fill=BG, stroke="none", sw=0)]
    p.append(text(W / 2, 32, "Скільки роботи коштує fib(n)", size=16, bold=True))

    ox, oy = 90, 360      # початок осей
    aw, ah = 620, 280     # довжина осей
    # осі
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=2))       # X
    p.append(arrow(ox, oy, ox, oy - ah, color=INK, sw=2))       # Y
    p.append(text(ox + aw - 4, oy + 30, "n (яке число рахуємо)", size=12.5, color=INK, anchor="end"))
    p.append(text(ox - 30, oy - ah + 6, "виклики", size=12.5, color=INK, anchor="start"))
    p.append(text(ox - 30, oy - ah + 22, "(роботи)", size=12.5, color=MUTED, anchor="start"))

    nmax = 14
    ceil_calls = 2 * fib_pair(nmax + 1) - 1   # значення наївної кривої в кінці = стеля
    sx = aw / nmax
    sy = (ah - 30) / ceil_calls

    def fx(n):
        return ox + n * sx

    def fy(v):
        return oy - v * sy

    # наївна: 2*F(n+1)-1 — злітає до стелі
    naive_pts = [(fx(n), fy(2 * fib_pair(n + 1) - 1)) for n in range(0, nmax + 1)]
    poly = " ".join("%.1f,%.1f" % pt for pt in naive_pts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (poly, NAIVE))
    # мемоізована: n+1 обчислень — майже притиснута до осі
    memo_pts = [(fx(n), fy(n + 1)) for n in range(0, nmax + 1)]
    polym = " ".join("%.1f,%.1f" % pt for pt in memo_pts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (polym, MEMO))

    # мітки кривих у вільних зонах, поза лініями
    p.append(text(fx(3.4), oy - ah + 44, "наївно ≈ 1.618ⁿ", size=14,
                  color=NAIVE, bold=True, anchor="start"))
    p.append(text(fx(6.2), fy(7) + 26, "з пам'яттю ≈ n", size=14,
                  color=MEMO, bold=True, anchor="start"))

    # поділки X
    for n in [0, 4, 8, 12, 14]:
        p.append(line(fx(n), oy, fx(n), oy + 6, color=INK, sw=1.5))
        p.append(text(fx(n), oy + 22, str(n), size=12, color=MUTED))

    p.append(text(W / 2, H - 14,
                  "Мемоізація міняє не швидкість на відсотки, а сам клас складності.",
                  size=12.5, color=INK))
    render(os.path.join(OUT, "growth-exponential-vs-linear.svg"), W, H, *p)


def fib_pair(n):
    """Число Фібоначчі F(n), F(1)=F(2)=1, F(0)=0."""
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


# ── ФІГУРА 5 (вставка hist): шлях memo-функції в часі ────────────────────────
def fig_timeline():
    W, H = 980, 360
    p = [rect(0, 0, W, H, fill=BG, stroke="none", sw=0)]
    p.append(text(W / 2, 32, "Шлях memo-функції: від зубріння машин до @cache",
                  size=17, bold=True))

    axis_y = 188
    p.append(line(64, axis_y, 906, axis_y, color=INK, sw=2))
    p.append(arrow(906, axis_y, 924, axis_y, color=INK, sw=2))

    xs = [120, 305, 490, 675, 862]
    years = ["1943", "1961", "1968", "1992", "нині"]
    descs = [
        "Блетчлі-парк:\nМічі ламає шифр Tunny,\nзустрічає Тюрінґа",
        "MENACE: 304 сірникові\nкоробки вчаться грати\nв хрестики-нулики",
        "«Memo Functions»,\nNature 218 —\nтермін народжується",
        "Норвіґ: memoize\nу Common Lisp —\nу щоденному вжитку",
        "@cache, lru_cache,\nuseMemo — memo\nу кожній мові",
    ]
    cols = [NEG, NEG, POS, FIELD, FIELD]
    above = [True, False, True, False, True]

    bw, bh = 186, 74
    for i, x in enumerate(xs):
        col = cols[i]
        big = (i == 2)
        r = 11 if big else 8
        p.append(circle(x, axis_y, r, fill="#ffffff", stroke=col, sw=3 if big else 2.4))
        if big:
            p.append(circle(x, axis_y, 4, fill=col, stroke="none", sw=0))
        if above[i]:
            by = 52
            p.append(line(x, by + bh, x, axis_y - r, color=col, sw=1.4, dash="3,3"))
            p.append(text(x, axis_y + 27, years[i], size=15, color=col, bold=True))
        else:
            by = H - 52 - bh
            p.append(line(x, by, x, axis_y + r, color=col, sw=1.4, dash="3,3"))
            p.append(text(x, axis_y - 18, years[i], size=15, color=col, bold=True))
        p.append(fitbox(x - bw / 2, by, bw, bh, descs[i], size=12.5, pad=9,
                        fill="#fbfbfd", stroke=col, sw=1.6, color=INK))

    p.append(text(W / 2, H - 13,
                  "Ідея Мічі про машину, що вчиться на власному досвіді, дожила до буденної оптимізації.",
                  size=12.5, color=MUTED))
    render(os.path.join(OUT, "memo-timeline.svg"), W, H, *p)


# ── ФІГУРА (math): звідки 2·F(n+1)−1 — рахуємо вузли повного дерева ───────────
def fig_count_closedform():
    W, H = 980, 500
    p = [rect(0, 0, W, H, fill=BG, stroke="none", sw=0)]
    p.append(text(W / 2, 30, "Звідки 2·F(n+1) − 1: рахуємо вузли дерева fib(5)", size=16, bold=True))

    def build(k):
        return {"k": k, "kids": [] if k < 2 else [build(k - 1), build(k - 2)]}
    root = build(5)

    counter = [0]
    pos = {}

    def layout(nd, depth):
        if not nd["kids"]:
            col = counter[0]
            counter[0] += 1
            pos[id(nd)] = [col, depth]
            return col
        cols = [layout(c, depth + 1) for c in nd["kids"]]
        col = sum(cols) / len(cols)
        pos[id(nd)] = [col, depth]
        return col
    layout(root, 0)
    nleaves = counter[0]

    lx, lw = 24, 620
    p.append(rect(lx, 46, lw, H - 70, fill="#fbfbfd", stroke=LINE, sw=1.4, rx=12))
    left, right, topy, vstep = lx + 44, lx + lw - 44, 80, 76

    def PX(col):
        return left + (right - left) * (col / (nleaves - 1))

    def PY(depth):
        return topy + depth * vstep

    def draw_edges(nd):
        x1, y1 = PX(pos[id(nd)][0]), PY(pos[id(nd)][1])
        for c in nd["kids"]:
            x2, y2 = PX(pos[id(c)][0]), PY(pos[id(c)][1])
            p.append(line(x1, y1 + 14, x2, y2 - 14, color="#c8ccd2", sw=1.5))
            draw_edges(c)
    draw_edges(root)

    def draw_nodes(nd):
        col, depth = pos[id(nd)]
        x, y = PX(col), PY(depth)
        k = nd["k"]
        if not nd["kids"]:
            if k == 1:
                fill, stroke, tc = "#e9f7ef", FIELD, "#1e7a43"
            else:
                fill, stroke, tc = "#f1f3f5", MUTED, MUTED
        else:
            fill, stroke, tc = "#ffffff", INK, INK
        p.append(circle(x, y, 14, fill=fill, stroke=stroke, sw=2.2))
        p.append(text(x, y + 4, "F%d" % k, size=11, color=tc, bold=True))
        for c in nd["kids"]:
            draw_nodes(c)
    draw_nodes(root)

    ly = 46 + (H - 70) - 24
    p.append(circle(lx + 60, ly, 8, fill="#e9f7ef", stroke=FIELD, sw=2))
    p.append(text(lx + 74, ly + 4, "fib(1) → 1", size=11.5, color="#1e7a43", anchor="start"))
    p.append(circle(lx + 190, ly, 8, fill="#f1f3f5", stroke=MUTED, sw=2))
    p.append(text(lx + 204, ly + 4, "fib(0) → 0", size=11.5, color=MUTED, anchor="start"))
    p.append(circle(lx + 320, ly, 8, fill="#ffffff", stroke=INK, sw=2))
    p.append(text(lx + 334, ly + 4, "внутрішній (одне +)", size=11.5, color=INK, anchor="start"))

    sx = lx + lw + 26
    swd = W - sx - 24
    p.append(rect(sx, 46, swd, H - 70, fill="#fbfbfd", stroke=NEG, sw=1.6, rx=12))
    cxs = sx + swd / 2
    p.append(text(cxs, 78, "Рахунок", size=14, color=NEG, bold=True))
    rows = [
        ("листків:", "8 = F(6)", INK),
        ("з них → 1:", "5 = fib(5)", "#1e7a43"),
        ("→ 0:", "3 = fib(4)", MUTED),
        ("внутрішніх:", "7 = F(6)−1", INK),
        ("усього:", "15", INK),
    ]
    yy = 116
    for lab, val, col in rows:
        p.append(text(sx + 18, yy, lab, size=12.5, color=MUTED, anchor="start"))
        p.append(text(sx + swd - 18, yy, val, size=13, color=col, bold=True, anchor="end"))
        yy += 32
    by = yy + 4
    p.append(rect(sx + 14, by, swd - 28, 58, fill="#eef2ff", stroke=NEG, sw=1.6, rx=8))
    p.append(text(cxs, by + 24, "C(5) = 2·F(6) − 1", size=13.5, color=NEG, bold=True))
    p.append(text(cxs, by + 44, "= 2·8 − 1 = 15", size=13.5, color=NEG, bold=True))
    p.append(fitbox(sx + 14, by + 74, swd - 28, 96,
                    "fib(5) = 5 — це просто\nкількість зелених\nлистків: машина складає\nп'ять розкиданих одиниць.",
                    size=12, pad=10, fill="#e9f7ef", stroke=FIELD, color="#1e7a43"))

    render(os.path.join(OUT, "count-closedform.svg"), W, H, *p)


# ── ФІГУРА (math): золотий перетин як корінь x²=x+1 ──────────────────────────
def fig_golden_char():
    W, H = 840, 470
    p = [rect(0, 0, W, H, fill=BG, stroke="none", sw=0)]
    p.append(text(W / 2, 30, "Звідки золотий перетин: корені x² = x + 1", size=16, bold=True))

    xmin, xmax = -2.0, 2.7
    ymin, ymax = -1.6, 3.2
    pl, pr, pt, pb = 70, 540, 66, 356

    def X(mx):
        return pl + (mx - xmin) / (xmax - xmin) * (pr - pl)

    def Y(my):
        return pb - (my - ymin) / (ymax - ymin) * (pb - pt)

    bx1, bx2 = X(-1), X(1)
    p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fff8e6" stroke="none"/>'
             % (bx1, pt - 4, bx2 - bx1, (pb + 12) - (pt - 4)))
    p.append(text((bx1 + bx2) / 2, pb + 30, "|x| < 1 — корінь згасає", size=11.5, color="#9a6b00"))

    p.append(line(pl - 10, Y(0), pr + 12, Y(0), color=INK, sw=1.6))
    p.append(line(X(0), pt - 6, X(0), pb + 12, color=INK, sw=1.6))
    p.append(text(pr + 8, Y(0) - 8, "x", size=13, color=INK, anchor="end"))

    pts = []
    mx = xmin
    while mx <= xmax + 1e-9:
        pts.append((X(mx), Y(mx * mx - mx - 1)))
        mx += 0.05
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join("%.1f,%.1f" % q for q in pts), NEG))
    p.append(text(X(2.34), Y(2.34 * 2.34 - 2.34 - 1) - 6, "y = x²−x−1", size=12.5, color=NEG, anchor="start"))

    phi = (1 + 5 ** 0.5) / 2
    psi = (1 - 5 ** 0.5) / 2
    p.append(circle(X(psi), Y(0), 6, fill=MUTED, stroke=MUTED, sw=1.5))
    p.append(text(X(psi), Y(0) + 44, "ψ ≈ −0.618", size=12.5, color=MUTED, bold=True))
    p.append(text(X(psi), Y(0) + 62, "ψⁿ → 0", size=11, color=MUTED))
    p.append(line(X(phi), Y(0), X(phi), pt + 6, color=POS, sw=1.4, dash="4,4"))
    p.append(circle(X(phi), Y(0), 6, fill=POS, stroke=POS, sw=1.5))
    p.append(text(X(phi), Y(0) + 44, "φ ≈ 1.618", size=13, color=POS, bold=True))
    p.append(text(X(phi), Y(0) + 62, "домінує: Cₙ ~ φⁿ", size=11.5, color=POS, bold=True))

    tx, tw = 596, W - 596 - 22
    p.append(rect(tx, 70, tw, 176, fill="#fbfbfd", stroke=LINE, sw=1.4, rx=10))
    p.append(text(tx + tw / 2, 96, "F(n+1) / F(n)", size=13, color=INK, bold=True))
    ratios = [("55 / 34", "1.6176"), ("89 / 55", "1.6182"), ("144 / 89", "1.6180")]
    ry = 126
    for a, b in ratios:
        p.append(text(tx + 18, ry, a, size=12.5, color=MUTED, anchor="start"))
        p.append(text(tx + tw - 18, ry, "= " + b, size=12.5, color=INK, anchor="end"))
        ry += 28
    p.append(line(tx + 16, ry - 6, tx + tw - 16, ry - 6, color="#dcdfe4", sw=1.2))
    p.append(text(tx + tw / 2, ry + 18, "→ φ = 1.61803…", size=13, color=POS, bold=True))

    p.append(text(W / 2, H - 16,
                  "Більший за модулем корінь характеристичного рівняння = основа зростання.",
                  size=12.5, color=INK))
    render(os.path.join(OUT, "golden-characteristic.svg"), W, H, *p)


# ── ФІГУРА (math): простір станів — пряма (fib) vs сітка ─────────────────────
def fig_state_space():
    W, H = 940, 430
    p = [rect(0, 0, W, H, fill=BG, stroke="none", sw=0)]
    p.append(text(W / 2, 30, "Розмір простору станів = ціна", size=16, bold=True))

    def arc(x1, y1, x2, y2, lift, color):
        cx = (x1 + x2) / 2
        cy = min(y1, y2) - lift
        return ('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
                'stroke-width="1.8" marker-end="url(#arrow)"/>' % (x1, y1, cx, cy, x2, y2, color))

    lx, lw = 24, 430
    p.append(rect(lx, 50, lw, H - 96, fill="#fbfbfd", stroke=NEG, sw=1.6, rx=12))
    p.append(text(lx + lw / 2, 78, "Один вимір: fib", size=14, color=NEG, bold=True))
    n = 6
    cw, gap = 44, 10
    total = (n + 1) * cw + n * gap
    sx0 = lx + (lw - total) / 2
    cy = 178
    xc = []
    for i in range(n + 1):
        x = sx0 + i * (cw + gap)
        xc.append(x + cw / 2)
        p.append(rect(x, cy, cw, cw, fill="#ffffff", stroke=INK, sw=1.8, rx=8))
        p.append(text(x + cw / 2, cy + cw / 2 + 5, "%d" % i, size=13, color=INK, bold=True))
    p.append(arc(xc[6], cy - 2, xc[5], cy - 2, 26, NEG))
    p.append(arc(xc[6], cy - 2, xc[4], cy - 2, 46, NEG))
    p.append(text(lx + lw / 2, cy - 60, "кожен стан ← два попередні", size=12, color=MUTED))
    p.append(text(lx + lw / 2, cy + cw + 44, "n + 1 станів × O(1) = O(n)", size=13.5, color=NEG, bold=True))

    rx0 = lx + lw + 32
    rw = W - rx0 - 24
    p.append(rect(rx0, 50, rw, H - 96, fill="#fbfbfd", stroke=FIELD, sw=1.6, rx=12))
    p.append(text(rx0 + rw / 2, 78, "Два виміри: сітка (редакційна відстань, LCS)", size=13.5, color=FIELD, bold=True))
    cols, rowsn = 6, 4
    g, gg = 38, 6
    gw = cols * g + (cols - 1) * gg
    gh = rowsn * g + (rowsn - 1) * gg
    gx0 = rx0 + (rw - gw) / 2
    gy0 = 108

    def cell_xy(c, r):
        return gx0 + c * (g + gg), gy0 + r * (g + gg)

    hi_c, hi_r = 3, 2
    for r in range(rowsn):
        for c in range(cols):
            x, y = cell_xy(c, r)
            if (c, r) == (hi_c, hi_r):
                fill, stroke, sw = "#e9f7ef", FIELD, 2.4
            elif (c, r) in [(hi_c - 1, hi_r), (hi_c, hi_r - 1), (hi_c - 1, hi_r - 1)]:
                fill, stroke, sw = "#eef7f1", "#8fcea8", 1.8
            else:
                fill, stroke, sw = "#ffffff", "#cfd4da", 1.5
            p.append(rect(x, y, g, g, fill=fill, stroke=stroke, sw=sw, rx=6))
    hx, hy = cell_xy(hi_c, hi_r)
    hcx, hcy = hx + g / 2, hy + g / 2
    for (c, r) in [(hi_c - 1, hi_r), (hi_c, hi_r - 1), (hi_c - 1, hi_r - 1)]:
        x, y = cell_xy(c, r)
        p.append(arrow(x + g / 2, y + g / 2, hcx, hcy, color=FIELD, sw=1.7))
    p.append(text(hcx + 4, hcy + 5, "(i,j)", size=10.5, color="#1e7a43", bold=True, anchor="start"))
    p.append(text(rx0 + rw / 2, gy0 + gh + 40, "(m+1)(n+1) станів × O(1) = O(m·n)", size=13.5, color=FIELD, bold=True))

    p.append(text(W / 2, H - 16,
                  "Час = (кількість станів) × (робота на стан). Вимірів більше — станів більше.",
                  size=12.5, color=INK, bold=True))
    render(os.path.join(OUT, "state-space.svg"), W, H, *p)


# ── ФІГУРИ ДО ВСТАВКИ «Редакційна відстань» ─────────────────────────────────
OP_DEL = "#2457d6"   # видалення (синє)
OP_INS = "#c0392b"   # вставлення (червоне)
OP_SUB = "#b45309"   # заміна (бурштин)
OP_MAT = "#1e7a43"   # збіг (зелене)
PATHF  = "#e5f6ec"   # заливка клітин доріжки
PATHS  = "#27ae60"   # обвід доріжки


def fig_ed_recurrence():
    """Один крок рекурентності: клітина (i,j) як найдешевша з трьох сусідів."""
    W, H = 860, 470
    p = [rect(0, 0, W, H, fill=BG, stroke="none", sw=0)]
    p.append(text(W / 2, 34, "Одна клітина — вибір із трьох сусідів", size=17, bold=True))

    s = 96
    gx, gy = 150, 96
    coords = {
        (0, 0): "dp[i−1,j−1]",
        (0, 1): "dp[i−1,j]",
        (1, 0): "dp[i,j−1]",
        (1, 1): "dp[i,j]",
    }
    for (r, c), lab in coords.items():
        x, y = gx + c * s, gy + r * s
        target = (r == 1 and c == 1)
        p.append(rect(x, y, s, s, fill=("#eafaf0" if target else "#f8fafc"),
                      stroke=(PATHS if target else "#c9cfd8"), sw=(2.6 if target else 1.6), rx=10))
        p.append(text(x + s / 2, y + s / 2 + 5, lab, size=12.5,
                      color=(INK if target else MUTED), bold=target))
    cxL, cxR = gx + s / 2, gx + s + s / 2
    cyT, cyB = gy + s / 2, gy + s + s / 2
    p.append(arrow(cxR, cyT + 30, cxR, cyB - 30, color=OP_DEL, sw=2.4))              # ↓ видалення
    p.append(arrow(cxL + 30, cyB, cxR - 30, cyB, color=OP_INS, sw=2.4))              # → вставлення
    p.append(arrow(cxL + 26, cyT + 26, cxR - 26, cyB - 26, color=OP_SUB, sw=2.4))    # ↘ заміна

    lx = gx + 2 * s + 44
    ly = gy + 8
    p.append(text(lx, ly, "dp[i,j] — найдешевша з трьох:", size=14, color=INK, bold=True, anchor="start"))
    rows = [
        (OP_DEL, "↓", "dp[i−1,j] + 1", "видалити A[i]"),
        (OP_INS, "→", "dp[i,j−1] + 1", "вставити B[j]"),
        (OP_SUB, "↘", "dp[i−1,j−1] + c", "замінити A[i] → B[j]"),
    ]
    for k, (col, ar, formula, note) in enumerate(rows):
        yy = ly + 42 + k * 48
        p.append(text(lx, yy, ar, size=20, color=col, bold=True, anchor="start"))
        p.append(text(lx + 34, yy, formula, size=14, color=INK, bold=True, anchor="start"))
        p.append(text(lx + 34, yy + 19, note, size=12.5, color=MUTED, anchor="start"))
    p.append(text(lx, ly + 42 + 3 * 48 + 4,
                  "c = 0, якщо A[i] = B[j];   c = 1, якщо різні",
                  size=12.5, color=OP_MAT, bold=True, anchor="start"))

    bx, bw, bh = textbox(W / 2, H - 40,
                         "База:  dp[0,j] = j  (вставити весь B)      dp[i,0] = i  (видалити весь A)",
                         size=13, pad=13, fill="#f4f6f8", stroke=LINE)
    p.append(bx)
    render(os.path.join(OUT, "ed-recurrence.svg"), W, H, *p)


def fig_ed_grid():
    """Заповнена сітка dp для «kitten» → «sitting» з відновленою доріжкою правок."""
    A = "kitten"          # рядки  (i = 0..6)
    B = "sitting"         # стовпці (j = 0..7)
    D = [
        [0, 1, 2, 3, 4, 5, 6, 7],
        [1, 1, 2, 3, 4, 5, 6, 7],
        [2, 2, 1, 2, 3, 4, 5, 6],
        [3, 3, 2, 1, 2, 3, 4, 5],
        [4, 4, 3, 2, 1, 2, 3, 4],
        [5, 5, 4, 3, 2, 2, 3, 4],
        [6, 6, 5, 4, 3, 3, 2, 3],
    ]
    path = {(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (6, 7)}
    answer = (6, 7)

    cell = 46
    gx, gy = 104, 108
    ncol = len(B) + 1     # 8
    nrow = len(A) + 1     # 7
    W = gx + ncol * cell + 48
    H = gy + nrow * cell + 100

    p = [rect(0, 0, W, H, fill=BG, stroke="none", sw=0)]
    p.append(text(W / 2, 34, "Сітка підзадач:  «kitten» → «sitting»", size=17, bold=True))

    head_b = ["ε"] + list(B)
    for j, ch in enumerate(head_b):
        cx = gx + j * cell + cell / 2
        p.append(text(cx, gy - 16, ch, size=15, color=OP_INS, bold=True))
    p.append(text(gx + ncol * cell / 2, gy - 42, "B = sitting  →", size=12.5, color=MUTED))
    head_a = ["ε"] + list(A)
    for i, ch in enumerate(head_a):
        cy = gy + i * cell + cell / 2 + 5
        p.append(text(gx - 22, cy, ch, size=15, color=OP_DEL, bold=True))
    p.append(text(gx - 64, gy + nrow * cell / 2, "A = kitten", size=12.5, color=MUTED))
    p.append(text(gx - 64, gy + nrow * cell / 2 + 17, "↓", size=14, color=MUTED))

    for i in range(nrow):
        for j in range(ncol):
            x, y = gx + j * cell, gy + i * cell
            on = (i, j) in path
            ans = (i, j) == answer
            fill = PATHF if on else "#ffffff"
            if ans:
                fill = "#c7edd6"
            p.append(rect(x, y, cell, cell, fill=fill,
                          stroke=(PATHS if on else "#d6dae1"),
                          sw=(2.8 if ans else (2.2 if on else 1.3)), rx=6))
            p.append(text(x + cell / 2, y + cell / 2 + 6, str(D[i][j]),
                          size=(17 if ans else 15),
                          color=(INK if on else "#8a8f99"),
                          bold=(on or ans)))

    # фінальний крок (6,6)→(6,7): вставка 'g' — коротка стрілка над цифрами
    xg = gx + 6 * cell + cell
    yg = gy + 6 * cell + 13
    p.append(arrow(xg - 12, yg, xg + 15, yg, color=OP_INS, sw=2.4))

    p.append(text(W / 2, H - 54,
                  "Зелена доріжка — відновлені правки:  k→s заміна · i · t · t збіг · e→i заміна · n збіг · +g вставка",
                  size=12.5, color=INK))
    p.append(text(W / 2, H - 32,
                  "Кут таблиці = 3.  Клітин (m+1)(n+1) = 7·8 = 56 — кожна рахується один раз.",
                  size=12.5, color=MUTED))
    render(os.path.join(OUT, "ed-grid.svg"), W, H, *p)


def fig_ed_tworows():
    """Оптимізація пам'яті: замість цілої сітки досить двох рядків."""
    W, H = 820, 380
    p = [rect(0, 0, W, H, fill=BG, stroke="none", sw=0)]
    p.append(text(W / 2, 34, "Пам'ять: ціла сітка → два рядки", size=17, bold=True))

    mc = 15
    mx, my = 58, 96
    rows, cols = 7, 8
    for i in range(rows):
        for j in range(cols):
            faded = i not in (3, 4)
            p.append(rect(mx + j * mc, my + i * mc, mc - 2, mc - 2,
                          fill=("#eef1f5" if faded else "#e5f6ec"),
                          stroke=("#dfe3ea" if faded else PATHS), sw=1.0, rx=2))
    gw = cols * mc
    p.append(text(mx + gw / 2, my - 16, "ціла сітка", size=13, color=INK, bold=True))
    p.append(text(mx + gw / 2, my + rows * mc + 22, "O(m·n) пам'яті", size=12.5, color=MUTED))
    p.append(text(mx + gw / 2, my + rows * mc + 42, "лише два рядки", size=11.5, color=PATHS, bold=True))
    p.append(text(mx + gw / 2, my + rows * mc + 57, "потрібні водночас", size=11.5, color=MUTED))

    ax = mx + gw + 24
    p.append(arrow(ax, my + rows * mc / 2, ax + 58, my + rows * mc / 2, color=INK, sw=2.4))
    p.append(text(ax + 29, my + rows * mc / 2 - 12, "досить", size=12.5, color=INK, bold=True))

    s = 44
    rx0 = ax + 86
    ry = 98
    ncell = 6
    bands = [
        (ry,                 "#eef1f5", "#dfe3ea", "рядок i−2 — викинуто", MUTED),
        (ry + s + 16,        "#eaf0fd", OP_DEL,    "рядок i−1 — попередній (prev)", OP_DEL),
        (ry + 2 * (s + 16),  "#eafaf0", PATHS,     "рядок i — поточний (curr)", OP_MAT),
    ]
    for by, fill, stroke, label, lcol in bands:
        for j in range(ncell):
            p.append(rect(rx0 + j * s, by, s - 4, s - 4, fill=fill, stroke=stroke, sw=1.6, rx=5))
        p.append(text(rx0 + ncell * s + 12, by + s / 2, label, size=12.5, color=lcol,
                      bold=True, anchor="start"))
    c = 4
    prev_y = ry + s + 16
    curr_y = ry + 2 * (s + 16)
    cx = rx0 + c * s + (s - 4) / 2
    lxc = rx0 + (c - 1) * s + (s - 4) / 2
    p.append(rect(rx0 + c * s, curr_y, s - 4, s - 4, fill="#c7edd6", stroke=PATHS, sw=2.8, rx=5))
    p.append(arrow(cx, prev_y + s - 4, cx, curr_y + 4, color=OP_DEL, sw=2.2))                       # ↓
    p.append(arrow(lxc + 6, prev_y + s - 8, cx - 6, curr_y + 6, color=OP_SUB, sw=2.2))              # ↘
    p.append(arrow(lxc + (s - 4) / 2 + 4, curr_y + (s - 4) / 2, cx - (s - 4) / 2 - 2,
                   curr_y + (s - 4) / 2, color=OP_INS, sw=2.2))                                     # →

    p.append(text(W / 2, H - 20,
                  "щойно рядок i готовий, рядок i−2 більше не потрібен → тримаємо два, пам'ять O(min(m,n))",
                  size=12.5, color=INK))
    render(os.path.join(OUT, "ed-tworows.svg"), W, H, *p)


if __name__ == "__main__":
    fig_explosion()
    fig_mechanism()
    fig_topdown_bottomup()
    fig_growth()
    fig_timeline()
    fig_count_closedform()
    fig_golden_char()
    fig_state_space()
    fig_ed_recurrence()
    fig_ed_grid()
    fig_ed_tworows()
    print("OK: figures written to", OUT)
