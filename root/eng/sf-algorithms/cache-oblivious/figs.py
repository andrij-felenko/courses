# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── model: модель ідеального кеша + лінійний скан ─────────────────────────────
# Ідея: ліворуч два рівні (швидкий кеш лініями по B над повільною пам'яттю) і
# єдине, що ми рахуємо, — пересилання блоку; праворуч скан N комірок = N/B промахів.

def fig_model():
    W, H = 820, 400
    p = []

    # ── ліва панель: два рівні ──
    cx = 210
    p.append(text(cx, 58, "Що рахуємо: пересилання блоків", size=12.5, color=INK, bold=True))

    # кеш зверху: 3 лінії по 5 комірок
    kx, ky = 96, 78
    cellw, cellh = 36, 22
    rows, cols = 3, 5
    p.append(rect(kx - 8, ky - 8, cols * cellw + 16, rows * (cellh + 8) + 8,
                  fill="none", stroke=NEG, sw=1.6, rx=8))
    for r in range(rows):
        for c in range(cols):
            x = kx + c * cellw
            y = ky + r * (cellh + 8)
            p.append(rect(x, y, cellw - 5, cellh, fill="#eef4ff", stroke=LINE, sw=1.0, rx=3))
    p.append(text(cx, 72, "швидкий кеш · місткість M", size=11, color=NEG, bold=True))
    # позначка «лінія = B» на середньому рядку
    liney = ky + (cellh + 8) + cellh / 2
    p.append(text(kx + cols * cellw + 20, liney + 4, "← лінія = B елементів",
                  size=10, color=MUTED, anchor="start"))

    # повільна пам'ять знизу
    my = 250
    p.append(rect(kx - 8, my, cols * cellw + 16, 66, fill="#fdf4f4", stroke=INK, sw=1.5, rx=6))
    p.append(text(cx, my + 30, "повільна пам'ять", size=12, color=INK, bold=True))
    p.append(text(cx, my + 48, "(без меж)", size=9.5, color=MUTED))

    # двобічне пересилання між рівнями
    midx = cx
    ay_top = ky + rows * (cellh + 8) + 4
    p.append(arrow(midx - 16, ay_top, midx - 16, my - 6, color=POS, sw=2.0))
    p.append(arrow(midx + 16, my - 6, midx + 16, ay_top, color=FIELD, sw=2.0))
    p.append(text(midx + 150, (ay_top + my) / 2 - 8, "промах:", size=10.5, color=POS, anchor="middle", bold=True))
    p.append(text(midx + 150, (ay_top + my) / 2 + 8, "приносять цілий B-блок", size=9.5, color=INK, anchor="middle"))

    # роздільник
    p.append(line(410, 54, 410, H - 30, color="#d8dde3", sw=1.2, dash="4 4"))

    # ── права панель: лінійний скан ──
    rcx = 615
    p.append(text(rcx, 58, "Лінійний прохід по N комірках", size=12.5, color=INK, bold=True))
    sx, sy = 452, 120
    sw_ = 26
    nblocks, bsz = 3, 4
    ncell = nblocks * bsz
    for i in range(ncell):
        x = sx + i * sw_
        b = i // bsz
        shade = "#eef4ff" if b % 2 == 0 else "#e3ecfb"
        p.append(rect(x, sy, sw_ - 2, 32, fill=shade, stroke=LINE, sw=0.9, rx=2))
        if i % bsz == 0:
            p.append(line(x, sy - 6, x, sy + 38, color=NEG, sw=1.7))
    p.append(line(sx + ncell * sw_, sy - 6, sx + ncell * sw_, sy + 38, color=NEG, sw=1.7))
    # хрестик-промах на початку блоку, крапки-влучання далі
    for i in range(ncell):
        x = sx + i * sw_ + (sw_ - 2) / 2
        if i % bsz == 0:
            p.append(text(x, sy - 12, "✗", size=13, color=POS, bold=True))
        else:
            p.append(text(x, sy - 12, "•", size=13, color=FIELD, bold=True))
    p.append(text(rcx, sy + 66, "1 промах ✗ на блок, решта — влучання •", size=10.5, color=INK))
    p.append(text(rcx, sy + 92, "усього ⌈N / B⌉ промахів", size=13, color=INK, bold=True))
    p.append(text(rcx, sy + 116, "— і жодного B у коді циклу", size=10.5, color=FIELD, italic=True))
    p.append(text(rcx, sy + 150, "✗ промах    • влучання", size=9.5, color=MUTED))

    render(os.path.join(OUT, "model.svg"), W, H, *p,
           title="Модель ідеального кеша: платимо лише за блоки, що їздять між рівнями")


# ── recursion: рекурсія влучає в кожен кеш одразу ─────────────────────────────
# Ідея: драбина підзадач, що дрібнішають навпіл; дві межі «вмістилося в кеш» на
# різній глибині — та сама рекурсія перетинає обидві, кеш-констант у коді нема.

def fig_recursion():
    W, H = 820, 470
    p = []
    cx = 290
    levels = [
        ("N",   350),
        ("N/2", 250),
        ("N/4", 176),
        ("N/8", 124),
        ("N/16", 86),
        ("N/32", 60),
    ]
    top, step, bh = 78, 60, 30
    ys = [top + i * step for i in range(len(levels))]

    # ліва вісь: рекурсія глибшає
    axx = cx - 210
    p.append(arrow(axx, ys[0] - 6, axx, ys[-1] + bh + 8, color=MUTED, sw=1.7))
    p.append(text(axx - 8, ys[0] + 60, "рекурсія", size=10, color=MUTED, anchor="end"))
    p.append(text(axx - 8, ys[0] + 74, "глибшає,", size=10, color=MUTED, anchor="end"))
    p.append(text(axx - 8, ys[0] + 88, "підзадача", size=10, color=MUTED, anchor="end"))
    p.append(text(axx - 8, ys[0] + 102, "дрібнішає", size=10, color=MUTED, anchor="end"))

    # смуги-підзадачі
    for i, (lab, w) in enumerate(levels):
        y = ys[i]
        p.append(rect(cx - w / 2, y, w, bh, fill="#eef4ff", stroke=NEG, sw=1.4, rx=5))
        p.append(text(cx + w / 2 + 14, y + bh / 2 + 4, lab, size=11, color=INK, anchor="start", bold=True))
        if i < len(levels) - 1:
            p.append(text(cx, y + bh + step / 2 - 4, "÷2", size=9.5, color=MUTED))

    # межа великого кеша (між N/4 і N/8)
    gy = (ys[2] + bh + ys[3]) / 2
    p.append(line(cx - 195, gy, cx + 150, gy, color=FIELD, sw=2.0, dash="6 4"))
    p.append(text(cx - 200, gy - 6, "великий кеш (L3):", size=10, color=FIELD, anchor="end", bold=True))
    p.append(text(cx - 200, gy + 8, "вміщає підзадачу ТУТ", size=10, color=FIELD, anchor="end"))
    p.append(text(cx + 154, gy + 4, "↓ далі безкоштовно", size=9.5, color=FIELD, anchor="start"))

    # межа малого кеша (між N/16 і N/32)
    by = (ys[4] + bh + ys[5]) / 2
    p.append(line(cx - 195, by, cx + 150, by, color=NEG, sw=2.0, dash="6 4"))
    p.append(text(cx - 200, by - 6, "малий кеш (L1):", size=10, color=NEG, anchor="end", bold=True))
    p.append(text(cx - 200, by + 8, "вміщає ТУТ", size=10, color=NEG, anchor="end"))
    p.append(text(cx + 154, by + 4, "↓ далі безкоштовно", size=9.5, color=NEG, anchor="start"))

    # виноска-присуд праворуч
    p.append(fitbox(560, 150, 236, 170,
                    "Та сама рекурсія проходить\nУСІ масштаби задачі.\n\n"
                    "Хоч би яким був кеш —\nзнайдеться рівень, де підзадача\nвже вмістилась, а нижче\nпромахів нема.\n\n"
                    "Влучає в L1, L2, L3 і RAM\nводночас. Кеш-констант\nу коді немає.",
                    size=11, fill="#f4f6f8", stroke=INK, color=INK))

    render(os.path.join(OUT, "recursion.svg"), W, H, *p,
           title="Одна рекурсія оптимальна для всіх кешів одразу")


