# -*- coding: utf-8 -*-
"""Фігури до теми «Балансування комірок батареї».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

AMBER = "#b8860b"   # тепло / резистор
REDBG = "#fbeee6"   # світлий червоний фон
BLUBG = "#eef3fb"   # світлий синій фон
GRNBG = "#e9f7ef"   # світлий зелений фон


# ── Розкид звужує корисне вікно ────────────────────────────────────────────────
def fig_window_shrink():
    W, H = 860, 440
    f = [text(W / 2, 30, "Розкид комірок звужує корисне вікно пакета",
              size=17, bold=True)]

    def y(pct):
        return 340 - 2.4 * pct          # 100% → 100 ; 0% → 340

    levels = [100, 93, 87, 80]          # SoC комірок після повного заряду
    centers = [200, 340, 480, 620]
    bw = 74
    for cx, lv in zip(centers, levels):
        # трек комірки (повний хід 0..100%)
        f.append(rect(cx - bw / 2, y(100), bw, y(0) - y(100), fill="#f0f0f0", stroke=MUTED, sw=1.3))
        # заряд (зелене)
        f.append(rect(cx - bw / 2 + 3, y(lv), bw - 6, y(0) - y(lv), fill=FIELD, stroke=FIELD, sw=1))
        f.append(text(cx, y(lv) - 8, "%d%%" % lv, size=11, bold=True, color=FIELD))
        f.append(text(cx, y(0) + 20, "комірка", size=10, color=MUTED))

    # дві опорні лінії: стеля заряду й спільна межа (найнижча комірка)
    f.append(line(150, y(100), 690, y(100), color=POS, sw=1.6, dash="6,4"))
    f.append(text(248, y(100) - 8, "стеля заряду — обриває найповніша", size=10.5, bold=True, color=POS, anchor="start"))
    f.append(line(150, y(80), 690, y(80), color=NEG, sw=1.6, dash="6,4"))
    f.append(text(150, y(80) + 15, "спільна межа — задає найнижча комірка", size=10.5, bold=True, color=NEG, anchor="start"))

    # брекети зліва: розкид (втрата) і корисне вікно
    f.append(line(120, y(100), 120, y(80), color=POS, sw=2))
    f.append(line(114, y(100), 126, y(100), color=POS, sw=2))
    f.append(line(114, y(80), 126, y(80), color=POS, sw=2))
    f.append(mtext(108, (y(100) + y(80)) / 2 - 6, "розкид\n(втрата)", size=10.5, bold=True, color=POS, anchor="end"))
    f.append(line(120, y(80), 120, y(0), color=FIELD, sw=2))
    f.append(line(114, y(80), 126, y(80), color=FIELD, sw=2))
    f.append(line(114, y(0), 126, y(0), color=FIELD, sw=2))
    f.append(mtext(108, (y(80) + y(0)) / 2 - 6, "корисне\nвікно", size=10.5, bold=True, color=FIELD, anchor="end"))

    b, _, _ = textbox(W / 2, 410,
                      "корисна ємність = повна − розкид: розбіжність комірок вкорочує вікно; вирівняти їх — повернути повне вікно",
                      size=11, fill=GRNBG, stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "window-shrink.svg"), W, H, *f)


# ── OCV-крива: чому балансувати по верху заряду ────────────────────────────────
def fig_top_balance_ocv():
    W, H = 820, 440
    f = [text(W / 2, 30, "Чому балансувати наприкінці заряду: OCV-крива",
              size=17, bold=True)]
    x0, x1 = 110, 740          # SoC 0..100 %
    yb, yt = 340, 100          # V 2.9 .. 4.25

    def px(soc):
        return x0 + (x1 - x0) * soc / 100.0

    def py(v):
        return yb - (v - 2.9) / (4.25 - 2.9) * (yb - yt)

    # затінені смуги: пласка середина й крута верхівка
    f.append(rect(px(30), yt, px(70) - px(30), yb - yt, fill="#f0f0f0", stroke="none", sw=0))
    f.append(rect(px(85), yt, px(100) - px(85), yb - yt, fill=REDBG, stroke="none", sw=0))

    # осі
    f.append(line(x0, yb, x1, yb, color=INK, sw=1.5))
    f.append(line(x0, yb, x0, yt, color=INK, sw=1.5))
    for soc in (0, 50, 100):
        f.append(text(px(soc), yb + 20, "%d" % soc, size=10, color=MUTED))
    f.append(text((x0 + x1) / 2, yb + 40, "заряд SoC, %", size=11, color=INK))
    for v in (3.0, 3.6, 4.2):
        f.append(text(x0 - 12, py(v) + 4, "%.1f" % v, size=10, color=MUTED, anchor="end"))
    f.append(text(x0 - 44, (yt + yb) / 2, "В", size=11, color=INK))

    # крива
    pts = [(0, 3.00), (5, 3.45), (10, 3.62), (20, 3.72), (30, 3.77), (40, 3.81),
           (50, 3.85), (60, 3.89), (70, 3.94), (80, 4.00), (88, 4.08),
           (94, 4.15), (100, 4.20)]
    d = "M " + " L ".join("%.1f %.1f" % (px(s), py(v)) for s, v in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, NEG))

    # підписи смуг
    f.append(mtext(px(50), 260, "пласка середина:\nоднакова V ховає різний SoC", size=10.5, color=INK))
    f.append(mtext(px(92), 400, "крута верхівка:\nмалий ΔV = чіткий ΔSoC\n→ балансуємо в CV", size=10.5, bold=True, color=POS))
    # стрілки від підписів до ділянок
    f.append(arrow(px(92), 358, px(94), py(4.15) + 8, color=POS, sw=1.4))
    render(os.path.join(IMG, "top-balance-ocv.svg"), W, H, *f)


# ── Пасивне балансування: резистор + ключ на кожну комірку ─────────────────────
def fig_passive_circuit():
    W, H = 820, 470
    f = [text(W / 2, 30, "Пасивне балансування: резистор і ключ на комірку",
              size=17, bold=True)]
    xs = 300                                    # вісь послідовної збірки
    nodes = [70, 160, 250, 340]                 # N0(+) N1 N2 N3(−)
    cells = [(80, 150, "4.15 В", "найповніша", POS),
             (170, 240, "4.10 В", "", FIELD),
             (260, 330, "4.08 В", "", FIELD)]
    # виводи + / −
    f.append(text(xs, 60, "+", size=15, bold=True, color=POS))
    f.append(text(xs, 358, "−", size=15, bold=True, color=NEG))
    # послідовна лінія
    f.append(line(xs, 62, xs, 340, color=INK, sw=2))
    # комірки
    for (ty, by, volt, tag, col) in cells:
        f.append(rect(xs - 50, ty, 100, by - ty, fill=GRNBG, stroke=col, sw=1.8))
        f.append(text(xs, (ty + by) / 2 - 4, "комірка", size=10, color=MUTED))
        f.append(text(xs, (ty + by) / 2 + 15, volt, size=11.5, bold=True, color=col))
        if tag:
            f.append(text(xs, ty - 6, tag, size=10, bold=True, color=POS))

    # рунги балансування (R + ключ) між сусідніми вузлами
    xr = 470
    rungs = [(70, 160, True), (160, 250, False), (250, 340, False)]
    for (ya, yb, hot) in rungs:
        col = POS if hot else INK
        f.append(line(xs, ya, xr, ya, color=col, sw=1.6))
        f.append(line(xr, ya, xr, ya + 14, color=col, sw=1.6))
        f.append(line(xr, ya + 40, xr, yb - 40, color=col, sw=1.6))
        f.append(line(xr, yb - 14, xr, yb, color=col, sw=1.6))
        f.append(line(xr, yb, xs, yb, color=col, sw=1.6))
        rc = (ya + yb) / 2
        f.append(rect(xr - 24, ya + 14, 48, 26, fill=BG, stroke=(POS if hot else AMBER), sw=1.7))
        f.append(text(xr, ya + 32, "R", size=12, bold=True, color=(POS if hot else AMBER)))
        f.append(rect(xr - 24, yb - 40, 48, 26, fill=BG, stroke=(POS if hot else INK), sw=1.7))
        f.append(text(xr, yb - 22, "ключ", size=10, bold=True, color=(POS if hot else INK)))
        if hot:
            f.append(arrow(xr, ya + 42, xr, yb - 42, color=POS, sw=1.8))
            f.append(text(xr + 34, rc - 6, "I ≈ 61 мА", size=11, bold=True, color=POS, anchor="start"))
            f.append(text(xr + 34, rc + 12, "→ тепло 0.25 Вт", size=10.5, color=POS, anchor="start"))

    # монітор комірок
    f.append(rect(50, 150, 160, 130, fill=BLUBG, stroke=NEG, sw=1.8))
    f.append(text(130, 195, "монітор", size=12.5, bold=True, color=NEG))
    f.append(text(130, 216, "комірок", size=12.5, bold=True, color=NEG))
    f.append(text(130, 240, "міряє V,", size=10, color=INK))
    f.append(text(130, 256, "керує ключами", size=10, color=INK))
    # керує ключами (зелене) до кожного ключа
    for (ya, yb, hot) in rungs:
        f.append(arrow(210, 200, xr - 24, yb - 27, color=FIELD, sw=1.3))
    # міряє напруги (синє пунктирне) до вузлів
    for ny in nodes:
        f.append(line(210, 250, xs - 50, ny, color=NEG, sw=1.1, dash="3,3"))

    b, _, _ = textbox(W / 2, 445,
                      "наприкінці заряду монітор замикає ключ найповнішої комірки; резистор зливає надлишок у тепло, поки вона не зрівняється з рештою",
                      size=11, fill=BLUBG, stroke=NEG)
    f.append(b)
    render(os.path.join(IMG, "passive-circuit.svg"), W, H, *f)


# ── Активне балансування: конденсатор проти котушки ────────────────────────────
def fig_active_topologies():
    W, H = 880, 415
    f = [text(W / 2, 30, "Активне балансування: перенести заряд, а не спалити",
              size=17, bold=True)]

    def panel(x0, ttl, elem):
        g = [rect(x0, 56, 390, 300, fill=BG, stroke=MUTED, sw=1.4)]
        g.append(text(x0 + 195, 82, ttl, size=13, bold=True))
        cx = x0 + 90
        # дві комірки, послідовно
        g.append(rect(cx - 50, 110, 100, 56, fill=GRNBG, stroke=FIELD, sw=1.7))
        g.append(text(cx, 132, "комірка", size=10, color=MUTED))
        g.append(text(cx, 150, "повна", size=11, bold=True, color=FIELD))
        g.append(rect(cx - 50, 236, 100, 56, fill="#f0f0f0", stroke=MUTED, sw=1.7))
        g.append(text(cx, 258, "комірка", size=10, color=MUTED))
        g.append(text(cx, 276, "порожніша", size=11, bold=True, color=NEG))
        g.append(line(cx, 166, cx, 236, color=INK, sw=2))
        # елемент-відро праворуч
        ex = x0 + 250
        g += elem(ex)
        # два кроки: набрати з повної, скинути в порожнішу
        g.append(arrow(cx + 50, 138, ex - 26, 185, color=POS, sw=1.8))
        g.append(text(cx + 96, 158, "1) набирає", size=10.5, bold=True, color=POS, anchor="start"))
        g.append(arrow(ex - 26, 215, cx + 50, 264, color=NEG, sw=1.8))
        g.append(text(cx + 96, 250, "2) скидає", size=10.5, bold=True, color=NEG, anchor="start"))
        return g

    def cap(ex):
        g = [line(ex - 10, 172, ex - 10, 216, color=INK, sw=3),
             line(ex + 6, 172, ex + 6, 216, color=INK, sw=3),
             line(ex - 10, 194, ex - 26, 194, color=INK, sw=1.5),
             line(ex + 6, 194, ex + 22, 194, color=INK, sw=1.5),
             text(ex - 2, 150, "C", size=14, bold=True, color=INK),
             text(ex - 2, 240, "летючий", size=10, color=MUTED),
             text(ex - 2, 255, "конденсатор", size=10, color=MUTED)]
        return g

    def coil(ex):
        d = "M %d 172" % ex
        yy = 172
        for _ in range(4):
            d += " a 8 8 0 0 1 0 16"
            yy += 16
        g = ['<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, INK),
             line(ex, 168, ex - 22, 168, color=INK, sw=1.5),
             line(ex, 236, ex - 22, 236, color=INK, sw=1.5),
             text(ex + 16, 150, "L", size=14, bold=True, color=INK),
             text(ex + 4, 258, "котушка", size=10, color=MUTED)]
        return g

    f += panel(30, "Ємнісний — летючий конденсатор", cap)
    f += panel(460, "Індуктивний — котушка як відро", coil)
    b, _, _ = textbox(W / 2, 390,
                      ["заряд переносять із повної комірки в порожнішу — конденсатором або котушкою —",
                       "замість палити; на відміну від пасивного, вміє піднімати відстаючу"],
                      size=11, fill=GRNBG, stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "active-topologies.svg"), W, H, *f)


# ── Діючий струм балансу: пік × шпаруватість проти розкиду витоку ───────────────
def fig_balance_effective_current():
    W, H = 920, 430
    f = [text(W / 2, 30, "Пік струму — не те, що працює: діючий струм балансу", size=16.5, bold=True)]

    # Панель A: імпульси в часі (висота НЕ в масштабі)
    ax0, ax1 = 70, 440
    ayb, ayt = 330, 95
    f.append(text((ax0 + ax1) / 2, 62, "А. Балансир умикається лиш у вікні", size=12.5, bold=True))
    f.append(line(ax0, ayb, ax1, ayb, color=INK, sw=1.5))
    f.append(line(ax0, ayb, ax0, ayt, color=INK, sw=1.5))
    f.append(text(ax0 - 8, ayt + 2, "I", size=11, color=INK, anchor="end"))
    centers = [135, 255, 375]
    for cx in centers:
        f.append(rect(cx - 11, ayt, 22, ayb - ayt, fill=REDBG, stroke=POS, sw=1.6, rx=2))
    f.append(text(centers[0], ayt - 9, "I_б = 60 мА", size=10.5, bold=True, color=POS))
    f.append(text(centers[1], ayt - 9, "вікно", size=10, color=POS))
    f.append(text(centers[2], ayt - 9, "~30 хв", size=10, color=POS))
    yavg = ayb - 24
    f.append(line(ax0, yavg, ax1, yavg, color=FIELD, sw=2, dash="7,4"))
    f.append(text(ax1 - 4, yavg - 7, "I_еф = I_б·D", size=10.5, bold=True, color=FIELD, anchor="end"))
    f.append(text((ax0 + ax1) / 2, ayb + 22, "час (цикли заряду) →", size=10.5, color=MUTED))
    f.append(text((ax0 + ax1) / 2, ayb + 40, "(висота не в масштабі)", size=9.5, color=MUTED, italic=True))

    # Панель B: перегони — I_еф проти розкиду витоку (в масштабі)
    sx0, sx1 = 560, 890            # 0 .. 1.0 мА
    def bpx(v):
        return sx0 + (sx1 - sx0) * v / 1.0
    f.append(text((sx0 + sx1) / 2, 62, "Б. I_еф проти розкиду витоку (в масштабі)", size=12.5, bold=True))
    f.append(line(sx0, 300, sx1, 300, color=INK, sw=1.5))
    for v in (0.0, 0.5, 1.0):
        f.append(line(bpx(v), 300, bpx(v), 305, color=INK, sw=1.2))
        f.append(text(bpx(v), 320, "%.1f" % v, size=10, color=MUTED))
    f.append(text((sx0 + sx1) / 2, 340, "струм, мА", size=10.5, color=INK))
    f.append(rect(sx0, 120, bpx(0.83) - sx0, 34, fill=GRNBG, stroke=FIELD, sw=1.7))
    f.append(text(sx0 + 4, 112, "I_еф ≈ 0.83 мА  (вікно 30 хв/добу)", size=10.5, bold=True, color=FIELD, anchor="start"))
    f.append(rect(sx0, 200, bpx(0.062) - sx0, 34, fill=REDBG, stroke=POS, sw=1.7))
    f.append(text(bpx(0.062) + 10, 222, "розкид витоку ΔI ≈ 0.06 мА", size=10.5, bold=True, color=POS, anchor="start"))
    f.append(text((sx0 + sx1) / 2, 272, "перекрито ≈ ×13 → тримати легко", size=11, bold=True, color=FIELD))

    b, _, _ = textbox(W / 2, 405,
                      "діючий струм I_еф = I_б·D — це усереднений пік; тримати вирівняний пакет проти саморозряду легко, бо розкид витоку лише мікроамперний",
                      size=11, fill=GRNBG, stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "balance-effective-current.svg"), W, H, *f)


# ── Сходження розриву по циклах: пасивне проти активного ────────────────────────
def fig_balance_convergence():
    W, H = 880, 450
    f = [text(W / 2, 30, "Сходження розриву: пасивне за вісім циклів, активне за два-три", size=16, bold=True)]
    x0, x1 = 95, 800
    yb, yt = 355, 95
    Qmax = 260.0

    def px(c):
        return x0 + (x1 - x0) * c / 9.0

    def py(q):
        return yb - (yb - yt) * q / Qmax

    f.append(line(x0, yb, x1, yb, color=INK, sw=1.5))
    f.append(line(x0, yb, x0, yt, color=INK, sw=1.5))
    for c in (0, 2, 4, 6, 8):
        f.append(line(px(c), yb, px(c), yb + 5, color=INK, sw=1.2))
        f.append(text(px(c), yb + 22, "%d" % c, size=10.5, color=MUTED))
    f.append(text((x0 + x1) / 2, yb + 42, "цикл заряду", size=11, color=INK))
    for q in (0, 120, 240):
        f.append(line(x0 - 5, py(q), x0, py(q), color=INK, sw=1.2))
        f.append(text(x0 - 10, py(q) + 4, "%d" % q, size=10.5, color=MUTED, anchor="end"))
    f.append(text(x0 - 58, (yt + yb) / 2 - 8, "розрив", size=10.5, color=INK))
    f.append(text(x0 - 58, (yt + yb) / 2 + 8, "ΔQ, мА·год", size=10.5, color=INK))
    f.append(text(px(0) + 8, py(240) - 12, "старт: 8% = 240 мА·год", size=10.5, bold=True, color=INK, anchor="start"))

    # пасивна ламана: 240 − 30·k
    pas = [(k, max(0, 240 - 30 * k)) for k in range(0, 9)]
    d = "M " + " L ".join("%.1f %.1f" % (px(c), py(q)) for c, q in pas)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, POS))
    for c, q in pas:
        f.append(circle(px(c), py(q), 3.5, fill=POS, stroke=POS, sw=1))
    f.append(text(px(3.2), 150, "пасивний: 30 мА·год/цикл", size=11, bold=True, color=POS, anchor="start"))
    f.append(text(px(3.2), 166, "→ 8 циклів, ≈1 Вт·год у тепло", size=10.5, color=POS, anchor="start"))

    # активна ламана: 240 − 120·k → 0 на циклі 2
    act = [(0, 240), (1, 120), (2, 0)]
    d2 = "M " + " L ".join("%.1f %.1f" % (px(c), py(q)) for c, q in act)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d2, FIELD))
    for c, q in act:
        f.append(circle(px(c), py(q), 3.5, fill=FIELD, stroke=FIELD, sw=1))
    f.append(arrow(px(3.0) + 5, 332, px(2) + 4, 352, color=FIELD, sw=1.5))
    f.append(text(px(3.0) + 10, 328, "активний: перенос → 2–3 цикли,", size=11, bold=True, color=FIELD, anchor="start"))
    f.append(text(px(3.0) + 10, 344, "майже без утрат", size=10.5, color=FIELD, anchor="start"))

    b, _, _ = textbox(W / 2, 428,
                      "щоцикла балансир прибирає порцію q = I_б·t_вікна; пасивний ллє її в тепло, активний переносить у сусідню комірку швидше й без спалення",
                      size=11, fill=BLUBG, stroke=NEG)
    f.append(b)
    render(os.path.join(IMG, "balance-convergence.svg"), W, H, *f)


# ── Перелом: цикли пасивного сходження ростуть з ємністю комірки ────────────────
def fig_balance_crossover():
    W, H = 860, 450
    f = [text(W / 2, 30, "Коли пасивного бракує: цикли сходження ростуть з ємністю", size=16, bold=True)]
    x0, x1 = 100, 760
    yb, yt = 350, 95
    Qmax = 18.0            # А·год
    Nmax = 40.0
    Qcross = 7.5

    def px(q):
        return x0 + (x1 - x0) * q / Qmax

    def py(n):
        return yb - (yb - yt) * n / Nmax

    # зони
    f.append(rect(px(0), yt, px(Qcross) - px(0), yb - yt, fill=GRNBG, stroke="none", sw=0))
    f.append(rect(px(Qcross), yt, px(Qmax) - px(Qcross), yb - yt, fill=REDBG, stroke="none", sw=0))
    # осі
    f.append(line(x0, yb, x1, yb, color=INK, sw=1.5))
    f.append(line(x0, yb, x0, yt, color=INK, sw=1.5))
    for q in (0, 5, 10, 15):
        f.append(line(px(q), yb, px(q), yb + 5, color=INK, sw=1.2))
        f.append(text(px(q), yb + 22, "%d" % q, size=10.5, color=MUTED))
    f.append(text((x0 + x1) / 2, yb + 42, "ємність комірки, А·год", size=11, color=INK))
    for n in (0, 20, 40):
        f.append(line(x0 - 5, py(n), x0, py(n), color=INK, sw=1.2))
        f.append(text(x0 - 10, py(n) + 4, "%d" % n, size=10.5, color=MUTED, anchor="end"))
    f.append(text(x0 - 60, (yt + yb) / 2 - 8, "циклів", size=10.5, color=INK))
    f.append(text(x0 - 60, (yt + yb) / 2 + 8, "сходження", size=10.5, color=INK))
    # межа прийнятного
    f.append(line(px(0), py(20), px(Qmax), py(20), color=MUTED, sw=1.6, dash="6,4"))
    f.append(text(px(Qmax) - 4, py(20) - 7, "межа ≈20 циклів", size=10, color=MUTED, anchor="end"))
    # пасивна пряма (N = 2.667·Q, до верху при Q=15)
    f.append(line(px(0), py(0), px(15), py(40), color=POS, sw=2.6))
    f.append(text(px(5.3), py(31), "пасивний 60 мА", size=11.5, bold=True, color=POS))
    f.append(text(px(5.3), py(31) + 16, "N = 0.08·Q / 30", size=10, color=POS))
    # активна майже плоска
    f.append(line(px(0), py(2.5), px(Qmax), py(2.5), color=FIELD, sw=2.6))
    f.append(text(px(12), py(2.5) - 12, "активне ≈ 2–3 цикли (амперами, двобічно)", size=10.5, bold=True, color=FIELD))
    # точка перелому
    f.append(line(px(Qcross), py(20), px(Qcross), yb, color=INK, sw=1, dash="3,3"))
    f.append(circle(px(Qcross), py(20), 4.5, fill=BG, stroke=INK, sw=2))
    f.append(text(px(Qcross) + 8, py(20) - 9, "перелом ≈ 7.5 А·год", size=10, bold=True, color=INK, anchor="start"))
    # маркери прикладів
    f.append(circle(px(3), py(8), 3.6, fill=POS, stroke=POS, sw=1))
    f.append(text(px(3) + 10, py(8) + 18, "телефон 3 А·год", size=10, color=INK, anchor="start"))
    f.append(text(px(11.5), py(12), "тягова 50 А·год →", size=10.5, bold=True, color=POS))
    f.append(text(px(11.5), py(12) - 15, "N ≈ 133 (за межею графіка)", size=10, color=POS))

    b, _, _ = textbox(W / 2, 428,
                      "малі комірки лишаються в зеленій зоні пасивного; великі тягові падають у червону, де рятує лише активне з його амперами й двобічністю",
                      size=11, fill=REDBG, stroke=POS)
    f.append(b)
    render(os.path.join(IMG, "balance-crossover.svg"), W, H, *f)


# ── Крос-бар летючого конденсатора + двофазний шатл (для proj) ─────────────────
def fig_crossbar_shuttle():
    W, H = 820, 600
    f = [text(W / 2, 30, "Крос-бар летючого конденсатора: дві фази, break-before-make",
              size=16, bold=True)]

    # послідовний рядок: 4 комірки, 5 відводів n0..n4
    xr = 168
    ny = [92, 165, 238, 311, 384]
    volt = ["4.152", "4.140", "4.133", "4.121"]
    colc = [POS, FIELD, FIELD, NEG]
    f.append(line(xr, ny[0], xr, ny[-1], color=INK, sw=2))
    for i, yv in enumerate(ny):
        f.append(circle(xr, yv, 3.6, fill=INK, stroke=INK, sw=1))
        f.append(text(xr - 12, yv + 4, "n%d" % i, size=10, color=MUTED, anchor="end"))
    for k in range(4):
        yc = (ny[k] + ny[k + 1]) / 2
        f.append(rect(66, ny[k] + 7, 92, ny[k + 1] - ny[k] - 14, fill=BG, stroke=colc[k], sw=1.7))
        f.append(text(112, yc - 3, "комірка %d" % k, size=9.5, color=MUTED))
        f.append(text(112, yc + 14, volt[k] + " В", size=11, bold=True, color=colc[k]))
    f.append(text(112, ny[0] - 8, "донор (повна)", size=9.5, bold=True, color=POS))
    f.append(text(112, ny[4] + 16, "реципієнт (порожня)", size=9.5, bold=True, color=NEG))

    # летючий конденсатор праворуч
    cxp = 452
    cyt, cyb = 214, 262
    f.append(line(cxp - 26, cyt, cxp + 26, cyt, color=INK, sw=3))
    f.append(line(cxp - 26, cyb, cxp + 26, cyb, color=INK, sw=3))
    f.append(text(cxp + 42, (cyt + cyb) / 2 - 2, "C", size=14, bold=True, color=INK, anchor="start"))
    f.append(text(cxp + 42, (cyt + cyb) / 2 + 15, "100 мкФ", size=9.5, color=MUTED, anchor="start"))
    jt = (cxp, cyt - 24)
    jb = (cxp, cyb + 24)
    f.append(line(cxp, cyt, jt[0], jt[1], color=INK, sw=1.6))
    f.append(line(cxp, cyb, jb[0], jb[1], color=INK, sw=1.6))

    def yat(p1, p2, x):
        return p1[1] + (p2[1] - p1[1]) * (x - p1[0]) / (p2[0] - p1[0])

    def sw_box(x, y, lbl, col):
        f.append(rect(x - 16, y - 10, 32, 20, fill=BG, stroke=col, sw=1.7))
        f.append(text(x, y + 4, lbl, size=9.5, bold=True, color=col))

    # CHARGE: суцільні POS до n0, n1
    f.append(line(jt[0], jt[1], xr, ny[0], color=POS, sw=2))
    f.append(line(jb[0], jb[1], xr, ny[1], color=POS, sw=2))
    sw_box(270, yat(jt, (xr, ny[0]), 270), "A0", POS)
    sw_box(292, yat(jb, (xr, ny[1]), 292), "B1", POS)
    # DUMP: пунктир NEG до n3, n4 (наступна фаза)
    f.append(line(jt[0], jt[1], xr, ny[3], color=NEG, sw=1.7, dash="6,4"))
    f.append(line(jb[0], jb[1], xr, ny[4], color=NEG, sw=1.7, dash="6,4"))
    sw_box(332, yat(jt, (xr, ny[3]), 332), "A3", NEG)
    sw_box(354, yat(jb, (xr, ny[4]), 354), "B4", NEG)

    # легенда селекторів
    f.append(line(556, 150, 586, 150, color=POS, sw=2))
    f.append(text(592, 154, "фаза CHARGE (цап на донора)", size=10, color=POS, anchor="start"))
    f.append(line(556, 172, 586, 172, color=NEG, sw=1.7, dash="6,4"))
    f.append(text(592, 176, "фаза DUMP (цап на реципієнта)", size=10, color=NEG, anchor="start"))
    # застереження про наскрізний струм
    b, _, _ = textbox(662, 258,
                      "правило крос-бару:\nодночасно лише ОДНА A і ОДНА B\nдві A разом коротять\nкомірки між їхніми вузлами",
                      size=10, fill=REDBG, stroke=POS)
    f.append(b)

    # часова стрічка двох фаз
    ty = 470
    x0 = 70
    segs = [("CHARGE", 250, "#fdecea", POS), ("", 28, "#e9edf2", MUTED),
            ("DUMP", 250, "#eaf0fd", NEG), ("", 28, "#e9edf2", MUTED)]
    x = x0
    mids = []
    for name, w, fillc, col in segs:
        f.append(rect(x, ty - 16, w, 32, fill=fillc, stroke=col, sw=1.5, rx=3))
        if name:
            f.append(text(x + w / 2, ty + 5, name, size=12, bold=True, color=col))
        mids.append((name, x + w / 2))
        x += w
    f.append(text(x + 14, ty + 5, "…", size=16, bold=True, color=MUTED, anchor="start"))
    f.append(text(mids[0][1], ty - 24, "≈ 20 мкс — цап набирає від донора", size=9.5, color=POS))
    f.append(text(mids[2][1], ty - 24, "≈ 20 мкс — цап віддає реципієнту", size=9.5, color=NEG))
    f.append(mtext(mids[1][1], ty + 30, "0.3 мкс\nмертвий час", size=9, color=MUTED))
    f.append(mtext(mids[3][1], ty + 30, "0.3 мкс\nмертвий час", size=9, color=MUTED))

    b2, _, _ = textbox(W / 2, 560,
                       "цап набирає заряд від донора, тоді — усе розімкнути на мертвий час — і віддає реципієнту; за цикл переносить q = C·ΔV",
                       size=11, fill=GRNBG, stroke=FIELD)
    f.append(b2)
    render(os.path.join(IMG, "crossbar-shuttle.svg"), W, H, *f)


# ── Логіка керма: вікно + гістерезисна машина станів (для proj) ────────────────
def fig_balance_fsm():
    W, H = 900, 450
    f = [text(W / 2, 30, "Логіка керма: вікно балансування + гістерезисна машина станів",
              size=16, bold=True)]

    # вікно балансування
    gx, gy, gw, gh = 40, 100, 250, 150
    f.append(rect(gx, gy, gw, gh, fill=BLUBG, stroke=NEG, sw=1.8))
    f.append(text(gx + gw / 2, gy + 30, "Вікно балансування", size=12.5, bold=True, color=NEG))
    f.append(text(gx + gw / 2, gy + 60, "|струм пакета| < I_макс", size=10.5, color=INK))
    f.append(text(gx + gw / 2, gy + 84, "І  зарядник у фазі CV", size=10.5, color=INK))
    f.append(line(gx + 22, gy + 104, gx + gw - 22, gy + 104, color=MUTED, sw=1, dash="3,3"))
    f.append(text(gx + gw / 2, gy + 126, "інакше → shuttle_stop", size=10, italic=True, color=MUTED))

    # стани
    def state(cx, cy, name, sub, col):
        f.append(rect(cx - 72, cy - 40, 144, 80, fill=BG, stroke=col, sw=2, rx=40))
        f.append(text(cx, cy - 4, name, size=15, bold=True, color=col))
        f.append(text(cx, cy + 20, sub, size=9.5, color=MUTED))

    iy = 175
    ix, ax = 500, 762
    state(ix, iy, "IDLE", "шатл вимкнено", MUTED)
    state(ax, iy, "ACTIVE", "шатл переносить", FIELD)

    # gate -> IDLE
    f.append(arrow(gx + gw, gy + 42, ix - 72, iy - 8, color=NEG, sw=1.8))
    f.append(text((gx + gw + ix - 72) / 2 + 4, gy + 26, "відкрито", size=10, bold=True, color=NEG))

    # IDLE -> ACTIVE (верхня дуга)
    f.append('<path d="M %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="2" '
             'marker-end="url(#arrow)"/>' % (ix + 72, iy - 18, (ix + ax) / 2, iy - 80,
                                             ax - 72, iy - 18, POS))
    f.append(text((ix + ax) / 2, iy - 76, "розкид > V_старт = 20 мВ", size=10.5, bold=True, color=POS))

    # ACTIVE -> IDLE (нижня дуга)
    f.append('<path d="M %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="2" '
             'marker-end="url(#arrow)"/>' % (ax - 72, iy + 18, (ix + ax) / 2, iy + 80,
                                             ix + 72, iy + 18, NEG))
    f.append(text((ix + ax) / 2, iy + 94, "розкид < V_стоп = 8 мВ  (гістерезис)", size=10.5, bold=True, color=NEG))

    # самопетля ACTIVE — переприцілитись
    f.append('<path d="M %d %d C %d %d %d %d %d %d" fill="none" stroke="%s" stroke-width="1.7" '
             'marker-end="url(#arrow)"/>' % (ax + 42, iy - 30, ax + 104, iy - 70,
                                             ax + 104, iy + 4, ax + 62, iy - 4, INK))
    f.append(mtext(ax + 18, iy - 92, "крайня комірка змінилась →\nstop · мертвий час · start",
                   size=9.5, color=INK, anchor="start"))

    b, _, _ = textbox(W / 2, 410,
                      "V_стоп < V_старт: гістерезисна смуга не дає торохтіти на межі; будь-яке переприцілювання йде тільки через розмикання",
                      size=11, fill=GRNBG, stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "balance-fsm.svg"), W, H, *f)


if __name__ == "__main__":
    fig_window_shrink()
    fig_top_balance_ocv()
    fig_passive_circuit()
    fig_active_topologies()
    fig_balance_effective_current()
    fig_balance_convergence()
    fig_balance_crossover()
    fig_crossbar_shuttle()
    fig_balance_fsm()
    print("OK: 9 figures ->", IMG)
