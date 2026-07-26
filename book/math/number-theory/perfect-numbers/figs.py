# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLUE_F  = "#e8eefc"
RED_F   = "#fdecea"
GREEN_F = "#e6f7ee"


# ── trichotomy: три долі числа за сумою власних дільників ─────────────────────
# Ідея: майже кожне число промахується — сума частин недобирає або переростає.
# Досконале стоїть точно на межі. Три панелі показують усі три випадки поряд.
def fig_trichotomy():
    W, H = 1020, 430
    p = []

    def panel(cx, head, col, fill, divs, total, num, verdict, vcol):
        out = [text(cx, 92, head, size=17, color=col, bold=True)]
        # плитки-дільники
        tw = 44
        n = len(divs)
        x0 = cx - n * tw / 2
        for i, d in enumerate(divs):
            out.append(rect(x0 + i * tw, 116, tw - 8, 40, fill=fill, stroke=col, sw=1.8, rx=4))
            out.append(text(x0 + i * tw + (tw - 8) / 2, 141, str(d), size=15, color=col, bold=True))
        # сума
        expr = " + ".join(str(d) for d in divs)
        out.append(text(cx, 196, expr + " = " + str(total), size=15, color=INK))
        # вирок
        out.append(fitbox(cx - 150, 226, 300, 52, verdict, size=17,
                          fill=fill, stroke=vcol, sw=2.4, bold=True, color=INK))
        return "".join(out)

    p.append(panel(180, "8 — недостатнє", NEG, BLUE_F, [1, 2, 4], 7,
                   8, "7 < 8", NEG))
    p.append(panel(510, "6 — досконале", FIELD, GREEN_F, [1, 2, 3], 6,
                   6, "6 = 6", FIELD))
    p.append(panel(840, "12 — надлишкове", POS, RED_F, [1, 2, 3, 4, 6], 16,
                   12, "16 > 12", POS))

    # роздільники між панелями
    p.append(line(345, 84, 345, 290, color=MUTED, sw=1.2, dash="5,5"))
    p.append(line(675, 84, 675, 290, color=MUTED, sw=1.2, dash="5,5"))

    p.append(text(W / 2, 328, "власні дільники (усі, крім самого числа) складають…",
                  size=13, color=MUTED, italic=True))
    p.append(fitbox(260, 350, 500, 46,
                    "досконале ⟺ сума власних дільників = самому числу",
                    size=16, fill=FILL, stroke=FIELD, sw=2, bold=True))

    return render(os.path.join(OUT, "trichotomy.svg"), W, H, *p,
                  title="Три долі числа: недобір, точний збіг, надлишок")


# ── euclid-bridge: p → число Мерсенна → досконале ────────────────────────────
# Ідея: досконале виникає лише тоді, коли 2^p − 1 просте. Таблиця показує
# робочі рядки й обрив на p = 11, де 2^p − 1 виявляється складеним.
def fig_euclid_bridge():
    W, H = 1040, 540
    p = []

    cols = [("p", 60, 84), ("2ᵖ − 1  (Мерсенн)", 168, 210),
            ("просте?", 396, 150), ("× 2^(p−1)", 560, 150),
            ("досконале n", 728, 288)]
    # заголовки
    for name, x, w in cols:
        p.append(text(x + w / 2, 104, name, size=14.5, color=INK, bold=True))
    p.append(line(52, 118, 1024, 118, color=MUTED, sw=1.4))

    rows = [
        ("2",  "2² − 1 = 3",       True,  "× 2",  "6"),
        ("3",  "2³ − 1 = 7",       True,  "× 4",  "28"),
        ("5",  "2⁵ − 1 = 31",      True,  "× 16", "496"),
        ("7",  "2⁷ − 1 = 127",     True,  "× 64", "8128"),
        ("11", "2¹¹ − 1 = 2047",   False, "—",    "2047 = 23·89 → немає"),
    ]
    y = 138
    rh = 66
    for pp, mers, ok, fac, perf in rows:
        col, fill = (FIELD, GREEN_F) if ok else (POS, RED_F)
        # p
        p.append(fitbox(60, y, 84, 50, pp, size=17, fill=BLUE_F, stroke=NEG, sw=1.8, bold=True))
        # мерсенн
        p.append(fitbox(168, y, 210, 50, mers, size=15, fill=fill, stroke=col, sw=1.8))
        # просте?
        p.append(fitbox(396, y, 150, 50, "просте ✓" if ok else "складене ✗",
                        size=14, fill=fill, stroke=col, sw=1.8, bold=True, color=INK))
        # множник
        p.append(fitbox(560, y, 150, 50, fac, size=15, fill=fill, stroke=col, sw=1.6))
        # досконале
        p.append(fitbox(728, y, 288, 50, perf, size=15 if ok else 13.5,
                        fill=fill, stroke=col, sw=2.2 if ok else 1.8,
                        bold=ok, color=INK))
        y += rh

    p.append(fitbox(60, y + 8, 956, 46,
                    "Просте p потрібне, але не досить: при p = 11 число Мерсенна складене — і досконалого немає.",
                    size=14, fill=FILL, stroke=MUTED, sw=1.8))

    return render(os.path.join(OUT, "euclid-bridge.svg"), W, H, *p,
                  title="Місток Евкліда: досконале число живе лише за простого 2ᵖ − 1")


