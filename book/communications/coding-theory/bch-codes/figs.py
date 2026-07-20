# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GFILL = "#eafaf0"; GSTRK = FIELD          # поле / замовлені корені (зелене)
BFILL = "#eef4ff"; BSTRK = "#2457d6"      # многочлени / локатор (синє)
RFILL = "#fdecea"; RSTRK = POS            # прийняте з помилкою (червоне)
GOLD  = "#b7791f"; SFILL = "#f6f4ec"      # синдроми / підсумок
GRAY  = "#c8ccd2"

_SUP = {"0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
        "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹"}


def a(n):
    """α у степені n з юнікод-надрядковим показником: a(12) -> 'α¹²'."""
    return "α" + "".join(_SUP[d] for d in str(n))


# ── Fig 1: замовлені корені — 2t сусідніх степенів α ───────────────────────────
def fig_designed_roots():
    W, H = 1000, 270
    n = 15
    t = 2
    designed = set(range(1, 2 * t + 1))          # α¹ … α⁴

    p = []
    r = 20
    pitch = 60
    x0 = 70
    cy = 150

    # брекет над замовленими коренями
    lo = x0 + 1 * pitch
    hi = x0 + (2 * t) * pitch
    by = cy - r - 22
    p.append(line(lo - r, by, hi + r, by, color=GSTRK, sw=2.2))
    p.append(line(lo - r, by, lo - r, by + 14, color=GSTRK, sw=2.2))
    p.append(line(hi + r, by, hi + r, by + 14, color=GSTRK, sw=2.2))
    p.append(mtext((lo + hi) / 2, by - 30, ["2t = 4 сусідні степені", "тут кожне слово = 0"],
                   size=13, color=GSTRK, bold=True, lh=1.25))

    # ряд вузлів α⁰ … α¹⁴
    for i in range(n):
        x = x0 + i * pitch
        if i in designed:
            fill, strk, tc = GFILL, GSTRK, FIELD
        elif i == 0:
            fill, strk, tc = BG, GRAY, MUTED
        else:
            fill, strk, tc = FILL, GRAY, MUTED
        p.append(circle(x, cy, r, fill=fill, stroke=strk, sw=2.4 if i in designed else 1.4))
        p.append(text(x, cy + 5, a(i), size=12.5, color=tc, bold=i in designed))

    p.append(text(x0, cy + r + 22, "старт із α¹", size=10.5, color=MUTED))

    # висновок
    box, bw, bh = textbox(W / 2, cy + r + 52,
                          "занулення у 2t точках  →  d ≥ 2t+1 = 5  →  код виправляє t = 2 помилки",
                          size=14, bold=True, fill=SFILL, stroke=INK, sw=2, pad=12)
    p.append(box)

    render(os.path.join(OUT, "designed-roots.svg"), W, H, *p,
           title="Замовлені корені: кожне кодове слово = 0 у 2t сусідніх степенях α")


