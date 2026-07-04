# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «Поворотний потенціометр».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

WIPER = "#c0392b"   # повзунок
TRACK = "#8a5a5a"   # доріжка опору
KNOB  = "#3b4048"   # вал/ручка


# ── 1. Що всередині: підкова опору + повзунок = три виводи, дільник напруги ───
def fig_inside():
    W, H = 940, 560
    f = [text(W / 2, 30, "Усередині: підкова опору з двома кінцями + повзунок на валу = три виводи",
              size=15, bold=True)]

    # --- ліворуч: сам механізм (вид зверху) ---
    cx, cy = 250, 268
    f.append(rect(cx - 165, cy - 175, 330, 330, fill="#fafbfc", stroke=MUTED, sw=1.6, rx=12))
    f.append(text(cx, cy - 190, "механізм (вид зверху)", size=11.5, bold=True, color=MUTED))

    # підкова опору — незамкнене кільце (дуга ~300°), кінці = виводи 1 і 3
    R = 118
    a0, a1 = 130, 130 + 280        # дуга від 130° за годинниковою на 280°
    def polar(a, r=R):
        t = math.radians(a)
        return cx + r * math.cos(t), cy - r * math.sin(t)
    x0, y0 = polar(a0)
    x1, y1 = polar(a1)
    large = 1 if (a1 - a0) > 180 else 0
    f.append('<path d="M %.1f %.1f A %.1f %.1f 0 %d 0 %.1f %.1f" '
             'fill="none" stroke="%s" stroke-width="13" stroke-linecap="round"/>'
             % (x0, y0, R, R, large, x1, y1, TRACK))

    # кінці доріжки — виводи 1 і 3 (на + і −); підписи винесено РАДІАЛЬНО назовні,
    # у порожнє поле, щоб їх не чіпала лапка повзунка
    f.append(circle(x0, y0, 8, fill="#fdecea", stroke=POS, sw=2))
    l1x, l1y = polar(a0, R + 34)
    f.append(text(l1x - 4, l1y + 4, "вивід 1", size=10.5, bold=True, color=POS, anchor="end"))
    f.append(circle(x1, y1, 8, fill="#eaf0fd", stroke=NEG, sw=2))
    l3x, l3y = polar(a1, R + 34)
    f.append(text(l3x + 4, l3y + 4, "вивід 3", size=10.5, bold=True, color=NEG, anchor="start"))

    # вал у центрі + рухома лапка-повзунок; напрямок повзунка — УНИЗ (у розрив підкови),
    # де немає підписів, щоб лапка й відведення нікого не перетинали
    aw = 270                       # поточний кут повзунка (вниз, у розрив дуги)
    wx, wy = polar(aw, R)
    f.append(circle(cx, cy, 26, fill=KNOB, stroke=INK, sw=1.6))       # вал
    f.append(circle(cx, cy, 7, fill="#5b616b", stroke=INK, sw=1))     # шліц
    f.append(line(cx, cy, wx, wy, color=WIPER, sw=4))                 # лапка повзунка
    f.append(circle(wx, wy, 6, fill=WIPER, stroke=INK, sw=1.4))       # точка контакту
    # відведення повзунка — це вивід 2 (донизу)
    lx, ly = polar(aw, R + 40)
    f.append(line(wx, wy, lx, ly, color=WIPER, sw=2))
    f.append(circle(lx, ly, 8, fill="#fdecea", stroke=WIPER, sw=2))
    f.append(text(lx, ly + 22, "вивід 2 (повзунок)", size=10.5, bold=True, color=WIPER, anchor="middle"))

    # підпис обертання — у верхньому вільному секторі (розрив підкови вгорі)
    f.append(text(cx, cy - 96, "крутиш вал →", size=10.5, color=MUTED))
    f.append(text(cx, cy - 80, "повзунок їде доріжкою", size=10.5, color=MUTED))

    # --- праворуч: та сама річ як електрична схема — дільник напруги ---
    px = 680
    top, bot = 96, 430
    f.append(text(px, 74, "те саме як схема: дільник напруги", size=12, bold=True, color=MUTED))
    # смужка опору вертикально, кінці на + і −
    f.append(rect(px - 14, top, 28, bot - top, fill="#f0e6e6", stroke=TRACK, sw=1.8, rx=7))
    # підпис повного опору — ЛІВОРУЧ від смужки (не над вертикальним + стеблом)
    f.append(text(px - 26, top + 44, "повний опір R", size=10, color=MUTED, anchor="end"))
    f.append(text(px - 26, top + 60, "(напр. 10 кОм)", size=10, color=MUTED, anchor="end"))
    # верхній кінець = +, нижній = −
    f.append(line(px, top, px, top - 26, color=POS, sw=2.4))
    f.append(plus(px, top - 40, 11))
    f.append(text(px + 22, top - 36, "вивід 1 → +", size=10.5, bold=True, color=POS, anchor="start"))
    f.append(line(px, bot, px, bot + 26, color=NEG, sw=2.4))
    f.append(minus(px, bot + 40, 11))
    f.append(text(px + 22, bot + 44, "вивід 3 → −", size=10.5, bold=True, color=NEG, anchor="start"))

    # повзунок ~60% зверху → стрілка вбік = вихідна напруга
    frac = 0.38                    # частка зверху (ближче до +)
    wy2 = top + (bot - top) * frac
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" stroke="%s" stroke-width="1.4"/>'
             % (px - 14, wy2, px - 40, wy2 - 12, px - 40, wy2 + 12, WIPER, INK))
    f.append(line(px - 40, wy2, px - 96, wy2, color=WIPER, sw=2.4))
    f.append(rect(px - 96 - 108, wy2 - 18, 108, 36, fill="#fdecea", stroke=WIPER, sw=1.7, rx=5))
    f.append(text(px - 96 - 54, wy2 - 3, "вивід 2", size=11, bold=True, color=WIPER))
    f.append(text(px - 96 - 54, wy2 + 13, "Uвих", size=11, bold=True, color=WIPER))
    # позначки: скільки опору зверху/знизу від повзунка
    f.append(mtext(px + 22, (top + wy2) / 2, ["опір зверху", "(до +)"], size=9.5, color="#7a4040", anchor="start"))
    f.append(mtext(px + 22, (wy2 + bot) / 2, ["опір знизу", "(до −)"], size=9.5, color="#7a4040", anchor="start"))

    b, _, _ = textbox(W / 2, 528,
                      "Повзунок ділить доріжку на дві частини: скільки опору лишилось до «+» і скільки до «−». "
                      "Вивід 2 віддає напругу\nрівно за цим поділом — от і весь потенціометр. Крутнув до «+» "
                      "кінця — Uвих ≈ живлення; до «−» — ≈ 0; посередині — ≈ половина.",
                      size=10.5, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "inside.svg"), W, H, *f)


