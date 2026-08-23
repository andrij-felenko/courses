# -*- coding: utf-8 -*-
# Фігури для детальної статті «Від PAL до FPGA» (pal-to-fpga-d.md).
# Окремий генератор, щоб не чіпати figs.py базової статті; вивід у той самий ./img/.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GREY  = "#8a8a8a"
BLUE  = NEG
AMBER = "#b8860b"
GREEN = FIELD
RED   = POS


def dot(cx, cy, color=RED, r=4.5):
    return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s" '
            'stroke-width="1"/>' % (cx, cy, r, color, color))


# ── 1. three-splits: PROM / PLA / PAL — де програмовані точки ──────────────────
def fig_three_splits():
    W, H = 900, 340
    p = []
    cards = [
        ("PROM", GREY,  "AND фікс. (усі 2ⁿ мінтерми)", "OR програмована",
         "добутків завжди 2ⁿ", "гнучко за виходом", "таблиці"),
        ("PLA",  BLUE,  "AND програмована", "OR програмована",
         "два рівні поспіль", "поділ термів між виходами", "найгнучкіше, повільніше"),
        ("PAL",  GREEN, "AND програмована", "OR фікс. (7–8 добутків/вихід)",
         "один рівень", "без поділу термів", "★ швидко й дешево"),
    ]
    x = 24
    cw, gap = 280, 12
    for name, col, androw, orrow, note1, note2, tag in cards:
        p.append(rect(x, 40, cw, 280, fill="#fafafa", stroke=col, sw=1.8))
        cx = x + cw / 2
        p.append(text(cx, 68, name, size=16, color=col, bold=True))
        p.append(line(x + 16, 80, x + cw - 16, 80, color="#e4e4e4", sw=1.3))
        # два ряди-матриці з точками
        p.append(fitbox(x + 24, 96, cw - 48, 30, androw, size=10.5,
                        fill="#f2f6ff", stroke=BLUE, color=INK, bold=True))
        # точковий рядок AND
        for i in range(6):
            on_and = (name != "PROM")  # у PROM AND не програмується
            p.append(dot(x + 40 + i * 40, 138, color=(RED if on_and else "#cfd4da"), r=3.8))
        p.append(fitbox(x + 24, 152, cw - 48, 30, orrow, size=10.5,
                        fill="#eef7ee", stroke=GREEN, color=INK, bold=True))
        for i in range(6):
            on_or = (name != "PAL")   # у PAL OR фіксована
            p.append(dot(x + 40 + i * 40, 194, color=(GREEN if on_or else "#cfd4da"), r=3.8))
        p.append(line(x + 16, 212, x + cw - 16, 212, color="#e4e4e4", sw=1.3))
        p.append(text(cx, 234, note1, size=10, color=MUTED, italic=True))
        p.append(text(cx, 252, note2, size=10, color=MUTED, italic=True))
        p.append(text(cx, 284, tag, size=11, color=col, bold=True))
        x += cw + gap
    p.append(text(W / 2, 22, "хто програмований — червоні точки в AND, зелені в OR", size=11, color=INK, bold=True))
    render(os.path.join(OUT, "three-splits.svg"), W, H, *p)


