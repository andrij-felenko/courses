# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Палітра ролей (на додачу до svgkit): нейтральне сіре, синє «логіка», бурштин «пам'ять».
GREY  = "#8a8a8a"
BLUE  = NEG
AMBER = "#b8860b"
GREEN = FIELD
RED   = POS


def dot(cx, cy, color=RED, r=4.5):
    return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s" '
            'stroke-width="1"/>' % (cx, cy, r, color, color))


# ── 1. and-or-plane: програмована матриця AND + фіксована OR ──────────────────
def fig_and_or_plane():
    W, H = 860, 320
    p = []
    # три горизонтальні лінії входів a, b, c
    rows = [("a", 110), ("b", 138), ("c", 166)]
    for name, y in rows:
        p.append(line(150, y, 700, y, color="#dfe3e8", sw=1.4))
        p.append(text(132, y + 4, name, size=13, color=BLUE, anchor="end", bold=True))
    p.append(text(150, 86, "програмована матриця AND", size=12, color=RED, anchor="start", bold=True))
    p.append(text(150, 100, "(точки = пропалені зв'язки)", size=10, color=MUTED, anchor="start"))
    # три вертикалі добутків
    prods = [("a·b", 300, [("a", RED), ("b", RED)]),
             ("b·c̄", 380, [("b", RED), ("c", BLUE)]),
             ("a·c", 460, [("a", RED), ("c", RED)])]
    ymap = {"a": 110, "b": 138, "c": 166}
    for label, x, conns in prods:
        p.append(line(x, 100, x, 200, color=INK, sw=1.6))
        p.append(text(x, 218, label, size=12, color=INK, bold=True))
        for nm, col in conns:
            p.append(dot(x, ymap[nm], color=col))
    # фіксована матриця OR
    p.append(text(610, 86, "фіксована матриця OR", size=12, color=GREEN, anchor="start", bold=True))
    orbox = rect(560, 116, 130, 64, fill="#eef7ee", stroke=GREEN, sw=1.8)
    p.append(orbox)
    p.append(text(625, 144, "OR", size=14, color=GREEN, bold=True))
    p.append(text(625, 164, "сума добутків", size=9.5, color=MUTED))
    for _, x, _ in prods:
        p.append(line(x, 200, 558, 150, color=GREY, sw=1.2))
    p.append(arrow(690, 148, 770, 148, color=GREEN, sw=2))
    p.append(text(795, 142, "F", size=13, color=GREEN, anchor="middle", bold=True))
    p.append(text(625, 200, "F = a·b + b·c̄ + a·c", size=12, color=INK, bold=True))
    render(os.path.join(OUT, "and-or-plane.svg"), W, H, *p)


# ── 2. spld-family: PROM / PAL / PLA / GAL ────────────────────────────────────
def fig_spld_family():
    W, H = 880, 250
    p = []
    cards = [
        ("PROM", GREY,  ["AND — фікс.", "OR — програм."], "повний дешифратор;", "добре для таблиць", None),
        ("PAL",  GREEN, ["AND — програм.", "OR — фікс."], "дешево й швидко;", "робоча конячка", "★ найпопулярніший"),
        ("PLA",  BLUE,  ["AND — програм.", "OR — програм."], "найгнучкіший,", "але повільніший", None),
        ("GAL",  AMBER, ["як PAL, але", "СТИРНИЙ"], "перепрограмовний", "(EEPROM)", "★ багаторазовий"),
    ]
    x = 30
    cw, gap = 200, 12
    for name, col, mat, n1, n2, star in cards:
        p.append(rect(x, 40, cw, 180, fill="#fafafa", stroke=col, sw=1.8))
        cx = x + cw / 2
        p.append(text(cx, 68, name, size=16, color=col, bold=True))
        p.append(line(x + 14, 80, x + cw - 14, 80, color="#e4e4e4", sw=1.3))
        p.append(text(cx, 104, mat[0], size=11, color=INK, bold=True))
        p.append(text(cx, 124, mat[1], size=11, color=INK, bold=True))
        p.append(line(x + 14, 138, x + cw - 14, 138, color="#e4e4e4", sw=1.3))
        p.append(text(cx, 160, n1, size=10, color=MUTED, italic=True))
        p.append(text(cx, 176, n2, size=10, color=MUTED, italic=True))
        if star:
            p.append(text(cx, 204, star, size=10, color=col, bold=True))
        x += cw + gap
    render(os.path.join(OUT, "spld-family.svg"), W, H, *p)