# ── 2. Лінійний проти логарифмічного профілю (крива «кут → частка опору») ──────
def fig_taper():
    W, H = 900, 540
    f = [text(W / 2, 30, "Профіль (taper): як частка опору росте з кутом — лінійний «B» проти лог «A»",
              size=14.5, bold=True)]

    # осі графіка
    gx0, gy0 = 130, 96             # лівий-верхній кут поля
    gw, gh = 560, 340
    gx1, gy1 = gx0 + gw, gy0 + gh  # правий-нижній
    f.append(rect(gx0, gy0, gw, gh, fill="#fcfcfd", stroke=MUTED, sw=1.5, rx=6))
    # осі
    f.append(line(gx0, gy1, gx1, gy1, color=INK, sw=1.8))   # X (кут)
    f.append(line(gx0, gy0, gx0, gy1, color=INK, sw=1.8))   # Y (частка)
    f.append(text(gx0 + gw / 2, gy1 + 40, "кут повороту вала  (0 → до кінця)", size=11, bold=True))
    f.append(text(gx0 - 44, gy0 + gh / 2, "частка", size=11, bold=True, anchor="middle"))
    f.append(text(gx0 - 44, gy0 + gh / 2 + 16, "опору", size=11, bold=True, anchor="middle"))
    # мітки 0 і кінець
    f.append(text(gx0, gy1 + 18, "0", size=10, color=MUTED))
    f.append(text(gx1, gy1 + 18, "кінець", size=10, color=MUTED, anchor="middle"))
    f.append(text(gx0 - 12, gy1 + 4, "0", size=10, color=MUTED, anchor="end"))
    f.append(text(gx0 - 12, gy0 + 4, "1", size=10, color=MUTED, anchor="end"))
    # середина осі X — половина ходу
    f.append(line(gx0 + gw / 2, gy1, gx0 + gw / 2, gy1 + 6, color=MUTED, sw=1.2))
    f.append(text(gx0 + gw / 2, gy1 + 18, "½ ходу", size=10, color=MUTED, anchor="middle"))

    def curve(fn, col, sw=2.6):
        pts = []
        N = 60
        for i in range(N + 1):
            t = i / N
            v = fn(t)
            X = gx0 + t * gw
            Y = gy1 - v * gh
            pts.append("%.1f,%.1f" % (X, Y))
        return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (" ".join(pts), col, sw)

    # лінійний B: пряма
    f.append(curve(lambda t: t, NEG))
    # логарифмічний-audio A: повільно спершу, круто в кінці (типова «аудіо» крива)
    f.append(curve(lambda t: (math.pow(10, 2 * t) - 1) / 99.0, WIPER))

    # позначка на ½ ходу: де опиняється кожна крива
    midx = gx0 + gw / 2
    # B на ½ = 0.5
    f.append(circle(midx, gy1 - 0.5 * gh, 4, fill=NEG, stroke=INK, sw=1))
    f.append(text(midx + 10, gy1 - 0.5 * gh - 8, "B: ½ ходу → ½ опору", size=10, bold=True, color=NEG, anchor="start"))
    # A на ½ = ~0.10
    va = (math.pow(10, 2 * 0.5) - 1) / 99.0
    f.append(circle(midx, gy1 - va * gh, 4, fill=WIPER, stroke=INK, sw=1))
    f.append(text(midx + 10, gy1 - va * gh + 16, "A: ½ ходу → лише ~10 %", size=10, bold=True, color=WIPER, anchor="start"))

    # легенда — праворуч, у порожньому куті
    lx, ly = gx1 + 24, gy0 + 30
    f.append(line(lx, ly, lx + 30, ly, color=NEG, sw=3))
    f.append(text(lx + 38, ly + 4, "B — лінійний", size=11, bold=True, color=NEG, anchor="start"))
    f.append(line(lx, ly + 28, lx + 30, ly + 28, color=WIPER, sw=3))
    f.append(text(lx + 38, ly + 32, "A — логарифмічний", size=11, bold=True, color=WIPER, anchor="start"))
    f.append(fitbox(gx1 + 24, ly + 54, 150, 110,
                    "A стискає початок:\nдалеко повернув —\nмало змінилось; під\nкінець — різко. Саме\nце пасує гучності,\nбо вухо чує логом.",
                    size=10, fill="#fdf0ee", stroke=WIPER))

    b, _, _ = textbox(W / 2, 500,
                      "Однакова доріжка, різний закон нанесення шару: у лінійного «B» кут пропорційний опору; "
                      "у логарифмічного «A» на\nпівходу набирається лише ~десята частина, а основне — під кінець. "
                      "Увага: маркування A/B у різних виробників плутане — звіряйся з даташитом.",
                      size=10.5, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "taper.svg"), W, H, *f)


