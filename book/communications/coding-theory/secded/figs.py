# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

PFILL = "#eef4ff"   # парність Геммінга
PSTRK = "#2457d6"
DFILL = "#eafaf0"   # дані
DSTRK = "#27ae60"
OFILL = "#fdf0dd"   # загальна парність / нічия земля
OSTRK = "#c77d00"
REDF  = "#fdecea"


# ── decision: дві відповіді → чотири вироки ───────────────────────────────────
def fig_decision():
    W, H = 820, 470
    p = []
    gx, gy = 252, 134
    cw, ch, gap = 268, 150, 16
    col_c = [gx + cw / 2, gx + cw + gap + cw / 2]
    row_c = [gy + ch / 2, gy + ch + gap + ch / 2]

    # шапка стовпців — синдром
    p.append(text((col_c[0] + col_c[1]) / 2, gy - 48, "СИНДРОМ ГЕММІНГА", size=12, color=MUTED, bold=True))
    p.append(text(col_c[0], gy - 22, "синдром = 0", size=15, color=INK, bold=True))
    p.append(text(col_c[1], gy - 22, "синдром ≠ 0", size=15, color=INK, bold=True))

    # підписи рядків — загальна парність
    p.append(mtext(gx - 24, row_c[0] - 4, ["загальна парність", "СХОДИТЬСЯ"], size=13, color=INK, anchor="end", bold=True))
    p.append(mtext(gx - 24, row_c[1] - 4, ["загальна парність", "ПОРУШЕНА"], size=13, color=INK, anchor="end", bold=True))

    def cell(c, r, s, fill, stroke):
        x = gx + c * (cw + gap)
        y = gy + r * (ch + gap)
        p.append(fitbox(x, y, cw, ch, s, size=15, pad=16, fill=fill, stroke=stroke, sw=2.4, color=INK, bold=True))

    cell(0, 0, "помилок немає\nслово ціле", DFILL, FIELD)
    cell(1, 0, "ДВІ помилки\nвиправити НЕ можна\n— бити тривогу", REDF, POS)
    cell(0, 1, "збій самого біта\nзагальної парності\n— дані цілі", "#eaf0fd", NEG)
    cell(1, 1, "ОДНА помилка\nсиндром = адреса\n— перевернути біт", "#eaf0fd", NEG)

    # кутові теги SEC / DED
    p.append(text(col_c[1], row_c[0] + ch / 2 - 14, "DED — лише виявлення", size=10.5, color=POS, italic=True))
    p.append(text(col_c[1], row_c[1] + ch / 2 - 14, "SEC — виправлення", size=10.5, color=NEG, italic=True))

    render(os.path.join(OUT, "decision.svg"), W, H, *p,
           title="Таблиця рішень SECDED: дві відповіді дають чотири вироки")