# ── Fig 2: 2t коренів → лише t мінімальних многочленів (квадрати задарма) ──────
def fig_gen_poly():
    W, H = 940, 440
    p = []

    chips = [1, 2, 3, 4]                  # замовлені корені α¹…α⁴
    dest  = {1: "m1", 2: "m1", 3: "m3", 4: "m1"}
    chip_cx = {1: 250, 2: 390, 3: 530, 4: 670}
    chip_y = 74
    cw, chh = 66, 40

    p.append(text(W / 2, 52, "замовлені корені для t = 2:", size=13, color=INK, bold=True))

    # чипи коренів (колір за призначенням)
    for k in chips:
        cx = chip_cx[k]
        strk = GSTRK if dest[k] == "m1" else BSTRK
        fill = GFILL if dest[k] == "m1" else BFILL
        p.append(rect(cx - cw / 2, chip_y, cw, chh, fill=fill, stroke=strk, sw=2.0, rx=6))
        p.append(text(cx, chip_y + chh / 2 + 5, a(k), size=15,
                      color=strk, bold=True))
    # позначки «квадрат — задарма»
    p.append(text(chip_cx[2], chip_y + chh + 15, "= (α¹)²", size=10.5, color=MUTED))
    p.append(text(chip_cx[4], chip_y + chh + 15, "= (α²)²", size=10.5, color=MUTED))

    # два мінімальні многочлени
    m1_cx, m3_cx, my = 320, 690, 232
    b1 = fitbox(m1_cx - 160, my - 32, 320, 64,
                ["m₁(x) = x⁴+x+1", "вбирає корені: α¹, α², α⁴, α⁸"],
                size=13.5, fill=GFILL, stroke=GSTRK, sw=2.0, bold=True)
    b3 = fitbox(m3_cx - 150, my - 32, 300, 64,
                ["m₃(x) = x⁴+x³+x²+x+1", "вбирає корені: α³, α⁶, α⁹, α¹²"],
                size=13.5, fill=BFILL, stroke=BSTRK, sw=2.0, bold=True)
    p.append(b1)
    p.append(b3)

    # стрілки чип → многочлен (колір за призначенням)
    for k in chips:
        cx = chip_cx[k]
        if dest[k] == "m1":
            tx, col = m1_cx + (cx - m1_cx) * 0.24, GSTRK
        else:
            tx, col = m3_cx + (cx - m3_cx) * 0.24, BSTRK
        p.append(arrow(cx, chip_y + chh + 20, tx, my - 34, color=col, sw=1.6))

    # добуток g(x)
    gx = fitbox(W / 2 - 300, 344, 600, 66,
                ["g(x) = m₁(x) · m₃(x) = x⁸+x⁷+x⁶+x⁴+1   (степінь 8)",
                 "надлишок n − k = 8   →   BCH(15, 7), виправляє 2 помилки"],
                size=14, fill=SFILL, stroke=INK, sw=2.2, bold=True)
    p.append(gx)
    p.append(arrow(m1_cx, my + 34, W / 2 - 80, 342, color=LINE, sw=1.8))
    p.append(arrow(m3_cx, my + 34, W / 2 + 80, 342, color=LINE, sw=1.8))

    render(os.path.join(OUT, "gen-poly.svg"), W, H, *p,
           title="Квадрати задарма: 2t коренів коштують лише ~t многочленів")


# ── Fig 3: декодування трьома кроками ─────────────────────────────────────────
def fig_decode():
    W, H = 1160, 300
    p = []
    cy = 150
    bw = 156
    m = 28
    step = (W - 2 * m - 5 * bw) / 4 + bw     # відстань між центрами
    cx0 = m + bw / 2
    centers = [cx0 + i * step for i in range(5)]

    boxes = [
        (["прийняте", "r(x)"], RFILL, RSTRK),
        (["синдроми", "S₁ … S₂ₜ"], SFILL, GOLD),
        (["локатор", "σ(x)"], BFILL, BSTRK),
        (["позиції", "битих бітів"], BFILL, BSTRK),
        (["виправлене", "c(x)"], GFILL, GSTRK),
    ]
    for cx, (label, fill, strk) in zip(centers, boxes):
        p.append(fitbox(cx - bw / 2, cy - 30, bw, 60, label,
                        size=14, fill=fill, stroke=strk, sw=2.0, bold=True))

    labels = [
        ["підставити", "α¹ … α²ᵗ"],
        ["Берлекамп–", "Мессі"],
        ["корені σ:", "перебір Ч'єна"],
        ["перевернути", "ті біти"],
    ]
    for i in range(4):
        x1 = centers[i] + bw / 2 + 4
        x2 = centers[i + 1] - bw / 2 - 4
        p.append(arrow(x1, cy, x2, cy, color=LINE, sw=2.0))
        p.append(mtext((x1 + x2) / 2, cy - 30, labels[i], size=10.5,
                       color=INK, lh=1.2, bold=True))

    # гілка «чисто»
    p.append(text(centers[1], cy + 44, "усі Sⱼ = 0  →  помилки немає",
                  size=11, color=MUTED, italic=True))

    p.append(text(W / 2, cy + 96,
                  "синдроми залежать лише від помилки — тому декодер знаходить і лагодить до t збоїв",
                  size=13, color=INK, bold=True))

    render(os.path.join(OUT, "decode.svg"), W, H, *p,
           title="Декодування BCH: синдроми → локатор → позиції → перевернути біти")


