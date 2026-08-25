# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GREEDY = POS       # червоний — жадібний
DP     = FIELD     # зелений — динамічне програмування / оптимум
COIN   = "#2457d6" # синій обвід монет


def coin_chip(cx, cy, val, r=27, col=INK):
    """Монета-кружечок із номіналом."""
    out = circle(cx, cy, r, fill="#ffffff", stroke=col, sw=2.6)
    out += circle(cx, cy, r - 5, fill="none", stroke=col, sw=1.0)
    out += text(cx, cy + 6, str(val), size=18, color=col, bold=True)
    return out


def carc(x1, y1, x2, y2, lift, color, sw=2.2, dash=None):
    """Дугова стрілка (квадратична крива) з наконечником."""
    cx = (x1 + x2) / 2
    cy = min(y1, y2) - lift
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
            'stroke-width="%.1f"%s marker-end="url(#arrow)"/>'
            % (x1, y1, cx, cy, x2, y2, color, sw, d))


# ── ФІГУРА 1: жадібний проти ДП на розміні 6 ────────────────────────────────
def fig_greedy_vs_dp():
    W, H = 900, 380
    p = [rect(0, 0, W, H, fill=BG, stroke="none", sw=0)]
    p.append(text(W / 2, 32, "Розмін суми 6 монетами {1, 3, 4}", size=17, bold=True))

    def panel(x0, w, border, title, coins, count_txt, count_col):
        p.append(rect(x0, 62, w, H - 128, fill="#fbfbfd", stroke=border, sw=1.9, rx=12))
        p.append(text(x0 + w / 2, 86, title, size=14.5, color=border, bold=True))
        p.append(text(x0 + w / 2, 112, "сума = 6", size=12, color=MUTED))
        # ряд монет із «+» між ними
        r = 27
        n = len(coins)
        gap = 40
        total = n * 2 * r + (n - 1) * gap
        sx = x0 + (w - total) / 2 + r
        cy = 172
        xs = []
        for i in range(n):
            cx = sx + i * (2 * r + gap)
            xs.append(cx)
        for i, (cx, v) in enumerate(zip(xs, coins)):
            if i > 0:
                p.append(text((xs[i - 1] + cx) / 2, cy + 7, "+", size=20, color=MUTED, bold=True))
            p.append(coin_chip(cx, cy, v, r=r, col=COIN))
        p.append(text(x0 + w / 2, 244, count_txt, size=16, color=count_col, bold=True))

    panel(30, 400, GREEDY, "Жадібний: щоразу найбільша монета",
          [4, 1, 1], "разом 3 монети", GREEDY)
    panel(470, 400, DP, "Динамічне програмування: найкращий підсумок",
          [3, 3], "разом 2 монети  —  оптимум", DP)

    note, nw, nh = textbox(W / 2, H - 34,
                           "Обидва набирають 6. Монета 4 лишає незручний залишок 2 = 1 + 1;  дві трійки коротші.",
                           size=13, pad=12, fill="#f4f6f8", stroke=LINE)
    p.append(note)
    render(os.path.join(OUT, "greedy-vs-dp.svg"), W, H, *p)