# ── triangular: 28 як трикутне число ─────────────────────────────────────────
# Ідея: 2^(p−1)(2^p − 1) = (2^p−1)·2^p/2 — це трикутне число зі стороною 2^p−1.
# Малюємо 28 як трикутник із рядків 1..7 кульок.
def fig_triangular():
    W, H = 780, 520
    p = []

    cx = 250
    r = 12
    dx = 34
    y0 = 96
    dy = 44
    for i in range(1, 8):                 # рядки з 1..7 кульок
        rowy = y0 + (i - 1) * dy
        startx = cx - (i - 1) * dx / 2
        for j in range(i):
            p.append(circle(startx + j * dx, rowy, r, fill=GREEN_F, stroke=FIELD, sw=1.8))
        # підпис рядка й накопичена сума — праворуч від трикутника, поза кульками
        run = i * (i + 1) // 2
        p.append(text(cx + 4 * dx, rowy + 5, "%d  (разом %d)" % (i, run),
                      size=12.5, color=MUTED, anchor="start"))

    # права колонка — арифметика
    xR = 500
    p.append(text(xR, 120, "1+2+3+4+5+6+7", size=18, color=INK, anchor="start", bold=True))
    p.append(text(xR, 150, "= 28", size=18, color=FIELD, anchor="start", bold=True))
    p.append(line(xR, 172, xR + 232, 172, color=MUTED, sw=1.2))
    p.append(mtext(xR, 206,
                   ["трикутне число зі стороною 7:", "T₇ = 7·8 / 2 = 28"],
                   size=14, color=INK, anchor="start", lh=1.5))
    p.append(mtext(xR, 270,
                   ["а сторона 7 = 2³ − 1,", "множник 4 = 2³⁻¹ —", "рівно Евклідова форма:"],
                   size=14, color=INK, anchor="start", lh=1.5))
    p.append(fitbox(xR - 4, 348, 250, 50, "28 = 2² · (2³ − 1)",
                    size=17, fill=GREEN_F, stroke=FIELD, sw=2.2, bold=True))
    p.append(text(xR + 120, 428, "(2ᵖ−1)·2ᵖ / 2 = 2^(p−1)(2ᵖ−1)",
                  size=13, color=MUTED, italic=True))

    return render(os.path.join(OUT, "triangular.svg"), W, H, *p,
                  title="Кожне парне досконале число — трикутне")


# ── binary: візерунок p одиниць і p−1 нулів ──────────────────────────────────
# Ідея: 2^(p−1)(2^p − 1) у двійці — це p одиниць (бо 2^p−1) і p−1 нулів (зсув).
def fig_binary():
    W, H = 1000, 492
    p = []

    cw = 30                                # ширина клітинки біта
    x0 = 210
    rows = [
        ("6",    2, 1),                    # (число, кількість одиниць p, нулів p−1)
        ("28",   3, 2),
        ("496",  5, 4),
        ("8128", 7, 6),
    ]
    y = 104
    rh = 74
    for num, ones, zeros in rows:
        p.append(text(x0 - 26, y + 22, num, size=16, color=INK, anchor="end", bold=True))
        for j in range(ones):
            xx = x0 + j * cw
            p.append(rect(xx, y, cw - 4, 34, fill=GREEN_F, stroke=FIELD, sw=1.8, rx=3))
            p.append(text(xx + (cw - 4) / 2, y + 23, "1", size=14, color=FIELD, bold=True))
        for j in range(zeros):
            xx = x0 + (ones + j) * cw
            p.append(rect(xx, y, cw - 4, 34, fill=BG, stroke=MUTED, sw=1.4, rx=3))
            p.append(text(xx + (cw - 4) / 2, y + 23, "0", size=14, color=MUTED))
        # p підпис
        p.append(text(x0 + (ones + zeros) * cw + 16, y + 22,
                      "p = %d" % ones, size=13, color=MUTED, anchor="start"))
        y += rh

    # підкреслення блоків ПІД нижнім рядком (8128: 7 одиниць, 6 нулів)
    yb = 104 + 3 * rh + 34 + 14           # трохи нижче нижнього рядка
    ax = x0
    bx = x0 + 7 * cw
    ex = x0 + 13 * cw
    p.append(line(ax, yb, bx - 4, yb, color=FIELD, sw=2))
    p.append(text((ax + bx) / 2, yb + 18, "p одиниць  (2ᵖ − 1)", size=12.5, color=FIELD, bold=True))
    p.append(line(bx, yb, ex - 4, yb, color=MUTED, sw=2))
    p.append(text((bx + ex) / 2, yb + 18, "p − 1 нулів  (× 2^(p−1))", size=12.5, color=MUTED, bold=True))

    p.append(fitbox(150, 424, 700, 46,
                    "Блок одиниць, за ним блок нулів — форму Евкліда видно з першого погляду.",
                    size=14, fill=FILL, stroke=NEG, sw=1.8))

    return render(os.path.join(OUT, "binary.svg"), W, H, *p,
                  title="Досконалі числа у двійковому запису")


