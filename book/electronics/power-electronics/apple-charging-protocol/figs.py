# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

APPLE = "#7a4fb0"   # фіолетовий — колір «дільникового» діалекту в цій темі


# ── code-table: дві лінії × два рівні = чотири числа ──────────────────────────
# Ідея: головна відмінність від BC1.2 — код несе НЕ «так/ні», а число. Матриця
# 2×2 показує, звідки беруться саме чотири класи струму й що вони не довільні.

def fig_code_table():
    W, H = 740, 430
    p = []

    cx = [352, 578]          # центри стовпців (D−)
    cy = [212, 328]          # центри рядків (D+)
    cw, ch = 208, 100

    # заголовки стовпців — D−
    p.append(text(465, 96, "напруга на D−", size=12, color=NEG, bold=True))
    for i, v in enumerate(["2.0 В", "2.7 В"]):
        p.append(text(cx[i], 130, v, size=15, color=NEG, bold=True))

    # заголовки рядків — D+
    p.append(text(150, 96, "напруга", size=12, color=POS, bold=True))
    p.append(text(150, 114, "на D+", size=12, color=POS, bold=True))
    for j, v in enumerate(["2.0 В", "2.7 В"]):
        p.append(text(150, cy[j] + 5, v, size=15, color=POS, bold=True))

    # клітини: (стовпець, рядок, струм, потужність, підпис)
    cells = [
        (0, 0, "0.5 А", "2.5 Вт", "старі аксесуари", MUTED, "#f2f3f5"),
        (1, 0, "1.0 А", "5 Вт", "Divider 1", FIELD, "#eafaf0"),
        (0, 1, "2.1 А", "10 Вт", "Divider 2", "#b8901f", "#fdf6e3"),
        (1, 1, "2.4 А", "12 Вт", "Divider 3", APPLE, "#f2ecf8"),
    ]
    for i, j, cur, w, name, col, fill in cells:
        x, y = cx[i] - cw / 2, cy[j] - ch / 2
        p.append(rect(x, y, cw, ch, fill=fill, stroke=col, sw=1.6, rx=8))
        p.append(text(cx[i], cy[j] - 16, cur, size=22, color=col, bold=True))
        p.append(text(cx[i], cy[j] + 8, w, size=12, color=INK))
        p.append(text(cx[i], cy[j] + 32, name, size=10, color=MUTED))

    b, bw, bh = textbox(W / 2, 400,
                        "дві лінії × два рівні = чотири числа: код каже не «так/ні», а СКІЛЬКИ саме ампер",
                        size=11, fill="#eafaf0", stroke=FIELD, sw=1.3, pad=8)
    p.append(b)

    render(os.path.join(OUT, "code-table.svg"), W, H, *p,
           title="Чотири комбінації напруг — чотири класи струму")


# ── divider-hardware: увесь протокол — чотири резистори ───────────────────────
# Ідея: показати схему Divider 2 (10 Вт) з реальними номіналами й одразу поруч
# еквівалент Тевеніна — бо саме вихідний опір, а не напруга, вирішує долю підпису.

def fig_divider_hardware():
    W, H = 760, 430
    p = []

    RAIL_Y, GND_Y, NODE_Y = 62, 276, 172
    LX, RX = 152, 608

    # шина VBUS і шина землі
    p.append(line(112, RAIL_Y, 648, RAIL_Y, color=POS, sw=2.2))
    p.append(text(W / 2, 44, "VBUS = 5.0 В", size=12, color=POS, bold=True))
    p.append(line(112, GND_Y, 648, GND_Y, color=INK, sw=2.2))

    # символ землі під центром
    p.append(line(W / 2, GND_Y, W / 2, GND_Y + 8, color=INK, sw=1.8))
    p.append(line(W / 2 - 15, GND_Y + 8, W / 2 + 15, GND_Y + 8, color=INK, sw=1.8))
    p.append(line(W / 2 - 10, GND_Y + 14, W / 2 + 10, GND_Y + 14, color=INK, sw=1.8))
    p.append(line(W / 2 - 5, GND_Y + 20, W / 2 + 5, GND_Y + 20, color=INK, sw=1.8))
    p.append(text(W / 2 + 30, GND_Y + 20, "GND", size=10, color=MUTED, anchor="start"))

    # два плеча: (x, верхній номінал, підпис-сторона)
    for bx, rtop, side in [(LX, "43.2 кОм", "end"), (RX, "75 кОм", "start")]:
        lx = bx - 24 if side == "end" else bx + 24
        p.append(line(bx, RAIL_Y, bx, 104, color=INK, sw=1.8))
        p.append(rect(bx - 15, 104, 30, 46, fill=BG, stroke=INK, sw=1.6, rx=3))
        p.append(text(lx, 132, rtop, size=11, color=INK, anchor=side, bold=True))
        p.append(line(bx, 150, bx, NODE_Y, color=INK, sw=1.8))
        p.append(circle(bx, NODE_Y, 4, fill=INK, stroke=INK, sw=1))
        p.append(line(bx, NODE_Y, bx, 200, color=INK, sw=1.8))
        p.append(rect(bx - 15, 200, 30, 46, fill=BG, stroke=INK, sw=1.6, rx=3))
        p.append(text(lx, 228, "49.9 кОм", size=11, color=INK, anchor=side, bold=True))
        p.append(line(bx, 246, bx, GND_Y, color=INK, sw=1.8))

    # роз'єм посередині
    p.append(rect(302, 134, 156, 76, fill=FILL, stroke=INK, sw=1.8, rx=8))
    p.append(text(380, 156, "роз'єм USB", size=11, color=INK, bold=True))
    p.append(text(316, NODE_Y + 22, "D+", size=12, color=POS, anchor="start", bold=True))
    p.append(text(444, NODE_Y + 22, "D−", size=12, color=NEG, anchor="end", bold=True))

    # виводи вузлів до роз'єму + напруги НАД лініями
    p.append(line(LX, NODE_Y, 302, NODE_Y, color=POS, sw=2.0))
    p.append(text(227, NODE_Y - 10, "2.68 В", size=12, color=POS, bold=True))
    p.append(line(RX, NODE_Y, 458, NODE_Y, color=NEG, sw=2.0))
    p.append(text(533, NODE_Y - 10, "2.00 В", size=12, color=NEG, bold=True))

    # живлення й земля в роз'єм
    p.append(line(380, RAIL_Y, 380, 134, color=POS, sw=2.0))
    p.append(line(380, 210, 380, GND_Y, color=INK, sw=2.0))

    # еквіваленти Тевеніна
    b1, _, _ = textbox(174, 334, "еквівалент Тевеніна\nD+: 2.68 В за 23.2 кОм",
                       size=11, fill="#fdecea", stroke=POS, sw=1.4, pad=9)
    p.append(b1)
    b2, _, _ = textbox(586, 334, "еквівалент Тевеніна\nD−: 2.00 В за 30.0 кОм",
                       size=11, fill="#eef4ff", stroke=NEG, sw=1.4, pad=9)
    p.append(b2)
    p.append(text(380, 330, "схема Divider 2", size=11, color="#b8901f", bold=True))
    p.append(text(380, 348, "(адаптер 10 Вт)", size=10, color=MUTED))

    b, bw, bh = textbox(W / 2, 400,
                        "увесь «протокол» — оці чотири резистори: ні логіки, ні такту, ні живлення",
                        size=11, fill="#eafaf0", stroke=FIELD, sw=1.3, pad=8)
    p.append(b)

    render(os.path.join(OUT, "divider-hardware.svg"), W, H, *p,
           title="Дільники, що кодують 10 Вт")


# ── window: відношення стале, пороги абсолютні ────────────────────────────────
# Ідея: дільник тримає ЧАСТКУ від VBUS, а пристрій міряє АБСОЛЮТНІ вольти. Тож
# щойно VBUS їде, точка повзе по осі — і випадає з приймального вікна.