# ── distance: чому d=4 ловить подвійну, а d=3 тихо бреше ──────────────────────
def fig_distance():
    W, H = 860, 470
    p = []
    X0, STEP = 200, 138
    def px(pos):
        return X0 + pos * STEP

    def draw_row(y, dmin, bpos, landing_zone, verdict, verdict_col, rowlabel):
        # осьова лінія
        left = px(0) - 0.5 * STEP
        right = px(bpos) + 0.5 * STEP
        # кулі виправлення (радіус 1) навколо A(0) і B(bpos)
        mid = (px(1) + px(bpos - 1)) / 2  # межа/центр між кулями
        # A-куля: pos -.. 1 ; B-куля: pos bpos-1 .. bpos+..
        aL, aR = left, px(1) + 0.5 * STEP
        bL, bR = px(bpos - 1) - 0.5 * STEP, right
        p.append(rect(aL, y - 26, aR - aL, 52, fill=DFILL, stroke=FIELD, sw=1.6, rx=10))
        p.append(rect(bL, y - 26, bR - bL, 52, fill=DFILL, stroke=FIELD, sw=1.6, rx=10))
        if landing_zone == "gap":
            # нічия земля між кулями (d=4)
            p.append(rect(aR + 3, y - 26, bL - aR - 6, 52, fill=OFILL, stroke=OSTRK, sw=1.6, rx=10))
        # осьова
        p.append(line(left - 6, y, right + 6, y, color=MUTED, sw=1.4))
        # позначки позицій
        for pos in range(0, bpos + 1):
            p.append(line(px(pos), y - 5, px(pos), y + 5, color=MUTED, sw=1.2))
        # кодові слова A, B
        for pos, lab in [(0, "A"), (bpos, "B")]:
            p.append(circle(px(pos), y, 15, fill=FIELD, stroke=INK, sw=1.6))
            p.append(text(px(pos), y + 5, lab, size=15, color="#ffffff", bold=True))
        # «дві помилки = 2 кроки» — пунктир від A до місця приземлення (pos 2)
        land = px(2)
        p.append(line(px(0), y - 40, land, y - 40, color=verdict_col, sw=2.0, dash="5,4"))
        p.append(text((px(0) + land) / 2, y - 48, "дві помилки = 2 кроки", size=11, color=verdict_col, bold=True))
        # маркер приземлення
        p.append(circle(land, y, 11, fill=REDF if verdict_col == POS else OFILL, stroke=verdict_col, sw=2.4))
        p.append(text(land, y + 4.5, "2", size=12, color=verdict_col, bold=True))
        # вирок під віссю
        p.append(text(land, y + 44, verdict, size=12, color=verdict_col, bold=True))
        # підпис рядка ліворуч
        p.append(mtext(60, y - 6, rowlabel, size=13, color=INK, anchor="start", bold=True))

    draw_row(150, 3, 3, "kiss", "тихо виправлено НЕ ТУДИ → у чуже слово B", POS, ["d = 3", "голий Геммінг"])
    draw_row(345, 4, 4, "gap", "нічия земля: видно, але не виправити", OSTRK, ["d = 4", "SECDED"])

    render(os.path.join(OUT, "distance.svg"), W, H, *p,
           title="Один зайвий біт розсуває слова: d=3 бреше, d=4 ловить подвійну помилку")


# ── word: будова SECDED-слова (8,4) = Геммінг (7,4) + загальна парність ───────
def fig_word():
    W, H = 780, 300
    p = []
    n = 7
    cw, ch = 76, 58
    gap8 = 14
    x0 = (W - (8 * cw + gap8)) / 2
    top = 132

    names = {1: "P1", 2: "P2", 4: "P4", 3: "D1", 5: "D2", 6: "D3", 7: "D4"}
    par = {1, 2, 4}
    cx = {}
    for i in range(1, n + 1):
        x = x0 + (i - 1) * cw
        cx[i] = x + cw / 2
        isp = i in par
        p.append(rect(x, top, cw, ch, fill=PFILL if isp else DFILL,
                      stroke=PSTRK if isp else DSTRK, sw=2.0, rx=6))
        p.append(text(x + cw / 2, top + ch / 2 + 5, names[i], size=16,
                      color=PSTRK if isp else DSTRK, bold=True))
        p.append(text(x + cw / 2, top - 12, "поз. %d" % i, size=11, color=MUTED))

    # восьма клітинка — загальна парність, із зазором
    x8 = x0 + n * cw + gap8
    cx8 = x8 + cw / 2
    p.append(rect(x8, top, cw, ch, fill=OFILL, stroke=OSTRK, sw=2.4, rx=6))
    p.append(text(cx8, top + ch / 2 + 5, "P₀", size=16, color=OSTRK, bold=True))
    p.append(text(cx8, top - 12, "поз. 8", size=11, color=MUTED))

    # дужка над клітинками 1..7
    bx1, bx2 = x0, x0 + n * cw
    by = top - 34
    p.append(line(bx1, by, bx2, by, color=PSTRK, sw=2.0))
    p.append(line(bx1, by, bx1, by + 8, color=PSTRK, sw=2.0))
    p.append(line(bx2, by, bx2, by + 8, color=PSTRK, sw=2.0))
    p.append(text((bx1 + bx2) / 2, by - 8, "код Геммінга (7,4): синдром називає адресу битого біта",
                  size=12, color=PSTRK, bold=True))

    # стрілка від дужки до P0
    p.append(arrow(bx2 + 4, by + 2, cx8 - 4, top - 6, color=OSTRK, sw=2.0))
    p.append(text(cx8 + 40, by + 6, "XOR усіх семи", size=11, color=OSTRK, bold=True, anchor="start"))

    # підписи знизу
    p.append(text(W / 2, top + ch + 30,
                  "P₀ — загальна парність: робить кількість одиниць у слові парною",
                  size=12.5, color=INK, bold=True))
    p.append(text(W / 2, top + ch + 54,
                  "у пам'яті — те саме, лише (72,64): 64 біти даних + 8 контрольних",
                  size=11.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "word.svg"), W, H, *p,
           title="Будова SECDED-слова: код Геммінга плюс один біт на все слово")


