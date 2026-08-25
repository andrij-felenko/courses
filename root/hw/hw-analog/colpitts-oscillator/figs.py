# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

ACC = "#8e44ad"   # акцент кола зворотного зв'язку
TANK = "#27ae60"  # коливальний контур


# ── helpers (локальні символи елементів) ────────────────────────────────────
def cap(cx, cy, horiz=False, gap=7, plate=15, lead=12, color=LINE):
    """Конденсатор: дві пластини. Вертикальний (виводи вгору/вниз) за замовч."""
    out = []
    if not horiz:
        out.append(line(cx, cy - gap - lead, cx, cy - gap, color=color))
        out.append(line(cx - plate, cy - gap, cx + plate, cy - gap, color=color, sw=2.2))
        out.append(line(cx - plate, cy + gap, cx + plate, cy + gap, color=color, sw=2.2))
        out.append(line(cx, cy + gap, cx, cy + gap + lead, color=color))
    else:
        out.append(line(cx - gap - lead, cy, cx - gap, cy, color=color))
        out.append(line(cx - gap, cy - plate, cx - gap, cy + plate, color=color, sw=2.2))
        out.append(line(cx + gap, cy - plate, cx + gap, cy + plate, color=color, sw=2.2))
        out.append(line(cx + gap, cy, cx + gap + lead, cy, color=color))
    return "".join(out)


def inductor(x1, y, x2, loops=4, color=LINE):
    """Котушка-індуктивність як низка дуг між x1 і x2 на висоті y."""
    out = []
    span = x2 - x1
    r = span / (2.0 * loops)
    out.append(line(x1, y, x1, y, color=color))
    d = "M %.1f %.1f" % (x1, y)
    for i in range(loops):
        cx = x1 + r * (2 * i + 1)
        d += " A %.1f %.1f 0 0 1 %.1f %.1f" % (r, r, cx + r, y)
    out.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (d, color))
    return "".join(out)


def npn(cx, cy, color=LINE, r=22):
    """NPN-транзистор у колі: база ліворуч, колектор угорі, емітер унизу."""
    out = [circle(cx, cy, r, fill="#fff", stroke=color, sw=1.6)]
    bx = cx - r
    # вертикальна база-пластина
    out.append(line(cx - 7, cy - 11, cx - 7, cy + 11, color=color, sw=2.4))
    out.append(line(bx, cy, cx - 7, cy, color=color))            # вивід бази
    out.append(line(cx - 7, cy - 5, cx + 9, cy - 13, color=color))   # до колектора
    out.append(line(cx + 9, cy - 13, cx + 9, cy - r - 6, color=color))
    out.append(line(cx - 7, cy + 5, cx + 9, cy + 13, color=color))   # до емітера
    out.append(line(cx + 9, cy + 13, cx + 9, cy + r + 6, color=color))
    # стрілка емітера (NPN — назовні)
    out.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
               % (cx + 4, cy + 7.5, cx + 9, cy + 13, cx + 1.5, cy + 12.5, color))
    return "".join(out), (cx + 9, cy - r - 6), (cx + 9, cy + r + 6), (bx, cy)  # body, C, E, B


def gnd(cx, cy, color=LINE):
    out = [line(cx, cy, cx, cy + 6, color=color)]
    for i, w in enumerate((16, 10, 5)):
        out.append(line(cx - w, cy + 6 + i * 4, cx + w, cy + 6 + i * 4, color=color, sw=2))
    return "".join(out)


def res_v(cx, y1, y2, color=LINE):
    """Вертикальний резистор-зиґзаґ між y1 і y2."""
    mid = (y1 + y2) / 2
    pts = [(cx, y1)]
    step = (y2 - 24 - (y1 + 12)) / 4.0
    yy = y1 + 12
    for i in range(5):
        dx = 8 if i % 2 == 0 else -8
        pts.append((cx + dx, yy))
        yy += step
    pts.append((cx, y2 - 12))
    pts.append((cx, y2))
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    return '<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (d, color)