def fig_window():
    W, H = 760, 360
    p = []

    X0, X1 = 96, 672
    V0, V1 = 1.5, 3.0
    sc = (X1 - X0) / (V1 - V0)

    def px(v):
        return X0 + (v - V0) * sc

    # приймальні вікна
    p.append(text(W / 2, 74, "приймальні вікна пристрою", size=12, color=INK, bold=True))
    p.append(rect(px(1.9), 92, px(2.1) - px(1.9), 62, fill="#eef4ff", stroke=NEG, sw=1.6, rx=5))
    p.append(text(px(2.0), 118, "клас", size=10, color=NEG, bold=True))
    p.append(text(px(2.0), 136, "2.0 В", size=11, color=NEG, bold=True))
    p.append(rect(px(2.57), 92, px(2.84) - px(2.57), 62, fill="#f2ecf8", stroke=APPLE, sw=1.6, rx=5))
    p.append(text(px(2.705), 118, "клас", size=10, color=APPLE, bold=True))
    p.append(text(px(2.705), 136, "2.7 В", size=11, color=APPLE, bold=True))

    # межі вікон — підписи над рамками
    p.append(text(px(1.9), 84, "1.9", size=9, color=MUTED))
    p.append(text(px(2.1), 84, "2.1", size=9, color=MUTED))
    p.append(text(px(2.57), 84, "2.57", size=9, color=MUTED))
    p.append(text(px(2.84), 84, "2.84", size=9, color=MUTED))

    # нічия земля
    p.append(text(px(2.335), 118, "нічия", size=10, color=POS, bold=True))
    p.append(text(px(2.335), 136, "земля", size=10, color=POS, bold=True))

    # лінійка напруги
    RY = 200
    p.append(arrow(X0 - 6, RY, X1 + 22, RY, color=INK, sw=1.6))
    p.append(text(X1 + 34, RY + 4, "В", size=11, color=INK, anchor="start", bold=True))
    for v in [1.5, 2.0, 2.5, 3.0]:
        p.append(line(px(v), RY, px(v), RY + 6, color=MUTED, sw=1.2))
        p.append(text(px(v), RY + 22, ("%.1f" % v), size=10, color=MUTED))

    # маркери — куди сідає вузол 2.7 при різній VBUS
    marks = [(2.25, POS), (2.68, FIELD), (2.79, NEG)]
    for v, col in marks:
        p.append(line(px(v), RY - 6, px(v), 158, color=col, sw=1.3, dash="4 3"))
        p.append(circle(px(v), RY, 5, fill=col, stroke=col, sw=1.2))

    # легенда — тлумачення маркерів (кольором, без написів на осі)
    rows = [
        (FIELD, "VBUS 5.0 В  →  вузол 2.68 В  —  у вікні класу 2.7"),
        (NEG, "VBUS 5.2 В (адаптер Apple 12 Вт)  →  2.79 В  —  ще у вікні"),
        (POS, "VBUS 4.2 В (просадка)  →  2.25 В  —  нічия земля, підпис зник"),
    ]
    for i, (col, s) in enumerate(rows):
        y = 270 + i * 26
        p.append(circle(126, y - 4, 5, fill=col, stroke=col, sw=1.2))
        p.append(text(146, y, s, size=11, color=INK, anchor="start"))

    render(os.path.join(OUT, "window.svg"), W, H, *p,
           title="Чому вікно мусить бути широким")


# ── two-dialects: несумісні вимоги й вихід через перемикання ──────────────────
# Ідея: BC1.2 і дільник вимагають від тих самих двох ліній фізично протилежного,
# тож блок не говорить обома мовами ОДНОЧАСНО — він перемикається за поведінкою.

def fig_two_dialects():
    W, H = 760, 430
    p = []

    p.append(text(W / 2, 44, "одна пара ліній — дві несумісні вимоги", size=13, color=INK, bold=True))

    # ліва вимога — BC1.2
    p.append(rect(58, 64, 276, 104, fill="#fdf6e3", stroke="#b8901f", sw=1.6, rx=9))
    p.append(text(196, 88, "BC1.2 вимагає", size=12, color="#b8901f", bold=True))
    p.append(text(196, 114, "D+ замкнено на D−", size=12, color=INK, bold=True))
    p.append(text(196, 136, "наскрізь, ≤200 Ом", size=11, color=MUTED))
    p.append(text(196, 158, "одна напруга на двох лініях", size=10, color=MUTED))

    # права вимога — дільник
    p.append(rect(426, 64, 276, 104, fill="#f2ecf8", stroke=APPLE, sw=1.6, rx=9))
    p.append(text(564, 88, "дільник вимагає", size=12, color=APPLE, bold=True))
    p.append(text(564, 114, "D+ = 2.7 В, D− = 2.0 В", size=12, color=INK, bold=True))
    p.append(text(564, 136, "різниця 0.7 В між лініями", size=11, color=MUTED))
    p.append(text(564, 158, "замкнеш — код зникне", size=10, color=MUTED))

    # знак суперечності між ними
    p.append(circle(380, 116, 20, fill="#fdecea", stroke=POS, sw=1.8))
    p.append(text(380, 122, "✗", size=18, color=POS, bold=True))

    p.append(text(W / 2, 206, "вихід — не обидва разом, а перемикання за поведінкою пристрою",
                  size=12, color=FIELD, bold=True))

    # автомат станів
    s1, w1, h1 = textbox(190, 300, "режим дільника\n2.7 В / 2.0 В\n(за замовчуванням)",
                         size=11, bold=True, color=APPLE, fill="#f2ecf8", stroke=APPLE, sw=1.8, pad=12)
    s2, w2, h2 = textbox(570, 300, "режим замикання\nD+ ↔ D−\n≤200 Ом",
                         size=11, bold=True, color="#b8901f", fill="#fdf6e3", stroke="#b8901f", sw=1.8, pad=12)

    p.append(arrow(190 + w1 / 2 + 4, 282, 570 - w2 / 2 - 4, 282, color=INK, sw=1.6))
    p.append(text(380, 268, "пристрій потяг D+ униз → це BC1.2-проба", size=10, color=INK))

    p.append(arrow(570 - w2 / 2 - 4, 320, 190 + w1 / 2 + 4, 320, color=MUTED, sw=1.6))
    p.append(text(380, 340, "D+ < 330 мВ → пристрій від'єднано", size=10, color=MUTED))

    p.append(s1)
    p.append(s2)

    b, bw, bh = textbox(W / 2, 398,
                        "той самий блок обслуговує обидва діалекти — по черзі, а не одночасно",
                        size=11, fill="#eafaf0", stroke=FIELD, sw=1.3, pad=8)
    p.append(b)

    render(os.path.join(OUT, "two-dialects.svg"), W, H, *p,
           title="Дільник проти BC1.2 і автовизначення")


# ── budget-stack: паспорт мікросхеми ≠ приймальне вікно ──────────────────────
# Ідея вставки: цифри 2.57–2.84 і 1.9–2.1 виміряні при VIN = 5.0 В рівно. На
# роз'ємі до них ДОДАЄТЬСЯ розкид самої VBUS — і хмара кожного класу росте вдвічі.
# Те, що лишається між хмарами, і є весь бюджет читача.

