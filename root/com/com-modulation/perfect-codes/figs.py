# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GREEN_A = "#e3f3e8"   # заливка кулі
GREEN_B = "#cfe9d7"   # сусідня куля (щоб плитки різнилися)
GREY    = "#ededed"   # нічийне слово


def slova(k):
    """Українська форма слова «слово» за числівником: 1 слово, 24 слова, 8 слів."""
    k10, k100 = k % 10, k % 100
    if k10 == 1 and k100 != 11:
        return "слово"
    if 2 <= k10 <= 4 and not (12 <= k100 <= 14):
        return "слова"
    return "слів"


# ── packing: звичайний код (порожнеча між кулями) vs досконалий (без залишку) ──
# Ідея: простір = сітка клітин-слів. Куля = група клітин навколо кодового слова.
# Ліворуч кулі не перетинаються, але лишають сірі нічийні клітини; праворуч
# кулі ділять увесь простір без залишку — кожна клітина в рівно одній кулі.

def fig_packing():
    W, H = 940, 500
    p = []

    CELL = 40
    COLS, ROWS = 8, 6
    gw, gh = COLS * CELL, ROWS * CELL

    def draw_panel(ox, oy, blocks, fill_grey, title):
        frags = []
        # блоки заданого як список (col, row) верхніх-лівих кутів; кожен 2 шир × 3 вис
        owner = {}
        for bi, (bc, br) in enumerate(blocks):
            for dc in range(2):
                for dr in range(3):
                    owner[(bc + dc, br + dr)] = bi
        # клітини
        for r in range(ROWS):
            for c in range(COLS):
                x, y = ox + c * CELL, oy + r * CELL
                if (c, r) in owner:
                    tint = GREEN_A if owner[(c, r)] % 2 == 0 else GREEN_B
                    frags.append(rect(x, y, CELL, CELL, fill=tint, stroke="#ffffff", sw=1.5, rx=0))
                else:
                    frags.append(rect(x, y, CELL, CELL, fill=(GREY if fill_grey else "#ffffff"),
                                      stroke="#ffffff", sw=1.5, rx=0))
        # межі блоків (кулі) + центр-кодове слово (червона крапка)
        for (bc, br) in blocks:
            x, y = ox + bc * CELL, oy + br * CELL
            frags.append(rect(x, y, 2 * CELL, 3 * CELL, fill="none", stroke=FIELD, sw=2.6, rx=6))
            cx, cy = x + CELL, y + 1.5 * CELL
            frags.append(circle(cx, cy, 8, fill=POS, stroke="#ffffff", sw=1.6))
        frags.append(text(ox + gw / 2, oy - 18, title, size=15, color=INK, bold=True))
        return frags

    # ЛІВА панель: 4 кулі, розкидані з порожнечею між ними
    lox, loy = 55, 96
    left_blocks = [(0, 0), (3, 0), (1, 3), (6, 2)]
    p += draw_panel(lox, loy, left_blocks, fill_grey=True,
                    title="звичайний код — між кулями порожнеча")
    # підпис на нічийну клітину
    p.append(text(lox + gw / 2, loy + gh + 30,
                  "сірі клітини — нічиї: не в жодній кулі", size=12.5, color=MUTED))

    # ПРАВА панель: кулі 2×3 замощують усе (4 стовпці × 2 ряди = 8 куль)
    rox, roy = 555, 96
    right_blocks = [(c, r) for r in (0, 3) for c in (0, 2, 4, 6)]
    p += draw_panel(rox, roy, right_blocks, fill_grey=False,
                    title="досконалий код — кулі заповнюють усе")
    p.append(text(rox + gw / 2, roy + gh + 30,
                  "жодної нічийної клітини: M · V = 2ⁿ", size=12.5, color=FIELD, bold=True))

    # спільна легенда внизу
    ly = 468
    lx = 120
    p.append(rect(lx, ly - 12, 18, 18, fill=GREEN_A, stroke=FIELD, sw=1.8, rx=3))
    p.append(text(lx + 26, ly + 3, "куля (територія кодового слова)", size=12.5, color=INK, anchor="start"))
    p.append(circle(lx + 300, ly - 3, 7, fill=POS, stroke="#ffffff", sw=1.4))
    p.append(text(lx + 314, ly + 3, "кодове слово", size=12.5, color=INK, anchor="start"))
    p.append(rect(lx + 470, ly - 12, 18, 18, fill=GREY, stroke="#cccccc", sw=1.4, rx=3))
    p.append(text(lx + 496, ly + 3, "нічийне слово", size=12.5, color=INK, anchor="start"))

    render(os.path.join(OUT, "packing.svg"), W, H, *p,
           title="Досконалий код: кулі виправлення ділять увесь простір без залишку")