# ══ ФІГУРА 1 — Схема генератора Колпітца ════════════════════════════════════
def fig_schematic():
    W, H = 660, 440
    f = []
    VTOP = 64           # шина живлення
    GNDY = 380          # земля
    xT = 215            # транзистор
    yT = 220
    body, C, E, B = npn(xT, yT)

    # шина живлення +V
    f.append(line(60, VTOP, 600, VTOP, color=POS, sw=2.2))
    f.append(text(60, VTOP - 10, "+V", size=14, color=POS, bold=True, anchor="start"))

    # координати контуру (права частина)
    xTank = 470
    yL = 150            # індуктивність угорі правої гілки
    yNodeTop = 110      # верхній вузол контуру (= колектор)
    yTap = 250          # відведення дільника (на емітер)
    yNodeBot = 330      # нижній вузол контуру (= земля)

    # колекторний дросель (RF choke) від +V до колектора
    f.append(inductor(xT - 34, VTOP, xT + 34, loops=4, color=MUTED))
    f.append(line(xT, VTOP, xT - 34, VTOP, color=MUTED))
    f.append(line(xT, VTOP, xT, C[1], color=LINE))
    f.append(text(xT + 44, VTOP + 4, "дросель живлення", size=11, color=MUTED, anchor="start"))

    # верх контуру → колектор (горизонталь на рівні yNodeTop)
    f.append(line(C[0], C[1], C[0], yNodeTop, color=LINE))
    f.append(line(C[0], yNodeTop, xTank, yNodeTop, color=LINE))

    # вузли контуру
    f.append(circle(xTank, yNodeTop, 3, fill=LINE, stroke=LINE))
    f.append(circle(xTank, yNodeBot, 3, fill=LINE, stroke=LINE))
    f.append(circle(xTank, yTap, 4, fill=ACC, stroke=ACC))

    # ліва гілка контуру: C1 (верх→відведення), C2 (відведення→низ)
    f.append(line(xTank, yNodeTop, xTank, (yNodeTop + yTap) / 2 - 12, color=LINE))
    f.append(cap(xTank, (yNodeTop + yTap) / 2, color=LINE))
    f.append(line(xTank, (yNodeTop + yTap) / 2 + 12, xTank, yTap, color=LINE))
    f.append(text(xTank - 22, (yNodeTop + yTap) / 2 + 4, "C1", size=14, bold=True, anchor="end"))
    f.append(line(xTank, yTap, xTank, (yTap + yNodeBot) / 2 - 12, color=LINE))
    f.append(cap(xTank, (yTap + yNodeBot) / 2, color=LINE))
    f.append(line(xTank, (yTap + yNodeBot) / 2 + 12, xTank, yNodeBot, color=LINE))
    f.append(text(xTank - 22, (yTap + yNodeBot) / 2 + 4, "C2", size=14, bold=True, anchor="end"))

    # права гілка контуру: L паралельно дільнику
    xLr = xTank + 90
    f.append(line(xTank, yNodeTop, xLr, yNodeTop, color=TANK))
    f.append(line(xTank, yNodeBot, xLr, yNodeBot, color=TANK))
    f.append(line(xLr, yNodeTop, xLr, yL - 9, color=TANK))
    f.append(line(xLr, yL + 9, xLr, yNodeBot, color=TANK))
    f.append(inductor(xLr - 34, yL, xLr + 34, loops=4, color=TANK))
    f.append(text(xLr + 14, yL + 4, "L", size=15, color=TANK, bold=True, anchor="start"))

    # відведення → емітер (зворотний зв'язок, фіолетова траса)
    xFb = E[0] + 75
    f.append(line(xTank, yTap, xFb, yTap, color=ACC, sw=2))
    f.append(line(xFb, yTap, xFb, E[1], color=ACC, sw=2))
    f.append(line(E[0], E[1], xFb, E[1], color=ACC, sw=2))
    f.append(text((xTank + xFb) / 2, yTap - 9, "відведення → емітер", size=11, color=ACC))

    # низ контуру → земля
    f.append(line(xTank, yNodeBot, xTank, GNDY, color=LINE))
    f.append(gnd(xTank, GNDY))

    # база: вузол зміщення від +V (схематично — резистор від шини на базу)
    xB = 110
    f.append(line(B[0], B[1], xB, B[1], color=LINE))
    f.append(res_v(xB, VTOP, B[1], color=MUTED))
    f.append(text(xB - 14, (VTOP + B[1]) / 2, "Rb", size=12, color=MUTED, anchor="end"))
    f.append(text(xB - 14, (VTOP + B[1]) / 2 + 16, "зміщення", size=10, color=MUTED, anchor="end"))

    # емітерний резистор струму спокою — окрема гілка вниз від точки емітера
    xRe = E[0]
    f.append(res_v(xRe, E[1] + 10, 340, color=LINE))
    f.append(line(xRe, E[1], xRe, E[1] + 10, color=LINE))
    f.append(line(xRe, 340, xRe, GNDY, color=LINE))
    f.append(gnd(xRe, GNDY))
    f.append(text(xRe - 14, (E[1] + 350) / 2, "Re", size=12, anchor="end"))

    # підпис транзистора
    f.append(text(xT, yT + 42, "підсилювач", size=11, color=MUTED))

    render(os.path.join(OUT, 'schematic.svg'), W, H, *f,
           title="Генератор Колпітца: підсилювач + LC-контур із ємнісним дільником")


