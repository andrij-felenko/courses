# -*- coding: utf-8 -*-
"""Фігури до теми «Калібрування DDR-інтерфейсу (тренування пам'яті)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Універсальна петля тренування: крути ручку → міряй → шукай центр ───────
def fig_loop():
    W, H = 860, 470
    frags = []

    # Верхня смуга — сама петля вимірювання (4 кроки по колу)
    steps = [
        (170, 130, "1. Постав\nручку\nна крок k\n(затримка / VREF)", "#eef2ff", NEG),
        (430, 130, "2. Прожени\nвідомий взірець\nчерез канал\n(запиши й прочитай)", "#eafaf1", FIELD),
        (690, 130, "3. Порівняй\nз еталоном:\nзбіглось?\nтак / ні", "#fdf2f2", POS),
    ]
    boxes = []
    for cx, cy, s, fill, stroke in steps:
        b, w, h = textbox(cx, cy, s, size=12.5, fill=fill, stroke=stroke, pad=13, bold=False)
        frags.append(b)
        boxes.append((cx, cy, w, h))

    # стрілки між кроками
    (c0, _, w0, _), (c1, _, w1, _), (c2, _, w2, _) = boxes
    frags.append(arrow(c0 + w0/2, 130, c1 - w1/2, 130, color=INK, sw=2))
    frags.append(arrow(c1 + w1/2, 130, c2 - w2/2, 130, color=INK, sw=2))
    # зворотна стрілка «наступний крок k+1»
    frags.append(line(c2, 130 + 52, c2, 210, color=MUTED, sw=1.8))
    frags.append(line(c2, 210, c0, 210, color=MUTED, sw=1.8, dash="5,4"))
    frags.append(arrow(c0, 210, c0, 130 + 52, color=MUTED, sw=1.8))
    frags.append(text((c0 + c2) / 2, 226, "наступний крок k+1 — доки не перебрали весь діапазон",
                     size=11.5, color=MUTED))

    # Нижня частина — карта результату: рядок F/P, вікно й центр
    y = 300
    x0 = 170
    cell = 42
    res = "FFFPPPPPPPFF"           # результат розгортки
    passes = [i for i, c in enumerate(res) if c == 'P']
    lo, hi = passes[0], passes[-1]
    mid = (lo + hi) // 2
    frags.append(text(x0 - 14, y + cell*0.62, "крок:", size=11.5, anchor="end", color=MUTED))
    for i, c in enumerate(res):
        x = x0 + i * cell
        if c == 'P':
            fill, stroke, tc = "#eafaf1", FIELD, FIELD
        else:
            fill, stroke, tc = "#fdecea", POS, POS
        frags.append(rect(x, y, cell - 4, cell - 4, fill=fill, stroke=stroke, sw=1.5, rx=4))
        frags.append(text(x + (cell - 4)/2, y + cell*0.60, c, size=14, color=tc, bold=True))
        frags.append(text(x + (cell - 4)/2, y - 8, str(i), size=9.5, color=MUTED))

    # дужка над вікном P
    xl = x0 + lo * cell
    xr = x0 + hi * cell + (cell - 4)
    frags.append(line(xl, y - 24, xr, y - 24, color=FIELD, sw=1.8))
    frags.append(line(xl, y - 24, xl, y - 18, color=FIELD, sw=1.8))
    frags.append(line(xr, y - 24, xr, y - 18, color=FIELD, sw=1.8))
    frags.append(text((xl + xr)/2, y - 30, "вікно, де канал працює (просвіт ока)", size=11, color=FIELD))

    # центр — стрілка вниз
    xc = x0 + mid * cell + (cell - 4)/2
    frags.append(arrow(xc, y + cell + 4, xc, y + cell + 40, color=NEG, sw=2.4))
    frags.append(text(xc, y + cell + 58, "ставимо ручку в ЦЕНТР вікна — найдалі від обох країв,",
                     size=11.5, color=NEG, bold=True))
    frags.append(text(xc, y + cell + 74, "тут запас максимальний", size=11.5, color=NEG))

    render(os.path.join(IMG, "training-loop.svg"), W, H, *frags,
           title="Ядро тренування: розгорни ручку, поміряй збіг, сядь у центр вікна")


# ── 2. Вирівнювання запису як бінарний пошук краю (0 → 1) ────────────────────
def fig_write_level():
    W, H = 840, 420
    frags = []

    # Ліворуч: механізм — строб питає, чіп відповідає рівнем такту
    b, wp, hp = textbox(140, 120, "PHY\nсуне затримку\nстроба DQS\nна крок kδ",
                        size=12.5, fill="#eafaf1", stroke=FIELD, pad=13, bold=False)
    frags.append(b)
    b, wd, hd = textbox(660, 120, "DRAM (режим MR1[7]=1):\nу мить фронту DQS\nзащіпає рівень такту CK\nі вертає його на DQ",
                        size=12, fill="#fdf2f2", stroke=POS, pad=13)
    frags.append(b)
    frags.append(arrow(140 + wp/2, 100, 660 - wd/2, 100, color=FIELD, sw=2))
    frags.append(text((140+wp/2 + 660-wd/2)/2, 88, "строб DQS →", size=11.5, color=FIELD))
    frags.append(arrow(660 - wd/2, 140, 140 + wp/2, 140, color=NEG, sw=2))
    frags.append(text((140+wp/2 + 660-wd/2)/2, 158, "← відповідь на DQ: 0 або 1", size=11.5, color=NEG))

    # Знизу: як пливе точка защіпання по такту CK і де 0 стає 1
    y = 250
    x0 = 130
    unit = 58
    # такт CK — прямокутна хвиля
    frags.append(text(x0 - 14, y + 4, "CK", size=12, anchor="end", color=INK, bold=True))
    patt = "0101010"
    xs = x0
    prev = None
    yhi, ylo = y - 22, y + 22
    for c in patt:
        lvl = yhi if c == '1' else ylo
        frags.append(line(xs, lvl, xs + unit, lvl, color=INK, sw=2.2))
        if prev is not None and prev != lvl:
            frags.append(line(xs, prev, xs, lvl, color=INK, sw=2.2))
        prev = lvl
        xs += unit

    # моменти защіпання строба (зростаюча затримка) з відповіддю
    fronts = [
        (0.35, "0", POS), (0.75, "0", POS), (1.15, "0", POS),
        (1.55, "1", FIELD), (1.95, "1", FIELD),
    ]
    for frac, val, col in fronts:
        xx = x0 + frac * unit * 2  # умовне положення вздовж такту
        frags.append(line(xx, yhi - 30, xx, ylo + 10, color=col, sw=1.6, dash="3,3"))
        frags.append(circle(xx, yhi - 30, 4, fill=col, stroke=col))
        frags.append(text(xx, yhi - 40, val, size=13, color=col, bold=True))
    # де стрибок 0→1
    xflip = x0 + 1.35 * unit * 2
    frags.append(arrow(xflip, y + 60, xflip, y + 30, color=NEG, sw=2.2))
    frags.append(text(xflip, y + 78, "стрибок 0 → 1: строб щойно наздогнав фронт CK —", size=11.5,
                     color=NEG, bold=True))
    frags.append(text(xflip, y + 94, "ось шукана затримка вирівнювання запису", size=11.5, color=NEG))

    frags.append(fitbox(70, 350, 700, 44,
        "Одна ручка, монотонна відповідь: збільшуємо затримку — рано чи пізно 0 зміниться на 1.\n"
        "Це край, а не вікно, тож досить знайти саму точку переходу (можна навпіл — бінарним пошуком).",
        size=11.5, fill="#fffef0", stroke="#caa300"))

    render(os.path.join(IMG, "write-level.svg"), W, H, *frags,
           title="Вирівнювання запису: пошук єдиної точки переходу 0→1")


# ── 3. Двовимірна карта (VREF × затримка) — шму-графік, беремо глибину ────────
def fig_shmoo():
    W, H = 800, 500
    frags = []
    ox, oy = 150, 90
    cols, rows = 15, 13
    cw, ch = 32, 26

    # осі
    frags.append(line(ox, oy, ox, oy + rows * ch, color=INK, sw=1.6))
    frags.append(line(ox, oy + rows * ch, ox + cols * cw, oy + rows * ch, color=INK, sw=1.6))
    frags.append(text(ox + cols * cw / 2, oy + rows * ch + 34,
                     "затримка строба (зсув у часі) →", size=12.5, color=INK))
    frags.append(text(ox - 40, oy + rows * ch / 2, "VREF",
                     size=12.5, color=INK, anchor="middle"))
    frags.append(text(ox - 40, oy + rows * ch / 2 + 16, "(поріг)",
                     size=11, color=MUTED, anchor="middle"))
    frags.append(text(ox - 40, oy - 8, "↑", size=15, color=INK))

    # форма «ока» у площині: центр (c0,r0), працює всередині еліпса
    c0, r0 = 7.0, 6.0
    a, b = 5.2, 4.2
    def passes(c, r):
        return ((c - c0) / a) ** 2 + ((r - r0) / b) ** 2 <= 1.0

    best = None
    best_depth = -1
    for r in range(rows):
        for c in range(cols):
            x = ox + c * cw
            y = oy + r * ch
            ok = passes(c + 0.5, r + 0.5)
            if ok:
                # «глибина» = запас до найближчого краю (мінімум по 4 напрямках)
                depth = 0
                for dc, dr in ((1,0),(-1,0),(0,1),(0,-1)):
                    d = 0
                    cc, rr = c + 0.5, r + 0.5
                    while passes(cc, rr):
                        d += 1; cc += dc; rr += dr
                    depth = depth if depth and depth < d else (d if depth == 0 else min(depth, d))
                frags.append(rect(x + 2, y + 2, cw - 4, ch - 4, fill="#eafaf1", stroke=FIELD, sw=1, rx=3))
                frags.append(text(x + cw/2, y + ch/2 + 4, "P", size=11, color=FIELD, bold=True))
                if depth > best_depth:
                    best_depth = depth; best = (c, r, x, y)
            else:
                frags.append(rect(x + 2, y + 2, cw - 4, ch - 4, fill="#fdecea", stroke="#e8b4ae", sw=1, rx=3))
                frags.append(text(x + cw/2, y + ch/2 + 4, "·", size=13, color="#c98d86"))

    # позначити обрану точку — найглибшу всередині
    if best:
        c, r, x, y = best
        frags.append(rect(x + 1, y + 1, cw - 2, ch - 2, fill="none", stroke=NEG, sw=2.6, rx=3))
        frags.append(arrow(x + cw + 70, y - 26, x + cw/2 + 4, y + 2, color=NEG, sw=2))
        frags.append(text(x + cw + 74, y - 34, "обрана точка:", size=11.5, color=NEG, anchor="start", bold=True))
        frags.append(text(x + cw + 74, y - 20, "найглибше всередині —", size=11, color=NEG, anchor="start"))
        frags.append(text(x + cw + 74, y - 6, "запас у ВСІ боки", size=11, color=NEG, anchor="start"))

    frags.append(fitbox(70, 440, 660, 42,
        "P — тут читання правильне, · — тут уже помилки. Область P і є око у площині «час × поріг».\n"
        "Тренування не бере край: воно шукає клітинку, найдальшу від межі в усі боки — там найбільший запас на дрейф.",
        size=11.5, fill="#f7fdfa", stroke=FIELD))

    render(os.path.join(IMG, "shmoo.svg"), W, H, *frags,
           title="Двовимірна розгортка VREF × затримка: беремо не край, а глибину")


# ── 4. ZQ-блок: зовнішній еталон · керований опір ніжками · компаратор ───────
def fig_zq_block():
    W, H = 880, 470
    frags = []

    # Ліворуч — ніжка ZQ і зовнішній точний резистор до землі
    frags.append(text(120, 70, "ніжка ZQ", size=13, color=INK, bold=True))
    frags.append(circle(120, 100, 7, fill="#fff", stroke=INK, sw=2))
    frags.append(line(120, 107, 120, 175, color=INK, sw=2))
    # резистор-еталон
    b, wr, hr = textbox(120, 205, "точний\nзовнішній\n240 Ω · 1%", size=11.5,
                        fill="#eef2ff", stroke=NEG, pad=10)
    frags.append(b)
    frags.append(line(120, 205 + hr/2, 120, 300, color=INK, sw=2))
    frags.append(line(96, 300, 144, 300, color=INK, sw=2.4))   # земля
    frags.append(line(104, 306, 136, 306, color=INK, sw=2))
    frags.append(line(112, 312, 128, 312, color=INK, sw=1.6))
    frags.append(text(120, 330, "GND", size=10.5, color=MUTED))

    # Усередині чіпа — набір паралельних транзисторних ніжок як керований опір
    chip_x = 300
    frags.append(rect(chip_x, 70, 500, 250, fill="#fafafa", stroke=MUTED, sw=1.4, rx=10))
    frags.append(text(chip_x + 250, 92, "усередині чіпа DRAM", size=12, color=MUTED))

    # набір ніжок (кванти опору)
    legs_x = chip_x + 40
    legs_y = 150
    frags.append(text(legs_x + 90, legs_y - 34, "керований опір: набір паралельних ніжок",
                     size=11.5, color=INK, bold=True))
    for i in range(6):
        x = legs_x + i * 30
        on = i < 4
        col = FIELD if on else MUTED
        fill = "#eafaf1" if on else "#f2f2f2"
        frags.append(rect(x, legs_y, 18, 40, fill=fill, stroke=col, sw=1.6, rx=3))
        frags.append(text(x + 9, legs_y + 24, "■" if on else "□", size=12, color=col))
    frags.append(text(legs_x + 90, legs_y + 60,
                     "більше ввімкнено (■) → менший опір; код керує скількома", size=10.5, color=MUTED))
    # вузол порівняння
    node_x = chip_x + 250
    frags.append(line(legs_x + 6*30 - 12, legs_y + 20, node_x, legs_y + 20, color=INK, sw=2))
    frags.append(circle(node_x, legs_y + 20, 5, fill=INK, stroke=INK))
    frags.append(text(node_x, legs_y + 6, "вузол", size=10, color=MUTED))
    # лінія до ніжки ZQ (спільний вузол з еталоном)
    frags.append(line(chip_x, legs_y + 20, 120, legs_y + 20, color=INK, sw=2, dash="4,3"))
    frags.append(line(120, legs_y + 20, 120, 175, color=INK, sw=2))
    frags.append(text(210, legs_y + 10, "той самий вузол", size=9.5, color=MUTED))

    # компаратор «більше/менше»
    comp_x = node_x + 60
    comp_y = legs_y + 20
    frags.append('<polygon points="%.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="#fdf2f2" '
                 'stroke="%s" stroke-width="1.6"/>' % (comp_x, comp_y - 34, comp_x, comp_y + 34,
                                                        comp_x + 58, comp_y, POS))
    frags.append(text(comp_x + 20, comp_y + 4, "?", size=20, color=POS, bold=True))
    frags.append(line(node_x, comp_y, comp_x, comp_y - 14, color=INK, sw=1.8))
    frags.append(text(comp_x - 6, comp_y - 20, "напруга вузла", size=9.5, color=MUTED, anchor="end"))
    frags.append(line(comp_x - 18, comp_y + 40, comp_x, comp_y + 14, color=NEG, sw=1.8))
    frags.append(text(comp_x - 22, comp_y + 52, "опора VDDQ/2", size=9.5, color=NEG, anchor="end"))
    # вихід компаратора: більше/менше
    b, wc, hc = textbox(comp_x + 140, comp_y, 'опір\n«більше / менше»\nеталона?', size=11,
                        fill="#fff", stroke=POS, pad=9)
    frags.append(b)
    frags.append(arrow(comp_x + 58, comp_y, comp_x + 140 - wc/2, comp_y, color=INK, sw=1.8))

    # логіка послідовного наближення
    b, wl, hl = textbox(chip_x + 250, 285,
        "логіка послідовного наближення: підкручує код, доки внутрішній опір = 240 Ω",
        size=11, fill="#eef2ff", stroke=NEG, pad=9)
    frags.append(b)
    frags.append(line(comp_x + 140, comp_y + hc/2, comp_x + 140, 285 - hl/2, color=MUTED, sw=1.6, dash="4,3"))

    # перенесення коду на всі DQ
    b, wo, ho = textbox(chip_x + 250, 385,
        "знайдений КОД → на всі виводи DQ:\nсила драйвера (читання) · опір термінації (запис)",
        size=11.5, fill="#eafaf1", stroke=FIELD, pad=11)
    frags.append(b)
    frags.append(arrow(chip_x + 250, 320, chip_x + 250, 385 - ho/2, color=FIELD, sw=2.2))

    render(os.path.join(IMG, "zq-block.svg"), W, H, *frags,
           title="ZQ-калібрування: чіп вивіряє власний опір за зовнішнім еталоном")


# ── 5. Послідовне наближення опору: код зважує ніжки по бітах ─────────────────
def fig_zq_sar():
    W, H = 926, 400
    frags = []
    frags.append(text(W/2, 56, "Пошук коду опору: той самий метод, що в АЦП послідовного наближення",
                     size=12.5, color=MUTED))

    # вісь опору квантами (кількість увімкнених ніжок)
    ox, oy = 90, 300
    axw = 640
    frags.append(line(ox, oy, ox + axw, oy, color=INK, sw=1.8))
    frags.append(arrow(ox + axw, oy, ox + axw + 20, oy, color=INK, sw=1.8))
    frags.append(text(ox + axw + 20, oy + 22, "код (кількість ніжок) →", size=11, color=INK, anchor="end"))
    # ціль — еталон 240 Ω
    tgt = ox + axw * 0.58
    frags.append(line(tgt, oy - 150, tgt, oy + 12, color=FIELD, sw=1.8, dash="5,4"))
    frags.append(text(tgt, oy - 158, "еталон 240 Ω", size=11.5, color=FIELD, bold=True))

    # кроки наближення: старший квант → молодший, компаратор веде навпіл
    steps = [
        (0.50, "1", "старший квант: замало → лишити", NEG),
        (0.75, "0", "наступний: забагато → зняти", POS),
        (0.62, "1", "далі: замало → лишити", NEG),
        (0.58, "1", "молодший: зійшлось", FIELD),
    ]
    yy = oy - 30
    for i, (frac, bit, note, col) in enumerate(steps):
        x = ox + axw * frac
        frags.append(circle(x, yy, 6, fill=col, stroke=col))
        frags.append(line(x, yy, x, oy, color=col, sw=1.4, dash="2,3"))
        frags.append(text(x, yy - 12, "крок %d: біт=%s" % (i+1, bit), size=10.5, color=col, bold=True))
        frags.append(text(ox + axw + 30, yy + 4, note, size=10, color=col, anchor="start"))
        yy -= 34

    frags.append(fitbox(70, 330, 680, 46,
        "Компаратор дає лише «більше/менше» — тож логіка йде від старшого кванта до молодшого,\n"
        "щоразу лишаючи ніжку ввімкненою чи ні. Кілька кроків замість перебору всіх кодів.",
        size=11, fill="#fffef0", stroke="#caa300"))

    render(os.path.join(IMG, "zq-sar.svg"), W, H, *frags,
           title="Опір теж шукають бінарно: послідовне наближення до еталона")


# ── 6. Коли калібрувати: довге на старті, коротке в паузах, не в звертанні ────
def fig_zq_timing():
    W, H = 840, 360
    frags = []

    # шкала часу
    ox, oy = 60, 150
    axw = 720
    frags.append(line(ox, oy, ox + axw, oy, color=INK, sw=1.6))
    frags.append(arrow(ox + axw, oy, ox + axw + 18, oy, color=INK, sw=1.6))
    frags.append(text(ox + axw + 18, oy + 22, "час →", size=11, color=INK, anchor="end"))

    def block(x0, w, label, sub, fill, stroke, above=True):
        f = []
        h = 44
        y = oy - h - 6 if above else oy + 6
        f.append(rect(x0, y, w, h, fill=fill, stroke=stroke, sw=1.6, rx=5))
        fs = fit_font(label, w - 8, 11.5, bold=True)
        f.append(text(x0 + w/2, y + 19, label, size=fs, color=stroke, bold=True))
        if sub:
            f.append(text(x0 + w/2, y + 35, sub, size=9.5, color=MUTED))
        return f

    # старт: довге ZQCL
    frags += block(ox + 8, 150, "повне (довге)", "усе з нуля, багато тактів", "#eef2ff", NEG)
    frags.append(text(ox + 8 + 75, oy + 24, "старт / скидання", size=10.5, color=NEG))
    frags.append(line(ox + 8, oy - 6, ox + 8, oy + 6, color=NEG, sw=1.6))

    # звичайні звертання до шини
    for i, xf in enumerate([0.32, 0.44, 0.70, 0.82]):
        x = ox + axw * xf
        frags += block(x, 46, "доступ", "", "#f2f2f2", MUTED, above=True)
    frags.append(text(ox + axw * 0.55, oy - 70, "звичайні звертання до шини (читання/запис)",
                     size=10.5, color=MUTED))

    # короткі ZQCS у паузах між доступами
    for xf in [0.57, 0.94]:
        x = ox + axw * xf
        frags += block(x, 60, "коротке", "проти дрейфу", "#eafaf1", FIELD, above=False)
    frags.append(text(ox + axw * 0.75, oy + 78, "короткі поновлення — ТІЛЬКИ в паузах, коли шина вільна",
                     size=10.5, color=FIELD, bold=True))

    # застереження — не збігтися зі зверненням
    frags.append(fitbox(60, 250, 720, 60,
        "Момент запуску калібрування мусить лягти в паузу: поки триває ZQCS/ZQCL, шина «мовчить» —\n"
        "тиша й потрібна для точного заміру. Збіжиш калібрування зі звертанням — або зіпсуєш замір, або впустиш дані.",
        size=11, fill="#fdf2f2", stroke=POS))

    render(os.path.join(IMG, "zq-timing.svg"), W, H, *frags,
           title="Коли калібрувати: довге на старті, короткі поновлення в паузах шини")


if __name__ == "__main__":
    fig_loop()
    fig_write_level()
    fig_shmoo()
    fig_zq_block()
    fig_zq_sar()
    fig_zq_timing()
    print("OK: 6 SVG у", IMG)