def fig_budget_stack():
    W, H = 820, 470
    p = []

    VLO, VHI = 1.70, 3.05
    X0, X1 = 100, 720
    def X(v): return X0 + (v - VLO) * (X1 - X0) / (VHI - VLO)

    C20, C27 = NEG, APPLE
    F20, F27 = "#eaf0fd", "#f2ecf8"

    # ── ряд 1: паспорт при VIN = 5.0 В ──
    p.append(text(W / 2, 74, "паспорт мікросхеми — виміряно при VIN = 5.0 В рівно",
                  size=12, color=MUTED, bold=True))
    yA, hA = 96, 34
    for lo, hi, col, fil, nm in [(1.90, 2.10, C20, F20, "клас 2.0"), (2.57, 2.84, C27, F27, "клас 2.7")]:
        p.append(rect(X(lo), yA, X(hi) - X(lo), hA, fill=fil, stroke=col, sw=2, rx=4))
        p.append(text((X(lo) + X(hi)) / 2, yA + 22, nm, size=12, color=col, bold=True))
        p.append(text((X(lo) + X(hi)) / 2, yA - 8, "%.2f–%.2f В" % (lo, hi), size=11, color=col))

    # ── стрілки росту ──
    p.append(text(W / 2, 144, "× VBUS = 4.75…5.25 В   (дільник тримає ЧАСТКУ, не вольти)",
                  size=12, color=INK, bold=True))
    for lo, hi, lo2, hi2, col in [(1.90, 2.10, 1.805, 2.205, C20), (2.57, 2.84, 2.4415, 2.982, C27)]:
        p.append(arrow(X(lo), 156, X(lo2), 192, color=col, sw=1.4))
        p.append(arrow(X(hi), 156, X(hi2), 192, color=col, sw=1.4))

    # ── ряд 2: що приходить на роз'єм ──
    yB, hB = 202, 34
    p.append(text(W / 2, 266, "хмара на роз'ємі — усе, що пристрій зобов'язаний прийняти",
                  size=12, color=MUTED, bold=True))
    for lo, hi, col, fil in [(1.805, 2.205, C20, F20), (2.4415, 2.982, C27, F27)]:
        p.append(rect(X(lo), yB, X(hi) - X(lo), hB, fill=fil, stroke=col, sw=2, rx=4))
        p.append(text((X(lo) + X(hi)) / 2, yB + 22, "±10 %", size=12, color=col, bold=True))
        p.append(text(X(lo) - 6, yB - 8, "%.2f" % lo, size=11, color=col, anchor="end"))
        p.append(text(X(hi) + 6, yB - 8, "%.2f" % hi, size=11, color=col, anchor="start"))

    # ── зазор ──
    gl, gr = X(2.205), X(2.4415)
    p.append(rect(gl, yB - 6, gr - gl, hB + 12, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=4))
    p.append(line(gl, 282, gl, 322, color=FIELD, sw=1.2, dash="3,3"))
    p.append(line(gr, 282, gr, 322, color=FIELD, sw=1.2, dash="3,3"))
    p.append(arrow(gl, 314, gr, 314, color=FIELD, sw=1.8))
    b, bw, bh = textbox((gl + gr) / 2, 352, ["зазор 0.24 В", "весь бюджет читача: ±5 %"],
                        size=11, fill="#eafaf0", stroke=FIELD, sw=1.4, pad=8, color=INK)
    p.append(b)

    # ── вісь ──
    yax = 406
    p.append(line(X0 - 14, yax, X1 + 14, yax, color=INK, sw=1.6))
    for v in [1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0]:
        p.append(line(X(v), yax - 5, X(v), yax + 5, color=INK, sw=1.4))
        p.append(text(X(v), yax + 21, "%.1f" % v, size=11, color=MUTED))
    p.append(text(X1 + 36, yax + 5, "В", size=12, color=INK, bold=True))

    b2, _, _ = textbox(W / 2, 450,
                       "паспорт при 5 В — це ще НЕ вікно приймання: воно вдвічі ширше",
                       size=11, fill=FILL, stroke=MUTED, sw=1.2, pad=8)
    p.append(b2)

    render(os.path.join(OUT, "budget-stack.svg"), W, H, *p,
           title="Як хмара класу росте від паспорта до роз'єму")


# ── budget-bars: хто справді витрачає вікно ─────────────────────────────────
# Ідея: інтуїція «винні резистори» — хибна. Резистори дають 25 мВ, VBUS — 134.

def fig_budget_bars():
    W, H = 860, 480
    p = []

    rows = [
        ("розкид VBUS,  ±5 %",         134, POS,      "чутливість 1.0 — проходить наскрізь"),
        ("похибка АЦП читача,  ±2 %",   54, "#b8901f", "опорна напруга плюс нелінійність"),
        ("резистори,  ±1 % обидва",     25, FIELD,    "(1−k) гасить; стеля VBUS·δ/2"),
        ("витік входу,  1 мкА",         23, MUTED,    "1 мкА · 23.2 кОм"),
    ]

    X0 = 296
    SCALE = 2.30          # px на мВ
    y = 88
    for name, mv, col, note in rows:
        p.append(text(X0 - 16, y + 15, name, size=12, color=INK, anchor="end", bold=True))
        p.append(rect(X0, y, mv * SCALE, 26, fill=col, stroke=col, sw=1, rx=3))
        p.append(text(X0 + mv * SCALE + 12, y + 15, "±%d мВ" % mv, size=12, color=col,
                      bold=True, anchor="start"))
        p.append(text(X0, y + 44, note, size=10, color=MUTED, anchor="start"))
        y += 66

    ys = y + 8
    p.append(line(40, ys, W - 40, ys, color=MUTED, sw=1.2, dash="4,3"))
    p.append(text(X0 - 16, ys + 32, "найгірший випадок  (сума)", size=12, color=INK,
                  anchor="end", bold=True))
    p.append(rect(X0, ys + 17, 236 * SCALE, 24, fill="#fdecea", stroke=POS, sw=1.8, rx=3))
    p.append(text(X0 + 236 * SCALE + 12, ys + 32, "±236 мВ", size=12, color=POS,
                  bold=True, anchor="start"))

    p.append(text(X0 - 16, ys + 76, "корінь суми квадратів", size=12, color=INK,
                  anchor="end", bold=True))
    p.append(rect(X0, ys + 61, 148 * SCALE, 24, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=3))
    p.append(text(X0 + 148 * SCALE + 12, ys + 76, "±148 мВ", size=12, color=FIELD,
                  bold=True, anchor="start"))

    p.append(text(W / 2, H - 18, "внесок кожного джерела у вузол 2.68 В класу 2.7",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "budget-bars.svg"), W, H, *p,
           title="Бюджет вузла: винні не резистори, а живлення")


# ── level-ladder: чому рівнів рівно два ─────────────────────────────────────
# Ідея-кульмінація: 2.0 приколоте порогом USB знизу, 2.7 = 2.0 × (1.15/0.85),
# а третій щабель уже не має де стояти — він вилазить за шину 3.3 В.

