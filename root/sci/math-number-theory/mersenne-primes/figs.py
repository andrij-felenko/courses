# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GREENF = "#e6f6ec"
BLUEF  = "#eef3fc"
REDF   = "#fbeceb"
MUTEDL = "#9aa3ad"


# ── helper: рядок бітових клітинок ───────────────────────────────────────────
def bit_cells(x0, y0, bits, cw=46, gap=8, fills=None, size=22):
    """Малює клітинки з бітами; fills — список кольорів заливки по клітинках."""
    out = []
    for i, b in enumerate(bits):
        fx = fills[i] if fills else FILL
        cx = x0 + i * (cw + gap)
        out.append(rect(cx, y0, cw, cw, fill=fx, stroke=LINE, sw=1.5, rx=5))
        out.append(text(cx + cw / 2, y0 + cw / 2 + size * 0.35, b, size=size, bold=True))
    total_w = len(bits) * cw + (len(bits) - 1) * gap
    return "".join(out), total_w


def underbrace(x1, x2, y, label, color=FIELD, size=15):
    """Підкреслення-дужка від x1 до x2 на рівні y, з підписом під нею."""
    mid = (x1 + x2) / 2
    out = [
        line(x1, y, x2, y, color=color, sw=2.4),
        line(x1, y, x1, y - 8, color=color, sw=2.4),
        line(x2, y, x2, y - 8, color=color, sw=2.4),
        line(mid, y, mid, y + 8, color=color, sw=2.4),
        text(mid, y + 26, label, size=size, bold=True, color=color),
    ]
    return "".join(out)


def dot_triangle(cx, y0, n, rd=8, dx=26, dy=26, fill=FIELD):
    """Трикутник із крапок: рядок r (згори вниз) має r крапок, вирівняний по центру cx."""
    out = []
    for r in range(1, n + 1):
        row_w = (r - 1) * dx
        startx = cx - row_w / 2
        yy = y0 + (r - 1) * dy
        for c in range(r):
            out.append(circle(startx + c * dx, yy, rd, fill=fill, stroke=LINE, sw=1.2))
    return "".join(out)


# ── Фіг. 1: складений показник → стрічка одиниць ділиться на блоки ────────────
# Дві панелі: та сама 2⁶−1 = 111111, розбита на 2×3 (множник 7) і на 3×2 (множник 3).
def fig_blocks():
    W, H = 800, 430
    x0 = 60
    cw, gap = 46, 8
    step = cw + gap

    def panel(y_top, groups, blockval, product, tint):
        # groups: список списків індексів клітинок в одному блоці
        fills = [None] * 6
        for gi, g in enumerate(groups):
            c = GREENF if gi % 2 == 0 else BLUEF
            for idx in g:
                fills[idx] = c
        cells, tw = bit_cells(x0, y_top, "111111", cw, gap, fills)
        frag = [cells]
        # дужки під кожним блоком
        by = y_top + cw + 14
        for g in groups:
            gx1 = x0 + g[0] * step
            gx2 = x0 + g[-1] * step + cw
            frag.append(underbrace(gx1, gx2, by, blockval, color=FIELD))
        # підпис праворуч
        cap_x = x0 + tw + 70
        frag.append(text(cap_x, y_top + 6, product[0], size=16, bold=True, anchor="start"))
        frag.append(text(cap_x, y_top + 34, product[1], size=15, anchor="start", color=MUTED))
        frag.append(text(cap_x, y_top + 62, product[2], size=17, bold=True, anchor="start", color=POS))
        return "".join(frag)

    top_label = text(x0 + (6 * cw + 5 * gap) / 2, 58, "2⁶ − 1 = 111111₂ = 63", size=17, bold=True)

    pA = panel(84, [[0, 1, 2], [3, 4, 5]], "111₂ = 7",
               ("6 = 2 · 3", "спільний блок 2³ − 1 = 7", "63 = 7 · 9"), GREENF)
    pB = panel(268, [[0, 1], [2, 3], [4, 5]], "11₂ = 3",
               ("6 = 3 · 2", "спільний блок 2² − 1 = 3", "63 = 3 · 21"), BLUEF)

    render(os.path.join(OUT, "blocks.svg"), W, H,
           top_label, pA, pB,
           title="Складений показник → повторюваний блок → спільний множник")