# ── Fig 4 (proj): систематичний кодер як регістр зсуву — ділення на g(x) ───────
def fig_lfsr_encoder():
    W, H = 1080, 360
    p = []
    cy = 205          # ряд комірок регістра
    y_rail = 96       # верхня шина зворотного зв'язку
    cw, ch = 60, 54
    pitch = 116
    x0 = 128          # ліва грань b0
    n = 8
    cell_left = [x0 + i * pitch for i in range(n)]
    cell_cx = [cl + cw / 2 for cl in cell_left]

    taps = {4, 6, 7}                       # XOR перед b4, b6, b7 (ненульові g4,g6,g7)
    gate_r = 14

    # заголовок-підказка над схемою
    p.append(text(W / 2, 56, "g(x) = x⁸+x⁷+x⁶+x⁴+1   →   відводи там, де коефіцієнт = 1",
                  size=13.5, color=INK, bold=True))

    # вхідний XOR (data_in ⊕ зворотний зв'язок)
    in_gx = x0 - 58
    # комірки регістра b0..b7
    for i in range(n):
        p.append(rect(cell_left[i], cy - ch / 2, cw, ch, fill=BFILL, stroke=BSTRK, sw=2.0, rx=7))
        p.append(text(cell_cx[i], cy + 6, "b%d" % i, size=15, color=BSTRK, bold=True))

    # стрілки зсуву між комірками (b_i -> b_{i+1})
    for i in range(n - 1):
        x1 = cell_left[i] + cw
        x2 = cell_left[i + 1]
        midx = (x1 + x2) / 2
        if (i + 1) in taps:
            # XOR-гейт на цьому проводі
            p.append(arrow(x1, cy, midx - gate_r, cy, color=LINE, sw=1.8))
            p.append(plus(midx, cy, r=gate_r))
            p.append(arrow(midx + gate_r, cy, x2, cy, color=LINE, sw=1.8))
        else:
            p.append(arrow(x1, cy, x2, cy, color=LINE, sw=1.8))

    # вхід -> XOR -> b0
    p.append(plus(in_gx, cy, r=gate_r))
    p.append(arrow(in_gx - 66, cy, in_gx - gate_r, cy, color=LINE, sw=1.8))
    p.append(text(in_gx - 66, cy - 16, "дані", size=12, color=INK, bold=True, anchor="start"))
    p.append(arrow(in_gx + gate_r, cy, cell_left[0], cy, color=LINE, sw=1.8))

    # вихід b7 (остача -> контрольні біти)
    out_x = cell_left[n - 1] + cw
    p.append(line(out_x, cy, out_x + 30, cy, color=LINE, sw=1.8))

    # шина зворотного зв'язку: від виходу b7 вгору, вліво по y_rail, вниз у кожен відвід
    fb_x_right = out_x + 30
    p.append(line(fb_x_right, cy, fb_x_right, y_rail, color=RSTRK, sw=2.0))
    p.append(line(in_gx, y_rail, fb_x_right, y_rail, color=RSTRK, sw=2.0))
    # дроп у вхідний XOR
    p.append(arrow(in_gx, y_rail, in_gx, cy - gate_r, color=RSTRK, sw=2.0))
    # дропи у відводи
    for i in taps:
        gx = (cell_left[i - 1] + cw + cell_left[i]) / 2
        p.append(arrow(gx, y_rail, gx, cy - gate_r, color=RSTRK, sw=2.0))
    p.append(text(fb_x_right + 8, (cy + y_rail) / 2, "зв.зв.", size=11, color=RSTRK,
                  bold=True, anchor="start"))

    # підпис-висновок
    box, bw, bh = textbox(W / 2, cy + ch / 2 + 62,
                          "після k тактів вкинутих даних у регістрі лежить остача r(x) = m(x)·x⁸ mod g(x) — це і є 8 контрольних бітів",
                          size=13, bold=True, fill=SFILL, stroke=INK, sw=2, pad=11)
    p.append(box)

    render(os.path.join(OUT, "lfsr-encoder.svg"), W, H, *p,
           title="Систематичний кодер BCH(15,7): ділення на g(x) регістром зсуву")