def fig_level_ladder():
    W, H = 900, 510
    p = []

    VTOP = 4.35
    YB, YT = 430, 64
    def Y(v): return YB - v * (YB - YT) / VTOP

    xl, xr = 250, 500

    # нуль і заборонена смуга
    p.append(rect(xl, Y(0.8), xr - xl, Y(0) - Y(0.8), fill="#f2f3f5", stroke=MUTED, sw=1.2, rx=3))
    p.append(text((xl + xr) / 2, (Y(0) + Y(0.8)) / 2 + 4, "логічний нуль", size=11, color=MUTED))

    p.append(rect(xl, Y(2.0), xr - xl, Y(0.8) - Y(2.0), fill="#fdecea", stroke=POS, sw=1.5, rx=3))
    p.append(text((xl + xr) / 2, (Y(0.8) + Y(2.0)) / 2 - 4, "заборонена смуга USB", size=11,
                  color=POS, bold=True))
    p.append(text((xl + xr) / 2, (Y(0.8) + Y(2.0)) / 2 + 13, "рівень невизначений", size=10, color=POS))

    # рівні з конусами ±15 %
    for v, col, fil, nm in [(2.0, NEG, "#eaf0fd", "рівень 2.0"), (2.7, APPLE, "#f2ecf8", "рівень 2.7")]:
        lo, hi = v * 0.85, v * 1.15
        p.append(rect(xl, Y(hi), xr - xl, Y(lo) - Y(hi), fill=fil, stroke=col, sw=2, rx=3))
        p.append(line(xl, Y(v), xr, Y(v), color=col, sw=2.2, dash="6,3"))
        p.append(text((xl + xr) / 2, Y(v) - 7, "%s  ±15 %%" % nm, size=12, color=col, bold=True))
        p.append(text(xr + 12, Y(hi) + 12, "%.2f" % hi, size=10, color=col, anchor="start"))
        p.append(text(xr + 12, Y(lo) - 4, "%.2f" % lo, size=10, color=col, anchor="start"))

    p.append(text(xl - 12, Y(2.2979) + 4, "хмари торкаються", size=10, color=INK, anchor="end"))

    # шина 3.3 В
    p.append(line(xl - 44, Y(3.3), xr + 130, Y(3.3), color=POS, sw=2.2))
    p.append(text(xl - 52, Y(3.3) + 4, "шина 3.3 В", size=11, color=POS, anchor="end", bold=True))

    # привид третього щабля
    lo3, hi3 = 3.66 * 0.85, 3.66 * 1.15
    p.append(rect(xl, Y(hi3), xr - xl, Y(lo3) - Y(hi3), fill="#ffffff", stroke=MUTED, sw=1.6, rx=3))
    p.append(line(xl, Y(3.66), xr, Y(3.66), color=MUTED, sw=1.6, dash="6,3"))
    p.append(text((xl + xr) / 2, Y(3.66) - 6, "третій щабель: 3.66 В", size=11, color=MUTED, bold=True))
    p.append(text((xl + xr) / 2, Y(3.66) + 12, "нема куди — 4.03 В за шиною", size=10, color=MUTED))

    # вісь
    ax = xl - 96
    p.append(line(ax, YB, ax, YT, color=INK, sw=1.6))
    for v in [0, 1, 2, 3, 4]:
        p.append(line(ax - 5, Y(v), ax + 5, Y(v), color=INK, sw=1.4))
        p.append(text(ax - 12, Y(v) + 4, "%d" % v, size=11, color=MUTED, anchor="end"))
    p.append(text(ax - 10, YT - 14, "В", size=12, color=INK, bold=True))

    # права колонка — звідки береться крок
    p.append(arrow(xr + 96, Y(2.0), xr + 96, Y(2.7), color=INK, sw=1.6))
    p.append(text(xr + 108, (Y(2.0) + Y(2.7)) / 2 - 6, "× 1.15/0.85", size=11, color=INK,
                  anchor="start", bold=True))
    p.append(text(xr + 108, (Y(2.0) + Y(2.7)) / 2 + 9, "= × 1.353", size=11, color=INK, anchor="start"))

    b, _, _ = textbox(W / 2, H - 32,
                      "низ приколотий порогом USB, верх — бюджетом; третьому щаблю місця вже нема",
                      size=11, fill="#eafaf0", stroke=FIELD, sw=1.3, pad=8)
    p.append(b)

    render(os.path.join(OUT, "level-ladder.svg"), W, H, *p,
           title="Чому рівнів рівно два — і саме 2.0 та 2.7")


# ── hist-timeline: як знання про підпис накопичувалося відмовами ──────────────
# Ідея вставки-історії: спільнота не «дізналася» таблицю, а добудовувала її по
#кроку, і кожен крок оплачений зламаним набором. Дві доріжки поряд показують
# асиметрію: ліворуч — що вимагав пристрій, праворуч — що на той момент знали.

def fig_hist_timeline():
    W, H = 1000, 726
    p = []

    AX = 232                       # вісь часу
    ax_a, aw_a = 268, 320          # колонка «вимога пристрою»
    ax_b, aw_b = 620, 350          # колонка «знання набору»
    BH = 66

    rows = [
        (118, ["травень", "2006"],
         ["iPod тієї доби", "не питає нічого"],
         ["v1.0 — лінії D+/D− просто висять,", "і цього досить"]),
        (208, ["2007–2008"],
         ["нові iPod: обидві лінії", "мусять бути підтягнуті вгору"],
         ["v1.1 → v2: спершу одна вниз і одна", "на 3 В, далі 100 кОм на обидві"]),
        (298, ["19 червня", "2009"],
         ["iPhone 3GS: «CHARGING IS NOT", "SUPPORTED WITH THIS ACCESSORY»"],
         ["набір мовчить: підтяжки —", "вже не той діалект"]),
        (388, ["2009 — початок", "2010"],
         ["у фірмовому блоці 3GS —", "чотири резистори на D+/D−"],
         ["випаяли, поміряли:", "2.8 і 2.0 В → 1 А"]),
        (478, ["3 квітня", "2010"],
         ["iPad і блок 10 Вт:", "ще один, сильніший клас"],
         ["спільнота міряє далі:", "2.7/2.0 → 2.1 А"]),
        (568, ["3 серпня", "2010"],
         ["Apple мовчить:", "специфікації як не було"],
         ["v3 (75к/49.9к → 0.5 А), відео", "й сторінка → Hackaday, Slashdot"]),
        (658, ["травень", "2013"],
         ["слова «Apple» в даташиті", "нема жодного разу"],
         ["TI TPS2513: Divider 1/2/3,", "2.57–2.84 і 1.9–2.1 В, 30 кОм"]),
    ]

    # заголовки колонок
    p.append(text(AX / 2 + 20, 76, "коли", size=13, color=MUTED, bold=True))
    p.append(text(ax_a + aw_a / 2, 76, "що вимагав пристрій Apple", size=13, color=APPLE, bold=True))
    p.append(text(ax_b + aw_b / 2, 76, "що на той час знав і робив набір", size=13, color=FIELD, bold=True))

    # вісь
    p.append(line(AX, 96, AX, H - 30, color=MUTED, sw=2))

    for y, dt, a, b in rows:
        p.append(mtext(AX / 2 + 20, y - (len(dt) - 1) * 7 + 4, dt, size=12, color=INK, bold=True))
        p.append(circle(AX, y, 7, fill=BG, stroke=MUTED, sw=2))
        p.append(line(AX + 7, y, ax_a - 6, y, color=MUTED, sw=1, dash="3,3"))
        p.append(fitbox(ax_a, y - BH / 2, aw_a, BH, a, size=12,
                        fill="#f3eefa", stroke=APPLE, sw=1.3))
        p.append(fitbox(ax_b, y - BH / 2, aw_b, BH, b, size=12,
                        fill="#eef7f0", stroke=FIELD, sw=1.3))

    render(os.path.join(OUT, "hist-timeline.svg"), W, H, *p,
           title="Сім років: кожен рядок таблиці оплачений зламаним набором")


# ── hist-fork: розвилка серпня 2010 — чесний підпис проти вигідного ───────────
# Кульмінація історії: код на 1 А вже відомий, і саме тому спокуса написати його
# найбільша. Малюнок показує, що брехня джерела карається не мораллю, а фізикою.