# ── Фіг. 2: швидка остача згортанням за модулем 2ᵖ−1 ──────────────────────────
def fig_fold():
    W, H = 720, 470
    cx = W / 2

    frag = []
    # рядок бітів 92 = 1011100
    x0 = 190
    cells, tw = bit_cells(x0, 66, "1011100", 42, 8)
    frag.append(text(cx, 48, "92 = 1011100₂", size=17, bold=True))
    frag.append(cells)

    step = 42 + 8
    # дужки: групи трійок справа →  [1][011][100]
    by = 66 + 42 + 12
    # групи індексів: 0 | 1,2,3 | 4,5,6
    groups = [([0], "1"), ([1, 2, 3], "011 = 3"), ([4, 5, 6], "100 = 4")]
    for idxs, lbl in groups:
        gx1 = x0 + idxs[0] * step
        gx2 = x0 + idxs[-1] * step + 42
        frag.append(underbrace(gx1, gx2, by, lbl, color=FIELD, size=14))

    # додавання шматків
    frag.append(text(cx, 210, "1  +  3  +  4  =  8", size=18, bold=True))
    frag.append(text(cx, 236, "(2³ ≡ 1, тому кожна трійка бітів важить як її значення)",
                     size=12.5, color=MUTED))

    # другий виток згортання
    frag.append(line(120, 262, 600, 262, color=MUTEDL, sw=1, dash="4 4"))
    frag.append(text(cx, 292, "8 = 1000₂  →  1 | 000  →  1 + 0 = 1", size=17, bold=True))
    frag.append(text(cx, 320, "число ще зменшилося — згортаємо, доки лишиться остача",
                     size=12.5, color=MUTED))

    # результат
    body, bw, bh = textbox(cx, 386, "92 ≡ 1 (mod 7)", size=20, pad=16,
                           fill=GREENF, stroke=FIELD, color=INK, bold=True)
    frag.append(body)
    frag.append(text(cx, 430, "перевірка: 92 = 13 · 7 + 1 — жодного ділення, лише додавання",
                     size=12.5, color=MUTED))

    render(os.path.join(OUT, "fold.svg"), W, H, *frag,
           title="Остача за модулем 2ᵖ−1: різати на p-бітові шматки й додавати")