# ── veb: розкладка ван Емде Боаса ─────────────────────────────────────────────
# Ідея: дерево ріжуть навпіл за висотою на трикутники; кожен трикутник кладуть
# у пам'ять суцільним блоком; шлях пошуку перетинає ланцюжок трикутників.

def fig_veb():
    W, H = 840, 430
    p = []

    # ── ліва панель: дерево з розрізом ──
    p.append(text(230, 56, "Дерево, розрізане навпіл за висотою", size=12, color=INK, bold=True))

    # координати вузлів
    root = (230, 82)
    L1 = [(150, 132), (310, 132)]
    L2 = [(110, 187), (190, 187), (270, 187), (350, 187)]
    L3 = [(90, 242), (130, 242), (170, 242), (210, 242),
          (250, 242), (290, 242), (330, 242), (370, 242)]

    TOPFILL, TOPSTK = "#eafaf0", FIELD
    BOT = ["#e3ecfb", "#dfeaf7", "#e8eefb", "#dbe6f6"]

    # ребра (спершу лінії, тоді вузли зверху)
    edges = [
        (root, L1[0]), (root, L1[1]),
        (L1[0], L2[0]), (L1[0], L2[1]), (L1[1], L2[2]), (L1[1], L2[3]),
        (L2[0], L3[0]), (L2[0], L3[1]), (L2[1], L3[2]), (L2[1], L3[3]),
        (L2[2], L3[4]), (L2[2], L3[5]), (L2[3], L3[6]), (L2[3], L3[7]),
    ]
    # виділений шлях корінь→листок: root → L1[0] → L2[0] → L3[0]
    path = {(root, L1[0]), (L1[0], L2[0]), (L2[0], L3[0])}
    for a, b in edges:
        if (a, b) in path:
            p.append(line(a[0], a[1], b[0], b[1], color=POS, sw=3.0))
        else:
            p.append(line(a[0], a[1], b[0], b[1], color=LINE, sw=1.2))

    # лінія розрізу (між L1 і L2)
    cuty = (132 + 187) / 2
    p.append(line(60, cuty, 400, cuty, color=MUTED, sw=1.6, dash="7 4"))
    p.append(text(175, cuty - 6, "розріз навпіл за висотою", size=9.5, color=MUTED, anchor="start"))

    # вузли: верхній трикутник
    r = 12
    for (x, y) in [root] + L1:
        p.append(circle(x, y, r, fill=TOPFILL, stroke=TOPSTK, sw=1.8))
    # нижні трикутники: (корінь L2[i], його двоє листків)
    bottoms = [
        (L2[0], [L3[0], L3[1]]),
        (L2[1], [L3[2], L3[3]]),
        (L2[2], [L3[4], L3[5]]),
        (L2[3], [L3[6], L3[7]]),
    ]
    for i, (top, leaves) in enumerate(bottoms):
        for (x, y) in [top] + leaves:
            p.append(circle(x, y, r, fill=BOT[i], stroke=NEG, sw=1.5))

    # позначка виділеного шляху
    p.append(text(230, 282, "шлях пошуку торкнувся 2 трикутників = 2 блоків",
                  size=10, color=POS, anchor="middle", bold=True))

    # роздільник
    p.append(line(418, 50, 418, 300, color="#d8dde3", sw=1.2, dash="4 4"))

    # ── права панель: пам'ять ──
    p.append(text(628, 56, "У пам'яті — трикутники суцільними блоками", size=12, color=INK, bold=True))
    bx, by = 448, 96
    bw, gap = 66, 8
    cellw = (bw - 12) / 3
    labels = ["верхній", "нижн.1", "нижн.2", "нижн.3", "нижн.4"]
    fills = [TOPFILL] + BOT
    strokes = [TOPSTK] + [NEG] * 4
    highlight = [True, True, False, False, False]  # блоки шляху
    for k in range(5):
        x = bx + k * (bw + gap)
        p.append(rect(x - 4, by - 6, bw + 8, 58,
                      fill="none", stroke=(POS if highlight[k] else "#c7ccd2"),
                      sw=(2.2 if highlight[k] else 1.0), rx=6))
        for c in range(3):
            p.append(rect(x + c * cellw, by, cellw - 3, 30, fill=fills[k], stroke=strokes[k], sw=1.1, rx=3))
        p.append(text(x + bw / 2 - 2, by + 48, labels[k], size=9, color=INK))

    p.append(text(628, by + 74, "кожен блок далі — за тим самим", size=10, color=MUTED))
    p.append(text(628, by + 90, "правилом (рекурсивно)", size=10, color=MUTED))
    p.append(text(628, by + 116, "червоним — 2 блоки, яких", size=10, color=POS))
    p.append(text(628, by + 132, "торкнувся цей пошук", size=10, color=POS))

    # виноска-присуд унизу на всю ширину
    p.append(fitbox(70, 330, 700, 74,
                    "Знайдеться рівень рекурсії, де трикутники завбільшки з блок B — кожен лягає в одну лінію.\n"
                    "Шлях корінь→листок перетинає ланцюжок таких трикутників, за кожен — один промах:\n"
                    "усього O(log_B N) промахів, як у B-дерева, але жодного B у побудові розкладки немає.",
                    size=11, fill="#f4f6f8", stroke=INK, color=INK))

    render(os.path.join(OUT, "veb.svg"), W, H, *p,
           title="Розкладка ван Емде Боаса: пошук у дереві, що не знає про кеш")