# ── hsiao-rows: вага рядків H — де саме сидить вузьке місце ───────────────────
def fig_hsiao_rows():
    W, H = 940, 630
    p = []
    base = 400          # лінія основи стовпчиків
    unit = 2.55         # px на одиницю ваги рядка
    bw, gap = 30, 8
    span = 8 * bw + 7 * gap

    def panel(x0, title, subtitle, weights, labels, fills, strokes, total, worst, note, note_col):
        p.append(text(x0 + span / 2, 60, title, size=15, color=INK, bold=True))
        p.append(text(x0 + span / 2, 82, subtitle, size=11.5, color=MUTED, italic=True))
        # основа
        p.append(line(x0 - 12, base, x0 + span + 12, base, color=MUTED, sw=1.4))
        for i, w in enumerate(weights):
            x = x0 + i * (bw + gap)
            h = w * unit
            p.append(rect(x, base - h, bw, h, fill=fills[i], stroke=strokes[i], sw=2.0, rx=4))
            p.append(text(x + bw / 2, base - h - 9, str(w), size=12, color=strokes[i], bold=True))
            p.append(text(x + bw / 2, base + 18, labels[i], size=10.5, color=MUTED))
        p.append(text(x0 + span / 2, base + 46, "рядки перевірочної матриці H", size=11, color=MUTED, italic=True))
        p.append(text(x0 + span / 2, base + 80, "найдовший рядок: %d" % worst, size=13.5, color=note_col, bold=True))
        p.append(text(x0 + span / 2, base + 102, "усього одиниць: %d" % total, size=12.5, color=INK))
        p.append(text(x0 + span / 2, base + 128, note, size=11.5, color=note_col, italic=True))

    # ліворуч — розширений Геммінг: сім рядків Геммінга + рядок із самих одиниць
    lx = 78
    hw = [36, 36, 36, 32, 32, 32, 8, 72]
    hl = ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"]
    hf = [PFILL] * 7 + [REDF]
    hs = [PSTRK] * 7 + [POS]
    panel(lx, "розширений Геммінг (72,64)", "сім рядків Геммінга + рядок загальної парності",
          hw, hl, hf, hs, 284, 72, "4 рівні XOR — і так на кожному записі", POS)

    # маркер вузького місця
    spike_x = lx + 7 * (bw + gap) + bw / 2
    p.append(arrow(spike_x + 62, base - 72 * unit - 44, spike_x + 6, base - 72 * unit - 10, color=POS, sw=2.0))
    p.append(mtext(spike_x + 70, base - 72 * unit - 58, ["рядок із самих одиниць:", "XOR усього слова"],
                   size=11.5, color=POS, anchor="start", bold=True))

    # праворуч — код Сяо: усі рядки рівні
    rx = 545
    xw = [27] * 8
    xl = ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"]
    xf = [DFILL] * 8
    xs = [DSTRK] * 8
    panel(rx, "код Сяо (72,64)", "усі стовпці непарної ваги, робота розкладена порівну",
          xw, xl, xf, xs, 216, 27, "3 рівні XOR — вузького місця немає", DSTRK)

    # пунктир рівня 27 через ліву панель — видно, наскільки Геммінг вищий
    p.append(line(lx - 12, base - 27 * unit, lx + span + 12, base - 27 * unit,
                  color=DSTRK, sw=1.4, dash="5,4"))
    p.append(text(lx - 18, base - 27 * unit + 4, "27", size=11, color=DSTRK, anchor="end", bold=True))

    p.append(text(W / 2, 572, "27 = 3³ — рівно три яруси тривходових XOR, без жодного змарнованого входу",
                  size=12, color=INK, bold=True))
    p.append(text(W / 2, 596, "той самий бюджет: 64 біти даних, 8 контрольних, d = 4",
                  size=11.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "hsiao-rows.svg"), W, H, *p,
           title="Вага рядків H: у Геммінга один рядок гальмує все, у Сяо робота розкладена порівну")