# ── ФІГУРА 2: оптимальна підструктура (принцип оптимальності) ────────────────
def fig_optimal_substructure():
    W, H = 900, 430
    p = [rect(0, 0, W, H, fill=BG, stroke="none", sw=0)]
    p.append(text(W / 2, 32, "Принцип оптимальності: оптимум цілого = перший крок + оптимум залишку",
                  size=15.5, bold=True))

    # верхній ланцюг
    y = 118
    bA, wA, hA = textbox(140, y, "Оптимум\nсуми a", size=14, pad=15,
                         fill="#eef2ff", stroke=NEG, bold=True)
    p.append(bA)
    bB, wB, hB = textbox(470, y, "Оптимум\nсуми a − c", size=14, pad=15,
                         fill="#e9f7ef", stroke=DP, bold=True)
    p.append(bB)
    bG, wG, hG = textbox(760, y, "0\n(база)", size=14, pad=15,
                         fill="#f4f6f8", stroke=LINE)
    p.append(bG)

    p.append(arrow(140 + wA / 2, y, 470 - wB / 2, y, color=INK, sw=2.2))
    p.append(text((140 + wA / 2 + 470 - wB / 2) / 2, y - 16, "монета c  (+1)", size=13, color=INK, bold=True))
    p.append(arrow(470 + wB / 2, y, 760 - wG / 2, y, color=MUTED, sw=2.0))
    p.append(text((470 + wB / 2 + 760 - wG / 2) / 2, y - 16, "…далі оптимально", size=12.5, color=MUTED))

    fb, fbw, fbh = textbox(W / 2, y + 78, "dp[a]  =  1  +  dp[a − c]", size=15, pad=12,
                           fill="#fff8e6", stroke="#f59e0b", bold=True, color="#9a6b00")
    p.append(fb)

    # нижня рамка: доведення «вирізати й вклеїти»
    iy = 262
    p.append(rect(40, iy, W - 80, H - iy - 24, fill="#fbfbfd", stroke=LINE, sw=1.5, rx=12))
    p.append(text(64, iy + 26, "Чому хвіст мусить бути оптимальний", size=13.5, color=INK, bold=True, anchor="start"))

    # два стовпчики вартості хвоста від стану a−c
    bx = 92
    barw_opt, barw_bad = 150, 232
    bh = 26
    y1 = iy + 52
    y2 = iy + 96
    p.append(rect(bx, y1, barw_opt, bh, fill="#e9f7ef", stroke=DP, sw=2, rx=5))
    p.append(text(bx + barw_opt + 12, y1 + 18, "оптимальний хвіст dp[a − c]", size=12.5, color="#1e7a43", bold=True, anchor="start"))
    p.append(rect(bx, y2, barw_bad, bh, fill="#f1f3f5", stroke=MUTED, sw=1.6, rx=5))
    p.append(text(bx + barw_bad + 12, y2 + 18, "припустимо, хвіст гірший (довший)", size=12.5, color=MUTED, anchor="start"))
    # стрілка підміни gray → green
    p.append(carc(bx + 8, y2, bx + 8, y1 + bh, 22, DP, sw=2.0))
    p.append(text(bx - 6, (y1 + y2) / 2 + 5, "підміна", size=11.5, color=DP, bold=True, anchor="end"))

    concl = ("Вклей кращий хвіст — ціле здешевіє.\n"
             "Та воно ж нібито вже оптимальне:\n"
             "суперечність. Отже хвіст оптимуму\n"
             "сам оптимальний для свого стану.")
    p.append(fitbox(566, iy + 40, 292, 116, concl, size=12.5, pad=13,
                    fill="#fdecea", stroke=GREEDY, color="#a5281b"))

    render(os.path.join(OUT, "optimal-substructure.svg"), W, H, *p)


# ── ФІГУРА 3: каркас із шести кроків ────────────────────────────────────────
def fig_dp_recipe():
    W, H = 880, 540
    p = [rect(0, 0, W, H, fill=BG, stroke="none", sw=0)]
    p.append(text(W / 2, 32, "Каркас динамічного програмування — шість кроків", size=16.5, bold=True))

    lx, lw = 46, 470            # ліва колонка: загальний крок
    rx, rw = lx + lw + 30, W - (lx + lw + 30) - 30   # права: приклад монет
    p.append(text(lx + 40, 66, "Крок каркаса", size=13, color=MUTED, bold=True, anchor="start"))
    p.append(text(rx + rw / 2, 66, "на прикладі монет {1,3,4}, сума 6", size=12.5, color=MUTED))

    steps = [
        ("Стан", "найменший опис підзадачі", "dp[a] — мінімум монет на суму a"),
        ("Перехід", "рекурентність через дрібніші стани", "dp[a] = 1 + min dp[a − c]"),
        ("База", "стани з очевидною відповіддю", "dp[0] = 0"),
        ("Порядок", "кожен стан — раніше за тих, хто на нього спирається", "суми від 0 до 6, зліва направо"),
        ("Відповідь", "стан, що є розв'язком цілого", "dp[6] = 2"),
        ("Відновлення", "за вказівниками назад до розв'язку", "6 → 3 → 0   =   {3, 3}"),
    ]
    top = 84
    rh = 68
    for i, (title, sub, ex) in enumerate(steps):
        y = top + i * rh
        # ліва картка
        p.append(rect(lx, y, lw, rh - 12, fill="#fbfbfd", stroke=LINE, sw=1.4, rx=10))
        p.append(circle(lx + 26, y + (rh - 12) / 2, 15, fill="#eef2ff", stroke=NEG, sw=2))
        p.append(text(lx + 26, y + (rh - 12) / 2 + 5, str(i + 1), size=14, color=NEG, bold=True))
        p.append(text(lx + 52, y + 24, title, size=14.5, color=INK, bold=True, anchor="start"))
        p.append(text(lx + 52, y + 44, sub, size=12, color=MUTED, anchor="start"))
        # права картка-приклад
        p.append(fitbox(rx, y, rw, rh - 12, ex, size=13, pad=10,
                        fill="#e9f7ef", stroke=DP, color="#1e7a43", bold=True))
        # стрілка вниз між кроками
        if i < len(steps) - 1:
            cx = lx + 26
            p.append(arrow(cx, y + rh - 12, cx, y + rh, color=NEG, sw=1.8))

    render(os.path.join(OUT, "dp-recipe.svg"), W, H, *p)


