# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLUE_F  = "#e8eefc"
RED_F   = "#fdecea"
GREEN_F = "#e6f7ee"


# ── invariant: чому крок не міняє НСД ────────────────────────────────────────
# Ідея: спільна мірка d вкладається ціло в a і в b, тому вкладається ціло й у
# хвіст a − b. І навпаки. Отже множина спільних дільників пари не змінюється —
# а разом із нею й найбільший її елемент.
def fig_invariant():
    W, H = 1000, 470
    p = []

    TW, TH = 36, 40          # плитка-мірка d = 3
    x0 = 140

    def bar(x, y, n, fill, stroke):
        out = []
        for i in range(n):
            out.append(rect(x + i * TW, y, TW, TH, fill=fill, stroke=stroke, sw=1.6, rx=3))
            out.append(text(x + i * TW + TW / 2, y + TH / 2 + 4.5, "3", size=13, color=stroke))
        return "".join(out)

    yA, yB, yD = 108, 178, 248
    p.append(bar(x0, yA, 7, BLUE_F, NEG))                  # a = 21 = 7 мірок
    p.append(bar(x0, yB, 5, GREEN_F, FIELD))               # b = 15 = 5 мірок
    p.append(bar(x0 + 5 * TW, yD, 2, RED_F, POS))          # a − b = 6 = 2 мірки

    for y, lab, col in ((yA, "a = 21", NEG), (yB, "b = 15", FIELD), (yD, "a − b = 6", POS)):
        p.append(text(x0 - 18, y + TH / 2 + 5, lab, size=15, color=col, anchor="end", bold=True))

    # межа «де закінчується b» і «де закінчується a» — по краях плиток
    p.append(line(x0 + 5 * TW, yA - 14, x0 + 5 * TW, yD + TH + 14, color=MUTED, sw=1.4, dash="5,4"))
    p.append(line(x0 + 7 * TW, yA - 14, x0 + 7 * TW, yD + TH + 14, color=MUTED, sw=1.4, dash="5,4"))
    p.append(text(x0 + 6 * TW, yA - 24, "хвіст a понад b", size=12, color=MUTED, italic=True))

    p.append(mtext(x0 + 3.5 * TW, yD + TH + 44,
                   ["мірка d = 3 вкладається ціло 7 разів у a і 5 разів у b —",
                    "отже вкладається ціло й у хвіст a − b (рівно 2 рази)"],
                   size=13, color=INK, lh=1.5))

    # права колонка — те саме мовою подільності
    xR = 560
    p.append(text(xR, 96, "Крок не міняє спільних дільників", size=16, color=INK,
                  anchor="start", bold=True))
    p.append(text(xR + 8, 140, "d | a  і  d | b   ⟹   d | (a − b)", size=15, color=NEG, anchor="start"))
    p.append(text(xR + 8, 172, "d | b  і  d | (a − b)   ⟹   d | a", size=15, color=POS, anchor="start"))

    p.append(mtext(xR, 224,
                   ["Стрілки в обидва боки, тому пари (a, b) і (b, a − b)",
                    "мають ТУ САМУ множину спільних дільників —",
                    "а отже й той самий найбільший її елемент."],
                   size=13.5, color=INK, anchor="start", lh=1.5))

    p.append(fitbox(xR, 316, 380, 58, "НСД(a, b) = НСД(b, a − b)",
                    size=21, fill=GREEN_F, stroke=FIELD, sw=2.5, bold=True, color=INK))
    p.append(text(xR + 190, 398, "Дільники шукати не треба — досить віднімати.",
                  size=12.5, color=MUTED, italic=True))

    return render(os.path.join(OUT, "invariant.svg"), W, H, *p)