# ── cube-tiling: куб 3-бітних слів ділиться на дві кулі (потрійне повторення) ──
# Ідея: 8 вершин куба = увесь простір; куля навколо 000 — {000,100,010,001},
# куля навколо 111 — {111,011,101,110}. 4 + 4 = 8, жодної нічийної вершини.

def fig_cube_tiling():
    W, H = 860, 520
    p = []

    front = {"000": (215, 375), "100": (365, 375), "110": (365, 215), "010": (215, 215)}
    back  = {"001": (300, 430), "101": (450, 430), "111": (450, 270), "011": (300, 270)}
    pos = {}; pos.update(front); pos.update(back)

    ballA = {"000", "100", "010", "001"}   # куля навколо 000
    ballB = {"111", "011", "101", "110"}   # куля навколо 111
    centers = {"000", "111"}

    def diff1(a, b):
        return sum(1 for i in range(3) if a[i] != b[i]) == 1
    seen = set()
    for a in pos:
        for b in pos:
            if a != b and diff1(a, b) and (b, a) not in seen:
                seen.add((a, b))
                ax, ay = pos[a]; bx, by = pos[b]
                p.append(line(ax, ay, bx, by, color="#e0e0e0", sw=2))

    # вершини: колір за кулею, центри — червоне кільце
    for w, (x, y) in pos.items():
        fill = GREEN_A if w in ballA else "#e6ecfb"
        ring = POS if w in centers else (FIELD if w in ballA else NEG)
        sw = 3.2 if w in centers else 2.0
        p.append(circle(x, y, 21, fill=fill, stroke=ring, sw=sw))
        p.append(text(x, y + 5, w, size=13, color=INK, bold=(w in centers)))

    # підписи куль (осторонь від куба)
    p.append(text(150, 150, "куля навколо 000", size=14, color=FIELD, bold=True))
    p.append(text(150, 172, "(центр + 3 сусіди = 4 слова)", size=11.5, color=MUTED))
    p.append(text(560, 150, "куля навколо 111", size=14, color=NEG, bold=True, anchor="start"))
    p.append(text(560, 172, "(центр + 3 сусіди = 4 слова)", size=11.5, color=MUTED, anchor="start"))

    # права картка-підсумок
    bx, by, bw, bh = 620, 250, 210, 150
    p.append(rect(bx, by, bw, bh, fill="#fbfbfb", stroke="#e4e4e4", sw=1.4, rx=10))
    p.append(text(bx + bw / 2, by + 30, "8 вершин куба", size=14, color=INK, bold=True))
    p.append(text(bx + bw / 2, by + 62, "= 2 кулі × 4 слова", size=14, color=INK))
    p.append(text(bx + bw / 2, by + 90, "= увесь простір 2³", size=14, color=FIELD, bold=True))
    p.append(text(bx + bw / 2, by + 122, "жодної нічийної", size=12.5, color=MUTED))

    p.append(text(W / 2, 500, "потрійне повторення: 000 і 111 — два кодові слова, кулі радіуса t = 1 замощують куб",
                  size=13, color=MUTED, italic=True))

    render(os.path.join(OUT, "cube-tiling.svg"), W, H, *p,
           title="Найменший досконалий код: дві кулі ділять увесь куб 3-бітних слів")


# ── ball-layers: звідки береться множник (q−1)ⁱ ──────────────────────────────
# Ідея: куля будується у два незалежні кроки. Спершу вибираємо, ЯКІ i позицій
# зіпсовано — C(n,i) способів. Потім на кожну з цих i позицій кладемо хибний
# символ — по (q−1) варіантів на позицію, разом (q−1)ⁱ. Добуток = розмір шару.
# Приклад n = 4, q = 3 (алфавіт {0,1,2}), центр 0000.

