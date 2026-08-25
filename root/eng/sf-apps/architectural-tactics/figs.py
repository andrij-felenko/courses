# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: анатомія тактики — стимул → елемент із рішенням → виміряна відповідь ──
def fig_anatomy():
    W, H = 760, 300
    p = []
    # ліворуч — стимул
    b1, w1, h1 = textbox(115, 150, ["Стимул", "запит приходить,", "коли база лежить"], size=13, pad=12)
    p.append(b1)
    # центр — елемент, у якому ухвалено ОДНЕ рішення
    ex, ey, ew, eh = 300, 95, 170, 110
    p.append(rect(ex, ey, ew, eh, fill="#eef7ff", stroke=NEG, sw=2))
    p.append(text(ex + ew / 2, ey + 24, "Елемент системи", size=13, bold=True))
    p.append(line(ex + 14, ey + 36, ex + ew - 14, ey + 36, color=MUTED, sw=1))
    p.append(mtext(ex + ew / 2, ey + 58, ["одне рішення:", "«поверни кеш,", "не чекай базу»"], size=12, color=NEG))
    # тактика — це саме ця «начинка» елемента
    p.append(text(ex + ew / 2, ey + eh + 26, "= ТАКТИКА", size=14, bold=True, color=POS))
    # праворуч — виміряна відповідь
    b3, w3, h3 = textbox(650, 150, ["Відповідь", "(вимірна)", "", "< 200 мс", "замість збою"], size=13, pad=12, stroke=FIELD, sw=2)
    p.append(b3)
    # стрілки
    p.append(arrow(115 + w1 / 2, 150, ex - 6, 150))
    p.append(arrow(ex + ew + 6, 150, 650 - w3 / 2 - 6, 150))
    render(os.path.join(OUT, 'anatomy.svg'), W, H, *p,
           title="Тактика — одне рішення, що перетворює стимул на вимірну відповідь")


# ── Фігура 2: одна турбота (доступність) фанає у сім'ї атомарних тактик ──
def fig_menu():
    W, H = 820, 430
    p = []
    # корінь — якісний атрибут
    root, rw, rh = textbox(410, 60, "Турбота: ДОСТУПНІСТЬ", size=15, pad=14, bold=True, fill="#eef7ff", stroke=NEG, sw=2)
    p.append(root)

    fams = [
        (150, "Виявити збій", ["ping/echo", "heartbeat", "таймаут", "монітор"]),
        (410, "Оговтатись", ["retry", "перемкнути", "на резерв", "відкотити стан"]),
        (670, "Не допустити", ["зняти з ротації", "обмежити доступ", "транзакція"]),
    ]
    fy = 175
    for fx, fname, tactics in fams:
        fb, fw, fh = textbox(fx, fy, fname, size=13, pad=11, bold=True, fill="#f0f0f0")
        p.append(fb)
        p.append(arrow(410, 60 + rh / 2, fx, fy - fh / 2 - 4))
        # меню атомарних тактик під сім'єю
        ty = fy + fh / 2 + 40
        for t in tactics:
            tb, tw, th = textbox(fx, ty, t, size=12, pad=8, stroke=POS, min_w=150)
            p.append(tb)
            ty += th + 12
    render(os.path.join(OUT, 'menu.svg'), W, H, *p,
           title="Атрибут → сім'ї тактик → меню атомарних рішень")


