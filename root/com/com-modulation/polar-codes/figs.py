# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GOODF, GOODS = "#eafaf0", "#27ae60"   # добрий канал / дані
BADF,  BADS  = "#fdecea", "#c0392b"   # поганий канал / заморожений
CHF,   CHS   = "#eef4ff", "#2457d6"   # канал/копія


# ── transform: зерно поляризації — перетворення двох каналів ──────────────────

def fig_transform():
    W, H = 840, 500
    p = []

    # координати butterfly
    ux, y1, y2 = 96, 156, 306
    xx = 316            # вузли x1 (⊕) та x2
    bx0, bw, bh = 424, 116, 46      # канальні коробки
    yx = 700            # виходи

    # входи u1, u2
    p.append(circle(ux, y1, 23, fill=GOODF, stroke=GOODS, sw=2.4))
    p.append(text(ux, y1 + 6, "u₁", size=16, color=GOODS, bold=True))
    p.append(circle(ux, y2, 23, fill=GOODF, stroke=GOODS, sw=2.4))
    p.append(text(ux, y2 + 6, "u₂", size=16, color=GOODS, bold=True))
    p.append(text(ux, y1 - 34, "1) декодуємо першим", size=11, color=MUTED, italic=True))
    p.append(text(ux, y2 + 44, "2) потім, знаючи u₁", size=11, color=MUTED, italic=True))

    # лінії до вузлів x1(⊕), x2
    p.append(line(ux + 23, y1, xx - 17, y1, color=LINE, sw=1.8))          # u1 → x1
    p.append(line(ux + 18, y2 - 12, xx - 12, y1 + 14, color=LINE, sw=1.8))  # u2 → x1 (діагональ)
    p.append(line(ux + 23, y2, xx - 12, y2, color=LINE, sw=1.8))          # u2 → x2

    # вузол x1 = XOR
    p.append(circle(xx, y1, 17, fill=BG, stroke=INK, sw=2.0))
    p.append(text(xx, y1 + 6, "⊕", size=17, color=INK, bold=True))
    p.append(text(xx, y1 - 30, "x₁ = u₁⊕u₂", size=12, color=INK))
    # вузол x2 (пряме)
    p.append(text(xx, y2 - 26, "x₂ = u₂", size=12, color=INK))
    p.append(circle(xx, y2, 6, fill=INK, stroke=INK, sw=1.0))

    # канальні коробки (BEC)
    for cy in (y1, y2):
        p.append(line(xx + 17 if cy == y1 else xx + 6, cy, bx0, cy, color=LINE, sw=1.8))
        p.append(rect(bx0, cy - bh / 2, bw, bh, fill=CHF, stroke=CHS, sw=2.0, rx=8))
        p.append(mtext(bx0 + bw / 2, cy - 3, ["канал", "стирання p"], size=12.5, color=CHS, bold=True))

    # виходи y1, y2
    for cy, lab in ((y1, "y₁"), (y2, "y₂")):
        p.append(line(bx0 + bw, cy, yx - 22, cy, color=LINE, sw=1.8))
        p.append(circle(yx, cy, 22, fill=FILL, stroke=INK, sw=2.0))
        p.append(text(yx, cy + 6, lab, size=15, color=INK, bold=True))

    # вердикти
    b1, w1, h1 = textbox(232, 430,
                         "u₁: потрібні ОБИДВА виходи\nW⁻ гірший · стирання 2p−p²",
                         size=13, bold=True, fill=BADF, stroke=BADS, sw=2.2, pad=12)
    p.append(b1)
    b2, w2, h2 = textbox(612, 430,
                         "u₂: досить ОДНОГО виходу\nW⁺ кращий · стирання p²",
                         size=13, bold=True, fill=GOODF, stroke=GOODS, sw=2.2, pad=12)
    p.append(b2)

    render(os.path.join(OUT, "transform.svg"), W, H, *p,
           title="Зерно поляризації: один канал стає гіршим, другий кращим")