# ── hsiao-columns: звідки беруться 72 непарні стовпці ─────────────────────────
def fig_hsiao_columns():
    W, H = 900, 470
    p = []

    # приклад стовпця: вісім клітинок, непарне число одиниць
    cx0, cy0 = 62, 118
    cell = 26
    demo = [1, 0, 1, 0, 0, 1, 0, 0]   # вага 3
    p.append(text(cx0 + cell / 2, cy0 - 40, "стовпець", size=12, color=INK, bold=True))
    p.append(text(cx0 + cell / 2, cy0 - 22, "8 рядків", size=10.5, color=MUTED))
    for i, b in enumerate(demo):
        y = cy0 + i * cell
        p.append(rect(cx0, y, cell, cell, fill=DFILL if b else FILL,
                      stroke=DSTRK if b else "#cbd5e1", sw=1.6, rx=3))
        if b:
            p.append(circle(cx0 + cell / 2, y + cell / 2, 5, fill=DSTRK, stroke=DSTRK, sw=1))
    p.append(mtext(cx0 + cell / 2, cy0 + 8 * cell + 22, ["вага 3 —", "непарна ✓"],
                   size=11.5, color=DSTRK, bold=True))

    # полиця наявних стовпців
    gx, gy = 190, 130
    bw2, bh2, g2 = 148, 92, 18
    groups = [
        ("вага 1", "C(8,1) = 8", 8, 8, "усі 8 — під контрольні біти", DFILL, DSTRK),
        ("вага 3", "C(8,3) = 56", 56, 56, "усі 56 — під дані", DFILL, DSTRK),
        ("вага 5", "C(8,5) = 56", 56, 8, "беремо лише 8", OFILL, OSTRK),
        ("вага 7", "C(8,7) = 8", 8, 0, "не потрібні", FILL, "#94a3b8"),
    ]
    p.append(text(gx + (4 * bw2 + 3 * g2) / 2, gy - 62, "УСІ НЕПАРНІ СТОВПЦІ ВИСОТИ 8", size=12, color=MUTED, bold=True))
    p.append(text(gx + (4 * bw2 + 3 * g2) / 2, gy - 40, "8 + 56 + 56 + 8 = 128 = 2⁷ — вибирати є з чого",
                  size=12, color=INK, bold=True))
    for i, (nm, cnt, have, take, note, fill, stroke) in enumerate(groups):
        x = gx + i * (bw2 + g2)
        p.append(rect(x, gy, bw2, bh2, fill=fill, stroke=stroke, sw=2.0, rx=6))
        p.append(text(x + bw2 / 2, gy + 26, nm, size=14, color=stroke, bold=True))
        p.append(text(x + bw2 / 2, gy + 48, cnt, size=12, color=INK))
        p.append(text(x + bw2 / 2, gy + 72, note, size=10.5, color=MUTED, italic=True))
        if take:
            p.append(text(x + bw2 / 2, gy + bh2 + 30, "взято %d" % take, size=13, color=stroke, bold=True))
            p.append(arrow(x + bw2 / 2, gy + bh2 + 42, x + bw2 / 2, gy + bh2 + 66, color=stroke, sw=1.8))
        else:
            p.append(text(x + bw2 / 2, gy + bh2 + 30, "—", size=13, color="#94a3b8", bold=True))

    # підсумок
    sy = gy + bh2 + 78
    p.append(fitbox(gx, sy, 4 * bw2 + 3 * g2, 66,
                    "8 + 56 + 8 = 72 стовпці   ·   1·8 + 3·56 + 5·8 = 216 одиниць   ·   216 / 8 = 27 на рядок",
                    size=14, pad=14, fill="#eaf0fd", stroke=NEG, sw=2.4, color=INK, bold=True))

    p.append(text(W / 2, sy + 108,
                  "жоден стовпець не нульовий і не повторюється → d = 3; усі непарної ваги → d = 4",
                  size=12, color=INK, bold=True))
    p.append(text(W / 2, sy + 132,
                  "сума непарного числа непарних стовпців — завжди непарна, тож трьом нізащо не дати нуль",
                  size=11.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "hsiao-columns.svg"), W, H, *p,
           title="Звідки беруться 72 непарні стовпці коду Сяо (72,64)")


