# -*- coding: utf-8 -*-
# Фігури теми «Лінійний vs імпульсний» та її історичної вставки.
# svgkit НЕ копіювати — лише імпортувати (§5 AUTHORING).
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── допоміжне: стовпчикове порівняння Вт·год/кг ───────────────────────────────
def _bars(ox, oy, aw, ah, items, unit="Вт·год/кг", barw=70):
    """items = [(назва, значення, колір)]; малює осі + стовпчики з підписами."""
    p = []
    vmax = max(v for _, v, _ in items) * 1.18
    p.append(line(ox, oy, ox, oy - ah, color=INK, sw=1.6))
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    n = len(items)
    gap = (aw - n * barw) / (n + 1)
    for i, (name, v, col) in enumerate(items):
        bx = ox + gap + i * (barw + gap)
        bh = ah * (v / vmax)
        p.append(rect(bx, oy - bh, barw, bh, fill=col, stroke=INK, sw=1.2, rx=3))
        p.append(text(bx + barw / 2, oy - bh - 8, str(v), size=13, color=INK, bold=True))
        p.append(text(bx + barw / 2, oy + 18, name, size=12, color=INK))
    p.append(text(ox - 6, oy - ah, unit, size=11, color=MUTED, anchor="end"))
    return "".join(p)


# ════════════════════════════════════════════════════════════════════════════
#  ТЕМА: linear-vs-switching
# ════════════════════════════════════════════════════════════════════════════

# 1) Одна батарея — багато шин ------------------------------------------------
#    Ідея: з єдиного плавного джерела окремі перетворювачі роблять різні
#    стабільні шини; мотори беруть напругу сирою.
def fig_rails():
    W, H = 760, 420
    p = []
    # батарея зліва
    bx, by, bw, bh = 60, 150, 96, 120
    p.append(rect(bx, by, bw, bh, fill="#eef4ff", stroke=NEG, sw=2, rx=8))
    p.append(mtext(bx + bw / 2, by + 44, ["Батарея 4S", "16.8 → 12 В", "(плаває)"],
                   size=13, color=INK, bold=False))
    p.append(plus(bx + bw / 2, by + 16, 9))
    busx = bx + bw + 40
    p.append(line(bx + bw, by + bh / 2, busx, by + bh / 2, color=INK, sw=2.4))
    p.append(line(busx, 70, busx, 350, color=INK, sw=2.4))  # спільна шина

    rows = [
        (96,  "Мотори",       "сира напруга батареї", "беруть як є", FIELD, True),
        (170, "Імпульсний",   "→ 5 В логіці",         "buck, ~90%",  POS,   False),
        (244, "Імпульсний",   "→ 12 В камері/підвісу", "boost/buck",  POS,   False),
        (318, "Лінійний",     "→ 3.3 В давачам",       "чисто, тихо", NEG,   False),
    ]
    for y, t1, t2, t3, col, raw in rows:
        p.append(line(busx, y, busx + 36, y, color=INK, sw=2))
        if raw:
            p.append(text(busx + 44, y - 6, t1, size=13, color=col, anchor="start", bold=True))
            p.append(text(busx + 44, y + 12, t2, size=12, color=INK, anchor="start"))
        else:
            box, w, h = textbox(busx + 110, y, t1, size=12, color="#fff",
                                fill=col, stroke=col, pad=7, bold=True, min_w=120)
            p.append(box)
            p.append(text(busx + 110 + w / 2 + 12, y + 4, t2, size=12, color=INK, anchor="start"))
        p.append(text(busx + 320, y + 4, t3, size=11, color=MUTED, anchor="start", italic=True))

    render(os.path.join(OUT, "one-battery-many-rails.svg"), W, H,
           *p, title="Одна батарея — багато стабільних шин")


# 2) Лінійний стабілізатор: різницю — у тепло ---------------------------------
#    Ідея: прохідний транзистор гасить надлишок; (Vвх−Vвих)·I стає теплом.
def fig_linear():
    W, H = 760, 380
    p = []
    y = 150
    inx = 70
    p.append(text(inx, y - 22, "16 В", size=14, color=INK, bold=True, anchor="start"))
    p.append(text(inx, y - 4, "вхід", size=11, color=MUTED, anchor="start"))
    p.append(line(inx, y + 10, 250, y + 10, color=INK, sw=2.4))
    # прохідний транзистор як регульований резистор
    tx = 250
    box, w, h = textbox(tx + 70, y + 10, ["прохідний", "транзистор", "(гасить різницю)"],
                        size=12, color=INK, fill=FILL, stroke=POS, sw=2, pad=10)
    p.append(box)
    p.append(line(tx + 70 + w / 2, y + 10, 560, y + 10, color=INK, sw=2.4))
    p.append(text(560, y - 22, "5 В", size=14, color=INK, bold=True, anchor="start"))
    p.append(text(560, y - 4, "вихід", size=11, color=MUTED, anchor="start"))
    p.append(circle(620, y + 10, 4, fill=INK, stroke=INK))
    p.append(line(620, y + 10, 620, y + 70, color=INK, sw=2))
    p.append(text(635, y + 50, "навантаження 1 А", size=11, color=INK, anchor="start"))
    # тепло вгору від транзистора
    for dx in (-14, 0, 14):
        p.append('<path d="M%.0f %.0f q 6 -14 0 -28 q -6 -14 0 -28" fill="none" '
                 'stroke="%s" stroke-width="2"/>' % (tx + 70 + dx, y - h / 2 - 6, POS))
    box2, w2, h2 = textbox(tx + 70, y - 96, ["11 Вт у ТЕПЛО", "(16−5)·1"],
                           size=13, color=POS, fill="#fdecea", stroke=POS, pad=9, bold=True)
    p.append(box2)
    # підсумок ККД
    p.append(textbox(W / 2, 300, "ККД = Vвих / Vвх = 5 / 16 ≈ 31 %   →   тільки 31 % корисні",
                     size=14, color=INK, fill="#eef4ff", stroke=NEG, pad=11, bold=True)[0])

    render(os.path.join(OUT, "linear-burns-difference.svg"), W, H,
           *p, title="Лінійний стабілізатор: надлишок напруги — у тепло")