# ── polarize: каскад поляризації, стовпчики тікають до полюсів ────────────────

def fig_polarize():
    W, H = 900, 500
    p = []

    N1 = [0.5]
    N2 = [0.25, 0.75]
    N4 = [0.0625, 0.4375, 0.5625, 0.9375]
    N8 = [0.0039, 0.1211, 0.1914, 0.3164, 0.6836, 0.8086, 0.8789, 0.9961]
    cols = [(N1, "N=1"), (N2, "N=2"), (N4, "N=4"), (N8, "N=8")]

    y_base = 396
    hmax = 250.0
    plot_x0, plot_x1 = 92, 852
    slot = (plot_x1 - plot_x0) / len(cols)

    # вісь пропускної + рівень 0.5
    p.append(line(plot_x0 - 8, y_base, plot_x1, y_base, color=INK, sw=1.8))
    p.append(line(plot_x0 - 8, y_base - hmax, plot_x0 - 8, y_base, color=INK, sw=1.8))
    for cap, lab in ((0.0, "0"), (0.5, "0.5"), (1.0, "1")):
        yy = y_base - cap * hmax
        p.append(text(plot_x0 - 18, yy + 4, lab, size=11.5, color=MUTED, anchor="end"))
        if cap == 0.5:
            p.append(line(plot_x0 - 8, yy, plot_x1, yy, color=MUTED, sw=1.2, dash="6 5"))
    p.append(text(plot_x0 - 52, y_base - hmax / 2, "C", size=13, color=INK, bold=True))

    for ci, (vals, lab) in enumerate(cols):
        cx = plot_x0 + slot * ci + slot / 2
        k = len(vals)
        inner = slot - 44
        bw = min(30.0, inner / k - 6)
        # рівномірно рознесені стовпчики
        gap = (inner - k * bw) / (k + 1)
        x = cx - inner / 2 + gap
        for v in vals:
            good = v > 0.5 + 1e-9
            mid = abs(v - 0.5) < 1e-9
            fill = "#eef1f4" if mid else (GOODF if good else BADF)
            strk = MUTED if mid else (GOODS if good else BADS)
            top = y_base - v * hmax
            p.append(rect(x, top, bw, v * hmax, fill=fill, stroke=strk, sw=1.8, rx=3))
            if k <= 2:      # числа лише там, де не тісно
                p.append(text(x + bw / 2, top - 8, "%.2f" % v, size=11, color=strk, bold=True))
            x += bw + gap
        p.append(text(cx, y_base + 24, lab, size=13, color=INK, bold=True))

    # стрілка «до полюсів»
    p.append(text(W / 2, y_base + 52, "з кожним рівнем розкол чіткішає — до полюсів 0 і 1",
                  size=12.5, color=INK, italic=True))

    # легенда
    ly = 92
    p.append(rect(560, ly - 11, 20, 20, fill=GOODF, stroke=GOODS, sw=1.8, rx=3))
    p.append(text(588, ly + 4, "під дані (C > 0.5)", size=12, color=INK, anchor="start"))
    p.append(rect(560, ly + 17, 20, 20, fill=BADF, stroke=BADS, sw=1.8, rx=3))
    p.append(text(588, ly + 32, "заморозити (C < 0.5)", size=12, color=INK, anchor="start"))

    render(os.path.join(OUT, "polarize.svg"), W, H, *p,
           title="Поляризаційний каскад: пропускна перетікає до країв")


# ── frozen: розподіл каналів на дані й заморожені ─────────────────────────────