# ── hist-timeline: дві нитки, що зійшлися лише назвою ─────────────────────────
# Ідея: нитка «як навчилися міряти кеш» і нитка ван Емде Боаса йшли окремо;
# нитка MIT народила поняття 1994–1999, а нитку 1975 р. приплели 2000-го — назвою.

STR_A = (NEG,   "#eef3fd")   # як навчилися міряти кеш
STR_B = (FIELD, "#eafaf0")   # нитка ван Емде Боаса
STR_C = (POS,   "#fdf0ee")   # нитка MIT


def fig_hist_timeline():
    W, H = 940, 852
    p = []
    p.append(text(W / 2, 32, "Дві нитки, що зійшлися лише назвою", size=14, color=INK, bold=True))

    # легенда
    leg = [(STR_A, "як навчилися МІРЯТИ кеш"),
           (STR_B, "нитка ван Емде Боаса"),
           (STR_C, "нитка MIT")]
    lx = 112
    for (col, fil), lab in leg:
        p.append(rect(lx, 50, 16, 12, fill=fil, stroke=col, sw=1.4, rx=2))
        p.append(text(lx + 24, 60, lab, size=9.5, color=col, anchor="start", bold=True))
        lx += 24 + len(lab) * 9.5 * 0.57 + 34

    # вертикальна вісь часу
    p.append(line(100, 92, 100, 812, color="#c7ccd2", sw=1.6))

    ev = [
        ("1969", STR_A, "Синглтон: поділ навпіл поліпшує локальність",
         "давно відома річ — але ще не теорія, а спостереження"),
        ("1975", STR_B, "ван Емде Боас: стратифіковані дерева",
         "O(log log n) на всесвіті 1…n; про кеші — ані слова"),
        ("1976", STR_B, "Каас і Зейлстра: реалізація і спільна стаття",
         "структуру доводить до пуття команда, не одна людина"),
        ("1981", STR_A, "Гонг і Кунг: червоно-синя камінцева гра",
         "нижні оцінки на обмін із повільною пам'яттю"),
        ("1988", STR_A, "Аґарвал і Віттер: модель із B і M",
         "точна міра з'явилась — але алгоритми в ній ЗНАЮТЬ B і M"),
        ("1994", STR_C, "Група MIT помічає: рекурсивне множення матриць",
         "кеш-оптимальне БЕЗ жодного підбору. Назви ще немає"),
        ("1996", STR_C, "Блумофе та ін., SPAA (Падуя): алгоритм у друку",
         "надрукований — але кеш-незалежності там не досліджують"),
        ("1997", STR_C, "Група ухвалює термін «cache-oblivious»",
         "спостереження нарешті стає програмою досліджень"),
        ("1999", STR_C, "Прокоп: магістерська MIT (21.05) → FOCS (Нью-Йорк, 17–19.10)",
         "модель ideal-cache; розкладка — 2 сторінки в «майбутній роботі»"),
        ("2000", STR_C, "Бендер, Демейн, Фарах-Колтон, FOCS: динамічні дерева",
         "і саме вони НАЗИВАЮТЬ розкладку іменем ван Емде Боаса"),
        ("2012", STR_C, "TALG 8(1):4 — журнальна версія, через 13 років",
         "заразом виправлено формулу Штрассена з версії 1999 р."),
    ]

    bx, bw, bh, stepy = 112, 580, 54, 66
    ys = {}
    for i, (year, (col, fil), t1, t2) in enumerate(ev):
        y = 100 + i * stepy
        ys[year] = y
        p.append(text(88, y + 30, year, size=12, color=INK, anchor="end", bold=True))
        p.append(circle(100, y + 26, 5.5, fill=col, stroke=col, sw=1.2))
        p.append(rect(bx, y, bw, bh, fill=fil, stroke=col, sw=1.4, rx=5))
        p.append(text(bx + 12, y + 22, t1, size=11, color=INK, anchor="start", bold=True))
        p.append(text(bx + 12, y + 41, t2, size=9.5, color=MUTED, anchor="start"))

    # стрілка 1975 → 2000: нитку приплели ЛИШЕ назвою
    y75 = ys["1975"] + 27
    y00 = ys["2000"] + 27
    ex = 752
    p.append(line(bx + bw, y75, ex, y75, color=FIELD, sw=1.8, dash="6 4"))
    p.append(line(ex, y75, ex, y00, color=FIELD, sw=1.8, dash="6 4"))
    p.append(arrow(ex, y00, bx + bw + 4, y00, color=FIELD, sw=1.8))
    lab = ["лише НАЗВА —", "за СХОЖІСТЮ", "форми, через", "25 років, і", "не від автора"]
    for k, s in enumerate(lab):
        p.append(text(766, (y75 + y00) / 2 - 34 + k * 17, s, size=9.5, color=FIELD, anchor="start", bold=(k == 0)))

    render(os.path.join(OUT, "hist-timeline.svg"), W, H, *p,
           title="Дві нитки: як міряли кеш, хто такий ван Емде Боас і що зробили в MIT")


# ── hist-credit: хто що саме зробив ───────────────────────────────────────────
# Ідея: розчепити «винайшов» на окремі дії — форма, спостереження, назва поняття,
# модель і доведення, назва розкладки; і показати, яке твердження джерела НЕ несуть.