# ── ФІГУРА 4: заповнена таблиця dp для розміну ──────────────────────────────
def fig_coin_table():
    W, H = 900, 430
    p = [rect(0, 0, W, H, fill=BG, stroke="none", sw=0)]
    p.append(text(W / 2, 30, "Таблиця підзадач: dp[a] — найменше монет на суму a  (монети 1, 3, 4)",
                  size=15, bold=True))

    vals = [0, 1, 2, 1, 1, 2, 2]
    n = len(vals)
    cw, gap = 66, 12
    total = n * cw + (n - 1) * gap
    startx = (W - total) / 2
    top = 250                      # верх ряду клітин

    def cx(i):
        return startx + i * (cw + gap) + cw / 2

    # клітини
    path_cells = {0, 3, 6}         # слід відновлення
    for i, v in enumerate(vals):
        x = startx + i * (cw + gap)
        on = i in path_cells
        p.append(rect(x, top, cw, cw, fill=("#e9f7ef" if on else "#ffffff"),
                      stroke=(DP if on else "#c9cfd8"), sw=(2.6 if on else 1.6), rx=8))
        p.append(text(x + cw / 2, top - 14, "a = %d" % i, size=12, color=MUTED))
        p.append(text(x + cw / 2, top + cw / 2 + 7, str(v), size=20,
                      color=(INK if on else "#555a63"), bold=True))

    celltop = top
    # три дуги-переходи в клітину 6: від 5 (монета 1), 3 (монета 3), 2 (монета 4)
    arcs = [
        (5, "монета 1", MUTED, 44, "dp[5]=2"),
        (2, "монета 4", MUTED, 150, "dp[2]=2"),
        (3, "монета 3  ✓", DP,  96, "dp[3]=1"),   # обрана — зелена, малюємо останньою
    ]
    for src, lab, col, lift, valtag in arcs:
        x1, x2 = cx(src), cx(6)
        p.append(carc(x1, celltop, x2, celltop, lift, col, sw=(2.6 if col == DP else 1.8),
                      dash=(None if col == DP else "5,4")))
        apex_x = (x1 + x2) / 2
        apex_y = celltop - lift
        p.append(text(apex_x, apex_y - 8, lab, size=12.5, color=col,
                      bold=(col == DP)))
        p.append(text(apex_x, apex_y - 24, valtag, size=11, color=col))

    p.append(text(W / 2, celltop - 168,
                  "dp[6] = 1 + min( dp[5], dp[3], dp[2] ) = 1 + 1 = 2   — найдешевше через dp[3], монетою 3",
                  size=12.5, color=INK, bold=True))

    # слід відновлення під рядком
    ry = top + cw + 40
    p.append(text(startx, ry, "відновлення:", size=12.5, color=MUTED, anchor="start"))
    chain = "6  →  3  →  0"
    p.append(text(W / 2, ry, chain, size=15, color=DP, bold=True))
    p.append(text(W - startx, ry, "монети  {3, 3}", size=13.5, color=DP, bold=True, anchor="end"))
    p.append(text(W / 2, H - 16,
                  "Клітин лише сім — кожну підзадачу пораховано рівно раз.",
                  size=12, color=MUTED))
    render(os.path.join(OUT, "coin-table.svg"), W, H, *p)


# ══ ФІГУРИ ДЛЯ ВСТАВКИ math-optimal-substructure ════════════════════════════
BLUE = "#2457d6"   # половина q→s
RED  = POS         # половина s→t / провал
GRN  = FIELD       # справжній оптимум
WARN = "#e8830c"   # попередження про повтор вершини


