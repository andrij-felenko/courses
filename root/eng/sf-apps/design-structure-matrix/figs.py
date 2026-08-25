# -*- coding: utf-8 -*-
"""Фігури до теми «Матриця залежностей (DSM)»."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

GRID = "#b9c0c9"
DIAG = "#dfe4ea"
MARK = "#33415c"
TINT_R = "#eaf2ff"
TINT_C = "#e9f8ee"


def grid(x0, y0, cell, n, labels=None, marks=(), feedback=(),
         tint_rows=(), tint_cols=(), lab_size=13, inset=None):
    """Сітка n×n. marks/feedback — множини пар (рядок, стовпець)."""
    out = []
    if inset is None:
        inset = max(4.0, cell * 0.24)
    # підсвітка рядків і стовпців
    for i in tint_rows:
        out.append(rect(x0, y0 + i * cell, n * cell, cell,
                        fill=TINT_R, stroke="none", sw=0, rx=0))
    for j in tint_cols:
        out.append(rect(x0 + j * cell, y0, cell, n * cell,
                        fill=TINT_C, stroke="none", sw=0, rx=0))
    # діагональ
    for i in range(n):
        out.append(rect(x0 + i * cell, y0 + i * cell, cell, cell,
                        fill=DIAG, stroke="none", sw=0, rx=0))
    # позначки
    for (i, j), color in [(m, MARK) for m in marks] + [(m, POS) for m in feedback]:
        out.append(rect(x0 + j * cell + inset, y0 + i * cell + inset,
                        cell - 2 * inset, cell - 2 * inset,
                        fill=color, stroke="none", sw=0, rx=max(1, int(cell * 0.08))))
    # лінії сітки
    for k in range(n + 1):
        w = 1.6 if k in (0, n) else 0.9
        out.append(line(x0, y0 + k * cell, x0 + n * cell, y0 + k * cell, color=GRID, sw=w))
        out.append(line(x0 + k * cell, y0, x0 + k * cell, y0 + n * cell, color=GRID, sw=w))
    # підписи
    if labels:
        for i, nm in enumerate(labels):
            out.append(text(x0 - 12, y0 + i * cell + cell / 2 + lab_size * 0.36, nm,
                            size=lab_size, anchor="end", color=INK))
            out.append(text(x0 + i * cell + cell / 2, y0 - 14, nm,
                            size=lab_size, anchor="middle", color=INK))
    return "".join(out)


def block(x0, y0, cell, a, b, color=FIELD, sw=3.0):
    """Рамка навколо блоку рядків/стовпців a..b включно."""
    return rect(x0 + a * cell - 2, y0 + a * cell - 2,
                (b - a + 1) * cell + 4, (b - a + 1) * cell + 4,
                fill="none", stroke=color, sw=sw, rx=3)


# ── 1. Як читати матрицю ────────────────────────────────────────────────────
def fig_anatomy():
    W, H = 900, 620
    cell, n = 48, 5
    x0, y0 = 330, 190
    lab = ["A", "B", "C", "D", "E"]
    marks = [(1, 0), (2, 0), (2, 1), (3, 1), (3, 2), (4, 0), (4, 3)]
    fb = [(0, 4)]
    f = [grid(x0, y0, cell, n, lab, marks, fb, tint_rows=[3], tint_cols=[1])]

    # праворуч: рядок (на висоті рядка D) і зворотна позначка (на висоті рядка A)
    yr = y0 + 3 * cell + cell / 2
    f.append(line(x0 + n * cell + 6, yr, 640, yr, color=MUTED, sw=1.4))
    bx, _, _ = textbox(748, yr, ["рядок D: що потрібно", "самому елементові D"], size=13)
    f.append(bx)

    ya = y0 + cell / 2
    f.append(line(x0 + n * cell + 6, ya, 640, ya, color=POS, sw=1.4))
    bx, _, _ = textbox(752, ya, ["позначка вище діагоналі:", "A потребує пізнішого E"],
                       size=13, stroke=POS, fill="#fdecea")
    f.append(bx)

    # згори: стовпець
    xc = x0 + 1 * cell + cell / 2
    f.append(line(xc, 128, xc, y0 - 36, color=MUTED, sw=1.4))
    bx, _, _ = textbox(xc, 100, ["стовпець B: хто потребує", "самого елемента B"], size=13)
    f.append(bx)

    # знизу: нижня половина і діагональ
    f.append(line(390, 486, 366, y0 + n * cell + 6, color=MUTED, sw=1.4))
    bx, _, _ = textbox(300, 528, ["позначки нижче діагоналі:", "залежність від того,",
                                  "хто стоїть раніше"], size=13)
    f.append(bx)

    f.append(line(660, 486, 574, y0 + n * cell + 4, color=MUTED, sw=1.4))
    bx, _, _ = textbox(716, 528, ["діагональ: елемент", "сам із собою — порожня"], size=13)
    f.append(bx)

    render(os.path.join(OUT, "anatomy.svg"), W, H, *f,
           title="Як читати матрицю залежностей: рядок потребує стовпця")


# ── 2. Граф проти матриці ───────────────────────────────────────────────────
EDGES = [(1, 0), (2, 0), (2, 1), (3, 1), (3, 0), (4, 2), (4, 3), (5, 3), (5, 4),
         (7, 6), (8, 6), (8, 7), (9, 7), (10, 8), (10, 9), (11, 9), (11, 10),
         (9, 4), (6, 2), (11, 5),
         (0, 12), (3, 12), (4, 12), (6, 12), (8, 12), (9, 12), (11, 12),
         (13, 5), (13, 11), (13, 12)]


def fig_graph_vs_matrix():
    W, H = 980, 530
    f = []
    # ліва панель: коло з 14 вузлів
    f.append(rect(30, 70, 440, 400, fill="#fcfcfd", stroke=GRID, sw=1.2, rx=10))
    cx, cy, r = 250, 272, 152
    pos = {}
    for k in range(14):
        a = -math.pi / 2 + 2 * math.pi * k / 14
        pos[k] = (cx + r * math.cos(a), cy + r * math.sin(a))
    for (i, j) in EDGES:
        x1, y1 = pos[i]
        x2, y2 = pos[j]
        f.append(line(x1, y1, x2, y2, color="#9aa3ad", sw=1.1))
    for k in range(14):
        x, y = pos[k]
        f.append(circle(x, y, 10, fill="#ffffff", stroke=MARK, sw=1.6))
    f.append(text(250, 56, "граф: 14 вузлів, 30 дуг", size=14, bold=True))

    # права панель: та сама система матрицею
    f.append(rect(510, 70, 440, 400, fill="#fcfcfd", stroke=GRID, sw=1.2, rx=10))
    order = [12, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13]
    ipos = {v: k for k, v in enumerate(order)}
    marks = [(ipos[i], ipos[j]) for (i, j) in EDGES]
    f.append(grid(548, 96, 26, 14, None, marks))
    f.append(text(730, 56, "матриця: 14 × 14", size=14, bold=True))

    render(os.path.join(OUT, "graph-vs-matrix.svg"), W, H, *f,
           title="Однакові відомості у двох формах")


# ── 3. Розбиття ─────────────────────────────────────────────────────────────
def fig_partition():
    W, H = 960, 480
    cell, n = 46, 6
    f = []

    labA = ["bil", "cfg", "db", "htp", "log", "ord"]
    mA = [(0, 2), (0, 5), (2, 1), (2, 4), (3, 0), (3, 4), (3, 5),
          (4, 1), (5, 0), (5, 2), (5, 4)]
    fbA = [(0, 2), (0, 5), (2, 4), (3, 5)]
    mA = [m for m in mA if m not in fbA]
    f.append(grid(120, 150, cell, n, labA, mA, fbA))
    f.append(text(258, 106, "порядок за абеткою", size=15, bold=True))
    f.append(text(258, 458, "позначок вище діагоналі: 4", size=13, color=POS))

    labB = ["cfg", "log", "db", "ord", "bil", "htp"]
    mB = [(1, 0), (2, 0), (2, 1), (3, 1), (3, 2), (4, 2), (4, 3),
          (5, 1), (5, 3), (5, 4)]
    fbB = [(3, 4)]
    f.append(grid(600, 150, cell, n, labB, mB, fbB))
    f.append(block(600, 150, cell, 3, 4))
    f.append(text(738, 106, "після розбиття", size=15, bold=True))
    f.append(text(738, 458, "одна позначка — усередині блоку", size=13, color=POS))

    render(os.path.join(OUT, "partition.svg"), W, H, *f,
           title="Одночасне переставляння рядків і стовпців нічого не змінює в системі")


# ── 4. Групування і спільна шина ────────────────────────────────────────────
def fig_cluster():
    W, H = 900, 700
    cell, n = 42, 10
    x0, y0 = 270, 152
    lab = ["cfg", "cart", "ord", "pay", "ship", "usr", "auth", "sess", "perm", "http"]
    marks = [(1, 0), (2, 0), (3, 0), (5, 0), (6, 0), (7, 0), (9, 0),
             (2, 1), (3, 1), (3, 2), (4, 2), (4, 3),
             (6, 5), (7, 5), (7, 6), (8, 6), (8, 7),
             (5, 2), (6, 3),
             (9, 4), (9, 8)]
    f = [grid(x0, y0, cell, n, lab, marks)]
    f.append(block(x0, y0, cell, 1, 4))
    f.append(block(x0, y0, cell, 5, 8))
    f.append(text(x0 + 3 * cell, 100, "модуль замовлень", size=14, bold=True, color=FIELD))
    f.append(text(x0 + 7 * cell, 100, "модуль доступу", size=14, bold=True, color=FIELD))

    xb = x0 + cell / 2
    f.append(line(xb, y0 + n * cell + 6, xb, 604, color=MUTED, sw=1.4))
    bx, _, _ = textbox(xb + 40, 638, ["перший стовпець заповнений:",
                                      "цей елемент потрібен усім — спільна шина"], size=13)
    f.append(bx)

    render(os.path.join(OUT, "cluster-bus.svg"), W, H, *f,
           title="Групування: позначки збираються у квадрати біля діагоналі")


# ── 5. Три прочитання однієї матриці (вставка про історію) ──────────────────
def fig_three_readings():
    W, H = 1040, 450
    cell, n = 38, 5
    y0 = 160
    marks = [(1, 0), (2, 1), (3, 2), (4, 2), (4, 3)]
    fb = [(3, 4)]

    panels = [
        (120, "1965 — рівняння", ["x1", "x2", "x3", "x4", "x5"],
         "позначка: рівняння", "містить це невідоме"),
        (460, "1981 — задачі проєкту", ["A", "B", "C", "D", "E"],
         "позначка: задача чекає", "на результат іншої"),
        (800, "2005 — модулі коду", ["cfg", "log", "db", "ord", "bil"],
         "позначка: модуль", "імпортує інший"),
    ]

    f = []
    for x0, title, lab, c1, c2 in panels:
        f.append(grid(x0, y0, cell, n, lab, marks, fb, lab_size=12))
        f.append(block(x0, y0, cell, 3, 4))
        cx = x0 + n * cell / 2
        f.append(text(cx, 112, title, size=15, bold=True))
        f.append(text(cx, 382, c1, size=12, color=MUTED))
        f.append(text(cx, 400, c2, size=12, color=MUTED))

    f.append(text(W / 2, 432, "той самий блок на діагоналі — те саме місце, "
                              "де порядок неможливий", size=13, color=POS))

    render(os.path.join(OUT, "three-readings.svg"), W, H, *f,
           title="Одна матриця, три предмети: рівняння, задачі, модулі")


# ── 6. Конвеєр програми розбиття (вставка proj) ─────────────────────────────
def fig_pipeline():
    W, H = 940, 770
    x0, bw, bh = 40, 270, 68
    stages = [
        ("1 · читання й нумерація",
         ["імена за абеткою → номери", "дуги без дублікатів і петель"],
         "O(E) + O(n log n)"),
        ("2 · дуги → CSR",
         ["head[] і to[]: сусіди підряд", "у пам'яті, списки впорядковані"],
         "O(E log E)"),
        ("3 · Тарджан без рекурсії",
         ["comp[v]; блоки вийшли одразу", "в топологічному порядку"],
         "O(n + E)"),
        ("4 · конденсація",
         ["граф блоків — без циклів", "за побудовою"],
         "O(n + E)"),
        ("5 · канонічний порядок",
         ["порядок, стійкий до появи", "нового модуля"],
         "O(C log C + Ec)"),
        ("6 · видимість на бітах",
         ["маска блоків для кожного блоку", "і вартість поширення"],
         "O(Ec · C / 64)"),
    ]
    f = [text(x0 + bw / 2, 76, "етап", size=13, bold=True, color=MUTED),
         text(340, 76, "що дає", size=13, bold=True, color=MUTED, anchor="start"),
         text(900, 76, "ціна", size=13, bold=True, color=MUTED, anchor="end")]
    for i, (nm, gives, cost) in enumerate(stages):
        y = 96 + i * 108
        f.append(fitbox(x0, y, bw, bh, nm, size=15, bold=True))
        f.append(mtext(340, y + 30, gives, size=13, anchor="start"))
        f.append(text(900, y + 39, cost, size=13, color=MUTED, anchor="end"))
        if i + 1 < len(stages):
            f.append(arrow(x0 + bw / 2, y + bh + 6, x0 + bw / 2, y + 102,
                           color=MUTED, sw=1.6))
    render(os.path.join(OUT, "partition-pipeline.svg"), W, H, *f,
           title="Від переліку залежностей до вартості поширення")


# ── 7. Видимість блоків OR-ом бітових масок (вставка proj) ──────────────────
def fig_visibility():
    W, H = 900, 520
    x0, cell = 250, 34
    rows = [
        ("B1  config",         {0},             "= сам",           "1 елемент"),
        ("B2  log",            {0, 1},          "= сам ⋁ B1",      "2 елементи"),
        ("B3  db",             {0, 1, 2},       "= сам ⋁ B1 ⋁ B2", "3 елементи"),
        ("B4  billing, order", {0, 1, 2, 3},    "= сам ⋁ B2 ⋁ B3", "5 елементів (у блоці 2)"),
        ("B5  http",           {0, 1, 2, 3, 4}, "= сам ⋁ B2 ⋁ B4", "6 елементів"),
    ]
    f = []
    for j in range(5):
        f.append(text(x0 + j * cell + cell / 2, 88, "B%d" % (j + 1),
                      size=12, color=MUTED))
    for i, (lab, bits, formula, count) in enumerate(rows):
        y = 108 + i * 62
        f.append(text(236, y + 22, lab, size=13, anchor="end"))
        for j in range(5):
            f.append(rect(x0 + j * cell, y, cell, cell,
                          fill=(MARK if j in bits else "#ffffff"),
                          stroke=GRID, sw=1.1, rx=2))
        f.append(text(450, y + 22, formula, size=13, anchor="start"))
        f.append(text(870, y + 22, count, size=13, color=MUTED, anchor="end"))
    bx, _, _ = textbox(450, 470,
                       ["сума за елементами: 1 + 2 + 3 + 5 + 5 + 6 = 22",
                        "вартість поширення = 22 / 6² ≈ 61 %"], size=13)
    f.append(bx)
    render(os.path.join(OUT, "visibility-blocks.svg"), W, H, *f,
           title="Видимість рахується раз на блок і множиться на його розмір")


# ── 8. Степені матриці й накопичене замикання (вставка math) ────────────────
LAB6 = ["cfg", "log", "db", "ord", "bil", "htp"]

POW_A = [(1, 0), (2, 0), (2, 1), (3, 1), (3, 2), (3, 4),
         (4, 2), (4, 3), (5, 1), (5, 3), (5, 4)]
POW_A2 = [(2, 0),
          (3, 0), (3, 1), (3, 2), (3, 3),
          (4, 0), (4, 1), (4, 2), (4, 4),
          (5, 0), (5, 1), (5, 2), (5, 3), (5, 4)]
POW_A3 = [(3, 0), (3, 1), (3, 2), (3, 4),
          (4, 0), (4, 1), (4, 2), (4, 3),
          (5, 0), (5, 1), (5, 2), (5, 3), (5, 4)]
VIS6 = [(0, 0),
        (1, 0), (1, 1),
        (2, 0), (2, 1), (2, 2),
        (3, 0), (3, 1), (3, 2), (3, 3), (3, 4),
        (4, 0), (4, 1), (4, 2), (4, 3), (4, 4),
        (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5)]


def fig_closure_powers():
    W, H = 950, 320
    cell, n = 26, 6
    y0 = 112
    xs = [96, 312, 528, 744]
    titles = ["A", "A²", "A³", "V = I ⋁ A ⋁ A² ⋁ …"]
    sets = [POW_A, POW_A2, POW_A3, VIS6]
    f = []
    for k, (x0, ttl, ms) in enumerate(zip(xs, titles, sets)):
        f.append(grid(x0, y0, cell, n, LAB6 if k == 0 else None, ms, lab_size=11))
        f.append(text(x0 + n * cell / 2, 66, ttl, size=15, bold=True))
    f.append(text(475, 300,
                  "маршрут довжини рівно k живе в Aᵏ; маршрут будь-якої довжини — у V",
                  size=13, color=MUTED))
    render(os.path.join(OUT, "closure-powers.svg"), W, H, *f,
           title="Степені булевої матриці й накопичене замикання")


# ── 9. Блочна будова матриці видимості (вставка math) ───────────────────────
BLK_FILL = "#dce8fa"
BLK_DIAG = "#b6d0f0"


def block_matrix(x0, y0, cell, sizes, reach):
    """Матриця видимості блоками: reach — пари (a, b), «клас a дістає клас b»."""
    starts, acc = [], 0
    for s in sizes:
        starts.append(acc)
        acc += s
    n = acc
    out = []
    for (a, b) in reach:
        out.append(rect(x0 + starts[b] * cell, y0 + starts[a] * cell,
                        sizes[b] * cell, sizes[a] * cell,
                        fill=(BLK_DIAG if a == b else BLK_FILL),
                        stroke="none", sw=0, rx=0))
    for k in range(n + 1):
        w = 1.4 if k in (0, n) else 0.7
        out.append(line(x0, y0 + k * cell, x0 + n * cell, y0 + k * cell, color=GRID, sw=w))
        out.append(line(x0 + k * cell, y0, x0 + k * cell, y0 + n * cell, color=GRID, sw=w))
    for p in starts:
        out.append(line(x0, y0 + p * cell, x0 + n * cell, y0 + p * cell, color=MARK, sw=2.0))
        out.append(line(x0 + p * cell, y0, x0 + p * cell, y0 + n * cell, color=MARK, sw=2.0))
    return out, starts, n


def fig_visibility_rectangles():
    W, H = 1000, 560
    f = []

    # ліва панель: справжня V наскрізного прикладу
    cell, n = 42, 6
    x0, y0 = 120, 140
    f.append(grid(x0, y0, cell, n, LAB6, VIS6, tint_rows=[3, 4]))
    f.append(block(x0, y0, cell, 3, 4))
    f.append(text(x0 + n * cell / 2, 96, "матриця видимості V", size=15, bold=True))
    bx, _, _ = textbox(x0 + n * cell / 2, 468,
                       ["рядки ord і bil збігаються клітинка в клітинку —",
                        "вони в одному класі взаємної досяжності"], size=13)
    f.append(bx)

    # права панель: та сама будова взагалі
    cell2, sizes = 30, [1, 3, 2, 2]
    reach = [(a, b) for a in range(4) for b in range(4) if a >= b]
    x1, y1 = 640, 140
    frags, starts, n2 = block_matrix(x1, y1, cell2, sizes, reach)
    f += frags
    f.append(text(x1 + n2 * cell2 / 2, 96, "блочна будова взагалі", size=15, bold=True))
    for k, s in enumerate(sizes):
        cy = y1 + (starts[k] + s / 2) * cell2
        f.append(text(x1 - 14, cy + 5, "C%d" % (k + 1), size=12, anchor="end"))
        cx = x1 + (starts[k] + s / 2) * cell2
        f.append(text(cx, y1 - 12, str(s), size=12, color=MUTED))
    f.append(text(x1 + n2 * cell2 / 2, y1 - 34, "розміри класів", size=12, color=MUTED))

    ax = x1 + (starts[1] + sizes[1] / 2) * cell2
    ay = y1 + (starts[2] + sizes[2] / 2) * cell2
    f.append(line(ax, ay, ax - 40, 418, color=MUTED, sw=1.4))
    bx, _, _ = textbox(x1 + n2 * cell2 / 2, 452,
                       ["прямокутник заповнений цілком,",
                        "його площа — |C₃|·|C₂| = 2·3 = 6"], size=13)
    f.append(bx)
    f.append(text(W / 2, 532, "|V| = Σ |C|·|D| по всіх парах класів, де C дістає D",
                  size=14, bold=True))

    render(os.path.join(OUT, "visibility-rectangles.svg"), W, H, *f,
           title="Матриця видимості складається із суцільних прямокутників")


fig_anatomy()
fig_graph_vs_matrix()
fig_partition()
fig_cluster()
fig_three_readings()
fig_pipeline()
fig_visibility()
fig_closure_powers()
fig_visibility_rectangles()
print("ok")