def fig_hist_credit():
    W, H = 920, 636
    p = []
    p.append(text(W / 2, 32, "Хто що саме зробив: «винайшов» розчеплено на дії", size=14, color=INK, bold=True))

    acts = [
        ("ФОРМА", "Петер ван Емде Боас · 1975", FIELD, "#eafaf0",
         "рекурсивний поділ на √-шматки — заради ЧАСУ O(log log n), не заради кеша"),
        ("СПОСТЕРЕЖЕННЯ", "група MIT · 1994", NEG, "#eef3fd",
         "рекурсія кеш-оптимальна без підбору; розмову започаткував Боббі Блумофе"),
        ("НАЗВА ПОНЯТТЯ", "група MIT · 1997", NEG, "#eef3fd",
         "«cache-oblivious»; хто саме вимовив її першим — джерела не кажуть"),
        ("МОДЕЛЬ · ДОВЕДЕННЯ · РОЗКЛАДКА", "Гаральд Прокоп · 1999", POS, "#fdf0ee",
         "ideal-cache, оптимальність, сама розкладка; керівник праці — Чарлз Лейзерсон"),
        ("НАЗВА РОЗКЛАДКИ", "Бендер, Демейн, Фарах-Колтон · 2000", POS, "#fdf0ee",
         "«van Emde Boas layout» — за схожістю форми, з обмовкою просто в зносці"),
    ]
    x, w, h, step = 70, 780, 68, 80
    for i, (act, who, col, fil, det) in enumerate(acts):
        y = 60 + i * step
        p.append(rect(x, y, w, h, fill=fil, stroke=col, sw=1.5, rx=6))
        p.append(circle(x + 28, y + 34, 15, fill="#ffffff", stroke=col, sw=1.6))
        p.append(text(x + 28, y + 39, str(i + 1), size=13, color=col, bold=True))
        p.append(text(x + 58, y + 24, act, size=11, color=INK, anchor="start", bold=True))
        p.append(text(x + 58, y + 43, who, size=10.5, color=col, anchor="start", bold=True))
        p.append(text(x + 58, y + 60, det, size=9.5, color=MUTED, anchor="start"))
        if i < len(acts) - 1:
            p.append(line(x + 28, y + h, x + 28, y + step, color="#c7ccd2", sw=1.4))

    # те, чого першоджерела не підтверджують
    dy = 474
    p.append(rect(x, dy, w, 128, fill="#fff8f0", stroke=POS, sw=2.0, rx=6))
    p.append(text(x + 16, dy + 26, "А що кажуть довідники:", size=11, color=POS, anchor="start", bold=True))
    p.append(text(x + 16, dy + 48,
                  "«Ідею (і назву) замислив Чарлз Лейзерсон ще 1996 р.» — з посиланням на працю Прокопа.",
                  size=10.5, color=INK, anchor="start", italic=True))
    p.append(text(x + 16, dy + 72, "Але в самій праці цього немає. Вона каже: 1994 — помітили, 1997 — ухвалили термін,",
                  size=10, color=INK, anchor="start"))
    p.append(text(x + 16, dy + 90, "і скрізь «наша група», а не одна людина. Журнальна версія 2012 р., підписана й самим",
                  size=10, color=INK, anchor="start"))
    p.append(text(x + 16, dy + 108, "Лейзерсоном, повторює ті самі 1994 і 1997. Статус: НЕ ПІДТВЕРДЖЕНО ПЕРШОДЖЕРЕЛОМ.",
                  size=10, color=INK, anchor="start"))

    render(os.path.join(OUT, "hist-credit.svg"), W, H, *p,
           title="Хто що зробив у народженні кеш-незалежності — і яке твердження не підтверджене")


# ── hist-resemblance: де схожість є і де вона ламається ───────────────────────
# Ідея: дерево ван Емде Боаса ділить ВСЕСВІТ ключів заради ЧАСУ; розкладка ділить
# ВИСОТУ заради ПРОМАХІВ. Спільна лише форма поділу — на цьому схожість і кінчається.

def fig_hist_resemblance():
    W, H = 940, 580
    p = []
    p.append(text(W / 2, 32, "Схожість, за яку дали ім'я, — і де вона ламається", size=14, color=INK, bold=True))
    p.append(line(470, 52, 470, 306, color="#d8dde3", sw=1.2, dash="4 4"))

    # ── ліворуч: стратифіковане дерево (1975) ──
    p.append(text(250, 66, "Стратифіковане дерево ван Емде Боаса, 1975", size=11.5, color=FIELD, bold=True))
    p.append(text(250, 92, "ділить ВСЕСВІТ ключів 1…n", size=10, color=INK))
    ux, uy, uw = 62, 106, 376
    p.append(rect(ux, uy, uw, 30, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=4))
    for k in range(1, 4):
        p.append(line(ux + k * uw / 4, uy, ux + k * uw / 4, uy + 30, color=FIELD, sw=1.5))
    for k in range(4):
        p.append(text(ux + (k + 0.5) * uw / 4, uy + 20, "√n", size=10, color=FIELD, bold=True))
    p.append(text(250, uy + 48, "√n блоків по √n ключів — і так рекурсивно вглиб", size=9.5, color=MUTED))
    p.append(arrow(250, uy + 58, 250, uy + 80, color=MUTED, sw=1.5))
    p.append(rect(120, uy + 84, 260, 34, fill="#f4f6f8", stroke=MUTED, sw=1.3, rx=4))
    p.append(text(250, uy + 105, "+ службова структура: де є ключі", size=9.5, color=INK))
    p.append(text(250, uy + 140, "міра: ЧАС, O(log log n)", size=11.5, color=FIELD, bold=True))
    p.append(text(250, uy + 160, "про кеші й блоки — ані слова", size=9.5, color=MUTED, italic=True))

    # ── праворуч: розкладка (1999) ──
    p.append(text(700, 66, "Розкладка: Прокоп 1999, названа 2000", size=11.5, color=POS, bold=True))
    p.append(text(700, 92, "ділить ВИСОТУ дерева h навпіл", size=10, color=INK))
    root = (700, 118)
    lv1 = [(650, 156), (750, 156)]
    lv2 = [(618, 196), (682, 196), (718, 196), (782, 196)]
    for a in lv1:
        p.append(line(root[0], root[1], a[0], a[1], color=LINE, sw=1.2))
    p.append(line(lv1[0][0], lv1[0][1], lv2[0][0], lv2[0][1], color=LINE, sw=1.2))
    p.append(line(lv1[0][0], lv1[0][1], lv2[1][0], lv2[1][1], color=LINE, sw=1.2))
    p.append(line(lv1[1][0], lv1[1][1], lv2[2][0], lv2[2][1], color=LINE, sw=1.2))
    p.append(line(lv1[1][0], lv1[1][1], lv2[3][0], lv2[3][1], color=LINE, sw=1.2))
    cuty = 176
    p.append(line(578, cuty, 822, cuty, color=MUTED, sw=1.5, dash="6 4"))
    p.append(text(826, cuty + 4, "розріз h/2", size=9, color=MUTED, anchor="start"))
    p.append(circle(root[0], root[1], 11, fill="#fdf0ee", stroke=POS, sw=1.6))
    for a in lv1:
        p.append(circle(a[0], a[1], 11, fill="#fdf0ee", stroke=POS, sw=1.6))
    for a in lv2:
        p.append(circle(a[0], a[1], 10, fill="#f8e6e2", stroke=POS, sw=1.4))
    p.append(text(700, 232, "шматки лягають у пам'ять суцільно, і так вглиб", size=9.5, color=MUTED))
    p.append(text(700, uy + 140, "міра: ПРОМАХИ, O(log_B N)", size=11.5, color=POS, bold=True))
    p.append(text(700, uy + 160, "саме дерево — звичайне, інший лише ПОРЯДОК", size=9.5, color=MUTED, italic=True))

    # ── спільне ──
    p.append(rect(50, 322, 840, 62, fill="#eafaf0", stroke=FIELD, sw=1.6, rx=6))
    p.append(text(66, 344, "СПІЛЬНЕ — сама форма:", size=11, color=FIELD, anchor="start", bold=True))
    p.append(text(66, 366, "рекурсивний поділ навпіл дає шматки завбільшки ≈ √цілого, тож рекурсія проходить УСІ масштаби одразу.",
                  size=10, color=INK, anchor="start"))

    # ── де ламається ──
    p.append(rect(50, 398, 840, 128, fill="#fdf0ee", stroke=POS, sw=1.8, rx=6))
    p.append(text(66, 422, "ЛАМАЄТЬСЯ — на всьому іншому:", size=11, color=POS, anchor="start", bold=True))
    for k, s in enumerate([
        "різні об'єкти поділу: всесвіт ключів  ↔  висота дерева;",
        "різна міра вартості: час виконання  ↔  пересилання блоків;",
        "дерево ван Емде Боаса — структура зі службовими вказівниками, розкладка ж — лише порядок вузлів у пам'яті.",
    ]):
        p.append(text(66, 446 + k * 20, "· " + s, size=10, color=INK, anchor="start"))
    p.append(text(66, 512, "Бендер, Демейн і Фарах-Колтон написали це просто у зносці — її майже ніколи не цитують.",
                  size=9.5, color=POS, anchor="start", italic=True))

    render(os.path.join(OUT, "hist-resemblance.svg"), W, H, *p,
           title="Схожість між деревом ван Емде Боаса й розкладкою — і межі цієї схожості")