# 3) Імпульсний перетворювач: чотири деталі -----------------------------------
#    Ідея: ключ ріже вхід, котушка запасає, діод замикає, конденсатор згладжує;
#    енергія не згоряє — звідси ККД 85–95%.
def fig_switching():
    W, H = 780, 380
    p = []
    y = 160
    inx = 60
    p.append(text(inx, y - 18, "вхід", size=12, color=MUTED, anchor="start"))
    p.append(line(inx, y, 150, y, color=INK, sw=2.4))
    # ключ MOSFET
    sx = 150
    p.append(rect(sx, y - 26, 70, 52, fill=FILL, stroke=POS, sw=2, rx=6))
    p.append(mtext(sx + 35, y - 2, ["ключ", "MOSFET"], size=12, color=INK))
    # котушка
    lx = sx + 70 + 40
    coil = '<path d="M%.0f %.0f' % (sx + 70, y)
    coil += ' h40'
    for k in range(4):
        coil += ' a8 8 0 1 1 16 0'
    coil += ' h40" fill="none" stroke="%s" stroke-width="2.6"/>' % INK
    p.append(coil)
    p.append(text(lx + 24, y - 22, "котушка L", size=12, color=INK, bold=True))
    p.append(text(lx + 24, y + 30, "запасає поле", size=11, color=MUTED))
    # вузол + діод донизу + конденсатор + вихід
    nodex = lx + 130
    p.append(line(lx + 88, y, nodex, y, color=INK, sw=2.4))
    p.append(circle(nodex, y, 4, fill=INK, stroke=INK))
    # діод донизу (від землі до вузла)
    p.append(line(nodex - 70, y, nodex - 70, y + 80, color=INK, sw=2))
    p.append(line(nodex - 70, y, nodex, y, color=INK, sw=2.4))
    dt = nodex - 70
    p.append('<path d="M%.0f %.0f L%.0f %.0f L%.0f %.0f z" fill="%s"/>'
             % (dt - 9, y + 52, dt + 9, y + 52, dt, y + 38, INK))
    p.append(line(dt - 9, y + 38, dt + 9, y + 38, color=INK, sw=2.4))
    p.append(text(dt - 14, y + 48, "діод", size=11, color=INK, anchor="end"))
    # конденсатор донизу від вузла
    p.append(line(nodex, y, nodex, y + 40, color=INK, sw=2))
    p.append(line(nodex - 14, y + 40, nodex + 14, y + 40, color=INK, sw=3))
    p.append(line(nodex - 14, y + 48, nodex + 14, y + 48, color=INK, sw=3))
    p.append(text(nodex + 20, y + 48, "конденсатор", size=11, color=INK, anchor="start"))
    # земля
    p.append(line(dt, y + 80, nodex, y + 80, color=INK, sw=2))
    p.append(line(nodex, y + 48, nodex, y + 80, color=INK, sw=2))
    gy = y + 80
    p.append(line(dt, gy, nodex, gy, color=INK, sw=2))
    # вихід
    p.append(line(nodex, y, nodex + 90, y, color=INK, sw=2.4))
    p.append(text(nodex + 90, y - 18, "вихід", size=12, color=MUTED, anchor="end"))
    # бейдж ККД
    p.append(textbox(W / 2, 320, "енергія не згоряє — передається пакетами   →   ККД 85–95 %",
                     size=14, color=INK, fill="#eafaf1", stroke=FIELD, pad=11, bold=True)[0])

    render(os.path.join(OUT, "switching-moves-energy.svg"), W, H,
           *p, title="Імпульсний перетворювач: ключ · котушка · діод · конденсатор")