def _vnode(cx, cy, label, fill="#ffffff", stroke=INK, sw=2.2, r=20, tc=INK):
    return (circle(cx, cy, r, fill=fill, stroke=stroke, sw=sw) +
            text(cx, cy + 6, label, size=16, color=tc, bold=True))


def _mini_graph(ox, oy, hi_edges, hi_verts, title, title_col=INK):
    """Малий граф q,r,s,t (ребра q-r, r-s, r-t, s-t) з підсвіченим шляхом.
    hi_edges: список (u,v,color,width); hi_verts: {вершина: колір-обводу}."""
    P = {"q": (ox + 40, oy + 118), "r": (ox + 150, oy + 40),
         "t": (ox + 150, oy + 196), "s": (ox + 260, oy + 118)}
    base = [("q", "r"), ("r", "s"), ("r", "t"), ("s", "t")]
    out = [text(ox + 150, oy - 6, title, size=13.5, color=title_col, bold=True)]
    # базові ребра (сірі)
    for u, v in base:
        (x1, y1), (x2, y2) = P[u], P[v]
        out.append(line(x1, y1, x2, y2, color="#c2c8d0", sw=2.0))
    # підсвічені ребра
    for u, v, col, wdt in hi_edges:
        (x1, y1), (x2, y2) = P[u], P[v]
        out.append(line(x1, y1, x2, y2, color=col, sw=wdt))
    # вершини
    for name, (x, y) in P.items():
        ring = hi_verts.get(name, INK)
        sw = 3.4 if name in hi_verts else 2.0
        out.append(_vnode(x, y, name, stroke=ring, sw=sw))
    return out


def fig_longest_path_fail():
    W, H = 1156, 500
    p = [rect(0, 0, W, H, fill=BG, stroke="none", sw=0)]
    p.append(text(W / 2, 30, "Найдовший простий шлях НЕ має оптимальної підструктури",
                  size=16.5, bold=True))
    p.append(text(W / 2, 52, "граф без ваг: довжина = кількість ребер;  ребра  q–r, r–s, r–t, s–t",
                  size=12.5, color=MUTED))

    # два малі графи — дві оптимальні половини
    p += _mini_graph(70, 96, [("q", "r", BLUE, 5), ("r", "t", BLUE, 5), ("t", "s", BLUE, 5)],
                     {"q": BLUE, "r": BLUE, "t": BLUE, "s": BLUE},
                     "Половина 1: найдовший  q → s  =  q-r-t-s  (3 ребра)", BLUE)
    p += _mini_graph(520, 96, [("s", "r", RED, 5), ("r", "t", RED, 5)],
                     {"s": RED, "r": RED, "t": RED},
                     "Половина 2: найдовший  s → t  =  s-r-t  (2 ребра)", RED)

    # смуга «склейка»
    gy = 356
    p.append(rect(40, gy - 26, W - 80, 150, fill="#fbfbfd", stroke=LINE, sw=1.5, rx=12))
    p.append(text(64, gy, "Склеюємо дві оптимальні половини в  q → t:", size=13.5,
                  color=INK, bold=True, anchor="start"))
    seq = [("q", INK), ("r", INK), ("t", INK), ("s", INK), ("r", WARN), ("t", WARN)]
    sx, sy, gap = 150, gy + 46, 92
    for i, (lab, col) in enumerate(seq):
        cx = sx + i * gap
        if i > 0:
            p.append(arrow(sx + (i - 1) * gap + 22, sy, cx - 22, sy, color=MUTED, sw=1.8))
        dup = col == WARN
        p.append(_vnode(cx, sy, lab, fill=("#fff4e6" if dup else "#ffffff"),
                        stroke=col, sw=(3.4 if dup else 2.2), r=20, tc=col))
        if dup:
            p.append(text(cx, sy + 40, "повтор!", size=11.5, color=WARN, bold=True))
    p.append(text(sx + 5 * gap + 60, sy, "→  не простий", size=14, color=RED, bold=True, anchor="start"))
    p.append(text(64, gy + 108,
                  "Справжній найдовший  q → t  =  q-r-s-t  (3 ребра) — його половини q-r-s (2) і s-t (1) "
                  "НЕ найдовші. Оптимум цілого зібрано з НЕоптимальних частин: підструктура не діє.",
                  size=12.5, color=GRN, bold=True, anchor="start"))

    render(os.path.join(OUT, "longest-path-fail.svg"), W, H, *p)


