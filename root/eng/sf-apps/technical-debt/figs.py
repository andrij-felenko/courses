# -*- coding: utf-8 -*-
"""Фігури для теми «Технічний борг і вартість зміни».
Вивід — ./img/*.svg. svgkit імпортуємо, не переписуємо."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_interest_curve():
    """Дві траєкторії вартості однієї правки з часом: борг гасять vs борг росте.
    Розрив між кривими — це відсотки (interest)."""
    W, H = 788, 470
    # межі поля графіка
    x0, y0 = 90, 90          # лівий-верхній кут осей (верх)
    xr, yb = 690, 380        # правий край / низ (базова лінія)
    els = []

    # осі
    els.append(line(x0, y0 - 20, x0, yb, color=INK, sw=2))            # вісь Y
    els.append(line(x0, yb, xr + 20, yb, color=INK, sw=2))            # вісь X
    els.append(text(x0 - 12, y0 - 26, "вартість", size=13, color=MUTED, anchor="middle"))
    els.append(text(x0 - 12, y0 - 10, "правки", size=13, color=MUTED, anchor="middle"))
    els.append(text(xr + 4, yb + 26, "час життя системи →", size=13, color=MUTED, anchor="end"))

    # базова «здорова» вартість — майже пласка, легкий ріст
    n = 40
    def X(i): return x0 + (xr - x0) * i / n
    healthy = [yb - 40 - 30 * (i / n) for i in range(n + 1)]          # трохи росте
    # борг росте — прискорення (квадратично), відсотки накопичуються
    debt = [yb - 40 - 30 * (i / n) - 250 * (i / n) ** 2 for i in range(n + 1)]

    def polyline(pts, color, sw, dash=None):
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        s = " ".join("%.1f,%.1f" % (X(i), pts[i]) for i in range(len(pts)))
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
                % (s, color, sw, d))

    els.append(polyline(healthy, NEG, 3.0))
    els.append(polyline(debt, POS, 3.0))

    # вертикальна стрілка-розрив «відсотки» на 3/4 шляху
    ci = 32
    xg = X(ci)
    els.append(line(xg, healthy[ci], xg, debt[ci], color=FIELD, sw=2, dash="4 3"))
    els.append(arrow(xg, healthy[ci], xg, debt[ci] + 4, color=FIELD, sw=2))
    # рамку ставимо ЛІВОРУЧ від розриву, у порожньому просторі під здоровою кривою
    gap_mid = (healthy[ci] + debt[ci]) / 2
    b, bw, bh = textbox(0, 0, "відсотки:\nнадплата\nна кожну\nправку",
                        size=12, color=FIELD, stroke=FIELD, fill="#eafaf0")
    b, bw, bh = textbox(xg - bw / 2 - 34, gap_mid, "відсотки:\nнадплата\nна кожну\nправку",
                        size=12, color=FIELD, stroke=FIELD, fill="#eafaf0")
    els.append(b)

    # підписи кривих — праворуч, з запасом
    els.append(text(xr + 14, debt[-1] + 4, "борг", size=14, color=POS, bold=True, anchor="start"))
    els.append(text(xr + 14, healthy[-1] + 4, "здорова", size=14, color=NEG, bold=True, anchor="start"))
    els.append(text(xr + 14, healthy[-1] + 22, "структура", size=14, color=NEG, bold=True, anchor="start"))

    render(os.path.join(IMG, "interest-curve.svg"), W, H, *els)


def fig_quadrant():
    """Квадрант Фаулера. Рядки: розважливий (верх) / безрозсудний (низ).
    Колонки: свідомий (ліво) / випадковий (право)."""
    W, H = 720, 560
    # поле 2×2 із запасом ліворуч під підписи рядків і зверху під підписи колонок
    L, T = 200, 100
    cw = 220                          # ширина/висота клітини
    els = []

    green = "#eafaf0"; yellow = "#fdf6e3"; orange = "#fdecea"

    def cell(col, row, txt, tone):
        x = L + col * cw
        y = T + row * cw
        return fitbox(x + 6, y + 6, cw - 12, cw - 12, txt, size=14,
                      fill=tone, stroke=LINE, sw=1.3)

    # col0=свідомий, col1=випадковий; row0=розважливий, row1=безрозсудний
    els.append(cell(0, 0, "«Треба відвантажити\nзараз — розберемося\nз наслідками потім»", green))
    els.append(cell(1, 0, "«Тепер ми розуміємо,\nяк слід було\nце зробити»", yellow))
    els.append(cell(0, 1, "«Нема часу\nна дизайн»", yellow))
    els.append(cell(1, 1, "«А що таке\nшари?»", orange))

    # підписи колонок — над кожною колонкою
    els.append(text(L + cw / 2, T - 24, "СВІДОМИЙ", size=14, bold=True, color=INK))
    els.append(text(L + cw / 2, T - 8, "(знали, що беремо борг)", size=11, color=MUTED))
    els.append(text(L + cw + cw / 2, T - 24, "ВИПАДКОВИЙ", size=14, bold=True, color=INK))
    els.append(text(L + cw + cw / 2, T - 8, "(усвідомили заднім числом)", size=11, color=MUTED))

    # підписи рядків — ліворуч від кожного рядка, у два рядки, без накладання на клітину
    lx = L - 24
    els.append(text(lx, T + cw / 2 - 8, "РОЗВАЖ-", size=14, bold=True, color=INK, anchor="end"))
    els.append(text(lx, T + cw / 2 + 10, "ЛИВИЙ", size=14, bold=True, color=INK, anchor="end"))
    els.append(text(lx, T + cw / 2 + 30, "(зважене", size=11, color=MUTED, anchor="end"))
    els.append(text(lx, T + cw / 2 + 45, "рішення)", size=11, color=MUTED, anchor="end"))
    els.append(text(lx, T + cw + cw / 2 - 8, "БЕЗРОЗ-", size=14, bold=True, color=INK, anchor="end"))
    els.append(text(lx, T + cw + cw / 2 + 10, "СУДНИЙ", size=14, bold=True, color=INK, anchor="end"))
    els.append(text(lx, T + cw + cw / 2 + 30, "(недбалість)", size=11, color=MUTED, anchor="end"))

    # ярлики бажаності в самих кутових клітинах — маленькі, у нижньому куті клітини
    els.append(text(L + 14, T + cw - 14, "найкраще", size=11, color=FIELD, bold=True, anchor="start"))
    els.append(text(L + 2 * cw - 14, T + 2 * cw - 14, "найгірше", size=11, color=POS, bold=True, anchor="end"))

    render(os.path.join(IMG, "quadrant.svg"), W, H, *els)


def fig_principal_interest():
    """Кожен реліз: або гасиш тіло боргу (рефакторинг), або лише платиш відсотки."""
    W, H = 720, 360
    els = []
    els.append(text(W / 2, 40, "На що йде час у кожному релізі", size=15, bold=True))

    # дві доріжки
    bar_x, bar_w = 70, 580
    def track(y, label, segs):
        out = [text(bar_x - 12, y + 22, label, size=13, anchor="end", color=INK)]
        x = bar_x
        for w, tone, cap, tcol in segs:
            out.append(rect(x, y, w, 44, fill=tone, stroke=LINE, sw=1.2))
            out.append(text(x + w / 2, y + 28, cap, size=12, color=tcol, bold=True))
            x += w
        return out

    # верх: борг ігнорують — відсотки з'їдають дедалі більше
    els += track(90, "борг росте",
                 [(230, "#eafaf0", "нова функція", FIELD),
                  (350, "#fdecea", "відсотки: обхід бруду", POS)])
    # низ: борг гасять — тіло меншає, відсотки малі
    els += track(200, "борг гасять",
                 [(360, "#eafaf0", "нова функція", FIELD),
                  (120, "#fdf6e3", "рефакторинг", "#b8860b"),
                  (100, "#fdecea", "відсотки", POS)])

    els.append(text(bar_x, 300, "Зелене — робота, за яку платить замовник. Червоне — податок боргу.",
                    size=12, color=MUTED, anchor="start"))
    els.append(text(bar_x, 322, "Жовте — разова виплата тіла: коштує зараз, зате гасить майбутні відсотки.",
                    size=12, color=MUTED, anchor="start"))
    render(os.path.join(IMG, "principal-interest.svg"), W, H, *els)


def fig_blast_radius():
    """Хвиля зміни: точка падіння (одне правило) і кола зчеплених місць, які
    доводиться правити слідом. Ліворуч — одна константа (радіус 0), праворуч —
    розмазана копіями логіка (радіус росте з кількістю зчеплених місць)."""
    W, H = 760, 420
    els = []
    els.append(text(W / 2, 34, "Хвиля зміни: скільки місць чіпає одна правка", size=15, bold=True))

    # --- ЛІВА панель: одне джерело правди ---
    cxL, cyL = 200, 250
    els.append(text(cxL, 78, "одне джерело правди", size=13, bold=True, color=FIELD))
    # кільце-контур без внутрішніх кіл (радіус хвилі = 0)
    els.append(circle(cxL, cyL, 96, fill="#f7fdf9", stroke="#cde7d8", sw=1.0))
    b, bw, bh = textbox(cxL, cyL, "BATTERY_FULL_V\n(одна константа)",
                        size=12, color=INK, stroke=FIELD, fill="#eafaf0", sw=1.6)
    els.append(b)
    els.append(text(cxL, cyL + 118, "правок: 1", size=13, bold=True, color=FIELD))
    els.append(text(cxL, cyL + 138, "хвиля не розходиться", size=11, color=MUTED))

    # --- ПРАВА панель: розмазане знання ---
    cxR, cyR = 545, 250
    els.append(text(cxR, 78, "розмазане знання", size=13, bold=True, color=POS))
    # концентричні кола — «кола на воді» від точки падіння
    for r in (110, 78, 46):
        els.append(circle(cxR, cyR, r, fill="none", stroke="#f0c9c4", sw=1.2))
    # точка падіння
    els.append(circle(cxR, cyR, 15, fill="#fdecea", stroke=POS, sw=2))
    els.append(text(cxR, cyR + 5, "×5", size=13, bold=True, color=POS))
    # зчеплені місця по колу — маленькі бирки
    sites = ["індикатор", "захист", "лог", "телеметрія", "калібр."]
    import math
    for i, name in enumerate(sites):
        a = -math.pi / 2 + i * 2 * math.pi / len(sites)
        px = cxR + 96 * math.cos(a)
        py = cyR + 96 * math.sin(a)
        els.append(circle(px, py, 6, fill=POS, stroke=POS, sw=1))
        # підпис ставимо назовні кола, від центру — щоб не наліг на кільця
        lx = cxR + 132 * math.cos(a)
        ly = cyR + 132 * math.sin(a)
        anc = "start" if math.cos(a) > 0.2 else ("end" if math.cos(a) < -0.2 else "middle")
        els.append(text(lx, ly + 4, name, size=11, color=INK, anchor=anc))
    els.append(text(cxR, cyR + 148, "правок: 5 (і це якщо всі знайшов)", size=13, bold=True, color=POS))

    render(os.path.join(IMG, "blast-radius.svg"), W, H, *els)


def fig_debt_timeline():
    """Часова смуга ідеї «код псується від змін»: Лехман описав ЯВИЩЕ (1974/1980),
    Каннінгем дав МЕТАФОРУ (1992), сам-таки уточнив її (2009). Показує, що
    емпіричний опроцес випередив образ на ~18 років."""
    W, H = 820, 340
    els = []
    els.append(text(W / 2, 34, "Одне явище — два погляди на нього", size=15, bold=True))

    # горизонтальна вісь часу
    ax_y = 150
    x_left, x_right = 70, 750
    els.append(line(x_left, ax_y, x_right, ax_y, color=INK, sw=2))
    els.append(arrow(x_right - 6, ax_y, x_right + 8, ax_y, color=INK, sw=2))
    els.append(text(x_right + 4, ax_y - 12, "час", size=12, color=MUTED, anchor="end"))

    # роки-віхи: (частка_шляху, рік, підпис, вгору/вниз, тон)
    def X(frac): return x_left + (x_right - x_left) * frac
    marks = [
        (0.06, "1974", "Лехман:\nперші закони\n(явище)", "up", NEG),
        (0.20, "1980", "Лехман:\nкласи S/P/E,\n5 законів", "down", NEG),
        (0.55, "1992", "Каннінгем:\nметафора боргу\n(OOPSLA)", "up", POS),
        (0.90, "2009", "Каннінгем\nуточнює\nметафору", "down", FIELD),
    ]
    for frac, year, cap, side, tone in marks:
        x = X(frac)
        els.append(circle(x, ax_y, 7, fill=tone, stroke=tone, sw=1))
        els.append(text(x, ax_y + (-16 if side == "up" else 24), year,
                        size=14, bold=True, color=tone))
        # рамка-підпис із запасом, поза віссю
        by = ax_y - 96 if side == "up" else ax_y + 40
        b, bw, bh = textbox(x, by + 30, cap, size=11, color=INK,
                            stroke=tone, fill="#ffffff", sw=1.2)
        els.append(b)

    # підпис-висновок унизу
    els.append(text(W / 2, H - 22,
                    "Лехман виміряв, що система під змінами дедалі складнішає; "
                    "Каннінгем дав цьому образ, зрозумілий бізнесу.",
                    size=11, color=MUTED))
    render(os.path.join(IMG, "debt-timeline.svg"), W, H, *els)


def fig_breakeven():
    """Накопичена вартість у часі: платити відсотки вічно (крута пряма) vs
    погасити тіло раз (стрибок P, далі полога пряма). Перетин — точка
    беззбитковості: скільки правок треба, щоб рефакторинг окупився. k* = P/i."""
    W, H = 800, 470
    x0, y0 = 100, 70          # верх осей
    xr, yb = 690, 380         # правий край поля / базова лінія
    els = []

    els.append(line(x0, y0 - 16, x0, yb, color=INK, sw=2))           # вісь Y
    els.append(line(x0, yb, xr + 20, yb, color=INK, sw=2))           # вісь X
    els.append(text(x0, y0 - 28, "накопичена", size=12, color=MUTED, anchor="middle"))
    els.append(text(x0, y0 - 14, "вартість", size=12, color=MUTED, anchor="middle"))
    els.append(text(xr + 16, yb + 26, "число правок k →", size=13, color=MUTED, anchor="end"))

    # модель (умовні одиниці часу):
    #   лишити брудним: cost(k) = (b+i)·k         — крута пряма з нуля
    #   рефакторинг:    cost(k) = P + b·k          — стрибок P, далі полога
    n = 12.0                  # горизонт по осі k
    b = 8.0                   # чиста вартість правки (нахил пологої)
    i = 6.0                   # надплата за брудну структуру (відсоток)
    P = 30.0                  # тіло боргу — разова виплата рефакторингу
    top = (b + i) * n         # максимум по вертикалі (крута пряма в кінці)

    def sx(k): return x0 + (xr - x0) * k / n
    def sy(v): return yb - (yb - y0) * v / top

    dirty = [(sx(k), sy((b + i) * k)) for k in range(int(n) + 1)]
    refac = [(sx(k), sy(P + b * k)) for k in range(int(n) + 1)]

    def poly(pts, color, sw):
        s = " ".join("%.1f,%.1f" % p for p in pts)
        return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (s, color, sw)

    kstar = P / i             # точка беззбитковості
    xs, ys = sx(kstar), sy((b + i) * kstar)

    els.append(line(xs, ys, xs, yb, color=MUTED, sw=1.3, dash="4 3"))
    els.append(poly(dirty, POS, 3.0))
    els.append(poly(refac, NEG, 3.0))
    els.append(circle(xs, ys, 6, fill=BG, stroke=INK, sw=2))

    # стрибок P на осі k=0 (виплата тіла зараз)
    els.append(line(sx(0), sy(0.2), sx(0), sy(P), color=NEG, sw=3))
    b1, bw1, bh1 = textbox(0, 0, "тіло P", size=12, color=NEG, stroke=NEG, fill="#eaf0fd")
    b1, bw1, bh1 = textbox(x0 - bw1 / 2 - 10, (sy(0) + sy(P)) / 2, "тіло P",
                           size=12, color=NEG, stroke=NEG, fill="#eaf0fd")
    els.append(b1)

    els.append(text(xs, yb + 22, "беззбитковість k*", size=12, color=INK, bold=True, anchor="middle"))
    els.append(text(xs, yb + 38, "= P / i", size=12, color=MUTED, anchor="middle"))

    # підписи прямих — праворуч, рознесені
    els.append(text(xr + 16, dirty[-1][1] + 4, "лишити брудним", size=13, color=POS, bold=True, anchor="start"))
    els.append(text(xr + 16, dirty[-1][1] + 21, "(b+i)·k", size=12, color=POS, anchor="start"))
    els.append(text(xr + 16, refac[-1][1] + 4, "рефакторинг", size=13, color=NEG, bold=True, anchor="start"))
    els.append(text(xr + 16, refac[-1][1] + 21, "P + b·k", size=12, color=NEG, anchor="start"))

    els.append(text((xs + xr) / 2, y0 + 8, "рефакторинг уже дешевший", size=12, color=FIELD, bold=True, anchor="middle"))

    render(os.path.join(IMG, "breakeven.svg"), W, H, *els)


def fig_hot_cold():
    """Площина рішення: горизонт H (вісь X) × частота змін f (вісь Y).
    Крива беззбитковості f·i·H = P — гіпербола — ділить площину: під нею
    холодний код (лишити брудним), над нею гарячий (гасити тіло)."""
    W, H = 760, 470
    x0, y0 = 90, 70
    xr, yb = 690, 380
    els = []

    els.append(line(x0, y0 - 16, x0, yb, color=INK, sw=2))
    els.append(line(x0, yb, xr + 20, yb, color=INK, sw=2))
    els.append(text(x0, y0 - 28, "частота", size=12, color=MUTED, anchor="middle"))
    els.append(text(x0, y0 - 14, "змін f", size=12, color=MUTED, anchor="middle"))
    els.append(text(xr + 16, yb + 26, "горизонт життя H →", size=13, color=MUTED, anchor="end"))

    # гіпербола f = C/H у нормованих координатах поля
    xw, yh = xr - x0, yb - y0
    C = 0.17
    pts = []
    for j in range(1, 121):
        u = j / 120.0
        v = C / u
        if v > 1.0:
            continue
        pts.append((x0 + u * xw, yb - v * yh))
    d = " ".join("%.1f,%.1f" % p for p in pts)
    els.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (d, INK))

    mid = pts[len(pts) // 2]
    els.append(text(mid[0] + 10, mid[1] - 8, "f · i · H = P", size=13, color=INK, bold=True, anchor="start"))
    els.append(text(mid[0] + 10, mid[1] + 9, "беззбитковість", size=11, color=MUTED, anchor="start"))

    # НАД кривою — гарячий код
    bh1, bw, bhh = textbox(x0 + xw * 0.70, y0 + yh * 0.28,
                           "ГАРЯЧИЙ КОД\nчасто правлять,\nдовго житиме\n→ гасити тіло",
                           size=13, color=POS, stroke=POS, fill="#fdecea", bold=True)
    els.append(bh1)
    # ПІД кривою — холодний код
    bc1, bw, bhh = textbox(x0 + xw * 0.30, yb - yh * 0.20,
                           "ХОЛОДНИЙ КОД\nрідко правлять\nабо скоро вмре\n→ лишити брудним",
                           size=13, color=NEG, stroke=NEG, fill="#eaf0fd", bold=True)
    els.append(bc1)

    render(os.path.join(IMG, "hot-cold.svg"), W, H, *els)


if __name__ == "__main__":
    fig_interest_curve()
    fig_quadrant()
    fig_principal_interest()
    fig_blast_radius()
    fig_debt_timeline()
    fig_breakeven()
    fig_hot_cold()
    print("OK: figures written to", IMG)