# 4) ККД vs перепад: лінійний падає, імпульсний тримає ------------------------
#    Ідея: ККД лінійного = Vвих/Vвх (пряма донизу), імпульсного ≈ 90% (рівно).
def fig_efficiency():
    W, H = 720, 420
    ox, oy = 90, 330
    aw, ah = 560, 250
    p = []
    p.append(line(ox, oy, ox, oy - ah - 6, color=INK, sw=1.8))
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.8))
    # вісь Y: 0..100%
    for pct in (0, 25, 50, 75, 100):
        yy = oy - ah * pct / 100
        p.append(line(ox - 5, yy, ox, yy, color=INK, sw=1.4))
        p.append(text(ox - 10, yy + 4, "%d%%" % pct, size=11, color=MUTED, anchor="end"))
    p.append(text(ox - 4, oy - ah - 14, "ККД", size=12, color=INK, bold=True, anchor="middle"))
    p.append(text(ox + aw, oy + 22, "перепад Vвх (вхід зростає) →", size=12,
                  color=INK, italic=True, anchor="end"))

    # лінійний: ККД = Vвих/Vвх, Vвих=5, Vвх від 5.5 до 20
    pts = []
    vin_lo, vin_hi = 5.5, 20.0
    for i in range(0, 121):
        vin = vin_lo + (vin_hi - vin_lo) * i / 120
        eff = 5.0 / vin
        x = ox + aw * (vin - vin_lo) / (vin_hi - vin_lo)
        yy = oy - ah * eff
        pts.append("%.1f,%.1f" % (x, yy))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join(pts), POS))
    # імпульсний: ~90% рівно
    ys = oy - ah * 0.90
    p.append(line(ox, ys, ox + aw, ys, color=FIELD, sw=2.8, dash="2 0"))

    # точка-приклад 16 В
    vx = ox + aw * (16 - vin_lo) / (vin_hi - vin_lo)
    p.append(line(vx, oy, vx, oy - ah, color=MUTED, sw=1, dash="4 4"))
    p.append(text(vx, oy + 18, "16 В", size=11, color=INK))
    p.append(circle(vx, oy - ah * (5.0 / 16), 4.5, fill=POS, stroke=POS))
    p.append(circle(vx, ys, 4.5, fill=FIELD, stroke=FIELD))

    # підписи кривих + втрати
    p.append(text(ox + aw - 8, ys - 10, "імпульсний ≈ 90 %  (втрати ~1 Вт)",
                  size=12, color=FIELD, anchor="end", bold=True))
    p.append(text(vx + 12, oy - ah * (5.0 / 16) + 24, "лінійний = Vвих/Vвх",
                  size=12, color=POS, anchor="start", bold=True))
    p.append(text(vx + 12, oy - ah * (5.0 / 16) + 42, "31 % за 16 В  (втрати 11 Вт)",
                  size=11, color=POS, anchor="start"))

    render(os.path.join(OUT, "efficiency-vs-drop.svg"), W, H,
           *p, title="ККД проти перепаду напруги")


# ════════════════════════════════════════════════════════════════════════════
#  ДЕТАЛЬНА (-d): ККД проти СТРУМУ — обидва типи -------------------------------
#  Ідея: лінійний = стеля Vвих/Vвх на всьому струмі, але провал зліва (Iq);
#  імпульсний = горб (провал зліва — сталі втрати, спад справа — I²R).
def fig_eff_vs_current():
    W, H = 760, 440
    ox, oy = 90, 340
    aw, ah = 590, 260
    p = []
    # осі
    p.append(line(ox, oy, ox, oy - ah - 6, color=INK, sw=1.8))
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.8))
    for pct in (0, 25, 50, 75, 100):
        yy = oy - ah * pct / 100
        p.append(line(ox - 5, yy, ox, yy, color=INK, sw=1.4))
        p.append(text(ox - 10, yy + 4, "%d%%" % pct, size=11, color=MUTED, anchor="end"))
    p.append(text(ox - 4, oy - ah - 14, "ККД", size=12, color=INK, bold=True))
    p.append(text(ox + aw, oy + 24, "струм навантаження (log) →", size=12,
                  color=INK, italic=True, anchor="end"))

    # вісь X — умовна лог-шкала струму: мітки
    for frac, lab in ((0.02, "мкА"), (0.28, "мА"), (0.62, "100 мА"), (0.95, "А")):
        xx = ox + aw * frac
        p.append(line(xx, oy, xx, oy + 5, color=INK, sw=1.2))
        p.append(text(xx, oy + 20, lab, size=10, color=MUTED))

    def X(f):
        return ox + aw * f

    def Y(e):
        return oy - ah * e

    # світла зона зліва — де лінійний виграє
    p.append(rect(ox, oy - ah, aw * 0.12, ah, fill="#eef7ee", stroke="none", rx=0))
    p.append(text(ox + aw * 0.06, oy - ah + 16, "тут", size=10, color=FIELD, bold=True))
    p.append(text(ox + aw * 0.06, oy - ah + 30, "лінійний", size=10, color=FIELD))
    p.append(text(ox + aw * 0.06, oy - ah + 44, "переганяє", size=10, color=FIELD))

    # лінійний: стеля Vвих/Vвх (тут ≈0.92, малий перепад), провал зліва через Iq
    ceil = 0.92
    lin = []
    for i in range(0, 121):
        f = i / 120.0
        # зліва Iq домінує → ефективність мала; далі виходить на стелю
        # модель: eff = ceil * Iнав/(Iнав+Iq); Iнав ~ 10^(f*5) відн., Iq ~ const
        Inav = 10 ** (f * 5)          # від 1 до 1e5 (умовні одиниці)
        Iq = 30.0                      # струм спокою в тих же одиницях
        eff = ceil * Inav / (Inav + Iq)
        lin.append("%.1f,%.1f" % (X(f), Y(eff)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join(lin), NEG))

    # імпульсний: горб — провал зліва (сталі втрати), спад справа (I²R)
    sw = []
    for i in range(0, 121):
        f = i / 120.0
        Inav = 10 ** (f * 5)
        # сталі втрати (P_qui+P_switch) ~ const; провідна ~ Inav (як частка → росте з Inav)
        Pout = Inav
        Pconst = 45.0
        Pcond = Inav * Inav / 6.0e4    # квадратична складова
        eff = 0.95 * Pout / (Pout + Pconst + Pcond)
        sw.append("%.1f,%.1f" % (X(f), Y(eff)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join(sw), FIELD))

    # підписи кривих
    p.append(text(X(0.60), Y(0.92) - 10, "лінійний (стеля Vвих/Vвх)",
                  size=12, color=NEG, anchor="start", bold=True))
    p.append(text(X(0.42), Y(0.955) - 10, "імпульсний (горб)",
                  size=12, color=FIELD, anchor="middle", bold=True))
    p.append(text(X(0.02), Y(0.30), "провал", size=9, color=FIELD, anchor="start"))
    p.append(text(X(0.90), Y(0.72), "спад I²R", size=10, color=FIELD, anchor="end"))

    render(os.path.join(OUT, "efficiency-vs-current-both.svg"), W, H,
           *p, title="ККД проти струму: лінійний — стеля, імпульсний — горб")