def fig_ball_layers():
    W, H = 1000, 560
    p = []

    RED_L = "#fdeceb"   # заливка «зіпсованої» позиції
    COL_I, COL_A, COL_X, COL_B, COL_EQ, COL_C = 66, 250, 430, 590, 718, 860

    p.append(text(W / 2, 44, "Куля радіуса t навколо слова 0000:  n = 4 позиції,  алфавіт {0, 1, 2},  q = 3",
                  size=16, color=INK, bold=True))
    p.append(text(W / 2, 68, "шар i — це слова, у яких зіпсовано РІВНО i позицій",
                  size=13, color=MUTED, italic=True))

    # заголовки колонок
    hy = 108
    p.append(text(COL_A, hy, "які позиції зіпсовано", size=13, color=INK, bold=True))
    p.append(text(COL_A, hy + 19, "C(4, i) способів", size=12, color=MUTED))
    p.append(text(COL_B, hy, "який хибний символ на кожній", size=13, color=INK, bold=True))
    p.append(text(COL_B, hy + 19, "(q−1)ⁱ = 2ⁱ способів", size=12, color=MUTED))
    p.append(text(COL_C, hy, "слів у шарі", size=13, color=INK, bold=True))
    p.append(text(COL_C, hy + 19, "добуток", size=12, color=MUTED))
    p.append(line(40, hy + 32, W - 40, hy + 32, color="#dddddd", sw=1.4))

    rows = [
        # (i, маска зіпсованих позицій, C(4,i), 2^i, текст-символи)
        (0, [0, 0, 0, 0], 1, 1, "нічого не зіпсовано"),
        (1, [1, 0, 0, 0], 4, 2, "× ∈ {1, 2}"),
        (2, [1, 1, 0, 0], 6, 4, "кожен × ∈ {1, 2}"),
    ]

    CELL = 30
    for k, (i, mask, cni, pw, sym) in enumerate(rows):
        y = 178 + k * 108

        # бейдж шару
        p.append(circle(COL_I, y, 22, fill="#eef2f7", stroke=NEG, sw=2.2))
        p.append(text(COL_I, y + 5, "i = %d" % i, size=13, color=NEG, bold=True))

        # A: маска позицій — 4 клітини
        x0 = COL_A - 2 * CELL
        for j, m in enumerate(mask):
            x = x0 + j * CELL
            p.append(rect(x, y - CELL / 2, CELL, CELL,
                          fill=(RED_L if m else "#f7f7f7"),
                          stroke=(POS if m else "#d8d8d8"), sw=(2.0 if m else 1.2), rx=4))
            p.append(text(x + CELL / 2, y + 5, ("×" if m else "·"),
                          size=15, color=(POS if m else "#9aa0a6"), bold=bool(m)))
        p.append(text(COL_A, y + 42, "C(4, %d) = %d" % (i, cni), size=13, color=INK, bold=True))

        # знак множення
        p.append(text(COL_X, y, "×", size=20, color=MUTED, bold=True))

        # B: варіанти хибних символів
        p.append(text(COL_B, y - 6, sym, size=13, color=INK))
        p.append(text(COL_B, y + 42, "2%s = %d" % (("⁰", "¹", "²")[i], pw), size=13, color=INK, bold=True))

        # знак рівності
        p.append(text(COL_EQ, y, "=", size=20, color=MUTED, bold=True))

        # C: розмір шару
        p.append(textbox(COL_C, y, "%d %s" % (cni * pw, slova(cni * pw)), size=15, pad=13,
                         fill="#eefaf1", stroke=FIELD, sw=2.0, color=INK, bold=True, min_w=120)[0])

    # ключове зауваження — чому q−1, а не q
    ny = 502
    p.append(rect(52, ny - 34, 520, 62, fill="#fffaf0", stroke="#e6c886", sw=1.6, rx=8))
    p.append(mtext(312, ny - 12, ["ЧОМУ q−1, а не q: позиція, оголошена зіпсованою,",
                                  "не має права лишитися правильною — правильний символ виключено"],
                   size=12.5, color=INK, lh=1.35))

    # підсумок кулі радіуса 2
    p.append(textbox(800, ny - 4, ["V(4, 2) = 1 + 8 + 24 = 33"], size=15, pad=15,
                     fill="#eef2f7", stroke=NEG, sw=2.2, color=INK, bold=True)[0])

    render(os.path.join(OUT, "ball-layers.svg"), W, H, *p,
           title="Розмір кулі: вибір позицій × вибір хибних символів = C(n,i)·(q−1)ⁱ")