# ── 3. Підключення пін-у-пін: 3 виводи — кінці на +/−, повзунок в АЦП ──────────
def fig_wiring():
    W, H = 900, 470
    f = [text(W / 2, 28, "Підключення: два кінці на живлення й землю, повзунок — в аналоговий вхід (АЦП)",
              size=14, bold=True)]

    # модуль ліворуч
    mx, my, mw, mh = 80, 100, 210, 240
    f.append(rect(mx, my, mw, mh, fill="#fafbfc", stroke=MUTED, sw=1.8, rx=10))
    f.append(text(mx + mw / 2, my + 26, "потенціометр", size=13.5, bold=True))
    f.append(text(mx + mw / 2, my + 44, "3 виводи (крутилка)", size=9, color=MUTED))
    # ручка схематично
    f.append(circle(mx + mw / 2, my + 104, 30, fill="none", stroke="#cfd4da", sw=1.2))
    f.append(circle(mx + mw / 2, my + 104, 17, fill=KNOB, stroke=INK, sw=1.4))
    f.append(line(mx + mw / 2, my + 104, mx + mw / 2 + 12, my + 82, color=WIPER, sw=3))

    # три виводи знизу
    pins = [("1", POS, "#fdecea"), ("2 (повз.)", WIPER, "#fdecea"), ("3", NEG, "#eaf0fd")]
    pin_x = []
    for i, (nm, col, fl) in enumerate(pins):
        px = mx + 40 + i * 66
        pin_x.append(px)
        f.append(rect(px - 26, my + mh - 4, 52, 24, fill=fl, stroke=col, sw=1.4, rx=3))
        f.append(text(px, my + mh + 12, nm, size=9.5, bold=True, color=col))

    # МК праворуч
    ax, ay, aw, ah = 600, 120, 210, 200
    f.append(rect(ax, ay, aw, ah, fill="#eef2f8", stroke=INK, sw=1.8, rx=10))
    f.append(text(ax + aw / 2, ay + 26, "мікроконтролер", size=12.5, bold=True))
    f.append(text(ax + aw / 2, ay + 44, "(Arduino / ESP32 …)", size=9, color=MUTED))
    mpins = [("3.3 В / 5 В", POS), ("A0 (АЦП)", WIPER), ("GND", NEG)]
    mpin_y = []
    for i, (nm, col) in enumerate(mpins):
        py = ay + 82 + i * 40
        mpin_y.append(py)
        f.append(rect(ax - 4, py - 11, 8, 22, fill="#fff", stroke=col, sw=1.4, rx=2))
        f.append(text(ax - 12, py + 4, nm, size=9.5, bold=True, color=col, anchor="end"))

    # дроти — усі стебла спускаються нижче пінів, тоді розходяться до МК
    routes = [
        (pin_x[0], mpin_y[0], POS,   374),   # 1 -> живлення
        (pin_x[1], mpin_y[1], WIPER, 390),   # 2 -> A0
        (pin_x[2], mpin_y[2], NEG,   406),   # 3 -> GND
    ]
    for sxp, ryp, col, ylevel in routes:
        f.append(line(sxp, my + mh + 20, sxp, ylevel, color=col, sw=1.9))
        f.append(line(sxp, ylevel, ax - 4, ryp, color=col, sw=1.9))

    b, _, _ = textbox(W / 2, 448,
                      "Кінці 1 і 3 — на живлення та землю (напрям задає, куди «росте» напруга); повзунок 2 — "
                      "в аналоговий вхід A0.\nЖивлення бери під логіку своєї плати: на 3.3-В МК живи від 3.3 В, "
                      "інакше повзунок віддасть до 5 В і приб'є вхід.",
                      size=10, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "wiring.svg"), W, H, *f)