# ══ ФІГУРА 2 — Ємнісний дільник як відведення зворотного зв'язку ════════════
def fig_divider():
    W, H = 600, 360
    f = []
    xc = 200
    yTop, yTap, yBot = 90, 200, 310
    f.append(circle(xc, yTop, 3, fill=POS, stroke=POS))
    f.append(circle(xc, yTap, 3, fill=ACC, stroke=ACC))
    f.append(circle(xc, yBot, 3, fill=NEG, stroke=NEG))
    # C1
    f.append(line(xc, yTop, xc, (yTop + yTap) / 2 - 12, color=LINE))
    f.append(cap(xc, (yTop + yTap) / 2, color=LINE))
    f.append(line(xc, (yTop + yTap) / 2 + 12, xc, yTap, color=LINE))
    f.append(text(xc - 24, (yTop + yTap) / 2 + 4, "C1", size=15, bold=True, anchor="end"))
    # C2
    f.append(line(xc, yTap, xc, (yTap + yBot) / 2 - 12, color=LINE))
    f.append(cap(xc, (yTap + yBot) / 2, color=LINE))
    f.append(line(xc, (yTap + yBot) / 2 + 12, xc, yBot, color=LINE))
    f.append(text(xc - 24, (yTap + yBot) / 2 + 4, "C2", size=15, bold=True, anchor="end"))

    # написи на вузлах
    f.append(text(xc + 18, yTop + 4, "вихід підсилювача (колектор)", size=12, color=POS, anchor="start"))
    f.append(text(xc + 18, yTap + 4, "відведення → вхід", size=12, color=ACC, anchor="start"))
    f.append(text(xc + 18, yBot + 4, "земля (спільна точка)", size=12, color=NEG, anchor="start"))

    # стрілки напруги: верх угору (+), низ вниз (−) відносно відведення
    f.append(arrow(xc - 70, yTap, xc - 70, yTop + 6, color=POS))
    f.append(arrow(xc - 70, yTap, xc - 70, yBot - 6, color=NEG))
    f.append(text(xc - 78, (yTop + yTap) / 2, "u1", size=13, color=POS, anchor="end"))
    f.append(text(xc - 78, (yTap + yBot) / 2, "u2", size=13, color=NEG, anchor="end"))

    # права колонка — формула дільника
    bx, w, h = textbox(460, 150,
                       "Дільник віддає назад\nчастку β = C1 / (C1 + C2)\nверх і відведення —\nу протифазі (−180°)",
                       size=13, pad=12, stroke=ACC, fill="#f6effa")
    f.append(bx)
    bx2, _, _ = textbox(460, 280,
                        "Сумарна ємність контуру:\nCs = C1·C2 / (C1 + C2)",
                        size=13, pad=12, stroke=TANK, fill="#eafaf0")
    f.append(bx2)

    render(os.path.join(OUT, 'divider.svg'), W, H, *f,
           title="Ємнісний дільник: одна напруга — два протифазні відведення")


