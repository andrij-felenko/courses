# -*- coding: utf-8 -*-
"""Фігури до теми «Поверхневий натяг».
Запуск із теки теми:  python figs.py   → SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

WATER = "#cfe8f5"
WATERD = "#6aa9cf"
MERC = "#c6c9cf"
MERCD = "#8f949c"
SOAP = "#fbf3d0"
GLASS = "#aeb6bf"
GREEN = FIELD
ORANGE = "#e08e0b"


def frange(a, b, n):
    return [a + (b - a) * i / (n - 1) for i in range(n)]


def path(d, fill="none", stroke=INK, sw=2.0):
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (d, fill, stroke, sw)


def dot(cx, cy, r, fill, stroke="none", sw=0):
    return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s" '
            'stroke-width="%.1f"/>' % (cx, cy, r, fill, stroke, sw))


# ── Фігура 1: молекула в глибині й на поверхні ───────────────────────────────
def fig_molecular():
    W, H = 940, 600
    F = []
    lx, lw = 70, 560
    surf = 170
    lbot = 520
    # тіло рідини
    F.append(rect(lx, surf, lw, lbot - surf, fill=WATER, stroke=WATERD, sw=1.6, rx=4))
    F.append(line(lx, surf, lx + lw, surf, color=WATERD, sw=3.0))
    F.append(text(lx + 62, surf - 24, "повітря", size=13.5, color=MUTED, italic=True))
    F.append(text(lx + 60, lbot - 16, "рідина", size=13.5, color="#3a6a86", italic=True))

    # тьмяна сітка молекул
    special = [(250, 360), (470, surf)]
    yy = surf + 34
    while yy < lbot - 12:
        xx = lx + 40
        while xx < lx + lw - 20:
            skip = any(abs(xx - sx) < 26 and abs(yy - sy) < 26 for sx, sy in special)
            if not skip:
                F.append(dot(xx, yy, 6.5, "#bfe0f0"))
            xx += 48
        yy += 46

    # ── глибинна молекула: 8 симетричних стрілок притягання ──
    bx, by = 250, 360
    R = 32
    for k in range(8):
        a = k * math.pi / 4
        F.append(arrow(bx, by, bx + R * math.cos(a), by + R * math.sin(a), color=NEG, sw=1.9))
    F.append(circle(bx, by, 11, fill="#ffffff", stroke=INK, sw=2.2))
    F.append(dot(bx, by, 4.5, NEG))
    F.append(fitbox(bx - 150, 430, 300, 46,
                    "у ГЛИБИНІ: тягне на всі боки однаково\nсумарна сила = 0",
                    size=13, bold=True, fill="#eaf0fd", stroke=NEG, pad=8))

    # ── поверхнева молекула: сусіди лише знизу й з боків ──
    sx, sy = 470, surf
    for a in [math.pi, 0, math.pi * 0.75, math.pi * 0.5, math.pi * 0.25]:
        F.append(arrow(sx, sy, sx + R * math.cos(a), sy + R * math.sin(a), color=NEG, sw=1.9))
    # сумарна сила — всередину
    F.append(arrow(sx, sy + 6, sx, sy + 78, color=POS, sw=3.4))
    F.append(circle(sx, sy, 11, fill="#ffffff", stroke=INK, sw=2.2))
    F.append(dot(sx, sy, 4.5, POS))
    F.append(fitbox(sx - 158, surf - 66, 316, 40,
                    "на ПОВЕРХНІ: згори сусідів немає",
                    size=13, bold=True, fill="#fdecea", stroke=POS, pad=8))
    F.append(text(sx + 92, sy + 52, "сумарна сила —", size=12.5, color=POS, bold=True, anchor="start"))
    F.append(text(sx + 92, sy + 70, "усередину рідини", size=12.5, color=POS, bold=True, anchor="start"))

    F.append(fitbox(lx, 548, lw, 44,
                    "Поверхнева молекула має менше сусідів, ніж глибинна — це стан вищої енергії. "
                    "Рідина відповідає єдиним способом: робить поверхню якнайменшою.",
                    size=13, bold=True, fill="#eafaf0", stroke=GREEN, pad=9))

    render(os.path.join(IMG, "molecular-origin.svg"), W, H, *F,
           title="Звідки береться натяг: молекула в глибині й на поверхні")


# ── Фігура 2: плівка на рамці — σ як сила/довжина = енергія/площа ─────────────
def fig_film():
    W, H = 900, 500
    F = []
    xL, xR = 210, 560
    yT, yB = 150, 340
    L = yB - yT

    # мильна плівка
    F.append(rect(xL, yT, xR - xL, L, fill=SOAP, stroke="#e6d78a", sw=1.3, rx=2))
    F.append(text((xL + xR) / 2, yT - 14, "мильна плівка", size=13, color="#8a7a20", italic=True))

    # дротяна рамка (П-подібна): ліва, верх, низ
    for x1, y1, x2, y2 in [(xL, yT, xL, yB), (xL, yT, xR, yT), (xL, yB, xR, yB)]:
        F.append(line(x1, y1, x2, y2, color=INK, sw=7))
    # рухомий стрижень праворуч
    F.append(line(xR, yT - 8, xR, yB + 8, color=ORANGE, sw=8))
    F.append(circle(xR, yT - 8, 6, fill=ORANGE, stroke=INK, sw=1.4))
    F.append(circle(xR, yB + 8, 6, fill=ORANGE, stroke=INK, sw=1.4))
    F.append(text(xR + 4, yT - 22, "рухомий стрижень", size=11.5, color=ORANGE, bold=True, anchor="start"))

    # плівка тягне стрижень усередину
    F.append(arrow(xR - 6, yT + 40, xR - 92, yT + 40, color=POS, sw=2.8))
    F.append(arrow(xR - 6, yB - 40, xR - 92, yB - 40, color=POS, sw=2.8))
    F.append(text((xL + xR) / 2 + 30, (yT + yB) / 2 - 8, "F = σ · 2L", size=17, color=POS, bold=True))
    F.append(text((xL + xR) / 2 + 30, (yT + yB) / 2 + 14, "дві поверхні → множник 2", size=11.5, color=POS))

    # утримувальна сила назовні
    F.append(arrow(xR + 10, (yT + yB) / 2, xR + 96, (yT + yB) / 2, color=INK, sw=2.6))
    F.append(text(xR + 104, (yT + yB) / 2 + 5, "утримуємо", size=12.5, color=INK, bold=True, anchor="start"))
    F.append(text(xR + 104, (yT + yB) / 2 + 23, "силою F", size=12.5, color=INK, anchor="start"))

    # розмір L
    F.append(arrow(xL - 22, yT, xL - 22, yB, color=INK, sw=1.6))
    F.append(arrow(xL - 22, yB, xL - 22, yT, color=INK, sw=1.6))
    F.append(text(xL - 30, (yT + yB) / 2 + 5, "L", size=16, color=INK, bold=True, italic=True, anchor="end"))

    # зсув Δx → нова площа
    F.append(line(xR + 40, yT, xR + 40, yB, color=MUTED, sw=1.6, dash="5 5"))
    F.append(arrow(xR, yB + 30, xR + 40, yB + 30, color=MUTED, sw=1.8))
    F.append(text(xR + 20, yB + 46, "Δx", size=12.5, color=MUTED, italic=True))

    F.append(fitbox(120, 402, 660, 62,
                    "потягнути стрижень на Δx назовні → нова площа 2L·Δx, робота σ·2L·Δx\n"
                    "σ = сила / довжина (Н/м)  =  енергія / площа (Дж/м²) — одне число, дві мови",
                    size=13.5, bold=True, fill="#eafaf0", stroke=GREEN, pad=10))

    render(os.path.join(IMG, "film-tension.svg"), W, H, *F,
           title="Плівка на рамці: сила на довжину — це те саме, що енергія на площу")


# ── Фігура 3: тиск під викривленою поверхнею (закон Лапласа) ──────────────────
def fig_laplace():
    W, H = 920, 540
    F = []
    cS = (250, 300); RS = 78
    cL = (650, 300); RL = 150
    R0 = 28  # старт стрілок відступає від центру, щоб не різати підписи "+Δp"/"малий"/"великий"

    # великий дроп
    F.append(circle(cL[0], cL[1], RL, fill=WATER, stroke=WATERD, sw=2.0))
    for a in [ -math.pi/2, math.pi/2, 0, math.pi ]:
        F.append(arrow(cL[0] + R0 * math.cos(a), cL[1] + R0 * math.sin(a),
                       cL[0] + 0.62 * RL * math.cos(a),
                       cL[1] + 0.62 * RL * math.sin(a), color="#e79a90", sw=2.0))
    F.append(text(cL[0], cL[1] - 6, "+Δp", size=17, color=POS, bold=True))
    F.append(text(cL[0], cL[1] + 16, "малий", size=12, color=MUTED))
    F.append(text(cL[0], cL[1] + RL + 30, "великий радіус → тиск малий", size=13, color=INK))

    # малий дроп
    F.append(circle(cS[0], cS[1], RS, fill=WATER, stroke=WATERD, sw=2.0))
    for k in range(8):
        a = k * math.pi / 4
        F.append(arrow(cS[0] + R0 * math.cos(a), cS[1] + R0 * math.sin(a),
                       cS[0] + 0.78 * RS * math.cos(a),
                       cS[1] + 0.78 * RS * math.sin(a), color=POS, sw=2.4))
    F.append(text(cS[0], cS[1] - 4, "+Δp", size=18, color=POS, bold=True))
    F.append(text(cS[0], cS[1] + 16, "великий", size=12, color=POS, bold=True))
    F.append(text(cS[0], cS[1] + RS + 30, "малий радіус → тиск високий", size=13, color=INK))

    # натяг стягує (тангенційні стрілки на малому дропі)
    F.append(arrow(cS[0] - 20, cS[1] - RS, cS[0] + 20, cS[1] - RS, color=NEG, sw=2.2))
    F.append(arrow(cS[0] + 20, cS[1] - RS, cS[0] - 20, cS[1] - RS, color=NEG, sw=2.2))
    F.append(text(cS[0], cS[1] - RS - 14, "натяг стягує поверхню", size=12, color=NEG, bold=True))

    # формула й закон
    F.append(textbox(460, 132, "Δp = 2σ / R", size=20, bold=True,
                     fill="#fdecea", stroke=POS, pad=12)[0])
    F.append(text(460, 176, "тиск ∝ 1 / R", size=14, color=POS, bold=True, italic=True))

    # мильна бульбашка — дві поверхні
    F.append(fitbox(700, 92, 200, 52,
                    "мильна бульбашка —\nдві поверхні → Δp = 4σ/R",
                    size=12.5, bold=True, fill=SOAP, stroke="#e6d78a", pad=8))

    F.append(fitbox(120, 470, 680, 44,
                    "Викривлена натягнута поверхня тисне на те, що під нею. "
                    "Що менший радіус — то крутіша кривина й вищий тиск усередині.",
                    size=13, bold=True, fill="#eafaf0", stroke=GREEN, pad=9))

    render(os.path.join(IMG, "laplace-pressure.svg"), W, H, *F,
           title="Тиск під викривленою поверхнею: менша крапля — вищий тиск")


# ── Фігура 4: капілярність — змочування, підйом і опускання ───────────────────
def fig_capillary():
    W, H = 960, 580
    F = []
    resY = 440          # рівень води в широкій посудині
    tubeTop = 150
    tubeBot = 486

    def glass(xi, wi):
        F.append(rect(xi - 5, tubeTop, 5, tubeBot - tubeTop, fill=GLASS, stroke=MERCD, sw=1.0, rx=1))
        F.append(rect(xi + wi, tubeTop, 5, tubeBot - tubeTop, fill=GLASS, stroke=MERCD, sw=1.0, rx=1))

    def concave(xi, wi, top, col, cold):
        # стовп води у трубці + угнутий меніск
        F.append(rect(xi, top, wi, 470 - top, fill=col, stroke="none"))
        xc = xi + wi / 2
        dip = min(7, wi * 0.35)
        # вирізати повітряний серпик над меніском (біле)
        F.append(path("M %.1f %.1f Q %.1f %.1f %.1f %.1f Z" %
                      (xi, top, xc, top + 2 * dip, xi + wi, top), fill=BG, stroke="none"))
        F.append(path("M %.1f %.1f Q %.1f %.1f %.1f %.1f" %
                      (xi, top, xc, top + 2 * dip, xi + wi, top), fill="none", stroke=cold, sw=1.6))

    # ── посудина з водою ──
    F.append(rect(80, resY, 430, 52, fill=WATER, stroke="none"))
    F.append(line(80, resY, 510, resY, color=WATERD, sw=2.0))
    F.append(line(80, resY, 80, 500, color=GLASS, sw=3))
    F.append(line(510, resY, 510, 500, color=GLASS, sw=3))
    F.append(line(80, 500, 510, 500, color=GLASS, sw=3))
    F.append(text(150, resY + 34, "вода", size=13, color="#3a6a86", italic=True))

    # тонка трубка (високий підйом)
    x1, w1, top1 = 205, 16, 188
    glass(x1, w1)
    concave(x1, w1, top1, WATER, WATERD)
    # товста трубка (низький підйом)
    x2, w2, top2 = 360, 34, 306
    glass(x2, w2)
    concave(x2, w2, top2, WATER, WATERD)

    # висоти h
    F.append(line(150, resY, 150, top1, color=POS, sw=1.4, dash="5 5"))
    F.append(arrow(150, top1 + 4, 150, top1, color=POS, sw=1.6))
    F.append(text(140, (resY + top1) / 2, "h₁", size=15, color=POS, bold=True, italic=True, anchor="end"))
    F.append(line(330, resY, 330, top2, color=ORANGE, sw=1.4, dash="5 5"))
    F.append(text(320, (resY + top2) / 2 + 4, "h₂", size=15, color=ORANGE, bold=True, italic=True, anchor="end"))

    F.append(text(x1 + w1 / 2, tubeTop - 16, "тонка", size=12, color=POS, bold=True))
    F.append(text(x2 + w2 / 2, tubeTop - 16, "товста", size=12, color=ORANGE, bold=True))
    F.append(fitbox(95, 512, 420, 44,
                    "вода ЗМОЧУЄ скло (θ ≈ 0): лізе вгору;\nтонша трубка → вище   (h ∝ 1/r)",
                    size=12.5, bold=True, fill="#eaf3fb", stroke=WATERD, pad=8))

    # ── посудина з ртуттю ──
    rx0, rx1 = 600, 900
    F.append(rect(rx0, resY, rx1 - rx0, 52, fill=MERC, stroke="none"))
    F.append(line(rx0, resY, rx1, resY, color=MERCD, sw=2.0))
    F.append(line(rx0, resY, rx0, 500, color=GLASS, sw=3))
    F.append(line(rx1, resY, rx1, 500, color=GLASS, sw=3))
    F.append(line(rx0, 500, rx1, 500, color=GLASS, sw=3))
    F.append(text(rx0 + 60, resY + 34, "ртуть", size=13, color="#5a5e66", italic=True))

    # трубка з опущеною ртуттю + опуклий меніск
    xm, wm, topm = 738, 26, 476
    glass(xm, wm)
    F.append(rect(xm, topm, wm, 470 - topm, fill=MERC, stroke="none"))
    xc = xm + wm / 2
    bulge = 9
    F.append(path("M %.1f %.1f Q %.1f %.1f %.1f %.1f Z" %
                  (xm, topm, xc, topm - 2 * bulge, xm + wm, topm), fill=MERC, stroke="none"))
    F.append(path("M %.1f %.1f Q %.1f %.1f %.1f %.1f" %
                  (xm, topm, xc, topm - 2 * bulge, xm + wm, topm), fill="none", stroke=MERCD, sw=1.6))
    F.append(line(rx0 + 10, resY, xm - 12, resY, color=MUTED, sw=1.2, dash="4 5"))
    F.append(arrow(xc, resY + 4, xc, topm - bulge - 2, color=MERCD, sw=1.6))
    F.append(text(xc + 40, (resY + topm) / 2, "нижче рівня", size=12, color="#5a5e66", anchor="start"))

    F.append(fitbox(610, 512, 300, 44,
                    "ртуть НЕ змочує скло (θ > 90°):\nопускається, меніск опуклий",
                    size=12.5, bold=True, fill="#eef0f2", stroke=MERCD, pad=8))

    render(os.path.join(IMG, "capillary-rise.svg"), W, H, *F,
           title="Капілярність: змочувальна рідина лізе вгору, незмочувальна — опускається")


PURPLE = "#8e44ad"


# ── Фігура 5 (hist): часова стрічка розуміння натягу ─────────────────────────
def fig_hist_timeline():
    W, H = 1000, 772
    F = []
    spineX = 300
    y0, step = 96, 66

    # категорія: (колір, підпис у легенді)
    rows = [
        ("~1490", "Леонардо да Вінчі", "чорнило саме лізе шпаринами — перше спостереження", MUTED),
        ("1709",  "Френсіс Гоксбі",    "точні виміри; ефект лишається й у порожнечі", MUTED),
        ("1718",  "Джеймс Жюрен",      "закон: тонша трубка — вище   (h ∝ 1/r)", WATERD),
        ("1805",  "Томас Юнг",         "крайовий кут, описаний самими СЛОВАМИ", ORANGE),
        ("1806",  "П'єр-Симон Лаплас", "тиск через кривину — строга ФОРМУЛА", POS),
        ("1830",  "Карл Фрідріх Гаусс","усе випливає з мінімуму ЕНЕРГІЇ", FIELD),
        ("1849",  "Жозеф Плато",       "мильні плівки; мінімальні поверхні; закони 120°", PURPLE),
        ("1891",  "Агнеса Покельс",    "корито на кухні; моношар; лист до лорда Релея", PURPLE),
        ("1917–35","Ленгмюр і Блоджетт","керовані молекулярні плівки — нова наука", PURPLE),
    ]

    yTop = y0 - 24
    yBot = y0 + (len(rows) - 1) * step + 24
    F.append(line(spineX, yTop, spineX, yBot, color=MUTED, sw=2.4))

    bx, bw, bh = 332, 620, 50
    for i, (yr, name, role, col) in enumerate(rows):
        y = y0 + i * step
        # рік ліворуч від хребта
        F.append(text(spineX - 24, y + 5, yr, size=14.5, color=INK, bold=True, anchor="end"))
        # картка праворуч
        F.append(rect(bx, y - bh / 2, bw, bh, fill="#fbfcfd", stroke=col, sw=2.0, rx=7))
        F.append(rect(bx, y - bh / 2, 7, bh, fill=col, stroke="none", rx=3))
        F.append(text(bx + 20, y - 6, name, size=15.5, color=INK, bold=True, anchor="start"))
        F.append(text(bx + 20, y + 16, role, size=12.5, color=MUTED, anchor="start"))
        # вузол на хребті
        F.append(circle(spineX, y, 9, fill=col, stroke=BG, sw=2.4))
        F.append(line(spineX + 9, y, bx, y, color=col, sw=1.6))

    # легенда: колір → сходинка розуміння
    ly = yBot + 40
    F.append(text(70, ly - 22, "сходинка розуміння:", size=12.5, color=INK, bold=True, anchor="start"))
    legend = [
        (MUTED, "спостереження"), (WATERD, "число-закон"), (ORANGE, "слово"),
        (POS, "формула"), (FIELD, "енергія"), (PURPLE, "дослід"),
    ]
    lx = [70, 250, 420, 540, 680, 830]
    for (col, lab), x in zip(legend, lx):
        F.append(circle(x, ly, 7, fill=col, stroke=BG, sw=1.4))
        F.append(text(x + 14, ly + 5, lab, size=12.5, color=INK, anchor="start"))

    render(os.path.join(IMG, "hist-timeline.svg"), W, H, *F,
           title="Сходинки до розуміння натягу: побачити → зміряти → сказати → вивести → звести до енергії")


# ── Фігура 6 (hist): корито Покельс ──────────────────────────────────────────
def fig_hist_pockels():
    W, H = 1000, 560
    F = []
    # ── таця з водою (боковий розріз) ──
    txL, txR = 110, 660
    surf = 300
    bot = 412
    F.append(rect(txL + 6, surf, txR - txL - 12, bot - surf, fill=WATER, stroke="none"))
    # стінки таці
    F.append(line(txL, 250, txL, bot, color=GLASS, sw=6))
    F.append(line(txR, 250, txR, bot, color=GLASS, sw=6))
    F.append(line(txL, bot, txR, bot, color=GLASS, sw=6))
    F.append(line(txL + 6, surf, txR - 6, surf, color=WATERD, sw=2.2))
    F.append(text(txL + 70, bot - 24, "корито: таця з водою по вінця", size=12.5,
                  color="#3a6a86", italic=True, anchor="start"))

    # ── бар'єри ──
    fixX = 232      # нерухома планка
    movX = 430      # рухома планка
    def barrier(x, col, lab, labcol):
        F.append(rect(x - 7, surf - 26, 14, 34, fill=col, stroke=INK, sw=1.4, rx=2))
        F.append(text(x, surf - 34, lab, size=12, color=labcol, bold=True))
    barrier(fixX, GLASS, "нерухома планка", "#5a5e66")
    barrier(movX, ORANGE, "рухома планка", ORANGE)
    # стрілка стиснення
    F.append(arrow(movX - 12, surf - 44, fixX + 24, surf - 44, color=ORANGE, sw=2.4))
    F.append(text((fixX + movX) / 2, surf - 52, "стискаємо плівку", size=12, color=ORANGE, bold=True))

    # ── плівка: молекули стоять «частоколом» між планками ──
    F.append(rect(fixX + 8, surf - 4, movX - fixX - 16, 4, fill=SOAP, stroke="none"))
    mx = fixX + 20
    while mx < movX - 12:
        F.append(line(mx, surf - 2, mx, surf - 16, color="#b5791f", sw=2.2))
        F.append(dot(mx, surf - 19, 3.4, "#e08e0b"))
        mx += 18
    F.append(text((fixX + movX) / 2, surf + 34, "плівка — один шар молекул",
                  size=12, color="#8a6a1a", italic=True))

    # ── ґудзик на нитці + терези ──
    diskX = 566
    F.append(rect(diskX - 22, surf - 3, 44, 7, fill=MERC, stroke=MERCD, sw=1.2, rx=2))
    F.append(line(diskX, surf - 3, diskX, 168, color=INK, sw=1.8))
    F.append(text(diskX, surf + 46, "ґудзик на нитці", size=12, color=INK, anchor="middle"))
    # натяг тримає ґудзик знизу
    F.append(arrow(diskX + 14, surf + 20, diskX + 14, surf + 2, color=POS, sw=2.2))
    F.append(text(diskX + 20, surf + 30, "натяг тягне вниз", size=11.5, color=POS, anchor="start"))

    # коромисло терезів
    beamY = 158
    pivX = 700
    F.append(line(diskX, beamY, 838, beamY, color=INK, sw=4))
    F.append(path("M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" %
                  (pivX - 16, beamY + 46, pivX + 16, beamY + 46, pivX, beamY),
                  fill=MERC, stroke=INK, sw=1.4))
    # права шалька з важками
    F.append(line(832, beamY, 832, beamY + 34, color=INK, sw=1.6))
    F.append(path("M %.1f %.1f Q %.1f %.1f %.1f %.1f" %
                  (812, beamY + 34, 832, beamY + 54, 852, beamY + 34), fill="none", stroke=INK, sw=1.8))
    F.append(rect(820, beamY + 20, 24, 14, fill=MERCD, stroke=INK, sw=1.2, rx=2))
    F.append(text(832, beamY + 78, "важки", size=11.5, color=INK))
    F.append(text(pivX + 6, beamY - 12, "аптекарські терези", size=12.5, color=INK, bold=True, anchor="start"))
    F.append(text(pivX + 6, beamY + 8, "міряють силу натягу", size=12, color=MUTED, anchor="start"))

    F.append(fitbox(120, 470, 760, 56,
                    "Стиснеш плівку планкою — натяг падає; терези одразу це читають силою на ґудзику.\n"
                    "Так самоучка Агнеса Покельс уперше кількісно виміряла поверхню — начинням із власної кухні.",
                    size=13, bold=True, fill="#eafaf0", stroke=FIELD, pad=10))

    render(os.path.join(IMG, "hist-pockels.svg"), W, H, *F,
           title="Корито Покельс: планка стискає плівку, терези міряють натяг")


def arc_pts(ox, oy, r, a0, a1, n=18):
    return [(ox + r * math.cos(math.radians(a)), oy - r * math.sin(math.radians(a)))
            for a in frange(a0, a1, n)]


def polyline(pts, color=INK, sw=2.0, dash=None):
    return "".join(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                        color=color, sw=sw, dash=dash) for i in range(len(pts) - 1))


# ── Фігура (math): баланс сил на півкулі → Δp = 2σ/R ──────────────────────────
def fig_hemisphere():
    W, H = 920, 570
    F = []
    cx, cy, R = 430, 270, 140

    # прибрана (ліва) півкуля — пунктиром: кулю розрізали навпіл
    F.append(path("M %.1f %.1f A %.1f %.1f 0 0 0 %.1f %.1f" %
                  (cx, cy - R, R, R, cx, cy + R), fill="none", stroke=WATERD, sw=1.4))
    # права півкуля — суцільна, заповнена
    F.append(path("M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f L %.1f %.1f Z" %
                  (cx, cy - R, R, R, cx, cy + R, cx, cy - R), fill=WATER, stroke=WATERD, sw=2.0))
    # площина перерізу (екватор, з ребра) — пунктир
    F.append(line(cx, cy - R - 8, cx, cy + R + 8, color=MUTED, sw=1.4, dash="6 5"))
    F.append(text(cx, cy - R - 16, "площина перерізу (екватор)", size=12, color=MUTED, italic=True))

    # радіус
    F.append(line(cx, cy, cx + R, cy, color=INK, sw=1.4, dash="5 5"))
    F.append(text(cx + R / 2, cy - 8, "R", size=15, color=INK, bold=True, italic=True))
    F.append(dot(cx, cy, 3.5, INK))

    # тиск на переріз — назовні (праворуч)
    for dy in (-58, 0, 58):
        F.append(arrow(cx + 6, cy + dy, cx + 74, cy + dy, color=POS, sw=2.8))
    F.append(text(cx + 150, cy - 8, "тиск Δp", size=13.5, color=POS, bold=True, anchor="start"))
    F.append(text(cx + 150, cy + 12, "тисне назовні", size=12.5, color=POS, anchor="start"))
    F.append(text(cx + 150, cy + 30, "на переріз πR²", size=12.5, color=POS, anchor="start"))

    # натяг по ободу — до перерізу (ліворуч), угорі й унизу
    F.append(arrow(cx, cy - R, cx - 70, cy - R, color=NEG, sw=2.6))
    F.append(arrow(cx, cy + R, cx - 70, cy + R, color=NEG, sw=2.6))
    F.append(text(cx - 78, cy - R - 6, "натяг σ по ободу 2πR", size=12.5, color=NEG, bold=True, anchor="end"))
    F.append(text(cx - 78, cy + R + 18, "тягне до перерізу", size=12.5, color=NEG, anchor="end"))

    # формули знизу
    F.append(textbox(232, 452, "F(натяг) = σ · 2πR", size=15, bold=True,
                     fill="#eaf0fd", stroke=NEG, pad=11)[0])
    F.append(textbox(640, 452, "F(тиск) = Δp · πR²", size=15, bold=True,
                     fill="#fdecea", stroke=POS, pad=11)[0])
    F.append(fitbox(150, 506, 620, 46,
                    "рівновага півкулі:  Δp · πR² = σ · 2πR   ⟹   Δp = 2σ / R",
                    size=15, bold=True, fill="#eafaf0", stroke=FIELD, pad=10))

    render(os.path.join(IMG, "hemisphere-balance.svg"), W, H, *F,
           title="Δp = 2σ/R балансом сил: розріж кулю навпіл")


# ── Фігура (math): загальна кривина → Δp = σ(1/R₁ + 1/R₂) ─────────────────────
def fig_patch():
    W, H = 980, 580
    F = []

    # ── лівий блок: ЧОМУ кривина дає силу до центра ──
    ox, oy, Rr = 250, 470, 230
    surf = arc_pts(ox, oy, Rr, 112, 68, 20)
    F.append(polyline(surf, color=WATERD, sw=3.2))
    top = (ox, oy - Rr)
    L, Rt = surf[0], surf[-1]
    F.append(line(ox, oy, top[0], top[1], color=INK, sw=1.3, dash="5 5"))
    F.append(line(ox, oy, L[0], L[1], color=MUTED, sw=1.1, dash="4 5"))
    F.append(line(ox, oy, Rt[0], Rt[1], color=MUTED, sw=1.1, dash="4 5"))
    F.append(dot(ox, oy, 3.5, INK))
    F.append(text(ox, oy + 20, "центр кривини", size=11.5, color=MUTED))
    F.append(text(ox + 12, (oy + top[1]) / 2, "R", size=15, color=INK, bold=True, italic=True, anchor="start"))
    for P, ex in ((L, (-0.982, 0.190)), (Rt, (0.982, 0.190))):
        F.append(arrow(P[0], P[1], P[0] + 72 * ex[0], P[1] + 72 * ex[1], color=NEG, sw=2.6))
    F.append(text(L[0] - 40, L[1] + 36, "σ·w", size=13, color=NEG, bold=True))
    F.append(text(Rt[0] + 40, Rt[1] + 36, "σ·w", size=13, color=NEG, bold=True))
    F.append(arrow(top[0], top[1], top[0], top[1] - 44, color=POS, sw=3.0))
    F.append(text(top[0], top[1] - 52, "Δp назовні", size=12.5, color=POS, bold=True))
    F.append(arrow(top[0], top[1] + 6, top[0], top[1] + 58, color=NEG, sw=3.0))
    F.append(text(top[0] + 132, top[1] + 40, "рівнодійна натягу", size=12, color=NEG, bold=True))
    F.append(text(top[0] + 132, top[1] + 57, "— до центра", size=12, color=NEG))
    F.append(fitbox(46, 496, 398, 78,
                    "два крайові натяги на дузі не гасяться —\n"
                    "їхня рівнодійна тисне до центра,\n"
                    "тим більша, чим крутіша дуга (менший R)",
                    size=12.5, bold=True, fill="#eaf0fd", stroke=NEG, pad=9))

    F.append(line(486, 60, 486, 556, color="#dfe3e8", sw=1.4))

    # ── правий блок: клаптик з двома радіусами й формула ──
    px, py, pw, ph = 648, 118, 152, 94
    F.append(rect(px, py, pw, ph, fill=WATER, stroke=WATERD, sw=1.8, rx=6))
    mx, my = px + pw / 2, py + ph / 2
    # натяг на всіх чотирьох краях — стрілки зсунуто від підписів
    F.append(arrow(mx - 34, py, mx - 34, py - 28, color=NEG, sw=2.2))
    F.append(arrow(mx + 34, py + ph, mx + 34, py + ph + 28, color=NEG, sw=2.2))
    F.append(arrow(px, my - 20, px - 28, my - 20, color=NEG, sw=2.2))
    F.append(arrow(px + pw, my + 20, px + pw + 28, my + 20, color=NEG, sw=2.2))
    F.append(text(mx + 24, py - 12, "dℓ₁", size=13, color=INK, italic=True, anchor="start"))
    F.append(text(px + pw + 12, my - 10, "dℓ₂", size=13, color=INK, italic=True, anchor="start"))

    F.append(textbox(730, 300, "Δp = σ · (1/R₁ + 1/R₂)", size=19, bold=True,
                     fill="#fdecea", stroke=POS, pad=12)[0])
    F.append(fitbox(556, 336, 350, 40,
                    "R₁, R₂ — головні радіуси кривини (у двох ⊥ напрямках)",
                    size=12.5, fill=FILL, stroke=MUTED, pad=8))
    F.append(fitbox(540, 388, 406, 128,
                    "куля:   R₁ = R₂ = R   →   Δp = 2σ/R\n"
                    "довгий циліндр:   R₂ → ∞   →   Δp = σ/R\n"
                    "мильна бульбашка (дві поверхні):   Δp = 4σ/R",
                    size=13.5, bold=True, fill="#eafaf0", stroke=FIELD, pad=11))

    render(os.path.join(IMG, "curved-patch.svg"), W, H, *F,
           title="Загальна кривина: тиск = натяг на суму обернених радіусів")


# ── Фігура (math): рівняння Юнга — три натяги на лінії контакту ───────────────
def fig_young():
    W, H = 940, 520
    F = []
    F.append(rect(120, 330, 560, 66, fill=GLASS, stroke=MERCD, sw=1.2, rx=2))
    F.append(text(610, 368, "тверде тіло", size=12.5, color="#4a4e56", italic=True))
    F.append(text(470, 150, "пара / повітря", size=12.5, color=MUTED, italic=True))

    F.append(path("M 330 330 Q 470 170 610 330 Z", fill=WATER, stroke=WATERD, sw=2.0))
    F.append(text(474, 300, "рідина", size=13, color="#3a6a86", italic=True))

    px, py = 330, 330
    F.append(dot(px, py, 3.6, INK))
    F.append(arrow(px, py, px - 84, py, color=MERCD, sw=2.8))
    F.append(text(px - 92, py - 16, "σsᴠ", size=14, color="#4a4e56", bold=True, anchor="end"))
    F.append(arrow(px, py, px + 88, py, color=WATERD, sw=2.8))
    F.append(text(px + 96, py + 6, "σsʟ", size=14, color="#2f6a8c", bold=True, anchor="start"))
    F.append(arrow(px, py, px + 47, py - 82, color=NEG, sw=2.9))
    F.append(text(px + 6, py - 84, "σ", size=15, color=NEG, bold=True, anchor="end"))
    F.append(text(px + 16, py - 84, "(= σʟᴠ)", size=11, color=NEG, anchor="start"))
    F.append(polyline(arc_pts(px, py, 44, 4, 56, 12), color=INK, sw=1.5))
    F.append(text(px + 70, py - 16, "θ", size=16, color=INK, bold=True, italic=True))

    F.append(textbox(760, 150, "σsᴠ = σsʟ + σ·cos θ", size=16, bold=True,
                     fill="#eafaf0", stroke=FIELD, pad=11)[0])
    F.append(text(760, 196, "cos θ = (σsᴠ − σsʟ) / σ", size=13.5, color=INK))
    F.append(text(760, 218, "знак різниці → змочує чи ні", size=12, color=MUTED))

    F.append(path("M 175 458 Q 250 430 325 458 Z", fill=WATER, stroke=WATERD, sw=1.6))
    F.append(text(250, 480, "θ < 90°:  змочує", size=12.5, color="#2f6a8c", bold=True))
    F.append(path("M 545 458 Q 595 384 645 458 Z", fill=WATER, stroke=WATERD, sw=1.6))
    F.append(text(595, 480, "θ > 90°:  не змочує", size=12.5, color="#7a5a2a", bold=True))
    F.append(line(120, 420, 680, 420, color="#dfe3e8", sw=1.2))

    render(os.path.join(IMG, "young-contact.svg"), W, H, *F,
           title="Рівняння Юнга: три натяги врівноважуються на лінії контакту")


if __name__ == "__main__":
    fig_molecular()
    fig_film()
    fig_laplace()
    fig_capillary()
    fig_hist_timeline()
    fig_hist_pockels()
    fig_hemisphere()
    fig_patch()
    fig_young()
    print("OK: 9 SVG ->", IMG)