def fig_frozen():
    W, H = 840, 470
    p = []

    rel = [0.0039, 0.1211, 0.1914, 0.3164, 0.6836, 0.8086, 0.8789, 0.9961]  # відсортовано
    K = 4                       # праві 4 (найнадійніші) — дані
    n = len(rel)

    x0, x1 = 96, 792
    y_base = 300
    hmax = 190.0
    slot = (x1 - x0) / n
    bw = 46

    # вісь
    p.append(line(x0 - 6, y_base, x1, y_base, color=INK, sw=1.8))
    p.append(mtext(x0 - 46, y_base - hmax / 2 - 6, ["надій-", "ність"], size=11.5, color=INK))

    # поріг між позиціями (n-K) та (n-K+1)
    cut = x0 + slot * (n - K)
    p.append(line(cut, y_base - hmax - 16, cut, y_base + 92, color=INK, sw=1.8, dash="6 5"))

    data_idx = list(range(n - K, n))
    d = 0
    for i, v in enumerate(rel):
        cx = x0 + slot * i + slot / 2
        is_data = i in data_idx
        fill = GOODF if is_data else BADF
        strk = GOODS if is_data else BADS
        top = y_base - v * hmax
        p.append(rect(cx - bw / 2, top, bw, v * hmax, fill=fill, stroke=strk, sw=2.0, rx=3))
        p.append(text(cx, top - 9, "%.2f" % v, size=10.5, color=strk, bold=True))
        # смужка бітового вектора під віссю
        cy = y_base + 22
        p.append(rect(cx - bw / 2, cy, bw, 34, fill=fill, stroke=strk, sw=1.8, rx=4))
        if is_data:
            d += 1
            p.append(text(cx, cy + 23, "d%d" % d, size=13, color=strk, bold=True))
        else:
            p.append(text(cx, cy + 23, "0", size=14, color=strk, bold=True))

    p.append(text((x0 + cut) / 2, y_base - hmax - 30, "4 найгірші → заморозити в 0",
                  size=12, color=BADS, bold=True))
    p.append(text((cut + x1) / 2, y_base - hmax - 30, "4 найкращі → біти даних",
                  size=12, color=GOODS, bold=True))

    box, bwd, bhd = textbox(W / 2, 430,
                            "швидкість  R = K/N = 4/8 = 0.5  =  C каналу зі стиранням p=0.5",
                            size=13.5, bold=True, fill="#f6f4ec", stroke=INK, sw=1.8, pad=12)
    p.append(box)

    render(os.path.join(OUT, "frozen.svg"), W, H, *p,
           title="Дані — на надійні канали, нуль — на решту")


# ── ceiling: дві стелі — C Шеннона і бар'єр R₀ (для hist-вставки) ─────────────

def fig_ceiling():
    W, H = 880, 470
    p = []

    bx0, bx1 = 112, 214           # вертикальна «колонка швидкості»
    y_C, y_0 = 96, 412            # верх = C, низ = 0
    y_R0 = y_0 - 0.55 * (y_0 - y_C)   # рівень R₀

    # колонка: зелена практична зона (під R₀) і червоний провал (R₀…C)
    p.append(rect(bx0, y_R0, bx1 - bx0, y_0 - y_R0, fill=GOODF, stroke=GOODS, sw=2.0, rx=4))
    p.append(rect(bx0, y_C, bx1 - bx0, y_R0 - y_C, fill=BADF, stroke=BADS, sw=2.0, rx=4))

    # ліва вісь із позначками 0 · R₀ · C
    p.append(line(bx0 - 8, y_0, bx0 - 8, y_C, color=INK, sw=1.8))
    for yy, lab, col in ((y_0, "0", MUTED), (y_R0, "R₀", BADS), (y_C, "C", INK)):
        p.append(line(bx0 - 12, yy, bx0 - 8, yy, color=INK, sw=1.6))
        p.append(text(bx0 - 20, yy + 5, lab, size=14, color=col, anchor="end", bold=(lab != "0")))
    # пунктир стелі Шеннона
    p.append(line(bx0 - 8, y_C, bx1 + 8, y_C, color=INK, sw=1.4, dash="6 5"))

    # стрілка «поляризація підіймає R₀ до C»
    p.append(arrow(bx1 + 26, y_R0, bx1 + 26, y_C + 4, color=GOODS, sw=2.6))
    p.append(mtext(bx1 + 40, (y_C + y_R0) / 2 - 4, ["полярний", "код"],
                   size=12, color=GOODS, anchor="start", bold=True))

    # праві пояснення
    b1, _, _ = textbox(636, y_C + 4,
                       "C — стеля Шеннона (1948):\nскільки взагалі можна передати",
                       size=13, bold=True, fill="#f2f6ff", stroke=INK, sw=1.6, pad=11)
    p.append(b1)
    b2, _, _ = textbox(636, (y_C + y_R0) / 2 + 4,
                       "провал: теорія дозволяє —\nскладність декодера ні\n(≈30 років практика жила під R₀)",
                       size=13, bold=True, fill=BADF, stroke=BADS, sw=1.8, pad=11)
    p.append(b2)
    b3, _, _ = textbox(636, y_R0 + 6,
                       "R₀ — обчислювальна стеля\nпослідовного декодування",
                       size=13, bold=True, fill=FILL, stroke=INK, sw=1.6, pad=11)
    p.append(b3)
    b4, _, _ = textbox(636, (y_R0 + y_0) / 2 + 6,
                       "практична зона:\nдекодер устигав рахувати",
                       size=13, bold=True, fill=GOODF, stroke=GOODS, sw=1.8, pad=11)
    p.append(b4)

    render(os.path.join(OUT, "ceiling.svg"), W, H, *p,
           title="Дві стелі: межа Шеннона C і бар'єр обчислення R₀")