# ── Фіг. 3: зростання рекорду в часі (лог-шкала) ──────────────────────────────
def fig_growth():
    W, H = 800, 500
    L, R, T, B = 92, 748, 78, 410  # межі поля графіка
    y0, y1 = 1600, 2040
    lo, hi = 0.5, 8.5  # log10(p)

    def X(year):
        return L + (year - y0) / (y1 - y0) * (R - L)

    def Y(logp):
        return B - (logp - lo) / (hi - lo) * (B - T)

    frag = []

    # горизонтальні лінії сітки 10¹…10⁸
    for k in range(1, 9):
        yy = Y(k)
        frag.append(line(L, yy, R, yy, color="#e6e9ee", sw=1))
        sup = "¹²³⁴⁵⁶⁷⁸"[k - 1]
        frag.append(text(L - 12, yy + 4, "10" + sup, size=12.5, color=MUTED, anchor="end"))

    # осі
    frag.append(line(L, T, L, B, color=LINE, sw=1.8))
    frag.append(line(L, B, R, B, color=LINE, sw=1.8))
    for yr in (1600, 1700, 1800, 1900, 2000):
        xx = X(yr)
        frag.append(line(xx, B, xx, B + 6, color=LINE, sw=1.5))
        frag.append(text(xx, B + 24, str(yr), size=12.5, color=MUTED))
    frag.append(text((L + R) / 2, H - 18, "рік відкриття", size=13, color=MUTED))
    frag.append(text(L - 62, T - 26, "показник p", size=13, color=MUTED, anchor="start"))

    # межа ери машин (1952)
    xm = X(1952)
    frag.append(line(xm, T, xm, B, color=MUTEDL, sw=1.3, dash="5 5"))

    pts = [
        (1600, 19,        "Катальді"),
        (1772, 31,        None),
        (1876, 127,       "Люка 1876"),
        (1952, 2281,      "SWAC 1952"),
        (1996, 1398269,   None),
        (2008, 43112609,  None),
        (2024, 136279841, "2024"),
    ]
    coords = [(X(yr), Y(math.log10(p))) for yr, p, _ in pts]

    # лінія
    d = "M " + " L ".join("%.1f %.1f" % c for c in coords)
    frag.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, POS))
    # точки
    for (xx, yy), (_, _, lbl) in zip(coords, pts):
        frag.append(circle(xx, yy, 5.5, fill=POS, stroke=BG, sw=1.5))

    # підписи точок (розріджено, з відступом, щоб не налазили)
    frag.append(text(X(1600) + 10, Y(math.log10(19)) + 5, "Катальді ~1600", size=12.5,
                     anchor="start", color=INK))
    frag.append(text(X(1876) + 12, Y(math.log10(127)) + 4, "Люка 1876", size=12.5,
                     anchor="start", color=INK))
    frag.append(text(X(1952) + 12, Y(math.log10(2281)) + 4, "SWAC 1952", size=12.5,
                     anchor="start", color=INK))
    frag.append(text(X(2024) - 8, Y(math.log10(136279841)) - 12, "2024:  p ≈ 1.4·10⁸",
                     size=12.5, anchor="end", color=INK, bold=True))

    # анотації ер
    frag.append(text(X(1710), Y(6.6), "рахунок пером", size=14, bold=True, color=MUTED))
    frag.append(text(X(1710), Y(6.15), "століттями — сотні й тисячі", size=11.5, color=MUTED))
    frag.append(text(X(1998), Y(2.4), "машини й мережа GIMPS:", size=13.5, bold=True,
                     color=FIELD, anchor="middle"))
    frag.append(text(X(1998), Y(1.95), "рекорд злітає на 8 порядків", size=11.5,
                     color=FIELD, anchor="middle"))

    render(os.path.join(OUT, "growth.svg"), W, H, *frag,
           title="Показник найбільшого відомого простого Мерсенна в часі")