# ── Фігура 3: патерн = зібраний пакет тактик із зафіксованим компромісом ──
def fig_pattern():
    W, H = 780, 360
    p = []
    # велика рамка патерна
    px, py, pw, ph = 60, 70, 660, 220
    p.append(rect(px, py, pw, ph, fill="#f7f7f7", stroke=INK, sw=2.2))
    p.append(text(px + pw / 2, py + 30, "ПАТЕРН: «запобіжник» (circuit breaker)", size=15, bold=True))
    p.append(text(px + pw / 2, py + 52, "компроміс уже зашитий усередині — ти береш пакет цілком", size=12, color=MUTED, italic=True))

    cells = [
        ("виявити", ["таймаут на", "виклик"]),
        ("не допустити", ["полічити збої,", "розімкнути"]),
        ("оговтатись", ["пробний запит,", "замкнути назад"]),
    ]
    cw, gap = 190, 20
    total = len(cells) * cw + (len(cells) - 1) * gap
    x0 = px + (pw - total) / 2
    cy = py + 145
    for i, (fam, body) in enumerate(cells):
        cx = x0 + i * (cw + gap)
        p.append(rect(cx, cy - 45, cw, 90, fill="#eef7ff", stroke=POS, sw=1.8))
        p.append(text(cx + cw / 2, cy - 24, "тактика: " + fam, size=12, bold=True, color=POS))
        p.append(mtext(cx + cw / 2, cy + 2, body, size=12))
    render(os.path.join(OUT, 'pattern.svg'), W, H, *p,
           title="Патерн — готовий пакет із кількох тактик")


# ── Фігура D1: ланцюг відмови й точки втручання (виведення меню тактик) ──────
def fig_fault_chain():
    import math
    W, H = 980, 440
    p = []

    # причинний ланцюг угорі
    chain = [
        (165, ["ДЕФЕКТ", "(fault)"]),
        (420, ["ПОМИЛКА", "(error)"]),
        (675, ["ВІДМОВА", "(failure)"]),
    ]
    cy = 110
    box_edges = {}
    for cx, lines in chain:
        b, w, h = textbox(cx, cy, lines, size=13, pad=11, bold=True,
                          fill="#eef7ff", stroke=NEG, sw=1.8)
        p.append(b)
        box_edges[cx] = (cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2)
    # наслідок (кінець ланцюга)
    bn, wn, hn = textbox(875, cy, ["наслідок", "для користувача"], size=12,
                         pad=10, fill="#f4f6f8", stroke=MUTED, sw=1.5)
    p.append(bn)
    box_edges[875] = (875 - wn / 2, 875 + wn / 2, cy - hn / 2, cy + hn / 2)

    # стрілки ланцюга + підписи переходів
    seq = [165, 420, 675, 875]
    trans = [("активація", 292), ("поширення", 547), ("вихід", 775)]
    for i in range(len(seq) - 1):
        r = box_edges[seq[i]][1] + 6
        l = box_edges[seq[i + 1]][0] - 6
        p.append(arrow(r, cy, l, cy, sw=1.8))
    for name, mx in trans:
        p.append(text(mx, 74, name, size=11, color=MUTED, italic=True))

    # сім'ї тактик унизу, рівним рядом
    def fambox(cx, top, title, lines, accent):
        alll = [title] + lines
        tw = max(text_width(s, 12, s == title) for s in alll)
        w = tw + 26
        lh = 12 * 1.35
        h = 22 + len(lines) * lh + 14
        x = cx - w / 2
        out = rect(x, top, w, h, fill="#f7f9fc", stroke=accent, sw=1.7)
        out += text(cx, top + 18, title, size=12, bold=True, color=accent)
        out += line(x + 10, top + 26, x + w - 10, top + 26, color=MUTED, sw=1)
        out += mtext(cx, top + 26 + lh, lines, size=11, color=INK, lh=1.35)
        return out, w, h, x, x + w

    fams = [
        (150, "Запобігти", ["зняти з ротації", "обмежити доступ", "транзакція"], NEG, (165, cy + 27)),
        (360, "Виявити", ["ping / echo", "heartbeat", "таймаут, монітор"], FIELD, (292, 92)),
        (600, "Оговтатись", ["retry, failover", "голосування", "checkpoint"], POS, (547, 92)),
        (830, "Повернути в лад", ["ресинхронізація", "escalating restart", "знову в пул"], NEG, (688, cy + 27)),
    ]
    ftop = 268
    for cx, title, lines, accent, target in fams:
        fb, fw, fh, fl, fr = fambox(cx, ftop, title, lines, accent)
        # тонкий конектор угору до потрібної ланки (без тексту на лінії)
        p.append(arrow(cx, ftop - 4, target[0], target[1], color=MUTED, sw=1.3))
        p.append(fb)
    render(os.path.join(OUT, 'fault-chain.svg'), W, H, *p,
           title="Меню тактик доступності — це точки, де перерізають ланцюг відмови")