# ── math-volume: чому в оцінці стоїть саме √M ─────────────────────────────────
# Ідея (поверхня проти об'єму): брусок √M×√M×√M робить M·√M роботи, торкнувшись
# лише 3M елементів — звідси B·√M роботи на один принесений блок.

def fig_math_volume():
    W, H = 880, 450
    p = []

    # ── куб роботи N×N×N (коса проєкція) ──
    fx0, fy0, S = 120, 150, 160
    fx1, fy1 = fx0 + S, fy0 + S
    dx, dy = 64, -50
    bx0, by0 = fx0 + dx, fy0 + dy
    bx1, by1 = fx1 + dx, fy1 + dy

    # приховані ребра (задній нижній лівий кут) — пунктиром
    p.append(line(bx0, by0, bx0, by1, color=MUTED, sw=1.0, dash="4 3"))
    p.append(line(bx0, by1, bx1, by1, color=MUTED, sw=1.0, dash="4 3"))
    p.append(line(fx0, fy1, bx0, by1, color=MUTED, sw=1.0, dash="4 3"))
    # видимі ребра заднього боку
    p.append(line(bx0, by0, bx1, by0, color=INK, sw=1.4))
    p.append(line(bx1, by0, bx1, by1, color=INK, sw=1.4))
    # з'єднувачі
    p.append(line(fx0, fy0, bx0, by0, color=INK, sw=1.4))
    p.append(line(fx1, fy0, bx1, by0, color=INK, sw=1.4))
    p.append(line(fx1, fy1, bx1, by1, color=INK, sw=1.4))
    # передня грань
    p.append(rect(fx0, fy0, S, S, fill="none", stroke=INK, sw=1.6, rx=0))

    # брусок √M×√M×√M у передньому нижньому куті
    s, sdx, sdy = 46, 18, -14
    kx0, ky0 = fx0, fy1 - s
    kx1, ky1 = kx0 + s, fy1
    p.append(line(kx0 + sdx, ky0 + sdy, kx1 + sdx, ky0 + sdy, color=POS, sw=1.2))
    p.append(line(kx1 + sdx, ky0 + sdy, kx1 + sdx, ky1 + sdy, color=POS, sw=1.2))
    p.append(line(kx0, ky0, kx0 + sdx, ky0 + sdy, color=POS, sw=1.2))
    p.append(line(kx1, ky0, kx1 + sdx, ky0 + sdy, color=POS, sw=1.2))
    p.append(line(kx1, ky1, kx1 + sdx, ky1 + sdy, color=POS, sw=1.2))
    p.append(rect(kx0, ky0, s, s, fill="#fdecea", stroke=POS, sw=2.0, rx=0))

    # підписи осей — поза кубом, із запасом
    p.append(text((fx0 + fx1) / 2, fy1 + 26, "N", size=13, color=INK, bold=True))
    p.append(text(fx0 - 16, (fy0 + fy1) / 2 + 5, "N", size=13, color=INK, bold=True, anchor="end"))
    p.append(text(bx1 + 16, (fy1 + by1) / 2 + 4, "N", size=13, color=INK, bold=True, anchor="start"))
    p.append(text(232, 374, "куб з N³ множень-додавань", size=11.5, color=MUTED))

    # ── права панель: арифметика ──
    p.append(text(662, 116, "Скільки роботи дає один принесений блок", size=12.5, color=INK, bold=True))
    p.append(fitbox(470, 132, 384, 210,
                    "Червоний брусок — √M × √M × √M:\n"
                    "рівно стільки, скільки влазить у кеш M.\n"
                    "\n"
                    "робота в бруску:   (√M)³ = M·√M\n"
                    "його дані:         3 грані по M = 3M\n"
                    "принести їх:       3M / B блоків\n"
                    "\n"
                    "на 1 блок роботи:  M·√M ÷ (3M/B) = B·√M / 3\n"
                    "\n"
                    "усього роботи N³ →\n"
                    "блоків ≈ N³ ÷ (B·√M / 3) = Θ(N³ / (B·√M))",
                    size=11.5, fill="#f4f6f8", stroke=INK, color=INK))

    render(os.path.join(OUT, "math-volume.svg"), W, H, *p,
           title="Чому в оцінці стоїть саме √M: поверхня проти об'єму")


# ── math-cut: дерево рекурсії, різ і підрахунок ───────────────────────────────
# Ідея: аналіз ріже дерево на рівні, де підзадача вперше влізла в кеш, і рахує
# вузли різу × ціну вузла; нижче різу промахів нема. Код про різ не знає.