# ── tiling: алгоритм = задача про плитку ─────────────────────────────────────
# Ідея: відрізати від прямокутника найбільший можливий квадрат = взяти залишок.
# Частка = скільки квадратів цього розміру відрізали; сторона ОСТАННЬОГО
# квадрата (той, що ділить усе націло) і є НСД.
def fig_tiling():
    W, H = 1000, 560
    p = []

    s = 22                    # px на одиницю
    x0, y0 = 76, 122
    w21, h15 = 21 * s, 15 * s

    # 1 квадрат 15×15
    p.append(rect(x0, y0, 15 * s, 15 * s, fill=BLUE_F, stroke=NEG, sw=2, rx=3))
    p.append(text(x0 + 7.5 * s, y0 + 7.5 * s + 6, "15 × 15", size=18, color=NEG, bold=True))

    # 2 квадрати 6×6
    xa = x0 + 15 * s
    for i in range(2):
        p.append(rect(xa, y0 + i * 6 * s, 6 * s, 6 * s, fill=RED_F, stroke=POS, sw=2, rx=3))
        p.append(text(xa + 3 * s, y0 + i * 6 * s + 3 * s + 5, "6 × 6", size=14, color=POS, bold=True))

    # 2 квадрати 3×3 — сторона останнього і є НСД
    yb = y0 + 12 * s
    for i in range(2):
        p.append(rect(xa + i * 3 * s, yb, 3 * s, 3 * s, fill=GREEN_F, stroke=FIELD, sw=2, rx=3))
        p.append(text(xa + i * 3 * s + 1.5 * s, yb + 1.5 * s + 4, "3×3", size=11, color=FIELD, bold=True))

    # розміри прямокутника
    p.append(line(x0, y0 - 22, x0 + w21, y0 - 22, color=MUTED, sw=1.4))
    p.append(text(x0 + w21 / 2, y0 - 32, "21", size=15, color=MUTED, bold=True))
    p.append(line(x0 - 26, y0, x0 - 26, y0 + h15, color=MUTED, sw=1.4))
    p.append(text(x0 - 46, y0 + h15 / 2 + 5, "15", size=15, color=MUTED, bold=True))

    # права колонка — арифметика того самого
    xR = 620
    rows = [
        ("21 = 1 · 15 + 6", "один квадрат 15×15 — лишається смуга 15×6", NEG),
        ("15 = 2 · 6 + 3",  "два квадрати 6×6 — лишається смуга 6×3",    POS),
        ("6 = 2 · 3 + 0",   "два квадрати 3×3 — і залишку немає",        FIELD),
    ]
    y = 152
    for eq, note, col in rows:
        p.append(text(xR, y, eq, size=18, color=col, anchor="start", bold=True))
        p.append(text(xR + 6, y + 24, note, size=12.5, color=MUTED, anchor="start"))
        y += 84

    p.append(fitbox(xR - 6, 400, 350, 58, "НСД(21, 15) = 3",
                    size=21, fill=GREEN_F, stroke=FIELD, sw=2.5, bold=True, color=INK))
    p.append(text(xR + 169, 482, "сторона останнього квадрата", size=12.5, color=MUTED, italic=True))

    p.append(text(x0 + w21 / 2, 508,
                  "Частки 1, 2, 2 — це кількості квадратів кожного розміру.",
                  size=13, color=INK))

    return render(os.path.join(OUT, "tiling.svg"), W, H, *p)


# ── speed: чому кроків мало і коли їх найбільше ──────────────────────────────
# Ідея: у типовому випадку залишок обвалюється стрибками; найповільніше — коли
# всі частки дорівнюють 1, а це рівно сусідні числа Фібоначчі (Ламе, 1844).
def fig_speed():
    W, H = 1000, 650
    p = []

    BARW = 250
    ROW = 46

    def column(x, head, seq, color, note):
        out = [text(x, 104, head, size=15.5, color=INK, anchor="start", bold=True)]
        top = float(seq[0])
        y = 146
        for v in seq:
            L = max(3.0, BARW * v / top) if v else 0.0
            out.append(text(x - 14, y + 13, str(v), size=13, color=INK, anchor="end", bold=True))
            if v:
                out.append(rect(x, y, L, 20, fill=color, stroke=color, sw=1, rx=3))
            else:
                out.append(text(x + 4, y + 14, "0 — стоп", size=13, color=FIELD,
                                anchor="start", bold=True))
            y += ROW
        out.append(text(x, y + 16, note, size=12.5, color=MUTED, anchor="start", italic=True))
        return "".join(out), y + 16

    left, _ = column(150, "Типово: НСД(1071, 462) — 3 кроки",
                     [1071, 462, 147, 21, 0], NEG,
                     "великі частки → залишок обвалюється")
    right, _ = column(640, "Найгірше: НСД(21, 13) — 6 кроків",
                      [21, 13, 8, 5, 3, 2, 1, 0], POS,
                      "усі частки = 1 → залишок сповзає ледь-ледь")
    p.append(left)
    p.append(right)

    p.append(text(150, 128, "послідовність залишків (довжина — в межах своєї колонки)",
                  size=11.5, color=MUTED, anchor="start", italic=True))

    p.append(fitbox(96, 558, 810, 66,
                    "За кожні ДВА кроки залишок меншає щонайменше вдвічі → кроків близько log.\n"
                    "Найповільніше — на сусідніх числах Фібоначчі: Ламе (1844) довів межу 5 · (цифр меншого).",
                    size=14, fill=FILL, stroke=NEG, sw=2))

    return render(os.path.join(OUT, "speed.svg"), W, H, *p)