# ДЕТАЛЬНА (-d): дерево живлення (гібрид buck+boost+LDO) -----------------------
#    Ідея: батарея → імпульсні головні гілки → лінійні листки для чутливого.
def fig_power_tree():
    W, H = 820, 470
    p = []
    # батарея зліва
    bx, by, bw, bh = 40, 200, 110, 90
    p.append(rect(bx, by, bw, bh, fill="#eef4ff", stroke=NEG, sw=2, rx=8))
    p.append(mtext(bx + bw / 2, by + 38, ["Батарея 4S", "16.8→12 В", "(брудна)"],
                   size=12, color=INK))
    p.append(plus(bx + bw / 2, by + 14, 8))

    trunkx = bx + bw + 26
    ty = by + bh / 2
    p.append(line(bx + bw, ty, trunkx, ty, color=INK, sw=2.6))
    p.append(line(trunkx, 70, trunkx, 400, color=INK, sw=2.6))  # стовбур

    def node(x, y, lines, col, kind):
        bxx = textbox(x, y, lines, size=11, color="#fff", fill=col, stroke=col,
                      pad=8, bold=True, min_w=118)
        return bxx

    # мотори — сира напруга (нагору)
    p.append(line(trunkx, 96, trunkx + 40, 96, color=INK, sw=2))
    p.append(text(trunkx + 48, 92, "Мотори / ESC", size=12, color=FIELD, anchor="start", bold=True))
    p.append(text(trunkx + 48, 108, "беруть батарею сирою", size=11, color=MUTED, anchor="start", italic=True))

    # головний buck 5 В
    y5 = 175
    p.append(line(trunkx, y5, trunkx + 30, y5, color=INK, sw=2))
    box5, w5, h5 = node(trunkx + 30 + 60, y5, ["buck → 5 В", "ККД ~90%"], POS, "sw")
    p.append(box5)
    x5r = trunkx + 30 + 60 + w5 / 2
    p.append(text(x5r + 8, y5 - 4, "головна шина (великий струм)", size=10,
                  color=MUTED, anchor="start", italic=True))

    # від 5 В далі вниз — під-стовбур
    sub5x = x5r
    p.append(line(sub5x, y5 + h5 / 2, sub5x, 330, color=INK, sw=2))

    # buck 3.3 В цифри від 5 В
    y33 = 265
    p.append(line(sub5x, y33, sub5x + 30, y33, color=INK, sw=2))
    box33, w33, h33 = node(sub5x + 30 + 62, y33, ["buck → 3.3 В", "цифра"], POS, "sw")
    p.append(box33)
    x33r = sub5x + 30 + 62 + w33 / 2

    # LDO 3.3 аналог від 3.3 цифри
    p.append(line(x33r, y33 + h33 / 2, x33r, y33 + 55, color=INK, sw=2))
    ylo = y33 + 55
    boxlo, wlo, hlo = node(x33r + 70, ylo, ["LDO → 3.3 В", "аналог (чисто)"], NEG, "lin")
    p.append(boxlo)
    p.append(text(x33r + 70 + wlo / 2 + 8, ylo - 4, "малий перепад → PSRR зрізає шум",
                  size=10, color=MUTED, anchor="start", italic=True))
    p.append(text(x33r + 70 + wlo / 2 + 8, ylo + 11, "для АЦП і радіо",
                  size=10, color=MUTED, anchor="start", italic=True))

    # boost 12 В від батареї (низ стовбура)
    y12 = 380
    p.append(line(trunkx, y12, trunkx + 30, y12, color=INK, sw=2))
    box12, w12, h12 = node(trunkx + 30 + 62, y12, ["boost → 12 В", "підвіс"], POS, "sw")
    p.append(box12)
    p.append(text(trunkx + 30 + 62 + w12 / 2 + 8, y12 - 4, "підіймає, коли батарея просіла",
                  size=10, color=MUTED, anchor="start", italic=True))

    # легенда
    p.append(rect(W - 210, 60, 190, 66, fill="#fff", stroke=MUTED, sw=1.2, rx=6))
    p.append(rect(W - 200, 74, 16, 12, fill=POS, stroke=POS))
    p.append(text(W - 178, 84, "імпульсний (ККД)", size=11, color=INK, anchor="start"))
    p.append(rect(W - 200, 98, 16, 12, fill=NEG, stroke=NEG))
    p.append(text(W - 178, 108, "лінійний (чистота)", size=11, color=INK, anchor="start"))

    render(os.path.join(OUT, "power-tree-hybrid.svg"), W, H,
           *p, title="Дерево живлення: імпульсні — гілки, лінійні — листя")