# ── timeline: шлях від межі Шеннона до 5G (для hist-вставки) ──────────────────

def fig_timeline():
    W, H = 900, 668
    p = []

    sx = 248                       # хребет
    ys = [96, 166, 236, 306, 376, 446, 516, 600]
    p.append(line(sx, ys[0] - 22, sx, ys[-1] + 22, color=INK, sw=2.2))

    rows = [
        ("1948", "Шеннон: у каналі є межа C — але не рецепт, як її сягнути", INK),
        ("1960-ті", "Возенкрафт, Фано: послідовне декодування; постає бар'єр R₀", INK),
        ("1960–80-ті", "Пінскер, потім Мессі: R₀ можна підняти, розщепивши канал", INK),
        ("1986", "Арікан захищає в MIT дисертацію (послідовне декодування) — у Р. Галлагера", INK),
        ("2006", "Стаття про комбінування й розщеплення каналів заради R₀", INK),
        ("2008–09", "«Channel Polarization…»: перший ДОВЕДЕНО capacity-achieving код", FIELD),
        ("2016", "3GPP (Рено): полярний код — у канал керування 5G", FIELD),
        ("2018 · 19", "Медаль Геммінга, потім премія Шеннона", FIELD),
    ]

    for (yr, desc, col), y in zip(rows, ys):
        big = col == FIELD
        p.append(circle(sx, y, 9 if big else 6.5,
                        fill=(GOODF if big else BG), stroke=(GOODS if big else INK), sw=2.4))
        p.append(text(sx - 26, y + 5, yr, size=14, color=col, anchor="end", bold=big))
        p.append(fitbox(sx + 22, y - 24, 592, 48, desc, size=15, pad=10,
                        fill=(GOODF if big else FILL),
                        stroke=(GOODS if big else LINE), sw=(2.0 if big else 1.4),
                        color=INK, bold=big))

    render(os.path.join(OUT, "timeline.svg"), W, H, *p,
           title="Шістдесят років до полярних кодів — і десять до 5G")


# ── sc_tree: SC-декодер як рекурсивне дерево (f ліворуч, g праворуч) ──────────