# ── binrules: чотири правила двійкового НСД ──────────────────────────────────
# Ідея: жодне правило не шукає дільників — кожне лише знімає двійку або
# замінює пару меншою. Двійку НСД набирає ЛИШЕ там, де вона спільна.
def fig_binrules():
    W, H = 1060, 560
    p = []

    rows = [
        ("НСД(u, 0) = u",
         ["Нуль ділиться на будь-що, тож обмежує лише u.",
          "База: далі йти нема куди."],
         FIELD, GREEN_F),
        ("u, v парні:   НСД = 2 · НСД(u/2, v/2)",
         ["Двійка спільна — вона входить у відповідь.",
          "Виносимо її й лічимо, скільки разів винесли."],
         NEG, BLUE_F),
        ("u непарне, v парне:   НСД(u, v) = НСД(u, v/2)",
         ["Двійка є лише в v, отже спільною бути не може.",
          "Викидаємо її задарма — відповідь не змінюється."],
         NEG, BLUE_F),
        ("u, v непарні, u ≤ v:   НСД(u, v) = НСД(u, v − u)",
         ["Той самий крок Евкліда — віднімання.",
          "Різниця двох непарних ПАРНА → одразу спрацює правило вище."],
         POS, RED_F),
    ]

    y = 96
    for rule, why, col, fill in rows:
        p.append(fitbox(56, y, 430, 66, rule, size=16, fill=fill, stroke=col, sw=2,
                        bold=True, color=INK))
        p.append(mtext(514, y + 24, why, size=13, color=INK, anchor="start", lh=1.55))
        y += 104

    p.append(fitbox(56, 500, 948, 44,
                    "Жодне правило не шукає дільників: кожне або знімає двійку, або зменшує пару.",
                    size=14.5, fill=FILL, stroke=MUTED, sw=1.8))

    return render(os.path.join(OUT, "binrules.svg"), W, H, *p,
                  title="Двійковий НСД: ділення замінено на зсув, порівняння й віднімання")


# ── bintrace: та сама пара — ділення проти зсувів ────────────────────────────
# Ідея: кроків БІЛЬШЕ (5 проти 3), але жоден із них не ділення. Обмін
# «дорогі кроки → більше дешевих» і є весь сенс двійкового НСД.
def fig_bintrace():
    W, H = 1060, 580
    p = []

    # ліва колонка — Евклід
    p.append(text(70, 96, "Евклід: 3 кроки — і всі три ДІЛЕННЯ", size=15.5,
                  color=INK, anchor="start", bold=True))
    eucl = ["1071 = 2 · 462 + 147", "462 = 3 · 147 + 21", "147 = 7 · 21 + 0"]
    y = 140
    for e in eucl:
        p.append(fitbox(70, y, 366, 50, e, size=15, fill=RED_F, stroke=POS, sw=1.8))
        p.append(text(70, y + 72, "ділення — найдорожча ціла операція", size=11.5,
                      color=MUTED, anchor="start", italic=True))
        y += 96
    p.append(fitbox(70, y + 6, 366, 46, "НСД = 21", size=17, fill=GREEN_F,
                    stroke=FIELD, sw=2.2, bold=True))

    # права колонка — двійковий
    p.append(text(560, 96, "Двійковий: 5 кроків — жодного ділення", size=15.5,
                  color=INK, anchor="start", bold=True))
    p.append(text(560, 118, "k = ctz(1071 | 462) = 0  →  спільних двійок немає",
                  size=11.5, color=MUTED, anchor="start", italic=True))

    hdr = [("крок", 578), ("u", 668), ("v", 748), ("що зробили", 838)]
    for h, x in hdr:
        p.append(text(x, 150, h, size=12.5, color=MUTED, anchor="start", bold=True))
    p.append(line(560, 158, 1004, 158, color=MUTED, sw=1.2))

    trace = [
        ("1", "231", "840", "v>>1, обмін, −"),
        ("2", "105", "126", "v>>3, обмін, −"),
        ("3", "63", "42", "v>>1, обмін, −"),
        ("4", "21", "42", "v>>1, обмін, −"),
        ("5", "21", "0", "v>>1, −  → стоп"),
    ]
    y = 182
    for n, u, v, op in trace:
        p.append(text(578, y, n, size=13.5, color=MUTED, anchor="start"))
        p.append(text(668, y, u, size=13.5, color=NEG, anchor="start", bold=True))
        p.append(text(748, y, v, size=13.5, color=NEG, anchor="start", bold=True))
        p.append(text(838, y, op, size=12.5, color=INK, anchor="start"))
        y += 34
    p.append(text(560, y + 18, "лише зсуви, порівняння й віднімання — кожне ≈ такт",
                  size=11.5, color=MUTED, anchor="start", italic=True))
    p.append(fitbox(560, y + 34, 444, 46, "u << k = 21 << 0 = 21", size=17,
                    fill=GREEN_F, stroke=FIELD, sw=2.2, bold=True))

    p.append(fitbox(56, 512, 948, 50,
                    "Обмін свідомий: кроків ~на 20 % більше, зате жодного ділення.\n"
                    "На випадкових 64-бітних парах — 37 ділень проти 45 зсувів-віднімань.",
                    size=13.5, fill=FILL, stroke=NEG, sw=2))

    return render(os.path.join(OUT, "bintrace.svg"), W, H, *p)