# ── budget: як діляться d−1 кроків між виправленням і виявленням ──────────────
def fig_budget():
    W, H = 900, 440
    p = []
    X0, STEP = 178, 136
    def px(i):
        return X0 + i * STEP          # 178, 314, 450, 586, 722
    Y = 214
    aR = (px(1) + px(2)) / 2          # межа кулі A
    bL = (px(2) + px(3)) / 2          # межа кулі B
    left, right = px(0) - 52, px(4) + 52

    # дужка «d(A,B) = 4»
    p.append(text(450, 92, "d(A, B) = 4 — найближча пара кодових слів", size=13, color=MUTED, bold=True))
    p.append(line(px(0), 110, px(4), 110, color=MUTED, sw=1.4))
    p.append(line(px(0), 110, px(0), 118, color=MUTED, sw=1.4))
    p.append(line(px(4), 110, px(4), 118, color=MUTED, sw=1.4))

    # зони: куля A · нічийна земля · куля B
    p.append(rect(left, Y - 30, aR - left, 60, fill=DFILL, stroke=FIELD, sw=1.8, rx=10))
    p.append(rect(aR + 5, Y - 30, bL - aR - 10, 60, fill=OFILL, stroke=OSTRK, sw=1.8, rx=10))
    p.append(rect(bL, Y - 30, right - bL, 60, fill=DFILL, stroke=FIELD, sw=1.8, rx=10))
    p.append(text((left + aR) / 2, 172, "куля A: радіус t = 1", size=12, color=FIELD, bold=True))
    p.append(text(450, 172, "нічийна земля", size=12, color=OSTRK, bold=True))
    p.append(text((bL + right) / 2, 172, "куля B: радіус t = 1", size=12, color=FIELD, bold=True))

    # вісь — сегментами між вузлами, щоб не різати написи
    for i in range(4):
        p.append(line(px(i) + 18, Y, px(i + 1) - 18, Y, color=MUTED, sw=1.4))
    p.append(line(left + 10, Y, px(0) - 18, Y, color=MUTED, sw=1.4))
    p.append(line(px(4) + 18, Y, right - 10, Y, color=MUTED, sw=1.4))

    for i, f, st in [(1, DFILL, FIELD), (2, OFILL, OSTRK), (3, REDF, POS)]:
        p.append(circle(px(i), Y, 12, fill=f, stroke=st, sw=2.4))
    for i, lab in [(0, "A"), (4, "B")]:
        p.append(circle(px(i), Y, 16, fill=FIELD, stroke=INK, sw=1.6))
        p.append(text(px(i), Y + 5.5, lab, size=15, color="#ffffff", bold=True))

    ecol = [MUTED, FIELD, OSTRK, POS, POS]
    for i in range(5):
        p.append(text(px(i), 266, "e = %d" % i, size=12, color=ecol[i], bold=True))

    verdicts = [
        (0, ["помилок немає", "слово ціле"], MUTED),
        (1, ["одна помилка", "виправлено ✓"], FIELD),
        (2, ["дві помилки", "тривога:", "видно, не правимо"], OSTRK),
        (3, ["три помилки", "тихо «полагоджено»", "у чуже слово B ✗"], POS),
        (4, ["чотири помилки", "прийнято за B ✗", "як за ціле слово"], POS),
    ]
    for i, lines, col in verdicts:
        p.append(mtext(px(i), 296, lines, size=12, color=col))

    # нижні дужки: чесна зона й перша брехня
    for x1, x2, col, lab, cx in [(px(0), px(2), OSTRK, "чесно: до s = 2 помилок", px(1)),
                                 (px(3), px(4), POS, "тиха брехня: e ≥ d − t = 3", (px(3) + px(4)) / 2)]:
        p.append(line(x1, 352, x2, 352, color=col, sw=1.8))
        p.append(line(x1, 344, x1, 352, color=col, sw=1.8))
        p.append(line(x2, 344, x2, 352, color=col, sw=1.8))
        p.append(text(cx, 372, lab, size=12, color=col, bold=True))

    p.append(text(450, 410, "t + s ≤ d − 1   →   1 + 2 = 3 = 4 − 1: бюджет вичерпано", size=13, color=INK, bold=True))

    render(os.path.join(OUT, "budget.svg"), W, H, *p,
           title="Бюджет d − 1: куди дівається кожен крок між двома кодовими словами")