def fig_sc_tree():
    W, H = 900, 566
    p = []

    xs = [78, 180, 282, 384, 486, 588, 690, 792]      # 8 листків
    y_leaf, y_n2, y_n4, y_root = 430, 322, 214, 116

    n2x = [(xs[0] + xs[1]) / 2, (xs[2] + xs[3]) / 2,
           (xs[4] + xs[5]) / 2, (xs[6] + xs[7]) / 2]
    n4x = [(n2x[0] + n2x[1]) / 2, (n2x[2] + n2x[3]) / 2]
    rootx = (n4x[0] + n4x[1]) / 2

    frozen = {0, 1, 2, 4}
    decided = {0: 0, 1: 0, 2: 0, 3: 1, 4: 0, 5: 0, 6: 1, 7: 1}
    sub = "₀₁₂₃₄₅₆₇"

    import math

    def edge(x1, y1, x2, y2, lab):
        sx, sy, ex, ey = x1, y1 + 15, x2, y2 - 17
        mx, my = (sx + ex) / 2, (sy + ey) / 2
        dx, dy = ex - sx, ey - sy
        L = math.hypot(dx, dy) or 1.0
        ux, uy, gap = dx / L, dy / L, 15
        p.append(line(sx, sy, mx - ux * gap, my - uy * gap, color=LINE, sw=1.6))
        p.append(line(mx + ux * gap, my + uy * gap, ex, ey, color=LINE, sw=1.6))
        col = NEG if lab == "f" else FIELD
        fillc = "#eaf0fd" if lab == "f" else GOODF
        p.append(circle(mx, my, 12, fill=fillc, stroke=col, sw=2.0))
        p.append(text(mx, my + 5, lab, size=13, color=col, bold=True, italic=True))

    # корінь
    p.append(circle(rootx, y_root, 16, fill=FILL, stroke=INK, sw=2.0))
    p.append(text(rootx, y_root + 5, "N=8", size=12, color=INK, bold=True))
    edge(rootx, y_root, n4x[0], y_n4, "f")
    edge(rootx, y_root, n4x[1], y_n4, "g")
    # N=4
    for j, nx in enumerate(n4x):
        p.append(circle(nx, y_n4, 15, fill=FILL, stroke=INK, sw=1.8))
        p.append(text(nx, y_n4 + 4, "N=4", size=11, color=INK, bold=True))
        edge(nx, y_n4, n2x[2 * j], y_n2, "f")
        edge(nx, y_n4, n2x[2 * j + 1], y_n2, "g")
    # N=2
    for j, nx in enumerate(n2x):
        p.append(circle(nx, y_n2, 14, fill=FILL, stroke=INK, sw=1.8))
        p.append(text(nx, y_n2 + 4, "N=2", size=10.5, color=INK, bold=True))
        edge(nx, y_n2, xs[2 * j], y_leaf, "f")
        edge(nx, y_n2, xs[2 * j + 1], y_leaf, "g")
    # листки
    bw = bh = 54
    for i, x in enumerate(xs):
        fr = i in frozen
        fill, strk = (BADF, BADS) if fr else (GOODF, GOODS)
        p.append(rect(x - bw / 2, y_leaf, bw, bh, fill=fill, stroke=strk, sw=2.2, rx=8))
        p.append(text(x, y_leaf - 9, "u" + sub[i], size=13, color=INK, bold=True))
        p.append(text(x, y_leaf + 26, str(decided[i]), size=21, color=strk, bold=True))
        p.append(text(x, y_leaf + 45, "заморож." if fr else "дані", size=9.5, color=strk))

    # бічні стрілки: довіра вниз, біти вгору
    p.append(arrow(38, y_root, 38, y_leaf, color=NEG, sw=2.2))
    p.append(mtext(22, (y_root + y_leaf) / 2, ["LLR", "вниз"], size=11, color=NEG, bold=True))
    p.append(arrow(W - 38, y_leaf, W - 38, y_root, color=FIELD, sw=2.2))
    p.append(mtext(W - 22, (y_root + y_leaf) / 2, ["біти", "вгору"], size=11, color=FIELD, bold=True))

    p.append(text(W / 2, y_leaf + bh + 40,
                  "обхід зліва направо: у кожному вузлі спершу f (ліворуч), потім g (праворуч, уже знаючи ліве)",
                  size=12, color=INK, italic=True))
    render(os.path.join(OUT, "sc-tree.svg"), W, H, *p,
           title="SC-декодер: рекурсивне дерево — f ліворуч, g праворуч")