# ════════════════════════════════════════════════════════════════════════════
#  ВСТАВКА: math-loss-breakdown
# ════════════════════════════════════════════════════════════════════════════

# 1) Стос втрат від струму: чотири механізми складаються в повну втрату --------
#    Ідея: quiescent+gate — сталі (горизонтальні смуги), switching — стала при
#    сталій f, conduction (I²R) — росте квадратично. Стос показує, ЩО домінує
#    зліва (сталі) і справа (провідна).
def fig_loss_stack():
    W, H = 780, 460
    ox, oy = 92, 350
    aw, ah = 590, 280
    p = []
    # осі
    p.append(line(ox, oy, ox, oy - ah - 6, color=INK, sw=1.8))
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.8))
    p.append(text(ox - 6, oy - ah - 14, "втрата, Вт", size=12, color=INK, bold=True, anchor="middle"))
    p.append(text(ox + aw, oy + 24, "струм навантаження I →", size=12,
                  color=INK, italic=True, anchor="end"))

    Imax = 3.0            # А по осі
    Pmax = 1.0            # Вт — верх осі
    def X(I): return ox + aw * (I / Imax)
    def Y(P): return oy - ah * (P / Pmax)

    # мітки осі Y
    for pw in (0.0, 0.25, 0.5, 0.75, 1.0):
        yy = Y(pw)
        p.append(line(ox - 5, yy, ox, yy, color=INK, sw=1.2))
        p.append(text(ox - 9, yy + 4, "%.2f" % pw, size=10, color=MUTED, anchor="end"))
    for I in (1, 2, 3):
        xx = X(I)
        p.append(line(xx, oy, xx, oy + 5, color=INK, sw=1.2))
        p.append(text(xx, oy + 19, "%d А" % I, size=11, color=MUTED))

    # константи з worked-прикладу (гарячі)
    Rtot = 0.030          # Ом сумарний провідний (Rds·D + Rdcr), гарячий
    Pconst_qui = 0.02     # quiescent (Вт) — тонка база
    Pconst_gate = 0.06    # gate-drive при робочій f (Вт)
    Psw0 = 0.12           # switching при робочій f (Вт), майже сталий від I тут

    N = 120
    # рівні стосу (кумулятивно знизу вгору)
    def band(pfun_lo, pfun_hi, col, op="0.85"):
        top = []; bot = []
        for i in range(N + 1):
            I = Imax * i / N
            top.append("%.1f,%.1f" % (X(I), Y(pfun_hi(I))))
        for i in range(N, -1, -1):
            I = Imax * i / N
            bot.append("%.1f,%.1f" % (X(I), Y(pfun_lo(I))))
        return ('<polygon points="%s %s" fill="%s" fill-opacity="%s" stroke="none"/>'
                % (" ".join(top), " ".join(bot), col, op))

    L0 = lambda I: 0.0
    L1 = lambda I: Pconst_qui
    L2 = lambda I: Pconst_qui + Pconst_gate
    L3 = lambda I: Pconst_qui + Pconst_gate + Psw0
    L4 = lambda I: Pconst_qui + Pconst_gate + Psw0 + Rtot * I * I

    p.append(band(L0, L1, "#9b59b6"))     # quiescent — фіолетовий
    p.append(band(L1, L2, "#2457d6"))     # gate — синій
    p.append(band(L2, L3, "#e67e22"))     # switching — помаранч
    p.append(band(L3, L4, "#c0392b", "0.80"))  # conduction I²R — червоний

    # верхня межа повних втрат
    tot = []
    for i in range(N + 1):
        I = Imax * i / N
        tot.append("%.1f,%.1f" % (X(I), Y(L4(I))))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join(tot), INK))

    # пунктир на межі, де провідна зрівнюється зі сталими (I★)
    Pconst = Pconst_qui + Pconst_gate + Psw0
    Istar = (Pconst / Rtot) ** 0.5
    p.append(line(X(Istar), oy, X(Istar), Y(L4(Istar)), color=INK, sw=1.2, dash="4 4"))
    p.append(text(X(Istar), oy + 34, "I★ ≈ %.1f А" % Istar, size=11, color=INK, bold=True))
    p.append(text(X(Istar), Y(L4(Istar)) - 10, "сталі = провідна", size=10, color=INK))

    # легенда
    lx, ly = ox + 14, oy - ah + 8
    leg = [("провідна  I²·R (росте)", "#c0392b"),
           ("перемиканнєва  ∝ f", "#e67e22"),
           ("затвор  Qg·Vg·f", "#2457d6"),
           ("спокою  Iq·Vвх", "#9b59b6")]
    for i, (t, c) in enumerate(leg):
        yy = ly + i * 20
        p.append(rect(lx, yy - 10, 15, 12, fill=c, stroke=c))
        p.append(text(lx + 22, yy, t, size=11, color=INK, anchor="start"))

    render(os.path.join(OUT, "loss-stack-vs-current.svg"), W, H,
           *p, title="Стос втрат перетворювача: сталі зліва, провідна справа")