# ── lcmtrap: чому в НСК ділять ДО множення ──────────────────────────────────
# Ідея: переповнюється не відповідь, а дорога до неї. Той самий НСК = 2³²
# влазить із величезним запасом — але тільки якщо не множити a·b спершу.
def fig_lcmtrap():
    W, H = 1060, 540
    p = []

    p.append(text(530, 74, "a = 2³¹ = 2 147 483 648        b = 2³² = 4 294 967 296        "
                           "НСД(a, b) = 2³¹", size=15, color=INK, bold=True))

    # ── лана 1: наївно
    p.append(fitbox(56, 116, 200, 54, "наївно\na · b / НСД", size=14, fill=RED_F,
                    stroke=POS, sw=2, bold=True, color=POS))
    p.append(arrow(264, 143, 316, 143, color=POS))
    p.append(fitbox(322, 116, 250, 54, "a · b = 2⁶³", size=15, fill=RED_F, stroke=POS, sw=1.8))
    p.append(arrow(580, 143, 632, 143, color=POS))
    p.append(fitbox(638, 116, 366, 54, "9 223 372 036 854 775 808", size=15,
                    fill=RED_F, stroke=POS, sw=1.8))

    p.append(text(638, 194, "INT64_MAX  =  9 223 372 036 854 775 807", size=13.5,
                  color=MUTED, anchor="start"))
    p.append(text(638, 216, "більше за стелю рівно на ОДИНИЦЮ", size=13.5,
                  color=POS, anchor="start", bold=True))

    p.append(arrow(820, 232, 820, 268, color=POS))
    p.append(fitbox(560, 274, 444, 54, "переповнення → −9 223 372 036 854 775 808",
                    size=14, fill=RED_F, stroke=POS, sw=2, color=POS, bold=True))
    p.append(arrow(820, 336, 820, 368, color=POS))
    p.append(fitbox(560, 374, 444, 54, "/ 2³¹  →  НСК = −4 294 967 296",
                    size=15, fill=RED_F, stroke=POS, sw=2.4, color=POS, bold=True))
    p.append(text(782, 448, "НСК вийшов ВІД'ЄМНИЙ", size=13, color=POS,
                  anchor="middle", italic=True))

    # ── лана 2: правильно
    p.append(fitbox(56, 274, 200, 54, "правильно\na / НСД · b", size=14, fill=GREEN_F,
                    stroke=FIELD, sw=2, bold=True, color=FIELD))
    p.append(arrow(264, 301, 316, 301, color=FIELD))
    p.append(fitbox(322, 274, 200, 54, "a / 2³¹ = 1", size=15, fill=GREEN_F,
                    stroke=FIELD, sw=1.8))
    p.append(arrow(422, 336, 422, 368, color=FIELD))
    p.append(text(444, 356, "спершу ділимо — число меншає", size=11.5,
                  color=MUTED, anchor="start", italic=True))
    p.append(fitbox(322, 374, 200, 54, "1 · b = 2³²", size=15, fill=GREEN_F,
                    stroke=FIELD, sw=2.4, bold=True))
    p.append(text(422, 448, "НСК = 4 294 967 296 ✓", size=13, color=FIELD,
                  anchor="middle", bold=True))

    p.append(fitbox(56, 476, 948, 44,
                    "Відповідь — 2³² — влазить у int64 із запасом у два мільярди разів. "
                    "Переповнюється не відповідь, а дорога до неї.",
                    size=13.5, fill=FILL, stroke=MUTED, sw=1.8))

    return render(os.path.join(OUT, "lcmtrap.svg"), W, H, *p)


