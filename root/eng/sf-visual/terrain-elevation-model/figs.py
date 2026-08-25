# -*- coding: utf-8 -*-
"""Фігури до теми «Цифрова модель рельєфу і профіль висот»."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)

WARM = "#fdecea"   # тепле виділення
COOL = "#eaf0fd"   # холодне виділення
SOFT = "#eef7ee"   # м'яке зелене


def poly(pts, color=INK, sw=2.0, dash=None):
    s = " ".join("%.1f,%.1f" % (x, y) for (x, y) in pts)
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<polyline points="%s" fill="none" stroke="%s" '
            'stroke-width="%.1f"%s/>' % (s, color, sw, d))


def vspan(x, y1, y2, color=INK, sw=1.8):
    """Двобічна вертикальна стрілка між y1 і y2."""
    ym = (y1 + y2) / 2.0
    return arrow(x, ym, x, y1, color=color, sw=sw) + arrow(x, ym, x, y2, color=color, sw=sw)


# ── 1. Чотири поверхні й чотири «висоти» ────────────────────────────────────
def heights():
    W, H = 1040, 570
    p = []
    XL, XR = 80, 820           # межі малюнка поверхонь
    Y_ELL, Y_GEO, Y_AIR = 470, 400, 140

    # апарат: пунктирний рівень і позначка
    p.append(line(XL, Y_AIR, XR, Y_AIR, color=MUTED, sw=1.2, dash="6,5"))
    p.append(circle(560, Y_AIR, 9, fill=WARM, stroke=POS, sw=2))

    # еліпсоїд — пряма
    p.append(line(XL, Y_ELL, XR, Y_ELL, color=NEG, sw=2.4))

    # геоїд — плавна хвиля навколо Y_GEO
    geo = [(XL + i * (XR - XL) / 60.0,
            Y_GEO + 16 * math.sin(i / 60.0 * 3.4) + 6 * math.sin(i / 60.0 * 8.1))
           for i in range(61)]
    p.append(poly(geo, color=FIELD, sw=2.4))

    # тверда земля — ламана над геоїдом
    ter = [(80, 372), (150, 356), (215, 334), (280, 348), (345, 318),
           (410, 300), (470, 322), (520, 296), (575, 330), (640, 312),
           (700, 336), (760, 318), (820, 330)]
    p.append(poly(ter, color=INK, sw=2.6))

    # чотири вертикальні виміри
    p.append(vspan(175, Y_ELL - 3, Y_AIR + 3, color=NEG))
    p.append(vspan(330, Y_ELL - 3, 404, color=FIELD))
    p.append(vspan(490, 396, Y_AIR + 3, color=POS))
    p.append(vspan(660, 330, Y_AIR + 3, color=INK))

    # підписи вимірів — угорі (порожня смуга) і внизу під еліпсоїдом
    p.append(fitbox(95, 78, 165, 38, "над еліпсоїдом", size=14, pad=6,
                    fill=BG, stroke=NEG, sw=1.6, bold=True))
    p.append(fitbox(400, 78, 185, 38, "над рівнем моря", size=14, pad=6,
                    fill=BG, stroke=POS, sw=1.6, bold=True))
    p.append(fitbox(600, 78, 150, 38, "над землею", size=14, pad=6,
                    fill=BG, stroke=INK, sw=1.6, bold=True))
    p.append(fitbox(238, 500, 190, 38, "ундуляція N", size=14, pad=6,
                    fill=BG, stroke=FIELD, sw=1.6, bold=True))

    # назви поверхонь — окрема колонка праворуч, лінії туди не доходять
    p.append(fitbox(840, Y_AIR - 19, 185, 38, "апарат", size=13, pad=6, fill=WARM, sw=1.4))
    p.append(fitbox(840, 311, 185, 38, "тверда земля", size=13, pad=6, fill=FILL, sw=1.4))
    p.append(fitbox(840, 381, 185, 38, "геоїд: рівень моря", size=13, pad=6, fill=SOFT, sw=1.4))
    p.append(fitbox(840, Y_ELL - 19, 185, 38, "еліпсоїд WGS-84", size=13, pad=6, fill=COOL, sw=1.4))

    p.append(text(W / 2, 548,
                  "модель рельєфу дає рівень твердої поверхні — без неї висота апарата ще не є висотою над землею",
                  size=13, color=MUTED))
    render(os.path.join(IMG, 'heights.svg'), W, H, *p,
           title="Одне слово «висота» — чотири різні відрізки")


# ── 2. Комірка сітки: ваги білінійної суміші й що між вузлами ───────────────
def grid_cell():
    W, H = 1040, 530
    p = []

    # ЛІВА ПАНЕЛЬ: комірка, поділена точкою на чотири прямокутники
    CX, CY, S = 90, 130, 280
    ux, vy = 175.0, 105.0                      # u = 0.625, v = 0.375
    p.append(text(230, 94, "комірка сітки: ваги суміші", size=15, bold=True))

    p.append(rect(CX,      CY,      ux,     vy,     fill=COOL, sw=1.2, rx=2))
    p.append(rect(CX + ux, CY,      S - ux, vy,     fill=BG,   sw=1.2, rx=2))
    p.append(rect(CX,      CY + vy, ux,     S - vy, fill=BG,   sw=1.2, rx=2))
    p.append(rect(CX + ux, CY + vy, S - ux, S - vy, fill=WARM, sw=1.2, rx=2))

    p.append(fitbox(CX + 12,      CY + 26,      ux - 24,     vy - 52,
                    "0.23 → h₁₁", size=13, pad=4, fill=BG, sw=0))
    p.append(fitbox(CX + ux + 10, CY + 26,      S - ux - 20, vy - 52,
                    "0.14 → h₀₁", size=13, pad=4, fill=BG, sw=0))
    p.append(fitbox(CX + 12,      CY + vy + 52, ux - 24,     S - vy - 104,
                    "0.39 → h₁₀", size=13, pad=4, fill=BG, sw=0))
    p.append(fitbox(CX + ux + 10, CY + vy + 52, S - ux - 20, S - vy - 104,
                    "0.23 → h₀₀", size=13, pad=4, fill=BG, sw=0))

    p.append(circle(CX + ux, CY + vy, 7, fill=POS, stroke=POS, sw=1.5))

    p.append(text(CX,     CY - 12, "h₀₀ = 312", size=13))
    p.append(text(CX + S, CY - 12, "h₁₀ = 318", size=13))
    p.append(text(CX,     CY + S + 24, "h₀₁ = 341", size=13))
    p.append(text(CX + S, CY + S + 24, "h₁₁ = 335", size=13))

    p.append(mtext(230, 462, ["u = 0.625, v = 0.375  →  h = 323.8 м",
                              "вага кута = площа протилежного прямокутника"],
                   size=12, color=MUTED))

    # ПРАВА ПАНЕЛЬ: переріз між двома вузлами
    p.append(text(780, 94, "переріз між двома вузлами", size=15, bold=True))
    NA, NB = (620, 330), (940, 330)
    p.append(poly([NA, (700, 300), (780, 262), (860, 300), NB], color=INK, sw=2.6))
    p.append(line(NA[0], NA[1], NB[0], NB[1], color=POS, sw=2.2, dash="7,5"))
    p.append(circle(NA[0], NA[1], 6, fill=BG, stroke=INK, sw=2))
    p.append(circle(NB[0], NB[1], 6, fill=BG, stroke=INK, sw=2))
    p.append(vspan(780, 266, 326, color=FIELD))

    p.append(fitbox(650, 196, 260, 40, "справжній гребінь +6 м", size=13, pad=6,
                    fill=SOFT, sw=1.5, bold=True))
    p.append(text(620, 362, "вузол", size=12, color=MUTED))
    p.append(text(940, 362, "вузол", size=12, color=MUTED))
    p.append(text(780, 362, "реконструкція — хорда між вузлами", size=12, color=POS))

    p.append(mtext(780, 462, ["крок сітки 30 м, нахил схилу 40 %:",
                              "цих шести метрів у даних немає взагалі"],
                   size=12, color=MUTED))

    p.append(text(W / 2, 508,
                  "чотири ваги невід'ємні й дають одиницю — тому суміш ніколи не виходить за межі кутових висот",
                  size=13, color=MUTED))
    render(os.path.join(IMG, 'grid-cell.svg'), W, H, *p,
           title="Між вузлами висоту не виміряно, а обчислено")


# ── 3. Згортка блоку: середнє, максимум, мінімум ────────────────────────────
def reduce_op():
    W, H = 1010, 640
    p = []

    # блок 2×2
    p.append(text(170, 92, "блок 2×2 сусідніх комірок, м", size=14, bold=True))
    vals = [("210", 78, 108), ("215", 170, 108), ("380", 78, 200), ("205", 170, 200)]
    for s, x, y in vals:
        col = WARM if s == "380" else BG
        p.append(fitbox(x, y, 92, 92, s, size=20, pad=8, fill=col, sw=1.6, bold=True))

    boxes = [
        (108, ["середнє 252.5", "такої висоти немає в жодній комірці — відповідь ні на що"], FILL),
        (196, ["максимум 380", "точна верхня межа: «чи є вище за X» вирішують без спуску"], WARM),
        (284, ["мінімум 205", "точна нижня межа: потрібна для стоку води й затоплення"], COOL),
    ]
    for y, lines, col in boxes:
        p.append(fitbox(330, y, 620, 76, lines, size=14, pad=10, fill=col, sw=1.6))
    for ys, ye in ((155, 146), (200, 234), (245, 322)):
        p.append(arrow(266, ys, 322, ye))

    # піраміда максимумів як прискорювач запиту
    p.append(fitbox(280, 384, 450, 40, "запит: чи є на ділянці рельєф вище за 300 м?",
                    size=14, pad=8, fill=BG, sw=1.6, bold=True))
    p.append(fitbox(390, 452, 230, 44, "грубий рівень: max = 380", size=14, pad=8,
                    fill=FILL, sw=1.6))
    p.append(arrow(505, 424, 505, 448))
    p.append(arrow(460, 498, 300, 528))
    p.append(arrow(550, 498, 710, 528))
    p.append(fitbox(150, 532, 300, 44, "блок A: max = 215", size=14, pad=8, fill=SOFT, sw=1.6))
    p.append(fitbox(560, 532, 300, 44, "блок B: max = 380", size=14, pad=8, fill=WARM, sw=1.6))
    p.append(text(300, 600, "нижче за 300 — відкинуто цілком", size=13, color=MUTED))
    p.append(text(710, 600, "може перевищувати — спускаємось", size=13, color=MUTED))

    render(os.path.join(IMG, 'reduce.svg'), W, H, *p,
           title="Оператор згортки має відповідати питанню")


# ── 4. Пряма видимість і здуття Землі ───────────────────────────────────────
def line_of_sight():
    W, H = 1040, 550
    p = []
    XA, XB = 120, 920
    Y_LOS = 300

    # легенда вгорі, у порожній смузі
    p.append(fitbox(58, 62, 322, 38, "пряма між антенами (плоска перевірка)",
                    size=13, pad=6, fill=BG, stroke=POS, sw=1.8))
    p.append(fitbox(398, 62, 302, 38, "лінія з поправкою на кривину",
                    size=13, pad=6, fill=BG, stroke=NEG, sw=1.8))
    p.append(fitbox(718, 62, 262, 38, "рельєф із профілю",
                    size=13, pad=6, fill=BG, stroke=INK, sw=1.8))

    # рельєф
    ter = [(XA, 430), (260, 418), (390, 388), (520, 360), (660, 383),
           (800, 405), (XB, 435)]
    p.append(poly(ter, color=INK, sw=2.6))

    # щогли
    p.append(line(XA, 430, XA, Y_LOS, color=MUTED, sw=2.4))
    p.append(line(XB, 435, XB, Y_LOS, color=MUTED, sw=2.4))
    p.append(circle(XA, Y_LOS, 6, fill=WARM, stroke=POS, sw=2))
    p.append(circle(XB, Y_LOS, 6, fill=WARM, stroke=POS, sw=2))
    p.append(text(XA, 278, "A", size=15, bold=True))
    p.append(text(XB, 278, "B", size=15, bold=True))

    # пряма й виправлена лінія
    p.append(line(XA, Y_LOS, XB, Y_LOS, color=POS, sw=2.4))
    sag = [(XA + i * (XB - XA) / 40.0,
            Y_LOS + 95 * (1 - ((XA + i * (XB - XA) / 40.0 - 520) / 400.0) ** 2))
           for i in range(41)]
    p.append(poly(sag, color=NEG, sw=2.4, dash="8,5"))

    # вимір здуття
    p.append(vspan(520, Y_LOS + 4, 391, color=NEG))
    p.append(fitbox(608, 314, 112, 34, "b = 36.8 м", size=13, pad=5,
                    fill=BG, stroke=NEG, sw=1.5))

    p.append(fitbox(320, 466, 400, 40,
                    "гребінь нижчий за пряму, але вищий за виправлену лінію",
                    size=13, pad=8, fill=SOFT, sw=1.6))

    p.append(text(W / 2, 528,
                  "траса 50 км: здуття посередині 49 м геометрично і 36.8 м для радіо з коефіцієнтом 4/3",
                  size=13, color=MUTED))
    render(os.path.join(IMG, 'line-of-sight.svg'), W, H, *p,
           title="Плоска перевірка видимости пропускає кривину Землі")


def legend_row(x, y, color, label, dash=None, sw=2.4, marker=False):
    """Рядок легенди: зразок лінії ліворуч, підпис праворуч."""
    s = line(x, y, x + 46, y, color=color, sw=sw, dash=dash)
    if marker:
        s += circle(x + 23, y, 6, fill=WARM, stroke=POS, sw=2)
    s += text(x + 58, y + 5, label, size=13, anchor="start")
    return s


# ── 5. Білінійна комірка: сідло, ізолінії, перерізи по діагоналях ───────────
def bilinear_saddle():
    """Комірка h00=100, h10=112, h01=112, h11=100 → D = −24, центр 106."""
    W, H = 1120, 620
    p = []

    # ── лівий план ─────────────────────────────────────────────────────────
    X0, Y0, S = 90, 110, 300
    CX, CY = X0 + S / 2.0, Y0 + S / 2.0
    p.append(text(CX, 72, "план комірки: ізолінії", size=15, bold=True))
    p.append(rect(X0, Y0, S, S, fill=BG, stroke=LINE, sw=2.0, rx=0))

    # вироджена ізолінія 106 — хрест через сідлову точку
    p.append(line(X0, CY, X0 + S, CY, color=FIELD, sw=2.0))
    p.append(line(CX, Y0, CX, Y0 + S, color=FIELD, sw=2.0))

    def hyper(c, color):
        """Дві вітки ū·v̄ = c у координатах комірки (ū, v̄ ∈ [−0.5, 0.5])."""
        a = abs(c)
        if a < 1e-9:
            return ""
        lo, hi = 2 * a, 0.5
        pts = []
        for i in range(41):
            uu = lo + (hi - lo) * i / 40.0
            vv = c / uu
            pts.append((CX + S * uu, CY - S * vv))
        mir = [(2 * CX - x, 2 * CY - y) for (x, y) in pts]
        return poly(pts, color=color, sw=2.0) + poly(mir, color=color, sw=2.0)

    for z in (102, 104, 108, 110):
        p.append(hyper((106.0 - z) / 24.0, NEG if z < 106 else POS))

    # кути й центр
    for (cx, cy, val) in ((X0, Y0 + S, "100"), (X0 + S, Y0 + S, "112"),
                          (X0, Y0, "112"), (X0 + S, Y0, "100")):
        p.append(circle(cx, cy, 7, fill=WARM, stroke=POS, sw=2))
    p.append(circle(CX, CY, 7, fill=SOFT, stroke=FIELD, sw=2))

    p.append(text(X0 - 4, 444, "h₀₀ = 100", size=13, anchor="start"))
    p.append(text(X0 + S + 4, 444, "h₁₀ = 112", size=13, anchor="end"))
    p.append(text(X0 - 4, 92, "h₀₁ = 112", size=13, anchor="start"))
    p.append(text(X0 + S + 4, 92, "h₁₁ = 100", size=13, anchor="end"))
    p.append(text(CX, 444, "u →", size=13, color=MUTED))
    p.append(text(X0 - 22, 264, "v ↑", size=13, color=MUTED, anchor="end"))
    p.append(text(CX + 28, 244, "106 м", size=13, color=FIELD, anchor="start"))

    p.append(mtext(X0, 484, ["ізолінії 102 · 104 · 108 · 110 м — дуги гіпербол,",
                             "асимптоти паралельні осям сітки; 106 м — хрест"],
                   size=13, color=MUTED, anchor="start"))

    # ── правий переріз ─────────────────────────────────────────────────────
    PX0, PX1, PY0, PY1 = 640, 1040, 130, 430
    p.append(text((PX0 + PX1) / 2.0, 72, "перерізи по діагоналях", size=15, bold=True))
    p.append(line(PX0 - 20, PY1, PX1 + 20, PY1, color=MUTED, sw=1.5))
    p.append(line(PX0 - 20, PY0, PX0 - 20, PY1, color=MUTED, sw=1.5))

    def zy(z):
        return PY1 - (z - 98.0) * 18.75

    def tx(t):
        return PX0 + (PX1 - PX0) * t

    main = [(tx(i / 40.0), zy(100 + 24 * (i / 40.0) - 24 * (i / 40.0) ** 2)) for i in range(41)]
    anti = [(tx(i / 40.0), zy(112 - 24 * (i / 40.0) + 24 * (i / 40.0) ** 2)) for i in range(41)]
    p.append(line(PX0, zy(100), PX1, zy(100), color=MUTED, sw=1.6, dash="7,5"))
    p.append(line(PX0, zy(112), PX1, zy(112), color=MUTED, sw=1.6, dash="7,5"))
    p.append(poly(main, color=NEG, sw=2.6))
    p.append(poly(anti, color=POS, sw=2.6))

    p.append(vspan(tx(0.5), zy(100) - 3, zy(106) + 3, color=NEG))
    p.append(vspan(tx(0.5), zy(112) + 3, zy(106) - 3, color=POS))
    p.append(fitbox(675, 320, 130, 40, "|D|/4 = 6 м", size=13, pad=6, fill=BG, stroke=NEG, sw=1.5))
    p.append(fitbox(885, 195, 130, 40, "|D|/4 = 6 м", size=13, pad=6, fill=BG, stroke=POS, sw=1.5))

    p.append(text(PX0 - 30, zy(100) + 5, "100", size=13, color=MUTED, anchor="end"))
    p.append(text(PX0 - 30, zy(106) + 5, "106", size=13, color=MUTED, anchor="end"))
    p.append(text(PX0 - 30, zy(112) + 5, "112", size=13, color=MUTED, anchor="end"))
    p.append(text(PX0, PY1 + 24, "t = 0", size=13, color=MUTED))
    p.append(text(PX1, PY1 + 24, "t = 1", size=13, color=MUTED))

    p.append(legend_row(PX0 - 20, 484, NEG, "по діагоналі 00 → 11: парабола вгору"))
    p.append(legend_row(PX0 - 20, 512, POS, "по діагоналі 10 → 01: парабола вниз"))
    p.append(legend_row(PX0 - 20, 540, MUTED, "хорди між кінцями діагоналей", dash="7,5", sw=1.6))

    render(os.path.join(IMG, 'bilinear-saddle.svg'), W, H, *p,
           title="Білінійна комірка — шматок гіперболічного параболоїда")


# ── 6. Стрибок нахилу на межі комірок ───────────────────────────────────────
def slope_jump():
    W, H = 1060, 560
    p = []
    XA, XB, XC = 190, 530, 870
    YLO, YHI = 400, 220

    p.append(line(120, 462, 940, 462, color=MUTED, sw=1.5))
    for (x, lbl) in ((XA, "0 м"), (XB, "30 м"), (XC, "60 м")):
        p.append(line(x, 462, x, 470, color=MUTED, sw=1.5))
        p.append(text(x, 492, lbl, size=13, color=MUTED))

    p.append(line(XA, YLO, XA, 455, color=MUTED, sw=1.2, dash="5,5"))
    p.append(line(XB, YHI, XB, 455, color=MUTED, sw=1.2, dash="5,5"))
    p.append(line(XC, YLO, XC, 455, color=MUTED, sw=1.2, dash="5,5"))

    p.append(poly([(XA, YLO), (XB, YHI), (XC, YLO)], color=INK, sw=3.0))

    # трикутники нахилу
    def seg_y(x):
        return YLO - (YLO - YHI) * (x - XA) / float(XB - XA) if x <= XB \
            else YHI + (YLO - YHI) * (x - XB) / float(XC - XB)

    p.append(poly([(300, seg_y(300)), (410, seg_y(300)), (410, seg_y(410))], color=NEG, sw=1.8, dash="6,4"))
    p.append(text(355, seg_y(300) + 22, "+0.40", size=13, color=NEG))
    p.append(poly([(650, seg_y(650)), (760, seg_y(650)), (760, seg_y(760))], color=NEG, sw=1.8, dash="6,4"))
    p.append(text(705, seg_y(650) - 12, "−0.40", size=13, color=NEG))

    # нормалі обабіч вузла
    p.append(arrow(XB, YHI, XB - 42.1, YHI - 79.5, color=POS, sw=2.2))
    p.append(arrow(XB, YHI, XB + 42.1, YHI - 79.5, color=POS, sw=2.2))
    p.append(text(XB, 112, "нормалі розходяться на 43.6°", size=13, color=POS))

    for (x, y, val) in ((XA, YLO, "100"), (XB, YHI, "112"), (XC, YLO, "100")):
        p.append(circle(x, y, 8, fill=WARM, stroke=POS, sw=2.2))
    p.append(text(XA - 20, YLO + 6, "100 м", size=13, anchor="end"))
    p.append(text(XC + 20, YLO + 6, "100 м", size=13, anchor="start"))
    p.append(text(XB + 26, YHI + 34, "112 м", size=13, anchor="start"))

    p.append(fitbox(50, 150, 380, 106,
                    "нахил ліворуч   (112 − 100)/30 = +0.400\n"
                    "нахил праворуч  (100 − 112)/30 = −0.400\n"
                    "стрибок  (100 − 2·112 + 100)/30 = −0.800",
                    size=13, pad=10, fill=COOL, stroke=NEG, sw=1.6))

    p.append(text(W / 2.0, 528,
                  "висота у вузлі та сама з обох боків — розривається лише нахил",
                  size=13, color=MUTED))
    render(os.path.join(IMG, 'slope-jump.svg'), W, H, *p,
           title="C⁰, але не C¹: злам рівно на межі комірок")


# ── 7. Аліасинг на сітці: 25 метрів читаються як 150 ─────────────────────────
def alias_grid():
    W, H = 1120, 580
    p = []
    X0, X1 = 90, 1010
    YC, AMP = 300.0, 90.0
    sx = (X1 - X0) / 300.0

    p.append(line(X0 - 10, YC, X1 + 10, YC, color=MUTED, sw=1.2, dash="5,5"))

    true_w = [(X0 + x * sx, YC - AMP * math.sin(2 * math.pi * x / 25.0))
              for x in [i * 0.5 for i in range(601)]]
    p.append(poly(true_w, color=MUTED, sw=1.4))

    alias_w = [(X0 + x * sx, YC - AMP * math.sin(2 * math.pi * x / 150.0))
               for x in [i * 0.5 for i in range(601)]]
    p.append(poly(alias_w, color=NEG, sw=2.4, dash="9,6"))

    nodes = [(X0 + 30.0 * n * sx, YC - AMP * math.sin(0.4 * math.pi * n)) for n in range(11)]
    p.append(poly(nodes, color=POS, sw=2.6))
    for (x, y) in nodes:
        p.append(circle(x, y, 6, fill=WARM, stroke=POS, sw=2))

    p.append(line(X0 - 10, 424, X1 + 10, 424, color=MUTED, sw=1.5))
    for m in (0, 60, 120, 180, 240, 300):
        x = X0 + m * sx
        p.append(line(x, 424, x, 432, color=MUTED, sw=1.5))
        p.append(text(x, 452, "%d" % m, size=12, color=MUTED))
    p.append(text(X1 + 10, 452, "м", size=12, color=MUTED, anchor="start"))

    p.append(fitbox(700, 62, 380, 66,
                    "1/25 − 1/30 = 1/150\n"
                    "фаза за крок: 2.4π ≡ 0.4π (mod 2π)",
                    size=13, pad=8, fill=COOL, stroke=NEG, sw=1.6))

    p.append(legend_row(X0, 490, MUTED, "справжня форма: хвиля завдовжки 25 м", sw=1.4))
    p.append(legend_row(X0, 518, POS, "вузли через 30 м і реконструкція між ними", marker=True))
    p.append(legend_row(X0, 546, NEG, "що читається з моделі: хвиля 150 м, амплітуда та сама",
                        dash="9,6"))

    render(os.path.join(IMG, 'alias-grid.svg'), W, H, *p,
           title="Форма, коротша за подвоєний крок, виходить із сітки чужою")


# ── 8. Геометрія однопрохідної інтерферометрії (вставка hist-srtm) ──────────
def insar_geometry():
    W, H = 1060, 600
    p = []
    A1 = (330.0, 118.0)
    A2 = (630.0, 118.0)
    P = (870.0, 452.0)

    # апарат і щогла
    p.append(fitbox(140, 96, 170, 46, "Endeavour\nорбіта ≈ 233 км", size=13, fill=COOL))
    p.append(line(A1[0], A1[1], A2[0], A2[1], color=INK, sw=5))
    p.append(fitbox(400, 52, 250, 34, "щогла: база B = 60 м", size=14, fill=BG, stroke=INK))
    p.append(circle(A1[0], A1[1], 9, fill=WARM, stroke=POS, sw=2))
    p.append(circle(A2[0], A2[1], 9, fill=COOL, stroke=NEG, sw=2))
    p.append(text(A1[0] - 26, 154, "A₁", size=14, color=POS, bold=True))
    p.append(text(A2[0] - 26, 154, "A₂", size=14, color=NEG, bold=True))

    # промені до точки на поверхні
    p.append(line(A1[0], A1[1], P[0], P[1], color=POS, sw=2.0))
    p.append(line(A2[0], A2[1], P[0], P[1], color=NEG, sw=2.0))
    p.append(fitbox(475, 285, 92, 32, "r₁", size=15, fill=BG, stroke=POS, sw=1.6))
    p.append(fitbox(805, 285, 92, 32, "r₂", size=15, fill=BG, stroke=NEG, sw=1.6))

    # поверхня
    ter = [(100, 478), (200, 470), (300, 482), (400, 466), (500, 480),
           (600, 470), (700, 486), (790, 470), (870, 452), (950, 474), (1010, 480)]
    p.append(poly(ter, color=INK, sw=2.6))
    p.append(circle(P[0], P[1], 7, fill=SOFT, stroke=FIELD, sw=2))
    p.append(fitbox(788, 500, 224, 34, "точка на поверхні", size=13, fill=SOFT, stroke=FIELD))

    p.append(fitbox(80, 240, 310, 118,
                    "Δr = r₁ − r₂\nΔφ = 2π · Δr / λ\nλ = 5.6 см (C-діапазон)",
                    size=15, fill=COOL, stroke=NEG))

    p.append(text(W / 2.0, 568,
                  "різниця ходу дає кут візування, кут разом із відстанню — висоту",
                  size=13, color=MUTED))
    render(os.path.join(IMG, 'insar-geometry.svg'), W, H, *p,
           title="Дві антени, рознесені на 60 метрів, бачать точку під різними кутами")


# ── 9. Чому виходить модель поверхні, а не землі (вставка hist-srtm) ────────
def surface_not_ground():
    W, H = 1020, 470
    p = []
    GY = 320.0

    p.append(text(275, 50, "ліс", size=15, bold=True))
    p.append(text(760, 50, "місто", size=15, bold=True))

    # ── ліс ────────────────────────────────────────────────────────────────
    for cx in (170, 235, 300, 365, 430):
        p.append(line(cx, 282, cx, GY, color=INK, sw=3))
    for cx in (170, 235, 300, 365, 430):
        p.append(circle(cx, 250, 32, fill=SOFT, stroke=FIELD, sw=1.8))

    p.append(line(145, 216, 480, 216, color=FIELD, sw=1.8, dash="7,5"))
    p.append(line(145, 250, 480, 250, color=POS, sw=2.2, dash="7,5"))
    p.append(line(145, GY, 480, GY, color=INK, sw=2.6))

    p.append(fitbox(50, 201, 90, 30, "верх крон", size=11, fill=BG, stroke=FIELD))
    p.append(fitbox(50, 235, 90, 30, "звідки йде\nсигнал", size=11, fill=BG, stroke=POS))
    p.append(fitbox(50, 306, 90, 28, "земля", size=11, fill=BG, stroke=INK))

    p.append(arrow(150, 90, 214, 200, color=MUTED, sw=1.8))
    p.append(arrow(250, 88, 314, 200, color=MUTED, sw=1.8))

    # ── місто ──────────────────────────────────────────────────────────────
    blds = [(570, 238, 66), (650, 196, 74), (738, 252, 58), (812, 214, 84), (908, 262, 52)]
    for (bx, by, bw) in blds:
        p.append(rect(bx, by, bw, GY - by, fill=FILL, stroke=INK, sw=1.8, rx=2))
        p.append(line(bx, by, bx + bw, by, color=POS, sw=3.4))
    p.append(line(550, GY, 970, GY, color=INK, sw=2.6))

    p.append(arrow(600, 92, 664, 186, color=MUTED, sw=1.8))
    p.append(arrow(700, 90, 764, 186, color=MUTED, sw=1.8))

    p.append(fitbox(50, 348, 430, 52,
                    "сигнал вертається з крон,\nа не з ґрунту під ними", size=13, fill=COOL))
    p.append(fitbox(550, 348, 420, 52,
                    "сигнал вертається з дахів,\nвулиця лишається невидимою", size=13, fill=COOL))

    p.append(text(W / 2.0, 432,
                  "хвиля 5.6 см не проходить крізь крони й дахи — виходить модель поверхні",
                  size=13, color=MUTED))
    render(os.path.join(IMG, 'surface-not-ground.svg'), W, H, *p,
           title="Радар міряє верх того, що стоїть на землі")


# ── 10. Родовід глобальних наборів висот (вставка hist-srtm) ───────────────
def dem_timeline():
    W, H = 1060, 610
    p = []
    AX = 530.0

    p.append(text(262, 62, "лінія SRTM", size=15, bold=True, color=NEG))
    p.append(text(798, 62, "інші джерела", size=15, bold=True, color=FIELD))
    p.append(line(AX, 78, AX, 570, color=MUTED, sw=2.0))

    rows = [
        (104, "2000", "L", "лютий: 11 днів радарної зйомки"),
        (158, "2003", "L", "3″ (90 м) світові, 1″ (30 м) — США"),
        (212, "2009", "R", "ASTER GDEM v1 — стерео з Terra"),
        (266, "2010", "R", "запуск TanDEM-X: база між супутниками"),
        (320, "2011", "L", "травень: X-діапазон DLR/ASI — смугами"),
        (374, "2013", "L", "SRTM v3: прогалини залатано чужим"),
        (428, "2014", "L", "вересень: 1″ відкрито світові"),
        (482, "2019", "R", "Copernicus DEM GLO-30: краще за 4 м"),
        (536, "2020", "L", "NASADEM: сирі дані переоброблено"),
    ]
    for (cy, year, side, label) in rows:
        if side == "L":
            p.append(fitbox(64, cy - 22, 396, 44, label, size=13, fill=COOL, stroke=NEG))
            p.append(line(460, cy, AX - 48, cy, color=MUTED, sw=1.4))
        else:
            p.append(fitbox(600, cy - 22, 396, 44, label, size=13, fill=SOFT, stroke=FIELD))
            p.append(line(AX + 48, cy, 600, cy, color=MUTED, sw=1.4))
        p.append(fitbox(AX - 48, cy - 16, 96, 32, year, size=14, fill=BG, stroke=INK, bold=True))

    p.append(text(W / 2.0, 592,
                  "одні виміри 2000 року відкривали двадцять років — і паралельно шукали їм заміну",
                  size=13, color=MUTED))
    render(os.path.join(IMG, 'dem-timeline.svg'), W, H, *p,
           title="Родовід вільних глобальних моделей рельєфу")


# ── Хід сіткою і квадратний тричлен усередині комірки (proj-terrain-profile) ─
def grid_walk():
    W, H = 1080, 640
    p = []

    # ЛІВА ПАНЕЛЬ: покомірний хід відрізком
    X0, Y0, CS, NC, NR = 66, 118, 64, 6, 5
    p.append(text(X0 + NC * CS / 2.0, 100,
                  "хід відрізком: кожна комірка рівно один раз", size=15, bold=True))

    ax, ay = 0.30, 4.55          # початок відрізка в координатах комірок
    bx, by = 5.75, 0.35          # кінець

    def walk(x0, y0, x1, y1):
        """Той самий хід, що й у коді вставки."""
        dx, dy = x1 - x0, y1 - y0
        i, j = int(math.floor(x0)), int(math.floor(y0))
        ie, je = int(math.floor(x1)), int(math.floor(y1))
        si = 1 if dx > 0 else (-1 if dx < 0 else 0)
        sj = 1 if dy > 0 else (-1 if dy < 0 else 0)
        INF = float('inf')
        tdx = abs(1.0 / dx) if si else INF
        tdy = abs(1.0 / dy) if sj else INF
        tmx = ((i + 1 - x0) / dx) if si > 0 else (((i - x0) / dx) if si < 0 else INF)
        tmy = ((j + 1 - y0) / dy) if sj > 0 else (((j - y0) / dy) if sj < 0 else INF)
        steps = abs(ie - i) + abs(je - j)
        out, t = [], 0.0
        for k in range(steps + 1):
            tn = 1.0 if k == steps else min(tmx, tmy, 1.0)
            out.append((i, j, t))
            if tn >= 1.0:
                break
            t = tn
            if tmx < tmy:
                i += si
                tmx += tdx
            else:
                j += sj
                tmy += tdy
        return out

    hits = walk(ax, ay, bx, by)
    for (i, j, _t) in hits:
        p.append(rect(X0 + i * CS, Y0 + j * CS, CS, CS, fill=WARM, stroke=BG, sw=0, rx=0))
    for c in range(NC + 1):
        p.append(line(X0 + c * CS, Y0, X0 + c * CS, Y0 + NR * CS, color=MUTED, sw=1.0))
    for r in range(NR + 1):
        p.append(line(X0, Y0 + r * CS, X0 + NC * CS, Y0 + r * CS, color=MUTED, sw=1.0))

    p.append(line(X0 + ax * CS, Y0 + ay * CS, X0 + bx * CS, Y0 + by * CS, color=INK, sw=2.6))
    for (_i, _j, t) in hits[1:]:
        p.append(circle(X0 + (ax + (bx - ax) * t) * CS,
                        Y0 + (ay + (by - ay) * t) * CS, 4.5, fill=POS, stroke=POS, sw=1.2))
    p.append(circle(X0 + ax * CS, Y0 + ay * CS, 6.5, fill=BG, stroke=INK, sw=2))
    p.append(circle(X0 + bx * CS, Y0 + by * CS, 6.5, fill=BG, stroke=INK, sw=2))

    p.append(fitbox(56, 458, 404, 92,
                    ["крок ходу: порівняти t до найближчої вертикалі",
                     "з t до найближчої горизонталі — і крокнути туди,",
                     "де воно менше; жодної комірки не пропущено",
                     "і жодної не відвідано двічі"],
                    size=13, pad=10, fill=COOL, sw=1.5))

    # ПРАВА ПАНЕЛЬ: висота вздовж відрізка всередині однієї комірки
    PX, PY, PW, PH = 630, 150, 380, 240
    A, B, C = -42.0, 46.0, 1840.0
    HLO, HHI = 1834.0, 1858.0

    def hy(h):
        return PY + PH * (HHI - h) / (HHI - HLO)

    def hx(t):
        return PX + PW * t

    p.append(text(PX + PW / 2.0, 100,
                  "усередині комірки висота — квадратний тричлен", size=15, bold=True))
    p.append(rect(PX, PY, PW, PH, fill=BG, stroke=MUTED, sw=1.2, rx=4))
    for h in (1840, 1845, 1850, 1855):
        p.append(line(PX, hy(h), PX + PW, hy(h), color="#e5e7eb", sw=1.0))
        p.append(text(PX - 14, hy(h) + 5, str(h), size=12, color=MUTED, anchor="end"))

    p.append(line(hx(0), hy(C), hx(1), hy(A + B + C), color=POS, sw=2.0, dash="7,5"))
    p.append(poly([(hx(k / 60.0), hy(A * (k / 60.0) ** 2 + B * (k / 60.0) + C))
                   for k in range(61)], color=INK, sw=2.6))

    tv = -B / (2.0 * A)
    hv = A * tv * tv + B * tv + C
    p.append(line(hx(tv), hy(hv), hx(tv), PY + PH, color=FIELD, sw=1.4, dash="5,4"))
    p.append(circle(hx(tv), hy(hv), 6.5, fill=SOFT, stroke=FIELD, sw=2))
    p.append(circle(hx(0), hy(C), 5.5, fill=BG, stroke=INK, sw=2))
    p.append(circle(hx(1), hy(A + B + C), 5.5, fill=BG, stroke=INK, sw=2))

    p.append(text(hx(tv), 138, "максимум 1852.6 м", size=13, color=FIELD, bold=True))
    p.append(arrow(hx(tv), 144, hx(tv), hy(hv) - 9, color=FIELD, sw=1.6))
    p.append(text(644, 352, "вхід 1840", size=12, color=MUTED, anchor="start"))
    p.append(text(998, 272, "вихід 1844", size=12, color=MUTED, anchor="end"))
    p.append(text(hx(tv), 412, "τ = 0.55", size=12, color=FIELD))
    p.append(text(PX + 36, 412, "τ = 0", size=12, color=MUTED))
    p.append(text(PX + PW - 36, 412, "τ = 1", size=12, color=MUTED))

    p.append(fitbox(624, 458, 396, 92,
                    ["кути комірки 1840 · 1852 · 1874 · 1844",
                     "штрихова лінія — оцінка лише за кінцями",
                     "справжній максимум лежить усередині",
                     "перевірка лише кінців губить 8.6 метра"],
                    size=13, pad=10, fill=WARM, sw=1.6))

    p.append(text(W / 2, 604,
                  "хід дає всі комірки, тричлен — точний максимум у кожній; вибіркою не дістати ні того, ні того",
                  size=13, color=MUTED))
    render(os.path.join(IMG, 'grid-walk.svg'), W, H, *p,
           title="Покомірний хід і точний екстремум у комірці")


# ── Глобальна адреса вузла: шва між квадратами не існує ─────────────────────
def tile_seam():
    W, H = 1080, 690
    p = []

    # ЛІВА ПАНЕЛЬ: чотири градусні квадрати
    T, X0, Y0 = 185, 80, 125
    p.append(text(X0 + T, 105, "чотири градусні квадрати", size=15, bold=True))
    names = [(0, 0, "N49E023", COOL), (1, 0, "N49E024", BG),
             (0, 1, "N48E023", BG),   (1, 1, "N48E024", COOL)]
    for (cx, cy, nm, col) in names:
        x, y = X0 + cx * T, Y0 + cy * T
        p.append(rect(x, y, T, T, fill=col, stroke=LINE, sw=1.6, rx=2))
        p.append(fitbox(x + T / 2 - 68, y + T / 2 - 18, 136, 36, nm,
                        size=13, pad=4, fill=BG, sw=1.2))
    p.append(line(X0 + T, Y0, X0 + T, Y0 + 2 * T, color=POS, sw=2.6))
    p.append(line(X0, Y0 + T, X0 + 2 * T, Y0 + T, color=POS, sw=2.6))
    p.append(line(X0 + 20, Y0 + 2 * T - 24, X0 + 2 * T - 28, Y0 + 26, color=INK, sw=2.6))

    p.append(fitbox(50, 520, 430, 100,
                    ["gi = (λ + 180°) · 3600      gj = (90° − φ) · 3600",
                     "квадрат:  E(gi div 3600 − 180) ,  N(89 − gj div 3600)",
                     "вузол:      col = gi mod 3600 ,  row = gj mod 3600",
                     "адресу вузла рахують ПЕРШОЮ, квадрат — наслідок"],
                    size=13, pad=10, fill=SOFT, sw=1.6))

    # ПРАВА ПАНЕЛЬ: той самий вузол у двох файлах
    p.append(text(770, 105, "той самий вузол у двох файлах", size=15, bold=True))
    TX, TY, HW, CW, RH = 510, 145, 152, 92, 46
    rows = [
        ("gi у світі", ["734398", "734399", "734400", "734401"], FILL),
        ("у N49E023",  ["3598",   "3599",   "3600",   "—"],      BG),
        ("у N49E024",  ["—",      "—",      "0",      "1"],      BG),
        ("код читає",  ["E023",   "E023",   "E024",   "E024"],   SOFT),
    ]
    for r, (head, cells, col) in enumerate(rows):
        y = TY + r * RH
        p.append(fitbox(TX, y, HW, RH, head, size=13, pad=6, fill=FILL, sw=1.2,
                        bold=(r == 0)))
        for c, s in enumerate(cells):
            fill = WARM if (r == 1 and c == 2) else col
            p.append(fitbox(TX + HW + c * CW, y, CW, RH, s, size=13, pad=5,
                            fill=fill, sw=1.2, bold=(r == 0)))
    p.append(text(770, 356, "стовпця 3600 код не читає ніколи — саме тому шва немає",
                  size=12, color=MUTED))

    # комірка на межі: два кути з одного файла, два з іншого
    NY0, NY1 = 402, 480
    for x in (600, 720, 840):
        p.append(line(x, NY0 - 16, x, NY1 + 16, color=MUTED, sw=1.0))
    p.append(rect(720, NY0, 120, NY1 - NY0, fill=WARM, stroke=LINE, sw=1.5, rx=2))
    p.append(line(840, NY0 - 30, 840, NY1 + 30, color=POS, sw=2.4, dash="7,5"))
    for x in (600, 720, 840):
        for y in (NY0, NY1):
            p.append(circle(x, y, 5.5, fill=BG, stroke=INK, sw=2))
    p.append(text(654, NY0 - 30, "N49E023", size=12, color=NEG))
    p.append(text(926, NY0 - 30, "N49E024", size=12, color=POS))
    p.append(text(770, NY1 + 48, "комірка на межі бере кути з ДВОХ файлів",
                  size=12, color=MUTED))

    p.append(fitbox(500, 520, 540, 100,
                    ["адреса вузла глобальна, тож зшивати нема чого:",
                     "кожен кут комірки сам знаходить свій файл,",
                     "дубльований крайній ряд не читається жодного разу,",
                     "а маршрут через межу нічим не відрізняється від решти"],
                    size=13, pad=10, fill=COOL, sw=1.6))

    p.append(text(W / 2, 658,
                  "шов між квадратами — не задача склеювання, а наслідок неправильного порядку обчислення адреси",
                  size=13, color=MUTED))
    render(os.path.join(IMG, 'tile-seam.svg'), W, H, *p,
           title="Глобальна адреса вузла прибирає шов між квадратами")


if __name__ == '__main__':
    heights()
    grid_cell()
    reduce_op()
    line_of_sight()
    bilinear_saddle()
    slope_jump()
    alias_grid()
    insar_geometry()
    surface_not_ground()
    dem_timeline()
    grid_walk()
    tile_seam()
    print("ok:", sorted(os.listdir(IMG)))