# ── Фігура D2: ручка тактики — криві купуємо/платимо, точка компромісу, оптимум ─
def fig_tradeoff_knob():
    import math
    W, H = 860, 470
    p = []
    X0, X1 = 90, 660
    YB = 380

    def vy(val):
        return YB - val * 290

    def px(t):
        return X0 + t * (X1 - X0)

    # осі
    p.append(line(X0, YB, X1 + 8, YB, color=INK, sw=1.6))
    p.append(line(X0, YB, X0, 70, color=INK, sw=1.6))
    p.append(text(X0 + 4, 58, "відповідь-міра", size=12, color=MUTED, anchor="start"))
    p.append(text((X0 + X1) / 2, 432, "значення ручки θ  (таймаут · кількість повторів)  →",
                  size=12, color=MUTED))

    def avail(t):
        return 1 - math.exp(-3 * t)

    def cost(t):
        return 0.85 * (t ** 1.8)

    def net(t):
        return avail(t) - cost(t)

    def poly(fn, color):
        pts = []
        t = 0.0
        while t <= 1.0001:
            pts.append("%.1f,%.1f" % (px(t), vy(fn(t))))
            t += 0.02
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                % (" ".join(pts), color))

    p.append(poly(avail, FIELD))
    p.append(poly(cost, POS))
    p.append(poly(net, NEG))

    # пік чистої користі → оптимум ручки
    best_t, best_v = 0, -9
    t = 0.0
    while t <= 1.0001:
        if net(t) > best_v:
            best_v, best_t = net(t), t
        t += 0.005
    bx, by = px(best_t), vy(best_v)
    p.append(line(bx, YB, bx, by, color=NEG, sw=1.2, dash="4 4"))
    p.append(circle(bx, by, 5, fill=BG, stroke=NEG, sw=2.2))
    p.append(text(bx, 402, "оптимум θ*", size=11, color=NEG, bold=True))

    # анотація «точка компромісу» вгорі (над кривими) з двома лідерами
    ax = 250
    ab, aw, ah = textbox(ax, 104, ["точка компромісу:", "одна θ рухає дві криві нарізно"],
                         size=11, pad=9, fill="#fbf7ee", stroke=MUTED, sw=1.4)
    p.append(ab)
    tcx = px(0.34)
    p.append(line(ax - 20, 104 + ah / 2, tcx, vy(avail(0.34)), color=FIELD, sw=1.1, dash="3 3"))
    p.append(line(ax + 20, 104 + ah / 2, tcx, vy(cost(0.34)), color=POS, sw=1.1, dash="3 3"))

    # легенда праворуч (текст поза кривими: криві до X1=660)
    lx, ly = 686, 150
    leg = [("доступність — купуємо", FIELD), ("ціна — платимо", POS), ("чиста користь", NEG)]
    for name, col in leg:
        p.append(line(lx, ly, lx + 26, ly, color=col, sw=3))
        p.append(text(lx + 32, ly + 4, name, size=11, color=INK, anchor="start"))
        ly += 26
    render(os.path.join(OUT, 'tradeoff-knob.svg'), W, H, *p,
           title="Ціна тактики як крива: точка чутливості, точка компромісу, оптимум")