def fig_states_vs_paths():
    W, H = 900, 540
    p = [rect(0, 0, W, H, fill=BG, stroke="none", sw=0)]
    p.append(text(W / 2, 30, "Перекриття згортає дерево шляхів у граф станів", size=16.5, bold=True))
    p.append(text(W / 2, 52, "розмін монетами {1, 2}, сума 4:  функція solve(a) = 1 + min( solve(a−1), solve(a−2) )",
                  size=12.5, color=MUTED))

    # колір за значенням стану (однакові стани — однаковий колір)
    scol = {4: "#ffffff", 3: "#fff1d6", 2: "#e9f7ef", 1: "#e6efff", 0: "#eef0f2"}
    sstroke = {4: INK, 3: "#d9a441", 2: GRN, 1: BLUE, 0: MUTED}

    # ── дерево наївної рекурсії (ліворуч) ──
    tree = {"arg": 4}

    def build(a):
        node = {"arg": a, "kids": []}
        if a >= 1:
            node["kids"].append(build(a - 1))
        if a >= 2:
            node["kids"].append(build(a - 2))
        return node

    root = build(4)
    leafx = [0]
    coords = []

    def layout(node, depth):
        if node["kids"]:
            xs = [layout(k, depth + 1) for k in node["kids"]]
            x = sum(xs) / len(xs)
        else:
            x = leafx[0]; leafx[0] += 1
        coords.append((node["arg"], x, depth, node["kids"]))
        node["_x"], node["_d"] = x, depth
        return x

    layout(root, 0)
    ox, oy = 70, 108
    colw, rowh = 78, 74
    # ребра дерева

    def draw_edges(node):
        for k in node["kids"]:
            p.append(line(ox + node["_x"] * colw, oy + node["_d"] * rowh + 20,
                          ox + k["_x"] * colw, oy + k["_d"] * rowh - 20,
                          color="#b9c0c9", sw=1.6))
            draw_edges(k)
    draw_edges(root)

    def draw_nodes(node):
        a = node["arg"]
        p.append(circle(ox + node["_x"] * colw, oy + node["_d"] * rowh, 18,
                        fill=scol[a], stroke=sstroke[a], sw=2.2))
        p.append(text(ox + node["_x"] * colw, oy + node["_d"] * rowh + 6, str(a),
                      size=15, color=INK, bold=True))
        for k in node["kids"]:
            draw_nodes(k)
    draw_nodes(root)
    p.append(text(210, 92, "наївне дерево: 12 викликів  (той самий стан — знову й знову)",
                  size=12.5, color=RED, bold=True))

    # ── стрілка згортання ──
    mx = 520
    p.append(arrow(455, 250, mx - 6, 250, color=INK, sw=2.4))
    p.append(text((455 + mx) / 2, 234, "мемоізація", size=12.5, color=INK, bold=True))
    p.append(text((455 + mx) / 2, 268, "однакові стани", size=11, color=MUTED))

    # ── граф станів (праворуч): 5 станів у ряд ──
    p.append(text(710, 92, "граф станів: 5 вузлів", size=13, color=GRN, bold=True))
    gx, gy2, ggap = 560, 250, 70
    pos = {}
    for i, a in enumerate([0, 1, 2, 3, 4]):
        cx = gx + i * ggap
        pos[a] = cx
        p.append(circle(cx, gy2, 20, fill=scol[a], stroke=sstroke[a], sw=2.4))
        p.append(text(cx, gy2 + 6, str(a), size=16, color=INK, bold=True))
    # залежності a → a-1, a → a-2 (дугами зверху/знизу)
    for a in [1, 2, 3, 4]:
        # a-1 (знизу)
        x1, x2 = pos[a], pos[a - 1]
        p.append(carc(x1, gy2 + 20, x2, gy2 + 20, -34, MUTED, sw=1.7))
        if a >= 2:
            x2b = pos[a - 2]
            p.append(carc(x1, gy2 - 20, x2b, gy2 - 20, 34, MUTED, sw=1.7))
    p.append(text(710, gy2 + 96, "кожен стан — рівно раз", size=11.5, color=GRN, bold=True))

    # ── нижня смуга: числа ──
    by = 430
    p.append(rect(40, by, W - 80, H - by - 20, fill="#fbfbfd", stroke=LINE, sw=1.5, rx=12))
    p.append(text(64, by + 28, "Скільки різних шляхів проти скількох різних станів",
                  size=13.5, color=INK, bold=True, anchor="start"))
    p.append(text(64, by + 54,
                  "монети {1, 2}, сума 40:   433 494 436 наївних викликів  ~ φⁿ   проти   41 стану  (лінійно)",
                  size=12.5, color=INK, anchor="start"))
    p.append(text(64, by + 76,
                  "сітка m×n:   C(m+n, n) монотонних шляхів (експонента)   проти   (m+1)(n+1) станів  —  для 20×20 це 137 846 528 820 проти 441",
                  size=12.5, color=INK, anchor="start"))

    render(os.path.join(OUT, "states-vs-paths.svg"), W, H, *p)