# ── repetition-parity: повторення досконале ⟺ довжина непарна ────────────────
# Ідея: розкласти простір на шари за вагою; ширина шару ∝ кількості слів у ньому.
# Непарне n: два півпростори точно порівну, розріз проходить рівно посередині.
# Парне n: середній шар C(n, n/2) рівновіддалений від обох центрів — нічия.

def fig_repetition_parity():
    W, H = 1000, 540
    p = []
    GREY = "#ededed"
    BLUE_L = "#e6ecfb"

    GX0, GW = 92, 800

    def panel(y_title, n, t, title, verdict, verdict_color):
        from math import comb
        cnts = [comb(n, i) for i in range(n + 1)]
        total = 2 ** n
        unit = GW / total

        yb = y_title + 82          # верх коробок
        BH = 48

        p.append(text(W / 2, y_title, title, size=15, color=INK, bold=True))

        # хто володіє шаром: A (0..t), нічия, B (n-t..n)
        owner = []
        for i in range(n + 1):
            if i <= t: owner.append("A")
            elif i >= n - t: owner.append("B")
            else: owner.append("-")

        x = GX0
        spans = {"A": [None, None], "B": [None, None], "-": [None, None]}
        for i, c in enumerate(cnts):
            w = c * unit
            o = owner[i]
            fill = {"A": GREEN_A, "B": BLUE_L, "-": GREY}[o]
            stroke = {"A": FIELD, "B": NEG, "-": "#c4c4c4"}[o]
            p.append(rect(x, yb, w, BH, fill=fill, stroke=stroke, sw=1.8, rx=3))
            # кількість слів — над коробкою; номер ваги — під коробкою
            p.append(text(x + w / 2, yb - 10, str(c), size=12.5, color=INK, bold=True))
            p.append(text(x + w / 2, yb + BH + 18, str(i), size=12.5, color=MUTED))
            if spans[o][0] is None: spans[o][0] = x
            spans[o][1] = x + w
            x += w

        p.append(text(GX0 - 40, yb + BH + 18, "вага:", size=12.5, color=MUTED, anchor="end"))

        # дужки-підписи над шарами
        by = yb - 32
        def bracket(o, label, color):
            a, b = spans[o]
            if a is None: return
            p.append(line(a + 2, by, b - 2, by, color=color, sw=2.2))
            p.append(line(a + 2, by, a + 2, by + 8, color=color, sw=2.2))
            p.append(line(b - 2, by, b - 2, by + 8, color=color, sw=2.2))
            p.append(text((a + b) / 2, by - 9, label, size=12.5, color=color, bold=True))
        vb = sum(cnts[:t + 1])
        tie = sum(c for i, c in enumerate(cnts) if owner[i] == "-")
        bracket("A", "куля навколо %s (радіус %d): %d %s" % ("0" * n, t, vb, slova(vb)), FIELD)
        bracket("B", "куля навколо %s: %d %s" % ("1" * n, vb, slova(vb)), NEG)
        bracket("-", "нічия: %d %s" % (tie, slova(tie)), "#8a8a8a")

        p.append(text(W / 2, yb + BH + 48, verdict, size=13.5, color=verdict_color, bold=True))

    panel(78, 5, 2, "n = 5 (непарна):  d = 5,  t = 2 — кулі ділять простір рівно навпіл",
          "M · V = 2 · 16 = 32 = 2⁵ — жодного нічийного слова: ДОСКОНАЛИЙ", FIELD)
    panel(318, 4, 1, "n = 4 (парна):  d = 4,  t = 1 — між кулями застряг цілий шар",
          "M · V = 2 · 5 = 10, а 2⁴ = 16: бракує рівно C(4,2) = 6 слів ваги 2 — НЕ досконалий", POS)

    render(os.path.join(OUT, "repetition-parity.svg"), W, H, *p,
           title="Повторення досконале лише за непарної довжини: парність лишає нічийний шар посередині")


# ── integrality-sieve: скільки пар (n,t) переживає фільтр подільності ────────
# Ідея: перебрати всі пари n = 3…100, t = 1…5 для q = 2 і лишити ті, де V(n,t)
# ділить 2ⁿ. З 470 пар лишається 11: діагональ повторення, рядок Геммінга,
# одна точка Голея — і один ПРИВИД n = 90, де арифметика сходиться, а коду нема.