# ── fg_nodes: дві операції декодера — f (boxplus) і g (сума) ──────────────────

def fig_fg_nodes():
    W, H = 900, 452
    p = []
    p.append(line(W / 2, 58, W / 2, H - 26, color=MUTED, sw=1.2, dash="5 6"))

    # --- f: верхня гілка ---
    fx = 230
    p.append(text(fx, 78, "f — верхня гілка: обережна", size=14.5, color=NEG, bold=True))
    p.append(text(fx, 104, "напр.  f(−4, 5) = −·min(4,5) = −4", size=11.5, color=MUTED, italic=True))
    for lx, lab in ((fx - 72, "L₁"), (fx + 72, "L₂")):
        p.append(circle(lx, 150, 21, fill=FILL, stroke=INK, sw=1.8))
        p.append(text(lx, 156, lab, size=14, color=INK, bold=True))
        p.append(line(lx, 171, fx + (14 if lx < fx else -14), 214, color=LINE, sw=1.8))
    p.append(circle(fx, 234, 31, fill="#eaf0fd", stroke=NEG, sw=2.5))
    p.append(text(fx, 242, "f", size=24, color=NEG, bold=True, italic=True))
    p.append(arrow(fx, 266, fx, 312, color=NEG, sw=2.0))
    box, _, _ = textbox(fx, 342, "sgn L₁ · sgn L₂ · min(|L₁|, |L₂|)",
                        size=13.5, bold=True, fill="#eaf0fd", stroke=NEG, sw=1.8, pad=11)
    p.append(box)
    p.append(fitbox(fx - 156, 378, 312, 50,
                    "знак = XOR знаків · впевненість = МЕНША з двох\n(ланцюг рветься по слабшій ланці)",
                    size=11.5, pad=8, fill=BG, stroke=MUTED, sw=1.2, color=MUTED))

    # --- g: нижня гілка ---
    gx = 668
    p.append(text(gx, 78, "g — нижня гілка: упевнена", size=14.5, color=FIELD, bold=True))
    p.append(text(gx, 104, "напр.  g(−4, 5, û=1) = 5 + (−1)(−4) = 9", size=11.5, color=MUTED, italic=True))
    for lx, lab in ((gx - 74, "L₁"), (gx + 30, "L₂")):
        p.append(circle(lx, 150, 21, fill=FILL, stroke=INK, sw=1.8))
        p.append(text(lx, 156, lab, size=14, color=INK, bold=True))
        p.append(line(lx, 171, gx - 30 + (14 if lx < gx - 30 else -14), 214, color=LINE, sw=1.8))
    # û — уже вирішений верхній біт
    p.append(circle(gx + 104, 156, 18, fill=GOODF, stroke=GOODS, sw=2.2))
    p.append(text(gx + 104, 162, "û", size=15, color=GOODS, bold=True))
    p.append(text(gx + 104, 128, "рішення", size=10, color=GOODS))
    p.append(line(gx + 90, 168, gx - 6, 216, color=GOODS, sw=1.8, dash="4 4"))
    p.append(circle(gx - 30, 234, 31, fill=GOODF, stroke=FIELD, sw=2.5))
    p.append(text(gx - 30, 242, "g", size=24, color=FIELD, bold=True, italic=True))
    p.append(arrow(gx - 30, 266, gx - 30, 312, color=FIELD, sw=2.0))
    box2, _, _ = textbox(gx, 342, "L₂ + (1 − 2û) · L₁",
                         size=13.5, bold=True, fill=GOODF, stroke=FIELD, sw=1.8, pad=11)
    p.append(box2)
    p.append(fitbox(gx - 156, 378, 312, 50,
                    "û=0 → L₁+L₂ · û=1 → L₂−L₁\nдокази ДОДАЮТЬСЯ → сигнал міцнішає",
                    size=11.5, pad=8, fill=BG, stroke=MUTED, sw=1.2, color=MUTED))

    render(os.path.join(OUT, "fg-nodes.svg"), W, H, *p,
           title="Дві операції SC: f поєднує обережно, g додає впевнено")