# 2) Крива ККД від струму з піком I★ і двома схилами ---------------------------
#    Ідея: η(I) = P_out/(P_out+P_const+I²R). Зліва падає через сталі втрати
#    (Δη ~ 1/I), справа — через I²R (Δη ~ I). Пік рівно там, де вони рівні.
def fig_eff_peak():
    W, H = 780, 460
    ox, oy = 92, 350
    aw, ah = 590, 285
    p = []
    p.append(line(ox, oy, ox, oy - ah - 6, color=INK, sw=1.8))
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.8))
    p.append(text(ox - 4, oy - ah - 14, "ККД η", size=12, color=INK, bold=True))
    p.append(text(ox + aw, oy + 24, "струм навантаження I (log) →", size=12,
                  color=INK, italic=True, anchor="end"))

    # модель
    Vout = 5.0
    Rtot = 0.030
    Pconst = 0.20         # сталі (qui+gate+switch)
    ceil = 1.0

    # вісь Y 0..100%
    for pct in (0, 25, 50, 75, 100):
        yy = oy - ah * pct / 100
        p.append(line(ox - 5, yy, ox, yy, color=INK, sw=1.2))
        p.append(text(ox - 9, yy + 4, "%d%%" % pct, size=10, color=MUTED, anchor="end"))

    # лог-шкала струму від 3 мА до 5 А
    import math as _m
    Ilo, Ihi = 0.003, 5.0
    def X(I): return ox + aw * (_m.log10(I) - _m.log10(Ilo)) / (_m.log10(Ihi) - _m.log10(Ilo))
    def Y(e): return oy - ah * e
    for I, lab in ((0.003, "3 мА"), (0.03, "30 мА"), (0.3, "0.3 А"), (3.0, "3 А")):
        xx = X(I)
        p.append(line(xx, oy, xx, oy + 5, color=INK, sw=1.2))
        p.append(text(xx, oy + 19, lab, size=10, color=MUTED))

    # крива η(I)
    pts = []
    N = 240
    for i in range(N + 1):
        I = 10 ** (_m.log10(Ilo) + (_m.log10(Ihi) - _m.log10(Ilo)) * i / N)
        Pout = Vout * I
        eff = ceil * Pout / (Pout + Pconst + Rtot * I * I)
        pts.append("%.1f,%.1f" % (X(I), Y(eff)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join(pts), FIELD))

    # пік: I★ = sqrt(Pconst/Rtot)
    Istar = (Pconst / Rtot) ** 0.5
    Pout_s = Vout * Istar
    eff_s = ceil * Pout_s / (Pout_s + Pconst + Rtot * Istar * Istar)
    p.append(line(X(Istar), oy, X(Istar), Y(eff_s), color=INK, sw=1.2, dash="4 4"))
    p.append(circle(X(Istar), Y(eff_s), 5, fill=POS, stroke=POS))
    p.append(text(X(Istar), Y(eff_s) - 12, "пік η   I★ = √(Pсталі/R)",
                  size=12, color=POS, bold=True))
    p.append(text(X(Istar), oy + 34, "I★ ≈ %.1f А" % Istar, size=11, color=INK, bold=True))

    # підписи двох схилів
    p.append(text(X(0.02), Y(0.42), "сталі втрати", size=11, color=NEG, anchor="middle", bold=True))
    p.append(text(X(0.02), Y(0.42) + 15, "з'їдають", size=10, color=NEG, anchor="middle"))
    p.append(text(X(0.02), Y(0.42) + 28, "малий струм", size=10, color=NEG, anchor="middle"))
    p.append(text(X(4.6), Y(0.62), "I²R", size=12, color=POS, anchor="end", bold=True))
    p.append(text(X(4.6), Y(0.62) + 14, "тягне вниз", size=10, color=POS, anchor="end"))

    render(os.path.join(OUT, "efficiency-peak-vs-current.svg"), W, H,
           *p, title="Крива ККД: пік там, де сталі втрати зрівнялися з I²R")


# ════════════════════════════════════════════════════════════════════════════
#  ВСТАВКА: proj-power-mode-select — автомат живлення RUN ↔ SLEEP
# ════════════════════════════════════════════════════════════════════════════