# ══ ФІГУРА 3 — Дуальність Колпітц ↔ Гартлі ══════════════════════════════════
def fig_dual():
    W, H = 620, 330
    f = []

    # ліва панель — Колпітц (2 ємності + 1 індуктивність)
    cxL = 165
    yT, yMid, yB = 110, 195, 280
    f.append(text(cxL, 70, "Колпітц", size=15, bold=True, color=ACC))
    # дільник з 2 конденсаторів
    f.append(line(cxL, yT, cxL, (yT + yMid) / 2 - 12, color=LINE))
    f.append(cap(cxL, (yT + yMid) / 2, color=LINE))
    f.append(line(cxL, (yT + yMid) / 2 + 12, cxL, yMid, color=LINE))
    f.append(text(cxL - 22, (yT + yMid) / 2 + 4, "C1", size=13, bold=True, anchor="end"))
    f.append(line(cxL, yMid, cxL, (yMid + yB) / 2 - 12, color=LINE))
    f.append(cap(cxL, (yMid + yB) / 2, color=LINE))
    f.append(line(cxL, (yMid + yB) / 2 + 12, cxL, yB, color=LINE))
    f.append(text(cxL - 22, (yMid + yB) / 2 + 4, "C2", size=13, bold=True, anchor="end"))
    # індуктивність паралельно
    xLr = cxL + 80
    f.append(line(cxL, yT, xLr, yT, color=TANK))
    f.append(line(cxL, yB, xLr, yB, color=TANK))
    f.append(line(xLr, yT, xLr, yMid - 26, color=TANK))
    f.append(inductor(xLr - 26, yMid, xLr + 26, loops=3, color=TANK))
    f.append(line(xLr, yMid + 9, xLr, yB, color=TANK))
    f.append(text(xLr + 34, yMid + 4, "L", size=14, bold=True, color=TANK, anchor="start"))
    f.append(circle(cxL, yMid, 3, fill=ACC, stroke=ACC))
    f.append(text(cxL, yB + 26, "відведення — на дільнику ємностей", size=11, color=MUTED))

    # розділювач
    f.append(line(W / 2, 55, W / 2, H - 20, color=MUTED, dash="4 4"))
    f.append(text(W / 2, 200, "дуальні", size=12, color=MUTED, bold=True))
    f.append(text(W / 2, 216, "C ↔ L", size=12, color=MUTED))

    # права панель — Гартлі (2 індуктивності + 1 ємність)
    cxR = 455
    f.append(text(cxR, 70, "Гартлі", size=15, bold=True, color=NEG))
    # дві індуктивності в стовпчик
    f.append(line(cxR, yT, cxR, (yT + yMid) / 2 - 16, color=TANK))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>'
             % (_coil_v(cxR, (yT + yMid) / 2 - 16, (yT + yMid) / 2 + 16, 3), TANK))
    f.append(line(cxR, (yT + yMid) / 2 + 16, cxR, yMid, color=TANK))
    f.append(text(cxR - 20, (yT + yMid) / 2 + 4, "L1", size=13, bold=True, anchor="end"))
    f.append(line(cxR, yMid, cxR, (yMid + yB) / 2 - 16, color=TANK))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>'
             % (_coil_v(cxR, (yMid + yB) / 2 - 16, (yMid + yB) / 2 + 16, 3), TANK))
    f.append(line(cxR, (yMid + yB) / 2 + 16, cxR, yB, color=TANK))
    f.append(text(cxR - 20, (yMid + yB) / 2 + 4, "L2", size=13, bold=True, anchor="end"))
    # ємність паралельно
    xCr = cxR + 80
    f.append(line(cxR, yT, xCr, yT, color=LINE))
    f.append(line(cxR, yB, xCr, yB, color=LINE))
    f.append(line(xCr, yT, xCr, yMid - 9, color=LINE))
    f.append(cap(xCr, yMid, color=LINE))
    f.append(line(xCr, yMid + 9, xCr, yB, color=LINE))
    f.append(text(xCr + 22, yMid + 4, "C", size=14, bold=True, anchor="start"))
    f.append(circle(cxR, yMid, 3, fill=ACC, stroke=ACC))
    f.append(text(cxR, yB + 26, "відведення — на дільнику котушок", size=11, color=MUTED))

    render(os.path.join(OUT, 'dual.svg'), W, H, *f,
           title="Та сама схема, дзеркальні елементи: Колпітц ↔ Гартлі")