# ── Фіг. 4: список Мерсенна 1644 проти дійсності — п'ять помилок ───────────────
def fig_errors():
    W, H = 830, 560
    x0 = 46
    cols = [("p", 74), ("Мерсенн, 1644", 200), ("Насправді", 150), ("Хто й коли розсудив", 296)]
    xs = [x0]
    for _, w in cols:
        xs.append(xs[-1] + w)
    right = xs[-1]
    top = 108
    rh = 48

    frag = []
    frag.append(text(W / 2, 44, "Список Мерсенна 1644 року: одинадцять тверджень, п'ять помилок",
                     size=17, bold=True))
    frag.append(text(W / 2, 72, "для p ≤ 19 список безпомилковий — уся драма починається з 31;",
                     size=13, color=MUTED))
    frag.append(text(W / 2, 92, "«просте ✗» — назвав простим складене; «пропустив» — просте, якого в списку нема",
                     size=13, color=MUTED))

    # шапка
    frag.append(rect(x0, top, right - x0, rh, fill=FILL, stroke=LINE, sw=1.6, rx=7))
    for (name, w), xa in zip(cols, xs):
        frag.append(text(xa + w / 2, top + rh / 2 + 5, name, size=13.5, bold=True, color=INK))

    # рядки: (p, текст-Мерсенн, вид, текст-дійсність, вид-дійсність, суддя)
    rows = [
        ("31",  "просте ✓",  "ok",    "просте",   "prime", "Ейлер, 1772"),
        ("61",  "пропустив", "err",   "просте",   "prime", "Первушин, 1883"),
        ("67",  "просте ✗",  "err",   "складене", "comp",  "Люка 1876 · Коул 1903"),
        ("89",  "пропустив", "err",   "просте",   "prime", "Пауерс, 1911"),
        ("107", "пропустив", "err",   "просте",   "prime", "Пауерс, 1914"),
        ("127", "просте ✓",  "ok",    "просте",   "prime", "Люка, 1876"),
        ("257", "просте ✗",  "err",   "складене", "comp",  "Лемер, 1932"),
    ]

    y = top + rh
    for p, mtxt, mkind, rtxt, rkind, judge in rows:
        tint = REDF if mkind == "err" else GREENF
        frag.append(rect(x0, y, right - x0, rh, fill=tint, stroke=LINE, sw=1.2, rx=0))
        # p
        frag.append(text(xs[0] + cols[0][1] / 2, y + rh / 2 + 6, p, size=17, bold=True, color=INK))
        # Мерсенн
        mcol = POS if mkind == "err" else FIELD
        frag.append(text(xs[1] + cols[1][1] / 2, y + rh / 2 + 5, mtxt, size=14, bold=True, color=mcol))
        # Насправді
        rcol = FIELD if rkind == "prime" else MUTED
        frag.append(text(xs[2] + cols[2][1] / 2, y + rh / 2 + 5, rtxt, size=14, bold=(rkind == "prime"),
                         color=rcol))
        # суддя (ліворуч, з відступом)
        frag.append(text(xs[3] + 16, y + rh / 2 + 5, judge, size=13, anchor="start", color=INK))
        y += rh

    # вертикальні розділові лінії
    for xa in xs[1:-1]:
        frag.append(line(xa, top, xa, y, color=LINE, sw=1.2))
    frag.append(rect(x0, top, right - x0, y - top, fill="none", stroke=LINE, sw=1.6, rx=7))

    # підсумок унизу
    frag.append(text(W / 2, y + 34, "від першої поправки до останньої — 160 років",
                     size=13.5, bold=True, color=MUTED))

    render(os.path.join(OUT, "errors.svg"), W, H, *frag,
           title="Список Мерсенна проти дійсності: п'ять помилок і хто їх виправив")


# ── Фіг. 5: σ мультиплікативна — таблиця добутків дільників 28 = 4·7 ───────────
def fig_divgrid():
    W, H = 760, 500
    cellW, cellH = 104, 66
    ox, oy = 300, 156
    rows = [1, 2, 4]   # дільники 4
    cols = [1, 7]      # дільники 7

    frag = []

    # σ(7) над стовпцями
    frag.append(text(ox + cellW, oy - 54, "σ(7) = 1 + 7 = 8", size=15, bold=True, color=NEG))
    frag.append(line(ox + 8, oy - 44, ox + 2 * cellW - 8, oy - 44, color=NEG, sw=2))
    # шапка стовпців: множники (дільники 7)
    for j, e in enumerate(cols):
        frag.append(text(ox + j * cellW + cellW / 2, oy - 16, "× %d" % e,
                         size=17, bold=True, color=NEG))

    # σ(4) ліворуч
    frag.append(mtext(122, oy + cellH * 1.5 - 16,
                      ["дільники 4:", "1, 2, 4", "σ(4) = 7"],
                      size=14.5, color=FIELD, anchor="middle", bold=True))
    # шапка рядків: дільники 4
    for i, d in enumerate(rows):
        frag.append(text(ox - 24, oy + i * cellH + cellH / 2 + 6, "%d ·" % d,
                         size=17, bold=True, color=FIELD, anchor="end"))

    # клітинки-добутки
    for i, d in enumerate(rows):
        for j, e in enumerate(cols):
            x = ox + j * cellW
            y = oy + i * cellH
            tint = GREENF if (i + j) % 2 == 0 else BLUEF
            frag.append(rect(x, y, cellW, cellH, fill=tint, stroke=LINE, sw=1.4, rx=6))
            frag.append(text(x + cellW / 2, y + cellH / 2 + 7, str(d * e), size=21, bold=True))

    # рамка навколо всієї сітки добутків
    frag.append(rect(ox - 2, oy - 2, 2 * cellW + 4, 3 * cellH + 4,
                     fill="none", stroke=INK, sw=2.2, rx=8))

    gy_bot = oy + 3 * cellH
    body, bw, bh = textbox(ox + cellW, gy_bot + 62,
                           "усі шість дільників 28:  1 + 2 + 4 + 7 + 14 + 28 = 56\n"
                           "σ(28) = σ(4) · σ(7) = 7 · 8 = 56 = 2 · 28   →   28 досконале",
                           size=15, pad=15, fill=GREENF, stroke=FIELD, bold=False)
    frag.append(body)

    render(os.path.join(OUT, "divgrid.svg"), W, H, *frag,
           title="σ мультиплікативна: 28 = 4 · 7  →  σ(28) = σ(4) · σ(7)")