def fig_integrality_sieve():
    W, H = 1000, 500
    p = []

    N0, N1 = 3, 100
    DX = 8.9
    X0 = 62
    def px(n): return X0 + (n - N0) * DX
    def py(t): return 262 - (t - 1) * 24

    p.append(text(W / 2, 58, "перебрано всі 470 пар n = 3…100, t = 1…5 — умову проходять лише 11",
                  size=13, color=MUTED, italic=True))

    # усі перевірені пари — ледь помітні крапки
    real = {(3, 1), (5, 2), (7, 1), (7, 3), (9, 4), (11, 5), (15, 1), (23, 3), (31, 1), (63, 1)}
    phantom = (90, 2)
    for n in range(N0, N1 + 1):
        for t in range(1, 6):
            if 2 * t + 1 > n: continue
            if (n, t) in real or (n, t) == phantom: continue
            p.append(circle(px(n), py(t), 1.5, fill="#dcdcdc", stroke="none", sw=0))

    for t in range(1, 6):
        p.append(text(X0 - 24, py(t) + 4, "t = %d" % t, size=11.5, color=MUTED, anchor="end"))

    # уцілілі пари
    for (n, t) in sorted(real):
        p.append(circle(px(n), py(t), 5.4, fill=FIELD, stroke="#ffffff", sw=1.5))
    p.append(circle(px(phantom[0]), py(phantom[1]), 5.4, fill=POS, stroke="#ffffff", sw=1.5))

    # дужка під рядком t = 1: сімейство Геммінга
    bx0, bx1, by = px(7) - 8, px(63) + 8, 286
    p.append(line(bx0, by, bx1, by, color=FIELD, sw=2.0))
    p.append(line(bx0, by, bx0, by - 7, color=FIELD, sw=2.0))
    p.append(line(bx1, by, bx1, by - 7, color=FIELD, sw=2.0))
    p.append(text((bx0 + bx1) / 2, by + 20, "рядок t = 1 — сімейство Геммінга: довжини 7, 15, 31, 63",
                  size=12.5, color=FIELD, bold=True))

    # осі
    ay = 332
    p.append(line(X0 - 14, ay, px(N1) + 10, ay, color="#bbbbbb", sw=1.4))
    for n in range(10, 101, 10):
        p.append(line(px(n), ay, px(n), ay + 6, color="#bbbbbb", sw=1.4))
        p.append(text(px(n), ay + 22, str(n), size=11.5, color=MUTED))
    p.append(text(px(N1) + 10, ay + 44, "n — довжина слова", size=12.5, color=MUTED, anchor="end"))

    # виноска: діагональ повторення (зліва вгорі, поряд із самою діагоналлю)
    p.append(line(px(3) - 16, py(1) - 2, px(11) + 2, py(5) - 16, color="#8a8a8a", sw=1.4, dash="4,3"))
    p.append(line(146, 150, 136, py(5) - 18, color="#8a8a8a", sw=1.2))
    p.append(textbox(150, 120, ["діагональ n = 2t+1:", "повторення непарної довжини"],
                     size=12, pad=9, fill="#f7f7f7", stroke="#b9b9b9", sw=1.6, color=INK)[0])

    # виноска: Голей
    p.append(line(px(23) + 5, py(3) - 6, 340, 146, color=MUTED, sw=1.2))
    p.append(textbox(438, 118, ["Голей [23, 12, 7]", "єдиний острівець поза сімействами"],
                     size=12, pad=9, fill="#eefaf1", stroke=FIELD, sw=1.8, color=INK)[0])

    # виноска: привид n = 90
    p.append(line(px(90) - 2, py(2) - 7, 792, 152, color=POS, sw=1.2))
    p.append(textbox(756, 116, ["ПРИВИД n = 90, t = 2", "арифметика сходиться (V = 2¹²),", "а коду не існує: 88/3 не ціле"],
                     size=12, pad=9, fill="#fdeceb", stroke=POS, sw=1.8, color=INK)[0])

    # легенда
    ly = 452
    p.append(circle(196, ly - 4, 1.8, fill="#dcdcdc", stroke="none", sw=0))
    p.append(text(210, ly, "пара відсіяна (V не ділить 2ⁿ)", size=12, color=MUTED, anchor="start"))
    p.append(circle(452, ly - 4, 5.4, fill=FIELD, stroke="#ffffff", sw=1.4))
    p.append(text(466, ly, "код справді існує", size=12, color=INK, anchor="start"))
    p.append(circle(636, ly - 4, 5.4, fill=POS, stroke="#ffffff", sw=1.4))
    p.append(text(650, ly, "умову пройдено, а коду немає", size=12, color=INK, anchor="start"))

    render(os.path.join(OUT, "integrality-sieve.svg"), W, H, *p,
           title="Умова подільності відсіює майже все: з 470 пар лишається 11, і одна з них — привид")