# ── 2. fuse-mechanism: ціла / перепалена перемичка + «відростання» ─────────────
def fig_fuse_mechanism():
    W, H = 860, 340
    p = []
    # ── ліворуч: ціла
    p.append(text(200, 50, "ціла перемичка", size=13, color=GREEN, bold=True))
    p.append(text(200, 68, "(зв'язок є — лог. 1)", size=10, color=MUTED))
    p.append(line(80, 110, 160, 110, color=INK, sw=2.2))     # лінія входу
    p.append(rect(160, 100, 80, 20, fill="#eef7ee", stroke=GREEN, sw=2, rx=4))
    p.append(line(240, 110, 320, 110, color=INK, sw=2.2))     # до добутку
    p.append(text(200, 114, "▬", size=10, color=GREEN))
    p.append(text(60, 114, "вхід", size=10, color=MUTED, anchor="end"))
    p.append(text(340, 114, "добуток", size=10, color=MUTED, anchor="start"))
    # ── праворуч: перепалена
    p.append(text(650, 50, "після імпульсу", size=13, color=RED, bold=True))
    p.append(text(650, 68, "10–12 В, десятки мкс — зв'язок 0", size=10, color=MUTED))
    p.append(line(530, 110, 610, 110, color=INK, sw=2.2))
    p.append(rect(610, 100, 80, 20, fill="#fdecea", stroke=RED, sw=2, rx=4))
    # розрив
    p.append(line(636, 110, 646, 110, color=BG, sw=6))
    p.append(text(628, 96, "розрив", size=9, color=RED, anchor="start"))
    p.append(line(690, 110, 770, 110, color=INK, sw=2.2))
    p.append(text(510, 114, "вхід", size=10, color=MUTED, anchor="end"))
    p.append(text(790, 114, "добуток", size=10, color=MUTED, anchor="start"))
    p.append(arrow(400, 110, 460, 110, color=INK, sw=2))
    p.append(text(430, 96, "струм", size=9, color=RED))
    # ── унизу: біда нихрому
    p.append(rect(90, 180, 680, 130, fill="#fff8e8", stroke=AMBER, sw=1.6))
    p.append(text(430, 206, "біда нихрому: «відростання» (fuse regrowth)", size=12, color="#9a7322", bold=True))
    # ниточка з містком, що відростає
    p.append(line(200, 250, 400, 250, color=INK, sw=2.2))
    p.append(line(295, 250, 305, 250, color="#fff8e8", sw=6))
    p.append('<path d="M295,250 q5,-10 10,0" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="3 2"/>' % RED)
    p.append(text(300, 234, "місток повзе назад", size=9.5, color=RED))
    p.append(text(430, 284, "розірваний метал із часом з'єднується → 0 повзе в 1;", size=10.5, color=INK))
    p.append(text(430, 300, "перехід на PtSi / TiW цю ваду прибрав. Руйнування необоротне → чип одноразовий.", size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "fuse-mechanism.svg"), W, H, *p)


# ── 3. olmc-detail: начинка вихідної макрокомірки ─────────────────────────────
def fig_olmc_detail():
    W, H = 880, 340
    p = []
    # сума добутків заходить
    p.append(text(70, 150, "сума", size=11, color=GREEN, anchor="start", bold=True))
    p.append(text(70, 166, "добутків", size=11, color=GREEN, anchor="start", bold=True))
    p.append(arrow(150, 158, 210, 158, color=INK, sw=2))
    # тригер (верхня гілка)
    p.append(rect(210, 90, 60, 46, fill="#eef0fb", stroke=BLUE, sw=1.7))
    p.append(text(240, 110, "D", size=11, color=BLUE, bold=True))
    p.append(text(240, 128, "тригер", size=9, color=BLUE, bold=True))
    p.append('<polyline points="214,130 219,124 219,130" fill="none" stroke="%s" stroke-width="1.4"/>' % BLUE)
    # шлях реєстровий і комбінаційний до вихідного MUX
    p.append(line(210, 158, 300, 158, color=INK, sw=1.8))     # комбінаційний прямо
    p.append('<polyline points="270,113 300,113 300,140" fill="none" stroke="%s" stroke-width="1.6"/>' % BLUE)  # реєстровий вниз
    # вихідний MUX
    p.append('<path d="M300,104 L336,118 L336,168 L300,182 Z" fill="#fff8e8" stroke="%s" stroke-width="1.7"/>' % AMBER)
    p.append(text(318, 138, "MUX", size=9, color="#9a7322", bold=True))
    p.append(text(318, 152, "рег/комб", size=8, color=MUTED))
    # XOR полярність
    p.append(circle(378, 143, 16, fill="#f3f5fd", stroke=BLUE, sw=1.6))
    p.append(text(378, 148, "=1", size=10, color=BLUE, bold=True))
    p.append(text(378, 176, "полярність", size=8.5, color=MUTED))
    p.append(line(336, 143, 362, 143, color=INK, sw=1.6))
    # tri-state буфер
    p.append('<path d="M400,128 L432,143 L400,158 Z" fill="#eef7ee" stroke="%s" stroke-width="1.7"/>' % GREEN)
    p.append(text(408, 147, "▷", size=10, color=GREEN))
    p.append(arrow(394, 143, 400, 143, color=INK, sw=1.6))
    p.append(line(416, 128, 416, 116, color=GREEN, sw=1.5))
    p.append(text(416, 108, "OE (добуток)", size=8, color=GREEN, anchor="middle"))
    # пін
    p.append(line(432, 143, 500, 143, color=INK, sw=2))
    p.append(circle(508, 143, 6, fill=BG, stroke=INK, sw=1.8))
    p.append(text(524, 147, "пін", size=11, color=INK, anchor="start", bold=True))
    p.append(text(524, 163, "(вихід або вхід у Hi-Z)", size=9, color=MUTED, anchor="start"))
    # MUX зворотного зв'язку
    p.append('<path d="M470,214 L470,258 L434,244 L434,228 Z" fill="#fff8e8" stroke="%s" stroke-width="1.6"/>' % AMBER)
    p.append(text(452, 240, "MUX", size=8.5, color="#9a7322", bold=True))
    p.append(text(452, 296, "зв'язок назад", size=9, color=MUTED))
    # входи у MUX зв'язку: тригер / пін / сусід
    p.append('<polyline points="240,136 240,236 468,236" fill="none" stroke="%s" stroke-width="1.4" stroke-dasharray="4 3"/>' % GREY)
    p.append(text(250, 232, "вих. тригера", size=8.5, color=MUTED, anchor="start"))
    p.append('<polyline points="508,149 508,250 472,250" fill="none" stroke="%s" stroke-width="1.4" stroke-dasharray="4 3"/>' % GREY)
    p.append(text(500, 268, "пін (двонапр.)", size=8.5, color=MUTED, anchor="middle"))
    # повернення в матрицю AND
    p.append('<polyline points="434,236 120,236 120,168 148,168" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="4 3"/>' % GREY)
    p.append(text(120, 252, "→ у матрицю AND (для автомата)", size=9, color=MUTED, anchor="start"))
    p.append(text(W / 2, 26, "OLMC: чотири перемикачі роблять один вихід універсальним", size=12, color=INK, bold=True))
    render(os.path.join(OUT, "olmc-detail.svg"), W, H, *p)


