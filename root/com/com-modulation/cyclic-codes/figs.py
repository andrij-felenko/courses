# -*- coding: utf-8 -*-
"""Фігури до статті «Циклічні коди». Запуск із теки теми: python figs.py
Виводить SVG у ./img/. Використовує спільний svgkit зі scripts/."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

ONE = "#d7f0e0"   # клітинка з бітом 1 (зелена заливка)
ONE_S = FIELD     # її обведення
ZERO = "#eef1f4"  # клітинка з бітом 0


def cell_row(x, y, bits, cell=30, gap=5):
    """Рядок клітинок-бітів зліва направо. Повертає (svg, ширина)."""
    out = []
    for i, b in enumerate(bits):
        cx = x + i * (cell + gap)
        fill = ONE if b == "1" else ZERO
        stroke = ONE_S if b == "1" else "#c3ccd4"
        out.append(rect(cx, y, cell, cell, fill=fill, stroke=stroke, sw=2, rx=5))
        out.append(text(cx + cell / 2, y + cell / 2 + 6, b, size=17,
                        color=(INK if b == "1" else MUTED), bold=(b == "1")))
    return "".join(out), len(bits) * (cell + gap) - gap


def arc_arrow(cx, cy, r, a1deg, a2deg, color=INK, sw=2.4):
    a1, a2 = math.radians(a1deg), math.radians(a2deg)
    x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
    x2, y2 = cx + r * math.cos(a2), cy + r * math.sin(a2)
    return ('<path d="M%.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" fill="none" '
            'stroke="%s" stroke-width="%.1f" marker-end="url(#arrow)"/>'
            % (x1, y1, r, r, x2, y2, color, sw))


# ── Фігура 1: колесо циклічних зсувів ───────────────────────────────────────
def fig_wheel():
    W, H = 820, 430
    parts = []
    # --- ліворуч: колесо з бітами слова 0001011 (c6..c0) ---
    wcx, wcy, R = 205, 235, 118
    word = "0001011"                     # c6 c5 c4 c3 c2 c1 c0
    parts.append(circle(wcx, wcy, R, fill=BG, stroke="#dfe4ea", sw=2))
    for i, b in enumerate(word):
        ang = math.radians(-90 + i * 360 / 7)   # c6 угорі, далі за годинниковою
        nx, ny = wcx + R * math.cos(ang), wcy + R * math.sin(ang)
        fill = ONE if b == "1" else ZERO
        stroke = ONE_S if b == "1" else "#c3ccd4"
        parts.append(circle(nx, ny, 20, fill=fill, stroke=stroke, sw=2.4))
        parts.append(text(nx, ny + 6, b, size=17,
                          color=(INK if b == "1" else MUTED), bold=(b == "1")))
        # підпис індексу назовні кола
        lx, ly = wcx + (R + 26) * math.cos(ang), wcy + (R + 26) * math.sin(ang)
        parts.append(text(lx, ly + 4, "c%d" % (6 - i), size=11, color=MUTED))
    # стрілка обертання (зверху, за годинниковою)
    parts.append(arc_arrow(wcx, wcy, R - 44, -128, -52, color=NEG, sw=2.6))
    parts.append(text(wcx, wcy + 4, "зсув", size=13, color=NEG, bold=True))
    parts.append(text(wcx, wcy + 22, "по колу", size=13, color=NEG))
    parts.append(text(wcx, H - 26, "слово на колі", size=13, color=MUTED))

    # --- праворуч: сім зсувів як рядки клітинок ---
    rots = ["0001011", "0010110", "0101100", "1011000",
            "0110001", "1100010", "1000101"]
    rx, ry0, step = 430, 78, 46
    parts.append(text(rx, ry0 - 26, "усі сім циклічних зсувів:",
                      size=14, color=INK, anchor="start", bold=True))
    for i, r in enumerate(rots):
        ry = ry0 + i * step
        row, rw = cell_row(rx, ry, r, cell=30, gap=5)
        parts.append(row)
        # зелена галочка «кодове слово»
        parts.append(text(rx + rw + 22, ry + 21, "✓", size=19, color=FIELD, bold=True))
        parts.append(text(rx + rw + 40, ry + 21, "кодове слово",
                          size=12, color=MUTED, anchor="start"))
    render(os.path.join(IMG, "wheel.svg"), W, H, *parts,
           title="Циклічний зсув: кожен поворот слова — теж кодове слово")


# ── Фігура 2: зсув = множення на x за модулем x⁷−1 ──────────────────────────
def fig_shift():
    W, H = 760, 380
    parts = []
    x0 = 150
    powers = ["x⁶", "x⁵", "x⁴", "x³", "x²", "x¹", "x⁰"]

    # верхній рядок: c(x)
    yt = 92
    parts.append(text(70, yt + 21, "c(x)", size=15, color=INK, anchor="end", bold=True))
    row, rw = cell_row(x0, yt, "0001011", cell=34, gap=6)
    parts.append(row)
    for i, p in enumerate(powers):
        cx = x0 + i * 40 + 17
        parts.append(text(cx, yt - 10, p, size=12, color=MUTED))
    parts.append(text(x0 + rw + 30, yt + 21, "=  x³ + x + 1",
                      size=15, color=INK, anchor="start"))

    # стрілка-операція
    parts.append(arrow(x0 + rw / 2, yt + 46, x0 + rw / 2, yt + 96, color=NEG, sw=2.2))
    parts.append(text(x0 + rw / 2 + 14, yt + 74, "× x,  за модулем x⁷ − 1",
                      size=13, color=NEG, anchor="start", bold=True))

    # нижній рядок: x·c(x)
    yb = 236
    parts.append(text(70, yb + 21, "x·c(x)", size=15, color=INK, anchor="end", bold=True))
    row2, rw2 = cell_row(x0, yb, "0010110", cell=34, gap=6)
    parts.append(row2)
    parts.append(text(x0 + rw2 + 30, yb + 21, "=  x⁴ + x² + x",
                      size=15, color=INK, anchor="start"))

    # дуга «старший біт повертається у вільний член» (c6 -> c0)
    xc6 = x0 + 17
    xc0 = x0 + 6 * 40 + 17
    parts.append('<path d="M%.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" '
                 'fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="5 4" '
                 'marker-end="url(#arrow)"/>'
                 % (xc6, yb + 40, xc6 - 30, yb + 108, xc0 + 30, yb + 108, xc0, yb + 40, POS))
    parts.append(text((xc6 + xc0) / 2, yb + 116, "x⁷ = 1  →  старший член повертається у вільний",
                      size=12, color=POS))
    render(os.path.join(IMG, "shift-as-x.svg"), W, H, *parts,
           title="Циклічний зсув — це множення многочлена на x")


# ── Фігура 3: розклад x⁷−1 → вибір твірного многочлена ─────────────────────
def fig_generator():
    W, H = 780, 350
    parts = []
    parts.append(text(60, 74, "x⁷ − 1   =",
                      size=20, color=INK, anchor="start", bold=True))
    # три множники
    facs = ["x + 1", "x³ + x + 1", "x³ + x² + 1"]
    fw = [120, 160, 172]
    fx = 200
    gap = 34
    boxes_cx = []
    for i, f in enumerate(facs):
        w = fw[i]
        chosen = (i == 1)
        parts.append(fitbox(fx, 50, w, 46, f, size=17,
                            fill=(ONE if chosen else FILL),
                            stroke=(FIELD if chosen else LINE),
                            sw=(2.6 if chosen else 1.5), bold=chosen))
        boxes_cx.append(fx + w / 2)
        if i < 2:
            parts.append(text(fx + w + gap / 2, 78, "·", size=22, color=MUTED))
        fx += w + gap

    # підпис до обраного множника
    gcx = boxes_cx[1]
    parts.append(text(gcx, 118, "обираємо за твірний g(x)",
                      size=13, color=FIELD, bold=True))
    parts.append(arrow(gcx, 128, gcx, 176, color=FIELD, sw=2.4))

    # підсумкова рамка
    box = ("g(x) = x³ + x + 1   (степінь 3)\n"
           "→  [7, 4]-код Геммінга:  4 біти даних + 3 перевірні\n"
           "кодові слова = всі кратні g(x) степеня < 7")
    parts.append(fitbox(150, 190, 480, 96, box, size=14, fill="#eef7f1",
                        stroke=FIELD, sw=2))
    parts.append(text(W / 2, 316, "будувати циклічний код = розкласти xⁿ−1 і взяти добуток частини множників за g(x)",
                      size=12, color=MUTED))
    render(os.path.join(IMG, "generator.svg"), W, H, *parts,
           title="Твірний многочлен — це дільник xⁿ − 1")


# ── Фігура 4 (hist): три роки, що зробили з кодів алгебру ───────────────────
def fig_hist_timeline():
    W, H = 1240, 452
    CTXF, CTXS = BG, "#c8ccd2"
    HINF, HINS = "#d7f0e0", FIELD
    DISF, DISS = "#eafaf0", FIELD
    BANDL, BANDR = "#eef1f4", "#eafaf0"
    left, right = 60, 1180
    colw = (right - left) / 6.0
    cx = [left + colw * (i + 0.5) for i in range(6)]
    axis_y = 300
    seam = cx[2]
    p = []

    # коротка пунктирна риска «злам» у чистій зоні між вузлом і смугою
    p.append(line(seam, axis_y + 18, seam, 350, color=FIELD, sw=2.0, dash="6 5"))

    # смуга фази: ліворуч комбінаторика, праворуч алгебра
    bandy, bandh = 352, 50
    p.append(rect(left, bandy, seam - left, bandh, fill=BANDL, stroke="#d3d8de", sw=1.2, rx=4))
    p.append(rect(seam, bandy, right - seam, bandh, fill=BANDR, stroke=HINS, sw=1.4, rx=4))
    p.append(mtext((left + seam) / 2, bandy + 20,
                   ["до 1957 — коди були вдалими здогадами", "(комбінаторика, без важелів)"],
                   size=12.5, color=MUTED, bold=True, lh=1.25))
    p.append(mtext((seam + right) / 2, bandy + 20,
                   ["від 1957 — код став ідеалом у GF(2)[x]/(xⁿ−1)",
                    "(алгебра: розклад, корені, скінченні поля)"],
                   size=12.5, color=FIELD, bold=True, lh=1.25))

    # вісь часу
    p.append(arrow(left - 8, axis_y, right + 26, axis_y, color="#aab0b8", sw=2.0))
    p.append(text(right + 22, axis_y - 12, "час", size=12, color=MUTED, anchor="end", italic=True))

    events = [
        (["Шеннон, 1948", "добрі коди існують —", "та не як їх будувати"], "ctx"),
        (["Геммінг, 1950", "код на одну", "помилку в слові"], "ctx"),
        (["Пренж · AFCRC, 1957", "слово = многочлен,", "зсув = ×x mod xⁿ−1"], "hinge"),
        (["Окенгем, 1959", "перша конструкція", "на t помилок"], "disc"),
        (["Бозе–Рей-Чоудхурі,", "1960 — те саме,", "незалежно"], "disc"),
        (["Рід–Соломон, 1960", "символи замість", "бітів у GF(2ᵐ)"], "disc"),
    ]
    sty = {"ctx": (CTXF, CTXS), "hinge": (HINF, HINS), "disc": (DISF, DISS)}
    for i, (lines, kind) in enumerate(events):
        f, s = sty[kind]
        hinge = kind == "hinge"
        bw = 188 if hinge else 176
        bh = 104 if hinge else 90
        by = 50 if hinge else 60
        p.append(fitbox(cx[i] - bw / 2, by, bw, bh, lines, size=13,
                        fill=f, stroke=s, sw=2.6 if hinge else 1.8, bold=True, color=INK))
        p.append(line(cx[i], by + bh, cx[i], axis_y - (16 if hinge else 11),
                      color="#aab0b8", sw=1.4))
        r = 16 if hinge else 11
        p.append(circle(cx[i], axis_y, r, fill=f, stroke=s, sw=2.8 if hinge else 2.2))
        if hinge:
            p.append(text(cx[i], axis_y + 5, "★", size=15, color=FIELD, bold=True))
            p.append(text(cx[i], by - 9, "ЗЛАМ", size=12, color=FIELD, bold=True))

    render(os.path.join(IMG, "hist-timeline.svg"), W, H, *p,
           title="Три роки, що зробили з кодів алгебру: 1957 — злам")


# ── Фігура 5 (hist): що відчинив погляд «код = ідеал» ──────────────────────
def fig_hist_lineage():
    W, H = 1120, 470
    ROOTF, ROOTS = "#d7f0e0", FIELD
    CF = {"crc": ("#eef4ff", NEG), "bch": ("#eafaf0", FIELD), "rs": ("#f6f4ec", "#b7791f")}
    p = []

    rw, rh = 640, 100
    rcx, rcy = W / 2, 92
    p.append(fitbox(rcx - rw / 2, rcy - rh / 2, rw, rh,
                    ["Пренж, 1957 · Дослідницький центр ВПС США (AFCRC)",
                     "циклічний код = ІДЕАЛ у кільці GF(2)[x]/(xⁿ−1),",
                     "заданий одним дільником g(x) многочлена xⁿ−1"],
                    size=14.5, fill=ROOTF, stroke=ROOTS, sw=2.6, bold=True))
    p.append(text(W / 2, rcy + rh / 2 + 24,
                  "той самий алгебраїчний ключ відчинив одразу три робочі родини:",
                  size=13, color=MUTED, italic=True))

    kids = [
        (200, "crc", ["CRC", "g(x) лише ВИЯВЛЯЄ збій;", "кілька вентилів XOR", "на повній швидкості лінії"]),
        (560, "bch", ["BCH — Окенгем 1959,", "Бозе–Рей-Чоудхурі 1960", "корені g у GF(2ᵐ)", "→ гарантована відстань"]),
        (920, "rs", ["Рід–Соломон, 1960", "Рід і Соломон · MIT", "цілі символи в GF(2ᵐ)", "CD, QR-коди, «Вояджер»"]),
    ]
    ky, kh, kw = 236, 122, 320
    for kx, key, lines in kids:
        f, s = CF[key]
        p.append(fitbox(kx - kw / 2, ky, kw, kh, lines, size=13.5,
                        fill=f, stroke=s, sw=2.0, bold=True))
        p.append(arrow(W / 2, rcy + rh / 2 + 40, kx, ky - 6, color=s, sw=1.9))

    p.append(text(W / 2, ky + kh + 46,
                  "жодна з трьох — не вдалий здогад: усі три СПРОЄКТОВАНО з алгебри поля й многочленів",
                  size=13, color=INK, bold=True))

    render(os.path.join(IMG, "hist-lineage.svg"), W, H, *p,
           title="Що відчинив погляд «код = ідеал»")


# ── Фігура 6 (math): твірна матриця як сходинка зсувів g(x) ─────────────────
def fig_staircase():
    """Рядки g, xg, x²g, x³g для g=1101 (n=7,k=4): провідні одиниці — сходинка,
    блок завширшки deg g+1 вміщається k = n−deg g разів."""
    W, H = 720, 344
    p = []
    x0, cell, gap = 190, 34, 6
    col = cell + gap                     # 40
    powers = ["x⁰", "x¹", "x²", "x³", "x⁴", "x⁵", "x⁶"]
    rows = [("g",     "1101000"),
            ("x·g",   "0110100"),
            ("x²·g",  "0011010"),
            ("x³·g",  "0001101")]
    y0, step = 88, 46

    # підписи степенів згори
    for i, pw in enumerate(powers):
        p.append(text(x0 + i * col + cell / 2, y0 - 14, pw, size=12, color=MUTED))

    for r, (label, bits) in enumerate(rows):
        ry = y0 + r * step
        p.append(text(x0 - 20, ry + 21, label, size=14, color=INK,
                      anchor="end", bold=True))
        row, _ = cell_row(x0, ry, bits, cell=cell, gap=gap)
        p.append(row)
        # провідна одиниця (півот) рядка r стоїть у стовпці r — обвести жирно
        px = x0 + r * col
        p.append(rect(px, ry, cell, cell, fill="none", stroke=INK, sw=3, rx=5))
        # мітка сходинки праворуч від рядка (не над текстом клітинок)
        p.append(text(x0 + 7 * col + 6, ry + 21, "◄ півот у стовпці %d" % r,
                      size=11, color=MUTED, anchor="start"))

    # брекет над блоком g першого рядка (стовпці 0..3, ширина deg g+1 = 4)
    bx1, bx2, by = x0, x0 + 4 * col - gap, y0 - 30
    p.append(line(bx1, by, bx2, by, color=NEG, sw=2.0))
    p.append(line(bx1, by, bx1, by + 6, color=NEG, sw=2.0))
    p.append(line(bx2, by, bx2, by + 6, color=NEG, sw=2.0))
    p.append(text((bx1 + bx2) / 2, by - 6, "блок g:  deg g + 1 = 4",
                  size=12, color=NEG, bold=True))

    # підсумкові рядки під ґраткою
    yb = y0 + 4 * step + 8
    p.append(mtext(W / 2, yb,
                   ["блок з'їжджає вниз-вправо і вміщається k = n − deg g = 4 рази",
                    "→ 4 незалежні рядки (ранг = k = dim);  перевірних n − k = deg g = 3"],
                   size=12.5, color=INK, bold=True, lh=1.35))
    render(os.path.join(IMG, "staircase-basis.svg"), W, H, *p,
           title="n − k = deg g: твірна матриця як сходинка зсувів g(x)")


# ── Фігура 7 (math): булева ґратка 8 циклічних кодів довжини 7 ──────────────
def fig_divisor_lattice():
    """Дільники x⁷−1 (підмножини трьох множників) = 8 кодів; ребро = +1 множник."""
    W, H = 940, 660
    p = []
    NB, NBs = "#eaf0fd", NEG            # симплекс — синій
    HG, HGs = "#d7f0e0", FIELD          # Геммінга — зелений
    GY, GYs = "#eef1f4", "#c3ccd4"      # нейтральні краї
    WM, WMs = "#f6f4ec", "#b7791f"      # повторення — теплий

    # вузол: (x, y, [рядки], fill, stroke, bold)
    y0, y1, y2, y3 = 82, 232, 402, 572
    xL, xC, xR = 205, 495, 785
    nodes = {
        "e":  (xC, y0, ["g = 1", "[7, 7, 1]", "увесь простір"], FILL, LINE, False),
        "A":  (xL, y1, ["g = x+1", "[7, 6, 2]", "парність"], FILL, LINE, False),
        "B":  (xC, y1, ["g = x³+x+1", "[7, 4, 3]", "Геммінга"], HG, HGs, True),
        "C":  (xR, y1, ["g = x³+x²+1", "[7, 4, 3]", "Геммінга′"], "#eaf7ef", HGs, False),
        "AB": (xL, y2, ["g = x⁴+x³+x²+1", "[7, 3, 4]", "симплексний"], NB, NBs, False),
        "AC": (xC, y2, ["g = x⁴+x²+x+1", "[7, 3, 4]", "симплексний′"], "#eef3fd", NBs, False),
        "BC": (xR, y2, ["g = x⁶+x⁵+…+x+1", "[7, 1, 7]", "повторення"], WM, WMs, False),
        "F":  (xC, y3, ["g = x⁷−1 ≡ 0", "[7, 0, —]", "лише нуль"], GY, GYs, False),
    }
    edges = [("e", "A"), ("e", "B"), ("e", "C"),
             ("A", "AB"), ("A", "AC"), ("B", "AB"), ("B", "BC"),
             ("C", "AC"), ("C", "BC"),
             ("AB", "F"), ("AC", "F"), ("BC", "F")]
    bw, bh = 252, 86

    # ребра — спершу, тонким сірим, під непрозорими рамками
    for a, b in edges:
        ax, ay = nodes[a][0], nodes[a][1]
        bx, by = nodes[b][0], nodes[b][1]
        p.append(line(ax, ay + bh / 2 - 6, bx, by - bh / 2 + 6,
                      color="#c8ccd2", sw=1.6))

    # ліва вісь напрямку
    p.append(arrow(44, y0 - 20, 44, y3 + 30, color="#aab0b8", sw=2.0))
    p.append(text(60, y0 - 30, "більший код", size=12, color=MUTED,
                  anchor="start", italic=True))
    p.append(text(60, y3 + 44, "менший код (більший g)", size=12, color=MUTED,
                  anchor="start", italic=True))
    p.append(text(W - 24, y0 - 30, "ребро: +1 множник у g → підкод",
                  size=12, color=MUTED, anchor="end", italic=True))

    # рамки
    for key, (x, y, lines, f, s, bold) in nodes.items():
        p.append(fitbox(x - bw / 2, y - bh / 2, bw, bh, lines, size=14,
                        fill=f, stroke=s, sw=2.4 if bold else 1.8, bold=bold))

    render(os.path.join(IMG, "divisor-lattice.svg"), W, H, *p,
           title="Вісім дільників x⁷ − 1 — вісім циклічних кодів довжини 7")


# ── Фігура 8 (proj): LFSR-кодер g(x)=x³+x+1 ────────────────────────────────
def fig_lfsr_encoder():
    W, H = 900, 380
    p = []
    NEGF = "#eef4ff"

    def xor_gate(cx, cy, r=16):
        return (circle(cx, cy, r, fill=NEGF, stroke=NEG, sw=2)
                + text(cx, cy + 6, "⊕", size=18, color=NEG, bold=True))

    cy = 214
    cw, ch = 78, 58
    cells = [("b₀", 300, "x⁰"), ("b₁", 470, "x¹"), ("b₂", 640, "x²")]
    for lbl, cx, pw in cells:
        p.append(rect(cx - cw / 2, cy - ch / 2, cw, ch, fill=ONE, stroke=ONE_S, sw=2.4, rx=8))
        p.append(text(cx, cy + 7, lbl, size=22, color=INK, bold=True))
        p.append(text(cx, cy + ch / 2 + 20, pw, size=13, color=MUTED))

    xorA, xorB = 212, 385
    # напрям зсуву: XOR-A → b0 → XOR-B → b1 → b2
    p.append(arrow(xorA + 16, cy, 300 - cw / 2, cy, color=INK, sw=2))
    p.append(arrow(300 + cw / 2, cy, xorB - 16, cy, color=INK, sw=2))
    p.append(arrow(xorB + 16, cy, 470 - cw / 2, cy, color=INK, sw=2))
    p.append(arrow(470 + cw / 2, cy, 640 - cw / 2, cy, color=INK, sw=2))
    p.append(xor_gate(xorA, cy))
    p.append(xor_gate(xorB, cy))
    p.append(text(xorA, cy + ch / 2 + 20, "g₀=1", size=12, color=NEG, bold=True))
    p.append(text(xorB, cy + ch / 2 + 20, "g₁=1", size=12, color=NEG, bold=True))
    p.append(mtext((470 + 640) / 2, cy - ch / 2 - 20, ["g₂=0", "(без відводу)"],
                   size=11.5, color=MUTED, lh=1.15))

    # шина зворотного зв'язку
    fby, topx = 98, 760
    p.append(line(640 + cw / 2, cy, topx, cy, color=INK, sw=2))
    p.append(line(topx, cy, topx, fby, color=INK, sw=2))
    p.append(xor_gate(topx, fby))
    p.append(arrow(topx, 46, topx, fby - 18, color=POS, sw=2.2))
    p.append(text(topx, 36, "дані, старший біт уперед", size=12.5, color=POS, bold=True))
    p.append(text(topx + 26, fby - 1, "fb = дані ⊕ b₂", size=12, color=NEG, anchor="start"))
    p.append(line(topx - 16, fby, xorA, fby, color=INK, sw=2))
    p.append(arrow(xorA, fby, xorA, cy - 18, color=INK, sw=2))
    p.append(arrow(xorB, fby, xorB, cy - 18, color=INK, sw=2))

    p.append(text(470, H - 22, "після K тактів у (b₀ b₁ b₂) лежить остача mod g — це перевірні біти",
                  size=13, color=INK))
    render(os.path.join(IMG, "lfsr-encoder.svg"), W, H, *p,
           title="LFSR-кодер g(x)=x³+x+1: ділення як зсувний регістр")


# ── Фігура 9 (proj): трасування error-trapping ─────────────────────────────
def fig_errortrap():
    W, H = 900, 384
    p = []
    x0, cell, gap = 165, 34, 5
    roww = 7 * (cell + gap) - gap
    sx0 = 476
    synw = 3 * (cell + gap) - gap

    # смуга «перевірні розряди» за трьома правими клітинками слова
    pw_x = x0 + 4 * (cell + gap)
    pw_w = 3 * (cell + gap) - gap
    p.append(rect(pw_x - 4, 88, pw_w + 8, 258, fill="#eafaf0", stroke=FIELD, sw=1.4, rx=6))
    p.append(text(pw_x + pw_w / 2, 80, "перевірні розряди (пастка)", size=12, color=FIELD, bold=True))

    hy = 112
    p.append(text(72, hy, "оберт", size=13, color=INK, bold=True))
    p.append(text(x0 + roww / 2, hy, "слово (циклічно зсунуте)", size=13, color=INK, bold=True))
    p.append(text(sx0 + synw / 2, hy, "синдром", size=13, color=INK, bold=True))
    p.append(text(704, hy, "вага", size=13, color=INK, bold=True))

    def hlrow(x, y, bits, err):
        out = []
        for i, b in enumerate(bits):
            cx = x + i * (cell + gap)
            is_e = (i == err)
            fill = "#fdecea" if is_e else (ONE if b == "1" else ZERO)
            stroke = POS if is_e else (ONE_S if b == "1" else "#c3ccd4")
            out.append(rect(cx, y, cell, cell, fill=fill, stroke=stroke, sw=(2.6 if is_e else 2), rx=5))
            col = POS if is_e else (INK if b == "1" else MUTED)
            out.append(text(cx + cell / 2, y + cell / 2 + 6, b, size=16, color=col, bold=(is_e or b == "1")))
        return "".join(out)

    rows = [(0, "1000011", 2, "110", 2, False),
            (1, "0000111", 1, "111", 3, False),
            (2, "0001110", 0, "101", 2, False),
            (3, "0011100", 6, "001", 1, True)]
    y, rh = 132, 50
    for j, word, err, syn, wt, trap in rows:
        p.append(text(72, y + cell / 2 + 6, "j = %d" % j, size=13, color=INK, bold=trap))
        p.append(hlrow(x0, y, word, err))
        for i, b in enumerate(syn):
            cx = sx0 + i * (cell + gap)
            one = (b == "1")
            p.append(rect(cx, y, cell, cell, fill=(ONE if one else ZERO),
                          stroke=(FIELD if trap else (ONE_S if one else "#c3ccd4")),
                          sw=(2.6 if trap else 2), rx=5))
            p.append(text(cx + cell / 2, y + cell / 2 + 6, b, size=16,
                          color=(INK if one else MUTED), bold=one))
        wcol = FIELD if wt == 1 else INK
        p.append(text(704, y + cell / 2 + 6, str(wt), size=17, color=wcol, bold=True))
        if trap:
            p.append(text(748, y + cell / 2 + 6, "← пастка!", size=13, color=FIELD, bold=True, anchor="start"))
        y += rh

    p.append(text(W / 2, H - 20,
                  "вага впала до 1 → синдром 001 і є той самий помилковий біт: XOR у розряд 0, тоді зсув назад на 3 → 1010011",
                  size=12.5, color=INK))
    render(os.path.join(IMG, "error-trap.svg"), W, H, *p,
           title="Error-trapping: крутимо слово, доки синдром не «замкнеться»")


if __name__ == "__main__":
    fig_wheel()
    fig_shift()
    fig_generator()
    fig_hist_timeline()
    fig_hist_lineage()
    fig_staircase()
    fig_divisor_lattice()
    fig_lfsr_encoder()
    fig_errortrap()
    print("OK: wheel.svg, shift-as-x.svg, generator.svg, hist-timeline.svg, "
          "hist-lineage.svg, staircase-basis.svg, divisor-lattice.svg, "
          "lfsr-encoder.svg, error-trap.svg")
