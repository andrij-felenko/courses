# -*- coding: utf-8 -*-
"""Фігури теми «Фотолітографія». svgkit імпортуємо зі scripts/, не переписуємо."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольори-дані (не тема UI): світло, резист, кремній, маска — лишаємо як акценти
LIGHT  = "#caa24a"   # промінь / засвічене
RESIST = "#f6d6a8"   # фоторезист
RES_ST = "#b8863a"
SI     = "#aebfd8"   # кремній
SI_TX  = "#5a6b86"
DUV    = "#6a3d9a"   # глибокий УФ
GLINE  = "#caa24a"   # видиме / близький УФ


def beam(x, y1, y2, sw=1.8):
    """Промінь світла зі стрілкою донизу."""
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%.1f" marker-end="url(#arrow)"/>' % (x, y1, x, y2, LIGHT, sw))


# ── fig 1: стек літографії ────────────────────────────────────────────────────
# Ідея: світло → маска (хром на кварці) → зменшувальна оптика 4× → резист на Si.
def fig_litho():
    W, H = 720, 380
    p = []

    # джерело світла
    src, sw_w, sw_h = textbox(360, 70, "Джерело світла (UV / EUV)", size=12.5,
                              fill="#fff2cc", stroke=LIGHT, sw=2, bold=True)
    p.append(src)
    for bx in (310, 335, 360, 385, 410):
        p.append(beam(bx, 88, 116))

    # маска: кварц із непрозорим хромом
    p.append(rect(250, 120, 220, 18, fill="#e7e7e7", stroke=INK, sw=2, rx=0))
    for cx, cw in ((250, 30), (310, 24), (370, 18), (420, 26)):
        p.append(rect(cx, 120, cw, 18, fill=INK, stroke=INK, sw=0, rx=0))
    p.append(text(486, 126, "Фотомаска (ретикл)", size=12.5, color=INK, anchor="start", bold=True))
    p.append(text(486, 142, "хром на кварці", size=11.5, color=MUTED, anchor="start"))

    # промені крізь прозорі вікна маски
    for bx in (280, 334, 388, 446):
        p.append(beam(bx, 138, 188))

    # зменшувальна оптика 4×
    p.append('<ellipse cx="360" cy="198" rx="96" ry="20" fill="#dbeafe" stroke="%s" stroke-width="2"/>' % NEG)
    p.append(text(360, 203, "Зменшувальна оптика  4×", size=12, color=NEG, bold=True))

    # збіжні промені до пластини
    for x1, x2 in ((280, 330), (334, 350), (388, 371), (446, 393)):
        p.append('<line x1="%.1f" y1="216" x2="%.1f" y2="270" stroke="%s" stroke-width="1.6" stroke-linecap="round"/>' % (x1, x2, LIGHT))
        p.append('<line x1="%.1f" y1="262" x2="%.1f" y2="278" stroke="%s" stroke-width="1.6" marker-end="url(#arrow)"/>' % (x2, x2, LIGHT))

    # пластина: резист поверх кремнію, засвічені смужки
    p.append(rect(210, 330, 300, 30, fill=SI, stroke=INK, sw=2, rx=0))
    p.append(text(202, 350, "Si", size=13, color=SI_TX, anchor="end", bold=True))
    p.append(rect(210, 300, 300, 30, fill=RESIST, stroke=RES_ST, sw=2, rx=0))
    for ex in (323, 343, 364, 386):
        p.append(rect(ex, 300, 14, 30, fill=LIGHT, stroke=POS, sw=1.5, rx=0))
    p.append(text(520, 318, "Фоторезист", size=12.5, color=RES_ST, anchor="start", bold=True))
    p.append(text(520, 334, "засвічені вікна", size=11.5, color=POS, anchor="start"))

    render(os.path.join(OUT, "litho.svg"), W, H, *p,
           title="Фотолітографія: малюнок переносять світлом")


# ── fig 2: позитивний vs негативний резист ────────────────────────────────────
def fig_resist():
    W, H = 720, 300
    p = []

    def column(x0, head, sub, washed_positive):
        c = []
        cx = x0 + 150
        c.append(text(cx, 58, head, size=14, color=INK, bold=True))
        c.append(text(cx, 76, sub, size=12, color=MUTED))
        # такт 1: суцільний резист під двома засвіченнями
        c.append(rect(x0, 118, 300, 18, fill=SI, stroke=INK, sw=1.6, rx=0))
        c.append(rect(x0, 96, 300, 22, fill=RESIST, stroke=RES_ST, sw=1.6, rx=0))
        for bx in (x0 + 90, x0 + 210):
            c.append(beam(bx, 74, 96, sw=1.6))
            c.append(rect(bx - 16, 96, 32, 22, fill=LIGHT, stroke=POS, sw=1.4, rx=0))
        c.append(text(x0 - 8, 108, "1", size=13, color=INK, anchor="end", bold=True))
        c.append(text(x0 + 150, 152, "засвічення", size=11, color=MUTED))
        # такт 2: після проявлення
        c.append(rect(x0, 222, 300, 18, fill=SI, stroke=INK, sw=1.6, rx=0))
        if washed_positive:   # позитив: змивається ЗАСВІЧЕНЕ → лишаються поля поза вікнами
            spans = ((x0, 74), (x0 + 106, 88), (x0 + 226, 74))
        else:                 # негатив: змивається НЕзасвічене → лишаються тільки вікна
            spans = ((x0 + 74, 32), (x0 + 194, 32))
        for sx, sw in spans:
            c.append(rect(sx, 200, sw, 22, fill=RESIST, stroke=RES_ST, sw=1.6, rx=0))
        c.append(text(x0 - 8, 212, "2", size=13, color=INK, anchor="end", bold=True))
        c.append(text(x0 + 150, 256, "після проявлення", size=11, color=MUTED))
        return c

    p += column(40,  "Позитивний", "змивається ЗАСВІЧЕНЕ", True)
    p += column(380, "Негативний", "змивається НЕзасвічене", False)

    render(os.path.join(OUT, "resist.svg"), W, H, *p,
           title="Позитивний і негативний фоторезист")


# ── fig 3: довжина хвилі ───────────────────────────────────────────────────────
# Ідея: коротша хвиля → дрібніший друк. g/i-line → DUV → EUV; частота росте зліва направо.
def fig_wavelength():
    import math
    W, H = 720, 300
    p = []
    baseline = 230.0
    amp = 26.0

    def wave(x0, x1, cycles, color):
        n = 64
        pts = []
        for i in range(n + 1):
            t = i / n
            x = x0 + (x1 - x0) * t
            y = baseline - 40 - amp * math.sin(2 * math.pi * cycles * t)
            pts.append("%.1f,%.1f" % (x, y))
        return '<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts), color)

    p.append(line(40, baseline, 690, baseline, color=INK, sw=1.5))

    # п'ять смуг із дедалі коротшою хвилею (більше циклів = коротша λ)
    bands = [
        (50, 165, 3,  GLINE, "g-line", "436 нм"),
        (165, 280, 4, GLINE, "i-line", "365 нм"),
        (290, 405, 6, DUV,   "KrF (DUV)", "248 нм"),
        (415, 530, 8, DUV,   "ArF (DUV)", "193 нм"),
        (540, 690, 18, NEG,  "EUV", "13.5 нм"),
    ]
    for x0, x1, cyc, col, name, nm in bands:
        p.append(wave(x0, x1, cyc, col))
        cx = (x0 + x1) / 2
        p.append(text(cx, baseline + 22, name, size=12.5, color=INK, bold=True))
        p.append(text(cx, baseline + 40, nm, size=12, color=col, bold=True))

    p.append(text(360, baseline - 92, "довжина хвилі ↓   →   роздільна здатність ↑",
                  size=12.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "wavelength.svg"), W, H, *p,
           title="Чим коротша хвиля, тим дрібніший друк")


# ── fig 4: масштаби чистої кімнати ─────────────────────────────────────────────
def fig_cleanroom():
    W, H = 720, 300
    p = []
    cx = 200.0
    items = [
        (90,  3.0,  FIELD, "Деталь чіпа",  "десятки нм"),
        (146, 7.0,  LIGHT, "Вірус",        "~100 нм"),
        (206, 35.0, POS,   "Дрібний пил",  "~1000 нм (1 мкм)"),
        (270, 100.0, INK,  "Волосина",     "~70 000 нм (70 мкм)"),
    ]
    for cy, r, col, name, sub in items:
        fill = "none" if r >= 100 else col
        p.append(circle(cx, cy, r, fill=fill, stroke=col, sw=2.5))
        p.append(text(360, cy - 4, name, size=13.5, color=INK, anchor="start", bold=True))
        p.append(text(360, cy + 15, sub, size=12, color=col, anchor="start"))

    render(os.path.join(OUT, "cleanroom.svg"), W, H, *p,
           title="Пилинка — гора над транзистором")


# ════════════════════════════════════════════════════════════════════════════
#  Фігури вставок: proj-place-and-route.md  +  hist-asml-euv.md
# ════════════════════════════════════════════════════════════════════════════

# Кольори-дані для вставок (узгоджені зі svgkit-палітрою):
#  POS=червоний (гаряче/довгі дроти), NEG=синій, FIELD=зелений (добре/вихід),
#  LIGHT=бурштин (світло/джерело). Додаткові акценти лишаємо явними, як у базі.
EDA    = "#6b7280"   # сірий — допоміжні етапи конвеєра (MUTED)
PNR    = "#e08030"   # помаранчевий — самі place & route
PURPLE = "#7a3ea8"   # фіолетовий — стрілка-оптимізація, шар via
SN     = "#1f47b5"   # крапля олова (синій)
MO     = "#6a3da0"   # шар молібдену в дзеркалі
SIL    = "#caa24a"   # шар кремнію в дзеркалі / світло


# ── proj fig 1: конвеєр EDA RTL → … → GDSII ────────────────────────────────────
# Ідея: текст логіки крок за кроком перетворюється на геометрію; place&route — у рамці.
def fig_pr_flow():
    W, H = 940, 360
    p = []

    # сім етапів конвеєра однакового розміру; колір = роль кроку
    bx, by, bw, bh, gap = 24, 70, 116, 70, 14
    steps = [
        ("RTL",        "Verilog / VHDL", INK,   "#eef0f2"),
        ("Синтез",     "synthesis",      NEG,   "#eef2fb"),
        ("Floorplan",  "план площі",     NEG,   "#eef2fb"),
        ("Розміщення", "placement",      PNR,   "#fdf0e2"),
        ("Трасування", "routing",        PNR,   "#fdf0e2"),
        ("Перевірки",  "DRC / LVS / STA", NEG,  "#eef2fb"),
        ("GDSII",      "OASIS",          FIELD, "#e9f6ec"),
    ]
    xs = []
    for i, (head, sub, col, fill) in enumerate(steps):
        x = bx + i * (bw + gap)
        xs.append(x)
        p.append(rect(x, by, bw, bh, fill=fill, stroke=col, sw=2, rx=8))
        p.append(text(x + bw / 2, by + 30, head, size=14, color=col, bold=True))
        p.append(text(x + bw / 2, by + 50, sub, size=11, color=MUTED))
        if i:                                   # стрілка від попереднього блоку
            xp = xs[i - 1] + bw
            p.append(arrow(xp + 1, by + bh / 2, x - 1, by + bh / 2, color=INK, sw=2))

    # рамка place & route навколо двох середніх кроків (Розміщення+Трасування)
    fx0 = xs[3] - 8
    fx1 = xs[4] + bw + 8
    p.append(rect(fx0, by - 16, fx1 - fx0, bh + 32, fill="none", stroke=PNR, sw=2.2, rx=10))
    p.append(text((fx0 + fx1) / 2, by - 24, "place & route (P&R)", size=13, color=PNR, bold=True))

    # нижня смуга: що тече каналом — нетлист без координат → координати → дроти по шарах
    p.append(text(W / 2, 196, "Що тече конвеєром", size=14, color=MUTED, bold=True))
    panels = [
        (40,  "Нетлист",      "комірки + зв'язки,\nБЕЗ координат",   NEG),
        (360, "Розміщення",   "кожна комірка\nотримала (x, y)",      PNR),
        (640, "Трасування",   "дроти прокладено\nпо шарах металу",   FIELD),
    ]
    pw, py, ph = 260, 214, 124
    cxs = []
    for px, head, body, col in panels:
        cxs.append(px + pw / 2)
        p.append(rect(px, py, pw, ph, fill=BG, stroke=col, sw=1.6, rx=8))
        p.append(text(px + pw / 2, py + 24, head, size=13, color=col, bold=True))
        p.append(mtext(px + pw / 2, py + 46, body, size=11, color=MUTED, lh=1.25))

    # маленькі ілюстрації всередині панелей
    # панель 1: три комірки-блоки, з'єднані лініями без сітки (граф)
    g = [(70, 300, "AND"), (150, 290, "DFF"), (110, 332, "OR")]
    for i in range(len(g) - 1):
        p.append(line(g[i][0] + 24, g[i][1] + 13, g[i + 1][0] + 24, g[i + 1][1] + 13,
                      color=MUTED, sw=1.4))
    for gx, gy, nm in g:
        p.append(rect(gx, gy, 48, 24, fill="#eef2fb", stroke=NEG, sw=1.4, rx=4))
        p.append(text(gx + 24, gy + 17, nm, size=11, color=NEG))
    # панель 2: комірки в рядках (сітка) з координатами
    for ry in (300, 326):
        p.append(line(376, ry + 13, 604, ry + 13, color="#e4e4e4", sw=7))
    for gx, gy, nm in ((392, 300, "AND"), (520, 300, "DFF"), (440, 326, "OR")):
        p.append(rect(gx, gy, 48, 24, fill="#fdf0e2", stroke=PNR, sw=1.4, rx=4))
        p.append(text(gx + 24, gy + 17, nm, size=11, color=PNR))
    # панель 3: комірки + дріт двома шарами через via
    for ry in (300, 326):
        p.append(line(656, ry + 13, 884, ry + 13, color="#e4e4e4", sw=7))
    for gx, gy, nm in ((672, 300, "AND"), (812, 300, "DFF"), (720, 326, "OR")):
        p.append(rect(gx, gy, 48, 24, fill="#e9f6ec", stroke=FIELD, sw=1.4, rx=4))
        p.append(text(gx + 24, gy + 17, nm, size=11, color=FIELD))
    p.append(line(720, 312, 770, 312, color=NEG, sw=2.4))      # метал гор.
    p.append(line(770, 312, 770, 339, color=POS, sw=2.4))      # метал верт.
    p.append(circle(770, 312, 3.2, fill=INK, stroke=INK, sw=1))  # via
    p.append(circle(770, 339, 3.2, fill=INK, stroke=INK, sw=1))

    render(os.path.join(OUT, "pr-flow.svg"), W, H, *p,
           title="Конвеєр EDA: текст логіки → геометрія → набір масок")


# ── proj fig 2: погане vs гарне розміщення ─────────────────────────────────────
def fig_pr_placement():
    W, H = 820, 420
    p = []

    def panel(x0, head, col, cells, wires, wire_col, verdict, vcol):
        c = []
        c.append(text(x0 + 150, 70, head, size=14, color=col, bold=True))
        c.append(rect(x0, 84, 300, 274, fill=BG, stroke=INK, sw=1.8, rx=6))
        # рядки стандартних комірок
        for ry in range(112, 350, 46):
            c.append(line(x0 + 14, ry, x0 + 286, ry, color="#e4e4e4", sw=10))
        # дроти (під комірками)
        for seg in wires:
            x1, y1, x2, y2 = seg
            c.append(line(x0 + x1, y1, x0 + x2, y2, color=wire_col, sw=2.6))
        # комірки A,B,C
        for cx, cy, nm in cells:
            c.append(rect(x0 + cx, cy, 46, 26, fill="#fdf0e2", stroke=PNR, sw=1.8, rx=4))
            c.append(text(x0 + cx + 23, cy + 18, nm, size=12, color=PNR, bold=True))
        c.append(text(x0 + 150, 380, verdict, size=12, color=vcol))
        return c

    # погане: комірки рознесені, довгий червоний ламаний дріт
    bad_cells = [(30, 112, "A"), (220, 204, "B"), (50, 296, "C")]
    bad_wires = [(53, 125, 243, 125), (243, 125, 243, 217),
                 (243, 217, 73, 217), (73, 217, 73, 309)]
    p += panel(40, "Погане розміщення", POS, bad_cells, bad_wires, POS,
               "сумарна довжина дротів ВЕЛИКА → більші затримки", POS)

    # гарне: комірки поруч, короткі зелені дроти
    good_cells = [(96, 204, "A"), (176, 204, "B"), (136, 250, "C")]
    good_wires = [(142, 217, 176, 217), (199, 230, 199, 256), (199, 256, 182, 263)]
    p += panel(480, "Гарне розміщення", FIELD, good_cells, good_wires, FIELD,
               "сумарна довжина дротів МАЛА → швидше й щільніше", FIELD)

    # стрілка-оптимізація між панелями
    p.append(arrow(352, 234, 462, 234, color=PURPLE, sw=2.6))
    p.append(text(407, 222, "цільова функція ↓", size=12, color=PURPLE, bold=True))
    p.append(text(407, 252, "≈ Σ довжин + штраф за перевантаження", size=10, color=PURPLE))

    render(os.path.join(OUT, "pr-placement.svg"), W, H, *p,
           title="Розміщення — оптимізація: коротші дроти, рівне навантаження")


# ── proj fig 3: GDSII — ієрархія ліворуч, стос шарів-полігонів праворуч ─────────
def fig_pr_gdsii():
    W, H = 880, 430
    p = []

    # ── ліворуч: псевдо-вміст GDSII (моноширинні рядки) ──
    mono = "Consolas, 'DejaVu Sans Mono', monospace"

    def code(x, y, s, color=INK, bold=False):
        return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="12" fill="%s" '
                'text-anchor="start"%s>%s</text>'
                % (x, y, mono, color, ' font-weight="700"' if bold else '', esc(s)))

    cx0 = 36
    p.append(text(cx0, 64, "Що всередині GDSII (спрощено):", size=13, color=INK,
                  anchor="start", bold=True))
    lines = [
        ("STRUCTURE  cpu_top",            INK,    True),
        ("  SREF  alu_cell   @(0,0)",     MUTED,  False),
        ("  SREF  alu_cell   @(12,0)  ← повтор", PURPLE, False),
        ("  STRUCTURE  alu_cell",         INK,    True),
        ("    BOUNDARY layer=ACTIVE  [полігон]", FIELD, False),
        ("    BOUNDARY layer=POLY    [полігон]", POS,   False),
        ("    BOUNDARY layer=METAL1  [полігон]", NEG,   False),
        ("    PATH     layer=METAL2  [дріт]",    PNR,   False),
    ]
    y = 90
    for s, col, bold in lines:
        p.append(code(cx0 + 6, y, s, color=col, bold=bold))
        y += 22
    p.append(text(cx0 + 6, y + 12, "координати в нанометрах; одну комірку",
                  size=11, color=MUTED, anchor="start"))
    p.append(text(cx0 + 6, y + 28, "ставлять багато разів через посилання",
                  size=11, color=MUTED, anchor="start"))
    p.append(text(cx0 + 6, y + 44, "(ієрархія, без копій).",
                  size=11, color=MUTED, anchor="start"))

    # ── праворуч: стос шарів як паралелограми-полігони ──
    p.append(text(640, 64, "стос шарів = опис кристала", size=13, color=INK,
                  anchor="start", bold=True))
    p.append(text(640, 82, "кожен шар → окрема фотомаска", size=11, color=MUTED, anchor="start"))

    layers = [   # знизу (METAL2) вгору (ACTIVE)
        ("ACTIVE",  FIELD,  "#e9f6ec"),
        ("POLY",    POS,    "#fbeae8"),
        ("CONTACT", MUTED,  "#efefef"),
        ("METAL1",  NEG,    "#eef2fb"),
        ("VIA1",    PURPLE, "#f1eafa"),
        ("METAL2",  PNR,    "#fdf0e2"),
    ]
    # геометрія паралелограма: ширина 210, висота шару 30, зсув по діагоналі
    pw, lh, sx, sy = 210, 30, 22, 22
    base_x, base_y = 470, 110          # лівий-верхній кут найвищого шару (ACTIVE)
    for i, (nm, col, fill) in enumerate(layers):
        ox = base_x - i * sx
        oy = base_y + i * sy
        pts = "%.0f,%.0f %.0f,%.0f %.0f,%.0f %.0f,%.0f" % (
            ox + sx, oy, ox + sx + pw, oy, ox + pw, oy + lh, ox, oy + lh)
        p.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="1.8"/>'
                 % (pts, fill, col))
        # три полігончики-вікна всередині шару
        for k in range(3):
            wx = ox + 34 + k * 58
            p.append(rect(wx, oy + 6, 30, 18, fill=BG, stroke=col, sw=1.4, rx=0))
        p.append(text(ox + sx - 6, oy + 20, nm, size=11, color=col, anchor="end", bold=True))

    # стрілка вниз до фотомаски (нижче за весь стос шарів)
    stack_bottom = base_y + (len(layers) - 1) * sy + lh   # нижній край METAL2
    arr_x = base_x - (len(layers) - 1) * sx + 70
    arr_y = stack_bottom + 14
    p.append(arrow(arr_x, arr_y, arr_x, arr_y + 28, color=INK, sw=2))
    p.append(text(arr_x + 14, arr_y + 22, "кожен шар → окрема фотомаска",
                  size=12, color=INK, anchor="start"))
    # сама фотомаска (темні смуги)
    mx, my = arr_x - 52, arr_y + 36
    p.append(rect(mx, my, 104, 32, fill="#f3f3f3", stroke=INK, sw=1.8, rx=3))
    for k in range(4):
        p.append(rect(mx + 8 + k * 24, my + 6, 12, 20, fill=INK, stroke="none", sw=0, rx=0))
    p.append(text(mx + 52, my + 48, "фотомаска (reticle)", size=11, color=MUTED))

    render(os.path.join(OUT, "pr-gdsii.svg"), W, H, *p,
           title="GDSII: чіп як полігони на шарах — кожен шар стає маскою")


# ── hist fig 1: вертикальна хронологія EUV ─────────────────────────────────────
def fig_euv_timeline():
    W, H = 940, 760
    p = []

    axis_x = 232
    p.append(line(axis_x, 84, axis_x, 736, color=MUTED, sw=3))

    # колір вузла: синій=наука/ідея, бурштин=гроші/масштаб, зелений=машина/виробництво
    events = [
        (118, "сер. 1980-х", NEG,
         "Кіношіта (NTT, Японія) висуває ідею",
         ["Хіроо Кіношіта (Hiroo Kinoshita) пропонує літографію в м'якому",
          "рентгені; 1986-го вперше фокусує EUV-зображення дзеркалами"]),
        (192, "1980-ті", NEG,
         "Андервуд і Барбі — перші багатошарові дзеркала",
         ["Джим Андервуд (Jim Underwood) і Трой Барбі (Troy Barbee) роблять",
          "перші Mo/Si-дзеркала, що відбивають EUV — без них ідея мертва"]),
        (272, "сер. 1980-х", NEG,
         "Bell Labs пробує плазмове джерело",
         ["Оберт Вуд (Obert Wood) і Білл Сілфваст (Bill Silfvast) запускають",
          "лазерну плазму як джерело EUV; Рік Фрімен вводить термін",
          "«EUV-літографія»"]),
        (356, "1992–94", SIL,
         "Intel і нацлабораторії США беруться всерйоз",
         ["Intel вкладає сотні мільйонів; Лівермор, Сандія, Берклі",
          "(Livermore, Sandia, Berkeley) ведуть роботу під DARPA/DOE"]),
        (430, "1997", SIL,
         "консорціум EUV-LLC",
         ["Intel збирає коаліцію (AMD, Motorola, IBM, Micron) і фінансує",
          "нацлабораторії — переносить науку ближче до виробництва"]),
        (504, "кінець 1990-х", FIELD,
         "ASML бере EUV у роботу",
         ["Європейська ASML ставить на EUV як наступника DUV; партнерство",
          "з Zeiss по оптиці й Cymer по джерелу світла"]),
        (584, "2012", FIELD,
         "Zeiss віддає ASML першу штатну оптику",
         ["Карл Цайс (Zeiss) розв'язує найстрашнішу задачу — дзеркала",
          "такої гладкості, що оптика перестає бути головним бар'єром"]),
        (664, "2013", FIELD,
         "ASML купує Cymer; джерело пробиває ~10 Вт",
         ["Cymer додає попередній імпульс, що розплескує краплю олова,",
          "і потужність нарешті росте; того ж року ASML купує Cymer"]),
        (728, "2018–2019", FIELD,
         "EUV у серійному виробництві",
         ["Перші чіпи масово друкують на EUV (Samsung, TSMC).",
          "Понад 30 років роботи дають робочу машину"]),
    ]
    for cy, when, col, head, body in events:
        p.append(circle(axis_x, cy, 7, fill=BG, stroke=col, sw=2.6))
        p.append(text(axis_x - 22, cy + 5, when, size=12, color=MUTED, anchor="end", bold=True))
        p.append(text(axis_x + 26, cy - 3, head, size=14, color=col, anchor="start", bold=True))
        ty = cy + 15
        for ln in body:
            p.append(text(axis_x + 26, ty, ln, size=11, color=INK, anchor="start", italic=True))
            ty += 16

    render(os.path.join(OUT, "euv-timeline.svg"), W, H, *p,
           title="Довгий шлях EUV: від ідеї середини 1980-х до фабрики 2019-го")


# ── hist fig 2: один цикл джерела світла EUV ───────────────────────────────────
def fig_euv_source():
    import math
    W, H = 940, 420
    p = []

    p.append(text(70, 92, "Один цикл — і так близько 50 000 разів за секунду:",
                  size=13, color=INK, anchor="start", bold=True))

    base = 168.0   # лінія, по якій летить крапля

    # 1. летить крапля
    p.append(arrow(120, base, 148, base, color=INK, sw=2))
    p.append(circle(170, base, 13, fill="#dfe3ea", stroke=SN, sw=2))
    p.append(text(170, base + 4, "Sn", size=11, color=SN, bold=True))
    p.append(text(170, base + 62, "1. летить крапля", size=13, color=INK, bold=True))
    p.append(text(170, base + 84, "розплавлене олово,", size=11, color=MUTED))
    p.append(text(170, base + 100, "крапля ~25–30 мкм", size=11, color=MUTED))

    # 2. попередній імпульс розплескує в «млинець»
    p.append(arrow(300, base, 392, base, color=POS, sw=2.4))
    p.append(text(346, base - 12, "слабкий", size=10, color=POS))
    # млинець — приплюснутий еліпс
    p.append('<ellipse cx="430" cy="%.0f" rx="26" ry="9" fill="#dfe3ea" stroke="%s" '
             'stroke-width="2"/>' % (base, SN))
    p.append(text(430, base + 62, "2. попередній імпульс", size=13, color=POS, bold=True))
    p.append(text(430, base + 84, "крапля стає пласким", size=11, color=MUTED))
    p.append(text(430, base + 100, "«млинцем» — більша ціль", size=11, color=MUTED))

    # 3. головний імпульс CO2 → плазма світить на 13.5 нм
    p.append(arrow(560, base, 662, base, color=POS, sw=3.4))
    p.append(text(611, base - 12, "потужний", size=10, color=POS))
    p.append(text(611, base - 28, "CO₂-лазер", size=10, color=POS, bold=True))
    # спалах плазми
    fx, fy = 700, base
    p.append(circle(fx, fy, 22, fill="#fff3d6", stroke="none", sw=0))
    p.append(circle(fx, fy, 15, fill="#ffe8a8", stroke="none", sw=0))
    p.append(circle(fx, fy, 8, fill=BG, stroke=SIL, sw=2))
    for k in range(12):
        a = math.radians(k * 30)
        r1, r2 = 24, 38
        p.append(line(fx + r1 * math.cos(a), fy + r1 * math.sin(a),
                      fx + r2 * math.cos(a), fy + r2 * math.sin(a),
                      color=SIL, sw=2))
    p.append(text(700, base + 62, "3. головний імпульс", size=13, color=POS, bold=True))
    p.append(text(700, base + 84, "плазма ~ десятки тисяч °C", size=11, color=MUTED))
    p.append(text(700, base + 100, "світить на 13.5 нм (EUV)", size=11, color=SIL, bold=True))

    # нижня рамка-пояснення (fitbox під заданий блок)
    bx, by, bw = 70, base + 132, 800
    p.append(fitbox(bx, by, bw, 28, "Чому так дивно, а не просто «увімкнути лампу»?",
                    size=13, fill="#fbf7ee", stroke=SIL, sw=1.6, bold=True))
    notes = [
        "• На 13.5 нм не світить жодна лампа й жоден лазер — цю хвилю доводиться добувати з гарячої плазми.",
        "• Мегаватний CO₂-лазер влучає в КОЖНУ краплю; попередній імпульс спершу розплескує її, щоб віддача світла зросла.",
        "• Лише ~кілька відсотків енергії лазера стає корисним EUV — решта йде в тепло; звідси гігантські лазер і охолодження.",
    ]
    ny = by + 52
    for n in notes:
        p.append(text(bx + 12, ny, n, size=11, color=INK, anchor="start"))
        ny += 20

    render(os.path.join(OUT, "euv-source.svg"), W, H, *p,
           title="Світло 13.5 нм: крапля олова під подвійним пострілом лазера")


# ── hist fig 3: чому дзеркала + бюджет світла (11 відбивань → ~2%) ──────────────
def fig_euv_budget():
    W, H = 940, 470
    p = []

    # ── ліворуч: чому не лінзи ──
    bx, by, bw, bh = 40, 70, 300, 300
    p.append(rect(bx, by, bw, bh, fill="#f5f7fb", stroke=NEG, sw=1.8, rx=12))
    p.append(text(bx + bw / 2, by + 26, "Чому НЕ лінзи (як у DUV)", size=13, color=NEG, bold=True))
    why = [
        ("EUV (13.5 нм) поглинає все:", False),
        ("   повітря, скло лінзи, плівка.", False),
        ("Промінь крізь лінзу згас би.", False),
        ("Тому: лише ВІДБИВАННЯ,", True),
        ("   дзеркалами Mo/Si.", False),
        ("І весь шлях — у ВАКУУМІ,", True),
        ("   бо повітря з'їло б промінь.", False),
    ]
    wy = by + 52
    for s, bold in why:
        pre = "• " if not s.startswith("   ") else ""
        p.append(text(bx + 18, wy, pre + s, size=11, color=INK, anchor="start", bold=bold))
        wy += 22
    # дзеркало Mo/Si: пари смуг
    p.append(text(bx + bw / 2, by + 224, "дзеркало = ~40–50 пар шарів Mo/Si",
                  size=10, color=MUTED))
    sx0 = bx + 50
    for k in range(10):
        col = MO if k % 2 == 0 else SIL
        p.append(rect(sx0 + k * 14, by + 234, 12, 14, fill=col, stroke="none", sw=0, rx=1))
    p.append(text(bx + bw / 2, by + 272, "відбиває лише ~70% навіть у теорії",
                  size=10, color=MUTED))

    # ── праворуч: бюджет світла, 11 відбивань ──
    p.append(text(640, 100, "Бюджет світла: 11 відбивань поспіль", size=13, color=INK, bold=True))
    p.append(text(640, 120, "кожне відбивання забирає ~30% — втрати множаться",
                  size=10, color=MUTED))

    # стовпчики спадної висоти; підпис під базовою лінією (вище за підсумок)
    baseY = 350
    bars = [
        (380, "100%", "джерело",                SIL,   210),
        (520, "24%",  "4 дзеркала-\nконденсори", NEG,    50),
        (660, "17%",  "маска\n(теж дзеркало)",   POS,    36),
        (800, "2%",   "6 дзеркал\nпроєкції",     FIELD,   8),
    ]
    for bx2, lab, sub, col, hgt in bars:
        top = baseY - hgt
        p.append(rect(bx2, top, 120, hgt, fill=BG, stroke=col, sw=2, rx=6))
        p.append(rect(bx2, top, 120, min(20, hgt), fill=col, stroke="none", sw=0, rx=6))
        p.append(text(bx2 + 60, baseY + 22, lab, size=14, color=col, bold=True))
        p.append(mtext(bx2 + 60, baseY + 40, sub, size=10, color=INK, lh=1.2))
    # стрілки між стовпчиками (на рівні базової лінії)
    for bx2 in (380, 520, 660):
        p.append(arrow(bx2 + 122, baseY - 8, bx2 + 138, baseY - 8, color=MUTED, sw=2))

    # підсумкова смуга — знизу, з відступом від підписів стовпчиків
    sb_x, sb_y, sb_w = 40, 416, 860
    p.append(rect(sb_x, sb_y, sb_w, 46, fill="#f4f7f4", stroke=FIELD, sw=1.6, rx=10))
    p.append(text(sb_x + sb_w / 2, sb_y + 20,
                  "Підсумок: до пластини доходить лише ~2% світла джерела —",
                  size=12, color=INK, bold=True))
    p.append(text(sb_x + sb_w / 2, sb_y + 38,
                  "тому джерело мусить бути шалено потужним, а машина — гігантською.",
                  size=12, color=INK, bold=True))

    render(os.path.join(OUT, "euv-budget.svg"), W, H, *p,
           title="EUV — лише дзеркала у вакуумі, і куди дівається 98% світла")


# ════════════════════════════════════════════════════════════════════════════
#  Фігури детальної статті: photolithography-d.md
# ════════════════════════════════════════════════════════════════════════════

# ── d fig 1: NA й дифракція — ширша лінза ловить крутіші промені ────────────────
# Ідея: дрібний візерунок розкидає світло під великими кутами; вузька лінза їх
# не ловить (деталь зникає), ширша (зокрема із зануренням) — ловить.
def fig_na_diffraction():
    import math
    W, H = 760, 380
    p = []

    def panel(cx, half_angle_deg, label, sub, col, capture_ok):
        c = []
        mask_y, lens_y, wafer_y = 96, 200, 320
        # маска з дрібним візерунком (джерело дифракції)
        c.append(rect(cx - 70, mask_y - 10, 140, 14, fill="#e7e7e7", stroke=INK, sw=1.6, rx=0))
        for k in range(-3, 4):
            c.append(rect(cx + k * 18 - 4, mask_y - 10, 8, 14, fill=INK, stroke=INK, sw=0, rx=0))
        c.append(text(cx, mask_y - 18, "дрібний візерунок", size=11, color=MUTED))
        # дифраговані промені віялом від центра маски
        for ang in (-40, -22, 0, 22, 40):
            rad = math.radians(ang)
            x2 = cx + (lens_y - mask_y) * math.tan(rad)
            caught = abs(ang) <= half_angle_deg + 0.5
            colr = SIL if caught else "#d9c7a0"
            c.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%.1f"/>'
                     % (cx, mask_y + 4, x2, lens_y, colr, 2.0 if caught else 1.2))
        # лінза — ширина = апертура
        half_w = (lens_y - mask_y) * math.tan(math.radians(half_angle_deg))
        c.append('<ellipse cx="%.1f" cy="%d" rx="%.1f" ry="14" fill="#dbeafe" stroke="%s" stroke-width="2.2"/>'
                 % (cx, lens_y, half_w, col))
        c.append(text(cx, lens_y + 5, "лінза", size=11.5, color=col, bold=True))
        # пластина
        c.append(rect(cx - 70, wafer_y, 140, 16, fill=SI, stroke=INK, sw=1.6, rx=0))
        # результат на пластині
        if capture_ok:
            for k in range(-3, 4):
                c.append(rect(cx + k * 18 - 4, wafer_y, 8, 16, fill=LIGHT, stroke=POS, sw=1.2, rx=0))
            c.append(text(cx, wafer_y + 34, "образ є — деталь надрукована", size=11.5, color=FIELD, bold=True))
        else:
            c.append(rect(cx - 40, wafer_y + 4, 80, 8, fill="#efe6d2", stroke="#cdbf9c", sw=1.0, rx=2))
            c.append(text(cx, wafer_y + 34, "промені втрачено — деталь зникла", size=11.5, color=POS, bold=True))
        c.append(text(cx, 58, label, size=14, color=col, bold=True))
        c.append(text(cx, 76, sub, size=11.5, color=MUTED))
        return c

    p += panel(190, 22, "Вузька апертура", "мала NA", POS, False)
    p += panel(560, 40, "Широка апертура / занурення", "велика NA", FIELD, True)
    p.append(line(375, 90, 375, 350, color="#e0e0e0", sw=1.2, dash="4 5"))

    render(os.path.join(OUT, "na-diffraction.svg"), W, H, *p,
           title="Числова апертура: ширша лінза ловить крутіші дифраговані промені")


# ── d fig 2: мультипатернінг LELE vs SADP ──────────────────────────────────────
# Ідея: один спалах не кладе лінії досить часто; два проходи (LELE) або спейсери
# на стінках риштування (SADP) подвоюють щільність.
def fig_multipatterning():
    W, H = 820, 430
    p = []
    sub_y, line_h = 300, 22

    def substrate(x0):
        return rect(x0, sub_y, 220, 16, fill=SI, stroke=INK, sw=1.6, rx=0)

    def bar(x, w, fill, stroke):
        return rect(x, sub_y - line_h, w, line_h, fill=fill, stroke=stroke, sw=1.4, rx=0)

    # ── LELE: дві маски в проміжки одна одної ──
    p.append(text(220, 70, "LELE — літо-травлення ×2", size=14, color=NEG, bold=True))
    p.append(text(220, 88, "дві маски, лінії другої лягають у проміжки першої", size=11, color=MUTED))
    # крок 1: рідкі лінії маски A
    p.append(substrate(110))
    for i in range(3):
        p.append(bar(130 + i * 64, 16, "#eef2fb", NEG))
    p.append(text(96, sub_y - 8, "A", size=12, color=NEG, anchor="end", bold=True))
    p.append(text(360, sub_y - 8, "1. перша маска (рідко)", size=11, color=MUTED, anchor="start"))
    # крок 2: додано лінії маски B між ними
    sub2 = sub_y + 78
    p.append(rect(110, sub2, 220, 16, fill=SI, stroke=INK, sw=1.6, rx=0))
    for i in range(3):
        p.append(rect(130 + i * 64, sub2 - line_h, 16, line_h, fill="#eef2fb", stroke=NEG, sw=1.4, rx=0))
    for i in range(3):
        p.append(rect(162 + i * 64, sub2 - line_h, 16, line_h, fill="#fbeae8", stroke=POS, sw=1.4, rx=0))
    p.append(text(96, sub2 - 8, "B", size=12, color=POS, anchor="end", bold=True))
    p.append(text(360, sub2 - 8, "2. друга маска у проміжки → вдвічі щільніше", size=11, color=MUTED, anchor="start"))
    p.append(text(220, sub2 + 28, "слабке місце: точність сполучення масок (overlay)", size=10.5, color=POS))

    # ── SADP: спейсери на стінках риштування ──
    bx = 470
    p.append(text(bx + 130, 70, "SADP — самовирівнювані спейсери", size=14, color=FIELD, bold=True))
    p.append(text(bx + 130, 88, "спейсери ростуть на стінках риштування — без другої маски", size=11, color=MUTED))
    # крок 1: риштування (mandrel)
    p.append(rect(bx, sub_y, 260, 16, fill=SI, stroke=INK, sw=1.6, rx=0))
    for i in range(2):
        p.append(rect(bx + 40 + i * 110, sub_y - line_h, 50, line_h, fill="#efe6d2", stroke="#b8863a", sw=1.4, rx=0))
    p.append(text(bx + 130, sub_y + 30, "1. риштування (mandrel)", size=11, color=MUTED))
    # крок 2: спейсери по боках + риштування витравлено
    sub2b = sub_y + 78
    p.append(rect(bx, sub2b, 260, 16, fill=SI, stroke=INK, sw=1.6, rx=0))
    for i in range(2):
        base = bx + 40 + i * 110
        p.append(rect(base - 8, sub2b - line_h, 8, line_h, fill="#e9f6ec", stroke=FIELD, sw=1.4, rx=0))
        p.append(rect(base + 50, sub2b - line_h, 8, line_h, fill="#e9f6ec", stroke=FIELD, sw=1.4, rx=0))
    p.append(text(bx + 130, sub2b + 30, "2. риштування геть → лишились 2× спейсери", size=11, color=MUTED))
    p.append(text(bx + 130, sub2b + 48, "самовирівняні — менший розкид", size=10.5, color=FIELD))

    p.append(line(410, 60, 410, 400, color="#e0e0e0", sw=1.2, dash="4 5"))

    render(os.path.join(OUT, "multipatterning.svg"), W, H, *p,
           title="Друк дрібніше за один спалах: LELE та SADP")


if __name__ == "__main__":
    fig_litho()
    fig_resist()
    fig_wavelength()
    fig_cleanroom()
    fig_pr_flow()
    fig_pr_placement()
    fig_pr_gdsii()
    fig_euv_timeline()
    fig_euv_source()
    fig_euv_budget()
    fig_na_diffraction()
    fig_multipatterning()
    print("ok: litho, resist, wavelength, cleanroom, "
          "pr-flow, pr-placement, pr-gdsii, euv-timeline, euv-source, euv-budget, "
          "na-diffraction, multipatterning")