# ── 3. macrocell: матриця AND-OR + тригер + MUX + зворотний зв'язок ────────────
def fig_macrocell():
    W, H = 860, 300
    p = []
    # матриця
    p.append(rect(70, 110, 160, 110, fill="#eef7ee", stroke=GREEN, sw=1.8))
    p.append(text(150, 150, "матриця", size=12, color=GREEN, bold=True))
    p.append(text(150, 168, "AND-OR", size=12, color=GREEN, bold=True))
    p.append(text(150, 190, "комбінаційна F", size=9.5, color=INK, bold=True))
    p.append(arrow(230, 165, 305, 165, color=INK, sw=2))
    # тригер
    p.append(rect(305, 142, 54, 48, fill="#eef0fb", stroke=BLUE, sw=1.8))
    p.append(text(332, 162, "D", size=11, color=BLUE, bold=True))
    p.append(text(332, 180, "тригер", size=9, color=BLUE, bold=True))
    p.append('<polyline points="309,184 314,178 314,184" fill="none" stroke="%s" stroke-width="1.4"/>' % BLUE)
    p.append(arrow(359, 165, 430, 165, color=INK, sw=2))
    # MUX
    p.append('<path d="M430,138 L470,150 L470,184 L430,196 Z" fill="#fff8e8" stroke="%s" stroke-width="1.8"/>' % AMBER)
    p.append(text(448, 168, "MUX", size=9, color="#9a7322", bold=True))
    p.append(text(450, 214, "рег. чи комб.?", size=9, color=MUTED))
    p.append(arrow(470, 165, 560, 165, color=AMBER, sw=2))
    p.append(text(610, 169, "вихідний пін", size=11, color=INK, bold=True))
    # зворотний зв'язок
    p.append('<polyline points="332,190 332,260 56,260 56,150 68,150" fill="none" '
             'stroke="%s" stroke-width="1.6" stroke-dasharray="4 3"/>' % GREY)
    p.append(text(200, 278, "зворотний зв'язок: вихід тригера повертається у матрицю", size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "macrocell.svg"), W, H, *p)


# ── 4. cpld-vs-fpga: дві архітектури поруч ────────────────────────────────────
def fig_cpld_vs_fpga():
    W, H = 880, 360
    p = []
    # ── CPLD ліворуч
    p.append(rect(30, 50, 380, 290, fill="#fbfbfb", stroke=BLUE, sw=1.6))
    p.append(text(220, 76, "CPLD", size=15, color=BLUE, bold=True))
    p.append(text(220, 94, "кілька «жирних» блоків", size=9.5, color=MUTED))
    # центральна матриця
    p.append(rect(150, 180, 140, 46, fill="#eef0fb", stroke=BLUE, sw=1.6))
    p.append(text(220, 207, "центральна матриця", size=9.5, color=BLUE, bold=True))
    for bx, by in [(70, 120), (290, 120), (70, 250), (290, 250)]:
        p.append(rect(bx, by, 100, 54, fill="#eef7ee", stroke=GREEN, sw=1.6))
        p.append(text(bx + 50, by + 23, "PAL-блок", size=10, color=GREEN, bold=True))
        p.append(text(bx + 50, by + 41, "+ макрокомірка", size=9, color=MUTED))
        p.append(line(bx + 50, by + (54 if by < 180 else 0), 220, 203, color="#e4e4e4", sw=1.3))
    p.append(text(220, 322, "мало блоків, та кожен потужний;", size=9.5, color=INK))
    p.append(text(220, 336, "стала затримка, миттєвий старт", size=9.5, color=GREEN, bold=True))
    # ── FPGA праворуч: сітка дрібних клітинок
    p.append(rect(450, 50, 400, 290, fill="#fbfbfb", stroke=GREEN, sw=1.6))
    p.append(text(650, 76, "FPGA", size=15, color=GREEN, bold=True))
    p.append(text(650, 94, "море дрібних клітинок", size=9.5, color=MUTED))
    gx0, gy0, cell, gapc = 500, 116, 28, 14
    cols, rowsn = 6, 5
    for r in range(rowsn):
        for c in range(cols):
            cx = gx0 + c * (cell + gapc)
            cy = gy0 + r * (cell + gapc)
            p.append(rect(cx, cy, cell, cell, fill="#eef7ee", stroke=GREEN, sw=1.2, rx=3))
            if c < cols - 1:
                p.append(line(cx + cell, cy + cell / 2, cx + cell + gapc, cy + cell / 2, color="#dfe3e8", sw=1.1))
            if r < rowsn - 1:
                p.append(line(cx + cell / 2, cy + cell, cx + cell / 2, cy + cell + gapc, color="#dfe3e8", sw=1.1))
    p.append(text(650, 322, "тисячі–мільйони LUT-клітинок;", size=9.5, color=INK))
    p.append(text(650, 336, "величезна ємність, гнучка маршрутизація", size=9.5, color=GREEN, bold=True))
    render(os.path.join(OUT, "cpld-vs-fpga.svg"), W, H, *p)