# ── 4. Вихідний опір повзунка від положення: R_out = k·(1−k)·R, макс. посередині ─
def fig_source_impedance():
    """Чому дрож найгірший посередині ходу: вихідний опір повзунка = паралель
    двох плечей = k·(1−k)·R_повний, максимум при k=0.5 (чверть повного опору)."""
    W, H = 900, 500
    f = [text(W / 2, 30, "Вихідний опір повзунка від положення ручки", size=16, bold=True),
         text(W / 2, 52, "R_вих = R_верх ∥ R_низ = k·(1−k)·R_повний — максимум рівно посередині ходу",
              size=12.5, color=MUTED)]

    # межі графіка
    gx0, gy0 = 130, 400        # початок осей (лівий-нижній)
    gw, gh = 620, 300          # ширина/висота поля
    gx1, gy1 = gx0 + gw, gy0 - gh

    # поле й осі
    f.append(rect(gx0, gy1, gw, gh, fill="#fbfcfd", stroke=MUTED, sw=1.2))
    f.append(line(gx0, gy0, gx1, gy0, color=INK, sw=2))        # X
    f.append(line(gx0, gy0, gx0, gy1, color=INK, sw=2))        # Y

    Rmax = 0.25   # k·(1−k) максимум = 0.25 (чверть R_повного)
    def px(k):    return gx0 + k * gw
    def py(frac): return gy0 - (frac / Rmax) * gh   # frac у частках R_повного

    # горизонтальні риски сітки: 0, чверть повного опору (=пік)
    for frac, lbl in [(0.0, "0"), (0.125, "⅛·R"), (0.25, "¼·R")]:
        yy = py(frac)
        f.append(line(gx0, yy, gx1, yy, color="#e3e7ec", sw=1))
        f.append(text(gx0 - 12, yy + 4, lbl, size=12, color=MUTED, anchor="end"))

    # вертикальні риски по k: 0, 0.5, 1
    for k, lbl in [(0.0, "0\n(упор −)"), (0.5, "½\n(середина)"), (1.0, "1\n(упор +)")]:
        xx = px(k)
        f.append(line(xx, gy0, xx, gy1, color="#e3e7ec", sw=1))
        f.append(mtext(xx, gy0 + 22, lbl, size=11.5, color=MUTED, lh=1.15))

    # сама крива R_вих = k·(1−k)
    pts = []
    n = 80
    for i in range(n + 1):
        k = i / n
        pts.append("%.1f,%.1f" % (px(k), py(k * (1 - k))))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
             % (" ".join(pts), POS))

    # позначити пік (анотація нижче-праворуч від вершини, зі стрілкою на неї)
    kpk = 0.5
    f.append(circle(px(kpk), py(0.25), 5, fill=POS, stroke=POS, sw=1))
    annx, anny = px(0.5) + 118, py(0.25) + 78
    f.append(line(px(kpk) + 6, py(0.25) + 3, annx - 92, anny - 12, color=POS, sw=1.4))
    box, bw, bh = textbox(annx, anny,
                          "пік дрожу: тут повзунок\n«м'якший» за все — джерело\nз найбільшим опором",
                          size=11, pad=8, fill="#fdecea", stroke=POS)
    f.append(box)

    # позначити край — жорсткий вихід (у правому нижньому куті, де крива низька)
    box2, w2, h2 = textbox(px(0.9), py(0.06) + 40,
                           "біля упорів R_вих → 0:\nвихід «жорсткий», дрож малий",
                           size=10.5, pad=7, fill="#eaf6ee", stroke=FIELD)
    f.append(box2)

    # підпис осей: X — під віссю праворуч, Y — вертикально ліворуч від осі Y
    f.append(text(gx1 - 4, gy0 + 52, "положення ручки  k", size=12.5, bold=True, anchor="end"))
    ylx = gx0 - 70
    f.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="12.5" fill="%s" '
             'font-weight="700" text-anchor="middle" transform="rotate(-90 %.1f %.1f)">'
             'вихідний опір повзунка</text>'
             % (ylx, (gy0 + gy1) / 2, FONT, INK, ylx, (gy0 + gy1) / 2))

    render(os.path.join(IMG, "source-impedance.svg"), W, H, *f)