# ── Fig 5 (hist): вертикальний таймлайн — теорема, потім декодер ───────────────
def fig_hist_timeline():
    W, H = 820, 660
    p = []
    ax = 250                                  # вертикальна вісь
    y0, stepy = 90, 70

    rows = [
        (1948, ["Шеннон: надійні коди існують,", "але не сказано, як їх будувати"], "ctx"),
        (1950, ["Гемінг: код на одну", "помилку в слові"], "ctx"),
        (1959, ["Окенгем · Chiffres (Франція):", "перша конструкція на t помилок"], "disc"),
        (1960, ["Бозе й Рей-Чоудхурі · Information and Control", "(США): те саме, незалежно"], "disc"),
        (1960, ["Пітерсон: перший декодер —", "лінійна алгебра, ціна ~t³"], "dec"),
        (1964, ["Ч'єн: швидкий перебір", "коренів локатора"], "dec"),
        (1968, ["Берлекамп: ітеративний", "декодер, ціна падає до ~t²"], "dec"),
        (1969, ["Мессі: регістр зсуву →", "Берлекамп–Мессі"], "dec"),
    ]
    style = {
        "ctx":  (BG,    GRAY,  MUTED, FILL,  GRAY),
        "disc": (GFILL, GSTRK, FIELD, GFILL, GSTRK),
        "dec":  (SFILL, GOLD,  GOLD,  SFILL, GOLD),
    }

    # вісь
    p.append(line(ax, y0 - 16, ax, y0 + (len(rows) - 1) * stepy + 16, color=GRAY, sw=2.2))

    for i, (yr, label, cat) in enumerate(rows):
        y = y0 + i * stepy
        ndf, nds, ycol, bxf, bxs = style[cat]
        p.append(text(ax - 26, y + 5, str(yr), size=15, color=ycol, bold=True, anchor="end"))
        p.append(circle(ax, y, 10, fill=ndf, stroke=nds, sw=2.6))
        p.append(fitbox(ax + 24, y - 26, 490, 52, label,
                        size=13.5, fill=bxf, stroke=bxs, sw=1.8, bold=True))

    # легенда
    ly = y0 + (len(rows) - 1) * stepy + 44
    lx = 250
    for fill, strk, lab in [(GFILL, GSTRK, "відкриття (теорема)"),
                            (SFILL, GOLD, "декодер (практика)")]:
        p.append(circle(lx, ly, 8, fill=fill, stroke=strk, sw=2.2))
        p.append(text(lx + 16, ly + 5, lab, size=12.5, color=INK, anchor="start"))
        lx += 250

    render(os.path.join(OUT, "hist-timeline.svg"), W, H, *p,
           title="Дві половини історії BCH: спершу теорема, потім робочий декодер")


# ── Fig 6 (hist): той самий код двома незалежними дорогами ─────────────────────
def fig_hist_two_roads():
    W, H = 1080, 430
    p = []
    lx, rx = 250, 830
    cbx = 540

    # верхні вузли-автори
    p.append(fitbox(lx - 165, 58, 330, 56, ["Алексіс Окенгем", "Франція · 1959"],
                    size=15, fill=GFILL, stroke=GSTRK, sw=2.0, bold=True))
    p.append(fitbox(rx - 175, 58, 350, 56, ["Бозе й Рей-Чоудхурі", "США · 1960"],
                    size=15, fill=GFILL, stroke=GSTRK, sw=2.0, bold=True))

    # «дороги» — з якого боку прийшли
    p.append(fitbox(lx - 175, 150, 350, 78,
                    ["дорога алгебри:", "многочлени й корені,", "циклічні коди"],
                    size=13, fill=BFILL, stroke=BSTRK, sw=1.8, bold=True))
    p.append(fitbox(rx - 185, 150, 370, 78,
                    ["дорога комбінаторики:", "плани, латинські квадрати,", "скінченні геометрії"],
                    size=13, fill=BFILL, stroke=BSTRK, sw=1.8, bold=True))
    p.append(arrow(lx, 116, lx, 148, color=LINE, sw=1.6))
    p.append(arrow(rx, 116, rx, 148, color=LINE, sw=1.6))

    # підсумкова рамка внизу
    p.append(fitbox(cbx - 280, 322, 560, 82,
                    ["ТОЙ САМИЙ КЛАС КОДІВ", "корені g(x) — у 2t сусідніх степенях α",
                     "→ коди BCH"],
                    size=14.5, fill=SFILL, stroke=INK, sw=2.2, bold=True))
    p.append(arrow(lx, 230, cbx - 150, 320, color=LINE, sw=2.0))
    p.append(arrow(rx, 230, cbx + 150, 320, color=LINE, sw=2.0))

    p.append(text(W / 2, 288, "жоден не знав про роботу іншого — різниця близько року",
                  size=12.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "hist-two-roads.svg"), W, H, *p,
           title="Той самий код, дві незалежні дороги")


