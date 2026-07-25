# -*- coding: utf-8 -*-
"""Фігури для теми ground-plane-design (проєктування площини землі).
svgkit імпортуємо зі scripts/, НЕ переписуємо (AUTHORING §5)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

COPPER = "#b5763a"   # колір міді доріжки
GOLD   = "#caa24a"


def density(cx, base_y, width, height, color, n=44):
    """Заповнений «дзвін» щільності струму, що стоїть на лінії base_y (пік угору)."""
    pts = []
    for i in range(n + 1):
        x = cx - width + (2 * width) * i / n
        g = math.exp(-((x - cx) / (width * 0.42)) ** 2)
        pts.append((x, base_y - height * g))
    d = "M %.1f %.1f " % (cx - width, base_y)
    for (x, y) in pts:
        d += "L %.1f %.1f " % (x, y)
    d += "L %.1f %.1f Z" % (cx + width, base_y)
    return ('<path d="%s" fill="%s" fill-opacity="0.32" stroke="%s" '
            'stroke-width="1.6"/>' % (d, color, color))


# ── 1. Зворотний струм над суцільною площиною ────────────────────────────────
def fig_return_current():
    W, H = 760, 420
    f = []

    # Панель А — висока частота
    f.append(text(380, 58, "висока частота — зворот стягнуто під доріжку",
                  size=13, color=POS, bold=True))
    f.append(rect(340, 82, 80, 12, fill=COPPER, stroke=COPPER, sw=1, rx=2))
    f.append(text(432, 78, "доріжка (прямий струм →)", size=11, color=INK, anchor="start"))
    f.append(rect(140, 160, 480, 26, fill="#eef0f2", stroke=MUTED, sw=1.2, rx=3))
    f.append(density(380, 160, 58, 50, POS))
    f.append(text(380, 206, "суцільна площина землі", size=11, color=MUTED))

    # роздільник панелей
    f.append(line(120, 224, 640, 224, color=MUTED, sw=1, dash="4,4"))

    # Панель Б — постійний струм
    f.append(text(380, 252, "постійний струм — зворот розлитий по всій міді",
                  size=13, color=NEG, bold=True))
    f.append(rect(340, 276, 80, 12, fill=COPPER, stroke=COPPER, sw=1, rx=2))
    f.append(text(432, 272, "та сама доріжка", size=11, color=INK, anchor="start"))
    f.append(rect(140, 352, 480, 26, fill="#eef0f2", stroke=MUTED, sw=1.2, rx=3))
    f.append(density(380, 352, 228, 16, NEG))
    f.append(text(380, 398, "зворот шукає найменший опір — розтікається широко",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "return-current.svg"), W, H, *f,
           title="Зворотний струм над суцільною площиною")


# ── 2. Зв'язок через спільний імпеданс ───────────────────────────────────────
def fig_common_impedance():
    W, H = 780, 400
    f = []
    railY = 300

    # спільна земляна мідь
    f.append(line(140, railY, 600, railY, color=COPPER, sw=9))
    # справжній нуль (символ землі праворуч)
    f.append(line(600, railY, 618, railY, color=INK, sw=2))
    f.append(line(618, railY, 618, railY + 12, color=INK, sw=2))
    for w, dy in [(22, 12), (14, 18), (7, 23)]:
        f.append(line(618 - w, railY + dy, 618 + w, railY + dy, color=INK, sw=2))
    f.append(text(618, railY - 12, "справжній нуль", size=11, color=INK))

    # силове коло (ліворуч)
    f.append(rect(160, 90, 150, 72, fill="#fdecea", stroke=POS, sw=2))
    f.append(mtext(235, 122, ["силове коло", "(перетворювач)"], size=12, color=INK))
    f.append(line(235, 162, 235, railY, color=POS, sw=2.4))

    # тихе коло (праворуч)
    f.append(rect(398, 90, 178, 72, fill="#eef7f0", stroke=FIELD, sw=2))
    f.append(mtext(487, 122, ["тихий еталон", "(АЦП, дільник ЗЗ)"], size=12, color=INK))
    f.append(line(487, 162, 487, railY, color=FIELD, sw=2.4))
    f.append(circle(487, railY, 5, fill=INK, stroke=INK))
    f.append(text(505, 205, "точка А", size=11, color=FIELD, bold=True, anchor="start"))

    # струм силового кола вздовж рейки
    f.append(arrow(250, 285, 588, 285, color=POS))
    f.append(text(410, 275, "I — зворот силового кола →", size=12, color=POS, bold=True))

    # спільний відтинок [А — нуль]
    f.append('<rect x="487" y="292" width="113" height="16" fill="%s" '
             'fill-opacity="0.18"/>' % POS)
    f.append(text(543, 332, "спільна мідь: Z = R + jωL", size=11, color=POS, bold=True))

    bx, bw, bh = textbox(
        390, 366,
        ["Струм силового кола тече крізь спільну мідь [А — нуль]",
         "і піднімає точку А на I·Z над справжнім нулем."],
        size=12, fill="#fbf7ec", stroke=GOLD)
    f.append(bx)

    render(os.path.join(OUT, "common-impedance.svg"), W, H, *f,
           title="Зв'язок через спільний імпеданс")


# ── 3. Розріз у площині роздуває зворотний контур ────────────────────────────
def fig_slot_detour():
    W, H = 760, 400
    f = []
    # площина (вид згори)
    f.append(rect(110, 118, 540, 214, fill="#eef0f2", stroke=MUTED, sw=1.3))
    f.append(text(120, 136, "площина землі (вид згори)", size=11, color=MUTED, anchor="start"))
    # розріз (біла щілина від верхнього краю до y=262)
    f.append('<rect x="372" y="118" width="16" height="144" fill="#ffffff" '
             'stroke="%s" stroke-width="1.6"/>' % POS)
    f.append(text(398, 150, "розріз", size=12, color=POS, bold=True, anchor="start"))

    # сигнальна доріжка зверху, перетинає розріз
    f.append(line(150, 175, 610, 175, color=COPPER, sw=6))
    f.append(text(150, 163, "доріжка (прямий струм →)", size=11, color=INK, anchor="start"))

    # ідеальний зворот (пунктир, якби не розрізу)
    f.append(line(160, 198, 600, 198, color=MUTED, sw=1.4, dash="5,4"))
    f.append(text(150, 240, "як було б без розрізу — прямо під доріжкою",
                  size=10, color=MUTED, anchor="start"))

    # фактичний зворот з обходом розрізу
    seg = [(600, 212), (392, 212), (392, 288), (356, 288), (356, 212), (160, 212)]
    for i in range(len(seg) - 1):
        (x1, y1), (x2, y2) = seg[i], seg[i + 1]
        f.append(line(x1, y1, x2, y2, color=POS, sw=2.6))
    f.append(arrow(232, 212, 176, 212, color=POS))

    # зайва площа контуру
    f.append('<rect x="356" y="212" width="36" height="76" fill="%s" '
             'fill-opacity="0.16"/>' % POS)
    f.append(text(230, 272, "зворот мусить обходити щілину", size=10, color=POS, bold=True))
    f.append(text(374, 306, "зайва площа", size=10, color=POS, bold=True))

    f.append(text(380, 360,
                  "Обхід роздуває контур: площа росте → індуктивність, викид, випромінювання.",
                  size=12, color=INK))

    render(os.path.join(OUT, "slot-detour.svg"), W, H, *f,
           title="Розріз у площині роздуває зворотний контур")


# ── 4. Зіркова точка: суцільна площина + розмежування ────────────────────────
def fig_star_tie():
    W, H = 800, 440
    f = []
    # суцільна площина
    f.append(rect(90, 110, 620, 270, fill="#eef0f2", stroke=MUTED, sw=1.3))
    f.append(text(400, 132, "суцільна площина землі — не різати", size=13, color=INK, bold=True))

    # зони (розмежування розкладкою)
    f.append('<rect x="105" y="150" width="285" height="205" rx="8" '
             'fill="%s" fill-opacity="0.07"/>' % POS)
    f.append('<rect x="410" y="150" width="285" height="205" rx="8" '
             'fill="%s" fill-opacity="0.07"/>' % FIELD)
    f.append(text(247, 172, "силова зона", size=12, color=POS, bold=True))
    f.append(text(552, 172, "тиха зона", size=12, color=FIELD, bold=True))

    # межа зон — не розріз
    f.append(line(400, 150, 400, 352, color=MUTED, sw=1.4, dash="6,5"))
    f.append(text(400, 372, "межа — розкладкою, не розрізом", size=10, color=MUTED))

    # силове коло
    f.append(rect(150, 196, 150, 58, fill="#fdecea", stroke=POS, sw=2))
    f.append(mtext(225, 218, ["перетворювач", "(гаряча петля тут)"], size=11, color=INK))

    # тихе коло
    f.append(rect(470, 196, 178, 58, fill="#eef7f0", stroke=FIELD, sw=2))
    f.append(mtext(559, 218, ["АЦП · еталон", "дільник ЗЗ"], size=12, color=INK))

    # зіркова точка й промені
    sx, sy = 400, 318
    f.append(line(225, 254, sx, sy, color=POS, sw=2.4))
    f.append(line(559, 254, sx, sy, color=FIELD, sw=2.4))
    f.append(circle(sx, sy, 7, fill="#fff3cd", stroke=GOLD, sw=2.4))
    f.append(text(sx + 16, sy - 4, "зіркова точка", size=12, color="#8a6d1a",
                  bold=True, anchor="start"))
    f.append(text(sx + 16, sy + 12, "(біля звороту Cвх)", size=10, color=MUTED, anchor="start"))

    f.append(text(400, 414,
                  "Тихі землі сходяться в зірковій точці, де силовий зворот уже замкнувся.",
                  size=12, color=INK))

    render(os.path.join(OUT, "star-tie.svg"), W, H, *f,
           title="Зіркова точка: суцільна площина плюс розмежування")


# ── 5. AGND/DGND — береги всередині кристала (для hist-вставки) ───────────────
def _gnd(x, y, color, sw=1.8):
    """Символ землі: вертикальний стовпчик і три бруски, що звужуються."""
    out = [line(x, y, x, y + 8, color=color, sw=sw)]
    for w, dy in [(11, 8), (7, 12), (3, 15)]:
        out.append(line(x - w, y + dy, x + w, y + dy, color=color, sw=sw))
    return out


def fig_agnd_dgnd():
    W, H = 820, 414
    f = []

    # пояснення над корпусом
    f.append(text(410, 52,
                  "у кристалі землі роз'єднані: цифровий сплеск не займає аналог",
                  size=11, color=MUTED))

    # корпус мікросхеми
    f.append(rect(200, 66, 420, 150, fill="#fbfbfd", stroke=INK, sw=2, rx=10))
    f.append(text(410, 90, "корпус мікросхеми (АЦП / ЦАП)", size=13, color=INK, bold=True))

    # аналогова частина (ліворуч)
    f.append(rect(224, 106, 168, 86, fill="#eef7f0", stroke=FIELD, sw=2))
    f.append(text(308, 128, "аналогова частина", size=12, color=INK, bold=True))
    f.extend(_gnd(308, 150, FIELD))
    f.append(text(308, 184, "внутр. аналог. земля", size=10, color=MUTED))

    # цифрова частина (праворуч)
    f.append(rect(428, 106, 168, 86, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(512, 128, "цифрова частина", size=12, color=INK, bold=True))
    f.extend(_gnd(512, 150, POS))
    f.append(text(512, 184, "внутр. цифрова земля", size=10, color=MUTED))

    # межа в кристалі
    f.append(line(410, 106, 410, 192, color=MUTED, sw=1.4, dash="5,4"))

    # виводи-ніжки
    f.append(line(308, 216, 308, 244, color=INK, sw=2))
    f.append(circle(308, 244, 4, fill=FIELD, stroke=FIELD))
    f.append(text(308, 262, "вивід AGND", size=12, color=FIELD, bold=True))
    f.append(line(512, 216, 512, 244, color=INK, sw=2))
    f.append(circle(512, 244, 4, fill=POS, stroke=POS))
    f.append(text(512, 262, "вивід DGND", size=12, color=POS, bold=True))

    # спільна перемичка виводів
    f.append(line(308, 272, 308, 292, color=GOLD, sw=3))
    f.append(line(512, 272, 512, 292, color=GOLD, sw=3))
    f.append(line(308, 292, 512, 292, color=GOLD, sw=3))
    f.append(circle(410, 292, 5, fill="#fff3cd", stroke=GOLD, sw=2))
    f.append(text(536, 288, "з'єднати найкоротше — обидва виводи разом",
                  size=11, color="#8a6d1a", bold=True, anchor="start"))

    # злив на одну площину
    f.append(arrow(410, 292, 410, 330, color=GOLD))
    f.append(rect(150, 332, 520, 54, fill="#eef0f2", stroke=MUTED, sw=1.3))
    f.append(text(410, 364, "ОДНА суцільна тиха (аналогова) площина землі",
                  size=13, color=INK, bold=True))

    render(os.path.join(OUT, "agnd-dgnd-inside.svg"), W, H, *f,
           title="AGND і DGND — це береги ВСЕРЕДИНІ кристала")


# ── 6. Лоренціан густини зворотного струму (для math-вставки) ─────────────────
def fig_lorentzian():
    W, H = 800, 440
    f = []
    x0, ybase, ytop = 400, 356, 96
    pxh = 48
    span = 6

    # вісь d
    f.append(line(96, ybase, 720, ybase, color=INK, sw=1.5))
    f.append(arrow(720, ybase, 734, ybase, color=INK))
    f.append(text(716, ybase + 30, "відстань убік від доріжки (в одиницях h)",
                  size=11, color=MUTED, anchor="end"))
    for u in range(-5, 6):
        x = x0 + u * pxh
        f.append(line(x, ybase, x, ybase + 5, color=INK, sw=1))
        f.append(text(x, ybase + 19, "0" if u == 0 else ("%+d" % u),
                      size=10, color=MUTED))

    # заливка смуги ±h
    dfill = "M %.1f %.1f " % (x0 - pxh, ybase)
    M = 44
    for i in range(M + 1):
        u = -1 + 2.0 * i / M
        x = x0 + u * pxh
        y = ybase - (ybase - ytop) * (1.0 / (1.0 + u * u))
        dfill += "L %.1f %.1f " % (x, y)
    dfill += "L %.1f %.1f Z" % (x0 + pxh, ybase)
    f.append('<path d="%s" fill="%s" fill-opacity="0.20" stroke="none"/>' % (dfill, POS))

    # крива
    d = ""
    N = 130
    for i in range(N + 1):
        u = -span + 2 * span * i / N
        x = x0 + u * pxh
        y = ybase - (ybase - ytop) * (1.0 / (1.0 + u * u))
        d += ("M %.1f %.1f " % (x, y)) if i == 0 else ("L %.1f %.1f " % (x, y))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, POS))

    # вертикалі ±h, ±3h
    for u, col in [(-1, MUTED), (1, MUTED), (-3, NEG), (3, NEG)]:
        x = x0 + u * pxh
        y = ybase - (ybase - ytop) * (1.0 / (1.0 + u * u))
        f.append(line(x, ybase, x, y, color=col, sw=1.2, dash="4,3"))

    # лінія піввисоти
    yh = ybase - (ybase - ytop) * 0.5
    f.append(line(x0 - pxh, yh, x0 + pxh, yh, color=MUTED, sw=1, dash="2,3"))
    f.append(text(x0 + pxh + 10, yh + 4, "піввисота → повна ширина 2h",
                  size=10, color=MUTED, anchor="start"))

    # пік
    f.append(circle(x0, ytop, 3.4, fill=POS, stroke=POS))
    f.append(text(x0, ytop - 12, "пік  i(0) = I / (π·h)", size=12, color=POS, bold=True))

    # підписи смуг
    f.append(text(x0, ybase - 12, "±h: 50%", size=11, color=INK, bold=True))
    f.append(text(x0 + 3 * pxh + 10, ybase - 44, "±3h: ≈80%",
                  size=11, color=NEG, bold=True, anchor="start"))
    f.append(text(x0 - 3 * pxh - 10, ytop + 46, "хвіст ~1/d² — спадає повільно",
                  size=10, color=MUTED, anchor="end"))

    render(os.path.join(OUT, "lorentzian.svg"), W, H, *f,
           title="Розподіл густини зворотного струму — лоренціан")


# ── 7. Частота переходу: опір проти реактивности (для math-вставки) ───────────
def fig_regime_crossover():
    W, H = 820, 400
    f = []
    xL, xR, yb = 130, 700, 336
    f.append(line(xL, yb, xR + 14, yb, color=INK, sw=1.5))
    f.append(arrow(xR + 2, yb, xR + 16, yb, color=INK))
    f.append(text(xR + 2, yb + 26, "частота →", size=12, color=MUTED, anchor="end"))
    f.append(line(xL, yb, xL, 72, color=INK, sw=1.5))
    f.append(text(xL - 8, 80, "імпеданс", size=11, color=MUTED, anchor="end"))

    # R — горизонталь
    yR = 236
    f.append(line(xL, yR, xR, yR, color=NEG, sw=2.4))
    f.append(text(xR - 6, yR - 10, "R (опір)", size=12, color=NEG, bold=True, anchor="end"))

    # ωL — росте
    x1, y1, x2, y2 = xL, 322, xR, 96
    f.append(line(x1, y1, x2, y2, color=POS, sw=2.4))
    f.append(text(x2 - 6, y2 - 6, "ωL (реактивність)", size=12, color=POS,
                  bold=True, anchor="end"))

    # перетин
    t = (yR - y1) / float(y2 - y1)
    xf = x1 + t * (x2 - x1)
    f.append(line(xf, yR, xf, yb, color=GOLD, sw=1.3, dash="4,3"))
    f.append(circle(xf, yR, 5.2, fill="#fff3cd", stroke=GOLD, sw=2))
    f.append(text(xf, yb + 26, "f₀ = R / (2π·L)", size=12, color="#8a6d1a", bold=True))

    # зони
    b1, _, _ = textbox(xf - 132, 150,
        ["R > ωL", "зворот розливається", "(найменший опір)"],
        size=11, fill="#eef7f0", stroke=FIELD)
    f.append(b1)
    b2, _, _ = textbox(xf + 176, 122,
        ["ωL > R", "зворот тісниться під доріжку", "(найменша індуктивність)"],
        size=11, fill="#fdecea", stroke=POS)
    f.append(b2)

    render(os.path.join(OUT, "regime-crossover.svg"), W, H, *f,
           title="Частота переходу: опір проти реактивності")


# ── 8. Метод дзеркальних зображень (для math-вставки) ─────────────────────────
def fig_image_current():
    W, H = 780, 430
    f = []
    planeY, x0 = 208, 340
    trY = planeY - 92
    imY = planeY + 12 + 92
    xd = x0 + 168

    # площина
    f.append(rect(90, planeY, 600, 12, fill="#eef0f2", stroke=MUTED, sw=1.3, rx=0))
    f.append(text(96, planeY - 8, "суцільна площина", size=11, color=MUTED, anchor="start"))

    # справжній струм +I
    f.append(circle(x0, trY, 13, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(x0, trY + 5, "+I", size=13, color=POS, bold=True))
    f.append(text(x0, trY - 22, "доріжка", size=11, color=INK))
    f.append(line(x0 - 48, trY, x0 - 48, planeY, color=MUTED, sw=1, dash="3,3"))
    f.append(text(x0 - 56, (trY + planeY) / 2 + 4, "h", size=12, color=INK, anchor="end"))

    # образ −I
    f.append('<circle cx="%.1f" cy="%.1f" r="13" fill="#eef2ff" stroke="%s" '
             'stroke-width="2" stroke-dasharray="4,3"/>' % (x0, imY, NEG))
    f.append(text(x0, imY + 5, "−I", size=13, color=NEG, bold=True))
    f.append(text(x0, imY + 30, "дзеркальний образ", size=11, color=NEG))
    f.append(line(x0 - 48, planeY + 12, x0 - 48, imY, color=MUTED, sw=1, dash="3,3"))
    f.append(text(x0 - 56, (planeY + 12 + imY) / 2 + 4, "h", size=12, color=NEG, anchor="end"))

    # рівні відстані ρ до точки d
    f.append(line(x0, trY, xd, planeY, color=MUTED, sw=1.2, dash="5,4"))
    f.append(line(x0, imY, xd, planeY, color=MUTED, sw=1.2, dash="5,4"))
    f.append(text((x0 + xd) / 2 + 6, trY + 44, "ρ", size=12, color=MUTED, italic=True))

    # точка на відстані d, тангенційне поле
    f.append(circle(xd, planeY, 3.4, fill=INK, stroke=INK))
    f.append(line(x0, planeY - 16, xd, planeY - 16, color=INK, sw=1, dash="4,3"))
    f.append(text((x0 + xd) / 2, planeY - 22, "d", size=12, color=INK))
    f.append(arrow(xd, planeY + 30, xd + 44, planeY + 30, color=FIELD))
    f.append(text(xd + 50, planeY + 34, "B∥", size=12, color=FIELD, bold=True, anchor="start"))

    # формула
    b, _, _ = textbox(x0 + 40, 398, "i(d) = I·h / (π·(d² + h²))",
                      size=13, fill="#fbf7ec", stroke=GOLD, bold=True)
    f.append(b)

    render(os.path.join(OUT, "image-current.svg"), W, H, *f,
           title="Метод дзеркальних зображень для звороту")


if __name__ == "__main__":
    fig_return_current()
    fig_common_impedance()
    fig_slot_detour()
    fig_star_tie()
    fig_agnd_dgnd()
    fig_lorentzian()
    fig_regime_crossover()
    fig_image_current()
    print("ok figs")
