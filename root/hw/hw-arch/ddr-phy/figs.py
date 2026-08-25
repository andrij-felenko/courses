# -*- coding: utf-8 -*-
"""Фігури до теми «DDR PHY: фізичний рівень DDR-інтерфейсу».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Де сидить PHY: між контролером і чіпом пам'яті ────────────────────────
def fig_place():
    W, H = 830, 430
    frags = []
    yb = 130  # рівень центрів верхніх блоків

    # три великі блоки у верхній смузі
    b, w1, h1 = textbox(135, yb, "Контролер\nпам'яті\n(широка шина,\nповільний\nядровий такт)",
                        size=14, fill="#eef2ff", stroke=NEG, bold=False, pad=14)
    frags.append(b)
    b, w2, h2 = textbox(415, yb, "DDR PHY\n(мішана\nаналого-\nцифрова частина)",
                        size=15, fill="#eafaf1", stroke=FIELD, bold=True, pad=16)
    frags.append(b)
    b, w3, h3 = textbox(695, yb, "Чіп DRAM\n(вузька шина,\nшвидкі фронти\nна ніжках)",
                        size=14, fill="#fdf2f2", stroke=POS, pad=14)
    frags.append(b)

    # стрілки-шини (пряма — запис, зворотна — читання)
    frags.append(arrow(135 + w1/2, yb-18, 415 - w2/2, yb-18, color=INK, sw=2))
    frags.append(text((135+w1/2 + 415-w2/2)/2, yb-42, "паралельно, за один", size=11, color=MUTED))
    frags.append(text((135+w1/2 + 415-w2/2)/2, yb-27, "ядровий такт — багато бітів", size=11, color=MUTED))
    frags.append(arrow(415 + w2/2, yb-18, 695 - w3/2, yb-18, color=INK, sw=2))
    frags.append(text((415+w2/2 + 695-w3/2)/2, yb-42, "послідовно, DQ + строб DQS", size=11, color=MUTED))
    frags.append(text((415+w2/2 + 695-w3/2)/2, yb-27, "двічі за такт, на обох фронтах", size=11, color=MUTED))
    frags.append(arrow(695 - w3/2, yb+22, 415 + w2/2, yb+22, color=MUTED, sw=1.6))
    frags.append(arrow(415 - w2/2, yb+22, 135 + w1/2, yb+22, color=MUTED, sw=1.6))
    frags.append(text(415, yb+40, "читання: дані й строб ідуть тим самим шляхом назад", size=11, color=MUTED))

    # окрема рамка «усередині PHY», з'єднана з блоком PHY
    inner = ["серіалізатор / десеріалізатор — збирає широке слово у вузький потік і назад",
             "DLL + лінії затримки — рухають фронти, тримають зсув 90° попри зміни PVT",
             "лінійні драйвери й приймачі — формують і ловлять швидкі фронти на ніжках",
             "термінатори ODT та опора VREF — гасять відбиття, задають поріг рішення",
             "логіка тренування й вирівнювання — сама шукає правильні затримки"]
    bx, by, bw, bh = 90, 250, 650, 150
    frags.append(rect(bx, by, bw, bh, fill="#f7fdfa", stroke=FIELD, sw=1.4))
    frags.append(line(415, yb + h2/2, 415, by, color=FIELD, sw=1.4, dash="4,4"))
    frags.append(text(bx + 16, by + 24, "що робить PHY усередині:", size=12.5, color=FIELD, bold=True, anchor="start"))
    for i, s in enumerate(inner):
        frags.append(text(bx + 16, by + 48 + i*20, "• " + s, size=11, color=INK, anchor="start"))

    render(os.path.join(IMG, "phy-place.svg"), W, H, *frags,
           title="PHY — перекладач між широкою повільною шиною і вузькою швидкою")


# ── 2. Головна ідея: строб треба посадити в центр ока ───────────────────────
def _wave(x0, y_hi, y_lo, unit, pattern, sw=2.2, color=INK, skew=0.0):
    """Прямокутна хвиля: pattern — рядок з '1'/'0'. skew — зсув по x у частках unit."""
    dx = skew * unit
    pts = []
    x = x0 + dx
    prev = None
    segs = []
    for c in pattern:
        y = y_hi if c == '1' else y_lo
        if prev is not None and prev != y:
            segs.append(line(x, prev, x, y, color=color, sw=sw))  # вертикальний фронт
        segs.append(line(x, y, x + unit, y, color=color, sw=sw))
        prev = y
        x += unit
    return "".join(segs)


def fig_strobe():
    W, H = 840, 470
    frags = []
    unit = 66
    x0 = 150
    patt = "10110"

    # --- читання: строб приходить по краю ока ---
    yhi, ylo = 90, 130
    frags.append(text(70, 70, "ЧИТАННЯ", size=14, bold=True, color=POS, anchor="start"))
    frags.append(text(70, yhi+6, "DQ", size=12, anchor="end", color=INK))
    frags.append(_wave(x0, yhi, ylo, unit, patt, color=INK))
    # DQS вирівняний по фронту (край ока)
    yqs = 180
    frags.append(text(70, yqs+6, "DQS (як прийшов)", size=11, anchor="end", color=MUTED))
    frags.append(_wave(x0, yqs-16, yqs+16, unit, "10101", color=MUTED, sw=2))
    # позначки фронтів на краях бітів
    for i in range(len(patt)+1):
        xx = x0 + i*unit
        frags.append(line(xx, yhi-6, xx, ylo+6, color="#f0b9b3", sw=1, dash="3,3"))
    frags.append(text(x0 + 2.5*unit, 210, "фронти строба стоять на КРАЯХ біта — там дані щойно змінились",
                     size=11, color=POS))

    # стрілка «зсув на 90°»
    frags.append(arrow(x0 + 5.4*unit, 150, x0 + 5.4*unit, 250, color=FIELD, sw=2))
    frags.append(text(x0 + 5.4*unit + 10, 205, "PHY зсуває", size=11, color=FIELD, anchor="start"))
    frags.append(text(x0 + 5.4*unit + 10, 220, "DQS на 90°", size=11, color=FIELD, anchor="start", bold=True))

    # DQS зсунутий — у центр
    yqs2 = 270
    frags.append(text(70, yqs2+6, "DQS (зсунутий)", size=11, anchor="end", color=FIELD))
    frags.append(_wave(x0 + 0.5*unit, yqs2-16, yqs2+16, unit, "1010", color=FIELD, sw=2.4))
    for i in range(len(patt)):
        xc = x0 + (i+0.5)*unit
        frags.append(circle(xc, (yhi+ylo)/2, 3.2, fill=FIELD, stroke=FIELD))
        frags.append(line(xc, (yhi+ylo)/2, xc, yqs2, color=FIELD, sw=1, dash="2,3"))
    frags.append(text(x0 + 2.5*unit, 300, "тепер фронт строба стоїть у ЦЕНТРІ біта — дані стабільні, читаємо певно",
                     size=11, color=FIELD))

    # --- запис: PHY одразу видає центр-вирівняно ---
    yhi3, ylo3 = 350, 390
    frags.append(text(70, 340, "ЗАПИС", size=14, bold=True, color=NEG, anchor="start"))
    frags.append(text(70, yhi3+6, "DQ", size=12, anchor="end", color=INK))
    frags.append(_wave(x0, yhi3, ylo3, unit, patt, color=INK))
    yqs3 = 435
    frags.append(text(70, yqs3+2, "DQS", size=12, anchor="end", color=NEG))
    frags.append(_wave(x0 + 0.5*unit, yqs3-14, yqs3+14, unit, "1010", color=NEG, sw=2.4))
    for i in range(len(patt)):
        xc = x0 + (i+0.5)*unit
        frags.append(line(xc, ylo3, xc, yqs3-14, color=NEG, sw=1, dash="2,3"))
    frags.append(text(x0 + 5.3*unit, yhi3-4, "PHY сам ставить строб у центр —", size=10.5, color=NEG, anchor="start"))
    frags.append(text(x0 + 5.3*unit, yhi3+11, "щоб він дійшов до чіпа в центрі ока", size=10.5, color=NEG, anchor="start"))

    render(os.path.join(IMG, "strobe-align.svg"), W, H, *frags,
           title="Уся робота PHY — посадити строб DQS у середину бітового ока")


# ── 3. Вирівнювання запису: строб питає такт, чіп відповідає ─────────────────
def fig_leveling():
    W, H = 820, 360
    frags = []

    # ліворуч — контролер/PHY регулює затримку
    b, wp, hp = textbox(150, 150, "PHY\nсуне затримку\nстроба DQS\nмаленькими\nкроками",
                       size=13, fill="#eafaf1", stroke=FIELD, bold=False, pad=14)
    frags.append(b)

    # праворуч — чіп DRAM у режимі вирівнювання
    b, wd, hd = textbox(650, 150, "DRAM\n(режим write leveling):\nстроб DQS клацає —\nчіп ловить значення\nтакту CK і вертає його\nна лінію DQ",
                       size=12, fill="#fdf2f2", stroke=POS, pad=14)
    frags.append(b)

    # DQS туди
    frags.append(arrow(150 + wp/2, 120, 650 - wd/2, 120, color=FIELD, sw=2))
    frags.append(text((150+wp/2 + 650-wd/2)/2, 105, "строб DQS →", size=12, color=FIELD))
    # CK туди (опорний такт)
    frags.append(arrow(150 + wp/2, 150, 650 - wd/2, 150, color=INK, sw=1.6))
    frags.append(text((150+wp/2 + 650-wd/2)/2, 168, "такт CK →", size=11, color=MUTED))
    # DQ назад
    frags.append(arrow(650 - wd/2, 195, 150 + wp/2, 195, color=NEG, sw=2))
    frags.append(text((150+wp/2 + 650-wd/2)/2, 213, "← відповідь на DQ: 0 чи 1", size=12, color=NEG))

    # висновок унизу
    b, wc, hc = textbox(410, 300,
        "0 → строб іще рано (до фронту CK): додати затримку.   1 → строб уже наздогнав фронт CK: край знайдено.",
        size=12, fill="#fffef0", stroke="#caa300", pad=12, min_w=760)
    frags.append(b)

    render(os.path.join(IMG, "write-leveling.svg"), W, H, *frags,
           title="Вирівнювання запису: PHY підганяє строб під такт на самому чіпі")


# ══ Фігури до вставки comp-ddr-io-signaling ═════════════════════════════════

# ── 4. SSTL проти POD: куди тече струм драйвера ──────────────────────────────
def fig_sstl_vs_pod():
    W, H = 860, 470
    frags = []

    def resistor(x, y1, y2, color=INK):
        """Вертикальний резистор-зигзаг між y1 (верх) і y2 (низ)."""
        n = 6
        seg = (y2 - y1) / (n + 1)
        pts = [(x, y1)]
        yy = y1 + seg
        for i in range(n):
            dx = 7 if i % 2 == 0 else -7
            pts.append((x + dx, yy))
            yy += seg
        pts.append((x, y2))
        out = []
        for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
            out.append(line(xa, ya, xb, yb, color=color, sw=1.8))
        return "".join(out)

    def rail(x0, x1, y, label, color, lab_color=None):
        out = [line(x0, y, x1, y, color=color, sw=2.4)]
        out.append(text(x1 + 8, y + 4, label, size=12, color=lab_color or color,
                        anchor="start", bold=True))
        return "".join(out)

    # ---- ЛІВОРУЧ: SSTL (DDR3) ----
    cx = 150
    frags.append(text(cx, 62, "SSTL — DDR3", size=15, bold=True, color=NEG))
    frags.append(text(cx, 80, "термінація до середини VDDQ/2", size=11, color=MUTED))
    top, mid, bot = 110, 235, 360
    frags.append(rail(cx - 80, cx + 80, top, "VDDQ (1.5 В)", INK))
    frags.append(rail(cx - 80, cx + 80, mid, "VTT = VDDQ/2", POS, POS))
    frags.append(rail(cx - 80, cx + 80, bot, "GND", INK))
    # верхній термінаційний резистор до VTT
    frags.append(resistor(cx, top, mid - 22, color=POS))
    frags.append(text(cx - 44, (top + mid) / 2, "Rтерм", size=10.5, color=POS, anchor="end"))
    # драйвер (нижнє плече відкрите → тягне лінію в 0)
    frags.append(rect(cx - 18, mid + 18, 36, 46, fill="#eaf0fd", stroke=NEG, sw=1.6))
    frags.append(text(cx, mid + 46, "драйвер", size=10, color=NEG))
    frags.append(line(cx, mid - 22, cx, mid + 18, color=INK, sw=2))  # вивід DQ
    frags.append(circle(cx, mid - 2, 3, fill=INK, stroke=INK))
    frags.append(text(cx + 10, mid + 2, "DQ", size=11, color=INK, anchor="start", bold=True))
    frags.append(line(cx, mid + 64, cx, bot, color=INK, sw=2))
    # струм тече З ОБОХ боків
    frags.append(arrow(cx - 30, top + 14, cx - 30, mid - 26, color=POS, sw=1.8))
    frags.append(text(cx - 36, (top + mid) / 2 + 6, "струм", size=10, color=POS, anchor="end"))
    frags.append(text(cx - 36, (top + mid) / 2 + 20, "живлення", size=10, color=POS, anchor="end"))

    # ---- ПРАВОРУЧ: POD (DDR4/5) ----
    cx2 = 560
    frags.append(text(cx2, 62, "POD — DDR4 / DDR5", size=15, bold=True, color=FIELD))
    frags.append(text(cx2, 80, "термінація до самого VDDQ (псевдо-відкритий стік)", size=11, color=MUTED))
    frags.append(rail(cx2 - 80, cx2 + 80, top, "VDDQ (1.2 / 1.1 В)", INK))
    frags.append(rail(cx2 - 80, cx2 + 80, bot, "GND", INK))
    # термінаційний резистор аж до VDDQ
    frags.append(resistor(cx2, top, mid - 22, color=FIELD))
    frags.append(text(cx2 - 44, (top + mid) / 2, "Rтерм", size=10.5, color=FIELD, anchor="end"))
    frags.append(rect(cx2 - 18, mid + 18, 36, 46, fill="#eafaf1", stroke=FIELD, sw=1.6))
    frags.append(text(cx2, mid + 46, "драйвер", size=10, color=FIELD))
    frags.append(line(cx2, mid - 22, cx2, mid + 18, color=INK, sw=2))
    frags.append(circle(cx2, mid - 2, 3, fill=INK, stroke=INK))
    frags.append(text(cx2 + 10, mid + 2, "DQ", size=11, color=INK, anchor="start", bold=True))
    frags.append(line(cx2, mid + 64, cx2, bot, color=INK, sw=2))
    # струм тече ЛИШЕ коли тягнемо в 0; при 1 — 0 струму
    frags.append(text(cx2, mid + 88, "струм лише коли DQ = 0;", size=10.5, color=FIELD))
    frags.append(text(cx2, mid + 103, "при DQ = 1 струм ≈ 0", size=10.5, color=FIELD, bold=True))

    # висновок унизу
    frags.append(fitbox(70, 398, 720, 56,
        "SSTL палить струм і на 0, і на 1 — обидва плеча активні.\n"
        "POD палить струм лише коли тягне 0: при 1 верх і драйвер на однаковому VDDQ, "
        "перепаду нема, струм ≈ 0. Половину рівнів отримали задарма.",
        size=12, fill="#fffef0", stroke="#caa300"))

    render(os.path.join(IMG, "sstl-vs-pod.svg"), W, H, *frags,
           title="Чому DDR4 покинув SSTL заради POD: економія струму драйвера")


# ── 5. Data Bus Inversion: інвертуємо байт, коли забагато нулів ──────────────
def fig_dbi():
    W, H = 840, 400
    frags = []
    cell = 40
    x0 = 250
    y0 = 110

    def draw_byte(y, bits, label, dbi_flag, note, ncolor):
        frags.append(text(x0 - 16, y + cell * 0.62, label, size=12, anchor="end", color=INK, bold=True))
        zeros = sum(1 for b in bits if b == 0)
        for i, b in enumerate(bits):
            x = x0 + i * cell
            fill = "#fdecea" if b == 0 else "#eafaf1"
            stroke = POS if b == 0 else FIELD
            frags.append(rect(x, y, cell - 4, cell - 4, fill=fill, stroke=stroke, sw=1.6, rx=4))
            frags.append(text(x + (cell - 4) / 2, y + cell * 0.62, str(b), size=15,
                              color=stroke, bold=True))
        # 9-й прапорець DBI
        xf = x0 + 8 * cell + 12
        ff = "#eef2ff"
        frags.append(rect(xf, y, cell - 4, cell - 4, fill=ff, stroke=NEG, sw=1.8, rx=4))
        frags.append(text(xf + (cell - 4) / 2, y + cell * 0.62, str(dbi_flag), size=15,
                          color=NEG, bold=True))
        frags.append(text(x0 + 4 * cell, y - 10, note, size=11, color=ncolor))
        return zeros

    frags.append(text(x0 + 4 * cell, 74, "8 ліній даних DQ", size=12, color=MUTED))
    frags.append(text(x0 + 8 * cell + 12 + (cell - 4) / 2, 74, "DBI", size=11, color=NEG, bold=True))

    # вихідний байт: 6 нулів з 8 → забагато
    orig = [0, 0, 1, 0, 0, 0, 1, 0]
    z1 = draw_byte(y0, orig, "було", 1, "6 нулів із 8 → POD палив би 6 струмів", POS)

    # стрілка вниз «інвертуємо весь байт»
    frags.append(arrow(x0 + 4 * cell, y0 + cell + 6, x0 + 4 * cell, y0 + cell + 54, color=FIELD, sw=2.2))
    frags.append(text(x0 + 4 * cell + 12, y0 + cell + 34,
                      "нулів > 4 → інвертуємо весь байт, прапорець DBI = 0", size=11.5,
                      color=FIELD, anchor="start", bold=True))

    inv = [1 - b for b in orig]
    y1 = y0 + cell + 70
    z2 = draw_byte(y1, inv, "стало", 0, "лише 2 нулі → POD палить 2 струми", FIELD)

    # висновок
    frags.append(fitbox(70, 296, 700, 74,
        "Правило: якщо в байті понад чотири нулі, передавач інвертує ВСІ вісім ліній\n"
        "і виставляє дев'ятий прапорець DBI = 0; приймач бачить прапорець і інвертує назад.\n"
        "Гарантія: із дев'яти ліній (8 DQ + DBI) щонайменше п'ять завжди тримають одиницю —\n"
        "а одиниця в POD струму не палить.",
        size=12, fill="#f7fdfa", stroke=FIELD))

    render(os.path.join(IMG, "dbi.svg"), W, H, *frags,
           title="Data Bus Inversion: менше нулів на шині — менше струму й завад")


# ── 6. VREF як межа рішення + DFE прибирає «хвіст» попереднього біта ─────────
def fig_vref_dfe():
    W, H = 860, 430
    frags = []

    # ---- ЛІВОРУЧ: VREF — де провести межу 0/1 ----
    ox, oy, ow, oh = 90, 120, 300, 190
    frags.append(text(ox + ow / 2, 92, "VREF — межа рішення", size=14, bold=True, color=NEG))
    frags.append(rect(ox, oy, ow, oh, fill="#fbfbfd", stroke=MUTED, sw=1.2))
    # «око» — дві криві, що лишають ромб посередині
    import math as _m
    top_env, bot_env = [], []
    for i in range(41):
        t = i / 40.0
        x = ox + t * ow
        openess = _m.sin(_m.pi * t)  # 0 на краях, 1 посередині
        top_env.append((x, oy + oh * (0.5 - 0.34 * openess)))
        bot_env.append((x, oy + oh * (0.5 + 0.34 * openess)))
    def polyline(pts, color, sw=2):
        return "".join(line(a[0], a[1], b[0], b[1], color=color, sw=sw)
                       for a, b in zip(pts, pts[1:]))
    frags.append(polyline(top_env, INK))
    frags.append(polyline(bot_env, INK))
    frags.append(text(ox + ow / 2, oy + 20, "рівень «1»", size=10.5, color=FIELD))
    frags.append(text(ox + ow / 2, oy + oh - 10, "рівень «0»", size=10.5, color=POS))
    # добра VREF — рівно в центр ока
    yv = oy + oh * 0.5
    frags.append(line(ox, yv, ox + ow, yv, color=FIELD, sw=2, dash="6,4"))
    frags.append(text(ox + ow + 8, yv + 4, "VREF у центрі:", size=10.5, color=FIELD, anchor="start", bold=True))
    frags.append(text(ox + ow + 8, yv + 18, "запас угору = вниз", size=10, color=FIELD, anchor="start"))
    # погана VREF — з'їхала вгору
    yb = oy + oh * 0.30
    frags.append(line(ox, yb, ox + ow, yb, color=POS, sw=1.6, dash="3,3"))
    frags.append(text(ox + ow + 8, yb + 2, "VREF з'їхала:", size=10.5, color=POS, anchor="start"))
    frags.append(text(ox + ow + 8, yb + 16, "запас угору малий", size=10, color=POS, anchor="start"))

    # ---- ПРАВОРУЧ: DFE прибирає хвіст попереднього біта ----
    bx, by = 470, 120
    frags.append(text(bx + 150, 92, "DFE — прибрати хвіст попереднього біта", size=13, bold=True, color=FIELD))
    unit = 60
    yhi, ylo = by + 20, by + 90
    # ідеальний сигнал (пунктир) і реальний з хвостом (суцільний)
    patt = "1000"
    # реальний: після 1 лишається спад-хвіст, що піднімає наступні 0
    xs = bx
    prev = None
    tail = [0.0, 0.55, 0.30, 0.15]  # частка розмаху, що «залипла» від попередньої 1
    for i, c in enumerate(patt):
        base = yhi if c == '1' else ylo
        # реальний рівень із хвостом угору для нулів
        lvl = base - (ylo - yhi) * tail[i] if c == '0' else base
        frags.append(line(xs, lvl, xs + unit, lvl, color=INK, sw=2.4))
        if prev is not None:
            frags.append(line(xs, prev, xs, lvl, color=INK, sw=2.4))
        prev = lvl
        xs += unit
    # межа VREF
    yvref = (yhi + ylo) / 2
    frags.append(line(bx, yvref, bx + 4 * unit, yvref, color=NEG, sw=1.6, dash="5,4"))
    frags.append(text(bx + 4 * unit + 6, yvref + 4, "VREF", size=10.5, color=NEG, anchor="start"))
    # позначка: перший 0 ледь не переліз VREF
    frags.append(circle(bx + 1.5 * unit, yhi + (ylo - yhi) * (1 - tail[1]), 4, fill="none", stroke=POS, sw=2))
    frags.append(text(bx + 1.5 * unit, by + 118, "цей 0 через хвіст 1", size=10, color=POS))
    frags.append(text(bx + 1.5 * unit, by + 132, "ледь не читається як 1", size=10, color=POS))

    # стрілка → після DFE
    frags.append(arrow(bx + 1.2 * unit, by + 150, bx + 1.2 * unit, by + 178, color=FIELD, sw=2))
    frags.append(text(bx + 150, by + 168, "DFE віднімає відомий хвіст попередньої 1 →", size=10.5,
                      color=FIELD))
    # чистий сигнал після DFE
    yhi2, ylo2 = by + 200, by + 250
    xs = bx
    prev = None
    for c in patt:
        lvl = yhi2 if c == '1' else ylo2
        frags.append(line(xs, lvl, xs + unit, lvl, color=FIELD, sw=2.4))
        if prev is not None:
            frags.append(line(xs, prev, xs, lvl, color=FIELD, sw=2.4))
        prev = lvl
        xs += unit
    frags.append(line(bx, (yhi2 + ylo2) / 2, bx + 4 * unit, (yhi2 + ylo2) / 2, color=NEG, sw=1.4, dash="5,4"))
    frags.append(text(bx + 4 * unit + 6, (yhi2 + ylo2) / 2 + 4, "запас відновлено", size=10, color=FIELD, anchor="start"))

    render(os.path.join(IMG, "vref-dfe.svg"), W, H, *frags,
           title="VREF задає межу рішення; DFE прибирає слід попереднього біта")


if __name__ == "__main__":
    fig_place()
    fig_strobe()
    fig_leveling()
    fig_sstl_vs_pod()
    fig_dbi()
    fig_vref_dfe()
    print("OK: 6 SVG у", IMG)