# ── census: перепис простору — куди подіти відповідь «не знаю» ────────────────
def fig_census():
    W, H = 900, 400
    p = []
    x0, sc, bh = 186, 2.2, 48
    y1, y2 = 118, 232
    BLUF, BLUS = "#eaf0fd", NEG

    def bar(y, segs):
        x = x0
        for n, fill, stroke, lab in segs:
            w = n * sc
            p.append(rect(x, y, w, bh, fill=fill, stroke=stroke, sw=2.0, rx=5))
            if lab:
                p.append(text(x + w / 2, y + bh / 2 + 4.5, lab, size=12, color=stroke, bold=True))
            x += w

    p.append(mtext(x0 - 14, y1 + 18, ["Геммінг (7,4)", "усі 2⁷ = 128 слів"], size=12,
                   color=INK, anchor="end", bold=True))
    bar(y1, [(16, DFILL, DSTRK, ""), (112, BLUF, BLUS, "112 слів — крок 1 від коду")])
    p.append(text(x0, y1 + bh + 26,
                  "16 · (1 + 7) = 128 = 2⁷ — кулі покрили ВЕСЬ простір: вільного слова нема, сказати «не знаю» нічим",
                  size=11.5, color=INK, anchor="start"))

    p.append(mtext(x0 - 14, y2 + 18, ["розширений (8,4)", "усі 2⁸ = 256 слів"], size=12,
                   color=INK, anchor="end", bold=True))
    bar(y2, [(16, DFILL, DSTRK, ""), (128, BLUF, BLUS, "128 слів — крок 1 від коду"),
             (112, OFILL, OSTRK, "112 слів — нічийна земля")])
    p.append(text(x0, y2 + bh + 26,
                  "16 · (1 + 8) = 144 із 256 — восьмий біт подвоїв простір, а кодових слів ті самі 16: 112 лишилися вільні",
                  size=11.5, color=INK, anchor="start"))

    ly, lx = 348, 110
    for f, st, lab in [(DFILL, DSTRK, "16 кодових слів"),
                       (BLUF, BLUS, "виправні: крок 1 від коду"),
                       (OFILL, OSTRK, "нічийна земля: видно, та не виправно")]:
        p.append(rect(lx, ly - 12, 18, 18, fill=f, stroke=st, sw=2.0, rx=4))
        p.append(text(lx + 26, ly + 2, lab, size=12, color=INK, anchor="start"))
        lx += 26 + len(lab) * 12 * 0.57 + 34

    render(os.path.join(OUT, "census.svg"), W, H, *p,
           title="Перепис простору: восьмий біт купує місце для чесного «не знаю»")