# ── zmap: мапа рекурсії Z (для math-вставки) ──────────────────────────────────

def fig_zmap():
    W, H = 880, 500
    p = []

    gx0, gx1 = 122, 548
    gy0, gy1 = 410, 104          # значення 0 (низ) .. 1 (верх)

    def X(z):
        return gx0 + z * (gx1 - gx0)

    def Y(v):
        return gy0 + v * (gy1 - gy0)

    # осі
    p.append(line(gx0, gy0, gx1 + 8, gy0, color=INK, sw=1.8))
    p.append(line(gx0, gy0, gx0, gy1 - 8, color=INK, sw=1.8))
    for z, lab in ((0, "0"), (0.5, "0.5"), (1, "1")):
        p.append(line(X(z), gy0, X(z), gy0 + 6, color=INK, sw=1.4))
        p.append(text(X(z), gy0 + 23, lab, size=12, color=MUTED))
    for v, lab in ((0.25, "0.25"), (0.5, "0.5"), (0.75, "0.75"), (1, "1")):
        p.append(line(gx0 - 6, Y(v), gx0, Y(v), color=INK, sw=1.4))
        p.append(text(gx0 - 12, Y(v) + 4, lab, size=11, color=MUTED, anchor="end"))
    p.append(text((gx0 + gx1) / 2, gy0 + 46, "вхідне  Z  (ненадійність каналу)", size=12.5, color=INK))
    p.append(text(gx0, gy1 - 22, "Z дітей", size=12, color=INK, bold=True))

    # діагональ — без змін
    p.append(line(X(0), Y(0), X(1), Y(1), color=MUTED, sw=1.5, dash="6 5"))

    def poly(f, color, sw=2.8):
        pts = " ".join("%.1f,%.1f" % (X(i / 120.0), Y(f(i / 120.0))) for i in range(121))
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
                'stroke-linejoin="round" stroke-linecap="round"/>' % (pts, color, sw))
    p.append(poly(lambda z: 2 * z - z * z, POS))    # Z⁻ — над діагоналлю
    p.append(poly(lambda z: z * z, FIELD))          # Z⁺ — під діагоналлю

    # розкол входу Z = 0.5 → діти 0.25 і 0.75
    z0 = 0.5
    p.append(line(X(z0), Y(0), X(z0), Y(0.75), color=INK, sw=1.1, dash="3 4"))
    for v, col in ((0.75, POS), (0.25, FIELD)):
        p.append(line(gx0, Y(v), X(z0), Y(v), color=col, sw=1.0, dash="3 4"))
        p.append(circle(X(z0), Y(v), 6, fill=BG, stroke=col, sw=2.6))
    p.append(circle(X(z0), Y(0.5), 4.5, fill=INK, stroke=INK, sw=1))

    # нерухомі точки — полюси
    p.append(circle(X(0), Y(0), 6.5, fill=FIELD, stroke=FIELD, sw=2))
    p.append(circle(X(1), Y(1), 6.5, fill=POS, stroke=POS, sw=2))
    p.append(text(X(0) + 12, Y(0) - 12, "полюс 0", size=11, color=FIELD, anchor="start", bold=True))
    p.append(text(X(1) - 8, Y(1) + 21, "полюс 1", size=11, color=POS, anchor="end", bold=True))

    # права панель: легенда + пояснення
    lx = 600
    p.append(line(lx, 150, lx + 34, 150, color=FIELD, sw=3))
    p.append(text(lx + 44, 154, "Z⁺ = Z²   (кращий → 0)", size=12.5, color=INK, anchor="start"))
    p.append(line(lx, 182, lx + 34, 182, color=POS, sw=3))
    p.append(text(lx + 44, 186, "Z⁻ = 2Z − Z²   (гірший → 1)", size=12.5, color=INK, anchor="start"))
    p.append(line(lx, 214, lx + 34, 214, color=MUTED, sw=2, dash="6 5"))
    p.append(text(lx + 44, 218, "Z   (без змін)", size=12.5, color=INK, anchor="start"))

    box, _, _ = textbox(lx + 116, 328,
                        "Полюси 0 і 1 — нерухомі:\nусі криві сходяться там.\nСередина відштовхує —\nдіти далі від 0.5, ніж Z.",
                        size=12.5, fill=FILL, stroke=INK, sw=1.5, pad=12)
    p.append(box)

    render(os.path.join(OUT, "zmap.svg"), W, H, *p,
           title="Мапа рекурсії Z: середину відштовхує, полюси притягують")