# ── 5. ladder: сходинки еволюції ──────────────────────────────────────────────
def fig_ladder():
    W, H = 880, 410
    p = []
    steps = [
        ("PROM/PAL", "1978", GREY,  340, "одна матриця AND-OR; десятки вентилів; пропалюється раз"),
        ("GAL",      "1983", AMBER, 280, "те саме, але СТИРНИЙ (EEPROM) — можна переписати"),
        ("CPLD",     "кін. 1980-х", BLUE, 220, "багато PAL-блоків + матриця; нелеткий"),
        ("FPGA",     "1985 →", GREEN, 160, "сітка LUT-клітинок + RAM/DSP; до мільйонів LUT"),
    ]
    widths = [330, 290, 250, 200]
    for (name, yr, col, y, desc), w in zip(steps, widths):
        p.append(rect(120, y, w, 50, fill="#fafafa", stroke=col, sw=1.8))
        p.append(text(134, y + 22, name, size=13, color=col, anchor="start", bold=True))
        p.append(text(134, y + 40, yr, size=9.5, color=MUTED, anchor="start", bold=True))
        p.append(text(230, y + 31, desc, size=9.6, color=INK, anchor="start"))
        p.append(arrow(140, y, 140, y - 14, color=INK, sw=1.8))
    p.append(text(100, 120, "більше ємності й гнучкості ↑", size=10.5, color=GREEN, anchor="start", bold=True))
    render(os.path.join(OUT, "ladder.svg"), W, H, *p)


# ── 6. glue: роль клейової логіки між великими чипами (вставка) ────────────────
def fig_glue():
    W, H = 860, 300
    p = []
    big = [("МК", 90, 110), ("давач", 90, 200), ("драйвер\nмотора", 640, 155)]
    for label, x, y in big:
        lines = label.split("\n")
        h = 70
        p.append(rect(x, y, 130, h, fill="#eef0fb", stroke=BLUE, sw=1.7))
        for i, ln in enumerate(lines):
            p.append(text(x + 65, y + 32 + i * 18, ln, size=12, color=BLUE, bold=True))
    # CMIC у проміжку
    p.append(rect(360, 130, 120, 70, fill="#fff8e8", stroke=AMBER, sw=2))
    p.append(text(420, 158, "CMIC", size=13, color="#9a7322", bold=True))
    p.append(text(420, 178, "(клейова логіка)", size=9, color=MUTED))
    p.append(arrow(220, 140, 358, 150, color=GREY, sw=1.6))
    p.append(arrow(220, 230, 358, 185, color=GREY, sw=1.6))
    p.append(arrow(480, 165, 638, 178, color=GREY, sw=1.6))
    p.append(text(290, 124, "поділити імпульси,", size=9.5, color=MUTED, italic=True))
    p.append(text(420, 232, "згенерувати ENABLE, витримати скид", size=9.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "glue.svg"), W, H, *p)