# ── Фіг. 6: кожне парне досконале число трикутне — N = q(q+1)/2 ────────────────
def fig_triangles():
    W, H = 780, 430
    frag = []

    # ліва: 6 = T₃
    frag.append(dot_triangle(190, 92, 3, rd=10, dx=32, dy=32, fill=GREENF))
    frag.append(text(190, 210, "6 = 1 + 2 + 3 = T₃", size=16, bold=True))
    frag.append(text(190, 234, "q = 3 = 2² − 1   (просте Мерсенна, p = 2)", size=12.5, color=MUTED))

    # права: 28 = T₇
    frag.append(dot_triangle(560, 82, 7, rd=8, dx=26, dy=26, fill=BLUEF))
    frag.append(text(560, 274, "28 = 1 + 2 + … + 7 = T₇", size=16, bold=True))
    frag.append(text(560, 298, "q = 7 = 2³ − 1   (просте Мерсенна, p = 3)", size=12.5, color=MUTED))

    # загальна формула
    body, bw, bh = textbox(W / 2, 366,
                           "N = 2ᵖ⁻¹(2ᵖ − 1) = q(q + 1)/2 ,    q = 2ᵖ − 1 — просте",
                           size=15.5, pad=14, fill=GREENF, stroke=FIELD, bold=True)
    frag.append(body)

    render(os.path.join(OUT, "triangles.svg"), W, H, *frag,
           title="Кожне парне досконале число трикутне: N = q(q+1)/2")