# ── Фігура D3: атом у кільці ремесла (hub-and-spoke) ─────────────────────────
def fig_decision_lifecycle():
    import math
    W, H = 900, 600
    cx, cy, R = 450, 300, 210
    p = []

    sats = [
        (90, ["Драйвер і сценарій", "ціль у числах"]),
        (30, ["Зважування — ATAM", "точки компромісу"]),
        (330, ["Економіка — CBAM", "вигода / вартість"]),
        (270, ["Час: ерозія →", "фітнес → еволюція"]),
        (210, ["Люди й закон Конвея", "які тактики можливі"]),
        (150, ["Невизначеність", "і ризик"]),
    ]
    # спиці (лише в порожньому проміжку — без тексту на лінії)
    for ang, _ in sats:
        a = math.radians(ang)
        ux, uy = math.cos(a), -math.sin(a)
        x1, y1 = cx + ux * 96, cy + uy * 60
        x2, y2 = cx + ux * (R - 88), cy + uy * (R - 60)
        p.append(line(x1, y1, x2, y2, color=MUTED, sw=1.6))
    # центр
    cb, cw, ch = textbox(cx, cy, ["ТАКТИКА", "одне рішення →", "вимірна відповідь"],
                         size=13, pad=13, bold=True, fill="#eef7ff", stroke=POS, sw=2.2)
    p.append(cb)
    # супутники
    for ang, lines in sats:
        a = math.radians(ang)
        sx, sy = cx + math.cos(a) * R, cy - math.sin(a) * R
        sb, sw_, sh = textbox(sx, sy, lines, size=12, pad=10,
                              fill="#f7f9fc", stroke=NEG, sw=1.6)
        p.append(sb)
    render(os.path.join(OUT, 'decision-lifecycle.svg'), W, H, *p,
           title="Повний цикл найдрібнішого рішення: атом у кільці ремесла")


# ── Фігура P1: скінченний автомат запобіжника — три стани, ручки на ребрах ────
def fig_cb_states():
    W, H = 900, 380
    p = []
    ry = 115
    c_closed, wC, hC = textbox(160, ry, ["ЗАМКНЕНО", "виклики йдуть,", "лічимо збої"],
                               size=13, pad=12, bold=True, fill="#eafaf0", stroke=FIELD, sw=2)
    c_open, wO, hO = textbox(460, ry, ["РОЗІМКНЕНО", "миттєвий збій —", "сусіда не чіпаємо"],
                             size=13, pad=12, bold=True, fill="#fdecea", stroke=POS, sw=2)
    c_half, wH, hH = textbox(770, ry, ["НАПІВВІДКРИТО", "один пробний", "виклик крізь"],
                             size=13, pad=12, bold=True, fill="#fff7e6", stroke=NEG, sw=2)
    p += [c_closed, c_open, c_half]

    closedR = 160 + wC / 2
    openL, openR = 460 - wO / 2, 460 + wO / 2
    halfL = 770 - wH / 2
    boxBottom = ry + hC / 2

    # прямі ребра вздовж ряду (виявлення → запобігання)
    p.append(arrow(closedR + 4, ry, openL - 4, ry))
    lb1, *_ = textbox((closedR + openL) / 2, ry - 44, "збої ≥ поріг", size=11, pad=7,
                      fill="#f0f0f0", stroke=MUTED, sw=1)
    p.append(lb1)
    p.append(arrow(openR + 4, ry, halfL - 4, ry))
    lb2, *_ = textbox((openR + halfL) / 2, ry - 44, "минув тайм-аут", size=11, pad=7,
                      fill="#f0f0f0", stroke=MUTED, sw=1)
    p.append(lb2)

    # зворот «пробний збій → знову розімкнено» (вища доріжка)
    fx, fy = 700, 195
    p.append(line(fx, boxBottom, fx, fy, color=POS, sw=1.8))
    p.append(line(fx, fy, 460, fy, color=POS, sw=1.8))
    p.append(arrow(460, fy, 460, boxBottom, color=POS))
    lbF, *_ = textbox(575, fy - 22, "пробний збій → знову розімкнено", size=11, pad=7,
                      fill="#fdecea", stroke=POS, sw=1.2)
    p.append(lbF)

    # зворот «N пробних успіхів → замкнено» (нижча доріжка)
    sx, sy = 770, 250
    p.append(line(sx, boxBottom, sx, sy, color=FIELD, sw=1.8))
    p.append(line(sx, sy, 160, sy, color=FIELD, sw=1.8))
    p.append(arrow(160, sy, 160, boxBottom, color=FIELD))
    lbS, *_ = textbox(465, sy + 22, "N пробних успіхів → замкнено", size=11, pad=7,
                      fill="#eafaf0", stroke=FIELD, sw=1.2)
    p.append(lbS)

    render(os.path.join(OUT, 'cb-states.svg'), W, H, *p,
           title="Запобіжник — це три стани, а ручки сидять на переходах")


