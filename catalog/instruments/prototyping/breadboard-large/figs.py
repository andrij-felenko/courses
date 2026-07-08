# -*- coding: utf-8 -*-
"""Фігури до статті «Макетна плата (велика)». Вивід — ./img/*.svg.
Запуск: python figs.py  (швидко, без залежностей)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

HOLE   = "#3a3f45"     # гніздо (темна крапка)
HOLE_R = 3.0           # радіус гнізда
RAIL_R = "#c0392b"     # шина «+»
RAIL_B = "#2457d6"     # шина «−»
STRIP  = "#eef1f4"     # підкладка смужки-вузла
STRIP_E = "#c9d2db"    # край смужки
BODY   = "#fbfbfa"     # корпус плати (біла пластмаса)


# ── Фігура 1: карта з'єднань плати на 830 (схема устрою) ───────────────────
def fig_internals():
    """Що з'єднано всередині: 4 шини живлення по краях, центральне поле
    зі стовпчиками по 5 гнізд (a-e / f-j), центральна канавка. Показуємо
    ЕЛЕКТРИЧНУ карту — які гнізда вже спаяні пружинкою в один вузол."""
    W, H = 900, 470
    p = []

    left = 70
    ncol = 20                    # показуємо 20 стовпчиків (реально 63) — досить для ідеї
    dx = (W - left - 40) / (ncol + 1)
    def cx(i): return left + dx * (i + 0.5)

    # ── верхня пара шин живлення ──────────────────────────────────────────
    def rail(y, color, sign):
        # довга підкладка-вузол уздовж усієї плати
        p.append(rect(left - 8, y - 10, W - left - 24, 20, fill=STRIP, stroke=STRIP_E, sw=1, rx=6))
        # кольорова лінія-маркер шини
        p.append(line(left - 2, y, W - 46, y, color=color, sw=2.6))
        for i in range(ncol):
            p.append(circle(cx(i), y, HOLE_R, fill=HOLE, stroke=None, sw=0))
        # знак на лівому полі
        if sign == "+":
            p.append(plus(left - 30, y, 9))
        else:
            p.append(minus(left - 30, y, 9))

    rail(70, RAIL_R, "+")
    rail(96, RAIL_B, "-")
    p.append(text(W/2, 44, "Верхня пара шин живлення — суцільний вузол уздовж усієї плати",
                  size=12.5, color=MUTED))

    # ── центральне поле: два блоки стовпчиків по 5, розділені канавкою ─────
    top_a = 160          # верх блоку a–e
    row_gap = 20
    # верхній блок: рядки a,b,c,d,e
    for r, lab in enumerate("abcde"):
        y = top_a + r * row_gap
        p.append(text(left - 34, y + 4, lab, size=12, color=MUTED))
    # нижній блок: рядки f,g,h,i,j
    top_f = top_a + 5 * row_gap + 46     # після канавки
    for r, lab in enumerate("fghij"):
        y = top_f + r * row_gap
        p.append(text(left - 34, y + 4, lab, size=12, color=MUTED))

    # вертикальні підкладки-стовпчики (кожен = один вузол), для верху й низу
    for i in range(ncol):
        x = cx(i)
        # верхній стовпчик a-e
        p.append(rect(x - 8, top_a - 10, 16, 5 * row_gap, fill=STRIP, stroke=STRIP_E, sw=1, rx=5))
        # нижній стовпчик f-j
        p.append(rect(x - 8, top_f - 10, 16, 5 * row_gap, fill=STRIP, stroke=STRIP_E, sw=1, rx=5))
        for r in range(5):
            p.append(circle(x, top_a + r * row_gap, HOLE_R, fill=HOLE, stroke=None, sw=0))
            p.append(circle(x, top_f + r * row_gap, HOLE_R, fill=HOLE, stroke=None, sw=0))

    # ── канавка посередині ────────────────────────────────────────────────
    groove_y = top_a + 5 * row_gap + 12
    p.append(rect(left - 8, groove_y - 6, W - left - 24, 20, fill="#e4e8ec", stroke=STRIP_E, sw=1, rx=4))
    p.append(text(W - 60, groove_y + 8, "канавка", size=11, color=MUTED, anchor="end"))

    # нумерація стовпчиків зверху (кожен 5-й, щоб не тісно)
    for i in range(0, ncol, 5):
        p.append(text(cx(i), top_a - 22, str(i + 1), size=10.5, color=MUTED))
    p.append(text(cx(ncol - 1) + dx, top_a - 22, "… 63", size=10.5, color=MUTED, anchor="start"))

    # ── виноски-пояснення (розставлені з запасом, поза гніздами) ──────────
    # 1) один стовпчик = вузол
    hix = cx(3)
    b, bw, bh = textbox(hix, top_f + 5 * row_gap + 44,
                        "5 гнізд одного стовпчика —\nодин вузол (спаяні пружинкою)",
                        size=11.5, pad=9, fill="#eaf7ef", stroke=FIELD, sw=2)
    p.append(b)
    p.append(line(hix, top_f + 5 * row_gap - 6, hix, top_f + 5 * row_gap + 44 - bh/2, color=FIELD, sw=1.6))

    # 2) канавка ділить верх і низ — стрілка від блоку a-e до f-j повз праворуч
    note_x = W - 120
    b2, bw2, bh2 = textbox(note_x, groove_y + 70,
                           "канавка розриває стовпчик:\nверх (a–e) і низ (f–j) —\nрізні вузли",
                           size=11, pad=9, fill="#f4f6f8", stroke=INK, sw=1.6)
    p.append(b2)

    render(os.path.join(OUT, 'internals.svg'), W, H, *p)


# ── Фігура 2: приклад розводки пін-у-пін (схема підключення) ───────────────
def fig_wiring():
    """Конкретний макет: живлення з плати МК на шини, DIP-чип верхи на канавці,
    світлодіод через резистор із ніжки МК на землю. Пін-у-пін, як воткнути."""
    W, H = 940, 520
    p = []

    left = 175
    ncol = 15
    dx = (W - left - 70) / (ncol + 1)
    def cx(i): return left + dx * (i + 0.5)
    row_gap = 22

    # шини живлення
    yplus, yminus = 66, 92
    p.append(rect(left - 8, yplus - 10, W - left - 44, 20, fill=STRIP, stroke=STRIP_E, sw=1, rx=6))
    p.append(line(left - 2, yplus, W - 66, yplus, color=RAIL_R, sw=2.6))
    p.append(rect(left - 8, yminus - 10, W - left - 44, 20, fill=STRIP, stroke=STRIP_E, sw=1, rx=6))
    p.append(line(left - 2, yminus, W - 66, yminus, color=RAIL_B, sw=2.6))
    for i in range(ncol):
        p.append(circle(cx(i), yplus, HOLE_R, fill=HOLE, stroke=None, sw=0))
        p.append(circle(cx(i), yminus, HOLE_R, fill=HOLE, stroke=None, sw=0))
    p.append(plus(left - 34, yplus, 9))
    p.append(minus(left - 34, yminus, 9))

    # центральне поле
    top_a = 150
    top_f = top_a + 5 * row_gap + 46
    groove_y = top_a + 5 * row_gap + 12
    for r, lab in enumerate("abcde"):
        p.append(text(left - 20, top_a + r * row_gap + 4, lab, size=11, color=MUTED))
    for r, lab in enumerate("fghij"):
        p.append(text(left - 20, top_f + r * row_gap + 4, lab, size=11, color=MUTED))
    for i in range(ncol):
        x = cx(i)
        p.append(rect(x - 8, top_a - 10, 16, 5 * row_gap, fill=STRIP, stroke=STRIP_E, sw=1, rx=5))
        p.append(rect(x - 8, top_f - 10, 16, 5 * row_gap, fill=STRIP, stroke=STRIP_E, sw=1, rx=5))
        for r in range(5):
            p.append(circle(x, top_a + r * row_gap, HOLE_R, fill=HOLE, stroke=None, sw=0))
            p.append(circle(x, top_f + r * row_gap, HOLE_R, fill=HOLE, stroke=None, sw=0))
    p.append(rect(left - 8, groove_y - 6, W - left - 44, 20, fill="#e4e8ec", stroke=STRIP_E, sw=1, rx=4))

    def hole(i, row):
        """Координати гнізда: row у 'abcdefghij'."""
        if row in "abcde":
            r = "abcde".index(row); return cx(i), top_a + r * row_gap
        r = "fghij".index(row); return cx(i), top_f + r * row_gap

    # ── DIP-чип верхи на канавці: стовпці 4..7, ніжки в рядах e та f ───────
    c0, c1 = 4, 7
    chx0, chx1 = cx(c0), cx(c1)
    p.append(rect(chx0 - 10, hole(c0, 'e')[1] + 6, (chx1 - chx0) + 20,
                  (hole(c0, 'f')[1] - hole(c0, 'e')[1]) - 12,
                  fill="#2b2f34", stroke="#15171a", sw=1.4, rx=4))
    # ніжки чипа (умовно) — короткі метал-риски від корпусу в гнізда e/f
    for i in range(c0, c1 + 1):
        p.append(line(cx(i), hole(i, 'e')[1] + 6, cx(i), hole(i, 'e')[1], color="#9aa3ad", sw=2.4))
        p.append(line(cx(i), hole(i, 'f')[1] - 6, cx(i), hole(i, 'f')[1], color="#9aa3ad", sw=2.4))
    p.append(text((chx0 + chx1) / 2, (hole(c0,'e')[1] + hole(c0,'f')[1]) / 2 + 4,
                  "DIP", size=11, color="#eef1f4"))
    # виноска до чипа
    b, bw, bh = textbox((chx0 + chx1) / 2, hole(c0, 'e')[1] - 66,
                        "DIP-чип верхи на канавці:\nліві ніжки й праві — різні вузли",
                        size=11, pad=8, fill="#f4f6f8", stroke=INK, sw=1.5)
    p.append(b)
    p.append(line((chx0+chx1)/2, hole(c0,'e')[1] - 66 + bh/2, (chx0+chx1)/2, hole(c0,'e')[1] + 4,
                  color=INK, sw=1.2, dash="4 3"))

    # ── МК зліва: блок із заголовком угорі та трьома виводами на правому краї ──
    blk_x, blk_w = 30, 92
    blk_y, blk_h = top_a + 8, 3.4 * row_gap
    p.append(rect(blk_x, blk_y, blk_w, blk_h, fill="#33404d", stroke="#1c242c", sw=1.6, rx=6))
    # заголовок «МК» — над блоком, у чистій зоні (не на пінах)
    p.append(text(blk_x + blk_w/2, blk_y - 10, "МК", size=14, color=INK, bold=True))
    # три виводи на ПРАВОМУ краї блоку, добре рознесені по вертикалі
    pin_edge = blk_x + blk_w
    py_3v3 = blk_y + 0.5 * row_gap
    py_gnd = blk_y + 1.7 * row_gap
    py_io  = blk_y + 2.9 * row_gap
    pin_3v3 = (pin_edge, py_3v3)
    pin_gnd = (pin_edge, py_gnd)
    pin_io  = (pin_edge, py_io)
    # мітки виводів — усередині блоку, притиснуті до правого краю (anchor=end)
    p.append(text(pin_edge - 6, py_3v3 + 4, "3V3", size=10, color="#ff9c8f", anchor="end"))
    p.append(text(pin_edge - 6, py_gnd + 4, "GND", size=10, color="#8fbaff", anchor="end"))
    p.append(text(pin_edge - 6, py_io + 4,  "IO",  size=10, color="#ffcf7a", anchor="end"))

    # перемички МК → ціль. Кожна має власну вертикальну смугу у лівому «жолобі»
    # (між блоком і полем), щоб дроти не лягали на мітки виводів.
    def wirepath(x1, y1, x2, y2, color, lane):
        p.append(line(x1, y1, lane, y1, color=color, sw=2.6))
        p.append(line(lane, y1, lane, y2, color=color, sw=2.6))
        p.append(line(lane, y2, x2, y2, color=color, sw=2.6))
        p.append(circle(x2, y2, HOLE_R + 1.4, fill="none", stroke=color, sw=2))

    # 3V3 → шина «+» (жолоб-смуга x=138)
    wirepath(pin_3v3[0], pin_3v3[1], cx(0), yplus, RAIL_R, 138)
    # GND → шина «−» (жолоб-смуга x=150)
    wirepath(pin_gnd[0], pin_gnd[1], cx(1), yminus, RAIL_B, 150)
    # IO → стовпчик 8, ряд a: у власну смугу вгору, тоді понад полем управо
    io_col = 8
    ix, iy = hole(io_col, 'a')
    p.append(line(pin_io[0], pin_io[1], 162, pin_io[1], color="#e0a640", sw=2.6))
    p.append(line(162, pin_io[1], 162, top_a - 32, color="#e0a640", sw=2.6))
    p.append(line(162, top_a - 32, ix, top_a - 32, color="#e0a640", sw=2.6))
    p.append(line(ix, top_a - 32, ix, iy, color="#e0a640", sw=2.6))
    p.append(circle(ix, iy, HOLE_R + 1.4, fill="none", stroke="#e0a640", sw=2))

    # ── ланцюг світлодіода: IO(стовп.9) → R → стовп.11 → LED → стовп.11(низ) →
    #    перемичка на шину «−». Усе в горизонталь по ряду c верхнього блоку, LED
    #    і його перемичка — праворуч, у широкій порожнечі. Підписи — у чистих зонах.

    # резистор лежить по ряду c між стовпчиком 9 і стовпчиком 11 (обидва верхній блок)
    rcol0, rcol1 = 9, 11
    rx0, ry = hole(rcol0, 'c')
    rx1, _  = hole(rcol1, 'c')
    p.append(line(rx0, ry, (rx0+rx1)/2 - 20, ry, color="#7a7a7a", sw=2))
    p.append(line((rx0+rx1)/2 + 20, ry, rx1, ry, color="#7a7a7a", sw=2))
    p.append(rect((rx0 + rx1)/2 - 20, ry - 7, 40, 14, fill="#d8c9a0", stroke="#9c8b5a", sw=1.4, rx=4))
    # напис резистора — праворуч над полем, у чистій зоні (не над дротами)
    p.append(text(rx1 + 8, top_a - 30, "R 330 Ω", size=11, color=INK, anchor="start"))

    # світлодіод: анод у стовпчик 11 (ряд e, низ верхнього блоку), катод — на шину «−»
    lax, lay = hole(rcol1, 'e')            # анод LED тут
    # ведемо анодний вивід від гнізда e стовпчика 11 донизу-вправо у порожнечу
    lx = cx(rcol1) + 44
    ly = groove_y + 6
    p.append(line(lax, lay, lax, lay + 16, color="#7a7a7a", sw=2))
    p.append(line(lax, lay + 16, lx, ly, color="#7a7a7a", sw=2))
    # тіло світлодіода (кружечок) у чистій зоні праворуч від канавки
    p.append(circle(lx, ly, 9, fill="#ffe08a", stroke="#c99a1a", sw=1.8))
    p.append(text(lx + 14, ly + 4, "LED", size=11, color=INK, anchor="start"))
    # катод LED → шина «−» (короткий синій дріт праворуч-угору до шини)
    p.append(line(lx, ly - 9, lx, yminus + 12, color=RAIL_B, sw=2.4))
    p.append(line(lx, yminus + 12, cx(ncol - 1), yminus + 12, color=RAIL_B, sw=2.4))
    p.append(line(cx(ncol - 1), yminus + 12, cx(ncol - 1), yminus, color=RAIL_B, sw=2.4))
    p.append(circle(cx(ncol - 1), yminus, HOLE_R + 1.4, fill="none", stroke=RAIL_B, sw=2))

    # підпис-нитка ланцюга — унизу ліворуч, у чистій зоні під полем
    b2, bw2, bh2 = textbox(230, H - 54,
                           "Ланцюг: IO → резистор 330 Ω →\nсвітлодіод → шина «−».\n3V3 і GND — на шини живлення.",
                           size=11, pad=9, fill="#eaf7ef", stroke=FIELD, sw=1.8)
    p.append(b2)

    render(os.path.join(OUT, 'wiring.svg'), W, H, *p)


# ── Фігура 3: розводка «кнопка → світлодіод» із внутрішньою підтяжкою ───────
def fig_blink_wiring():
    """До вставки proj-blink-wiring. Показуємо ДВА ланцюги на тій самій платі:
    (1) ВХІД — кнопка з ніжки IN у стовпчик поля, друга нога кнопки на шину «−»;
        усередині МК намальовано внутрішню підтяжку до «+» (INPUT_PULLUP).
    (2) ВИХІД — ніжка OUT → резистор → світлодіод → шина «−».
    Ключова думка фігури: підтяжка живе ВСЕРЕДИНІ МК, тож кнопці досить
    замикати вхід на землю; відпущена кнопка лишає на вході тверду 1."""
    W, H = 960, 560
    p = []

    left = 250
    ncol = 12
    dx = (W - left - 80) / (ncol + 1)
    def cx(i): return left + dx * (i + 0.5)
    row_gap = 22

    # ── шини живлення ─────────────────────────────────────────────────────
    yplus, yminus = 66, 92
    p.append(rect(left - 8, yplus - 10, W - left - 54, 20, fill=STRIP, stroke=STRIP_E, sw=1, rx=6))
    p.append(line(left - 2, yplus, W - 76, yplus, color=RAIL_R, sw=2.6))
    p.append(rect(left - 8, yminus - 10, W - left - 54, 20, fill=STRIP, stroke=STRIP_E, sw=1, rx=6))
    p.append(line(left - 2, yminus, W - 76, yminus, color=RAIL_B, sw=2.6))
    for i in range(ncol):
        p.append(circle(cx(i), yplus, HOLE_R, fill=HOLE, stroke=None, sw=0))
        p.append(circle(cx(i), yminus, HOLE_R, fill=HOLE, stroke=None, sw=0))
    p.append(plus(left - 34, yplus, 9))
    p.append(minus(left - 34, yminus, 9))

    # ── центральне поле ───────────────────────────────────────────────────
    top_a = 190
    top_f = top_a + 5 * row_gap + 46
    groove_y = top_a + 5 * row_gap + 12
    for r, lab in enumerate("abcde"):
        p.append(text(left - 20, top_a + r * row_gap + 4, lab, size=11, color=MUTED))
    for r, lab in enumerate("fghij"):
        p.append(text(left - 20, top_f + r * row_gap + 4, lab, size=11, color=MUTED))
    for i in range(ncol):
        x = cx(i)
        p.append(rect(x - 8, top_a - 10, 16, 5 * row_gap, fill=STRIP, stroke=STRIP_E, sw=1, rx=5))
        p.append(rect(x - 8, top_f - 10, 16, 5 * row_gap, fill=STRIP, stroke=STRIP_E, sw=1, rx=5))
        for r in range(5):
            p.append(circle(x, top_a + r * row_gap, HOLE_R, fill=HOLE, stroke=None, sw=0))
            p.append(circle(x, top_f + r * row_gap, HOLE_R, fill=HOLE, stroke=None, sw=0))
    p.append(rect(left - 8, groove_y - 6, W - left - 54, 20, fill="#e4e8ec", stroke=STRIP_E, sw=1, rx=4))

    def hole(i, row):
        if row in "abcde":
            r = "abcde".index(row); return cx(i), top_a + r * row_gap
        r = "fghij".index(row); return cx(i), top_f + r * row_gap

    # ── МК зліва: блок із заголовком, трьома виводами й внутрішньою підтяжкою ──
    blk_x, blk_w = 34, 150
    blk_y, blk_h = top_a - 6, 4.6 * row_gap
    p.append(rect(blk_x, blk_y, blk_w, blk_h, fill="#33404d", stroke="#1c242c", sw=1.6, rx=6))
    p.append(text(blk_x + blk_w/2, blk_y - 12, "Мікроконтролер", size=13, color=INK, bold=True))

    pin_edge = blk_x + blk_w
    py_out = blk_y + 0.7 * row_gap
    py_gnd = blk_y + 2.0 * row_gap
    py_in  = blk_y + 3.6 * row_gap
    # мітки виводів — ПІД лінією виводу (нижче на 15px), притиснуті до правого краю,
    # щоб горизонтальні дроти, які виходять із пінів, не лягали на написи
    p.append(text(pin_edge - 10, py_out + 16, "OUT", size=10, color="#ffcf7a", anchor="end"))
    p.append(text(pin_edge - 10, py_gnd + 16, "GND", size=10, color="#8fbaff", anchor="end"))
    p.append(text(pin_edge - 10, py_in + 16,  "IN",  size=10, color="#9ff0c0", anchor="end"))
    # маленькі вузли-піни на правому краю блоку
    for py in (py_out, py_gnd, py_in):
        p.append(circle(pin_edge, py, 2.4, fill="#dfe6ee", stroke="#1c242c", sw=1))

    # внутрішня підтяжка: зигзаг від внутрішньої «+»-рейки МК до вузла піна IN
    railx = blk_x + 26
    p.append(line(railx, blk_y + 8, railx, py_in, color="#ff9c8f", sw=1.6))
    p.append(text(railx, blk_y + 4, "+", size=12, color="#ff9c8f", bold=True))
    # символ резистора-зигзага (підтяжка) на короткому відрізку
    zx0, zx1 = railx + 6, pin_edge - 30
    zy = py_in
    seg = (zx1 - zx0) / 6
    zig = "M %.1f %.1f" % (zx0, zy)
    for k in range(1, 7):
        yy = zy + (7 if k % 2 else -7)
        if k == 6: yy = zy
        zig += " L %.1f %.1f" % (zx0 + seg * k, yy)
    p.append('<path d="%s" fill="none" stroke="#ff9c8f" stroke-width="1.6"/>' % zig)
    p.append(line(zx1, zy, pin_edge, py_in, color="#9ff0c0", sw=1.6))
    # виноска про підтяжку — над блоком МК, у чистій зоні
    bpull, wpull, hpull = textbox(blk_x + blk_w/2 + 18, blk_y + blk_h + 44,
                        "Підтяжка ~20…50 кОм —\nусередині МК (INPUT_PULLUP):\nвідпущена кнопка → на IN твердий «1»",
                        size=10.5, pad=8, fill="#fff4ec", stroke="#e0a640", sw=1.6)
    p.append(bpull)

    # ── ВХІД: кнопка. IN → стовпчик 3 (ряд a). Кнопка замикає стовпч.3 і стовпч.5.
    #    Зі стовпчика 5 перемичка на шину «−». Натиск → IN сідає на землю. ──
    in_col = 3
    ixp, iyp = hole(in_col, 'a')
    # дріт IN → стовпчик 3
    lane_in = blk_x + blk_w + 18
    p.append(line(pin_edge, py_in, lane_in, py_in, color="#3fbf82", sw=2.6))
    p.append(line(lane_in, py_in, lane_in, top_a - 40, color="#3fbf82", sw=2.6))
    p.append(line(lane_in, top_a - 40, ixp, top_a - 40, color="#3fbf82", sw=2.6))
    p.append(line(ixp, top_a - 40, ixp, iyp, color="#3fbf82", sw=2.6))
    p.append(circle(ixp, iyp, HOLE_R + 1.4, fill="none", stroke="#3fbf82", sw=2))

    # тіло кнопки: корпус, що сідає у стовпчики 3 і 5 (перекриває канавку по x)
    bcol0, bcol1 = 3, 5
    bx0, bx1 = cx(bcol0), cx(bcol1)
    by = (top_a + top_f) / 2      # верхи на канавці
    p.append(rect(bx0 - 12, by - 20, (bx1 - bx0) + 24, 40, fill="#3a3f45", stroke="#15171a", sw=1.5, rx=5))
    p.append(circle((bx0+bx1)/2, by, 8, fill="#8a929c", stroke="#5a616b", sw=1.6))
    # ноги кнопки у стовпчики 3 і 5 (ряд e — верхній блок)
    for c in (bcol0, bcol1):
        hx, _ = hole(c, 'e')
        p.append(line(hx, by - 20, hx, hole(c, 'e')[1], color="#9aa3ad", sw=2.4))
        p.append(circle(hx, hole(c, 'e')[1], HOLE_R + 1.4, fill="none", stroke="#9aa3ad", sw=1.8))
    p.append(text((bx0+bx1)/2, by - 26, "кнопка", size=11, color=INK, bold=True))

    # перемичка: стовпчик 5 (ряд a) → шина «−»
    jx, jy = hole(bcol1, 'a')
    p.append(line(jx, jy, jx, yminus + 14, color=RAIL_B, sw=2.4))
    p.append(line(jx, yminus + 14, jx, yminus, color=RAIL_B, sw=2.4))
    p.append(circle(jx, yminus, HOLE_R + 1.4, fill="none", stroke=RAIL_B, sw=2))
    p.append(circle(jx, jy, HOLE_R + 1.4, fill="none", stroke=RAIL_B, sw=2))

    # ── ВИХІД: OUT → стовпчик 8 → резистор → стовпчик 10 → LED → шина «−» ──
    out_col = 8
    oxp, oyp = hole(out_col, 'a')
    lane_out = blk_x + blk_w + 8
    p.append(line(pin_edge, py_out, lane_out, py_out, color="#e0a640", sw=2.6))
    p.append(line(lane_out, py_out, lane_out, top_a - 58, color="#e0a640", sw=2.6))
    p.append(line(lane_out, top_a - 58, oxp, top_a - 58, color="#e0a640", sw=2.6))
    p.append(line(oxp, top_a - 58, oxp, oyp, color="#e0a640", sw=2.6))
    p.append(circle(oxp, oyp, HOLE_R + 1.4, fill="none", stroke="#e0a640", sw=2))

    # GND виводу МК → шина «−»: вправо у чистій зоні над полем, тоді ВНИЗ на
    # гніздо шини у стовпчику 0 (не вздовж рейки — щоб не різати «−»-маркер)
    gnd_dx = cx(0)
    p.append(line(pin_edge, py_gnd, gnd_dx, py_gnd, color=RAIL_B, sw=2.4))
    p.append(line(gnd_dx, py_gnd, gnd_dx, yminus, color=RAIL_B, sw=2.4))
    p.append(circle(gnd_dx, yminus, HOLE_R + 1.4, fill="none", stroke=RAIL_B, sw=2))

    # резистор по ряду c між стовпчиками 8 і 10
    rcol0, rcol1 = 8, 10
    rx0, ry = hole(rcol0, 'c')
    rx1, _  = hole(rcol1, 'c')
    p.append(line(rx0, ry, (rx0+rx1)/2 - 20, ry, color="#7a7a7a", sw=2))
    p.append(line((rx0+rx1)/2 + 20, ry, rx1, ry, color="#7a7a7a", sw=2))
    p.append(rect((rx0 + rx1)/2 - 20, ry - 7, 40, 14, fill="#d8c9a0", stroke="#9c8b5a", sw=1.4, rx=4))
    p.append(text((rx0+rx1)/2, top_a - 40, "R 330 Ω", size=11, color=INK))

    # світлодіод: анод у стовпчик 10 (ряд e), катод на шину «−»
    lax, lay = hole(rcol1, 'e')
    lx = cx(rcol1) + 46
    ly = groove_y + 6
    p.append(line(lax, lay, lax, lay + 16, color="#7a7a7a", sw=2))
    p.append(line(lax, lay + 16, lx, ly, color="#7a7a7a", sw=2))
    p.append(circle(lx, ly, 9, fill="#ffe08a", stroke="#c99a1a", sw=1.8))
    p.append(text(lx + 14, ly + 4, "LED", size=11, color=INK, anchor="start"))
    p.append(line(lx, ly - 9, lx, yminus + 12, color=RAIL_B, sw=2.4))
    p.append(line(lx, yminus + 12, cx(ncol - 1), yminus + 12, color=RAIL_B, sw=2.4))
    p.append(line(cx(ncol - 1), yminus + 12, cx(ncol - 1), yminus, color=RAIL_B, sw=2.4))
    p.append(circle(cx(ncol - 1), yminus, HOLE_R + 1.4, fill="none", stroke=RAIL_B, sw=2))

    # ── два підписи-нитки: вхід і вихід ───────────────────────────────────
    bi, wi, hi = textbox(cx(bcol1) + 6, H - 96,
                    "ВХІД: кнопка замикає IN на «−».\nВідпущена — підтяжка тримає «1»,\nнатиснута — читаємо «0».",
                    size=10.5, pad=9, fill="#eaf7ef", stroke=FIELD, sw=1.8)
    p.append(bi)
    bo, wo, ho = textbox(cx(rcol1) + 60, H - 96,
                    "ВИХІД: OUT → 330 Ω →\nсвітлодіод → «−».\nПеремикаємо OUT — LED блимає.",
                    size=10.5, pad=9, fill="#fdf3e7", stroke="#c99a1a", sw=1.8)
    p.append(bo)

    render(os.path.join(OUT, 'blink-wiring.svg'), W, H, *p)


# ── Фігура (історія): «тоді vs нині» — дерев'яна дошка з цвяхами → пластмаса ──
def fig_then_now():
    """До вставки hist-breadboard-name. Дві панелі поряд.
    ЛІВОРУЧ: дерев'яна хлібна дошка 1920-х — лампова панелька прибита цвяхами,
    резистор на цвяхах-стовпчиках, обкручені дроти, відрізок мідної шини.
    ПРАВОРУЧ: сучасна безпаяльна плата — біла пластмаса, ряди гнізд, DIP-чип
    верхи на канавці. Показуємо ФІЗИЧНУ еволюцію, про яку йдеться в тексті."""
    import math
    W, H = 900, 440
    p = []

    pw = 372                      # ширина панелі
    gap = 44
    lx0 = 40                      # лівий край лівої панелі
    rx0 = lx0 + pw + gap          # лівий край правої панелі
    top = 80
    ph = 262                      # висота панелі

    # заголовки панелей (над рамками, у чистій зоні)
    p.append(text(lx0 + pw/2, 44, "1910–1930-ті: дошка з цвяхами", size=14.5, bold=True))
    p.append(text(rx0 + pw/2, 44, "від 1971-го: пружинна пластмаса", size=14.5, bold=True))

    # ── ЛІВА панель: дерев'яна дошка ─────────────────────────────────────────
    WOOD  = "#c9a36a"
    WOOD_E = "#9c7b45"
    GRAIN = "#b98f52"
    NAIL  = "#7a7a7a"
    p.append(rect(lx0, top, pw, ph, fill=WOOD, stroke=WOOD_E, sw=2, rx=8))
    # волокна дерева — рідкі горизонтальні штрихи
    for k in range(5):
        gy = top + 40 + k * 46
        p.append(line(lx0 + 18, gy, lx0 + pw - 18, gy, color=GRAIN, sw=1.2))

    # лампова панелька (октальний сокет), прибита двома цвяхами
    sx, sy = lx0 + 92, top + 92
    p.append(circle(sx, sy, 32, fill="#2e2e2e", stroke="#111", sw=2))
    p.append(circle(sx, sy, 18, fill="#3a3a3a", stroke="#111", sw=1.2))
    for a in range(8):            # вісім контактів сокета
        ang = a * (2*math.pi/8)
        p.append(circle(sx + 24*math.cos(ang), sy + 24*math.sin(ang), 2.4,
                        fill="#c9c9c9", stroke=None, sw=0))
    # два цвяхи, якими сокет прибитий до дошки
    p.append(circle(sx - 28, sy - 28, 3.2, fill=NAIL, stroke="#555", sw=1))
    p.append(circle(sx + 28, sy + 28, 3.2, fill=NAIL, stroke="#555", sw=1))
    p.append(text(sx, sy + 52, "лампова панелька", size=11, color="#3d2f16"))

    # ряд цвяхів-стовпчиків праворуч + резистор із обкрученими дротами
    nail_xs = [lx0 + 208, lx0 + 250, lx0 + 300, lx0 + 342]
    ny = top + 66
    for nx in nail_xs:
        p.append(circle(nx, ny, 3.4, fill=NAIL, stroke="#555", sw=1))          # капелюшок цвяха
        p.append(circle(nx, ny + 96, 3.4, fill=NAIL, stroke="#555", sw=1))
    # резистор між двома цвяхами (тіло + обкручені виводи)
    rlx, rrx = nail_xs[0], nail_xs[1]
    p.append(line(rlx, ny, rlx, ny + 22, color="#4a4a4a", sw=1.8))
    p.append(rect(rlx - 6, ny + 22, (rrx - rlx) + 12, 12, fill="#d8c08a", stroke="#8a6b2e", sw=1.2, rx=3))
    p.append(line(rrx, ny + 28, rrx, ny + 96, color="#4a4a4a", sw=1.8))
    # відрізок мідної шини — товстий дріт, прибитий цвяхами
    busy = ny + 96
    p.append(line(nail_xs[0], busy, nail_xs[-1], busy, color="#b5651d", sw=3.4))
    p.append(text((nail_xs[0]+nail_xs[-1])/2, busy + 22, "виводи обкручені й припаяні",
                  size=10.5, color="#3d2f16"))
    p.append(text(lx0 + pw/2, top + ph - 14, "дірки свердлиш сам · нічого не з'єднано наперед",
                  size=11, color="#3d2f16"))

    # ── ПРАВА панель: сучасна безпаяльна плата ───────────────────────────────
    p.append(rect(rx0, top, pw, ph, fill=BODY, stroke=STRIP_E, sw=2, rx=8))
    # дві шини живлення згори
    p.append(line(rx0 + 22, top + 24, rx0 + pw - 22, top + 24, color=RAIL_R, sw=2.4))
    p.append(line(rx0 + 22, top + 36, rx0 + pw - 22, top + 36, color=RAIL_B, sw=2.4))
    # сітка гнізд: 12 стовпчиків × (5 + канавка + 5)
    gcols = 12
    gx0 = rx0 + 44
    gdx = (pw - 88) / (gcols - 1)
    rows_top = [top + 64 + i*15 for i in range(5)]     # a–e
    groove = rows_top[-1] + 26
    rows_bot = [groove + 16 + i*15 for i in range(5)]  # f–j
    for c in range(gcols):
        gx = gx0 + c*gdx
        for gy in rows_top + rows_bot:
            p.append(circle(gx, gy, 2.6, fill=HOLE, stroke=None, sw=0))
    # канавка
    p.append(line(rx0 + 32, groove, rx0 + pw - 32, groove, color=STRIP_E, sw=6))
    # DIP-чип верхи на канавці (чорний прямокутник з ніжками в e/f)
    cx1 = gx0 + 3*gdx
    cx2 = gx0 + 6*gdx
    p.append(rect(cx1 - 6, groove - 12, (cx2 - cx1) + 12, 24, fill="#2b2b2b", stroke="#111", sw=1.4, rx=3))
    p.append(text((cx1+cx2)/2, groove + 3, "DIP", size=9, color="#eaeaea"))
    p.append(text(rx0 + pw/2, top + ph - 14, "крок 0.1″ під ніжки DIP · частина гнізд з'єднана наперед",
                  size=11, color=MUTED))

    # ── стрілка еволюції між панелями ────────────────────────────────────────
    ay = top + ph/2
    p.append(arrow(lx0 + pw + 8, ay, rx0 - 8, ay, color=INK, sw=2.2))

    # нижній підпис-нитка — що збереглося
    b, bw, bh = textbox(W/2, H - 26,
                        "Дошки не стало — лишилася назва «breadboard» і сама ідея: чернетка схеми, яку легко переробити.",
                        size=11.5, pad=9, fill="#f4f6f8", stroke=MUTED, sw=1.4)
    p.append(b)

    render(os.path.join(OUT, 'then-now.svg'), W, H, *p)


if __name__ == '__main__':
    fig_internals()
    fig_wiring()
    fig_blink_wiring()
    fig_then_now()
    print("OK: internals.svg, wiring.svg, blink-wiring.svg, then-now.svg")