# ══ ФІГУРА ДЛЯ ВСТАВКИ hist-bellman: хронологія назви vs каденція міністра ════
def fig_name_timeline():
    W, H = 940, 440
    p = [rect(0, 0, W, H, fill=BG, stroke="none", sw=0)]
    p.append(text(W / 2, 30, "Хронологія назви: термін ужито ДО того, як Вілсон став міністром",
                  size=16, bold=True))
    p.append(text(W / 2, 52, "чому легенда про «прикриття від міністра» не сходиться за календарем",
                  size=12.5, color=MUTED))

    x0, x1 = 120, 830
    def X(yr):
        return x0 + (yr - 1949) * (x1 - x0) / 8.0
    axis_y = 250

    # смуга-розрив 1952→1953 (позаду всього)
    gx0, gx1 = X(1952), X(1953)
    p.append(rect(gx0, 66, gx1 - gx0, axis_y - 66, fill="#fff3d6", stroke="none", sw=0, rx=0))
    p.append(text((gx0 + gx1) / 2, 234, "розрив", size=11, color="#9a6b00", bold=True))

    # вісь років
    p.append(line(x0 - 24, axis_y, x1 + 34, axis_y, color=INK, sw=2.2))
    for yr in range(1949, 1958):
        xx = X(yr)
        p.append(line(xx, axis_y - 5, xx, axis_y + 5, color=INK, sw=1.6))
        p.append(text(xx, axis_y + 22, str(yr), size=12, color=MUTED))

    # зелені віхи «народження назви» над віссю
    def event(yr, cy, label):
        xx = X(yr)
        box, bw, bh = textbox(xx, cy, label, size=12, pad=9,
                              fill="#e9f7ef", stroke=DP, color="#1e7a43", bold=True)
        p.append(line(xx, cy + bh / 2, xx, axis_y - 6, color=DP, sw=1.5, dash="4,3"))
        p.append(circle(xx, axis_y, 5.5, fill=DP, stroke="#ffffff", sw=1.6))
        p.append(box)

    event(1949, 102, "1949\nБеллман у RAND")
    event(1950, 178, "1950\nвигадує назву")
    event(1952, 102, "1952\nперша друкована\nпраця з терміном")
    event(1957, 178, "1957\nкнига, принцип\nоптимальності")

    # червона смуга каденції Вілсона під віссю
    wx0, wx1 = X(1953), X(1957) + 10
    p.append(rect(wx0, 284, wx1 - wx0, 32, fill="#fdecea", stroke=POS, sw=2, rx=8))
    p.append(text((wx0 + wx1) / 2, 305, "Ч. Вілсон — міністр оборони  (січень 1953 – 1957)",
                  size=12.5, color="#a5281b", bold=True))

    # каптіон-вирок ліворуч від смуги
    p.append(fitbox(120, 300, 330, 64,
                    "Назву вжито в друці 1952-го —\nза рік до того, як Вілсон\nобійняв посаду.",
                    size=12.5, pad=11, fill="#fbfbfd", stroke="#f59e0b", color="#9a6b00"))

    # нижній вирок
    p.append(text(W / 2, 402,
                  "Отже мотив «сховати математику від міністра» — радше пізніша прикраса, ніж причина назви.",
                  size=12.5, color=INK, bold=True))

    render(os.path.join(OUT, "name-timeline.svg"), W, H, *p)


# ══ ФІГУРИ ДЛЯ ВСТАВКИ proj-knapsack ════════════════════════════════════════
TAKE = FIELD       # зелений — «взяти» річ
SKIP = MUTED       # сірий — «пропустити» річ
BUG  = POS         # червоний — помилка (річ порахована двічі)
SRC  = "#2457d6"   # синій — прочитана клітина-джерело