# ── 7. cmic-inside: нутро CMIC — банк блоків + матриця + NVM (вставка) ─────────
def fig_cmic_inside():
    W, H = 860, 340
    p = []
    # банк блоків ліворуч
    p.append(text(150, 60, "банк блоків", size=12, color=INK, bold=True))
    blocks = ["LUT", "тригери", "лічильники", "компаратор", "ЦАП", "осцилятор"]
    for i, b in enumerate(blocks):
        y = 80 + i * 38
        p.append(rect(60, y, 180, 30, fill="#eef7ee", stroke=GREEN, sw=1.4))
        p.append(text(150, y + 20, b, size=11, color=GREEN, bold=True))
        p.append(line(240, y + 15, 360, y + 15, color="#dfe3e8", sw=1.2))
    # матриця з'єднань (центр)
    p.append(rect(360, 80, 150, 228, fill="#fafafa", stroke=AMBER, sw=1.8))
    p.append(text(435, 70, "матриця з'єднань", size=11, color="#9a7322", bold=True))
    for i in range(6):
        for j in range(3):
            cx = 385 + j * 50
            cy = 100 + i * 36
            on = (i + j) % 2 == 0
            p.append(dot(cx, cy, color=(GREEN if on else "#d6dbe0"), r=4))
    # GPIO праворуч
    p.append(text(640, 60, "GPIO", size=12, color=INK, bold=True))
    for i in range(6):
        y = 80 + i * 38
        p.append(rect(620, y, 150, 30, fill="#f3f5fd", stroke=BLUE, sw=1.4))
        p.append(text(695, y + 20, "GPIO %d" % (i + 1), size=10, color=BLUE, bold=True))
        p.append(line(510, 95 + i * 36, 620, y + 15, color="#dfe3e8", sw=1.2))
    # NVM унизу
    p.append(rect(360, 312, 150, 22, fill="#fff8e8", stroke=AMBER, sw=1.6))
    p.append(text(435, 327, "NVM (зберігає схему)", size=9, color="#9a7322", bold=True))
    render(os.path.join(OUT, "cmic-inside.svg"), W, H, *p)


# ── 8. config-flow: чотири кроки першої конфігурації (вставка) ─────────────────
def fig_config_flow():
    W, H = 860, 280
    p = []
    steps = [
        ("1. малюємо схему", "у GUI-конструкторі", GREEN),
        ("2. запис по I²C", "схема → у NVM чипа", AMBER),
        ("3. знеструмлення", "конфігурація лишається", BLUE),
        ("4. увімкнули знову", "чип одразу готовий", RED),
    ]
    x = 30
    bw, gap = 190, 20
    for i, (t, sub, col) in enumerate(steps):
        p.append(rect(x, 70, bw, 80, fill="#fafafa", stroke=col, sw=1.7))
        p.append(text(x + bw / 2, 102, t, size=11.5, color=col, bold=True))
        p.append(text(x + bw / 2, 124, sub, size=9.5, color=MUTED))
        if i < 3:
            p.append(arrow(x + bw, 110, x + bw + gap, 110, color=INK, sw=2))
        x += bw + gap
    # контраст МК vs CMIC
    p.append(rect(30, 180, 790, 70, fill="#f7f8fa", stroke=GREY, sw=1.4))
    p.append(text(425, 206, "МК щоразу при старті ВИКОНУЄ програму інструкція за інструкцією,", size=11, color=INK, bold=True))
    p.append(text(425, 228, "а CMIC просто Є потрібною схемою з першої мілісекунди після подачі живлення.", size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "config-flow.svg"), W, H, *p)


if __name__ == "__main__":
    fig_and_or_plane()
    fig_spld_family()
    fig_macrocell()
    fig_cpld_vs_fpga()
    fig_ladder()
    fig_glue()
    fig_cmic_inside()
    fig_config_flow()
    print("OK: figures written to", OUT)
