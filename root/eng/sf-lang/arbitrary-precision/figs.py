# -*- coding: utf-8 -*-
"""Фігури до теми «Довга арифметика»."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def polyline(pts, color, sw=2.6, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % p for p in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" '
            'stroke-width="%.1f"%s/>' % (s, color, sw, d))


# ── 1. Число як масив лімбів ────────────────────────────────────────────────
def fig_limbs():
    W, H = 960, 440
    p = []
    p.append(text(W / 2, 84, "340 282 366 920 938 463 463 374 607 431 768 211 455",
                  size=17, bold=True))
    p.append(text(W / 2, 110, "одне ціле число: 39 десяткових цифр, 128 бітів",
                  size=13, color=MUTED))
    p.append(arrow(W / 2, 124, W / 2, 158))

    bw, gap, bh = 196, 24, 66
    total = 4 * bw + 3 * gap
    x0 = (W - total) / 2
    y = 176
    names = ["a\u2083", "a\u2082", "a\u2081", "a\u2080"]
    weights = ["\u00b7 B\u00b3", "\u00b7 B\u00b2", "\u00b7 B\u00b9", "\u00b7 B\u2070"]
    bits = ["\u0431\u0456\u0442\u0438 127\u202696", "\u0431\u0456\u0442\u0438 95\u202664",
            "\u0431\u0456\u0442\u0438 63\u202632", "\u0431\u0456\u0442\u0438 31\u20260"]
    for i in range(4):
        x = x0 + i * (bw + gap)
        p.append(fitbox(x, y, bw, bh, names[i] + "\n0xFFFFFFFF", size=17, bold=True))
        p.append(text(x + bw / 2, y + bh + 30, weights[i], size=16, color=FIELD, bold=True))
        p.append(text(x + bw / 2, y + bh + 58, bits[i], size=13, color=MUTED))

    p.append(text(W / 2, 366, "N = a\u2083\u00b7B\u00b3 + a\u2082\u00b7B\u00b2 + a\u2081\u00b7B\u00b9 + a\u2080\u00b7B\u2070,   B = 2\u00b3\u00b2",
                  size=16, bold=True))
    p.append(text(W / 2, 400, "\u0443 \u043f\u0430\u043c\u2019\u044f\u0442\u0456 \u043f\u043e\u0440\u044f\u0434\u043e\u043a \u0437\u0432\u043e\u0440\u043e\u0442\u043d\u0438\u0439: a\u2080 \u043b\u0435\u0436\u0438\u0442\u044c \u0437\u0430 \u043d\u0430\u0439\u043c\u0435\u043d\u0448\u043e\u044e \u0430\u0434\u0440\u0435\u0441\u043e\u044e",
                  size=13, color=MUTED))
    render(os.path.join(OUT, "limbs.svg"), W, H, *p)


# ── 2. Ланцюг переносів у додаванні ─────────────────────────────────────────
def fig_carry():
    W, H = 960, 500
    p = []
    cw, gap, ch = 168, 26, 44
    total = 4 * cw + 3 * gap
    x0 = 196
    lab_x = x0 - 22

    a = ["0x00000000", "0xFFFFFFFF", "0xFFFFFFFF", "0xFFFFFFFF"]
    b = ["0x00000000", "0x00000000", "0x00000000", "0x00000001"]
    r = ["0x00000001", "0x00000000", "0x00000000", "0x00000000"]

    ya, yb, yadd, yr = 70, 130, 214, 320
    p.append(text(lab_x, ya + 28, "\u0434\u043e\u0434\u0430\u043d\u043e\u043a a", size=14, anchor="end", bold=True))
    p.append(text(lab_x, yb + 28, "\u0434\u043e\u0434\u0430\u043d\u043e\u043a b", size=14, anchor="end", bold=True))
    p.append(text(lab_x, yadd + 32, "\u0434\u043e\u0434\u0430\u0432\u0430\u043d\u043d\u044f", size=14, anchor="end", bold=True))
    p.append(text(lab_x, yr + 28, "\u0440\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442", size=14, anchor="end", bold=True))

    for i in range(4):
        x = x0 + i * (cw + gap)
        p.append(fitbox(x, ya, cw, ch, a[i], size=15))
        p.append(fitbox(x, yb, cw, ch, b[i], size=15))
        p.append(fitbox(x, yadd, cw, 56, "a + b + \u043f\u0435\u0440\u0435\u043d\u043e\u0441", size=14))
        p.append(fitbox(x, yr, cw, ch, r[i], size=15,
                        fill=("#fdecea" if i == 0 else FILL),
                        stroke=(POS if i == 0 else LINE)))
        p.append(arrow(x + cw / 2, yb + ch + 4, x + cw / 2, yadd - 6))
        p.append(arrow(x + cw / 2, yadd + 56 + 6, x + cw / 2, yr - 6))

    # перенос іде справа наліво: з молодшого лімба у старший сусідній
    for i in range(1, 4):
        x_src = x0 + i * (cw + gap)             # ліве ребро джерела
        x_dst = x0 + (i - 1) * (cw + gap) + cw  # праве ребро приймача
        p.append(arrow(x_src - 3, yadd + 28, x_dst + 3, yadd + 28, color=POS))
        p.append(text((x_src + x_dst) / 2, yadd + 12, "1", size=13, color=POS, bold=True))

    p.append(text(W / 2, 424, "\u043a\u043e\u0436\u043d\u0430 \u0447\u0435\u0440\u0432\u043e\u043d\u0430 \u0441\u0442\u0440\u0456\u043b\u043a\u0430 \u2014 \u043e\u0434\u0438\u043d \u0431\u0456\u0442 \u043f\u0435\u0440\u0435\u043d\u043e\u0441\u0443 \u0432 \u043d\u0430\u0441\u0442\u0443\u043f\u043d\u0438\u0439 \u043b\u0456\u043c\u0431",
                  size=14, color=POS, bold=True))
    p.append(text(W / 2, 456, "\u0434\u043e\u0434\u0430\u043d\u043d\u044f \u043e\u0434\u0438\u043d\u0438\u0446\u0456 \u0437\u043c\u0456\u043d\u044e\u0454 \u0432\u0441\u0456 \u0447\u043e\u0442\u0438\u0440\u0438 \u043b\u0456\u043c\u0431\u0438: \u0434\u043e\u0432\u0436\u0438\u043d\u0430 \u043b\u0430\u043d\u0446\u044e\u0433\u0430 \u2014 \u0446\u0435 \u0432\u0441\u044f \u0434\u043e\u0432\u0436\u0438\u043d\u0430 \u0447\u0438\u0441\u043b\u0430",
                  size=13, color=MUTED))
    render(os.path.join(OUT, "carry-chain.svg"), W, H, *p)


# ── 3. Сітка часткових добутків ─────────────────────────────────────────────
def fig_mulgrid():
    W, H = 960, 540
    p = []
    cw, chh, gx, gy = 202, 78, 20, 18
    x0, y0 = 214, 132
    p.append(text(W / 2, 78, "\u043a\u043e\u0436\u0435\u043d \u043b\u0456\u043c\u0431 a \u043c\u043d\u043e\u0436\u0438\u0442\u044c\u0441\u044f \u043d\u0430 \u043a\u043e\u0436\u0435\u043d \u043b\u0456\u043c\u0431 b", size=16, bold=True))

    for j in range(3):
        x = x0 + j * (cw + gx)
        p.append(text(x + cw / 2, y0 - 16, "a\u2080a\u2081a\u2082"[2 * j:2 * j + 2], size=15, bold=True, color=NEG))
    for i in range(3):
        y = y0 + i * (chh + gy)
        p.append(text(x0 - 24, y + chh / 2 + 5, "b\u2080b\u2081b\u2082"[2 * i:2 * i + 2],
                      size=15, bold=True, anchor="end", color=NEG))
        for j in range(3):
            x = x0 + j * (cw + gx)
            s = "a%s\u00b7b%s" % ("\u2080\u2081\u2082"[j], "\u2080\u2081\u2082"[i])
            idx = i + j
            sub = "\u2080\u2081\u2082\u2083\u2084\u2085"
            p.append(fitbox(x, y, cw, chh,
                            s + "\n\u2192 r" + sub[idx] + " \u0456 r" + sub[idx + 1], size=15))

    box, bw, bh = textbox(W / 2, 434,
                          "\u0434\u043e\u0431\u0443\u0442\u043e\u043a \u0434\u0432\u043e\u0445 \u043b\u0456\u043c\u0431\u0456\u0432 \u2014 \u0446\u0435 \u043f\u043e\u0434\u0432\u0456\u0439\u043d\u0435 \u0441\u043b\u043e\u0432\u043e:\n"
                          "\u043c\u043e\u043b\u043e\u0434\u0448\u0430 \u043f\u043e\u043b\u043e\u0432\u0438\u043d\u0430 \u043b\u044f\u0433\u0430\u0454 \u0432 r\u1d62\u208a\u2c7c, \u0441\u0442\u0430\u0440\u0448\u0430 \u2014 \u0432 r\u1d62\u208a\u2c7c\u208a\u2081",
                          size=15, fill="#eef7f0", stroke=FIELD)
    p.append(box)
    p.append(text(W / 2, 498, "n \u00b7 m \u0434\u043e\u0431\u0443\u0442\u043a\u0456\u0432 \u0441\u043b\u0456\u0432 \u2014 \u0437\u0432\u0456\u0434\u0441\u0438 \u043a\u0432\u0430\u0434\u0440\u0430\u0442\u0438\u0447\u043d\u0430 \u0432\u0430\u0440\u0442\u0456\u0441\u0442\u044c",
                  size=14, color=MUTED))
    render(os.path.join(OUT, "mul-grid.svg"), W, H, *p)


# ── 4. Де окупається складніший алгоритм ────────────────────────────────────
def fig_cost():
    W, H = 960, 520
    X0, X1, Y0, Y1 = 120, 840, 96, 440
    LOGN, LOGC = 6.0, 12.5

    def px(logn):
        return X0 + logn / LOGN * (X1 - X0)

    def py(cost):
        return Y1 - (math.log10(cost)) / LOGC * (Y1 - Y0)

    def curve(f, color):
        pts = []
        k = 0
        while k <= 120:
            logn = LOGN * k / 120.0
            n = 10 ** logn
            if n >= 2:
                pts.append((px(logn), py(f(n))))
            k += 1
        return polyline(pts, color)

    school = lambda n: n * n
    karat = lambda n: 3.466 * n ** 1.585
    fft = lambda n: 41.2 * n * math.log(n, 2)

    p = []
    p.append(line(X0, Y1, X1, Y1))
    p.append(line(X0, Y1, X0, Y0))
    p.append(text(X0, Y0 - 22, "\u0432\u0430\u0440\u0442\u0456\u0441\u0442\u044c, \u043b\u043e\u0433\u0430\u0440\u0438\u0444\u043c\u0456\u0447\u043d\u0430 \u0448\u043a\u0430\u043b\u0430",
                  size=14, anchor="start", color=MUTED))
    p.append(text(X1, Y1 + 58, "\u0434\u043e\u0432\u0436\u0438\u043d\u0430 \u0447\u0438\u0441\u043b\u0430 \u0432 \u043b\u0456\u043c\u0431\u0430\u0445, \u043b\u043e\u0433\u0430\u0440\u0438\u0444\u043c\u0456\u0447\u043d\u0430 \u0448\u043a\u0430\u043b\u0430",
                  size=14, anchor="end", color=MUTED))
    ticks = ["1", "10", "100", "10\u00b3", "10\u2074", "10\u2075", "10\u2076"]
    for i, t in enumerate(ticks):
        x = px(i)
        p.append(line(x, Y1, x, Y1 + 7, color=MUTED))
        p.append(text(x, Y1 + 27, t, size=13, color=MUTED))

    p.append(curve(school, POS))
    p.append(curve(karat, NEG))
    p.append(curve(fft, FIELD))

    # пороги
    p.append(line(px(math.log10(20)), Y1, px(math.log10(20)), py(400), color=MUTED, dash="5,5"))
    p.append(circle(px(math.log10(20)), py(400), 5, fill=BG, stroke=INK, sw=2))
    p.append(mtext(px(math.log10(20)) - 16, Y1 - 52,
                   ["\u0442\u0443\u0442 \u043e\u043a\u0443\u043f\u0430\u0454\u0442\u044c\u0441\u044f", "\u041a\u0430\u0440\u0430\u0446\u0443\u0431\u0430"],
                   size=13, anchor="end", color=MUTED))
    p.append(line(px(math.log10(5000)), Y1, px(math.log10(5000)), py(karat(5000)), color=MUTED, dash="5,5"))
    p.append(circle(px(math.log10(5000)), py(karat(5000)), 5, fill=BG, stroke=INK, sw=2))
    p.append(mtext(px(math.log10(5000)) - 16, Y1 - 52,
                   ["\u0442\u0443\u0442 \u043e\u043a\u0443\u043f\u0430\u0454\u0442\u044c\u0441\u044f", "\u0428\u041f\u0424"],
                   size=13, anchor="end", color=MUTED))

    # легенда
    p.append(rect(X0 + 16, Y0 + 14, 330, 108, fill="#ffffff", stroke=MUTED, sw=1))
    rows = [("\u0448\u043a\u0456\u043b\u044c\u043d\u0435 \u043c\u043d\u043e\u0436\u0435\u043d\u043d\u044f: n\u00b2", POS),
            ("\u041a\u0430\u0440\u0430\u0446\u0443\u0431\u0430: n^1.585", NEG),
            ("\u0428\u041f\u0424: n\u00b7log n", FIELD)]
    for i, (s, c) in enumerate(rows):
        yy = Y0 + 44 + i * 32
        p.append(line(X0 + 32, yy - 5, X0 + 74, yy - 5, color=c, sw=3))
        p.append(text(X0 + 88, yy, s, size=14, anchor="start"))

    render(os.path.join(OUT, "cost-crossover.svg"), W, H, *p)


# ── 5. Родовід ремесла (вставка hist-bignum) ────────────────────────────────
def fig_hist_timeline():
    rows = [
        ("1876",
         "Едуар Люка вручну доводить простоту числа 2¹²⁷−1 — 39 цифр",
         "цей рекорд не поб’ють 75 років"),
        ("1903",
         "Френк Нельсон Коул мовчки розкладає на дошці 2⁶⁷−1",
         "пошук множників коштував йому «трьох років неділь»"),
        ("1949",
         "ENIAC рахує 2037 цифр π за 70 годин машинного часу",
         "терпіння вперше стає дешевим ресурсом"),
        ("1952",
         "SWAC знаходить M₅₂₁, а через дві години — M₆₀₇",
         "код пишуть під одну задачу й одну машину"),
        ("1968",
         "Macsyma в MIT: бігнами вбудовані в мову MACLISP",
         "точне ціле стає типом даних, а не підпрограмою"),
        ("1969",
         "Кнут, «TAOCP» том 2: алгоритми A, S, M і D",
         "рецепти замінюються доведеними межами"),
        ("1991",
         "Перший випуск GMP Торб’єрна Ґранлунда",
         "швидкість переїжджає в окрему бібліотеку з асемблером"),
        ("2008",
         "Python 3.0: короткого цілого більше немає",
         "кожне ціле довге; переповнення зникає з мови"),
    ]
    W = 980
    top, step, bh = 96, 94, 70
    H = top + (len(rows) - 1) * step + bh + 78
    xline, xbox, wbox = 196, 236, 700
    p = []
    p.append(text(W / 2, 46,
                  "від «трьох років неділь» до мови, де довге число є типом за замовчуванням",
                  size=17, bold=True))
    p.append(line(xline, top + bh / 2, xline, top + (len(rows) - 1) * step + bh / 2,
                  color=MUTED, sw=2))
    for i, (year, l1, l2) in enumerate(rows):
        y = top + i * step
        cy = y + bh / 2
        p.append(text(xline - 34, cy + 6, year, size=18, bold=True, anchor="end", color=POS))
        p.append(circle(xline, cy, 7, fill=BG, stroke=INK, sw=2))
        p.append(line(xline + 8, cy, xbox - 6, cy, color=MUTED, sw=1.5))
        p.append(fitbox(xbox, y, wbox, bh, l1 + "\n" + l2, size=15))
    p.append(text(W / 2, H - 34,
                  "дати й імена звірені за першоджерелами й зведеними хронологіями",
                  size=13, color=MUTED))
    render(os.path.join(OUT, "hist-timeline.svg"), W, H, *p)


# -- 5. Struktura big u pamyati (do vstavky proj-bignum-c) --
def fig_layout():
    W, H = 1080, 500
    p = []

    p.append(text(200, 74, "struct big", size=17, bold=True))
    rows = ["d  \u2192  \u0431\u0443\u0444\u0435\u0440 \u043b\u0456\u043c\u0431\u0456\u0432",
            "n = 3  \u0437\u043d\u0430\u0447\u0443\u0449\u0438\u0445",
            "cap = 8  \u0432\u0438\u0434\u0456\u043b\u0435\u043d\u043e",
            "neg = 0  \u0437\u043d\u0430\u043a \u043e\u043a\u0440\u0435\u043c\u043e"]
    for i, s in enumerate(rows):
        p.append(fitbox(60, 92 + i * 44, 280, 36, s, size=14))
    p.append(arrow(346, 110, 388, 178))

    cw, gap, cy, ch = 76, 6, 150, 66
    x0 = 400

    def cx(i):
        return x0 + i * (cw + gap)

    vals = ["7", "0", "5"]
    for i in range(3):
        st = FIELD if i == 2 else LINE
        p.append(fitbox(cx(i), cy, cw, ch, "d[%d]\n%s" % (i, vals[i]),
                        size=15, stroke=st, sw=3 if i == 2 else 1.5))
    for i in range(3, 8):
        p.append(fitbox(cx(i), cy, cw, ch, "d[%d]\n?" % i,
                        size=15, fill="#f2f2f2", stroke="#c8c8c8", color=MUTED))

    p.append(text(cx(2) + cw / 2, 138, "\u2260 0", size=13, color=FIELD, bold=True))

    weights = ["\u00b7 B\u2070", "\u00b7 B\u00b9", "\u00b7 B\u00b2"]
    for i in range(3):
        p.append(text(cx(i) + cw / 2, 246, weights[i], size=15, color=FIELD, bold=True))

    p.append(line(cx(3), 232, cx(7) + cw, 232, color=MUTED, sw=1.5))
    p.append(text((cx(3) + cx(7) + cw) / 2, 256,
                  "\u0437\u0430 \u043c\u0435\u0436\u0435\u044e n \u043b\u0435\u0436\u0438\u0442\u044c \u0431\u0443\u0434\u044c-\u0449\u043e \u2014 \u043d\u0435 \u0447\u0438\u0442\u0430\u0454\u043c\u043e",
                  size=13, color=MUTED))

    b1, _, _ = textbox(276, 348,
                       ["\u0456\u043d\u0432\u0430\u0440\u0456\u0430\u043d\u0442 1",
                        "d[n\u22121] \u2260 0 \u2014 \u0432\u0435\u0434\u0443\u0447\u0438\u0445 \u043d\u0443\u043b\u0456\u0432 \u043d\u0435\u043c\u0430\u0454"],
                       size=14, stroke=FIELD, sw=2, fill="#f2fbf5")
    b2, _, _ = textbox(780, 348,
                       ["\u0456\u043d\u0432\u0430\u0440\u0456\u0430\u043d\u0442 2",
                        "n = 0 \u21d2 neg = 0 \u2014 \u00ab\u043c\u0456\u043d\u0443\u0441 \u043d\u0443\u043b\u044f\u00bb \u043d\u0435\u043c\u0430\u0454"],
                       size=14, stroke=FIELD, sw=2, fill="#f2fbf5")
    p.append(b1)
    p.append(b2)

    p.append(mtext(W / 2, 430,
                   ["\u041e\u0431\u0438\u0434\u0432\u0430 \u0456\u043d\u0432\u0430\u0440\u0456\u0430\u043d\u0442\u0438 \u0442\u0440\u0438\u043c\u0430\u0454 \u043e\u0434\u043d\u0430 \u0444\u0443\u043d\u043a\u0446\u0456\u044f \u2014 big_trim():",
                    "\u0437\u0440\u0456\u0437\u0430\u0454 \u043d\u0443\u043b\u044c\u043e\u0432\u0456 \u043b\u0456\u043c\u0431\u0438 \u0437\u0433\u043e\u0440\u0438 \u0456, \u043a\u043e\u043b\u0438 \u0447\u0438\u0441\u043b\u043e \u0441\u0442\u0430\u043b\u043e \u043d\u0443\u043b\u0435\u043c, \u0433\u0430\u0441\u0438\u0442\u044c \u0437\u043d\u0430\u043a."],
                   size=14, color=MUTED))

    render(os.path.join(OUT, "bignum-layout.svg"), W, H, *p,
           title="\u0414\u043e\u0432\u0433\u0435 \u0447\u0438\u0441\u043b\u043e \u044f\u043a \u0441\u0442\u0440\u0443\u043a\u0442\u0443\u0440\u0430 \u0434\u0430\u043d\u0438\u0445: \u0431\u0443\u0444\u0435\u0440, \u0434\u043e\u0432\u0436\u0438\u043d\u0430, \u0437\u043d\u0430\u043a")


# -- 6. Nakopychuvalnyi prokhid mnozhennya (do vstavky proj-bignum-c) --
def fig_addmul():
    W, H = 1020, 470
    p = []
    n = 3
    cw, gap, x0 = 100, 8, 340

    def cx(i):
        return x0 + i * (cw + gap)

    for i in range(6):
        p.append(text(cx(i) + cw / 2, 84, "r[%d]" % i, size=14, bold=True))
        p.append(fitbox(cx(i), 96, cw, 34, "0", size=14, fill="#f8f8f8", stroke=MUTED))
    p.append(text(x0 - 24, 120,
                  "\u0441\u0442\u0430\u0440\u0442: \u0443\u0441\u0456 \u043d\u0443\u043b\u0456",
                  size=14, anchor="end", color=MUTED))

    for k in range(3):
        y = 160 + k * 88
        for i in range(6):
            p.append(rect(cx(i), y, cw, 56, fill="#fcfcfc", stroke="#dddddd", sw=1))
        ww = n * cw + (n - 1) * gap
        p.append(rect(cx(k), y, ww, 56, fill="#fdecea", stroke=POS, sw=2.4))
        p.append(text(cx(k) + ww / 2, y + 35,
                      "r[%d..%d] += a \u00b7 b[%d]" % (k, k + n - 1, k),
                      size=16, bold=True, color=POS))
        p.append(rect(cx(n + k), y, cw, 56, fill="#eaf7ee", stroke=FIELD, sw=2.4))
        p.append(text(cx(n + k) + cw / 2, y + 35,
                      "\u043f\u0435\u0440\u0435\u043d\u043e\u0441", size=13, color=FIELD, bold=True))
        p.append(mtext(x0 - 24, y + 24,
                       ["\u043f\u0440\u043e\u0445\u0456\u0434 j = %d" % k,
                        "n = 3 \u043c\u043d\u043e\u0436\u0435\u043d\u043d\u044f \u0441\u043b\u0456\u0432"],
                       size=14, anchor="end"))

    p.append(mtext(W / 2, 420,
                   ["\u041a\u043e\u0436\u0435\u043d \u043f\u0440\u043e\u0445\u0456\u0434 \u0447\u0456\u043f\u0430\u0454 n \u043a\u043b\u0456\u0442\u0438\u043d\u043e\u043a \u0456 \u043a\u043b\u0430\u0434\u0435 \u043f\u0435\u0440\u0435\u043d\u043e\u0441 \u0443 \u043d\u0430\u0441\u0442\u0443\u043f\u043d\u0443.",
                    "\u0412\u043e\u043d\u0430 \u0449\u043e\u0440\u0430\u0437\u0443 \u0449\u0435 \u043d\u0443\u043b\u044c\u043e\u0432\u0430 \u2014 \u0442\u043e\u043c\u0443 \u0442\u0443\u0434\u0438 \u043c\u043e\u0436\u043d\u0430 \u043f\u0438\u0441\u0430\u0442\u0438, \u0430 \u043d\u0435 \u0434\u043e\u0434\u0430\u0432\u0430\u0442\u0438. \u0420\u0430\u0437\u043e\u043c n\u00b7m = 9 \u043c\u043d\u043e\u0436\u0435\u043d\u044c \u0441\u043b\u0456\u0432."],
                   size=14, color=MUTED))

    render(os.path.join(OUT, "addmul-sweep.svg"), W, H, *p,
           title="\u041c\u043d\u043e\u0436\u0435\u043d\u043d\u044f \u043d\u0430\u043a\u043e\u043f\u0438\u0447\u0443\u0432\u0430\u043b\u044c\u043d\u0438\u043c \u043f\u0440\u043e\u0445\u043e\u0434\u043e\u043c: \u0432\u0456\u043a\u043d\u043e \u0457\u0434\u0435 \u0432\u043f\u0440\u0430\u0432\u043e \u043d\u0430 \u043b\u0456\u043c\u0431 \u0437\u0430 \u043a\u0440\u043e\u043a")



# ── Що саме викидають, коли вгадують цифру частки ───────────────────────────
def fig_div_truncate():
    W, H = 1060, 500
    p = [text(W / 2, 30, "Що відкидають, коли вгадують цифру частки", size=18, bold=True)]

    x0, cw, gap = 210, 155, 11
    yu, yv, bh = 88, 200, 62
    col = lambda i: x0 + i * (cw + gap)

    p.append(text(28, 112, "ділене  u", size=16, anchor="start", bold=True))
    p.append(text(28, 134, "n+1 лімбів", size=13, anchor="start", color=MUTED))
    p.append(text(28, 224, "дільник  v", size=16, anchor="start", bold=True))
    p.append(text(28, 246, "n лімбів", size=13, anchor="start", color=MUTED))

    u_names = ["uⱼ₊ₙ", "uⱼ₊ₙ₋₁", "uⱼ₊ₙ₋₂", "…", "uⱼ"]
    for i, s in enumerate(u_names):
        keep = i < 2
        p.append(fitbox(col(i), yu, cw, bh, s, size=19, bold=keep,
                        fill="#ffffff" if keep else "#eaf0fd",
                        stroke=INK if keep else NEG,
                        color=INK if keep else NEG))
    v_names = ["vₙ₋₁", "vₙ₋₂", "…", "v₀"]
    for i, s in enumerate(v_names):
        keep = i == 0
        p.append(fitbox(col(i + 1), yv, cw, bh, s, size=19, bold=keep,
                        fill="#ffffff" if keep else "#fdecea",
                        stroke=INK if keep else POS,
                        color=INK if keep else POS))

    p.append(line(col(0), 80, col(1) + cw, 80, color=FIELD, sw=3))
    p.append(text((col(0) + col(1) + cw) / 2, 70,
                  "ці два лімби — ділене пробного ділення",
                  size=14, color=FIELD, bold=True))
    p.append(line(col(1), 274, col(1) + cw, 274, color=FIELD, sw=3))
    p.append(text(col(1) + cw / 2, 294, "цей один — дільник",
                  size=14, color=FIELD, bold=True))

    b, _, _ = textbox(300, 356,
                      ["у діленого відкинули хвіст",
                       "→ пробна цифра МЕНШАЄ",
                       "(і то не більш як на 1)"],
                      size=14, fill="#eaf0fd", stroke=NEG, color=NEG)
    p.append(b)
    b, _, _ = textbox(768, 356,
                      ["у дільника відкинули хвіст",
                       "→ дільник став МЕНШИЙ",
                       "→ цифра БІЛЬШАЄ — аж до B/vₙ₋₁"],
                      size=14, fill="#fdecea", stroke=POS, color=POS)
    p.append(b)

    b, _, _ = textbox(W / 2, 452,
                      "другий ефект переважає:    q ≤ q̂ < q + B/vₙ₋₁ + 1",
                      size=17, bold=True, fill="#eafaf0", stroke=FIELD, sw=2)
    p.append(b)

    render(os.path.join(OUT, "div-truncate.svg"), W, H, *p)


# ── Похибка як функція старшого лімба дільника ──────────────────────────────
def fig_div_bound():
    W, H = 1040, 460
    B = 64.0
    X0, X1, Y0, YT = 130, 940, 372, 90
    EMAX = 34.0
    px = lambda t: X0 + (t / B) * (X1 - X0)
    py = lambda e: Y0 - (e / EMAX) * (Y0 - YT)

    p = [text(W / 2, 30, "Скільки виправлень коштує пробна цифра", size=18, bold=True)]

    p.append(rect(px(B / 2), YT - 8, X1 - px(B / 2), Y0 - YT + 8,
                  fill="#eafaf0", stroke="#eafaf0", sw=0, rx=0))
    p.append(mtext((px(B / 2) + X1) / 2, 124,
                   ["нормалізований дільник:  vₙ₋₁ ≥ B/2",
                    "похибка ніколи не більша за 2"],
                   size=14, color=FIELD, bold=True))

    p.append(line(X0, Y0, X1, Y0, color=INK, sw=2))
    p.append(line(X0, Y0, X0, YT - 8, color=INK, sw=2))
    p.append(text(X0 - 12, 64, "похибка  q̂ − q", size=14, anchor="end", color=MUTED))
    p.append(text(X1, Y0 + 46, "старший лімб дільника  vₙ₋₁",
                  size=14, anchor="end", color=MUTED))

    for t, lab in ((1, "1"), (8, "B/8"), (16, "B/4"), (32, "B/2"), (64, "B")):
        p.append(line(px(t), Y0, px(t), Y0 + 7, color=INK, sw=1.5))
        p.append(text(px(t), Y0 + 26, lab, size=14, color=MUTED))
    for e in (2, 8, 16, 32):
        p.append(line(X0 - 7, py(e), X0, py(e), color=INK, sw=1.5))
        p.append(text(X0 - 14, py(e) + 5, str(e), size=13, anchor="end", color=MUTED))

    p.append(line(X0, py(2), X1, py(2), color=FIELD, sw=1.8, dash="7,6"))
    p.append(text(X1 - 12, py(2) - 36, "нижче цієї межі тримається алгоритм D",
                  size=13, anchor="end", color=FIELD))

    # точний найгірший випадок, порахований перебором для B = 64
    WORST = [32, 21, 16, 13, 11, 9, 8, 7, 7, 6, 6, 5, 5, 5, 4, 4, 4, 4, 4, 3,
             3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
             2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1]
    pts = [(px(t), py(WORST[t - 1])) for t in range(1, 64)]
    p.append(polyline(pts, POS, sw=3.0))
    p.append(circle(px(1), py(32), 6, fill=POS, stroke=POS))
    p.append(mtext(px(1) + 24, 100,
                   ["vₙ₋₁ = 1: похибка сягає B/2",
                    "для B = 2⁶⁴ це ≈ 9.2·10¹⁸ виправлень"],
                   size=14, color=POS, anchor="start", bold=True))
    p.append(text(W / 2, H - 18,
                  "крива — точний найгірший випадок, порахований перебором для B = 64",
                  size=13, color=MUTED))

    render(os.path.join(OUT, "div-error-bound.svg"), W, H, *p)


# ── Скільки кроків доходить до кожної стадії корекції ───────────────────────
def fig_div_funnel():
    W, H = 1020, 470
    p = [text(W / 2, 32, "Куди подіваються виправлення", size=18, bold=True)]

    rows = [
        ("усі кроки ділення", "100 %", 1.000, MUTED),
        ("q̂ > q — потрібне бодай одне виправлення", "≈ 33 %", 0.331, POS),
        ("q̂ = q + 2 — потрібні аж два", "≈ 0.9 %", 0.009, POS),
        ("після перевірки за vₙ₋₂ лишилося q̂ = q + 1", "≈ 0.5 %", 0.005, FIELD),
    ]
    x0, wmax, y0, bh, step = 470, 470, 78, 52, 76
    for i, (lab, num, frac, col) in enumerate(rows):
        y = y0 + i * step
        # ширина смуги — логарифмічна: інакше останні дві були б тоншими за лінію
        w = max(wmax * (1.0 + math.log10(frac) / 3.0), 26)
        p.append(rect(x0, y, w, bh, fill="#fdecea" if col is POS else
                      ("#eafaf0" if col is FIELD else "#f2f2f2"),
                      stroke=col, sw=2))
        p.append(text(x0 - 20, y + bh / 2 + 6, lab, size=15, anchor="end"))
        p.append(text(x0 + w + 16, y + bh / 2 + 6, num, size=16,
                      anchor="start", bold=True, color=col))
        if i < len(rows) - 1:
            p.append(arrow(x0 + 13, y + bh + 2, x0 + 13, y + step - 2, color=MUTED))

    b, _, _ = textbox(W / 2, 400,
                      ["Виміряно на 600 000 випадкових кроків при B = 64; ширина смуг логарифмічна.",
                       "Остання смуга спадає як ≈ 0.34/B: при B = 2⁶⁴ це ≈ 2·10⁻²⁰ —",
                       "гілка «додати дільник назад» практично ніколи не виконується."],
                      size=14, fill="#eafaf0", stroke=FIELD, sw=2)
    p.append(b)

    render(os.path.join(OUT, "div-correction-funnel.svg"), W, H, *p)


fig_limbs()
fig_carry()
fig_mulgrid()
fig_cost()
fig_hist_timeline()
fig_layout()
fig_addmul()
fig_div_truncate()
fig_div_bound()
fig_div_funnel()
print("ok")