# ── bezout-set: що взагалі можна зібрати з a і b ─────────────────────────────
# Ідея (вставка math-bezout): множина всіх комбінацій a·x + b·y — це РІВНО
# кратні НСД. Дрібнішого кроку не буває, тож найменший додатний елемент і є d.
def fig_bezout_set():
    W, H = 1060, 580
    p = []

    lo, hi = -4, 12
    x0, step = 90, 54
    yL = 196

    def X(v):
        return x0 + (v - lo) * step

    p.append(text(W / 2, 52, "Що можна зібрати з a = 6 і b = 4 самими цілими кроками вперед і назад",
                  size=16, color=INK, bold=True))

    p.append(line(X(lo) - 26, yL, X(hi) + 26, yL, color=MUTED, sw=1.4))

    for v in range(lo, hi + 1):
        reach = (v % 2 == 0)
        if v == 2:                                    # найменше додатне — воно ж d
            p.append(circle(X(v), yL, 11, fill=GREEN_F, stroke=FIELD, sw=3))
        elif reach:
            p.append(circle(X(v), yL, 9, fill=GREEN_F, stroke=FIELD, sw=2))
        else:
            p.append(circle(X(v), yL, 7, fill=BG, stroke=MUTED, sw=1.5))
        p.append(text(X(v), yL + 34, str(v), size=12.5,
                      color=(INK if reach else MUTED), bold=reach))

    # приклади-комбінації — рознесені так, щоб підписи не сходилися
    for v, lab in ((-4, "6·0 + 4·(−1) = −4"), (2, "6·1 + 4·(−1) = 2"), (10, "6·1 + 4·1 = 10")):
        p.append(text(X(v), 112, lab, size=13, color=INK))
        p.append(arrow(X(v), 126, X(v), yL - 22, color=MUTED, sw=1.5))

    p.append(text(X(2), 186, "найменше додатне", size=11.5, color=FIELD, italic=True, bold=True))

    p.append(text(W / 2, yL + 66,
                  "Зелене — досяжне (усі парні). Порожнє — недосяжне: непарного з двох парних кроків не скласти.",
                  size=13, color=MUTED, italic=True))

    p.append(text(W / 2, 276,
                  "Основа: сума й різниця двох комбінацій — знову комбінація тих самих a і b. Множина S замкнена.",
                  size=13, color=NEG, bold=True))

    bw, bh, by = 300, 126, 296
    cols = [
        (50, "Крок 1 · усе в S кратне d",
         "d — найменший додатний елемент.\nБеремо t ∈ S, ділимо: r = t − q·d.\nЦе теж елемент S, але 0 ≤ r < d.\nМеншого додатного нема → r = 0."),
        (380, "Крок 2 · d — спільний дільник",
         "Самі a = a·1 + b·0 та b = a·0 + b·1\nлежать у S. За кроком 1 d ділить\nкожен елемент S — отже, ділить\nі a, і b."),
        (710, "Крок 3 · d — найбільший",
         "Спільний дільник c ділить кожну\nкомбінацію a·x + b·y, а значить,\nі сам d. Дільник не більший за те,\nщо ділить: c ≤ d."),
    ]
    for bx, head, body in cols:
        p.append(rect(bx, by, bw, bh, fill=FILL, stroke=NEG, sw=2))
        p.append(text(bx + bw / 2, by + 26, head, size=13.5, color=NEG, bold=True))
        p.append(mtext(bx + bw / 2, by + 54, body.split("\n"), size=12, color=INK, lh=1.45))

    p.append(fitbox(180, 460, 700, 60,
                    "S = { a·x + b·y } = кратні НСД(a, b)",
                    size=21, fill=GREEN_F, stroke=FIELD, sw=2.5, bold=True, color=INK))
    p.append(text(W / 2, 548,
                  "Звідси одразу: НСД подається як a·x + b·y, а рівняння a·x + b·y = c розв'язне ⟺ НСД ділить c.",
                  size=13, color=INK))

    return render(os.path.join(OUT, "bezout-set.svg"), W, H, *p)