def fig_hist_fork():
    W, H = 940, 566
    p = []

    b, _, _ = textbox(W / 2, 66,
                      ["Серпень 2010: код на 1 А вже розгаданий.",
                       "Що написати на лініях власного набору?"],
                      size=14, bold=True, fill="#fdf6e3", stroke=MUTED, sw=1.5, pad=12)
    p.append(b)

    cols = [
        (60, 380, POS, "#fdecea",
         ["Написати 2.8/2.0 — «я на 1 А»",
          "iPhone повірить і візьме цілий ампер",
          "але LT1302-5 віддає щонайбільше 600 мА",
          "дві пальчикові просідають, VBUS падає",
          "підпис зникає → відкат → знову бере → цикл"]),
        (500, 380, FIELD, "#eafaf0",
         ["Написати 2.0/2.0 — «я на 0.5 А»",
          "iPhone візьме рівно пів ампера",
          "LT1302-5 тримає це з добрим запасом",
          "VBUS стоїть, підпис лишається читним",
          "заряджає — повільніше, зате завжди"]),
    ]

    for x, w, col, fill, items in cols:
        cx = x + w / 2
        p.append(arrow(W / 2, 96, cx, 142, color=col, sw=1.8))
        yy = 150
        for i, s in enumerate(items):
            p.append(fitbox(x, yy, w, 52, s, size=13,
                            fill=fill, stroke=col, sw=(2 if i == 0 else 1.3),
                            bold=(i == 0)))
            if i < len(items) - 1:
                p.append(arrow(cx, yy + 52, cx, yy + 74, color=col, sw=1.5))
            yy += 76

    render(os.path.join(OUT, "hist-fork.svg"), W, H, *p,
           title="Чому набір підписався слабшим, ніж міг би збрехати")


# ═══ фігури до вставки proj-divider-signature ════════════════════════════════

import math


def _curve(pts, color, sw=2.4, dash=None):
    d = "M %.2f %.2f " % pts[0] + " ".join("L %.2f %.2f" % q for q in pts[1:])
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s '
            'stroke-linejoin="round"/>' % (d, color, sw, da))


# ── sh-settling: те саме джерело, два різні числа ─────────────────────────────
# Ідея: за штатні 1.5 такту банка S/H не встигає перезарядитися крізь 30 кОм —
# і показує суміш попереднього каналу з нинішнім. Тобто число залежить від того,
# що міряли ДО того. Довга вибірка стирає цю залежність начисто.

def fig_sh_settling():
    W, H = 860, 486
    p = []

    X0, X1 = 128, 626
    T0, T1 = 0.0, 4.0                 # мкс
    YT, YB = 100, 344                 # пікселі верху й низу шкали напруги
    VT, VB = 3.4, 0.0

    def px(t):
        return X0 + (t - T0) / (T1 - T0) * (X1 - X0)

    def py(v):
        return YB - (v - VB) / (VT - VB) * (YB - YT)

    TAU, VF = 0.296, 2.68             # стала часу (мкс) і напруга на лінії

    # приймальне вікно класу 2.7 — підпис винесено ПРАВОРУЧ від поля
    p.append(rect(X0, py(2.84), X1 - X0, py(2.57) - py(2.84),
                  fill="#f2ecf8", stroke=APPLE, sw=1.0, rx=0))
    p.append(mtext(X1 + 18, py(2.705) - 8, ["вікно", "класу 2.7 В"],
                   size=10, color=APPLE, anchor="start", bold=True))

    # осі
    p.append(line(X0, YT - 10, X0, YB, color=INK, sw=1.6))
    p.append(arrow(X0, YB, X1 + 10, YB, color=INK, sw=1.6))
    p.append(text(X1 + 18, YB + 5, "мкс", size=11, color=INK, anchor="start", bold=True))
    for v in [0, 1, 2, 3]:
        p.append(line(X0 - 6, py(v), X0, py(v), color=MUTED, sw=1.2))
        p.append(text(X0 - 13, py(v) + 4, "%d" % v, size=10, color=MUTED, anchor="end"))
    p.append(mtext(X0 - 58, py(1.7) - 13, ["напруга", "на банці", "S/H, В"],
                   size=10, color=MUTED, anchor="middle"))
    for t in [1, 2, 3, 4]:
        p.append(line(px(t), YB, px(t), YB + 6, color=MUTED, sw=1.2))
        p.append(text(px(t), YB + 21, "%d" % t, size=10, color=MUTED))

    # дві криві: та сама лінія D+, різна попередня вибірка
    for v0, col in [(0.0, NEG), (3.3, POS)]:
        pts = []
        for i in range(241):
            t = T0 + (T1 - T0) * i / 240.0
            v = VF + (v0 - VF) * math.exp(-t / TAU)
            pts.append((px(t), py(v)))
        p.append(_curve(pts, col))

    # маркер штатної вибірки 1.5 такту (125 нс) — підпис високо над полем
    t_short = 0.125
    p.append(line(px(t_short), YT - 8, px(t_short), YB, color=MUTED, sw=1.2, dash="4 3"))
    p.append(text(px(t_short) + 7, YT - 16, "1.5 такту", size=10, color=MUTED, anchor="start"))
    for v0, col in [(0.0, NEG), (3.3, POS)]:
        v = VF + (v0 - VF) * math.exp(-t_short / TAU)
        p.append(circle(px(t_short), py(v), 5, fill=col, stroke=col, sw=1.2))

    # маркер 41.5 такту (3.46 мкс) — обидві криві вже злилися
    t_long = 3.46
    p.append(line(px(t_long), YT - 8, px(t_long), YB, color=FIELD, sw=1.4, dash="5 3"))
    p.append(text(px(t_long), YT - 16, "41.5 такту", size=10, color=FIELD, bold=True))
    p.append(circle(px(t_long), py(VF), 5, fill=FIELD, stroke=FIELD, sw=1.2))

    # легенда — числа винесено сюди, щоб нічого не тіснити біля кривих
    rows = [
        (POS, "перед D+ міряли канал на 3.3 В  →  на 1.5 такту АЦП прочитає 3.09 В"),
        (NEG, "перед D+ міряли канал на 0 В  →  на 1.5 такту АЦП прочитає 0.92 В"),
        (FIELD, "на 41.5 такту обидві дають 2.68 В — попередня вже не має значення"),
    ]
    for i, (col, s) in enumerate(rows):
        y = 398 + i * 27
        p.append(circle(150, y - 4, 5, fill=col, stroke=col, sw=1.2))
        p.append(text(172, y, s, size=11, color=INK, anchor="start"))

    render(os.path.join(OUT, "sh-settling.svg"), W, H, *p,
           title="Та сама лінія, два різні числа — бо різна попередня вибірка")


# ── sh-load-budget: скільки з лінії можна брати ───────────────────────────────
# Ідея: банка S/H, яку смикають f разів на секунду, — це резистор 1/(C·f) на
# землю. Даташит обіцяє вікно лише за навантаження ≤5 мкА — це стеля частоти.