# ── Фігура P2: три ручки, кожна — циферблат між двома шкодами ─────────────────
def fig_cb_knobs():
    W, H = 860, 430
    p = []
    rows = [
        (110, "ПОРІГ РОЗМИКАННЯ (failureThreshold)",
              ["малий поріг:", "моргання", "хибно розмикає"],
              ["великий поріг:", "лавина", "встигає пройти"]),
        (240, "ТАЙМ-АУТ ВІДКРИТОГО (resetTimeout)",
              ["короткий:", "штурмуємо ще", "хворого сусіда"],
              ["довгий:", "відмовляємо всім", "і по одужанні"]),
        (370, "ПРОБНІ ЗАПИТИ (N у напіввідкритому)",
              ["N = 1:", "одна невдача", "знов розмикає"],
              ["N велике:", "тиск на щойно", "оживлого"]),
    ]
    AX0, AX1 = 258, 566
    mid = (AX0 + AX1) / 2
    for ry, title, lh, rh in rows:
        p.append(text(mid, ry - 52, title, size=12, bold=True))
        p.append(line(AX0, ry, AX1, ry, color=INK, sw=1.6))
        p.append(text(AX0, ry - 12, "менше", size=10, color=MUTED, anchor="start"))
        p.append(text(AX1, ry - 12, "більше", size=10, color=MUTED, anchor="end"))
        p.append(rect(mid - 34, ry - 10, 68, 20, fill="#eafaf0", stroke=FIELD, sw=1.4))
        p.append(circle(mid, ry, 5, fill=BG, stroke=FIELD, sw=2.2))
        p.append(text(mid, ry + 26, "робочий θ*", size=10, color=FIELD, bold=True))
        lb, *_ = textbox(128, ry, lh, size=11, pad=9, fill="#fdecea", stroke=POS, sw=1.4)
        p.append(lb)
        rb, *_ = textbox(700, ry, rh, size=11, pad=9, fill="#fdecea", stroke=POS, sw=1.4)
        p.append(rb)
    render(os.path.join(OUT, 'cb-knobs.svg'), W, H, *p,
           title="Кожна ручка запобіжника — циферблат між двома шкодами")


# ── Вставка math-retry-tradeoff: ймовірність зрештою-успіху vs стеля кореляції ─
def fig_success_floor():
    W, H = 880, 470
    X0, X1 = 100, 650
    YB, YT = 390, 80
    Nmax = 8
    q, p0 = 0.2, 0.1
    P = []

    def px(n):
        return X0 + (n - 1) / (Nmax - 1) * (X1 - X0)

    def vy(s):
        return YB - s * (YB - YT)

    P.append(line(X0, YB, X1 + 12, YB, color=INK, sw=1.6))
    P.append(line(X0, YB, X0, YT - 8, color=INK, sw=1.6))
    P.append(text(X0, 62, "P(зрештою успіх за N спроб)", size=12, color=MUTED, anchor="start"))
    P.append(text((X0 + X1) / 2, 434, "число спроб  N  →", size=12, color=MUTED))

    for s, lab in [(0.0, "0"), (0.5, "0.5"), (0.8, "0.8"), (1.0, "1.0")]:
        P.append(text(X0 - 10, vy(s) + 4, lab, size=11, color=MUTED, anchor="end"))
    for n in range(1, Nmax + 1):
        P.append(text(px(n), YB + 20, str(n), size=11, color=MUTED))

    P.append(line(X0, vy(1 - q), X1, vy(1 - q), color=POS, sw=1.4, dash="6 5"))
    P.append(line(X0, vy(1.0), X1, vy(1.0), color=MUTED, sw=1.0, dash="3 4"))

    def curve(fn, color):
        pts = " ".join("%.1f,%.1f" % (px(n), vy(fn(n))) for n in range(1, Nmax + 1))
        return '<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (pts, color)

    # незалежна крива бере ту саму виміряну однокрокову невдачу, що й суміш:
    #   marginal = q·1 + (1−q)·p0 = 0.2 + 0.8·0.1 = 0.28  → обидві стартують з 0.72
    indep = lambda n: 1 - 0.28 ** n
    corr = lambda n: (1 - q) * (1 - p0 ** n)
    P.append(curve(indep, NEG))
    P.append(curve(corr, POS))
    for n in range(1, Nmax + 1):
        P.append(circle(px(n), vy(indep(n)), 3, fill=BG, stroke=NEG, sw=1.6))
        P.append(circle(px(n), vy(corr(n)), 3, fill=BG, stroke=POS, sw=1.6))

    lx = 670
    P.append(text(lx, vy(1 - q) + 4, "стеля 1−q = 0.8", size=11, color=POS, anchor="start"))
    ly = 224
    P.append(line(lx, ly, lx + 26, ly, color=NEG, sw=3))
    P.append(text(lx + 32, ly + 4, "незалежні: 1−pᴺ → 1", size=11, color=INK, anchor="start"))
    ly += 28
    P.append(line(lx, ly, lx + 26, ly, color=POS, sw=3))
    P.append(text(lx + 32, ly + 4, "корельовані:", size=11, color=INK, anchor="start"))
    P.append(text(lx + 32, ly + 20, "(1−q)(1−p₀ᴺ)", size=11, color=INK, anchor="start"))

    render(os.path.join(OUT, 'success-floor.svg'), W, H, *P,
           title="Зрештою-успіх: незалежні збої 1−pᴺ проти стелі кореляції 1−q")