# ── bezout-passes: дорога назад проти дороги вниз ────────────────────────────
# Ідея: та сама відповідь (−3, 7), але вниз — одним проходом і з памʼяттю на
# два рядки; назад — треба зберегти ВЕСЬ ланцюг і пройти його вдруге.
def fig_bezout_passes():
    W, H = 1120, 650
    p = []

    xL = 60
    p.append(rect(xL, 76, 470, 476, fill=BG, stroke=POS, sw=2))
    p.append(text(xL + 235, 106, "Дорогою назад — два проходи", size=15.5, color=POS, bold=True))

    y = 150
    for ln in ["1071 = 2 · 462 + 147", " 462 = 3 · 147 +  21", " 147 = 7 ·  21 +   0"]:
        p.append(text(xL + 28, y, ln, size=14, color=INK, anchor="start"))
        y += 30
    p.append(text(xL + 28, y + 8, "усі рядки треба зберегти", size=11.5, color=MUTED,
                  anchor="start", italic=True))

    p.append(arrow(xL + 408, 272, xL + 408, 162, color=POS, sw=2.2))
    p.append(text(xL + 424, 218, "прохід 2", size=12, color=POS, anchor="start", bold=True))

    y = 326
    for ln in ["21 = 462 − 3 · 147",
               "   = 462 − 3 · (1071 − 2 · 462)",
               "   = 1071 · (−3) + 462 · 7"]:
        p.append(text(xL + 28, y, ln, size=13.5, color=INK, anchor="start"))
        y += 30
    p.append(mtext(xL + 235, 442,
                   ["Підстановка розкриває дужки знизу вгору.",
                    "Памʼять — увесь ланцюг часток: для чисел на",
                    "тисячу двійкових розрядів це близько півтори",
                    "тисячі рядків, потрібних аж наприкінці."],
                   size=12, color=MUTED, lh=1.5))

    xR = 590
    p.append(rect(xR, 76, 470, 476, fill=BG, stroke=FIELD, sw=2))
    p.append(text(xR + 235, 106, "Дорогою вниз — один прохід", size=15.5, color=FIELD, bold=True))

    cols = [("k", 42), ("r", 132), ("x", 226), ("y", 310), ("q", 396)]
    for h, dx in cols:
        p.append(text(xR + dx, 148, h, size=13.5, color=MUTED, bold=True))
    p.append(line(xR + 24, 158, xR + 424, 158, color=MUTED, sw=1.2))

    tab = [("0", "1071", "1", "0", "2"),
           ("1", "462", "0", "1", "3"),
           ("2", "147", "1", "−2", "7"),
           ("3", "21", "−3", "7", "—"),
           ("4", "0", "22", "−51", "")]
    y = 190
    for row in tab:
        hit = (row[0] == "3")
        if hit:
            p.append(rect(xR + 24, y - 19, 400, 30, fill=GREEN_F, stroke=FIELD, sw=1.6, rx=4))
        for (h, dx), val in zip(cols, row):
            p.append(text(xR + dx, y, val, size=13.5,
                          color=(FIELD if hit else INK), bold=hit))
        y += 40
    p.append(text(xR + 235, y + 8, "останній ненульовий r — це НСД, а x, y поруч — готові коефіцієнти",
                  size=11.5, color=MUTED, italic=True))

    p.append(arrow(xR + 442, 180, xR + 442, 356, color=FIELD, sw=2.2))

    p.append(mtext(xR + 235, 442,
                   ["Три стовпці — r, x, y — крутять ОДНЕ Й ТЕ САМЕ правило",
                    "«новий = позаминулий − q · минулий». Різні лише зачини.",
                    "Памʼять — два рядки, скільки б кроків не було."],
                   size=12, color=MUTED, lh=1.5))

    p.append(fitbox(160, 574, 800, 56,
                    "Та сама відповідь: 21 = 1071 · (−3) + 462 · 7 — але здобута дорогою вниз",
                    size=16, fill=FILL, stroke=NEG, sw=2, bold=True))

    return render(os.path.join(OUT, "bezout-passes.svg"), W, H, *p)


# ── bezout-modinv: обернене за модулем на колі лишків ────────────────────────
# Ідея: крокуючи по a за модулем m, попадемо в 1 тоді й лише тоді, коли
# НСД(a, m) = 1. Кількість кроків — це x, кількість повних обертів — це −y.
def fig_bezout_modinv():
    import math

    W, H = 1080, 610
    p = []

    def ring(cx, cy, R, m, path, good, head, sub, col):
        out = [text(cx, cy - R - 76, head, size=15.5, color=col, bold=True),
               text(cx, cy - R - 54, sub, size=12.5, color=MUTED, italic=True),
               circle(cx, cy, R, fill=BG, stroke=MUTED, sw=1.4)]

        def pt(i):
            ang = -math.pi / 2 + 2 * math.pi * i / m
            return cx + R * math.cos(ang), cy + R * math.sin(ang)

        for i in range(len(path) - 1):
            x1, y1 = pt(path[i])
            x2, y2 = pt(path[i + 1])
            dx, dy = x2 - x1, y2 - y1
            L = math.hypot(dx, dy) or 1.0
            k = 20.0 / L
            out.append(arrow(x1 + dx * k, y1 + dy * k, x2 - dx * k, y2 - dy * k, color=col, sw=2))

        for i in range(m):
            x, y = pt(i)
            if i == 1:
                fill, st, sw = ((GREEN_F, FIELD, 3) if good else (RED_F, POS, 3))
            elif i in path:
                fill, st, sw = (BLUE_F, NEG, 2)
            else:
                fill, st, sw = (BG, MUTED, 1.4)
            out.append(circle(x, y, 15, fill=fill, stroke=st, sw=sw))
            out.append(text(x, y + 5, str(i), size=13, color=INK, bold=(i in path or i == 1)))
        return "".join(out)

    p.append(ring(272, 294, 132, 10, [0, 7, 4, 1], True,
                  "НСД(7, 10) = 1 — крок 7 попадає в 1",
                  "0 → 7 → 4 → 1: три кроки по 7 і два повні оберти", NEG))
    p.append(mtext(272, 480,
                   ["7 · 3 = 21 = 2 · 10 + 1   →   7 · 3 + 10 · (−2) = 1",
                    "За модулем 10 оберти зникають: 7 · 3 ≡ 1 (mod 10).",
                    "Отже обернене до 7 за модулем 10 — це 3."],
                   size=13, color=INK, lh=1.55))

    p.append(ring(808, 294, 132, 9, [0, 6, 3, 0], False,
                  "НСД(6, 9) = 3 — в 1 не попасти ніколи",
                  "0 → 6 → 3 → 0: коло замкнулося, оминувши 1", POS))
    p.append(mtext(808, 480,
                   ["Крок 6 і модуль 9 обидва кратні 3, тож і 6·x + 9·y кратне 3.",
                    "Одиниця на 3 не ділиться — такої комбінації не буває.",
                    "Обернене існує ⟺ НСД(a, m) = 1. Без винятків."],
                   size=13, color=INK, lh=1.55))

    p.append(line(540, 108, 540, 530, color=MUTED, sw=1.2, dash="6,5"))

    return render(os.path.join(OUT, "bezout-modinv.svg"), W, H, *p)