def fig_sh_load_budget():
    W, H = 860, 462
    p = []

    X0, X1 = 146, 606
    LF0, LF1 = 4.0, 6.1               # log10(частота, Гц): 10 кГц … ~1.26 МГц
    LI0, LI1 = -0.85, 1.55            # log10(струм, мкА)
    YT, YB = 96, 326

    def px(lf):
        return X0 + (lf - LF0) / (LF1 - LF0) * (X1 - X0)

    def py(li):
        return YB - (li - LI0) / (LI1 - LI0) * (YB - YT)

    L5 = math.log10(5.0)

    # заборонена смуга — понад 5 мкА даташит уже нічого не обіцяє
    p.append(rect(X0, YT, X1 - X0, py(L5) - YT, fill="#fdecea", stroke="#fdecea", sw=0, rx=0))
    p.append(line(X0, py(L5), X1, py(L5), color=POS, sw=1.8, dash="6 3"))
    p.append(mtext(X1 + 16, py(L5) - 22, ["5 мкА — умова,", "за якої даташит", "обіцяє вікно"],
                   size=10, color=POS, anchor="start", bold=True))

    # осі
    p.append(line(X0, YT - 10, X0, YB, color=INK, sw=1.6))
    p.append(arrow(X0, YB, X1 + 10, YB, color=INK, sw=1.6))
    p.append(text(X1 + 16, YB + 5, "Гц", size=11, color=INK, anchor="start", bold=True))
    for f, lab in [(1e4, "10 к"), (3e4, "30 к"), (1e5, "100 к"), (3e5, "300 к"), (1e6, "1 М")]:
        p.append(line(px(math.log10(f)), YB, px(math.log10(f)), YB + 6, color=MUTED, sw=1.2))
        p.append(text(px(math.log10(f)), YB + 21, lab, size=10, color=MUTED))
    for i, lab in [(-0.699, "0.2"), (0.0, "1"), (0.699, "5"), (1.0, "10"), (1.301, "20")]:
        p.append(line(X0 - 6, py(i), X0, py(i), color=MUTED, sw=1.2))
        p.append(text(X0 - 13, py(i) + 4, lab, size=10, color=MUTED, anchor="end"))
    p.append(mtext(X0 - 62, py(0.35) - 13, ["середній", "струм із", "лінії, мкА"],
                   size=10, color=MUTED, anchor="middle"))

    # I_сер = C·ΔU·f  →  у лог-лог це пряма
    def li_of(f):
        return math.log10(8e-12 * 2.7 * f * 1e6)

    pts = []
    for i in range(121):
        lf = LF0 + (LF1 - LF0) * i / 120.0
        pts.append((px(lf), py(li_of(10 ** lf))))
    p.append(_curve(pts, NEG))
    p.append(text(px(4.28), py(li_of(10 ** 4.28)) - 18, "I = C · ΔU · f",
                  size=11, color=NEG, anchor="start", bold=True))

    # робоча точка й точка провалу
    for f, col in [(47.6e3, FIELD), (857e3, POS)]:
        p.append(circle(px(math.log10(f)), py(li_of(f)), 6, fill=col, stroke=col, sw=1.2))

    # легенда — щоб підписи точок не лізли на криву
    rows = [
        (FIELD, "239.5 такту, конверсії поспіль: 47.6 кГц → 1.03 мкА  ✓"),
        (POS, "1.5 такту, безперервний режим: 857 кГц → 18.5 мкА  ✗ майже вчетверо понад умову"),
    ]
    for i, (col, s) in enumerate(rows):
        y = 380 + i * 27
        p.append(circle(154, y - 4, 5, fill=col, stroke=col, sw=1.2))
        p.append(text(176, y, s, size=11, color=INK, anchor="start"))

    b, _, _ = textbox(W / 2, 440,
                      "банка 8 пФ, яку смикають f разів на секунду, — це резистор 1/(C·f) на землю",
                      size=11, fill="#eafaf0", stroke=FIELD, sw=1.3, pad=8)
    p.append(b)

    render(os.path.join(OUT, "sh-load-budget.svg"), W, H, *p,
           title="Скільки з лінії можна брати: бюджет у мікроамперах")


# ── read-sequence: порядок дій і двері в один бік ─────────────────────────────
# Ідея: дільник читається РІВНО ОДИН раз — до будь-якої BC1.2-проби, бо проба
# перемикає блок у режим замикання й підпис зникає. Плюс засув після рішення.

def fig_read_sequence():
    W, H = 900, 496
    p = []

    BY = 156
    boxes = [
        (132, "від'єднано\nVBUS < 4.0 В\nліміт 0", MUTED, "#f2f3f5"),
        (350, "улягання, 100 мс\nPHY геть, піни аналогові\nліміт 100 мА", NEG, "#eef4ff"),
        (582, "читання\n239.5 такту, медіана з 5\nD+ і D−", APPLE, "#f2ecf8"),
        (786, "засув\nліміт виставлено\nбільше не читаємо", FIELD, "#eafaf0"),
    ]
    ws = []
    for cx, s, col, fill in boxes:
        b, w, h = textbox(cx, BY, s, size=10.5, color=INK, fill=fill, stroke=col, sw=1.8, pad=11)
        ws.append((cx, w, b))

    labels = ["VBUS > 4.4 В", "лінії вільні", "клас відомий"]
    for i in range(3):
        cx0, w0, _ = ws[i]
        cx1, w1, _ = ws[i + 1]
        x0, x1 = cx0 + w0 / 2 + 6, cx1 - w1 / 2 - 6
        p.append(arrow(x0, BY, x1, BY, color=INK, sw=1.6))
        p.append(text((x0 + x1) / 2, BY - 32, labels[i], size=9.5, color=INK))
    for _, _, b in ws:
        p.append(b)

    p.append(text(W / 2, 92, "єдиний шанс прочитати дільник — ось тут, до будь-якої проби",
                  size=12, color=APPLE, bold=True))

    # двері в один бік
    DY = 314
    p.append(line(582, BY + 46, 582, DY - 40, color=MUTED, sw=1.5, dash="4 3"))
    p.append(text(596, DY - 60, "якщо клас не впізнано — можна спробувати BC1.2,",
                  size=10, color=MUTED, anchor="start"))
    p.append(text(596, DY - 44, "але назад дороги вже нема:", size=10, color=MUTED, anchor="start"))

    d1, w1, _ = textbox(226, DY, "блок у режимі\nдільника\n2.7 В / 2.0 В",
                        size=10.5, bold=True, color=APPLE, fill="#f2ecf8", stroke=APPLE, sw=1.8, pad=11)
    d2, w2, _ = textbox(662, DY, "блок у режимі\nзамикання\nпідпису НЕМА",
                        size=10.5, bold=True, color="#b8901f", fill="#fdf6e3", stroke="#b8901f", sw=1.8, pad=11)
    p.append(arrow(226 + w1 / 2 + 7, DY - 14, 662 - w2 / 2 - 7, DY - 14, color=POS, sw=1.8))
    p.append(text(444, DY - 28, "BC1.2-проба: D+ ← 0.6 В", size=10, color=POS, bold=True))
    p.append(arrow(662 - w2 / 2 - 7, DY + 16, 226 + w1 / 2 + 7, DY + 16, color=MUTED, sw=1.4))
    p.append(text(444, DY + 36, "лише коли D+ провисне нижче 330 мВ", size=10, color=MUTED))
    p.append(d1)
    p.append(d2)

    b, _, _ = textbox(W / 2, 446,
                      "спершу дільник, потім BC1.2 — ніколи навпаки: проба стирає підпис, який ви ще не прочитали",
                      size=11, fill="#eafaf0", stroke=FIELD, sw=1.3, pad=8)
    p.append(b)

    render(os.path.join(OUT, "read-sequence.svg"), W, H, *p,
           title="Порядок дій після появи VBUS")


# ── помічники для комп-вставки: символи ключів ────────────────────────────────

def _sw_h(x, y, label, col=INK):
    """Горизонтальний РОЗІМКНЕНИЙ ключ; підпис над ним."""
    return [
        line(x - 26, y, x - 13, y, color=col, sw=1.8),
        circle(x - 13, y, 3.6, fill=BG, stroke=col, sw=1.6),
        line(x - 11, y - 2, x + 10, y - 13, color=col, sw=1.8),
        circle(x + 13, y, 3.6, fill=BG, stroke=col, sw=1.6),
        line(x + 13, y, x + 26, y, color=col, sw=1.8),
        text(x, y - 24, label, size=11, color=MUTED, bold=True),
    ]


def _sw_v(x, y, label, col=INK):
    """Вертикальний РОЗІМКНЕНИЙ ключ; підпис праворуч."""
    return [
        line(x, y - 26, x, y - 13, color=col, sw=1.8),
        circle(x, y - 13, 3.6, fill=BG, stroke=col, sw=1.6),
        line(x + 2, y - 11, x + 13, y + 10, color=col, sw=1.8),
        circle(x, y + 13, 3.6, fill=BG, stroke=col, sw=1.6),
        line(x, y + 13, x, y + 26, color=col, sw=1.8),
        text(x + 28, y + 4, label, size=11, color=MUTED, bold=True, anchor="start"),
    ]


# ── comp-block: три джерела, чотири ключі, один автомат ───────────────────────
# Ідея: усередині немає ні шини, ні регістрів — лише опорні джерела за навмисно
# великим опором і ключі, що їх комутують. Автомат стежить за ВЛАСНИМ вузлом DP.