# ── golay-timeline: хронологія відкриття й закриття питання досконалих кодів ──
# Ідея: порядок подій не той, якого чекаєш. Код надрукували в журналі футбольного
# тоталізатора РАНІШЕ за наукову статтю; здогад із тієї статті доводили 24 роки;
# а первість гравця виплила аж через сорок чотири.

def fig_golay_timeline():
    W, H = 980, 880
    p = []
    SPINE = 150
    CARD_X, CARD_W = 178, 760

    events = [
        ("1947", "Юхані Віртакалліо друкує 729 стовпчиків у «Veikkaaja»",
         "фінський журнал тоталізатора; це трійковий код [11, 6, 5] — але цього ще ніхто не знає", POS),
        ("1948", "Шеннон наводить код [7, 4] як приклад у §17",
         "метод прямо приписано Геммінгові; сам Геммінг ще не опублікувався", MUTED),
        ("1949", "Голей: «Notes on Digital Coding», Proc. IRE 37, с. 657",
         "півсторінки: q-ковий Геммінг, перша перевірна матриця, [23, 12, 7], [11, 6, 5] і здогад", POS),
        ("1950", "Геммінг нарешті друкує власну статтю",
         "патентні застереження затримали публікацію на три роки", MUTED),
        ("1957", "Стюарт Ллойд: «Binary block coding» — теорема Ллойда",
         "необхідна умова: корені многочлена Ллойда мусять бути цілими — знаряддя пошуку", NEG),
        ("1962", "Юрій Васильєв: нелінійні досконалі коди",
         "параметри Геммінга, але код не лінійний — отже, параметри не визначають самого коду", MUTED),
        ("1970–71", "Як ван Лінт відтинає випадок за випадком",
         "над GF(q) немає досконалих кодів на дві й на три помилки", NEG),
        ("1973", "Аймо Тієтявяйнен закриває питання над скінченними полями",
         "незалежно — Віктор Зинов'єв і Володимир Леонтьєв; здогад Голея доведено через 24 роки", FIELD),
        ("1991–93", "Ііро Гонкала й Олександр Барг знаходять Віртакалліо",
         "первість фінського гравця виходить на світло через сорок чотири роки", POS),
    ]

    p.append(line(SPINE, 74, SPINE, 812, color="#dcdcdc", sw=3))

    y = 100
    for (year, title, detail, col) in events:
        p.append(text(130, y + 5, year, size=13, color=col, anchor="end", bold=True))
        p.append(line(158, y, CARD_X, y, color="#dcdcdc", sw=1.6))
        p.append(rect(CARD_X, y - 32, CARD_W, 64, fill="#fbfbfb", stroke="#e8e8e8", sw=1.3, rx=8))
        p.append(text(CARD_X + 16, y - 7, title, size=14, color=INK, anchor="start", bold=True))
        p.append(text(CARD_X + 16, y + 16, detail, size=12, color=MUTED, anchor="start"))
        p.append(circle(SPINE, y, 7, fill=col, stroke="#ffffff", sw=2.4))
        y += 84

    p.append(text(W / 2, 848,
                  "код із журналу тоталізатора випередив наукову статтю; "
                  "здогад із тієї статті доводили двадцять чотири роки",
                  size=13, color=MUTED, italic=True))

    render(os.path.join(OUT, "golay-timeline.svg"), W, H, *p,
           title="Досконалі коди: хто, коли й у якому порядку")


# ── football-pool: чому саме 11 символів — купон тоталізатора на 12 матчів ────
# Ідея: 12 матчів × три наслідки (1/X/2) = трійковий алфавіт. Один матч гравець
# знає напевно й виносить за дужки → лишається 11. Система з 729 рядків укриває
# усі 3¹¹ = 177 147 наслідків кулями радіуса 2: 729 · 243 = 177 147.