def fig_math_cut():
    W, H = 880, 520
    p = []

    # рівень 0
    p.append(rect(287, 68, 86, 30, fill="#eef4ff", stroke=NEG, sw=1.6))
    p.append(text(330, 88, "N", size=13, color=INK, bold=True))
    p.append(text(565, 88, "8⁰ = 1 вузол, розмір N", size=11, color=MUTED, anchor="start"))

    # рівень 1 (8 підзадач; показано 4 + «…»)
    for x in [180, 260, 400, 480]:
        p.append(line(330, 98, x, 140, color=LINE, sw=0.9))
        p.append(rect(x - 24, 140, 48, 30, fill="#eef4ff", stroke=NEG, sw=1.4))
        p.append(text(x, 160, "N/2", size=10.5, color=INK))
    p.append(text(330, 160, "…", size=15, color=MUTED))
    p.append(text(565, 152, "8¹ = 8 вузлів, розмір N/2", size=11, color=MUTED, anchor="start"))
    p.append(text(565, 170, "(поділ ÷2 по кожній з 3 осей)", size=9.5, color=MUTED, anchor="start"))

    # рівень 2
    for x in [140, 180, 220, 260, 400, 440, 480, 520]:
        p.append(rect(x - 13, 212, 26, 22, fill="#e3ecfb", stroke=NEG, sw=1.1, rx=3))
    p.append(text(330, 228, "…", size=15, color=MUTED))
    p.append(text(565, 230, "8² = 64 вузли, розмір N/4", size=11, color=MUTED, anchor="start"))

    # лінія різу
    p.append(text(100, 256, "РІЗ — рівень i, де підзадача вперше влізла в кеш:  3·(N/2ⁱ)² ≤ M",
                  size=11, color=FIELD, anchor="start", bold=True))
    p.append(line(100, 270, 700, 270, color=FIELD, sw=2.0, dash="6 4"))

    # рівень різу
    for k in range(12):
        p.append(rect(140 + k * 36 - 9, 296, 18, 20, fill="#fdecea", stroke=POS, sw=1.3, rx=2))
    p.append(text(565, 310, "8ⁱ вузлів, кожен ≈ √M × √M", size=11, color=POS, anchor="start", bold=True))
    p.append(text(330, 338, "кожен вузол на різі вже влазить у кеш", size=10.5, color=POS))

    # нижче різу
    p.append(fitbox(100, 354, 620, 36,
                    "нижче різу — дані вже в кеші: нових промахів немає",
                    size=11, fill="#f0f7f2", stroke=FIELD, color=FIELD))

    # підрахунок
    p.append(fitbox(60, 406, 760, 96,
                    "рівень різу i:    3·(N/2ⁱ)² ≈ M   →   2ⁱ ≈ N·√3 / √M\n"
                    "вузлів на різі:   8ⁱ = (2ⁱ)³ ≈ 3√3 · N³ / (M·√M)\n"
                    "ціна вузла:       принести його 3M елементів = Θ(M / B) блоків\n"
                    "разом:            Θ(N³ / (M·√M)) · Θ(M / B) = Θ(N³ / (B·√M))",
                    size=11.5, fill="#f4f6f8", stroke=INK, color=INK))

    render(os.path.join(OUT, "math-cut.svg"), W, H, *p,
           title="Дерево рекурсії множення матриць: де різати й що рахувати")


# ── math-merge: чому основа логарифма саме M/B ────────────────────────────────
# Ідея: за прохід зливаємо стільки доріжок, скільки блокових буферів влазить у
# кеш, тобто M/B; звідси основа логарифма й число проходів.

def fig_math_merge():
    W, H = 880, 440
    p = []

    # ── ліва панель: буфери в кеші ──
    p.append(text(290, 58, "Скільки доріжок зливаємо за один прохід", size=12, color=INK, bold=True))
    p.append(rect(140, 82, 300, 244, fill="none", stroke=NEG, sw=1.8, rx=8))
    p.append(text(290, 104, "кеш M", size=12, color=NEG, bold=True))

    p.append(text(98, 96, "вхідні", size=10, color=POS))
    p.append(text(98, 110, "доріжки", size=10, color=POS))
    for y in [122, 156, 190, 224]:
        p.append(rect(170, y, 180, 24, fill="#eef4ff", stroke=LINE, sw=1.0, rx=3))
        p.append(text(260, y + 17, "буфер = 1 блок (B елементів)", size=9.5, color=INK))
        p.append(arrow(102, y + 12, 166, y + 12, color=POS, sw=1.6))
    p.append(text(260, 268, "⋮", size=15, color=MUTED))
    p.append(text(290, 300, "усього M/B буферів — по одному на доріжку",
                  size=10.5, color=NEG, bold=True))

    p.append(arrow(290, 330, 290, 360, color=FIELD, sw=2.0))
    p.append(text(290, 384, "злита доріжка — довша в M/B разів", size=10.5, color=FIELD))

    # ── права панель: скільки проходів ──
    p.append(text(668, 58, "Скільки таких проходів", size=12, color=INK, bold=True))
    p.append(fitbox(480, 82, 380, 244,
                    "За прохід кількість доріжок ділиться\n"
                    "на M/B — стільки буферів по B\n"
                    "влазить у кеш M.\n"
                    "\n"
                    "на старті:  N/B доріжок (по 1 блоку)\n"
                    "після k проходів:  (N/B) / (M/B)^k\n"
                    "лишилась одна  →  k = log_{M/B}(N/B)\n"
                    "\n"
                    "один прохід читає й пише все:  Θ(N/B)\n"
                    "\n"
                    "разом:  Θ( (N/B) · log_{M/B}(N/B) )",
                    size=11.5, fill="#f4f6f8", stroke=INK, color=INK))

    render(os.path.join(OUT, "math-merge.svg"), W, H, *p,
           title="Чому основа логарифма — саме M/B")


# ── proj-rowcol: чому наївний цикл мучить саме B ──────────────────────────────
# Ідея: у row-major рядок A лежить підряд (1 промах на B доступів), а стовпець B
# розкиданий по рядках — кожен елемент у своїй лінії, тож промах на кожен доступ.