def fig_comp_block():
    W, H = 920, 570
    p = []

    y_dp, y_12, y_dm = 168, 268, 356
    SRC_X, RES_X, SW_X = 116, 250, 384
    RAIL_X0, RAIL_X1 = 410, 752
    S4_X, SENSE_X = 652, 580

    # межа кристала
    p.append(text(80, 60, "мікросхема-контролер зарядного порту",
                  size=12, color=MUTED, anchor="start"))
    p.append(rect(80, 68, 692, 332, fill="#fbfbfc", stroke=MUTED, sw=1.4, rx=10))

    # рейки DP і DM
    p.append(line(RAIL_X0, y_dp, RAIL_X1, y_dp, color=POS, sw=2.4))
    p.append(line(RAIL_X0, y_dm, RAIL_X1, y_dm, color=NEG, sw=2.4))

    rows = [
        (y_dp, "2.7 В", "30 кОм", "S1", POS),
        (y_12, "1.2 В", "105 кОм", "S3", MUTED),
        (y_dm, "2.0 В", "30 кОм", "S2", NEG),
    ]
    for y, volts, res, sw_name, col in rows:
        p.append(rect(SRC_X - 34, y - 19, 68, 38, fill=BG, stroke=col, sw=1.7, rx=5))
        p.append(text(SRC_X, y + 5, volts, size=13, color=col, bold=True))
        p.append(line(SRC_X + 34, y, RES_X - 19, y, color=INK, sw=1.7))
        p.append(rect(RES_X - 19, y - 14, 38, 28, fill=BG, stroke=INK, sw=1.6, rx=3))
        p.append(text(RES_X, y + 30, res, size=10, color=MUTED, bold=True))
        p.append(line(RES_X + 19, y, SW_X - 26, y, color=INK, sw=1.7))
        p.extend(_sw_h(SW_X, y, sw_name))

    # 1.2 В приєднується до рейки DP окремою гілкою (нічого не перетинає)
    p.append(line(SW_X + 26, y_12, 470, y_12, color=INK, sw=1.7))
    p.append(line(470, y_12, 470, y_dp, color=INK, sw=1.7))
    p.append(circle(470, y_dp, 4, fill=INK, stroke=INK, sw=1))

    # S4 — місток замикання між рейками
    p.append(circle(S4_X, y_dp, 4, fill=INK, stroke=INK, sw=1))
    p.append(line(S4_X, y_dp, S4_X, y_12 - 26, color=INK, sw=1.8))
    p.extend(_sw_v(S4_X, y_12, "S4"))
    p.append(line(S4_X, y_12 + 26, S4_X, y_dm, color=INK, sw=1.8))
    p.append(circle(S4_X, y_dm, 4, fill=INK, stroke=INK, sw=1))

    # автомат: сенс власного вузла DP (лінія йде ВГОРУ — нічого не перетинає)
    p.append(circle(SENSE_X, y_dp, 4, fill=INK, stroke=INK, sw=1))
    p.append(line(SENSE_X, y_dp, SENSE_X, 122, color=MUTED, sw=1.6, dash="5,4"))
    b, _, _ = textbox(580, 96, "автомат: читає ВЛАСНИЙ вузол DP\nповернення до дільника — нижче 330 мВ",
                      size=11, fill="#f2ecf8", stroke=APPLE, sw=1.4, pad=9)
    p.append(b)

    # ніжки на межі кристала
    for y, name, col in [(y_dp, "DP", POS), (y_dm, "DM", NEG)]:
        p.append(rect(752, y - 17, 40, 34, fill=FILL, stroke=INK, sw=1.7, rx=4))
        p.append(text(772, y + 5, name, size=12, color=col, bold=True))
        p.append(line(792, y, 856, y, color=col, sw=2.0))
    p.append(text(866, y_dp + 5, "D+", size=12, color=POS, anchor="start", bold=True))
    p.append(text(866, y_dm + 5, "D−", size=12, color=NEG, anchor="start", bold=True))

    # три режими = три комбінації ключів
    modes = [
        (190, "Дільник (типово)\nS1 + S2 замкнені", APPLE, "#f2ecf8"),
        (460, "Замикання BC1.2\nлише S4 замкнений", FIELD, "#eafaf0"),
        (730, "Режим 1.2 В\nS3 + S4 замкнені", "#b8901f", "#fdf6e3"),
    ]
    for x, s, col, fill in modes:
        b, _, _ = textbox(x, 450, s, size=11, fill=fill, stroke=col, sw=1.4, pad=9)
        p.append(b)

    b, _, _ = textbox(W / 2, 530,
                      "ні шини, ні регістрів: увесь «протокол» — які з чотирьох ключів зараз замкнені",
                      size=11, fill="#eafaf0", stroke=FIELD, sw=1.3, pad=8)
    p.append(b)

    render(os.path.join(OUT, "comp-block.svg"), W, H, *p,
           title="Що всередині: три опорні джерела й чотири ключі")


# ── comp-pinout: шість ніжок проти шістнадцяти ────────────────────────────────
# Ідея: підпис коштує РІВНО дві ніжки. Усі інші ніжки повного виконання — це вже
# не підпис, а ключ, дані, режим і телеметрія. Контраст 6 ↔ 16 і є повідомленням.

def fig_comp_pinout():
    W, H = 900, 600
    p = []

    PWR, SIG, DAT, MOD, CUR, TEL = POS, APPLE, NEG, "#b8901f", FIELD, MUTED

    # ── мінімальне виконання: лише підпис, 6 ніжок ──
    p.append(text(210, 96, "мінімальне: лише підпис", size=13, color=INK, bold=True))
    p.append(rect(150, 150, 120, 150, fill=FILL, stroke=INK, sw=1.8, rx=6))
    left6 = [(180, "1", "DP1", SIG), (225, "2", "GND", PWR), (270, "3", "DP2", SIG)]
    right6 = [(180, "6", "DM1", SIG), (225, "5", "IN", PWR), (270, "4", "DM2", SIG)]
    for y, num, name, col in left6:
        p.append(line(150, y, 118, y, color=col, sw=2.0))
        p.append(text(112, y + 4, name, size=12, color=col, anchor="end", bold=True))
        p.append(text(162, y + 4, num, size=9, color=MUTED))
    for y, num, name, col in right6:
        p.append(line(270, y, 302, y, color=col, sw=2.0))
        p.append(text(308, y + 4, name, size=12, color=col, anchor="start", bold=True))
        p.append(text(258, y + 4, num, size=9, color=MUTED))

    b, _, _ = textbox(210, 355, "два незалежні порти;\nдві ніжки з шести — живлення",
                      size=11, fill="#f2ecf8", stroke=SIG, sw=1.4, pad=9)
    p.append(b)

    # ── повне виконання: 16 ніжок ──
    p.append(text(625, 96, "повне: підпис + ключ + дані", size=13, color=INK, bold=True))
    p.append(rect(560, 120, 130, 320, fill=FILL, stroke=INK, sw=1.8, rx=6))
    left16 = [(150, "IN", PWR), (190, "OUT", PWR), (230, "GND", PWR), (270, "EN", PWR),
              (310, "DP_IN", SIG), (350, "DM_IN", SIG),
              (390, "DP_OUT", DAT), (430, "DM_OUT", DAT)]
    right16 = [(150, "CTL1", MOD), (190, "CTL2", MOD), (230, "CTL3", MOD),
               (270, "ILIM_HI", CUR), (310, "ILIM_LO", CUR),
               (350, "FAULT", TEL), (390, "STATUS", TEL), (430, "CS", TEL)]
    for y, name, col in left16:
        p.append(line(560, y, 528, y, color=col, sw=2.0))
        p.append(text(522, y + 4, name, size=11, color=col, anchor="end", bold=True))
    for y, name, col in right16:
        p.append(line(690, y, 722, y, color=col, sw=2.0))
        p.append(text(728, y + 4, name, size=11, color=col, anchor="start", bold=True))
    p.append(text(625, 460, "+ тепловий пад", size=10, color=MUTED))

    # легенда груп
    legend = [(80, PWR, "живлення"), (200, SIG, "підпис"), (300, DAT, "дані наскрізь"),
              (450, MOD, "режим"), (550, CUR, "струм"), (650, TEL, "телеметрія")]
    for x, col, name in legend:
        p.append(rect(x - 8, 514, 12, 12, fill=col, stroke=col, sw=1, rx=2))
        p.append(text(x + 10, 524, name, size=10, color=INK, anchor="start"))

    b, _, _ = textbox(W / 2, 566,
                      "підпис коштує рівно дві ніжки — решта чотирнадцять уже не про підпис",
                      size=11, fill="#eafaf0", stroke=FIELD, sw=1.3, pad=8)
    p.append(b)

    render(os.path.join(OUT, "comp-pinout.svg"), W, H, *p,
           title="Розпіновка класу: шість ніжок і шістнадцять")