def fig_football_pool():
    W, H = 980, 520
    p = []

    CX, CY, CW, CH = 56, 76, 260, 400
    SURE = 3                       # індекс «певного» матчу (0-based)
    p.append(rect(CX, CY, CW, CH, fill="#ffffff", stroke="#d8d8d8", sw=1.6, rx=10))
    p.append(text(CX + CW / 2, CY + 28, "купон: 12 матчів", size=14, color=INK, bold=True))
    p.append(text(CX + CW / 2, CY + 48, "у кожному — 1, X або 2", size=12, color=MUTED))

    ROW0, STEP = CY + 84, 25
    BX = [CX + 132, CX + 164, CX + 196]
    BW, BH = 26, 19

    p.append(text(CX + 20, ROW0 - 14, "матч", size=12, color=MUTED, anchor="start"))
    for i, lbl in enumerate(("1", "X", "2")):
        p.append(text(BX[i] + BW / 2, ROW0 - 14, lbl, size=12, color=MUTED, bold=True))

    for i in range(12):
        y = ROW0 + i * STEP
        if i == SURE:
            p.append(rect(CX + 12, y - 4, CW - 24, BH + 8, fill="#eaf7ef",
                          stroke=FIELD, sw=1.4, rx=5))
        p.append(text(CX + 20, y + 14, "матч %d" % (i + 1), size=12,
                      color=(INK if i == SURE else MUTED), anchor="start"))
        for k in range(3):
            mark = (i == SURE and k == 0)
            p.append(rect(BX[k], y, BW, BH,
                          fill=("#ffffff" if not mark else FIELD),
                          stroke=(FIELD if mark else "#d8d8d8"),
                          sw=(2.0 if mark else 1.2), rx=3))

    KX, KW = 380, 552
    p.append(arrow(324, ROW0 + SURE * STEP + 10, KX - 8, 142, color=FIELD, sw=2))

    p.append(rect(KX, 90, KW, 96, fill="#eaf7ef", stroke=FIELD, sw=1.5, rx=9))
    p.append(text(KX + 18, 120, "один матч гравець знає напевно", size=14,
                  color=INK, anchor="start", bold=True))
    p.append(text(KX + 18, 145, "його виносять за дужки — системою грають решту", size=12,
                  color=MUTED, anchor="start"))
    p.append(text(KX + 18, 172, "лишається 11 матчів", size=13, color=FIELD,
                  anchor="start", bold=True))

    p.append(arrow(KX + KW / 2, 188, KX + KW / 2, 202, color="#c8c8c8", sw=2))

    p.append(rect(KX, 204, KW, 80, fill="#fbfbfb", stroke="#e0e0e0", sw=1.4, rx=9))
    p.append(text(KX + 18, 234, "3¹¹ = 177 147 можливих рядків", size=14,
                  color=INK, anchor="start", bold=True))
    p.append(text(KX + 18, 260, "зіграти всі — годі й мріяти", size=12,
                  color=MUTED, anchor="start"))

    p.append(arrow(KX + KW / 2, 286, KX + KW / 2, 300, color="#c8c8c8", sw=2))

    p.append(rect(KX, 302, KW, 130, fill="#fdecea", stroke=POS, sw=1.5, rx=9))
    p.append(text(KX + 18, 332, "система Віртакалліо: 729 рядків", size=14,
                  color=POS, anchor="start", bold=True))
    p.append(text(KX + 18, 358, "729 · 243 = 177 147 — рівно весь простір", size=13,
                  color=INK, anchor="start"))
    p.append(text(KX + 18, 382, "кожен рядок укриває 243 сусідні — з ≤ 2 хибами", size=12,
                  color=MUTED, anchor="start"))
    p.append(text(KX + 18, 412, "гарантія: щонайменше 10 із 12 вгадано", size=13,
                  color=POS, anchor="start", bold=True))

    p.append(text(W / 2, 498,
                  "Віртакалліо шукав систему для тоталізатора — а знайшов досконалий код",
                  size=13, color=MUTED, italic=True))

    render(os.path.join(OUT, "football-pool.svg"), W, H, *p,
           title="Чому саме одинадцять: купон тоталізатора на дванадцять матчів")


if __name__ == "__main__":
    fig_packing()
    fig_cube_tiling()
    fig_ball_layers()
    fig_repetition_parity()
    fig_integrality_sieve()
    fig_golay_timeline()
    fig_football_pool()
    print("OK: figures written to", OUT)