# ── Фіг. 7: форма дільника як сито — 4792 → 157 → 84 кандидати для M₃₁ ─────────
# Дві умови на дільник зрізають перебір: від усіх простих до кореня до 84 штук.
def fig_sieve():
    W, H = 780, 544
    cx = W / 2

    def band(y, w, desc, count, ccol, tint):
        x = cx - w / 2
        out = [rect(x, y, w, 70, fill=tint, stroke=LINE, sw=1.6, rx=10)]
        out.append(text(x + 24, y + 42, desc, size=15.5, anchor="start", bold=True, color=INK))
        out.append(text(x + w - 24, y + 46, str(count), size=30, anchor="end", bold=True, color=ccol))
        return "".join(out)

    def gate(yc, cond, why):
        body, bw, bh = textbox(cx, yc, cond, size=15, pad=12, fill=BG, stroke=FIELD,
                               sw=2, bold=True, color=FIELD)
        return body + text(cx, yc + 34, why, size=12.5, color=MUTED)

    frag = []
    frag.append(band(60, 620, "усі прості  q ≤ √M₃₁ ≈ 46 340", 4792, MUTED, FILL))
    frag.append(text(cx, 148, "▼", size=15, color=MUTEDL))
    frag.append(gate(178, "сито 1:   q ≡ 1  (mod 2p),   2p = 62",
                     "порядок двійки за модулем q дорівнює p, далі — мала теорема Ферма"))
    frag.append(band(232, 452, "прості  q ≡ 1  (mod 62)", 157, NEG, BLUEF))
    frag.append(text(cx, 320, "▼", size=15, color=MUTEDL))
    frag.append(gate(350, "сито 2:   q ≡ ±1  (mod 8)",
                     "з чотирьох класів {1, 63, 125, 187} лишаються два: {1, 63}"))
    frag.append(band(404, 400, "прості  q ≡ 1 або 63  (mod 248)", 84, FIELD, GREENF))

    body, bw, bh = textbox(cx, 502,
                           "84 пробні ділення пером — жодне не ділить  →  M₃₁ = 2³¹ − 1 просте",
                           size=14.5, pad=13, fill=GREENF, stroke=FIELD, sw=1.8, bold=True)
    frag.append(body)

    render(os.path.join(OUT, "sieve.svg"), W, H, *frag,
           title="Форма дільника як сито: 4792 → 157 → 84 кандидати (Ейлер, M₃₁)")


# ── Фіг. 8: анатомія одного кроку Люка–Лемера над великим числом ──────────────
# Конвеєр: sₖ (p біт) → квадрат (2p біт, найдорожче) → згортка (назад до p біт) → −2.
def fig_ll_step():
    W, H = 880, 566
    cx = W / 2
    bh = 48
    frag = []

    def bar(cy, wpx, main, fill, sub):
        x = cx - wpx / 2
        frag.append(fitbox(x, cy, wpx, bh, main, size=17, pad=10,
                           fill=fill, stroke=LINE, bold=True))
        frag.append(text(cx, cy + bh + 17, sub, size=12.5, color=MUTED))

    def op(y1, y2, lbl):
        frag.append(arrow(cx, y1, cx, y2, color=INK, sw=2.2))
        frag.append(text(cx + 26, (y1 + y2) / 2 + 4, lbl, size=13,
                         color=FIELD, anchor="start", bold=True))

    #                y    wpx  головний напис            заливка   підпис під смугою
    bar(74,  300, "sₖ  —  p бітів",     GREENF, "n = ⌈p/32⌉ слів по 32 біти")
    op(146, 196, "піднести до квадрата")
    bar(200, 600, "sₖ²  —  2p бітів",   REDF,   "2n слів · єдина по-справжньому дорога дія")
    op(272, 322, "згорнути:  верх + низ  (2ᵖ ≡ 1)")
    bar(326, 300, "остача  —  p бітів",  BLUEF,  "самі додавання · жодного ділення")
    op(398, 448, "− 2  (з поправкою, коли остача 0 чи 1)")
    bar(452, 300, "sₖ₊₁  —  p бітів",    GREENF, "готове до наступного з p − 2 кроків")

    # бічна примітка про особливий випадок — праворуч від смуги «остача»
    note, nw, nh = textbox(cx + 300, 349, "остача = Mₚ?\n(усі одиниці) → 0",
                           size=12.5, pad=10, fill=FILL, stroke=POS, color=INK, bold=True)
    frag.append(note)

    render(os.path.join(OUT, "ll-step.svg"), W, H, *frag,
           title="Один крок тесту Люка–Лемера: квадрат подвоює довжину, згортка стискає назад")


if __name__ == "__main__":
    fig_blocks()
    fig_fold()
    fig_growth()
    fig_errors()
    fig_divgrid()
    fig_triangles()
    fig_sieve()
    fig_ll_step()
    print("OK: blocks.svg, fold.svg, growth.svg, errors.svg, divgrid.svg, triangles.svg, sieve.svg, ll-step.svg")