# ── comp-crossing: конфіг лежить у міді ───────────────────────────────────────
# Ідея: чип ЗАВЖДИ тримає 2.7 В на DP і 2.0 В на DM. Що це означає — вирішує
# розводка: куди саме розвели ці ніжки. Схрестив доріжки — змінив клас струму.

def fig_comp_crossing():
    W, H = 880, 470
    p = []

    panels = [
        (40, "розводка «як є»", False, "D+ = 2.7 В, D− = 2.0 В\nDivider 2 → 10 Вт → 2.1 А", "#b8901f", "#fdf6e3"),
        (460, "доріжки схрещено", True, "D+ = 2.0 В, D− = 2.7 В\nDivider 1 → 5 Вт → 1.0 А", FIELD, "#eafaf0"),
    ]
    for ox, title, crossed, verdict, col, fill in panels:
        p.append(rect(ox, 78, 360, 254, fill="#fbfbfc", stroke=MUTED, sw=1.3, rx=10))
        p.append(text(ox + 180, 104, title, size=13, color=INK, bold=True))

        # чип: напруги на ніжках НЕ змінюються ніколи
        p.append(rect(ox + 16, 126, 96, 108, fill=FILL, stroke=INK, sw=1.8, rx=5))
        p.append(text(ox + 64, 158, "DP  2.7 В", size=11, color=POS, bold=True))
        p.append(text(ox + 64, 204, "DM  2.0 В", size=11, color=NEG, bold=True))

        # роз'єм
        p.append(rect(ox + 250, 126, 86, 108, fill=FILL, stroke=INK, sw=1.8, rx=5))
        p.append(text(ox + 293, 158, "D+", size=13, color=INK, bold=True))
        p.append(text(ox + 293, 204, "D−", size=13, color=INK, bold=True))

        # доріжки — колір везе за собою ніжку, тож перестановку видно оком
        if crossed:
            p.append(line(ox + 112, 152, ox + 250, 198, color=POS, sw=2.4))
            p.append(line(ox + 112, 198, ox + 250, 152, color=NEG, sw=2.4))
        else:
            p.append(line(ox + 112, 152, ox + 250, 152, color=POS, sw=2.4))
            p.append(line(ox + 112, 198, ox + 250, 198, color=NEG, sw=2.4))

        b, _, _ = textbox(ox + 176, 290, verdict, size=11, fill=fill, stroke=col, sw=1.4, pad=9)
        p.append(b)

    b, _, _ = textbox(W / 2, 400,
                      "той самий чип, ті самі вольти: клас струму задано міддю, а не регістром",
                      size=11, fill="#eafaf0", stroke=FIELD, sw=1.3, pad=8)
    p.append(b)

    render(os.path.join(OUT, "comp-crossing.svg"), W, H, *p,
           title="«Перший байт» написано міддю")


# ── comp-cable-comp: компенсація кабелю і її ціна ─────────────────────────────
# Ідея: ніжка CS піднімає VBUS під навантаженням, щоб на дальньому кінці кабелю
# лишалося 5 В. Але дільник тримає ЧАСТКУ від VBUS — і вузол класу 2.0 їде до стелі.

def fig_comp_cable_comp():
    W, H = 900, 470
    p = []

    # ── ліворуч: ланцюжок причин ──
    p.append(text(250, 124, "як CS піднімає VBUS", size=13, color=INK, bold=True))
    chain = [
        (160, "струм у кабель росте"),
        (215, "CS тягне струм із вузла FB"),
        (270, "регулятор бачить занижений FB"),
        (325, "і піднімає свій вихід до ≈5.2 В"),
        (380, "на дальньому кінці кабелю — знову ≈5 В"),
    ]
    for i, (y, s) in enumerate(chain):
        col, fill = (FIELD, "#eafaf0") if i == len(chain) - 1 else (INK, FILL)
        b, _, _ = textbox(250, y, s, size=11, fill=fill, stroke=col, sw=1.4, pad=8)
        p.append(b)
        if i < len(chain) - 1:
            p.append(arrow(250, y + 16, 250, y + 39, color=MUTED, sw=1.6))

    # ── праворуч: вертикальна вісь напруги вузла класу 2.0 ──
    p.append(text(700, 124, "чим це віддається на підписі", size=13, color=INK, bold=True))
    AX_X, Y0, V0, SCALE = 700, 380, 1.85, 733.0   # px на вольт

    def vy(v):
        return Y0 - (v - V0) * SCALE

    p.append(line(AX_X, 390, AX_X, 170, color=INK, sw=2.0))
    # приймальне вікно класу 2.0
    p.append(rect(AX_X - 30, vy(2.1), 60, vy(1.9) - vy(2.1),
                  fill="#eafaf0", stroke=FIELD, sw=1.6, rx=4))
    p.append(text(AX_X - 40, vy(1.9) + 4, "1.9 В", size=10, color=FIELD, anchor="end", bold=True))
    p.append(text(AX_X - 40, vy(2.1) + 4, "2.1 В", size=10, color=FIELD, anchor="end", bold=True))
    p.append(text(752, 186, "стеля вікна 2.1 В", size=10, color=FIELD, anchor="start"))

    for v, lab, col in [(2.00, "2.00 В — при VBUS 5.0 В", NEG),
                        (2.08, "2.08 В — при VBUS 5.2 В", POS)]:
        y = vy(v)
        p.append(line(AX_X - 40, y, AX_X + 44, y, color=col, sw=2.0))
        p.append(circle(AX_X, y, 4.5, fill=col, stroke=col, sw=1))
        p.append(text(752, y + 4 if v == 2.00 else 218, lab, size=10, color=col,
                      anchor="start", bold=True))

    b, _, _ = textbox(W / 2, 440,
                      "компенсація кабелю рятує ватти — і водночас підпихає вузол класу 2.0 до стелі його вікна",
                      size=11, fill="#fdf6e3", stroke="#b8901f", sw=1.3, pad=8)
    p.append(b)

    render(os.path.join(OUT, "comp-cable-comp.svg"), W, H, *p,
           title="Ніжка CS: компенсація кабелю та її побічний ефект")


if __name__ == "__main__":
    fig_code_table()
    fig_divider_hardware()
    fig_window()
    fig_two_dialects()
    fig_budget_stack()
    fig_budget_bars()
    fig_level_ladder()
    fig_hist_timeline()
    fig_hist_fork()
    fig_sh_settling()
    fig_sh_load_budget()
    fig_read_sequence()
    fig_comp_block()
    fig_comp_pinout()
    fig_comp_crossing()
    fig_comp_cable_comp()
    print("OK: figures written to", OUT)