def fig_proj_rowcol():
    W, H = 880, 500
    p = []
    cell = 21
    n = 8

    # ── ліва панель: A — уздовж рядка ──
    ax, ay = 96, 96
    p.append(text(ax + n * cell / 2, 62, "A[i][k] — біжимо ВЗДОВЖ рядка", size=12.5,
                  color=FIELD, bold=True))
    for r in range(n):
        for c in range(n):
            hot = (r == 3)
            p.append(rect(ax + c * cell, ay + r * cell, cell - 2, cell - 2,
                          fill=("#d6f3e2" if hot else "#f0f3f7"),
                          stroke=(FIELD if hot else "#c7ccd2"),
                          sw=(1.4 if hot else 0.7), rx=2))
        p.append(rect(ax - 4, ay + r * cell - 4, n * cell + 6, cell + 4,
                      fill="none", stroke="#aeb6bf", sw=0.8, rx=3))
    p.append(text(ax + n * cell + 16, ay + 3 * cell + cell / 2 + 4, "← увесь рядок i",
                  size=10, color=FIELD, anchor="start"))
    p.append(text(ax + n * cell / 2, ay + n * cell + 22, "рамка = одна лінія кеша",
                  size=9.5, color=MUTED))

    # ── права панель: B — униз по стовпцю ──
    bx, by = 480, 96
    p.append(text(bx + n * cell / 2, 62, "B[k][j] — біжимо ВНИЗ по стовпцю", size=12.5,
                  color=POS, bold=True))
    for r in range(n):
        for c in range(n):
            hot = (c == 3)
            p.append(rect(bx + c * cell, by + r * cell, cell - 2, cell - 2,
                          fill=("#fadbd6" if hot else "#f0f3f7"),
                          stroke=(POS if hot else "#c7ccd2"),
                          sw=(1.4 if hot else 0.7), rx=2))
        p.append(rect(bx - 4, by + r * cell - 4, n * cell + 6, cell + 4,
                      fill="none", stroke="#aeb6bf", sw=0.8, rx=3))
    p.append(text(bx + n * cell / 2, by + n * cell + 22, "стовпець j протикає ВСІ лінії",
                  size=9.5, color=POS))

    # ── смуги пам'яті під панелями ──
    sy = 310
    p.append(text(ax + n * cell / 2, sy - 12, "у пам'яті: підряд", size=10, color=INK, bold=True))
    sw_ = 19
    for i in range(16):
        x = ax + i * sw_ - 26
        p.append(rect(x, sy, sw_ - 2, 22, fill="#d6f3e2", stroke=FIELD, sw=0.9, rx=2))
        p.append(text(x + (sw_ - 2) / 2, sy - 2 + 38, "✗" if i % 8 == 0 else "•",
                      size=11, color=(POS if i % 8 == 0 else FIELD), bold=True))
        if i % 8 == 0:
            p.append(line(x - 2, sy - 5, x - 2, sy + 27, color=INK, sw=1.5))
    p.append(line(ax + 16 * sw_ - 28, sy - 5, ax + 16 * sw_ - 28, sy + 27, color=INK, sw=1.5))
    p.append(text(ax + n * cell / 2, sy + 60, "1 промах на 8 доступів → N/B на прохід",
                  size=10.5, color=FIELD, bold=True))

    p.append(text(bx + n * cell / 2, sy - 12, "у пам'яті: через кожні N·8 байтів",
                  size=10, color=INK, bold=True))
    gx0 = bx - 26
    for g in range(3):
        gx = gx0 + g * 66
        for i in range(3):
            x = gx + i * sw_
            hot = (i == 0)
            p.append(rect(x, sy, sw_ - 2, 22,
                          fill=("#fadbd6" if hot else "#f0f3f7"),
                          stroke=(POS if hot else "#c7ccd2"), sw=0.9, rx=2))
        p.append(line(gx - 2, sy - 5, gx - 2, sy + 27, color=INK, sw=1.5))
        p.append(text(gx + (sw_ - 2) / 2, sy + 36, "✗", size=11, color=POS, bold=True))
        if g < 2:
            p.append(text(gx + 3 * sw_ + 10, sy + 15, "…", size=13, color=MUTED))
    p.append(text(bx + n * cell / 2, sy + 60, "промах на КОЖЕН доступ → N на прохід",
                  size=10.5, color=POS, bold=True))

    p.append(line(430, 54, 430, 380, color="#d8dde3", sw=1.2, dash="4 4"))

    p.append(fitbox(70, 396, 740, 78,
                    "Внутрішній цикл по k тягне рядок A (дешево) і стовпець B (дорого): щоб стовпець окупився,\n"
                    "його N ліній мають дожити до наступного j. Доживають, лише якщо в кеші є місце на N + N/B + 1 ліній.\n"
                    "Не доживають — і кожен доступ до B стає промахом: N³ промахів замість N³/B. Обрив залежить від M і B.",
                    size=11, fill="#f4f6f8", stroke=INK, color=INK))

    render(os.path.join(OUT, "proj-rowcol.svg"), W, H, *p,
           title="Наївний цикл: рядок A дешевий, стовпець B руйнівний")


# ── proj-quadrants: блокова тотожність і 8 підзадач ───────────────────────────
# Ідея: кожну з трьох матриць ріжемо на 4 квадранти; добуток розпадається на 8
# множень половинного розміру, по два на кожен квадрант C. Арифметики — стільки ж.

def fig_proj_quadrants():
    W, H = 880, 540
    p = []
    QF = ["#dbe7fb", "#d6f3e2", "#fdeee1", "#f2e3fa"]
    QS = [NEG, FIELD, "#c87f2c", "#7d4bab"]

    def quad(gx, gy, s, names, fills, strokes):
        out = []
        for r in range(2):
            for c in range(2):
                k = r * 2 + c
                out.append(rect(gx + c * s, gy + r * s, s, s,
                                fill=fills[k], stroke=strokes[k], sw=1.6, rx=3))
                out.append(text(gx + c * s + s / 2, gy + r * s + s / 2 + 5,
                                names[k], size=12, color=INK, bold=True))
        return out

    s = 58
    cy = 92
    # C = A · B
    p.extend(quad(96, cy, s, ["C11", "C12", "C21", "C22"], QF, QS))
    p.append(text(96 + s, cy - 14, "C", size=13, color=INK, bold=True))
    p.append(text(96 + 2 * s + 30, cy + s + 5, "=", size=22, color=INK))

    p.extend(quad(96 + 2 * s + 62, cy, s, ["A11", "A12", "A21", "A22"],
                  ["#eef2f7"] * 4, [MUTED] * 4))
    p.append(text(96 + 2 * s + 62 + s, cy - 14, "A", size=13, color=INK, bold=True))
    p.append(text(96 + 4 * s + 92, cy + s + 5, "·", size=26, color=INK))

    p.extend(quad(96 + 4 * s + 124, cy, s, ["B11", "B12", "B21", "B22"],
                  ["#eef2f7"] * 4, [MUTED] * 4))
    p.append(text(96 + 4 * s + 124 + s, cy - 14, "B", size=13, color=INK, bold=True))

    p.append(text(W / 2, cy + 2 * s + 34,
                  "кожну матрицю ріжемо навпіл по обох осях — і добуток розпадається сам",
                  size=11, color=MUTED, italic=True))

    # 8 викликів, згрупованих за цільовим квадрантом
    rows = [
        ("C11", "A11·B11", "A12·B21", 0),
        ("C12", "A11·B12", "A12·B22", 1),
        ("C21", "A21·B11", "A22·B21", 2),
        ("C22", "A21·B12", "A22·B22", 3),
    ]
    ry = cy + 2 * s + 62
    rh = 40
    for i, (tgt, p1, p2, k) in enumerate(rows):
        y = ry + i * rh
        p.append(rect(150, y, 62, rh - 9, fill=QF[k], stroke=QS[k], sw=1.5, rx=4))
        p.append(text(181, y + (rh - 9) / 2 + 5, tgt, size=12, color=INK, bold=True))
        p.append(text(228, y + (rh - 9) / 2 + 5, "+=", size=12, color=INK, anchor="start", bold=True))
        p.append(rect(266, y, 118, rh - 9, fill="#f7f9fb", stroke=MUTED, sw=1.0, rx=4))
        p.append(text(325, y + (rh - 9) / 2 + 5, p1, size=11.5, color=INK))
        p.append(text(398, y + (rh - 9) / 2 + 5, "+", size=12, color=INK))
        p.append(rect(416, y, 118, rh - 9, fill="#f7f9fb", stroke=MUTED, sw=1.0, rx=4))
        p.append(text(475, y + (rh - 9) / 2 + 5, p2, size=11.5, color=INK))
        p.append(text(556, y + (rh - 9) / 2 + 5, "два виклики розміру n/2",
                      size=9.5, color=MUTED, anchor="start"))

    p.append(text(690, ry - 16, "8 підзадач", size=12, color=POS, bold=True))
    p.append(line(548, ry - 6, 548, ry + 4 * rh - 12, color=POS, sw=1.6))

    p.append(fitbox(70, ry + 4 * rh + 4, 740, 74,
                    "T(n) = 8·T(n/2) + Θ(n²)  →  Θ(n³): множень рівно стільки ж, скільки в наївного циклу.\n"
                    "Рекурсія не економить арифметику — вона переставляє ЗВЕРТАННЯ так, щоб підзадача,\n"
                    "яка вже влізла в кеш, доробилася без жодного нового промаху. Розмірів кеша в коді немає.",
                    size=11, fill="#f4f6f8", stroke=INK, color=INK))

    render(os.path.join(OUT, "proj-quadrants.svg"), W, H, *p,
           title="Блокова тотожність: один добуток = вісім половинних")