def _coil_v(cx, y1, y2, loops):
    """Вертикальна котушка (дуги ліворуч) — для фіг.3."""
    span = y2 - y1
    r = span / (2.0 * loops)
    d = "M %.1f %.1f" % (cx, y1)
    for i in range(loops):
        cy = y1 + r * (2 * i + 1)
        d += " A %.1f %.1f 0 0 0 %.1f %.1f" % (r, r, cx, cy + r)
    return d


# ══ ФІГУРА (hist) — Ідея / публікація / патент на одній шкалі ════════════════
def fig_timeline():
    """Для вставки hist: три різні події рознесено в часі для обох винахідників.
    Показує, що «придумав» ≠ «надрукував» ≠ «отримав патент»."""
    W, H = 720, 430
    f = []

    # вісь часу
    x0, x1 = 70, 660
    yAx = 235
    yr0, yr1 = 1914, 1928           # межі шкали (роки)

    def X(year):
        return x0 + (year - yr0) / float(yr1 - yr0) * (x1 - x0)

    f.append(line(x0, yAx, x1 + 6, yAx, color=INK, sw=2))
    f.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
             % (x1 + 6, yAx - 5, x1 + 16, yAx, x1 + 6, yAx + 5, INK))
    # засічки років
    for yr in range(1915, 1928, 1):
        xx = X(yr)
        major = (yr % 5 == 0)
        f.append(line(xx, yAx, xx, yAx + (8 if major else 4), color=MUTED, sw=1.4))
        if major:
            f.append(text(xx, yAx + 24, str(yr), size=12, color=MUTED))

    # маркер події НАД віссю (Гартлі): риска вниз до кружка, рамка з центром y_label
    def event_hi(year, y_label, label, color, fill):
        xx = X(year)
        f.append(line(xx, yAx - 3, xx, y_label + 22, color=color, sw=1.6, dash="3 3"))
        f.append(circle(xx, yAx, 5, fill=color, stroke=color))
        bx, w, h = textbox(xx, y_label, label, size=11.5, pad=8, stroke=color, fill=fill)
        f.append(bx)

    # маркер події ПІД віссю (Колпітц): риска вгору до кружка
    def event_lo(year, y_label, label, color, fill):
        xx = X(year)
        f.append(line(xx, yAx + 3, xx, y_label - 22, color=color, sw=1.6, dash="3 3"))
        f.append(circle(xx, yAx, 5, fill=color, stroke=color))
        bx, w, h = textbox(xx, y_label, label, size=11.5, pad=8, stroke=color, fill=fill)
        f.append(bx)

    # ── Гартлі (індуктивний, синій) — над віссю ─────────────────────────────
    f.append(text(x0, 44, "Гартлі — індуктивний прообраз", size=13, bold=True,
                  color=NEG, anchor="start"))
    event_hi(1915, 80, "1915\nідея + заявка\n(US 1,356,763)", NEG, "#eaf0fd")
    event_hi(1920, 90, "1920\nпатент видано", NEG, "#eaf0fd")

    # ── Колпітц (ємнісний, фіолетовий) — під віссю ──────────────────────────
    f.append(text(x0, 412, "Колпітц — ємнісний двійник", size=13, bold=True,
                  color=ACC, anchor="start"))
    # 1918 заявка й 1919 стаття близько в часі — рознесено по глибині, щоб не злипались
    event_lo(1918.0, 312, "1918\nідея + заявка", ACC, "#f6effa")
    event_lo(1919.3, 378, "1919\nстаття\nКрафта–Колпітца", ACC, "#f6effa")
    event_lo(1927.0, 322, "1927\nпатент\n(US 1,624,537)", ACC, "#f6effa")

    render(os.path.join(OUT, 'timeline.svg'), W, H, *f,
           title="Придумав ≠ надрукував ≠ запатентував")


if __name__ == '__main__':
    fig_schematic()
    fig_divider()
    fig_dual()
    fig_timeline()
    print("OK: 4 figures")