# ── Fig 7 (math): межа BCH через визначник Вандермонда ─────────────────────────
def fig_bch_bound():
    W, H = 980, 430
    p = []

    # матриця Вандермонда V у квадратних дужках
    bx1, bx2 = 92, 432
    ytop, ybot = 76, 272
    for bxx, dirn in [(bx1, 1), (bx2, -1)]:
        p.append(line(bxx, ytop, bxx, ybot, color=INK, sw=2.2))
        p.append(line(bxx, ytop, bxx + 10 * dirn, ytop, color=INK, sw=2.2))
        p.append(line(bxx, ybot, bxx + 10 * dirn, ybot, color=INK, sw=2.2))
    p.append(text(52, (ytop + ybot) / 2 + 6, "V =", size=17, color=INK, bold=True))

    cols = [150, 224, 300, 374]
    rows = [108, 152, 196, 240]
    entries = [
        ["1",   "1",   "1",   "1"],
        ["X₁",  "X₂",  "X₃",  "X₄"],
        ["X₁²", "X₂²", "X₃²", "X₄²"],
        ["X₁³", "X₂³", "X₃³", "X₄³"],
    ]
    for r, ry in enumerate(rows):
        for c, cx in enumerate(cols):
            p.append(text(cx, ry + 5, entries[r][c], size=15,
                          color=INK if r == 0 else FIELD, bold=True))
    p.append(text((bx1 + bx2) / 2, ybot + 22,
                  "стовпці — різні локатори Xₗ   ·   рядки — степені 0…w−1",
                  size=11, color=MUTED))

    # формула визначника
    p.append(fitbox(470, 84, 478, 104,
                    ["det V = ∏ (Xⱼ − Xᵢ),   i < j",
                     "= (X₂−X₁)(X₃−X₁)(X₄−X₁)",
                     "     ·(X₃−X₂)(X₄−X₂)(X₄−X₃)"],
                    size=15, fill=BFILL, stroke=BSTRK, sw=2.0, bold=True))

    # чому ненульовий
    p.append(fitbox(470, 200, 478, 72,
                    ["вузли Xₗ різні  ⟹  кожна різниця ≠ 0",
                     "GF(2ᵐ) без дільників нуля  ⟹  det V ≠ 0"],
                    size=13.5, fill=GFILL, stroke=GSTRK, sw=1.8, bold=True))

    # підсумковий банер
    box, bw, bh = textbox(W / 2, 352,
                          ["det ≠ 0   ⟹   однорідна система  M·c = 0  має лише  c = 0",
                           "легкого ненульового слова (вага ≤ 2t) нема   ⟹   d ≥ 2t+1"],
                          size=15, bold=True, fill=SFILL, stroke=INK, sw=2.2, pad=14)
    p.append(box)

    render(os.path.join(OUT, "bch-bound.svg"), W, H, *p,
           title="Чому 2t сусідніх коренів дають d ≥ 2t+1: визначник Вандермонда ≠ 0")


if __name__ == "__main__":
    fig_designed_roots()
    fig_gen_poly()
    fig_decode()
    fig_lfsr_encoder()
    fig_hist_timeline()
    fig_hist_two_roads()
    fig_bch_bound()
    print("OK: figures written to", OUT)