# ── anthyphairesis: дві долі однієї процедури ────────────────────────────────
# Ідея: греки ганяли взаємне віднімання не заради НСД, а заради питання
# «спиниться чи ні». Спинилося → величини сумірні, останній залишок і є міра.
# Не спиниться → спільної міри НЕ ІСНУЄ. НСД — приз за відповідь «спиниться».
def fig_anthyphairesis():
    W, H = 1100, 700
    p = []

    def column(x, head, rows, col, fill):
        out = [text(x, 78, head, size=15.5, color=col, anchor="start", bold=True)]
        y = 104
        for r in rows:
            out.append(fitbox(x, y, 420, 48, r, size=16, fill=fill, stroke=col, sw=1.8))
            y += 60
        return "".join(out), y

    left, yl = column(
        60, "21 і 15 — процедура спиняється",
        ["21 = 1 · 15 + 6", "15 = 2 · 6 + 3", "6 = 2 · 3 + 0   ← залишку немає"],
        NEG, BLUE_F)
    p.append(left)
    p.append(fitbox(60, yl + 24, 420, 74,
                    "СУМІРНІ\nспільна міра є, і вона = 3",
                    size=16, fill=GREEN_F, stroke=FIELD, sw=2.5, bold=True, color=INK))

    right, yr = column(
        620, "сторона a й діагональ d квадрата — не спиняється",
        ["d = 1 · a + r₁", "a = 2 · r₁ + r₂", "r₁ = 2 · r₂ + r₃",
         "r₂ = 2 · r₃ + r₄", "…  далі 2, 2, 2 …  без кінця"],
        POS, RED_F)
    p.append(right)
    p.append(fitbox(620, yr + 24, 420, 74,
                    "НЕСУМІРНІ\nспільної міри не існує ЗОВСІМ",
                    size=16, fill=RED_F, stroke=POS, sw=2.5, bold=True, color=INK))

    p.append(fitbox(60, 506, 980, 68,
                    "a : r₁  =  r₁ : r₂  =  r₂ : r₃  =  √2 + 1 ≈ 2.414  —  на кожному щаблі та сама картина, лише менша.\n"
                    "Самоподібність не дає процедурі спинитися: частки 1, 2, 2, 2, … тягнуться в нескінченність.",
                    size=14, fill=FILL, stroke=MUTED, sw=1.8))

    p.append(fitbox(60, 596, 980, 68,
                    "Греки ганяли цю процедуру не заради НСД, а заради питання «спиниться чи ні».\n"
                    "НСД — приз, який дістається тоді, коли відповідь «спиниться».",
                    size=14.5, fill=BLUE_F, stroke=NEG, sw=2))

    return render(os.path.join(OUT, "anthyphairesis.svg"), W, H, *p,
                  title="Та сама процедура — дві долі")