# ── Вставка math-retry-tradeoff: коефіцієнт множення навантаження A(p) → N ─────
def fig_storm_amplification():
    W, H = 860, 470
    X0, X1 = 100, 610
    YB, YT = 390, 80
    N = 5
    Amax = 5.5
    pstar = 0.52
    P = []

    def px(t):
        return X0 + t * (X1 - X0)

    def vy(a):
        return YB - a / Amax * (YB - YT)

    P.append(rect(px(pstar), YT, X1 - px(pstar), vy(2) - YT, fill="#fdecea", stroke="#fdecea", sw=0.6, rx=2))

    P.append(line(X0, YB, X1 + 12, YB, color=INK, sw=1.6))
    P.append(line(X0, YB, X0, YT - 8, color=INK, sw=1.6))
    P.append(text(X0, 62, "множник навантаження  A(p) = викликів на 1 запит", size=12, color=MUTED, anchor="start"))
    P.append(text((X0 + X1) / 2, 434, "частка невдалих викликів  p  →", size=12, color=MUTED))

    for a in range(1, 6):
        P.append(text(X0 - 10, vy(a) + 4, str(a) + "×", size=11, color=MUTED, anchor="end"))
    for t in [0.0, 0.25, 0.5, 0.75, 1.0]:
        P.append(text(px(t), YB + 20, ("%.2f" % t), size=11, color=MUTED))

    P.append(line(X0, vy(N), X1, vy(N), color=MUTED, sw=1.1, dash="5 4"))
    P.append(text(px(0.05), vy(N) - 10, "стеля підсилення  A → N = 5", size=11, color=INK, anchor="start"))
    P.append(line(X0, vy(2), X1, vy(2), color=FIELD, sw=1.4, dash="6 5"))
    P.append(text(px(0.05), vy(2) - 10, "потужність сусіда  C/λ = 2×", size=11, color=FIELD, anchor="start"))

    pts = []
    t = 0.0
    while t <= 0.985:
        a = (1 - t ** N) / (1 - t)
        pts.append("%.1f,%.1f" % (px(t), vy(a)))
        t += 0.015
    P.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(pts), POS))

    P.append(text(px(0.80), vy(4.5), "зона шторму повторів", size=12, color=POS, bold=True))
    P.append(text(px(0.80), vy(4.5) + 17, "A·λ > C → колапс", size=11, color=POS))
    P.append(text(px(0.09), vy(0.7), "порочне коло:  p↑ → A↑ → p↑", size=11, color=INK, anchor="start"))

    P.append(line(px(pstar), vy(2), px(pstar), YB, color=NEG, sw=1.3, dash="4 4"))
    P.append(text(px(pstar) + 6, vy(1.25), "запобіжник розмикає:", size=11, color=NEG, anchor="start"))
    P.append(text(px(pstar) + 6, vy(1.25) + 16, "далі A обривається до 0", size=11, color=NEG, anchor="start"))

    render(os.path.join(OUT, 'storm-amplification.svg'), W, H, *P,
           title="Шторм повторів: підсилення A(p) росте до N, доки запобіжник не обірве")