# ── proj-misses: виміряні промахи — обрив проти 1/√M ──────────────────────────
# Ідея: наївний тримається, поки стовпець B влазить у кеш, і обривається;
# рекурсивний спадає рівно як 1/√M — учетверо більший кеш дає рівно вдвічі менше.

def fig_proj_misses():
    W, H = 880, 520
    p = []
    caches = [2048, 4096, 8192, 16384, 32768, 65536]
    labels = ["2 КБ", "4 КБ", "8 КБ", "16 КБ", "32 КБ", "64 КБ"]
    naive = [2377728, 2377728, 2377728, 266240, 266240, 266240]
    recur = [81920, 65536, 40960, 32768, 20480, 16384]

    import math
    x0, x1 = 132, 690
    y0, y1 = 86, 356
    lo, hi = 4.0, 6.5           # десяткові логарифми меж

    def X(i):
        return x0 + i * (x1 - x0) / (len(caches) - 1)

    def Y(v):
        return y0 + (hi - math.log10(v)) / (hi - lo) * (y1 - y0)

    # сітка
    for d in (4, 5, 6):
        yy = Y(10 ** d)
        p.append(line(x0 - 14, yy, x1 + 12, yy, color="#dfe3e8", sw=1.0))
        p.append(text(x0 - 22, yy + 4, "10%s" % ("⁴" if d == 4 else "⁵" if d == 5 else "⁶"),
                      size=10, color=MUTED, anchor="end"))
    p.append(line(x0 - 14, y1 + 6, x1 + 12, y1 + 6, color=INK, sw=1.4))
    p.append(line(x0 - 14, y0 - 10, x0 - 14, y1 + 6, color=INK, sw=1.4))
    p.append(text(x0 - 52, y0 + 40, "промахів", size=10.5, color=INK, anchor="middle", bold=True))
    p.append(text((x0 + x1) / 2, y1 + 44, "місткість кеша M (лінія B = 64 Б)",
                  size=11, color=INK, bold=True))

    for i, lb in enumerate(labels):
        p.append(text(X(i), y1 + 24, lb, size=10, color=INK))

    # наївний
    for i in range(len(caches) - 1):
        p.append(line(X(i), Y(naive[i]), X(i + 1), Y(naive[i + 1]), color=POS, sw=2.6))
    for i, v in enumerate(naive):
        p.append(circle(X(i), Y(v), 4.6, fill=POS, stroke=POS, sw=1.0))
    p.append(text(X(0) + 6, Y(naive[0]) - 14, "наївний потрійний цикл",
                  size=11.5, color=POS, anchor="start", bold=True))
    p.append(text(X(0) + 6, Y(naive[0]) + 22, "2 377 728 = N³ + N³/B + N² + N²/B",
                  size=9.5, color=POS, anchor="start"))
    p.append(text(X(4) + 4, Y(naive[4]) - 14, "266 240 ≈ N³/B", size=9.5, color=POS, anchor="start"))

    # обрив — вертикаль лише в зоні наївного, щоб не чіпати написів нижче
    p.append(text((X(2) + X(3)) / 2, y0 - 22, "обрив: стовпець B (145 ліній)", size=10,
                  color=POS, bold=True))
    p.append(text((X(2) + X(3)) / 2, y0 - 8, "перестав влазити", size=10, color=POS))
    p.append(line((X(2) + X(3)) / 2, y0 - 4, (X(2) + X(3)) / 2, Y(266240) + 16,
                  color="#e6b0aa", sw=1.4, dash="5 4"))

    # рекурсивний
    for i in range(len(caches) - 1):
        p.append(line(X(i), Y(recur[i]), X(i + 1), Y(recur[i + 1]), color=NEG, sw=2.6))
    for i, v in enumerate(recur):
        p.append(circle(X(i), Y(v), 4.6, fill=NEG, stroke=NEG, sw=1.0))
    p.append(text(X(0) + 8, Y(recur[0]) + 26, "рекурсія на квадрантах",
                  size=11.5, color=NEG, anchor="start", bold=True))
    p.append(text(X(0) + 8, Y(recur[0]) + 42, "81 920", size=9.5, color=NEG, anchor="start"))
    p.append(text(X(5) - 2, Y(recur[5]) + 20, "16 384", size=9.5, color=NEG, anchor="end"))

    # виноска
    p.append(fitbox(716, 92, 150, 218,
                    "Виміряно\nсимулятором\nз тексту.\n\nN = 128,\nлінія = 8 double.\n\n"
                    "Кеш ×4  →\nпромахів ÷2\nРІВНО:\n65 536 → 32 768.\nЦе і є 1/√M.\n\n"
                    "Жодного M\nу коді рекурсії.",
                    size=10.5, fill="#f4f6f8", stroke=INK, color=INK))

    p.append(fitbox(70, 420, 740, 76,
                    "Наївний тримається, поки в кеші є місце на стовпець B, — і провалюється вдев'ятеро, щойно його нема.\n"
                    "Де саме лежить обрив, вирішують M і B, яких код не знає. Рекурсія обриву не має взагалі: вона спадає\n"
                    "рівно як 1/√M на кожній машині — і на 4 КБ виграє в наївного 36 разів, нічого про кеш не питаючи.",
                    size=11, fill="#f4f6f8", stroke=INK, color=INK))

    render(os.path.join(OUT, "proj-misses.svg"), W, H, *p,
           title="Виміряні промахи: обрив наївного проти 1/√M рекурсії")


if __name__ == "__main__":
    fig_model()
    fig_recursion()
    fig_veb()
    fig_hist_timeline()
    fig_hist_credit()
    fig_hist_resemblance()
    fig_math_volume()
    fig_math_cut()
    fig_math_merge()
    fig_proj_rowcol()
    fig_proj_quadrants()
    fig_proj_misses()
    print("figs: готово")