# ── mersenne-fold: зведення за модулем 2ᵖ−1 самими зсувами ────────────────────
# Ідея: 2ᵖ ≡ 1 (mod 2ᵖ−1), тож старші біти числа «падають» на молодші й просто
# додаються. Приклад: 676 mod 31 (p=5). 676 = 1010100100₂: старші 5 бітів = 21,
# молодші 5 = 4; 21 + 4 = 25 = 676 mod 31 — без жодного ділення.
def fig_mersenne_fold():
    W, H = 960, 486
    p = []

    p.append(text(W / 2, 56,
                  "Звести великий добуток за модулем Mₚ = 2ᵖ − 1 — без ділення "
                  "(приклад: 676 mod 31, p = 5)",
                  size=14.5, color=MUTED, italic=True))

    bits = [1, 0, 1, 0, 1, 0, 0, 1, 0, 0]      # 676 = 1010100100₂ (bit9…bit0)
    cw, x0, yb, ch = 46, 250, 96, 40
    p.append(text(x0 - 18, yb + 26, "676 =", size=15, color=INK, anchor="end", bold=True))
    for i, b in enumerate(bits):
        xx = x0 + i * cw
        hi = i < 5                              # ліві 5 клітинок — старша частина
        fill, col = (RED_F, POS) if hi else (GREEN_F, FIELD)
        p.append(text(xx + (cw - 6) / 2, yb - 8, str(9 - i), size=10, color=MUTED))
        p.append(rect(xx, yb, cw - 6, ch, fill=fill, stroke=col, sw=1.8, rx=3))
        p.append(text(xx + (cw - 6) / 2, yb + 26, str(b), size=15, color=col, bold=True))

    xsplit = x0 + 5 * cw - 3                     # межа між bit5 і bit4
    p.append(line(xsplit, yb - 16, xsplit, yb + ch + 40, color=POS, sw=1.6, dash="5,4"))

    p.append(fitbox(x0, 150, 5 * cw - 12, 44, "старші 5 бітів = 10101₂ = 21",
                    size=13.5, fill=RED_F, stroke=POS, sw=1.8, bold=True))
    p.append(fitbox(x0 + 5 * cw + 10, 150, 5 * cw - 12, 44, "молодші 5 бітів = 00100₂ = 4",
                    size=13.5, fill=GREEN_F, stroke=FIELD, sw=1.8, bold=True))

    p.append(text(W / 2, 232,
                  "2⁵ = 32 ≡ 1 (mod 31)   ⟹   старша частина «падає» на молодшу й додається:",
                  size=14.5, color=INK))

    # згортання: 21 + 4 = 25
    p.append(fitbox(360, 260, 76, 50, "21", size=19, fill=RED_F, stroke=POS, sw=2, bold=True))
    p.append(text(462, 292, "+", size=24, color=INK, bold=True))
    p.append(fitbox(482, 260, 60, 50, "4", size=19, fill=GREEN_F, stroke=FIELD, sw=2, bold=True))
    p.append(text(566, 293, "=", size=22, color=INK, bold=True))
    p.append(fitbox(588, 260, 92, 50, "25", size=19, fill=FILL, stroke=FIELD, sw=2.6, bold=True))
    p.append(text(W / 2, 336, "25 < 31 → зупиняємось", size=13, color=MUTED, italic=True))

    p.append(fitbox(230, 360, 500, 48,
                    "676 mod 31 = 25 — самим зсувом і додаванням, без ділення",
                    size=15, fill=FILL, stroke=NEG, sw=1.9, bold=True))
    p.append(text(W / 2, 446,
                  "Єдиний окремий випадок: якщо після згортання лишиться рівно 2ᵖ − 1 — це той самий 0.",
                  size=12.5, color=MUTED, italic=True))

    return render(os.path.join(OUT, "mersenne-fold.svg"), W, H, *p,
                  title="Форма Мерсенна робить зведення за модулем безкоштовним")