# ── 4. cpld-timing: центральна матриця → однаковий шлях кожному сигналу ────────
def fig_cpld_timing():
    W, H = 880, 380
    p = []
    p.append(rect(24, 40, 540, 320, fill="#fbfbfb", stroke=BLUE, sw=1.6))
    p.append(text(294, 64, "CPLD: усі сигнали крізь ту саму центральну матрицю", size=12, color=BLUE, bold=True))
    # центральна матриця
    p.append(rect(224, 158, 140, 44, fill="#eef0fb", stroke=BLUE, sw=1.8))
    p.append(text(294, 179, "центральна", size=10, color=BLUE, bold=True))
    p.append(text(294, 194, "матриця", size=10, color=BLUE, bold=True))
    cy_m = 180
    blocks = [(60, 90), (400, 90), (60, 232), (400, 232)]
    for i, (bx, by) in enumerate(blocks):
        p.append(rect(bx, by, 104, 50, fill="#eef7ee", stroke=GREEN, sw=1.6))
        p.append(text(bx + 52, by + 21, "PAL-блок", size=10, color=GREEN, bold=True))
        p.append(text(bx + 52, by + 38, "AND·OR·макро", size=8.5, color=MUTED))
        col = RED if i in (0, 3) else GREY
        sww = 1.9 if i in (0, 3) else 1.2
        ax = bx + 52
        ay = by + (50 if by < cy_m else 0)
        p.append(line(ax, ay, 294, cy_m, color=col, sw=sww))
    p.append(line(24 + 8, 300, 564 - 8, 300, color="#e4e4e4", sw=1.2))
    p.append(text(294, 320, "t_PD — стала, одне число в даташиті (напр. 5 нс)", size=10.5, color=GREEN, bold=True))
    p.append(text(294, 337, "джитера немає: шляхи різні, а довжина в ланках однакова", size=9.5, color=MUTED, italic=True))
    p.append(text(294, 354, "конфіг у власній EEPROM/флеші → готовий із 1-ї мс", size=10, color=INK, bold=True))
    # ── контраст FPGA праворуч
    p.append(rect(584, 40, 272, 320, fill="#fff8f6", stroke=RED, sw=1.4))
    p.append(text(720, 64, "FPGA — для контрасту", size=12, color=RED, bold=True))
    gx0, gy0, cell, gapc = 610, 90, 26, 12
    for r in range(5):
        for c in range(5):
            cx = gx0 + c * (cell + gapc)
            cy = gy0 + r * (cell + gapc)
            p.append(rect(cx, cy, cell, cell, fill="#fdecea", stroke=RED, sw=1.0, rx=3))
    # звивистий шлях
    p.append('<polyline points="623,103 661,103 661,141 737,141 737,217 775,217" fill="none" stroke="%s" stroke-width="2.4"/>' % RED)
    p.append(text(720, 300, "шлях крізь невідоме число перемикачів", size=9.5, color=RED, bold=True))
    p.append(text(720, 318, "→ затримка «плаває», єдиного t_PD нема", size=9.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "cpld-timing.svg"), W, H, *p)