def fig_knapsack_table():
    W, H = 980, 520
    p = [rect(0, 0, W, H, fill=BG, stroke="none", sw=0)]
    p.append(text(W / 2, 30, "Таблиця рюкзака: dp[i][w] — найбільша цінність із перших i речей за місткості w",
                  size=15, bold=True))
    p.append(text(W / 2, 52, "речі  A(1кг,$1)  B(3кг,$4)  C(4кг,$5)  D(5кг,$7);   рюкзак витримує  W = 7",
                  size=12.5, color=MUTED))

    rows = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 1],
        [0, 1, 1, 4, 5, 5, 5, 5],
        [0, 1, 1, 4, 5, 6, 6, 9],
        [0, 1, 1, 4, 5, 7, 8, 9],
    ]
    labels = ["— 0 речей", "A · 1кг · $1", "B · 3кг · $4", "C · 4кг · $5", "D · 5кг · $7"]
    path = {(0, 0), (1, 0), (2, 3), (3, 7), (4, 7)}     # слід відновлення

    gx, gy, cw, ch = 196, 150, 44, 44
    def cellx(w): return gx + w * cw
    def celly(i): return gy + i * ch

    for w in range(8):
        p.append(text(cellx(w) + cw / 2, gy - 12, "w=%d" % w, size=12, color=MUTED))
    for i in range(5):
        p.append(text(gx - 12, celly(i) + ch / 2 + 5, labels[i], size=11.5, color=INK, anchor="end", bold=True))
        for w in range(8):
            on = (i, w) in path
            p.append(rect(cellx(w), celly(i), cw, ch,
                          fill=("#e9f7ef" if on else "#ffffff"),
                          stroke=(TAKE if on else "#cdd3db"),
                          sw=(2.6 if on else 1.3), rx=6))
            p.append(text(cellx(w) + cw / 2, celly(i) + ch / 2 + 6, str(rows[i][w]),
                          size=(16 if on else 14), color=(INK if on else "#5a616b"), bold=on))

    p.append(text(cellx(7) + cw / 2, celly(4) + ch + 18, "відповідь = 9", size=12.5, color=TAKE, bold=True))

    # стрілки сліду: «взяти» — горизонталлю по лінії між рядками; «пропустити» — короткою вертикаллю
    p.append(arrow(cellx(7) + cw / 2, celly(3), cellx(3) + cw / 2 + 6, celly(3), color=TAKE, sw=2.6))  # взяти C
    p.append(arrow(cellx(3) + cw / 2, celly(2), cellx(0) + cw / 2 + 6, celly(2), color=TAKE, sw=2.6))  # взяти B
    p.append(arrow(cellx(7) + 9, celly(4) + ch / 2, cellx(7) + 9, celly(3) + ch / 2, color=SKIP, sw=2.2))  # пропустити D
    p.append(arrow(cellx(0) + 9, celly(1) + ch / 2, cellx(0) + 9, celly(0) + ch / 2, color=SKIP, sw=2.2))  # пропустити A

    # легенда-трасування праворуч від сітки
    bx, by = 588, 150
    p.append(rect(bx, by, 372, 236, fill="#fbfbfd", stroke=LINE, sw=1.5, rx=12))
    p.append(text(bx + 18, by + 26, "Відновлення: від dp[4][7] назад", size=13.5, color=INK, bold=True, anchor="start"))
    p.append(line(bx + 18, by + 48, bx + 42, by + 48, color=TAKE, sw=3.2))
    p.append(text(bx + 50, by + 52, "взяти — по діагоналі, місткість − вага", size=11.5, color=TAKE, bold=True, anchor="start"))
    p.append(line(bx + 18, by + 68, bx + 42, by + 68, color=SKIP, sw=3.2))
    p.append(text(bx + 50, by + 72, "пропустити — вгору, місткість та сама", size=11.5, color=SKIP, anchor="start"))
    steps = [
        ("dp[4][7]=9 = dp[3][7]", "пропустити D", SKIP),
        ("dp[3][7]=9 = dp[2][3]+5", "взяти C", TAKE),
        ("dp[2][3]=4 = dp[1][0]+4", "взяти B", TAKE),
        ("dp[1][0]=0 = dp[0][0]", "пропустити A", SKIP),
    ]
    sy = by + 104
    for eqn, dec, col in steps:
        p.append(text(bx + 18, sy, eqn, size=12, color=INK, anchor="start"))
        p.append(text(bx + 234, sy, "→ " + dec, size=12, color=col, bold=True, anchor="start"))
        sy += 25
    p.append(text(bx + 18, sy + 8, "набір {B, C}:  вага 3+4=7,  цінність 4+5=9",
                  size=12.5, color=TAKE, bold=True, anchor="start"))

    fb, _, _ = textbox(gx + 4 * cw - 20, 466,
                       "перехід:  dp[i][w] = max( dp[i−1][w],  dp[i−1][w−вагаᵢ] + цінністьᵢ )\n"
                       "ліворуч — пропустити річ i;   праворуч — узяти, якщо вагаᵢ ≤ w",
                       size=13, pad=12, fill="#fff8e6", stroke="#f59e0b", color="#9a6b00", bold=True)
    p.append(fb)
    render(os.path.join(OUT, "knapsack-table.svg"), W, H, *p)


