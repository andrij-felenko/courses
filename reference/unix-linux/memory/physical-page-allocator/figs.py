# -*- coding: utf-8 -*-
"""Фігури для теми «Фізичні сторінки в ядрі: зони, блоки за порядками й ущільнення»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

GRN_F = "#eafaf0"
BLU_F = "#eaf0fd"
RED_F = "#fdecea"
YEL_F = "#fff5e0"
GRY_F = "#eceff3"


# ── 1. Половинення й приятель ──────────────────────────────────────────────
def fig_buddy_split():
    W, H = 1340, 700
    F = []

    X0, X1 = 250, 1290
    SW = X1 - X0
    ROW_H = 60
    GAP = 44

    rows = [
        (3, 1, BLU_F),
        (2, 2, GRN_F),
        (1, 4, YEL_F),
        (0, 8, RED_F),
    ]

    y = 74
    row_y = {}
    for order, n, col in rows:
        per = 8 // n
        F.append(fitbox(24, y, 200, ROW_H,
                        "порядок %d\n%d %s у блоці" % (order, per, "кадр" if per == 1 else "кадри" if per < 5 else "кадрів"),
                        size=13, fill=FILL))
        w = SW / float(n)
        for i in range(n):
            x = X0 + i * w
            lo = i * per
            hi = lo + per - 1
            lbl = "кадри %d–%d" % (lo, hi) if lo != hi else "кадр %d" % lo
            F.append(fitbox(x + 5, y, w - 10, ROW_H, lbl, size=13, fill=col))
        row_y[order] = y
        y += ROW_H + GAP

    # стрілки половинення між рівнями
    for order in (3, 2, 1):
        n = 8 // (2 ** order)          # скільки блоків на цьому рівні
        w = SW / float(n)
        ytop = row_y[order] + ROW_H
        ybot = row_y[order - 1]
        for i in range(n):
            cx = X0 + i * w + w / 2
            F.append(arrow(cx, ytop + 4, cx, ybot - 6, color=MUTED, sw=1.6))
    F.append(text(150, row_y[2] - GAP / 2 + 4, "половинення", size=13, color=MUTED))

    # нижня панель: правило приятеля
    py = row_y[0] + ROW_H + 46
    F.append(fitbox(24, py, 400, 118,
                    "приятель блоку порядку k,\nщо починається з кадру i:\n\ni ⊕ 2ᵏ",
                    size=15, fill=FILL, bold=True))
    F.append(fitbox(452, py, 400, 118,
                    "кадр 6, порядок 0:\n6 ⊕ 1 = 7 → приятель кадр 7\n\nблок 4–5, порядок 1:\n4 ⊕ 2 = 6 → приятель блок 6–7",
                    size=13, fill=GRN_F))
    F.append(fitbox(880, py, 410, 118,
                    "кадри 5 і 6 обидва вільні,\nале приятель 5 — це 4,\nа приятель 6 — це 7.\nВони не зіллються ніколи.",
                    size=13, fill=RED_F))

    render(os.path.join(IMG, 'buddy-split.svg'), W, H, *F,
           title="Половинення блоків і єдиний можливий приятель")


# ── 2. Форма вільної пам'яті ───────────────────────────────────────────────
def fig_free_shape():
    import math
    W, H = 1400, 660
    F = []

    panels = [
        (30, "щойно після завантаження", GRN_F,
         [120, 80, 55, 40, 28, 20, 14, 9, 6, 4, 3],
         "вільно ≈ 41 МіБ", "найбільший суцільний блок — 4 МіБ"),
        (720, "після місяця роботи", RED_F,
         [4000, 1800, 500, 90, 10, 0, 0, 0, 0, 0, 0],
         "вільно ≈ 41 МіБ", "найбільший суцільний блок — 64 КіБ"),
    ]

    PW = 650
    BAR_X = 150          # відступ від лівого краю панелі до початку смуги
    BAR_MAX = 300
    ROW_H = 34
    TOP = 118

    for px, headline, col, counts, total, biggest in panels:
        F.append(rect(px, 58, PW, 560, fill=BG, stroke=MUTED, sw=1.4))
        F.append(fitbox(px + 14, 68, PW - 28, 38, headline, size=15, fill=col, bold=True))

        top_log = math.log10(max(counts) + 1.0)
        for k, c in enumerate(counts):
            y = TOP + k * ROW_H
            F.append(fitbox(px + 14, y, 118, ROW_H - 6, "порядок %d" % k, size=12, fill=FILL))
            bw = 0.0
            if c > 0:
                bw = max(6.0, BAR_MAX * math.log10(c + 1.0) / top_log)
                F.append(rect(px + BAR_X, y + 3, bw, ROW_H - 12, fill=col, stroke=LINE, sw=1.2, rx=3))
            lbl = "%d блок." % c if c else "немає"
            F.append(text(px + BAR_X + bw + 12, y + ROW_H / 2 + 1, lbl,
                          size=12, color=INK if c else MUTED, anchor="start"))

        F.append(fitbox(px + 14, 522, PW - 28, 40, total, size=14, fill=FILL, bold=True))
        F.append(fitbox(px + 14, 568, PW - 28, 40, biggest, size=14, fill=col))

    render(os.path.join(IMG, 'free-shape.svg'), W, H, *F,
           title="Однакове число вільних байтів — різна форма вільної пам'яті")


# ── 3. Блоки сторінок і рухомість ──────────────────────────────────────────
def fig_pageblock_mobility():
    W, H = 1360, 620
    F = []

    X0 = 40
    N = 24
    CW = (1300 - X0) / float(N)
    CH = 62
    PB = 6                       # кадрів у блоці сторінок (умовно)

    strips = [
        (140, "кадри роздаються впереміш", [3, 9, 14, 20]),
        (400, "кадри розсортовані за рухомістю", [0, 1, 2, 3]),
    ]

    for sy, headline, fixed in strips:
        F.append(text(X0, sy - 22, headline, size=15, bold=True, anchor="start"))
        for i in range(N):
            x = X0 + i * CW
            if i in fixed:
                F.append(rect(x, sy, CW - 3, CH, fill=RED_F, stroke=POS, sw=1.6, rx=3))
            else:
                F.append(rect(x, sy, CW - 3, CH, fill=GRN_F, stroke=FIELD, sw=1.2, rx=3))
        # межі блоків сторінок і вирок під кожним
        for b in range(N // PB):
            bx = X0 + b * PB * CW
            bw = PB * CW - 3
            dirty = any(bx <= X0 + f * CW < bx + bw for f in fixed)
            F.append(line(bx - 3, sy - 8, bx - 3, sy + CH + 8, color=INK, sw=2.4))
            F.append(fitbox(bx, sy + CH + 16, bw, 46,
                            "блок зайнятий назавжди" if dirty else "блок можна звільнити цілком",
                            size=12, fill=RED_F if dirty else GRN_F))
        F.append(line(X0 + N * CW - 3, sy - 8, X0 + N * CW - 3, sy + CH + 8, color=INK, sw=2.4))

    F.append(fitbox(X0, 546, 620, 52,
                    "червоне — нерухомий кадр (структура ядра, закріплений буфер)",
                    size=13, fill=RED_F))
    F.append(fitbox(680, 546, 620, 52,
                    "зелене — рухомий кадр (сторінка процесу, кеш файлу)",
                    size=13, fill=GRN_F))

    render(os.path.join(IMG, 'pageblock-mobility.svg'), W, H, *F,
           title="Один нерухомий кадр псує весь блок — тому кадри сортують наперед")


# ── 4. Два сканери ущільнення ──────────────────────────────────────────────
def fig_compaction():
    W, H = 1340, 620
    F = []

    X0 = 60
    N = 30
    CW = (1280 - X0) / float(N)
    CH = 58

    busy_before = [0, 2, 3, 6, 9, 10, 13, 17, 19, 22, 25, 28]
    busy_after = list(range(N - 12, N))

    def strip(sy, busy, caption):
        F.append(text(X0, sy - 20, caption, size=15, bold=True, anchor="start"))
        for i in range(N):
            x = X0 + i * CW
            occupied = i in busy
            F.append(rect(x, sy, CW - 3, CH,
                          fill=BLU_F if occupied else GRY_F,
                          stroke=NEG if occupied else MUTED,
                          sw=1.6 if occupied else 1.0, rx=3))

    strip(120, busy_before, "до ущільнення: 12 зайнятих кадрів розсипано по зоні")

    # сканери
    F.append(arrow(X0 + 6, 214, X0 + 330, 214, color=NEG, sw=2.2))
    F.append(text(X0 + 8, 240, "сканер міграції збирає рухомі сторінки знизу",
                  size=13, color=NEG, anchor="start"))
    F.append(arrow(X0 + N * CW - 9, 214, X0 + N * CW - 330, 214, color=FIELD, sw=2.2))
    F.append(text(X0 + N * CW - 8, 240, "сканер вільних збирає порожні кадри згори",
                  size=13, color=FIELD, anchor="end"))

    F.append(arrow(W / 2, 268, W / 2, 340, color=INK, sw=2.4))
    F.append(fitbox(W / 2 - 330, 286, 300, 44,
                    "сторінку копіюють у зібраний кадр", size=13, fill=FILL))
    F.append(fitbox(W / 2 + 30, 286, 330, 44,
                    "і правлять усі записи, що на неї вказували", size=13, fill=FILL))

    strip(392, busy_after, "після: згори щільно зайнято, знизу — суцільне вільне поле")

    F.append(fitbox(X0, 486, 560, 52,
                    "зайнятих кадрів стільки ж — 12", size=14, fill=BLU_F))
    F.append(fitbox(X0 + 600, 486, 620, 52,
                    "але тепер збирається блок на 16 кадрів поспіль", size=14, fill=GRN_F))

    render(os.path.join(IMG, 'compaction-scanners.svg'), W, H, *F,
           title="Ущільнення: два сканери йдуть назустріч усередині зони")


# ── 5. Часова шкала: приятелі й поверхи над ними ───────────────────────────
def fig_hist_timeline():
    W, H = 1300, 780
    F = []

    AX = 300                      # вісь часу
    Y0, STEP = 88, 84
    LBL_W, LBL_H = 240, 60
    BOX_X, BOX_W, BOX_H = 356, 900, 60

    rows = [
        ("1963", "RAND, SIMSCRIPT",
         "Harry Markowitz придумує половинення блоків — за Кнутом", YEL_F),
        ("1965", "Bell Labs, CACM 8(10)",
         "Kenneth C. Knowlton друкує «A fast storage allocator»", YEL_F),
        ("2007", "ядро 2.6.24",
         "Mel Gorman: групування сторінок за рухомістю", BLU_F),
        ("2010", "ядро 2.6.35",
         "Mel Gorman: ущільнення пам'яті — два зустрічні сканери", GRN_F),
        ("2012", "ядро 3.5",
         "CMA (Samsung Poland); lumpy reclaim прибрано", GRN_F),
        ("2016", "ядро 4.6",
         "Vlastimil Babka: фонова нитка kcompactd", GRN_F),
        ("2020", "ядро 5.9",
         "Nitin Gupta: випереджальне ущільнення", GRN_F),
        ("2023–24", "ядра 6.4 і 6.8",
         "MAX_ORDER стає включним і зветься MAX_PAGE_ORDER", RED_F),
    ]

    ylast = Y0 + (len(rows) - 1) * STEP + LBL_H / 2
    F.append(line(AX, Y0 - 16, AX, ylast + 20, color=MUTED, sw=2.2))

    for i, (year, where, what, col) in enumerate(rows):
        cy = Y0 + i * STEP + LBL_H / 2
        F.append(fitbox(AX - 24 - LBL_W, cy - LBL_H / 2, LBL_W, LBL_H,
                        "%s\n%s" % (year, where), size=14, fill=GRY_F))
        F.append(circle(AX, cy, 7, fill=col, stroke=INK, sw=2))
        F.append(line(AX + 7, cy, BOX_X - 6, cy, color=MUTED, sw=1.6))
        F.append(fitbox(BOX_X, cy - BOX_H / 2, BOX_W, BOX_H, what, size=15, fill=col))

    F.append(fitbox(AX - 24 - LBL_W, ylast + 34, LBL_W + 24 + BOX_W, 46,
                    "алгоритм лишився той самий — навколо нього наростили поверхи",
                    size=15, fill=FILL))

    render(os.path.join(IMG, 'hist-timeline.svg'), W, H, *F,
           title="Шість десятиліть навколо системи приятелів")


# ── 6. Карта рішення індексу фрагментації ──────────────────────────────────
def fig_fragindex_map():
    W, H = 1140, 820
    F = []

    X0, PW = 320.0, 700.0          # вісь x: частка s/R від 0 до 0.75
    Y1, PH = 680.0, 540.0          # вісь y: 1/B від 0 (низ) до 1 (верх)
    XMAX = 0.75

    def PX(x):
        return X0 + (x / XMAX) * PW

    def PY(y):
        return Y1 - y * PH

    # осі
    F.append(line(X0, Y1, X0 + PW + 20, Y1, color=MUTED, sw=2.0))
    F.append(line(X0, Y1, X0, Y1 - PH - 10, color=MUTED, sw=2.0))

    # стіна s = R/2
    F.append(line(PX(0.5), Y1 - PH, PX(0.5), Y1, color=MUTED, sw=2.0, dash="5,5"))
    F.append(fitbox(PX(0.5), Y1 - PH + 10, PX(XMAX) - PX(0.5), PH - 20,
                    "недосяжно:\nтут знайшовся б\nпридатний блок,\nа тоді індекс = −1000",
                    size=13, fill=GRY_F, color=MUTED))

    # межа індекс = 0  (s/R + 1/B = 1)  і межа індекс = 500  (s/R + 1/B = 0.5)
    F.append(line(PX(0.0), PY(1.0), PX(0.5), PY(0.5), color=INK, sw=2.2))
    F.append(line(PX(0.0), PY(0.5), PX(0.5), PY(0.0), color=INK, sw=2.0, dash="8,6"))

    # підписи областей
    F.append(fitbox(335, 585, 230, 70, "індекс > 500\nущільнювати", size=16, fill=GRN_F))
    F.append(fitbox(440, 379, 240, 70, "0 ≤ індекс ≤ 500\nвитісняти", size=16, fill=YEL_F))
    F.append(fitbox(525, 161, 250, 70, "індекс < 0\nу зоні один вільний блок", size=15, fill=RED_F))

    # поділки осі x
    for xv, lbl in ((0.0, "0"), (0.25, "R/4"), (0.5, "R/2")):
        F.append(line(PX(xv), Y1, PX(xv), Y1 + 6, color=MUTED, sw=1.6))
        F.append(text(PX(xv), Y1 + 24, lbl, size=13, color=MUTED))

    # поділки осі y
    for yv, lbl in ((0.0, "багато блоків"), (0.25, "B = 4"), (0.5, "B = 2"), (1.0, "B = 1")):
        F.append(line(X0 - 6, PY(yv), X0, PY(yv), color=MUTED, sw=1.6))
        F.append(text(X0 - 12, PY(yv) + 5, lbl, size=13, color=MUTED, anchor="end"))

    F.append(mtext(150, 350, ["1 / B", "(доданок, що", "ловить брак", "пам'яті)"],
                   size=13, color=MUTED))
    F.append(mtext(680, 726,
                   ["середній розмір вільного блоку  s = free_pages / free_blocks_total,",
                    "у частках від розміру запиту  R = 2 в степені порядку"],
                   size=14, color=MUTED))
    F.append(fitbox(250, 764, 860, 40,
                    "суцільна межа — індекс = 0 · штрихова — індекс = 500, типове vm.extfrag_threshold",
                    size=14, fill=FILL, color=MUTED))

    render(os.path.join(IMG, 'fragindex-map.svg'), W, H, *F,
           title="індекс / 1000 = 1 − s/R − 1/B: де проходять обидві межі")


# ── 7. Розклад індексу на два доданки, чотири зони ─────────────────────────
def fig_fragindex_split():
    W, H = 1300, 540
    F = []

    BX, BW = 390.0, 640.0
    ROW0, STEP, BH = 120.0, 90.0, 54.0

    F.append(fitbox(BX, 52, 200, 36, "s / R", size=15, fill=BLU_F))
    F.append(fitbox(BX + 210, 52, 200, 36, "1 / B", size=15, fill=YEL_F))
    F.append(fitbox(BX + 420, 52, 220, 36, "індекс / 1000", size=15, fill=GRN_F))

    rows = [
        ("≈1 ГіБ вільно\n8000 блоків по 128 КіБ", 0.0625, 0.000125, "індекс 938\nущільнювати"),
        ("≈4 ГіБ вільно\n8000 блоків по 512 КіБ", 0.25,   0.000125, "індекс 750\nущільнювати"),
        ("1 МіБ вільно\n2 блоки по 512 КіБ",      0.25,   0.5,      "індекс 250\nвитісняти"),
        ("2 МіБ вільно\n2 блоки по 1 МіБ",        0.5,    0.5,      "індекс 0\nвитісняти"),
    ]

    for i, (left, sr, ib, right) in enumerate(rows):
        y = ROW0 + i * STEP
        F.append(fitbox(40, y - 4, 330, 62, left, size=15, fill=GRY_F))
        F.append(fitbox(1050, y - 4, 210, 62, right, size=15, fill=FILL))
        x = BX
        for frac, col in ((sr, BLU_F), (ib, YEL_F), (max(0.0, 1.0 - sr - ib), GRN_F)):
            w = frac * BW
            if w >= 3.0:
                F.append(rect(x, y, w, BH, fill=col, sw=1.4, rx=3))
            x += w

    # лінійка часток
    RY = 470.0
    F.append(line(BX, RY, BX + BW, RY, color=MUTED, sw=1.6))
    for frac, lbl in ((0.0, "0"), (0.5, "0.500"), (1.0, "1.000")):
        F.append(line(BX + frac * BW, RY, BX + frac * BW, RY + 6, color=MUTED, sw=1.6))
        F.append(text(BX + frac * BW, RY + 26, lbl, size=13, color=MUTED))

    render(os.path.join(IMG, 'fragindex-split.svg'), W, H, *F,
           title="Запит на 2 МіБ (порядок 9): з чого складається одиниця")


# ── 8. Від nr_free до avail(k) ─────────────────────────────────────────────
def fig_avail_ladder():
    W, H = 1300, 800
    F = []

    nr = [88214, 19842, 6120, 1544, 306, 58, 11, 3, 0, 0, 0]
    avail = [0] * len(nr)
    acc = 0
    for k in range(len(nr) - 1, -1, -1):
        acc = acc * 2 + nr[k]
        avail[k] = acc

    X_K, W_K = 36, 130
    X_N, W_N = 182, 300
    X_A, W_A = 500, 330
    ROW_H, GAP = 42, 6
    TOP = 134

    F.append(fitbox(X_K, 56, W_K, 62, "порядок\nk", size=14, fill=GRY_F, bold=True))
    F.append(fitbox(X_N, 56, W_N, 62, "nr_free[k]\nстовпець рядка buddyinfo",
                    size=13, fill=GRY_F, bold=True))
    F.append(fitbox(X_A, 56, W_A, 62, "avail(k)\nблоків порядку k ще дістану",
                    size=13, fill=GRY_F, bold=True))

    for i in range(len(nr)):
        k = len(nr) - 1 - i                      # згори вниз: 10 → 0
        y = TOP + i * (ROW_H + GAP)
        col = GRN_F if avail[k] else RED_F
        F.append(fitbox(X_K, y, W_K, ROW_H, "%d" % k, size=15, fill=FILL, bold=True))
        F.append(fitbox(X_N, y, W_N, ROW_H, "%d" % nr[k], size=14, fill=FILL))
        F.append(fitbox(X_A, y, W_A, ROW_H, "%d" % avail[k], size=15, fill=col, bold=True))

    AX = X_A + W_A + 28
    for i in range(len(nr) - 1):
        y1 = TOP + i * (ROW_H + GAP) + ROW_H
        y2 = TOP + (i + 1) * (ROW_H + GAP)
        F.append(arrow(AX, y1 + 1, AX, y2 - 3, color=NEG, sw=1.6))

    NX, NW = AX + 24, 366
    F.append(fitbox(NX, TOP + 4, NW, 124,
                    "avail(k) = 2·avail(k+1) + nr_free[k]\n\n"
                    "вільний блок порядку k+1 — це\nрівно два блоки порядку k,\n"
                    "і розділити їх нічого не коштує",
                    size=13, fill=BLU_F))
    F.append(fitbox(NX, TOP + 156, NW, 96,
                    "avail(9) = 0\nвелика сторінка не складеться\nні з чого — просто зараз",
                    size=13, fill=RED_F))
    F.append(fitbox(NX, TOP + 280, NW, 96,
                    "avail(0) = 172570\nце і є всі вільні кадри зони,\n674.1 МіБ",
                    size=13, fill=GRN_F))

    F.append(fitbox(X_K, TOP + 11 * (ROW_H + GAP) + 20, W - 2 * X_K, 56,
                    "число праворуч — стеля, а не обіцянка: позначки зон, тип рухомості "
                    "й резерви ще можуть відмовити",
                    size=14, fill=YEL_F))

    render(os.path.join(IMG, 'avail-ladder.svg'), W, H, *F,
           title="Від стовпців buddyinfo до відповіді «скільки блоків порядку k ще дістану»")


# ── 9. Прогноз проти дійсності ─────────────────────────────────────────────
def fig_predict_vs_reality():
    W, H = 1360, 660
    F = []

    cols = [
        (30, 262, "прогін"),
        (308, 232, "avail(9)\nпрогноз"),
        (556, 240, "великих сторінок дано\nз 128 запитаних"),
        (812, 226, "приріст\ncompact_stall"),
        (1054, 276, "хто за це заплатив"),
    ]
    for x, w, title in cols:
        F.append(fitbox(x, 54, w, 76, title, size=13, fill=GRY_F, bold=True))

    rows = [
        ("defrag = never", "0", "0", "0", "ніхто —\nпросто відмова", RED_F),
        ("defrag = madvise", "0", "96", "112", "сама програма,\nу своєму потоці", YEL_F),
        ("defrag = never,\nпісля compact_memory", "104", "101", "0",
         "той, хто писав\nу sysctl", GRN_F),
    ]

    y = 162
    ROW_H, ROW_GAP = 106, 18
    for label, pred, got, stall, who, col in rows:
        F.append(fitbox(cols[0][0], y, cols[0][1], ROW_H, label, size=14, fill=col, bold=True))
        F.append(fitbox(cols[1][0], y, cols[1][1], ROW_H, pred, size=17, fill=FILL, bold=True))
        F.append(fitbox(cols[2][0], y, cols[2][1], ROW_H, got, size=17, fill=FILL, bold=True))
        F.append(fitbox(cols[3][0], y, cols[3][1], ROW_H, stall, size=15, fill=FILL))
        F.append(fitbox(cols[4][0], y, cols[4][1], ROW_H, who, size=13, fill=FILL))
        y += ROW_H + ROW_GAP

    F.append(fitbox(30, y + 6, W - 60, 62,
                    "прогноз збігається з дійсністю лише там, де ніхто нишком не ущільнює: "
                    "другий рядок дав 96 сторінок, хоч вільних блоків не було зовсім",
                    size=14, fill=BLU_F))

    render(os.path.join(IMG, 'predict-vs-reality.svg'), W, H, *F,
           title="Той самий зонд у трьох різних станах системи")


# ── Позначки рівня зони (довідник регуляторів) ─────────────────────────────
def fig_watermark_bands():
    W, H = 1360, 620
    F = []

    X0, X1 = 110.0, 1290.0
    SCALE = 20000.0            # скільки сторінок вкладається у всю вісь
    AX = 300.0                 # рівень осі

    def px(v):
        return X0 + (v / SCALE) * (X1 - X0)

    marks = [
        (4096,  "min",   "4 096 · 16.0 МіБ"),
        (8290,  "low",   "8 290 · 32.4 МіБ"),
        (12484, "high",  "12 484 · 48.8 МіБ"),
        (16678, "promo", "16 678 · 65.1 МіБ"),
    ]
    xs = [px(v) for v, _, _ in marks]

    bands = [
        (X0,    xs[0], RED_F, "нижче min\nлише GFP_ATOMIC\nі __GFP_HIGH"),
        (xs[0], xs[1], YEL_F, "min…low\nпрямий відбір\nу потоці прохача"),
        (xs[1], xs[2], BLU_F, "low…high\nkswapd прокинувся\nй працює"),
        (xs[2], xs[3], GRN_F, "high…promo\nшвидкий шлях,\nніхто не будиться"),
        (xs[3], X1,    GRY_F, "вище promo\nє запас під\nпідвищення сторінок"),
    ]
    for x1, x2, col, lbl in bands:
        F.append(fitbox(x1 + 6, 150, x2 - x1 - 12, 100, lbl, size=14, fill=col))

    F.append(arrow(X0, AX, X1 + 10, AX, color=INK, sw=2.0))
    F.append(text((xs[1] + xs[2]) / 2, AX + 36, "вільних сторінок у зоні →",
                  size=13, color=MUTED))

    for (v, name, val), x in zip(marks, xs):
        F.append(line(x, 250, x, 356, color=MUTED, sw=1.6, dash="4,4"))
        F.append(fitbox(x - 95, 366, 190, 62, name + "\n" + val, size=14, fill=FILL))

    for i in range(3):
        a, b = xs[i], xs[i + 1]
        F.append(arrow(a + 4, 480, b - 4, 480, color=NEG, sw=1.6))
        F.append(arrow(b - 4, 480, a + 4, 480, color=NEG, sw=1.6))
        F.append(text((a + b) / 2, 462, "Δ", size=15, color=NEG, bold=True))

    for cx, txt, col in ((232, "місце min задає\nmin_free_kbytes", YEL_F),
                         (723, "Δ = managed · watermark_scale_factor / 10000", BLU_F),
                         (1150, "watermark_boost тимчасово\nсуне всі три вправо", GRN_F)):
        body, _, _ = textbox(cx, 552, txt, size=13, fill=col)
        F.append(body)

    render(os.path.join(IMG, 'watermark-bands.svg'), W, H, *F,
           title="Позначки рівня однієї зони: 16 ГіБ, типові min_free_kbytes і watermark_scale_factor")


if __name__ == '__main__':
    fig_buddy_split()
    fig_free_shape()
    fig_pageblock_mobility()
    fig_compaction()
    fig_hist_timeline()
    fig_fragindex_map()
    fig_fragindex_split()
    fig_avail_ladder()
    fig_predict_vs_reality()
    fig_watermark_bands()
    print("ok")