# ── hmatrix: три маски — і чому синдром дорівнює номеру позиції ───────────────
def fig_hmatrix():
    W, H = 1000, 470
    p = []
    cols = [("1", "P1"), ("2", "P2"), ("3", "D1"), ("4", "P4"),
            ("5", "D2"), ("6", "D3"), ("7", "D4"), ("P0", "P0")]
    x0, y0 = 296, 118
    cw, ch = 66, 46

    # шапка: номер позиції і що в ній лежить
    p.append(text(x0 + 4 * cw, y0 - 66, "ПОЗИЦІЯ В СЛОВІ", size=12, color=MUTED, bold=True))
    for i, (num, nm) in enumerate(cols):
        cx = x0 + i * cw + cw / 2
        is_p0 = (num == "P0")
        p.append(text(cx, y0 - 42, num, size=15, color=OSTRK if is_p0 else INK, bold=True))
        p.append(text(cx, y0 - 21, nm, size=12,
                      color=OSTRK if is_p0 else (PSTRK if nm[0] == "P" else DSTRK)))

    rows = [("s₁ = XOR(w & 0x55)", 0x55, "1·3·5·7"),
            ("s₂ = XOR(w & 0x66)", 0x66, "2·3·6·7"),
            ("s₄ = XOR(w & 0x78)", 0x78, "4·5·6·7")]

    def draw_row(ry, label, mask, note, fill, stroke):
        p.append(text(x0 - 22, ry + ch / 2 + 5, label, size=13, color=INK, anchor="end", bold=True))
        for i in range(8):
            bit = (mask >> i) & 1
            x = x0 + i * cw
            p.append(rect(x, ry, cw, ch, fill=fill if bit else "#fbfbfc",
                          stroke=stroke if bit else "#d8dce2", sw=2.0 if bit else 1.0, rx=5))
            if bit:
                p.append(text(x + cw / 2, ry + ch / 2 + 6, "1", size=16, color=stroke, bold=True))
        p.append(text(x0 + 8 * cw + 20, ry + ch / 2 + 5, note, size=12, color=MUTED, anchor="start"))

    for k, (label, mask, note) in enumerate(rows):
        draw_row(y0 + k * ch, label, mask, note, PFILL, PSTRK)

    # окремо — перевірка загальної парності: закриває ВСІ вісім
    ry = y0 + 3 * ch + 16
    draw_row(ry, "p  = XOR(w & 0xFF)", 0xFF, "усі вісім", OFILL, OSTRK)

    # двійковий номер позиції під стовпцем
    by = ry + ch + 34
    p.append(text(x0 - 22, by + 4, "номер позиції у двійковій", size=12,
                  color=MUTED, anchor="end", italic=True))
    for i, (num, _) in enumerate(cols):
        cx = x0 + i * cw + cw / 2
        s = "—" if num == "P0" else format(i + 1, "03b")
        p.append(text(cx, by + 4, s, size=13, color=OSTRK if num == "P0" else NEG, bold=True))

    p.append(text(W / 2, by + 46,
                  "Стовпець, прочитаний ЗНИЗУ ВГОРУ (s₄ s₂ s₁), — це двійковий номер позиції.",
                  size=13.5, color=INK, bold=True))
    p.append(text(W / 2, by + 70,
                  "Позиція 5 = 101₂: закрита масками s₄ і s₁, не закрита s₂. Тому синдром і Є адреса — шукати нема чого.",
                  size=12, color=MUTED))

    render(os.path.join(OUT, "hmatrix.svg"), W, H, *p,
           title="Три маски — увесь кодек: 0x55, 0x66, 0x78")