# ── hunt-pipeline: як сьогодні шукають просте Мерсенна (= досконале число) ────
# Ідея: справжній конвеєр GIMPS — простий показник → пробне ділення → Люка-Лемера/
# PRP через ШПФ → перевірка Гербіца → незалежне підтвердження. Дорогі кроки — на GPU.
def fig_hunt_pipeline():
    W, H = 960, 616
    p = []

    bx, bw, bh = 150, 380, 58
    tops = [64, 152, 240, 328, 416, 504]
    cx = bx + bw / 2

    stages = [
        ("1 · Обрати простий показник p", BLUE_F, NEG, 1.8, False),
        ("2 · Пробне ділення", FILL, INK, 1.6, False),
        ("3 · Тест Люка–Лемера / PRP: p − 2 піднесень квадрата mod Mₚ", GREEN_F, FIELD, 2.4, True),
        ("4 · Перевірка Гербіца під час рахунку", FILL, INK, 1.6, False),
        ("5 · Незалежна повторна перевірка", FILL, INK, 1.6, False),
        ("Нове просте Мерсенна  ⇒  нове досконале число", GREEN_F, FIELD, 2.6, True),
    ]
    notes = [
        ("p мусить бути простим — інакше 2ᵖ − 1 складене", FILL, MUTED, False),
        ("GPU · відсіює p, де 2ᵖ − 1 має малий дільник", RED_F, POS, True),
        ("GPU · кожне піднесення — одне ШПФ", RED_F, POS, True),
        ("ловить апаратний збій просто на льоту", FILL, MUTED, False),
        ("інше залізо й софт мусять підтвердити", FILL, MUTED, False),
        (None, None, None, False),
    ]

    for i, (txt, fill, col, sw, bold) in enumerate(stages):
        t = tops[i]
        p.append(fitbox(bx, t, bw, bh, txt, size=14.5, fill=fill, stroke=col, sw=sw, bold=bold))
        if i < len(stages) - 1:
            p.append(arrow(cx, t + bh, cx, tops[i + 1], color=MUTED, sw=1.8))
        ntxt, nfill, ncol, nbold = notes[i]
        if ntxt:
            p.append(line(bx + bw, t + bh / 2, bx + bw + 26, t + bh / 2,
                          color=MUTED, sw=1.3, dash="4,3"))
            p.append(fitbox(bx + bw + 30, t + bh / 2 - 21, 348, 42, ntxt,
                            size=12.5, fill=nfill, stroke=ncol, sw=1.5, bold=nbold, color=INK))

    return render(os.path.join(OUT, "hunt-pipeline.svg"), W, H, *p,
                  title="Сучасне полювання на досконале число (конвеєр GIMPS)")