# ── Вставка math-retry-tradeoff: одна ручка N — дві криві нарізно ──────────────
def fig_knob_two_gauges():
    W, H = 860, 470
    X0, X1 = 120, 600
    YB, YT = 390, 90
    Nmax = 7
    Lmax = 5000.0
    P = []

    def px(n):
        return X0 + (n - 1) / (Nmax - 1) * (X1 - X0)

    def vyA(s):
        return YB - s * (YB - YT)

    def vyL(L):
        return YB - (L / Lmax) * (YB - YT)

    succ = lambda n: 1 - 0.5 ** n
    lat = lambda n: 200 * n + 50 * (2 ** (n - 1) - 1)

    P.append(line(X0, YB, X1, YB, color=INK, sw=1.6))
    P.append(line(X0, YB, X0, YT - 8, color=FIELD, sw=1.6))
    P.append(line(X1, YB, X1, YT - 8, color=POS, sw=1.6))
    P.append(text(X0 - 6, 70, "доступність 1−pᴺ", size=12, color=FIELD, anchor="start"))
    P.append(text(X1 + 6, 70, "гірша затримка, мс", size=12, color=POS, anchor="end"))
    P.append(text((X0 + X1) / 2, 434, "ручка: число спроб  N  →", size=12, color=MUTED))

    for s, lab in [(0.0, "0"), (0.5, "0.5"), (1.0, "1.0")]:
        P.append(text(X0 - 10, vyA(s) + 4, lab, size=11, color=FIELD, anchor="end"))
    for L, lab in [(0, "0"), (2500, "2500"), (5000, "5000")]:
        P.append(text(X1 + 10, vyL(L) + 4, lab, size=11, color=POS, anchor="start"))
    for n in range(1, Nmax + 1):
        P.append(text(px(n), YB + 20, str(n), size=11, color=MUTED))

    a_pts = " ".join("%.1f,%.1f" % (px(n), vyA(succ(n))) for n in range(1, Nmax + 1))
    l_pts = " ".join("%.1f,%.1f" % (px(n), vyL(lat(n))) for n in range(1, Nmax + 1))
    P.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (a_pts, FIELD))
    P.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (l_pts, POS))
    for n in range(1, Nmax + 1):
        P.append(circle(px(n), vyA(succ(n)), 3, fill=BG, stroke=FIELD, sw=1.6))
        P.append(circle(px(n), vyL(lat(n)), 3, fill=BG, stroke=POS, sw=1.6))

    nx = px(4)
    P.append(line(nx, YB, nx, YT + 4, color=MUTED, sw=1.1, dash="4 4"))
    P.append(text(nx + 6, YT + 18, "точка компромісу N*", size=11, color=INK, anchor="start"))
    P.append(text(nx + 6, YT + 34, "далі: користь ×p ↓, ціна ×2 ↑", size=11, color=MUTED, anchor="start"))

    P.append(text(px(2.0), vyA(succ(2)) - 14, "насичується", size=11, color=FIELD))
    P.append(text(px(5.55), vyL(lat(6)) + 6, "вибухає ×2/крок", size=11, color=POS))

    render(os.path.join(OUT, 'knob-two-gauges.svg'), W, H, *P,
           title="Одна ручка N — дві криві нарізно: користь насичується, ціна вибухає")