# Ідея: два стабільні стани (RUN / SLEEP) і дзеркальні переходи між ними;
# на вхід у сон MCU перекидається на LDO ПЕРШИМ, шини гасяться у зворотному
# порядку, buck іде в пропуск; на вихід — buck у PWM, шини за порядком із
# очікуванням PGOOD, MCU назад на buck ОСТАННІМ.
def fig_power_mode_fsm():
    W, H = 860, 560
    p = []

    # два стани: великі рамки зліва (RUN) і справа (SLEEP)
    rx1, ry, rw, rh = 40, 210, 210, 150
    rx2 = W - 40 - rw
    p.append(rect(rx1, ry, rw, rh, fill="#eafaf1", stroke=FIELD, sw=2.4, rx=12))
    p.append(text(rx1 + rw / 2, ry + 30, "СТАН: RUN", size=16, color=FIELD, bold=True))
    p.append(mtext(rx1 + rw / 2, ry + 60, [
        "buck → повний PWM", "усі шини живі",
        "MCU живиться від buck", "(ефективно)"], size=12, color=INK))

    p.append(rect(rx2, ry, rw, rh, fill="#eef4ff", stroke=NEG, sw=2.4, rx=12))
    p.append(text(rx2 + rw / 2, ry + 30, "СТАН: SLEEP", size=16, color=NEG, bold=True))
    p.append(mtext(rx2 + rw / 2, ry + 60, [
        "buck → пропуск (PFM)", "зайві шини вимкнені",
        "MCU живиться від LDO", "(тихо, мкА)"], size=12, color=INK))

    ax1, ax2 = rx1 + rw, rx2

    # верхня дуга: RUN → SLEEP (вхід у сон)
    top_y = 118
    p.append('<path d="M%.0f %.0f C %.0f %.0f, %.0f %.0f, %.0f %.0f" '
             'fill="none" stroke="%s" stroke-width="2.4" marker-end="url(#arrow)"/>'
             % (ax1, ry + 28, ax1 + 90, top_y, ax2 - 90, top_y, ax2, ry + 28, POS))
    steps_down = [
        "1. MCU → LDO (make-before-break)",
        "2. шини OFF у зворотному порядку",
        "3. buck → режим пропуску",
    ]
    box, w, h = textbox(W / 2, top_y + 8, steps_down, size=12, color=INK,
                        fill="#fdecea", stroke=POS, pad=11, min_w=330)
    p.append(box)
    p.append(text(W / 2, top_y - h / 2 - 4, "вхід у сон", size=13,
                  color=POS, bold=True))

    # нижня дуга: SLEEP → RUN (прокидання)
    bot_y = 452
    p.append('<path d="M%.0f %.0f C %.0f %.0f, %.0f %.0f, %.0f %.0f" '
             'fill="none" stroke="%s" stroke-width="2.4" marker-end="url(#arrow)"/>'
             % (ax2, ry + rh - 28, ax2 - 90, bot_y, ax1 + 90, bot_y, ax1, ry + rh - 28, FIELD))
    steps_up = [
        "1. buck → повний PWM",
        "2. шини ON за порядком, КОЖНА чекає PGOOD",
        "3. MCU → buck (останнім)",
    ]
    box2, w2, h2 = textbox(W / 2, bot_y - 6, steps_up, size=12, color=INK,
                           fill="#eafaf1", stroke=FIELD, pad=11, min_w=360)
    p.append(box2)
    p.append(text(W / 2, bot_y + h2 / 2 + 18, "прокидання", size=13,
                  color=FIELD, bold=True))

    # підпис-мораль про дзеркальність унизу
    p.append(text(W / 2, H - 14,
                  "MCU: на LDO — ПЕРШИМ у сон, на buck — ОСТАННІМ з нього; "
                  "шини дзеркально; PGOOD вартує кожне вмикання",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "power-mode-fsm.svg"), W, H,
           *p, title="Автомат живлення: RUN ↔ SLEEP через дзеркальні переходи")


# ════════════════════════════════════════════════════════════════════════════
#  ВСТАВКА: hist-lithium
# ════════════════════════════════════════════════════════════════════════════

# 1) Чому літій — питома енергія -----------------------------------------------
def fig_why_lithium():
    W, H = 720, 380
    p = [_bars(90, 300, 560, 220, [
        ("свинець-\nкислота", 35, "#9aa6b2"),
        ("нікель-\nметал-гідрид", 80, "#7f8fa6"),
        ("літій-іон", 250, FIELD),
    ])]
    # багаторядкові підписи під віссю — домалюємо власноруч (другий рядок)
    render(os.path.join(OUT, "why-lithium-energy.svg"), W, H,
           *p, title="Чому літій: питома енергія, Вт·год/кг")


# 2) Три внески → Sony --------------------------------------------------------
def fig_three_men():
    W, H = 820, 360
    p = []
    y = 170
    nodes = [
        ("Віттінгем", "~1976", ["перший", "перезаряджуваний", "(літій-метал —", "небезпечно)"], NEG),
        ("Гуденаф", "1980", ["катод LiCoO₂", "напруга ×2", "(2 → 4 В)"], INK),
        ("Йосіно", "1985", ["анод-вуглець", "прибрав", "металевий літій"], FIELD),
        ("Sony", "1991", ["перший", "товар на ринку"], POS),
    ]
    n = len(nodes)
    gap = 30
    bw = (W - 80 - (n - 1) * gap) / n
    x = 40
    for i, (name, yr, lines, col) in enumerate(nodes):
        p.append(rect(x, y - 70, bw, 140, fill="#fff", stroke=col, sw=2.2, rx=10))
        p.append(text(x + bw / 2, y - 44, name, size=14, color=col, bold=True))
        p.append(text(x + bw / 2, y - 26, yr, size=12, color=MUTED))
        p.append(mtext(x + bw / 2, y - 2, lines, size=11, color=INK))
        if i < n - 1:
            ax = x + bw
            p.append(arrow(ax + 4, y, ax + gap - 4, y, color=INK, sw=2))
        x += bw + gap

    render(os.path.join(OUT, "three-men-to-sony.svg"), W, H,
           *p, title="Літій-іон збирали троє вчених — реле внесків")