# ── broken-laws: два «закони» Нікомаха, спростовані 5-м і 6-м числами ─────────
# Ідея (історична вставка): з перших чотирьох чисел Нікомах вивів дві
# «закономірності» — по одному числу на кожну довжину й кінцівки 6,8,6,8. Обидві
# живі, доки не порахуєш 5-те (33 550 336) і 6-те число, які їх убивають.
def fig_broken_laws():
    W, H = 1040, 560
    p = []

    p.append(text(W / 2, 50,
                  "Нікомах вивів два закони з перших чотирьох чисел — "
                  "п'яте й шосте їх спростували.",
                  size=13.5, color=MUTED, italic=True))

    # стовпці таблиці
    x_no,  w_no  = 60,  44
    x_num, w_num = 112, 252
    x_dig, w_dig = 376, 78
    x_end, w_end = 464, 96
    heads = [(x_no, w_no, "№"), (x_num, w_num, "досконале число"),
             (x_dig, w_dig, "цифр"), (x_end, w_end, "остання")]
    for x, w, name in heads:
        p.append(text(x + w / 2, 96, name, size=14, color=INK, bold=True))
    p.append(line(52, 108, x_end + w_end, 108, color=MUTED, sw=1.4))

    # (№, число, цифр, остання, ламає-закон-I(цифр), ламає-закон-II(остання))
    rows = [
        ("1", "6",               "1",  "6", False, False),
        ("2", "28",              "2",  "8", False, False),
        ("3", "496",             "3",  "6", False, False),
        ("4", "8128",            "4",  "8", False, False),
        ("5", "33 550 336",      "8",  "6", True,  True),
        ("6", "8 589 869 056",   "10", "6", False, True),
        ("7", "137 438 691 328", "12", "8", False, False),
    ]
    y0, rh = 120, 52
    for i, (no, num, dig, end, bd, be) in enumerate(rows):
        top = y0 + i * rh
        cy = top + rh / 2
        p.append(text(x_no + w_no / 2, cy + 5, no, size=13, color=MUTED, bold=True))
        p.append(fitbox(x_num, top + 6, w_num, rh - 12, num, size=15,
                        fill=GREEN_F, stroke=FIELD, sw=1.6, bold=True))
        dc, df = (POS, RED_F) if bd else (FIELD, GREEN_F)
        p.append(fitbox(x_dig, top + 6, w_dig, rh - 12, dig, size=15,
                        fill=df, stroke=dc, sw=2.4 if bd else 1.6, bold=True, color=INK))
        ec, ef = (POS, RED_F) if be else (FIELD, GREEN_F)
        p.append(fitbox(x_end, top + 6, w_end, rh - 12, end, size=15,
                        fill=ef, stroke=ec, sw=2.4 if be else 1.6, bold=True, color=INK))

    # роздільник: чотири античні числа / знайдені в Європі значно пізніше
    yd = y0 + 4 * rh
    p.append(line(52, yd, x_end + w_end, yd, color=INK, sw=1.6, dash="6,4"))

    # праворуч — два закони й де саме вони вмерли (червоні клітинки вище)
    cxL = 588
    p.append(fitbox(cxL, 150, 430, 96,
                    "Закон I: по одному числу на\nкожну довжину — 1, 2, 3, 4 цифри.\n"
                    "✗ Наступне має 8 цифр:\nна 5, 6 і 7 цифр — жодного.",
                    size=13.5, fill=RED_F, stroke=POS, sw=2, color=INK))
    p.append(fitbox(cxL, 296, 430, 96,
                    "Закон II: кінцівки чергуються\n6, 8, 6, 8, …\n"
                    "✗ П'яте й шосте — обидва\nзакінчуються на 6.",
                    size=13.5, fill=RED_F, stroke=POS, sw=2, color=INK))

    p.append(text(60, 536,
                  "Рядки 1–4 — числа Нікомаха (≈100 н.е.); 5–7 пораховано в Європі аж 1536–1772.",
                  size=12, color=MUTED, anchor="start", italic=True))

    return render(os.path.join(OUT, "broken-laws.svg"), W, H, *p,
                  title="Два закони Нікомаха — і числа, що їх спростували")


# ── hunt-timeline: рідкість відкриттів і довга тиша ──────────────────────────
# Ідея: досконалі числа знаходили жахливо повільно, і кожне нове вбивало черговий
# «закон». Вертикальна вісь показує 2000+ років та ≈1450-річну тишу в Європі.
def fig_hunt_timeline():
    W, H = 1000, 700
    p = []
    spine = 330
    p.append(line(spine, 96, spine, 648, color=MUTED, sw=2.2))

    # (рік, [рядки опису], тип: 0 звичайний / 1 закон вмер / 2 джерело законів)
    ms = [
        ("≈500 до н.е.", ["Піфагорійці", "6 і 28 — образи довершеності"], 0),
        ("≈300 до н.е.", ["Евклід, «Начала» IX.36", "правило 2^(p−1)(2ᵖ−1)"], 0),
        ("≈100 н.е.",    ["Нікомах: 4 числа", "і два «закони» (обидва хибні)"], 2),
        ("≈1000",        ["Ібн аль-Хайсам (араб. світ)", "часткове обернене Евкліда"], 0),
        ("≈1250",        ["Ібн Фаллус (араб. світ)", "таблиця: 7 правильних чисел"], 0),
        ("1536",         ["Регіус друкує 5-те: 33 550 336", "→ закон «n цифр» мертвий"], 1),
        ("1588",         ["Катальді: 6-те й 7-те числа", "→ закон «6,8,6,8» мертвий"], 1),
        ("1644",         ["Мерсенн: список простих 2ᵖ−1", "(з п'ятьма помилками)"], 0),
        ("1772",         ["Ойлер: 8-ме число; обернене", "доведено — парний випадок закрито"], 0),
    ]
    y0, step = 118, 64
    ys = []
    for i, (yr, lines, kind) in enumerate(ms):
        y = y0 + i * step
        ys.append(y)
        col = POS if kind == 1 else (NEG if kind == 2 else INK)
        dot_fill = RED_F if kind == 1 else (BLUE_F if kind == 2 else FILL)
        p.append(circle(spine, y, 7.5, fill=dot_fill, stroke=col, sw=2.4))
        p.append(text(spine - 26, y + 5, yr, size=13.5, color=col, anchor="end", bold=(kind != 0)))
        p.append(mtext(spine + 26, y - 4, lines, size=13, color=INK, anchor="start", lh=1.35))

    # тиша в Європі: між Нікомахом (i=2) і Регіусом (i=5)
    yA, yB = ys[2], ys[5]
    xb = 150
    p.append(line(xb, yA, xb, yB, color=MUTED, sw=2, dash="5,5"))
    p.append(line(xb, yA, xb + 10, yA, color=MUTED, sw=2))
    p.append(line(xb, yB, xb + 10, yB, color=MUTED, sw=2))
    p.append(mtext(84, (yA + yB) / 2 - 16, ["у Європі —", "≈1450 років", "без нового", "числа"],
                   size=12.5, color=MUTED, anchor="middle", lh=1.3))

    return render(os.path.join(OUT, "hunt-timeline.svg"), W, H, *p,
                  title="Полювання завдовжки у два тисячоліття")


