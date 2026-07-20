# -*- coding: utf-8 -*-
"""Фігури до теми «Втома матеріалу».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── допоміжне ────────────────────────────────────────────────────────────────
def tbox(*a, **k):
    """textbox, але повертає лише SVG-тіло (ширину/висоту не потребуємо)."""
    return textbox(*a, **k)[0]


def qbez(x1, y1, cx, cy, x2, y2, color=INK, sw=1.6, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" '
            'stroke="%s" stroke-width="%.1f"%s/>' % (x1, y1, cx, cy, x2, y2, color, sw, d))


def polyline(pts, color=INK, sw=2.0):
    d = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, color, sw)


# ── Фігура 1: три стадії втомної тріщини + слід на зламі ──────────────────────
def fig_stages():
    W, H = 900, 470
    f = []
    f.append(text(228, 40, "Тріщина росте циклами", size=16, bold=True))
    f.append(text(668, 40, "Слід, який вона лишає на зламі", size=16, bold=True))

    # --- лівий: пластина під циклічним розтягом із тріщиною ---
    bx, by, bw, bh = 95, 175, 250, 95
    f.append(rect(bx, by, bw, bh, fill="#eef1f4"))
    # розтяг у два боки (стрілки)
    f.append(arrow(bx - 12, by + bh / 2, bx - 52, by + bh / 2, color=INK, sw=2.4))
    f.append(arrow(bx + bw + 12, by + bh / 2, bx + bw + 52, by + bh / 2, color=INK, sw=2.4))
    f.append(text(220, 300, "тягне то сильніше, то слабше — цикл за циклом", size=12, color=MUTED))
    # надріз на верхній грані + тріщина вглиб
    nx = 178
    f.append(line(nx - 8, by, nx, by + 14, color=INK, sw=2))
    f.append(line(nx + 8, by, nx, by + 14, color=INK, sw=2))
    f.append(polyline([(nx, by + 14), (nx + 7, by + 34), (nx - 5, by + 52), (nx + 6, by + 70)],
                      color=POS, sw=2.6))
    # підписи
    f.append(tbox(150, 120, "подряпина\n(концентратор)", size=12))
    f.append(arrow(160, 138, 176, 172, color=MUTED, sw=1.6))
    f.append(tbox(300, 150, "тріщина\nповзе вглиб", size=12))
    f.append(arrow(268, 168, 192, 216, color=MUTED, sw=1.6))

    # --- правий: поверхня зламу ---
    fx, fy, fw, fh = 545, 150, 250, 150
    f.append(rect(fx, fy, fw, fh, fill=BG))
    # осередок зародження (ліва грань, посередині)
    f.append(circle(fx + 3, fy + fh / 2, 6, fill=POS, stroke=POS, sw=1))
    # «пляжні смуги» — дуги, опуклі геть від осередку
    for xi, bulge in [(585, 26), (620, 30), (652, 34), (680, 38)]:
        f.append(qbez(xi, fy, xi + bulge, fy + fh / 2, xi, fy + fh, color=MUTED, sw=1.5))
    # зона доламу — груба, точкова текстура праворуч
    zx0 = 706
    f.append(rect(zx0, fy, fx + fw - zx0, fh, fill="#f6ece1", stroke="none", sw=0))
    x = zx0 + 8
    while x < fx + fw - 5:
        y = fy + 12
        while y < fy + fh - 8:
            f.append(circle(x, y, 1.5, fill=MUTED, stroke=MUTED, sw=0.4))
            y += 15
        x += 13
    # праву грань перемалюємо поверх текстури, щоб рамка лишалась чіткою
    f.append(line(fx + fw, fy, fx + fw, fy + fh, color=LINE, sw=1.5))
    # підписи зон
    f.append(tbox(475, 225, "звідси\nпочалося", size=12, color=POS))
    f.append(arrow(514, 225, 540, 225, color=POS, sw=1.6))
    f.append(tbox(600, 360, "гладенька зона:\nповільний ріст", size=12))
    f.append(arrow(600, 338, 628, 292, color=MUTED, sw=1.6))
    f.append(tbox(762, 360, "зона доламу:\nгруба, миттєва", size=12))
    f.append(arrow(762, 338, 748, 292, color=MUTED, sw=1.6))

    render(os.path.join(IMG, "fatigue-stages.svg"), W, H, *f)


# ── Фігура 2: крива втоми (S–N) для сталі й алюмінію ──────────────────────────
def fig_sn():
    W, H = 800, 470
    f = []
    f.append(text(400, 34, "Крива втоми: скільки циклів до зламу", size=16, bold=True))

    ox, oy = 110, 380          # початок осей
    xr, yt = 735, 68           # кінці осей
    f.append(arrow(ox, oy, xr, oy, color=INK, sw=1.8))       # вісь N →
    f.append(arrow(ox, oy + 4, ox, yt, color=INK, sw=1.8))   # вісь σ ↑
    f.append(text(430, 432, "Число циклів до руйнування N  (лог)", size=13, color=INK))
    f.append(text(96, 60, "σ, амплітуда напруження", size=13, color=INK, anchor="start"))

    # десяткові позначки на осі N
    def xd(d):
        return ox + (d - 3) / 5.0 * (xr - 30 - ox)
    sup = {3: "³", 4: "⁴", 5: "⁵", 6: "⁶", 7: "⁷", 8: "⁸"}
    for d in range(3, 9):
        X = xd(d)
        f.append(line(X, oy, X, oy + 6, color=INK, sw=1.4))
        f.append(text(X, oy + 22, "10" + sup[d], size=13, color=MUTED))

    # крива сталі — спад і горизонтальна поличка
    steel = [(xd(3), 100), (xd(3.6), 128), (xd(4.2), 162), (xd(4.8), 198),
             (xd(5.4), 228), (xd(6.0), 250), (xd(6.5), 258), (xd(7.2), 260), (xd(8), 261)]
    f.append(polyline(steel, color=INK, sw=2.6))
    # крива алюмінію — спадає без упину
    alu = [(xd(3), 150), (xd(3.7), 182), (xd(4.4), 214), (xd(5.1), 246),
           (xd(5.8), 278), (xd(6.5), 308), (xd(7.2), 340), (xd(8), 372)]
    f.append(polyline(alu, color=NEG, sw=2.6))

    # границя витривалості — пунктир на рівні полички
    f.append(line(xd(6.3), 258, xr - 12, 258, color=MUTED, sw=1.4, dash="6 5"))
    f.append(tbox(600, 205, "границя\nвитривалості", size=12, color=INK))
    f.append(arrow(600, 224, 585, 257, color=MUTED, sw=1.5))

    # легенда
    f.append(line(150, 96, 186, 96, color=INK, sw=2.6))
    f.append(text(194, 100, "сталь — має поличку", size=13, color=INK, anchor="start"))
    f.append(line(150, 120, 186, 120, color=NEG, sw=2.6))
    f.append(text(194, 124, "алюміній — полички нема", size=13, color=NEG, anchor="start"))

    render(os.path.join(IMG, "sn-curve.svg"), W, H, *f)


# ── Фігура 3: концентрація напружень — круглий отвір проти гострого виріза ────
def fig_concentration():
    W, H = 920, 410
    f = []
    f.append(text(460, 34, "Де збиваються силові лінії — там родиться тріщина", size=15, bold=True))

    def plate(px, sub, sharp):
        py, pw, ph = 108, 290, 210
        g = [rect(px, py, pw, ph, fill="#eef1f4")]
        # розтяг обабіч
        g.append(arrow(px - 10, py + ph / 2, px - 48, py + ph / 2, color=INK, sw=2.4))
        g.append(arrow(px + pw + 10, py + ph / 2, px + pw + 48, py + ph / 2, color=INK, sw=2.4))
        g.append(text(px - 60, py + ph / 2 + 5, "σ", size=16, bold=True, italic=True, anchor="end"))
        g.append(text(px + pw + 60, py + ph / 2 + 5, "σ", size=16, bold=True, italic=True, anchor="start"))
        cx, cy = px + pw / 2, py + ph / 2
        # силові лінії: густішають до отвору згори й знизу
        for y in (py + 15, py + 30, py + 44, py + 56, py + 66):
            g.append(line(px + 12, y, px + pw - 12, y, color=MUTED, sw=1.2))
        for y in (py + ph - 15, py + ph - 30, py + ph - 44, py + ph - 56, py + ph - 66):
            g.append(line(px + 12, y, px + pw - 12, y, color=MUTED, sw=1.2))
        if sharp:
            # квадратний виріз із гострими кутами
            s = 80
            hx, hy = cx - s / 2, cy - s / 2
            g.append(rect(hx, hy, s, s, fill=BG))
            for (kx, ky, dx, dy) in [(hx, hy, -7, -7), (hx + s, hy, 7, -7),
                                     (hx, hy + s, -7, 7), (hx + s, hy + s, 7, 7)]:
                g.append(circle(kx, ky, 6, fill=POS, stroke=POS, sw=1))
                g.append(line(kx, ky, kx + dx, ky + dy, color=POS, sw=2.2))
            g.append(text(cx, cy + 5, "K ≫ 3", size=13, color=POS, bold=True))
        else:
            r = 40
            g.append(circle(cx, cy, r, fill=BG))
            g.append(circle(cx, cy - r, 5.5, fill=POS, stroke=POS, sw=1))
            g.append(circle(cx, cy + r, 5.5, fill=POS, stroke=POS, sw=1))
            g.append(text(cx, cy + 5, "K ≈ 3", size=13, color=POS, bold=True))
        g.append(text(cx, py + ph + 34, sub, size=14, bold=True))
        return g

    f += plate(80, "круглий отвір: напруження втричі", sharp=False)
    f += plate(560, "гострий кут: напруження в рази вище", sharp=True)

    render(os.path.join(IMG, "stress-concentration.svg"), W, H, *f)


# ── Фігура 4: століття відкриття втоми (часова смуга) ─────────────────────────
def fig_timeline():
    W, H = 1040, 390
    f = []
    sy = 200                       # висота хребта-осі часу

    # хребет часу зі стрілкою праворуч
    f.append(arrow(60, sy, 990, sy, color=INK, sw=2.2))
    f.append(text(966, sy + 26, "час →", size=13, color=MUTED, anchor="end"))

    # вузли: (x, рік, підпис, колір, вгорі?)
    nodes = [
        (130, "1839", "Понселе, Мец:\nметал «втомлюється»", NEG,   True),
        (320, "1842", "Медон під Парижем:\nзлам осі паровоза", POS, False),
        (510, "1854", "Брейтвейт:\n«fatigue» — в англ.",      NEG,  True),
        (700, "1850–70", "Веллер: втомні машини,\nграниця витривалості", FIELD, False),
        (890, "1954", "Comet:\nтріщини з кутів вікон",        POS,  True),
    ]
    for x, year, cap, col, up in nodes:
        f.append(circle(x, sy, 8, fill=col, stroke=col, sw=1))
        if up:
            f.append(line(x, sy - 8, x, sy - 22, color=MUTED, sw=1.4))
            f.append(text(x, sy - 34, year, size=15, color=col, bold=True))
            f.append(tbox(x, sy - 92, cap, size=12))
        else:
            f.append(line(x, sy + 8, x, sy + 22, color=MUTED, sw=1.4))
            f.append(text(x, sy + 40, year, size=15, color=col, bold=True))
            f.append(tbox(x, sy + 96, cap, size=12))

    # легенда категорій
    ly = 356
    for lx, col, lab in [(300, POS, "катастрофа"), (500, NEG, "новий термін"),
                         (720, FIELD, "систематична наука")]:
        f.append(circle(lx, ly - 4, 7, fill=col, stroke=col, sw=1))
        f.append(text(lx + 14, ly, lab, size=13, color=INK, anchor="start"))

    render(os.path.join(IMG, "fatigue-history-timeline.svg"), W, H, *f,
           title="Століття, за яке втома із загадки стала наукою")


# ── Фігура 5: крива Періса — три режими росту тріщини ─────────────────────────
def fig_paris():
    W, H = 840, 520
    f = []
    f.append(text(420, 34, "Крива Періса: три режими росту тріщини", size=16, bold=True))

    ox, oy = 130, 430          # початок осей
    xr, yt = 800, 90           # кінці осей
    f.append(arrow(ox, oy, xr, oy, color=INK, sw=1.8))       # вісь ΔK →
    f.append(arrow(ox, oy + 4, ox, yt, color=INK, sw=1.8))   # вісь da/dN ↑
    f.append(text(470, 495, "log ΔK  (розмах коефіцієнта інтенсивності)", size=13, color=INK))
    f.append(text(112, 60, "log da/dN", size=13, color=INK, anchor="start"))
    f.append(text(112, 78, "(приріст за цикл)", size=11, color=MUTED, anchor="start"))

    # пороги-асимптоти
    f.append(line(235, oy, 235, 350, color=MUTED, sw=1.4, dash="5 5"))
    f.append(text(235, 452, "ΔK_th", size=13, color=MUTED))
    f.append(text(235, 468, "(поріг)", size=11, color=MUTED))
    f.append(line(690, oy, 690, 95, color=MUTED, sw=1.4, dash="5 5"))
    f.append(text(690, 452, "K_c", size=13, color=MUTED))
    f.append(text(690, 468, "(в'язкість)", size=11, color=MUTED))

    # сигмоїдна крива da/dN(ΔK)
    curve = [(248, 408), (262, 395), (280, 372), (305, 345),
             (340, 315), (400, 273), (470, 224), (545, 172),
             (590, 150), (630, 122), (662, 100), (678, 88)]
    f.append(polyline(curve, color=INK, sw=2.8))

    # мітки режимів
    f.append(text(300, 400, "I", size=16, color=MUTED, bold=True))
    f.append(text(420, 330, "II", size=16, color=MUTED, bold=True))
    f.append(text(655, 178, "III", size=16, color=MUTED, bold=True))

    # трикутник нахилу m на прямій вітці
    f.append(line(400, 273, 470, 273, color=MUTED, sw=1.4))
    f.append(line(470, 273, 470, 224, color=MUTED, sw=1.4))
    f.append(text(486, 252, "m", size=14, color=MUTED, italic=True))

    # виноска з формулою Періса
    f.append(tbox(432, 122, "da/dN = C·(ΔK)ᵐ", size=14, fill=BG))
    f.append(arrow(432, 140, 452, 230, color=MUTED, sw=1.5))

    render(os.path.join(IMG, "paris-curve.svg"), W, H, *f)


# ── Фігура 6: крива деформація–життя (пружна + пластична вітки) ───────────────
def fig_strain_life():
    W, H = 840, 520
    f = []
    f.append(text(420, 34, "Крива деформація–життя: пружна і пластична вітки", size=16, bold=True))

    ox, oy = 130, 430
    xr, yt = 800, 90
    f.append(arrow(ox, oy, xr, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy + 4, ox, yt, color=INK, sw=1.8))
    f.append(text(455, 495, "log 2N_f  (реверси до руйнування)", size=13, color=INK))
    f.append(text(112, 60, "log(Δε/2)", size=13, color=INK, anchor="start"))
    f.append(text(112, 78, "амплітуда деф.", size=11, color=MUTED, anchor="start"))

    # прямі вітки
    plastic = [(165, 120), (560, 430)]     # Коффін–Менсон, крута
    elastic = [(165, 300), (790, 405)]     # Басквін, полога
    total = [(165, 108), (250, 165), (350, 240), (457, 318),
             (560, 360), (680, 385), (790, 398)]
    f.append(polyline(plastic, color=POS, sw=2.4))
    f.append(polyline(elastic, color=NEG, sw=2.4))
    f.append(polyline(total, color=INK, sw=2.8))

    # перехідне життя (перетин прямих)
    f.append(line(457, oy, 457, 320, color=MUTED, sw=1.4, dash="5 5"))
    f.append(circle(457, 349, 4, fill=MUTED, stroke=MUTED, sw=1))
    f.append(text(457, 452, "2N_t", size=13, color=MUTED))
    f.append(text(457, 468, "(перехідне)", size=11, color=MUTED))

    # межі режимів
    f.append(text(285, 452, "низькоциклова", size=12, color=MUTED))
    f.append(text(650, 452, "високоциклова", size=12, color=MUTED))

    # легенда (порожній верхній правий кут)
    f.append(line(575, 116, 611, 116, color=POS, sw=2.6))
    f.append(text(619, 120, "пластична (Коффін–Менсон)", size=12, color=POS, anchor="start"))
    f.append(line(575, 140, 611, 140, color=NEG, sw=2.6))
    f.append(text(619, 144, "пружна (Басквін)", size=12, color=NEG, anchor="start"))
    f.append(line(575, 164, 611, 164, color=INK, sw=2.6))
    f.append(text(619, 168, "сумарна", size=12, color=INK, anchor="start"))

    render(os.path.join(IMG, "strain-life.svg"), W, H, *f)


# ── Фігура: rainflow виловлює ВКЛАДЕНІ замкнені цикли ─────────────────────────
def fig_nested_cycles():
    W, H = 900, 430
    f = []
    f.append(text(450, 34, "Rainflow бачить у записі вкладені замкнені цикли", size=16, bold=True))

    ox, oy = 90, 300
    xr, yt = 840, 70
    f.append(arrow(ox, oy, xr, oy, color=INK, sw=1.8))        # час →
    f.append(arrow(ox, oy + 2, ox, yt, color=INK, sw=1.8))    # σ ↑
    f.append(text(792, oy + 26, "час", size=13, color=INK))
    f.append(text(70, 84, "σ", size=15, color=INK, bold=True, italic=True, anchor="end"))

    def X(u):
        return ox + 24 + u * (xr - ox - 60)

    def Y(s):
        return oy - s / 10.0 * (oy - yt - 10)

    pts_s = [(0.00, 1.0), (0.12, 9.2), (0.24, 4.4), (0.36, 6.2),
             (0.50, 2.6), (0.63, 7.2), (0.76, 3.4), (0.88, 8.0), (1.00, 1.0)]
    P = [(X(u), Y(s)) for u, s in pts_s]
    f.append(polyline(P, color=INK, sw=2.4))
    for (x, y) in P:
        f.append(circle(x, y, 3.4, fill=BG, stroke=INK, sw=1.6))

    # великий цикл — дуга під віссю від найнижчої западини до найвищого піка
    x0, _ = P[0]
    xend, _ = P[-1]
    f.append(qbez(x0, oy + 14, (x0 + xend) / 2, oy + 60, xend, oy + 14, color=POS, sw=2.6))
    f.append(tbox(450, oy + 92, "великий цикл: розмах від найнижчої западини до найвищого піка",
                  size=12, color=POS))

    # два вкладені малі цикли — короткі дуги над відповідними парами точок
    def small_arc(i, j, label, lx, ly):
        xa, ya = P[i]; xb, yb = P[j]
        top = min(ya, yb) - 26
        f.append(qbez(xa, ya - 6, (xa + xb) / 2, top, xb, yb - 6, color=NEG, sw=2.0))
        f.append(tbox(lx, ly, label, size=11, color=NEG))
        f.append(arrow(lx, ly + 16, (xa + xb) / 2, top - 2, color=NEG, sw=1.4))

    small_arc(2, 3, "малий\nвкладений цикл", 300, 116)
    small_arc(5, 6, "ще один\nмалий цикл", 648, 116)

    render(os.path.join(IMG, "rainflow-nested.svg"), W, H, *f)


# ── Фігура: де ховається шкода — спектр циклів прикладу ───────────────────────
def fig_damage_spectrum():
    W, H = 900, 470
    f = []
    f.append(text(450, 34, "Кілька великих циклів з'їдають майже всю шкоду", size=16, bold=True))

    ox, oy = 130, 358
    xr, yt = 852, 96
    f.append(arrow(ox, oy + 2, ox, yt, color=INK, sw=1.8))     # амплітуда ↑
    f.append(line(ox, oy, xr, oy, color=INK, sw=1.8))          # база
    f.append(text(112, 88, "амплітуда", size=12, color=INK, anchor="end"))
    f.append(text(112, 104, "σₐ, МПа", size=12, color=INK, anchor="end"))

    # (амплітуда, частка шкоди %, чи з залишку)
    cyc = [(107.5, 44.2, True), (92.5, 29.1, True), (82.5, 21.9, False),
           (60.0, 2.8, False), (60.0, 1.6, False), (60.0, 0.5, True), (32.5, 0.03, False)]
    n = len(cyc)
    slot = (xr - ox - 44) / n
    bw = slot * 0.54

    def Yb(a):
        return oy - a / 120.0 * (oy - yt - 8)

    for i, (a, share, resid) in enumerate(cyc):
        cx = ox + 34 + slot * (i + 0.5)
        big = share >= 10
        col = POS if big else MUTED
        f.append(rect(cx - bw / 2, Yb(a), bw, oy - Yb(a),
                      fill="#f7d9d4" if big else "#eceef1", stroke=col, sw=1.6, rx=3))
        lbl = ("%.0f%%" % share) if share >= 1 else "<1%"
        f.append(text(cx, Yb(a) - 12, lbl, size=13, color=col, bold=big))
        f.append(text(cx, oy + 22, "%.0f" % a, size=12, color=INK))
        if resid:
            f.append(text(cx, oy + 40, "залишок", size=10.5, color=POS))

    # дужка над трьома найбільшими
    bx0 = ox + 34 + slot * 0.5 - bw / 2
    bx1 = ox + 34 + slot * 2.5 + bw / 2
    f.append(line(bx0, yt + 4, bx1, yt + 4, color=INK, sw=1.6))
    f.append(line(bx0, yt + 4, bx0, yt + 12, color=INK, sw=1.6))
    f.append(line(bx1, yt + 4, bx1, yt + 12, color=INK, sw=1.6))
    f.append(text((bx0 + bx1) / 2, yt - 6, "3 цикли = 95% шкоди", size=13, color=INK, bold=True))

    f.append(tbox(450, 438,
                  "Стовпчик — окремий цикл; підпис — його частка втомної шкоди.\n"
                  "Два найшкідливіші цикли — із ЗАЛИШКУ: викинути залишок = проґавити 73% шкоди.",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "rainflow-damage.svg"), W, H, *f)


if __name__ == "__main__":
    fig_stages()
    fig_sn()
    fig_concentration()
    fig_timeline()
    fig_paris()
    fig_strain_life()
    fig_nested_cycles()
    fig_damage_spectrum()
    print("OK: figs -> img/")