# ── syndrome-space: у справжньому (72,64) вироків не чотири, а пʼять ──────────
def fig_syndrome_space():
    W, H = 1010, 560
    p = []
    gx, gy = 268, 150
    cw, ch, gap = 232, 132, 14
    col_c = [gx + i * (cw + gap) + cw / 2 for i in range(3)]
    row_c = [gy + i * (ch + gap) + ch / 2 for i in range(2)]

    p.append(text(gx + 1.5 * cw + gap, gy - 76, "СИНДРОМ: 7 бітів = 128 значень",
                  size=12, color=MUTED, bold=True))
    heads = [("нуль", "1 значення"),
             ("реальна позиція", "71 значення (1..71)"),
             ("НЕ ІСНУЄ такої позиції", "56 значень (72..127)")]
    for i, (a, b) in enumerate(heads):
        p.append(text(col_c[i], gy - 50, a, size=14, color=OSTRK if i == 2 else INK, bold=True))
        p.append(text(col_c[i], gy - 29, b, size=11.5, color=MUTED))

    p.append(mtext(gx - 26, row_c[0] - 4, ["загальна парність", "ПАРНА"],
                   size=13, color=INK, anchor="end", bold=True))
    p.append(mtext(gx - 26, row_c[1] - 4, ["загальна парність", "НЕПАРНА"],
                   size=13, color=INK, anchor="end", bold=True))

    def cell(c, r, s, fill, stroke):
        p.append(fitbox(gx + c * (cw + gap), gy + r * (ch + gap), cw, ch, s,
                        size=13.5, pad=14, fill=fill, stroke=stroke, sw=2.4, color=INK, bold=True))

    cell(0, 0, "NO_ERROR\nслово ціле", DFILL, FIELD)
    cell(1, 0, "DETECTED_DOUBLE\nдві помилки", REDF, POS)
    cell(2, 0, "DETECTED_DOUBLE\nбагатобітна", REDF, POS)
    cell(0, 1, "PARITY_BIT_ERROR\nзбій самого P0", "#eaf0fd", NEG)
    cell(1, 1, "CORRECTED_SINGLE\nсиндром = адреса", "#eaf0fd", NEG)
    cell(2, 1, "DETECTED_\nUNCORRECTABLE\nадреси НЕМА", OFILL, OSTRK)

    # виділити пʼятий вирок
    x2 = gx + 2 * (cw + gap)
    p.append(rect(x2 - 6, gy + ch + gap - 6, cw + 12, ch + 12,
                  fill="none", stroke=OSTRK, sw=3.0, rx=10))
    p.append(text(col_c[2], gy + 2 * ch + gap + 24, "◄ пʼятий вирок, якого нема у (8,4)",
                  size=12, color=OSTRK, bold=True))

    p.append(text(W / 2, H - 56,
                  "У навчальному (8,4) синдром має 3 біти й усі 7 ненульових значень — справжні позиції: третій стовпець порожній.",
                  size=12.5, color=INK))
    p.append(text(W / 2, H - 32,
                  "У (72,64) 56 зі 128 синдромів не вказують нікуди. Наївне «data ^= 1 << (s−1)» тут пише ПОЗА словом.",
                  size=12.5, color=POS, bold=True))

    render(os.path.join(OUT, "syndrome-space.svg"), W, H, *p,
           title="Справжній декодер (72,64): синдром має три класи, не два")


if __name__ == "__main__":
    fig_decision()
    fig_distance()
    fig_word()
    fig_hsiao_rows()
    fig_hsiao_columns()
    fig_budget()
    fig_census()
    fig_hmatrix()
    fig_syndrome_space()
    print("OK: figures written to", OUT)