# ── sigma-grid: мультиплікативність σ як прямокутник дільників ────────────────
# Ідея (вставка math-euler-converse): для взаємно простих a, b кожен дільник ab —
# рівно одна клітинка сітки (дільник a)×(дільник b); сума по сітці розкладається
# в добуток σ(a)·σ(b). Приклад 12 = 4·3: 6 клітинок = усі 6 дільників 12.
def fig_sigma_grid():
    W, H = 1000, 540
    p = []

    da = [1, 2, 4]                 # дільники 4 — рядки
    db = [1, 3]                    # дільники 3 — стовпці
    GX, GY, CW, CH = 360, 162, 128, 74

    # групові підписи осей
    p.append(text(GX + len(db) * CW / 2, 96, "дільники 3", size=15, color=NEG, bold=True))
    grid_mid = GY + len(da) * CH / 2
    p.append('<text transform="translate(272,%.1f) rotate(-90)" font-family="%s" '
             'font-size="15" fill="%s" text-anchor="middle" font-weight="700">дільники 4</text>'
             % (grid_mid, FONT, FIELD))

    # заголовки стовпців (дільники 3)
    for j, d2 in enumerate(db):
        p.append(fitbox(GX + j * CW + 8, 112, CW - 16, 34, str(d2),
                        size=17, fill=BLUE_F, stroke=NEG, sw=1.8, bold=True))
    # заголовки рядків (дільники 4)
    for i, d1 in enumerate(da):
        p.append(fitbox(GX - 62, GY + i * CH + 14, 46, CH - 28, str(d1),
                        size=17, fill=GREEN_F, stroke=FIELD, sw=1.8, bold=True))
    # клітинки — добутки (усі дільники 12)
    for i, d1 in enumerate(da):
        for j, d2 in enumerate(db):
            x, y = GX + j * CW + 8, GY + i * CH + 8
            iw, ih = CW - 16, CH - 16
            p.append(rect(x, y, iw, ih, fill=FILL, stroke=INK, sw=1.4, rx=5))
            p.append(text(x + iw / 2, y + ih / 2 - 5, "%d · %d" % (d1, d2),
                          size=13, color=MUTED))
            p.append(text(x + iw / 2, y + ih / 2 + 17, "%d" % (d1 * d2),
                          size=17, color=INK, bold=True))

    gh = GY + len(da) * CH
    p.append(fitbox(GX - 62, gh + 26, len(db) * CW + 62, 52,
                    "σ(12) = (1 + 2 + 4) · (1 + 3) = 7 · 4 = 28",
                    size=18, fill=GREEN_F, stroke=FIELD, sw=2.4, bold=True))
    p.append(mtext(W / 2, gh + 104,
                   ["кожен дільник 12 — рівно одна клітинка сітки;",
                    "сума виносить дільники 4 і дільники 3 в окремі дужки (бо 4 і 3 взаємно прості)"],
                   size=12.5, color=MUTED, lh=1.4))

    return render(os.path.join(OUT, "sigma-grid.svg"), W, H, *p,
                  title="σ мультиплікативна: сітка дільників розкладає суму в добуток")