# 3) Принцип «крісла-гойдалки» ------------------------------------------------
def fig_rocking_chair():
    W, H = 760, 400
    p = []
    # два електроди
    cx1, cx2 = 150, 610
    ey, eh = 110, 200
    p.append(rect(cx1 - 30, ey, 60, eh, fill="#fdecea", stroke=POS, sw=2, rx=6))
    p.append(rect(cx2 - 30, ey, 60, eh, fill="#eef4ff", stroke=NEG, sw=2, rx=6))
    p.append(mtext(cx1, ey - 16, ["катод", "LiCoO₂"], size=12, color=POS, bold=True))
    p.append(mtext(cx2, ey - 16, ["анод", "графіт"], size=12, color=NEG, bold=True))
    # шари
    for k in range(1, 6):
        yy = ey + eh * k / 6
        p.append(line(cx1 - 26, yy, cx1 + 26, yy, color=POS, sw=1))
        p.append(line(cx2 - 26, yy, cx2 + 26, yy, color=NEG, sw=1))
    # електроліт між ними
    p.append(text(W / 2, ey - 16, "електроліт (проводить іони Li⁺)", size=12,
                  color=MUTED))
    # іони течуть (заряд: катод → анод)
    midy = ey + eh / 2
    p.append(arrow(cx1 + 36, midy - 24, cx2 - 36, midy - 24, color=INK, sw=2))
    p.append(text(W / 2, midy - 30, "заряд: Li⁺ →", size=11, color=INK))
    p.append(arrow(cx2 - 36, midy + 24, cx1 + 36, midy + 24, color=INK, sw=2))
    p.append(text(W / 2, midy + 40, "← розряд: Li⁺", size=11, color=INK))
    for fx in (260, 360, 460):
        p.append(circle(fx, midy, 7, fill="#fff3cd", stroke="#b8860b", sw=1.5))
        p.append(text(fx, midy + 4, "Li⁺", size=9, color="#7a5b00"))
    # зовнішнє коло — електрони
    p.append(line(cx1, ey, cx1, 60, color=INK, sw=2))
    p.append(line(cx1, 60, cx2, 60, color=INK, sw=2))
    p.append(line(cx2, 60, cx2, ey, color=INK, sw=2))
    p.append(rect(W / 2 - 40, 44, 80, 32, fill=FILL, stroke=INK, sw=1.5, rx=6))
    p.append(text(W / 2, 64, "апарат", size=12, color=INK))
    p.append(text(W / 2, 96, "електрони йдуть зовнішнім колом — це струм", size=11,
                  color=MUTED))

    render(os.path.join(OUT, "rocking-chair-ions.svg"), W, H,
           *p, title="Принцип «крісла-гойдалки»: іони снують між шарами")


# 4) Батарея — серце й слабке місце (трикутник компромісу) --------------------
def fig_drone_battery():
    W, H = 720, 420
    p = []
    # трикутник компромісу
    cx, cy, r = W / 2, 250, 150
    pts = []
    labels = [("Енергія", "Вт·год/кг", FIELD), ("Потужність", "C-rate", POS),
              ("Безпека", "ризик пожежі", NEG)]
    coords = []
    for i in range(3):
        ang = -math.pi / 2 + i * 2 * math.pi / 3
        x = cx + r * math.cos(ang)
        yy = cy + r * math.sin(ang)
        coords.append((x, yy))
        pts.append("%.1f,%.1f" % (x, yy))
    p.append('<polygon points="%s" fill="#f4f6f8" stroke="%s" stroke-width="2"/>'
             % (" ".join(pts), INK))
    for (x, yy), (t1, t2, col) in zip(coords, labels):
        ang = math.atan2(yy - cy, x - cx)
        lx = x + 18 * math.cos(ang)
        ly = yy + 18 * math.sin(ang)
        anc = "middle" if abs(x - cx) < 30 else ("start" if x > cx else "end")
        p.append(circle(x, yy, 6, fill=col, stroke=col))
        p.append(text(lx, ly - 4, t1, size=14, color=col, bold=True, anchor=anc))
        p.append(text(lx, ly + 13, t2, size=11, color=MUTED, anchor=anc))
    p.append(mtext(cx, cy - 6, ["не можна", "мати все", "одразу"], size=12, color=INK))
    p.append(text(cx, 60, "Батарея — найбільший шматок ваги дрона", size=13,
                  color=INK, bold=True))
    p.append(text(cx, 80, "і його головна єдина точка відмови", size=12, color=MUTED))

    render(os.path.join(OUT, "battery-tradeoff-triangle.svg"), W, H,
           *p, title="Батарея: компроміс енергія · потужність · безпека")


if __name__ == "__main__":
    fig_rails()
    fig_linear()
    fig_switching()
    fig_efficiency()
    fig_eff_vs_current()
    fig_power_tree()
    fig_loss_stack()
    fig_eff_peak()
    fig_power_mode_fsm()
    fig_why_lithium()
    fig_three_men()
    fig_rocking_chair()
    fig_drone_battery()
    print("OK: фігури згенеровано у", OUT)