# ── 5. routing-scaling: чому лінійне росте, а квадратичне впирається ───────────
def fig_routing_scaling():
    W, H = 880, 380
    p = []
    # ── ліворуч CPLD: центральна матриця
    p.append(rect(24, 40, 400, 300, fill="#fbfbfb", stroke=BLUE, sw=1.6))
    p.append(text(224, 64, "CPLD: одна центральна матриця", size=12, color=BLUE, bold=True))
    p.append(rect(150, 170, 148, 60, fill="#eef0fb", stroke=BLUE, sw=1.8))
    p.append(text(224, 196, "матриця", size=11, color=BLUE, bold=True))
    p.append(text(224, 214, "~ входи × виходи", size=9.5, color=MUTED))
    pts = [(70, 90), (224, 84), (378, 90), (60, 300), (224, 306), (388, 300), (60, 195), (388, 195)]
    for bx, by in pts:
        p.append(rect(bx - 26, by - 14, 52, 28, fill="#eef7ee", stroke=GREEN, sw=1.3))
        p.append(text(bx, by + 4, "блок", size=8.5, color=GREEN, bold=True))
        p.append(line(bx, by + (14 if by < 200 else -14) if by != 195 else by,
                      224, 200, color="#cfd4da", sw=1.0))
    p.append(text(224, 328, "складність росте квадратично → стеля ємності", size=10, color=RED, bold=True))
    # ── праворуч FPGA: локальні switch box
    p.append(rect(456, 40, 400, 300, fill="#fbfbfb", stroke=GREEN, sw=1.6))
    p.append(text(656, 64, "FPGA: локальні switch box'и", size=12, color=GREEN, bold=True))
    gx0, gy0, cell, gapc = 500, 96, 32, 22
    cols, rowsn = 6, 5
    for r in range(rowsn):
        for c in range(cols):
            cx = gx0 + c * (cell + gapc)
            cy = gy0 + r * (cell + gapc)
            p.append(rect(cx, cy, cell, cell, fill="#eef7ee", stroke=GREEN, sw=1.1, rx=3))
            if c < cols - 1:
                mx = cx + cell + gapc / 2
                p.append(line(cx + cell, cy + cell / 2, cx + cell + gapc, cy + cell / 2, color="#dfe3e8", sw=1.0))
                p.append(dot(mx, cy + cell / 2, color="#b8c0c8", r=2.4))
            if r < rowsn - 1:
                my = cy + cell + gapc / 2
                p.append(line(cx + cell / 2, cy + cell, cx + cell / 2, cy + cell + gapc, color="#dfe3e8", sw=1.0))
    # червоний звивистий шлях крізь кілька перемикачів
    p.append('<polyline points="516,112 570,112 570,166 678,166 678,220 732,220" fill="none" stroke="%s" stroke-width="2.4"/>' % RED)
    p.append(text(656, 322, "додаєш клітинку — додаєш сталу порцію проводу → росте лінійно", size=9.6, color=GREEN, bold=True))
    p.append(text(656, 300, "шлях крізь різне число перемикачів → затримка залежить від довжини", size=9.3, color=RED, italic=True))
    p.append(text(W / 2, 26, "масштабованість і сталу затримку не мати водночас — два боки одного вибору", size=11, color=INK, bold=True))
    render(os.path.join(OUT, "routing-scaling.svg"), W, H, *p)


if __name__ == "__main__":
    fig_three_splits()
    fig_fuse_mechanism()
    fig_olmc_detail()
    fig_cpld_timing()
    fig_routing_scaling()
    print("OK: detailed figures written to", OUT)