# ── euler-squeeze: чому m має РІВНО два дільники ──────────────────────────────
# Ідея (вставка math-euler-converse): рівняння σ(n)=2n зводиться до σ(m)=m+c, де
# c = m/M, M = 2^(k+1)−1. m і c — уже два дільники m, і їхня сума ВЖЕ дорівнює
# σ(m); отже, іншого дільника немає → m просте, менший дільник c = 1 → m = M.
def fig_euler_squeeze():
    W, H = 1000, 560
    p = []
    M = "2ᵏ⁺¹ − 1"

    p.append(text(W / 2, 64,
                  "Рівняння досконалості лишає для σ(m) єдину можливість:   σ(m) = m + c,   c = m ∕ (%s)" % M,
                  size=14.5, color=INK))

    BX, BW, BY, BH = 150, 620, 122, 62
    mw = 0.76 * BW
    cw = BW - mw

    p.append(text(BX + BW / 2, 104, "σ(m) — сума ВСІХ дільників m", size=13, color=MUTED, italic=True))
    p.append(rect(BX, BY, mw, BH, fill=GREEN_F, stroke=FIELD, sw=2, rx=5))
    p.append(text(BX + mw / 2, BY + BH / 2 + 7, "m", size=22, color=FIELD, bold=True))
    p.append(rect(BX + mw, BY, cw, BH, fill=BLUE_F, stroke=NEG, sw=2, rx=5))
    p.append(text(BX + mw + cw / 2, BY + BH / 2 + 6, "c", size=19, color=NEG, bold=True))
    p.append(text(BX + mw + cw / 2, BY + BH + 22, "c = m ∕ (%s)" % M, size=12.5, color=NEG))

    # стеля, задана рівнянням, і третій дільник, що не влазить
    p.append(line(BX + BW, BY - 16, BX + BW, BY + BH + 34, color=POS, sw=1.8, dash="5,4"))
    p.append(rect(BX + BW + 14, BY, 92, BH, fill=RED_F, stroke=POS, sw=1.8, rx=5))
    p.append(text(BX + BW + 14 + 46, BY + BH / 2 + 6, "d ?", size=18, color=POS, bold=True))
    p.append(text(BX + BW + 60, BY + BH + 22, "не влазить", size=12, color=POS))

    p.append(mtext(W / 2, 256,
                   ["m і c — уже два дільники m, і їхня сума m + c ВЖЕ дорівнює σ(m).",
                    "Тож інших дільників m немає; а 1 завжди ділить m — отже 1 і є менший із двох, c = 1."],
                   size=14, color=INK, lh=1.5))

    cx = W / 2
    p.append(fitbox(cx - 200, 300, 400, 46, "m має РІВНО два дільники  ⟹  m просте",
                    size=15, fill=FILL, stroke=INK, sw=1.8, bold=True))
    p.append(arrow(cx, 346, cx, 372, color=MUTED, sw=1.8))
    p.append(fitbox(cx - 200, 372, 400, 46, "а два дільники простого — це 1 і m  ⟹  c = 1, m = %s" % M,
                    size=15, fill=FILL, stroke=INK, sw=1.8))
    p.append(arrow(cx, 418, cx, 444, color=MUTED, sw=1.8))
    p.append(fitbox(cx - 285, 444, 570, 56,
                    "n = 2ᵏ · (%s),  де %s просте  —  форма Евкліда" % (M, M),
                    size=17, fill=GREEN_F, stroke=FIELD, sw=2.6, bold=True))

    return render(os.path.join(OUT, "euler-squeeze.svg"), W, H, *p,
                  title="Оберт Ойлера: σ(m) = m + c затискає m у просте число")