# ── zflee: розліт значень Z до полюсів (для math-вставки) ─────────────────────

def fig_zflee():
    W, H = 900, 548
    p = []

    def kids(zs):
        out = []
        for z in zs:
            out.append(z * z)          # W⁺
            out.append(2 * z - z * z)  # W⁻
        return out
    levels = [[0.5]]
    while len(levels) <= 6:
        levels.append(kids(levels[-1]))
    cols = levels[1:7]                  # N = 2, 4, 8, 16, 32, 64

    gx0, gx1 = 158, 858
    yb, yt = 438, 96                   # Z = 0 внизу, Z = 1 вгорі

    def Y(z):
        return yb + z * (yt - yb)
    slot = (gx1 - gx0) / len(cols)

    # вісь Z
    p.append(line(gx0 - 10, yb, gx0 - 10, yt, color=INK, sw=1.8))
    for z, lab in ((0, "0"), (0.5, "0.5"), (1, "1")):
        p.append(line(gx0 - 14, Y(z), gx0 - 10, Y(z), color=INK, sw=1.4))
        p.append(text(gx0 - 20, Y(z) + 4, lab, size=11.5, color=MUTED, anchor="end"))
    p.append(text(gx0 - 46, (yb + yt) / 2 + 4, "Z", size=14, color=INK, bold=True))

    # межа 0.5
    p.append(line(gx0 - 10, Y(0.5), gx1, Y(0.5), color=MUTED, sw=1.1, dash="6 5"))

    for ci, vals in enumerate(cols):
        cx = gx0 + slot * ci + slot / 2
        k = len(vals)
        r = 3.2 if k <= 16 else (2.6 if k <= 32 else 2.1)
        for j, z in enumerate(sorted(vals)):
            good = z < 0.5 - 1e-9
            col = FIELD if good else (POS if z > 0.5 + 1e-9 else MUTED)
            jit = ((j * 53) % 31 - 15) / 15.0 * (slot * 0.30)   # розкид по горизонталі
            p.append(circle(cx + jit, Y(z), r, fill=col, stroke=col, sw=1))
        p.append(text(cx, yb + 26, "N=%d" % (2 ** (ci + 1)), size=12.5, color=INK, bold=True))

    # підписи полюсів
    b1, _, _ = textbox((gx0 + gx1) / 2, yt - 32,
                       "Z → 1 : непридатні канали (майбутні заморожені)",
                       size=12.5, bold=True, fill=BADF, stroke=BADS, sw=1.6, pad=9)
    p.append(b1)
    b2, _, _ = textbox((gx0 + gx1) / 2, 512,
                       "Z → 0 : досконалі канали · їхня частка → C = 0.5",
                       size=12.5, bold=True, fill=GOODF, stroke=GOODS, sw=1.6, pad=9)
    p.append(b2)

    render(os.path.join(OUT, "zflee.svg"), W, H, *p,
           title="Розліт Z до полюсів: чим довший блок, то порожніша середина")


if __name__ == "__main__":
    fig_transform()
    fig_polarize()
    fig_frozen()
    fig_ceiling()
    fig_timeline()
    fig_sc_tree()
    fig_fg_nodes()
    fig_zmap()
    fig_zflee()
    print("OK: figures written to", OUT)