# ── deng: правило «Дев'яти розділів» і його двозначність ─────────────────────
# Ідея: китайський текст спиняється не на нулі, а на РІВНОСТІ, і кличе НСД
# «рівним». А фраза «можна — поділи навпіл» читається двояко — звідси й уся
# суперечка про те, чи це вже двійковий НСД.
def fig_deng():
    W, H = 1120, 640
    p = []

    p.append(text(60, 78, "Правило: скоротити дріб, не знаючи дільників",
                  size=15.5, color=INK, anchor="start", bold=True))
    steps = [
        ("1", "Якщо ОБИДВА можна поділити навпіл — ділимо"),
        ("2", "Далі: від більшого віднімаємо менше"),
        ("3", "Повторюємо, доки числа не ЗРІВНЯЮТЬСЯ"),
        ("4", "Це число — «рівне» (děng). Ділимо на нього"),
    ]
    y = 106
    for n, s in steps:
        p.append(circle(80, y + 24, 15, fill=BLUE_F, stroke=NEG, sw=2))
        p.append(text(80, y + 29, n, size=14, color=NEG, bold=True))
        p.append(fitbox(108, y, 380, 48, s, size=13.5, fill=FILL, stroke=NEG, sw=1.6))
        y += 62

    p.append(text(620, 78, "12/18 — крок за кроком", size=15.5,
                  color=INK, anchor="start", bold=True))
    trace = [
        ("12 і 18 — обидва парні → 6 і 9", NEG, BLUE_F),
        ("9 − 6 = 3      → пара (6, 3)", POS, RED_F),
        ("6 − 3 = 3      → пара (3, 3)  зрівнялися", POS, RED_F),
        ("«рівне» = 3", FIELD, GREEN_F),
        ("6 / 3 = 2,   9 / 3 = 3   →   2/3", FIELD, GREEN_F),
    ]
    y = 106
    for s, col, fill in trace:
        p.append(fitbox(620, y, 440, 48, s, size=14, fill=fill, stroke=col, sw=1.8))
        y += 62

    p.append(text(620, y + 8, "спиняє не нуль, а рівність — так природно, коли лише віднімаєш",
                  size=11.5, color=MUTED, anchor="start", italic=True))

    p.append(fitbox(60, 502, 1000, 96,
                    "«Якщо можна — поділи навпіл»: половинити ОБИДВА (тоді це Евклід зі скороченням)\n"
                    "чи ТЕ З НИХ, що парне (тоді це двійковий НСД, перевідкритий 1967-го)?\n"
                    "Текст не уточнює — і на цій одній фразі тримається вся суперечка.",
                    size=14.5, fill=FILL, stroke=POS, sw=2.2))

    return render(os.path.join(OUT, "deng.svg"), W, H, *p,
                  title="«Дев'ять розділів»: взаємне віднімання й «рівне» число")


# ── attribution: хто зробив ↔ чиє ім'я ───────────────────────────────────────
# Ідея: обидва епоніми в цій історії показують той самий механізм — ім'я
# чіпляється не до першого, хто знайшов, а до каналу, через який знайшли всі.
def fig_attribution():
    W, H = 1160, 660
    p = []

    def row(y, label, nodes, note, x0, bw, gap):
        out = [text(40, y, label, size=15.5, color=INK, anchor="start", bold=True)]
        x = x0
        for i, (txt, hot) in enumerate(nodes):
            col, fill = (POS, RED_F) if hot else (NEG, BLUE_F)
            out.append(fitbox(x, y + 18, bw, 92, txt, size=13, fill=fill,
                              stroke=col, sw=2.4 if hot else 1.6))
            if i < len(nodes) - 1:
                out.append(arrow(x + bw + 5, y + 64, x + bw + gap - 5, y + 64, color=MUTED))
            x += bw + gap
        out.append(text(40, y + 138, note, size=13, color=MUTED, anchor="start", italic=True))
        return "".join(out)

    p.append(row(70, "«Тотожність Безу» — про ЦІЛІ числа",
                 [("Евклід\n~300 до н. е.\nіснування", False),
                  ("Баше\n1624\nусі розв'язки", False),
                  ("Безу\n1779\nдля МНОГОЧЛЕНІВ", True),
                  ("Бурбакі\n1949\nприліпив ім'я", False)],
                 "Ім'я — на тому, хто розв'язував ІНШУ задачу. Цілочисельний випадок зробили Евклід і Баше.",
                 70, 200, 60))

    p.append(row(280, "«Теорема Ламе» — межа на кількість кроків",
                 [("Рейно\n1811\nслабка межа", False),
                  ("Леже\n1837\nрезультат знав", False),
                  ("Фінк\n1841\nповне доведення", False),
                  ("Ламе\n1844\nім'я тут", True),
                  ("Шаллі\n1994\nрозкопав правду", False)],
                 "Ім'я — на четвертому. Перших трьох забули на півтора століття.",
                 38, 182, 36))

    p.append(fitbox(70, 470, 1020, 76,
                    "Закон Стіглера (1980): жодне наукове відкриття не назване іменем свого відкривача.\n"
                    "Стіглер приписав цей закон Мертонові — щоб закон справдився й на самому собі.",
                    size=14.5, fill=GREEN_F, stroke=FIELD, sw=2))

    p.append(fitbox(70, 566, 1020, 62,
                    "Механізм той самий двічі: ім'я чіпляється не до того, хто знайшов ПЕРШИМ,\n"
                    "а до того, через кого про це дізналися ВСІ РЕШТА.",
                    size=14, fill=FILL, stroke=MUTED, sw=1.8))

    return render(os.path.join(OUT, "attribution.svg"), W, H, *p,
                  title="Хто зробив — і чиє ім'я")


for f in (fig_invariant, fig_tiling, fig_speed, fig_binrules, fig_bintrace, fig_lcmtrap,
          fig_bezout_set, fig_bezout_passes, fig_bezout_modinv,
          fig_anthyphairesis, fig_deng, fig_attribution):
    print("написано:", f())