# ── odd-parity: форма Ойлера з одного підрахунку парності ─────────────────────
# Ідея (вставка math-odd-perfect): для непарного досконалого N рівняння σ(N)=2N
# дає v₂(σ(N))=1 — двійка ділить σ(N) рівно раз. Серед цеглинок σ(pᵢ^aᵢ) рівно
# одна парна (виділене q, α≡1 mod4, q≡1 mod4), решта непарні (парні показники →
# повний квадрат m²). Разом N = q^α·m².
def fig_odd_parity():
    W, H = 1000, 560
    p = []

    p.append(fitbox(150, 60, 700, 54,
                    "N непарне  ⟹  σ(N) = 2N ≡ 2 (mod 4):  v₂(σ(N)) = 1",
                    size=16, fill=FILL, stroke=NEG, sw=2.2, bold=True))
    p.append(text(W / 2, 144,
                  "σ(N) — добуток цеглинок σ(pᵢ^aᵢ); рівно одна з них парна:",
                  size=13.5, color=MUTED, italic=True))

    cells = [
        ("σ(q^α)\nПАРНЕ · ÷2 раз", GREEN_F, FIELD, True),
        ("σ(p₂^a₂)\nнепарне", FILL, MUTED, False),
        ("σ(p₃^a₃)\nнепарне", FILL, MUTED, False),
        ("σ(p₄^a₄)\nнепарне", FILL, MUTED, False),
    ]
    cw, gap, ch = 200, 24, 62
    total = len(cells) * cw + (len(cells) - 1) * gap
    x0 = (W - total) / 2
    ytop = 166
    for i, (txt, fill, col, strong) in enumerate(cells):
        x = x0 + i * (cw + gap)
        p.append(fitbox(x, ytop, cw, ch, txt, size=14, fill=fill, stroke=col,
                        sw=2.6 if strong else 1.6, bold=strong, color=INK))
        p.append(arrow(x + cw / 2, ytop + ch, x + cw / 2, ytop + ch + 54,
                       color=MUTED, sw=1.8))

    yc = ytop + ch + 54
    p.append(fitbox(x0, yc, cw, 66,
                    "q^α\nq ≡ 1 (mod 4)\nα ≡ 1 (mod 4)",
                    size=13, fill=GREEN_F, stroke=FIELD, sw=2.6, bold=True, color=INK))
    rx = x0 + (cw + gap)
    rw = 3 * cw + 2 * gap
    p.append(fitbox(rx, yc, rw, 66,
                    "показники всі парні  ⟹  повні квадрати\nїхній добуток = m²",
                    size=14, fill=FILL, stroke=MUTED, sw=1.8, color=INK))

    p.append(fitbox(240, yc + 100, 520, 56,
                    "N = q^α · m²,   q ≡ α ≡ 1 (mod 4),   q ∤ m",
                    size=17, fill=GREEN_F, stroke=FIELD, sw=3, bold=True))

    return render(os.path.join(OUT, "odd-parity.svg"), W, H, *p,
                  title="Форма Ойлера випливає з одного підрахунку парності")


# ── odd-walls: стіни навколо можливого непарного досконалого числа ────────────
# Ідея: кожна умова — доведене «якщо існує, то мусить…». Стос стін із джерелами;
# унизу — нагадування, що над 10^1500 стелі немає, тож задача досі відкрита.
def fig_odd_walls():
    W, H = 1000, 566
    p = []

    rows = [
        ("N  >  10¹⁵⁰⁰", "Ошем–Рао, 2012"),
        ("Ω(N) ≥ 101  простих множників (з кратністю)", "Ошем–Рао, 2012"),
        ("ω(N) ≥ 10  РІЗНИХ простих множників", "Нільсен, 2015"),
        ("найбільший простий дільник  >  10⁸", "Ґото–Оно, 2008"),
        ("другий за величиною простий дільник  >  10⁴", "Іаннуччі, 1999"),
        ("форма Ойлера:  q^α · m²,  q ≡ α ≡ 1 (mod 4)", "Ойлер, XVIII ст."),
    ]
    x0, xw = 84, 622
    sx, sw_ = 726, 200
    y0, rh, gap = 72, 54, 12
    for i, (cond, src) in enumerate(rows):
        y = y0 + i * (rh + gap)
        p.append(fitbox(x0, y, xw, rh, cond, size=15, fill=GREEN_F, stroke=FIELD,
                        sw=2.2, bold=True, color=INK))
        p.append(fitbox(sx, y, sw_, rh, src, size=13, fill=FILL, stroke=MUTED,
                        sw=1.5, color=INK))

    yb = y0 + len(rows) * (rh + gap) + 8
    p.append(fitbox(84, yb, 832, 56,
                    "Усі умови — «якщо існує, то…»: вони відрізають малі числа, "
                    "але стелі над 10¹⁵⁰⁰ немає. Кут вузький — та не порожній.",
                    size=14, fill=RED_F, stroke=POS, sw=2, color=INK))

    return render(os.path.join(OUT, "odd-walls.svg"), W, H, *p,
                  title="Стіни навколо непарного досконалого числа")


for f in (fig_trichotomy, fig_euclid_bridge, fig_triangular, fig_binary,
          fig_mersenne_fold, fig_hunt_pipeline,
          fig_broken_laws, fig_hunt_timeline,
          fig_sigma_grid, fig_euler_squeeze,
          fig_odd_parity, fig_odd_walls):
    print("написано:", f())