# ── Вставка hist-tactics-lineage: родовід поділу «патерн → тактика» ───────────
def fig_hist_lineage():
    W, H = 900, 620
    p = []
    spine_x = 250
    nodes = [
        (95, "1977", "«A Pattern Language» · Крістофер Александер",
             "патерн — фрагмент живого цілого (архітектура)"),
        (185, "1987", "OOPSLA · Кент Бек і Ворд Каннінгем",
              "патерни вперше приходять у код (5 патернів для UI)"),
        (275, "1994", "«Design Patterns» — Банда чотирьох (GoF)",
              "Гамма · Гелм · Джонсон · Вліссідес — каталог із 23 патернів"),
        (365, "1999", "ABAS · Software Engineering Institute",
              "Марк Кляйн і Рік Кецман — рамка міркування за атрибутом"),
        (455, "2003", "«Software Architecture in Practice» (2-ге вид.)",
              "Басс · Клементс · Кецман — тактику кодифіковано"),
        (545, "2004", "Таксономія надійності (IEEE TDSC)",
              "Авіженіс, Лапрі й ін. — корінь тактик доступності"),
    ]
    p.append(line(spine_x, 78, spine_x, 560, color=MUTED, sw=2))
    box_x, box_w = 288, 596
    for ny, year, title, desc in nodes:
        p.append(rect(box_x, ny - 33, box_w, 66, fill="#f7f9fc", stroke=NEG, sw=1.6))
        p.append(text(228, ny + 6, year, size=20, bold=True, color=POS, anchor="end"))
        p.append(circle(spine_x, ny, 7, fill=BG, stroke=INK, sw=2.4))
        p.append(line(spine_x + 8, ny, box_x - 2, ny, color=MUTED, sw=1.4))
        p.append(text(box_x + 16, ny - 7, title, size=13, bold=True, anchor="start"))
        p.append(text(box_x + 16, ny + 16, desc, size=12, color=MUTED, anchor="start"))
    render(os.path.join(OUT, 'hist-lineage.svg'), W, H, *p,
           title="Родовід поділу «патерн → тактика»: три дисципліни, тридцять років")


# ── Вставка hist-tactics-lineage: як дрібнішала одиниця рішення ───────────────
def fig_hist_grain():
    W, H = 940, 320
    p = []
    y_top, ph, pw = 92, 195, 250
    panels = [
        (40, NEG, "Александер · 1977", "ЦІЛЕ",
         ["патерн — фрагмент", "живого цілого;", "мета — повнота", "й «якість без імені»"]),
        (345, MUTED, "GoF · 1994", "ПАКЕТ",
         ["патерн — названий", "каталожний розв'язок;", "компроміс уже", "зашито автором"]),
        (650, POS, "Басс · SEI · 2003", "АТОМ",
         ["тактика — один важіль,", "одна вимірна відповідь;", "компроміс", "лишається тобі"]),
    ]
    for px_, accent, header, tag, body in panels:
        cx = px_ + pw / 2
        p.append(rect(px_, y_top, pw, ph, fill=BG, stroke=accent, sw=1.8))
        p.append(text(cx, y_top + 28, header, size=14, bold=True, color=accent))
        by = y_top + 60
        for ln in body:
            p.append(text(cx, by, ln, size=12, color=INK))
            by += 22
        tb, tw, th = textbox(cx, y_top + ph - 28, tag, size=13, pad=8, bold=True,
                             fill="#f4f6f8", stroke=accent, sw=1.6, color=accent)
        p.append(tb)
    p.append(arrow(290, 150, 345, 150, sw=1.8))
    p.append(arrow(595, 150, 650, 150, sw=1.8))
    for lx, l1, l2 in [(318, "назвати", "й зібрати"), (622, "розібрати", "на атоми")]:
        p.append(text(lx, 130, l1, size=11, color=MUTED, italic=True))
        p.append(text(lx, 144, l2, size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, 'hist-grain.svg'), W, H, *p,
           title="Одиниця рішення дрібнішала: живе ціле → пакет → атом")


fig_anatomy()
fig_menu()
fig_pattern()
fig_fault_chain()
fig_tradeoff_knob()
fig_decision_lifecycle()
fig_cb_states()
fig_cb_knobs()
fig_success_floor()
fig_storm_amplification()
fig_knob_two_gauges()
fig_hist_lineage()
fig_hist_grain()
print("figs done")