# ── 5. (hist) Метод компенсації Поггендорффа: баланс на нуль, струм не тече ─────
def fig_compensation():
    W, H = 940, 520
    f = [text(W / 2, 30, "Метод компенсації: невідому ЕРС урівноважують часткою відомої напруги — гальванометр на нулі",
              size=13.5, bold=True)]

    # верхнє коло: відома напруга жене струм крізь довгий однорідний дріт
    wire_y = 158
    wx0, wx1 = 190, 800
    bx = 120
    f.append(line(bx, wire_y, wx0, wire_y, color=INK, sw=2))
    f.append(line(bx, wire_y, bx, wire_y + 64, color=INK, sw=2))
    f.append(line(bx - 14, wire_y + 64, bx + 14, wire_y + 64, color=POS, sw=3))
    f.append(line(bx - 8, wire_y + 74, bx + 8, wire_y + 74, color=NEG, sw=2))
    f.append(mtext(bx - 48, wire_y + 60, ["відоме", "джерело"], size=10.5, bold=True, color=MUTED, anchor="end"))
    f.append(rect(wx0, wire_y - 7, wx1 - wx0, 14, fill="#f0e6e6", stroke=TRACK, sw=1.8, rx=6))
    f.append(text((wx0 + wx1) / 2, wire_y - 22, "однорідний слайд-дріт: спад напруги ∝ довжині", size=10.5, color="#7a4040"))
    for i in range(11):
        mx = wx0 + (wx1 - wx0) * i / 10
        f.append(line(mx, wire_y + 7, mx, wire_y + 13, color=MUTED, sw=1))
    f.append(text(wx0, wire_y + 30, "0", size=10, color=MUTED))
    f.append(text(wx1, wire_y + 30, "весь дріт = вся відома напруга", size=10, color=MUTED, anchor="end"))
    f.append(line(wx1, wire_y, wx1 + 44, wire_y, color=INK, sw=2))
    f.append(line(wx1 + 44, wire_y, wx1 + 44, wire_y + 74, color=INK, sw=2))
    f.append(line(wx1 + 44, wire_y + 74, bx, wire_y + 74, color=INK, sw=2))
    f.append(arrow(wx0 + 70, wire_y - 44, wx0 + 200, wire_y - 44, color=MUTED, sw=1.6))
    f.append(text(wx0 + 250, wire_y - 40, "постійний струм жене напругу вздовж дроту", size=9.5, color=MUTED, anchor="start"))

    # рухомий контакт (повзунок) на дроті
    tap_frac = 0.60
    tapx = wx0 + (wx1 - wx0) * tap_frac
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" stroke="%s" stroke-width="1.5"/>'
             % (tapx, wire_y + 7, tapx - 12, wire_y + 32, tapx + 12, wire_y + 32, WIPER, INK))
    # підпис повзунка — ЛІВОРУЧ від стебла (щоб вертикальне стебло його не різало)
    f.append(mtext(tapx - 22, wire_y + 50, ["рухомий контакт", "(совгаєш, доки G = 0)"],
                   size=10, bold=True, color=WIPER, anchor="end"))

    # нижня гілка: невідома ЕРС + гальванометр
    branch_y = 388
    f.append(line(tapx, wire_y + 32, tapx, branch_y, color=WIPER, sw=2))
    f.append(line(tapx, branch_y, wx0, branch_y, color=INK, sw=2))
    f.append(line(wx0, branch_y, wx0, wire_y, color=INK, sw=2))
    gx, gy = tapx - 150, branch_y
    f.append(circle(gx, gy, 24, fill="#eef2f8", stroke=INK, sw=2))
    f.append(text(gx, gy + 5, "G", size=17, bold=True))
    f.append(line(gx, gy, gx, gy - 14, color=POS, sw=2))
    f.append(text(gx, gy - 20, "0", size=10, bold=True, color=INK))
    f.append(mtext(gx, gy + 44, ["гальванометр", "показує НУЛЬ → струму нема"], size=10, bold=True, color=FIELD))
    cx2 = (wx0 + (gx - 24)) / 2
    f.append(line(cx2, branch_y - 14, cx2, branch_y + 14, color=POS, sw=3))
    f.append(line(cx2 + 12, branch_y - 8, cx2 + 12, branch_y + 8, color=NEG, sw=2))
    f.append(mtext(cx2 + 2, branch_y + 40, ["невідома", "ЕРС Eₓ"], size=10.5, color=POS, bold=True))

    # пояснювальна рамка — у вільному правому полі, праворуч від повзунка,
    # нижче зворотного дроту й вище нижньої гілки: жодна лінія її не перетинає
    f.append(fitbox(580, 250, 342, 124,
                    "Совгаєш контакт, доки напруга на відрізку\n"
                    "дроту (частка відомої) точно не зрівняє\n"
                    "невідому ЕРС. Тоді G = 0: струм крізь\n"
                    "невідоме джерело не тече, і його ЕРС\n"
                    "виміряна БЕЗ відбору струму — без\n"
                    "спотворення внутрішнім опором джерела.",
                    size=10.5, fill="#eef6ef", stroke=FIELD))

    b, _, _ = textbox(W / 2, 492,
                      "Оце і є «potentiometer» у первісному значенні: прилад, що МІРЯЄ потенціал балансом на нуль. "
                      "Довжина відрізка дроту від лівого\nкінця до контакту (за рівномірною шкалою) прямо дає невідому "
                      "напругу — точно саме тому, що в мить балансу давач нічого не навантажує.",
                      size=10.5, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "compensation.svg"), W, H, *f)


if __name__ == "__main__":
    fig_inside()
    fig_taper()
    fig_wiring()
    fig_source_impedance()
    fig_compensation()
    print("OK: 5 figures ->", IMG)