def fig_knapsack_direction():
    W, H = 940, 478
    p = [rect(0, 0, W, H, fill=BG, stroke="none", sw=0)]
    p.append(text(W / 2, 30, "Один рядок dp[w]: місткість перебирають НАЗАД — інакше річ клонується",
                  size=15.5, bold=True))
    p.append(text(W / 2, 52, "додаємо річ B (3 кг, $4) до рядка, що вже враховує A:  було dp = [0,1,1,1,1,1,1,1]",
                  size=12.5, color=MUTED))

    cw, cellw = 84, 74
    x0 = (W - 8 * cw) / 2 + 5
    def cx(w): return x0 + w * cw
    def ctr(w): return cx(w) + cellw / 2

    def band(ytitle, ycells, vals, hi, direction, title, tcol, note, ncol):
        p.append(text(W / 2, ytitle, title, size=13.5, color=tcol, bold=True))
        ya = ytitle + 16
        if direction == "back":
            p.append(arrow(ctr(7), ya, ctr(0), ya, color=INK, sw=2.0))
        else:
            p.append(arrow(ctr(0), ya, ctr(7), ya, color=INK, sw=2.0))
        for w in range(8):
            role = hi.get(w)
            fill, stroke, sw, tc = "#ffffff", "#cdd3db", 1.3, "#5a616b"
            if role == "src":    fill, stroke, sw, tc = "#e6efff", SRC, 2.6, INK
            if role == "srcbug": fill, stroke, sw, tc = "#fff1e0", WARN, 2.6, "#9a5b00"
            if role == "dst":    fill, stroke, sw, tc = "#e9f7ef", TAKE, 2.8, INK
            if role == "bug":    fill, stroke, sw, tc = "#fdecea", BUG, 2.8, BUG
            p.append(rect(cx(w), ycells, cellw, 50, fill=fill, stroke=stroke, sw=sw, rx=7))
            p.append(text(ctr(w), ycells - 8, "w=%d" % w, size=11, color=MUTED))
            p.append(text(ctr(w), ycells + 31, str(vals[w]), size=18, color=tc, bold=(role is not None)))
        yb = ycells + 50
        acol = SRC if direction == "back" else WARN
        p.append(carc(ctr(3), yb, ctr(6), yb, -30, acol, sw=2.2))
        p.append(text((ctr(3) + ctr(6)) / 2, yb + 50, note, size=12, color=ncol, bold=True))

    band(92, 140,
         [0, 1, 1, 1, 1, 1, 5, 5], {3: "src", 6: "dst"}, "back",
         "НАЗАД:  w = 7, 6, 5, 4, 3   (правильний 0/1-рюкзак)", TAKE,
         "dp[6] читає dp[3]=1 — стару, з речі A   →   dp[6]=1+4=5    ✓  річ B узято раз", TAKE)

    band(286, 334,
         [0, 1, 1, 4, 5, 5, 8, 1], {3: "srcbug", 6: "bug"}, "fwd",
         "ВПЕРЕД:  w = 3, 4, 5, 6, 7   (помилка — вийде безмежний рюкзак)", BUG,
         "dp[6] читає dp[3]=4 — вже оновлену річчю B!   →   dp[6]=4+4=8    ✗  B узято двічі (6 кг)", BUG)

    render(os.path.join(OUT, "knapsack-direction.svg"), W, H, *p)


if __name__ == "__main__":
    fig_greedy_vs_dp()
    fig_optimal_substructure()
    fig_dp_recipe()
    fig_coin_table()
    fig_longest_path_fail()
    fig_states_vs_paths()
    fig_name_timeline()
    fig_knapsack_table()
    fig_knapsack_direction()
    print("OK: figures written to", OUT)
