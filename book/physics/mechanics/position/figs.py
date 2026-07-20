# -*- coding: utf-8 -*-
"""Фігури до теми «Положення і радіус-вектор».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

RVEC = FIELD        # радіус-вектор — зелена стрілка (головний об'єкт теми)
PROJ = MUTED        # проєкції — сірий пунктир
ALT  = "#b07a2f"    # другий початок / другий опис — теплий коричнюватий
DR   = POS          # переміщення Δr — червоне


def dot(cx, cy, r=6, col=INK, fill=BG):
    return circle(cx, cy, r, fill=fill, stroke=col, sw=2)


def right_angle(cx, cy, ux, uy, vx, vy, s=13, col=INK):
    """Позначка прямого кута в (cx,cy) між напрямками (ux,uy) і (vx,vy)."""
    ax, ay = cx + ux * s, cy + uy * s
    bx, by = ax + vx * s, ay + vy * s
    dx, dy = cx + vx * s, cy + vy * s
    return ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f" fill="none" '
            'stroke="%s" stroke-width="1.4"/>' % (ax, ay, bx, by, dx, dy, col))


def arc_poly(cx, cy, R, a0, a1, col=INK, sw=1.6, steps=28):
    """Дуга кола (кут у градусах, екранний y — вгору при додатному куті)."""
    pts = []
    for i in range(steps + 1):
        t = math.radians(a0 + (a1 - a0) * i / steps)
        pts.append("%.1f,%.1f" % (cx + R * math.cos(t), cy - R * math.sin(t)))
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>'
            % (" ".join(pts), col, sw))


# ── Фігура 1: радіус-вектор і координати ───────────────────────────────────────
def fig_radius_vector():
    W, H = 760, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Радіус-вектор r і координати точки", size=16, bold=True))

    ox, oy = 155, 388               # початок відліку O
    px, py = 545, 158               # точка P
    fx, fy = px, oy                 # основа перпендикуляра на вісь x
    gx, gy = ox, py                 # основа перпендикуляра на вісь y

    # осі
    f.append(arrow(ox - 40, oy, 720, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy + 26, ox, 78, color=INK, sw=1.8))
    f.append(text(712, oy + 24, "x", size=15, color=INK, italic=True, anchor="end"))
    f.append(text(ox - 16, 86, "y", size=15, color=INK, italic=True, anchor="start"))

    # проєкції (пунктир)
    f.append(line(px, py, fx, fy, color=PROJ, sw=1.5, dash="4,5"))
    f.append(line(px, py, gx, gy, color=PROJ, sw=1.5, dash="4,5"))
    f.append(right_angle(fx, fy, 0, -1, -1, 0, s=12))
    f.append(right_angle(gx, gy, 1, 0, 0, -1, s=12))

    # відрізки-координати на осях (трохи товщі, кольором)
    f.append(line(ox, oy, fx, oy, color=NEG, sw=3))
    f.append(line(ox, oy, ox, gy, color=NEG, sw=3))
    f.append(text((ox + fx) / 2, oy + 30, "x", size=15, color=NEG, bold=True, italic=True))
    f.append(text(ox - 22, (oy + gy) / 2 + 5, "y", size=15, color=NEG, bold=True,
                  italic=True, anchor="end"))

    # радіус-вектор
    f.append(arrow(ox, oy, px, py, color=RVEC, sw=4))
    mx, my = (ox + px) / 2, (oy + py) / 2
    f.append(text(mx - 40, my - 12, "r", size=18, color=RVEC, bold=True, italic=True))
    f.append(text(mx - 40, my + 8, "|r|", size=12.5, color=RVEC, anchor="middle"))

    # точки
    f.append(dot(ox, oy, 6, col=INK))
    f.append(text(ox - 12, oy + 26, "початок O", size=13, bold=True, anchor="end"))
    f.append(dot(px, py, 7, col=RVEC, fill="#eafaf0"))
    f.append(text(px + 14, py - 4, "тіло P", size=13.5, bold=True, anchor="start"))

    b, bw, bh = textbox(W / 2, 452,
                        ["Координати x, y — довжини тіней r на осях;",
                         "|r| = √(x² + y²)  —  відстань від початку до тіла."],
                        size=13, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "radius-vector.svg"), W, H, *f)


# ── Фігура 2: одна точка — дві системи координат ──────────────────────────────
def fig_coordinate_systems():
    W, H = 800, 490
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Одна точка — дві системи координат", size=16, bold=True))

    DXP, DYP = 105, -140            # спільна форма положення для обох панелей

    # ── панель A: прямокутні ──
    oax, oay = 120, 360
    pax, pay = oax + DXP, oay + DYP
    f.append(arrow(oax - 24, oay, 350, oay, color=INK, sw=1.6))
    f.append(arrow(oax, oay + 22, oax, 120, color=INK, sw=1.6))
    f.append(text(344, oay + 22, "x", size=13.5, color=INK, italic=True, anchor="end"))
    f.append(text(oax - 14, 128, "y", size=13.5, color=INK, italic=True, anchor="start"))
    f.append(line(pax, pay, pax, oay, color=PROJ, sw=1.4, dash="4,5"))
    f.append(line(pax, pay, oax, pay, color=PROJ, sw=1.4, dash="4,5"))
    f.append(line(oax, oay, pax, oay, color=NEG, sw=2.6))
    f.append(line(oax, oay, oax, pay, color=NEG, sw=2.6))
    f.append(text((oax + pax) / 2, oay + 26, "x = 3 м", size=12.5, color=NEG, bold=True))
    f.append(text(oax - 12, (oay + pay) / 2 + 4, "y = 4 м", size=12.5, color=NEG,
                  bold=True, anchor="end"))
    f.append(arrow(oax, oay, pax, pay, color=RVEC, sw=3.2))
    f.append(dot(oax, oay, 5, col=INK))
    f.append(dot(pax, pay, 6, col=RVEC, fill="#eafaf0"))
    f.append(text(pax + 12, pay - 4, "P", size=14, bold=True, anchor="start"))
    f.append(text(oax + 100, 410, "прямокутні:  (3 м, 4 м)", size=13, bold=True,
                  anchor="middle"))

    # роздільник
    f.append(line(400, 92, 400, 396, color=PROJ, sw=1.4, dash="3,6"))

    # ── панель B: полярні ──
    obx, oby = 470, 360
    pbx, pby = obx + DXP, oby + DYP
    f.append(arrow(obx - 24, oby, 700, oby, color=INK, sw=1.6))
    f.append(text(694, oby + 22, "вісь відліку", size=12, color=INK, anchor="end"))
    # дуга кута φ
    ang = math.degrees(math.atan2(-DYP, DXP))
    f.append(arc_poly(obx, oby, 52, 0, ang, col=ALT, sw=2))
    f.append(text(obx + 66, oby - 26, "φ = 53°", size=12.5, color=ALT, bold=True,
                  anchor="start"))
    f.append(arrow(obx, oby, pbx, pby, color=RVEC, sw=3.2))
    rmx, rmy = (obx + pbx) / 2, (oby + pby) / 2
    f.append(text(rmx - 34, rmy - 6, "r = 5 м", size=12.5, color=RVEC, bold=True,
                  anchor="end"))
    f.append(dot(obx, oby, 5, col=INK))
    f.append(dot(pbx, pby, 6, col=RVEC, fill="#eafaf0"))
    f.append(text(pbx + 12, pby - 4, "P", size=14, bold=True, anchor="start"))
    f.append(text(obx + 100, 410, "полярні:  (5 м, 53°)", size=13, bold=True,
                  anchor="middle"))

    b, bw, bh = textbox(W / 2, 462,
                        ["Місце те саме — той самий кінчик тієї самої стрілки.",
                         "Різниться лише спосіб назвати його числами."],
                        size=13, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "coordinate-systems.svg"), W, H, *f)


# ── Фігура 3: положення відносне — різні початки ──────────────────────────────
def fig_origin_relative():
    W, H = 820, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Один об'єкт, різні початки — різні координати",
                  size=16, bold=True))

    ox, oy = 150, 384               # початок O
    ox2, oy2 = 356, 300             # початок O′
    px, py = 596, 168               # об'єкт P (нерухомий)

    # зсув між початками (ледь помітний)
    f.append(line(ox, oy, ox2, oy2, color=PROJ, sw=1.5, dash="4,6"))
    f.append(text((ox + ox2) / 2 + 30, (oy + oy2) / 2 + 46, "зсув початку",
                  size=11.5, color=MUTED, anchor="middle"))

    # два радіус-вектори до того самого P
    f.append(arrow(ox, oy, px, py, color=RVEC, sw=3.6))
    f.append(arrow(ox2, oy2, px, py, color=ALT, sw=3.6))

    # підписи стрілок
    f.append(text(286, 244, "r  (від O)", size=13.5, color=RVEC, bold=True,
                  italic=True, anchor="middle"))
    f.append(text(474, 292, "r′  (від O′)", size=13.5, color=ALT, bold=True,
                  italic=True, anchor="middle"))

    # початки і об'єкт
    f.append(dot(ox, oy, 6, col=INK))
    f.append(text(ox - 12, oy + 24, "початок O", size=13, bold=True, anchor="end"))
    f.append(dot(ox2, oy2, 6, col=INK))
    f.append(text(ox2 + 13, oy2 + 22, "початок O′", size=13, bold=True, anchor="start"))
    f.append(dot(px, py, 8, col=INK, fill="#eef2f7"))
    f.append(text(px + 16, py - 2, "об'єкт P", size=14, bold=True, anchor="start"))

    # координатні зчитування
    b1, w1, h1 = textbox(690, 300, ["від O:", "(5, 2)"], size=13.5, pad=10,
                         fill="#eafaf0", stroke=RVEC, sw=1.6, color=RVEC, bold=True)
    f.append(b1)
    b2, w2, h2 = textbox(690, 372, ["від O′:", "(3, 1)"], size=13.5, pad=10,
                         fill="#f7efe2", stroke=ALT, sw=1.6, color=ALT, bold=True)
    f.append(b2)

    b, bw, bh = textbox(W / 2, 444,
                        ["Об'єкт не зрушив, а координати різні: (5, 2) від O, (3, 1) від O′.",
                         "Абсолютного «де» немає — положення завжди відлічене від чогось."],
                        size=12.5, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "origin-relative.svg"), W, H, *f)


# ── Фігура 4: положення в часі — траєкторія ───────────────────────────────────
def fig_trajectory():
    W, H = 820, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Положення в часі: r(t) малює траєкторію",
                  size=16, bold=True))

    ox, oy = 130, 402               # початок O

    # осі-натяк
    f.append(arrow(ox - 20, oy, 780, oy, color=INK, sw=1.4))
    f.append(arrow(ox, oy + 20, ox, 92, color=INK, sw=1.4))
    f.append(text(774, oy + 22, "x", size=13, color=INK, italic=True, anchor="end"))
    f.append(text(ox - 14, 100, "y", size=13, color=INK, italic=True, anchor="start"))

    # траєкторія (плавна крива)
    def C(t):
        x = ox + 90 + 560 * t
        y = oy - 60 - 210 * math.sin(math.pi * (0.15 + 0.72 * t))
        return x, y

    pts, t = [], 0.0
    while t <= 1.0 + 1e-9:
        x, y = C(t)
        pts.append("%.1f,%.1f" % (x, y))
        t += 0.01
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3" '
             'stroke-dasharray="1,0"/>' % (" ".join(pts), MUTED))
    cx, cy = C(0.5)
    f.append(text(cx - 30, cy - 132, "траєкторія", size=13.5, color=MUTED, bold=True,
                  anchor="middle"))

    # дві миті
    p1 = C(0.16)
    p2 = C(0.74)

    # радіус-вектори
    f.append(arrow(ox, oy, p1[0], p1[1], color=RVEC, sw=3.2))
    f.append(arrow(ox, oy, p2[0], p2[1], color=RVEC, sw=3.6))
    f.append(text((ox + p1[0]) / 2 - 6, (oy + p1[1]) / 2 + 24, "r(t₁)", size=13.5,
                  color=RVEC, bold=True, italic=True, anchor="middle"))
    f.append(text((ox + p2[0]) / 2 + 28, (oy + p2[1]) / 2 + 6, "r(t₂)", size=13.5,
                  color=RVEC, bold=True, italic=True, anchor="middle"))

    # переміщення Δr
    f.append(arrow(p1[0], p1[1], p2[0], p2[1], color=DR, sw=3.2))
    f.append(text((p1[0] + p2[0]) / 2 + 6, (p1[1] + p2[1]) / 2 - 14, "Δr",
                  size=15, color=DR, bold=True, italic=True, anchor="middle"))

    # точки-миті
    f.append(dot(ox, oy, 6, col=INK))
    f.append(text(ox - 12, oy + 24, "O", size=13.5, bold=True, anchor="end"))
    f.append(dot(p1[0], p1[1], 6, col=INK, fill="#eef2f7"))
    f.append(text(p1[0] - 12, p1[1] - 10, "t₁", size=13, bold=True, anchor="end"))
    f.append(dot(p2[0], p2[1], 6, col=INK, fill="#eef2f7"))
    f.append(text(p2[0] + 12, p2[1] - 10, "t₂", size=13, bold=True, anchor="start"))

    b, bw, bh = textbox(W / 2, 452,
                        ["Кожній миті — свій радіус-вектор r(t).  Різниця Δr = r(t₂) − r(t₁) — переміщення;",
                         "поділена на час — швидкість. Уся кінематика виростає зі зміни положення."],
                        size=12.5, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "trajectory.svg"), W, H, *f)


# ── Фігура 5 (вставка hist): «широта форм» Орема ──────────────────────────────
def fig_oresme_latitude():
    W, H = 780, 520
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "«Широта форм» Орема — картина, що передвістила координати",
                  size=15.5, bold=True))

    ox, oy = 150, 400               # початок O (лівий нижній кут)
    ax, ay = 650, 115               # верхівка (кінцева «широта»)

    # заливка трикутника (площа = шлях) — під усім
    f.append('<path d="M %.0f %.0f L %.0f %.0f L %.0f %.0f Z" fill="#eafaf0" '
             'stroke="none"/>' % (ox, oy, 650, oy, ax, ay))

    # осі
    f.append(arrow(ox - 40, oy, 705, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy + 20, ox, 102, color=INK, sw=1.8))
    f.append(text(410, 432, "час  →  довгота (longitudo)", size=13, color=INK))
    f.append(text(168, 120, "швидкість", size=13, color=INK, anchor="start"))
    f.append(text(168, 137, "широта (latitudo)", size=12, color=MUTED, anchor="start"))
    f.append(right_angle(ox, oy, 1, 0, 0, -1, s=13))

    # вертикальні «широти» (швидкість у кожну мить) — тонкі бари
    def yhyp(x):
        return oy - (x - ox) / (650 - ox) * (oy - ay)
    x = ox + 25
    while x <= 635:
        f.append(line(x, oy, x, yhyp(x), color=PROJ, sw=1.4))
        x += 46

    # права грань (кінцева швидкість) і гіпотенуза
    f.append(line(650, oy, ax, ay, color=FIELD, sw=2.4))
    f.append(text(660, 250, "v ∝ час", size=12, color=FIELD, bold=True, anchor="start"))
    f.append(line(ox, oy, ax, ay, color=INK, sw=2.6))

    # виділена мить: одна «широта» як координатна пара
    hx = 415
    hy = yhyp(hx)
    f.append(line(hx, oy, hx, hy, color=FIELD, sw=3.4))
    f.append(dot(hx, hy, 6, col=FIELD, fill="#eafaf0"))
    f.append(line(300, 205, hx, hy, color=MUTED, sw=1.2, dash="3,4"))
    f.append(text(268, 160, "у Орема — «широта» якості,", size=12.5, color=INK, anchor="start"))
    f.append(text(268, 178, "у нас — координата (час; швидкість)", size=12.5, color=INK,
                  anchor="start"))

    # площа = шлях (винесено праворуч від грані — усередині трикутника кожен рядок
    # неминуче перетне якийсь із вертикальних барів, бо крок бара 46px < ширини напису)
    f.append(text(662, 300, "площа =", size=13, color=INK, bold=True, anchor="start"))
    f.append(text(662, 318, "пройдений шлях", size=13, color=INK, bold=True, anchor="start"))

    # точки
    f.append(dot(ox, oy, 6, col=INK))
    f.append(text(ox - 12, oy + 24, "початок", size=12.5, bold=True, anchor="end"))

    b, bw, bh = textbox(W / 2, 486,
                        ["Кожній миті — своя вертикальна «широта» (швидкість); їхні верхи лягають у пряму.",
                         "Це ще картина, не рівняння. Але вісь, друга вісь і точка як пара чисел — уже тут."],
                        size=12.5, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "oresme-latitude.svg"), W, H, *f)


# ── Фігура 6 (вставка hist): хроніка народження координат ──────────────────────
def fig_coordinates_timeline():
    W, H = 860, 520
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Народження координат: одна ідея, кілька рук, три століття",
                  size=15.5, bold=True))
    f.append(text(W / 2, 52, "передвісник · незалежна ідея · друк · система · слова",
                  size=12.5, color=MUTED))

    rows = [
        ("≈1350", "ПЕРЕДВІСНИК", MUTED,
         "Орем малює «широту форм» — картину якості, ще без рівнянь"),
        ("1636",  "ІДЕЯ",        FIELD,
         "Ферма: рівняння з двома невідомими — це крива (рукопис)"),
        ("1637",  "ДРУК",        NEG,
         "Декарт друкує La Géométrie — але осі в нього косі, довільні"),
        ("1649",  "СИСТЕМА",     ALT,
         "ван Схотен латиною: звідси й пішли перпендикулярні осі, квадранти"),
        ("1679",  "ДРУК",        FIELD,
         "Ферма виходить посмертно — рукопис пролежав у тіні 43 роки"),
        ("1692",  "СЛОВА",       INK,
         "Ляйбніц усталює «абсцису», «ординату», «координати»"),
    ]

    x_badge = 128
    y0, step = 122, 66
    # хребет-лінія крізь бейджі
    f.append(line(x_badge, y0 - 26, x_badge, y0 + step * (len(rows) - 1) + 26,
                  color=MUTED, sw=1.4, dash="2,5"))

    for i, (year, cat, col, desc) in enumerate(rows):
        y = y0 + i * step
        bw, bh = 108, 46
        f.append(rect(x_badge - bw / 2, y - bh / 2, bw, bh, fill=col, stroke="none",
                      sw=0, rx=8))
        f.append(text(x_badge, y - 3, year, size=16, color="#ffffff", bold=True))
        f.append(text(x_badge, y + 15, cat, size=10.5, color="#ffffff"))
        f.append(text(x_badge + 74, y + 5, desc, size=13.5, color=INK, anchor="start"))

    # зв'язок «ідея → друк» у Ферма (рядки 2 і 5)
    yf1 = y0 + 1 * step
    yf2 = y0 + 4 * step
    f.append(line(x_badge + bw / 2 + 4, yf1, x_badge + bw / 2 + 4, yf2,
                  color=FIELD, sw=2, dash="4,4"))
    f.append(text(x_badge + bw / 2 + 12, (yf1 + yf2) / 2 - 2, "та сама ідея,",
                  size=11, color=FIELD, bold=True, anchor="start"))
    f.append(text(x_badge + bw / 2 + 12, (yf1 + yf2) / 2 + 13, "друк аж через 43 роки",
                  size=11, color=FIELD, bold=True, anchor="start"))

    return render(os.path.join(IMG, "coordinates-timeline.svg"), W, H, *f)


# ── Фігура 7 (вставка proj): повна зміна системи — поворот, тоді трансляція ─────
def fig_frame_transform():
    W, H = 820, 540
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Перехід «тіло → світ»: поворот, тоді трансляція",
                  size=16, bold=True))

    ox, oy = 130, 452               # світовий початок O (куток кімнати)
    SC = 70.0                       # px на одиницю

    def W2S(wx, wy):                # світові координати → екран
        return ox + wx * SC, oy - wy * SC

    th = math.radians(30.0)
    c, s = math.cos(th), math.sin(th)

    # світові осі
    f.append(arrow(ox - 24, oy, 782, oy, color=INK, sw=1.7))
    f.append(arrow(ox, oy + 22, ox, 96, color=INK, sw=1.7))
    f.append(text(774, oy + 24, "x", size=14, color=INK, italic=True, anchor="end"))
    f.append(text(ox - 14, 104, "y", size=14, color=INK, italic=True, anchor="start"))
    f.append(text(ox - 12, oy + 24, "світ O", size=12.5, bold=True, anchor="end"))

    # робот у d = (2, 1)
    dx, dy = W2S(2, 1)
    # тілесна вісь y (короткий стуб для орієнтації); вісь x збігається з вектором до P
    byx, byy = dx - s * 78, dy - c * 78
    f.append(arrow(dx, dy, byx, byy, color=ALT, sw=2.2))
    f.append(text(byx - 6, byy - 4, "тіло y", size=12, color=ALT, italic=True, anchor="end"))

    # перешкода P у світі (4.598, 2.5)
    pwx, pwy = W2S(4.598, 2.5)

    # тілесний радіус-вектор: від робота вздовж носа (тіло x) до P
    f.append(arrow(dx, dy, pwx, pwy, color=ALT, sw=3.4))
    tmx, tmy = (dx + pwx) / 2, (dy + pwy) / 2
    f.append(text(tmx + 4, tmy - 12, "тіло x:  (3, 0)", size=12.5, color=ALT, bold=True,
                  anchor="start"))

    # світовий радіус-вектор: від O до P
    f.append(arrow(ox, oy, pwx, pwy, color=RVEC, sw=3.4))
    wmx, wmy = (ox + pwx) / 2, (oy + pwy) / 2
    f.append(text(wmx - 46, wmy + 22, "світ:  (4.60, 2.50)", size=12.5, color=RVEC,
                  bold=True, anchor="middle"))

    # хибний порядок (3.83, 3.37) — бліда червона мітка
    wrx, wry = W2S(3.83, 3.366)
    f.append(circle(wrx, wry, 6, fill=BG, stroke=POS, sw=2.2))
    f.append(text(wrx + 12, wry - 6, "хибний порядок", size=11.5, color=POS,
                  bold=True, anchor="start"))
    f.append(text(wrx + 12, wry + 9, "(3.83, 3.37)", size=11.5, color=POS, anchor="start"))

    # точки
    f.append(dot(ox, oy, 6, col=INK))
    f.append(dot(dx, dy, 6, col=ALT, fill="#f7efe2"))
    f.append(text(dx + 12, dy + 22, "робот   d = (2, 1),  θ = 30°", size=12.5, bold=True,
                  color=ALT, anchor="start"))
    f.append(dot(pwx, pwy, 7, col=RVEC, fill="#eafaf0"))
    f.append(text(pwx + 12, pwy - 6, "перешкода P", size=13, bold=True, anchor="start"))

    b, bw, bh = textbox(W / 2, 508,
                        ["p_світ = R·p_тіло + d :  спершу поворот у напрямки світу, тоді зсув d.",
                         "Переставиш кроки — точка перескочить на цілі метри (бліда мітка)."],
                        size=12.5, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "frame-transform.svg"), W, H, *f)


# ── Фігура 8 (вставка proj): ENU як місцевий тригранник на глобусі ─────────────
def fig_enu_ecef():
    W, H = 780, 560
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "ECEF → ENU: місцева сітка на глобусі", size=16, bold=True))

    cx, cy, R = 300, 312, 170       # центр Землі = нуль ECEF
    f.append(circle(cx, cy, R, fill="#eef4fa", stroke=MUTED, sw=1.6))

    # осі ECEF з центру
    f.append(arrow(cx, cy, cx, cy - R - 44, color=INK, sw=1.7))   # Z на полюс
    f.append(arrow(cx, cy, cx + R + 60, cy, color=INK, sw=1.7))   # X екватор
    f.append(text(cx + 6, cy - R - 50, "Z (на полюс)", size=12.5, color=INK,
                  italic=True, anchor="start"))
    f.append(text(cx + R + 56, cy + 20, "X (екватор)", size=12.5, color=INK,
                  italic=True, anchor="end"))

    # опорна точка на широті φ0
    phi0 = math.radians(50.0)
    rx = cx + R * math.cos(phi0)
    ry = cy - R * math.sin(phi0)
    f.append(arc_poly(cx, cy, 70, 0, 50, col=MUTED, sw=1.8))
    f.append(text(cx + 90, cy - 30, "φ₀", size=14, color=MUTED, bold=True, italic=True,
                  anchor="start"))
    # ECEF-вектор до опори
    f.append(line(cx, cy, rx, ry, color=NEG, sw=2.0, dash="5,5"))
    f.append(text(243, 262, "ECEF-положення опори",
                  size=11.5, color=NEG, anchor="middle"))

    # місцевий тригранник у опорі
    ux, uy = math.cos(phi0), -math.sin(phi0)          # Up — по нормалі назовні
    nx, ny = -math.sin(phi0), -math.cos(phi0)         # North — до полюса по дотичній
    f.append(arrow(rx, ry, rx + ux * 80, ry + uy * 80, color=FIELD, sw=3.0))   # Up
    f.append(arrow(rx, ry, rx + nx * 72, ry + ny * 72, color=INK, sw=2.6))     # North
    f.append(text(rx + ux * 80 + 6, ry + uy * 80 - 2, "Up", size=13, color=FIELD,
                  bold=True, anchor="start"))
    f.append(text(rx + nx * 72 - 6, ry + ny * 72 - 4, "North", size=12.5, color=INK,
                  bold=True, anchor="end"))
    # East — з площини на нас (⊙)
    ex, ey = rx + 46, ry + 30
    f.append(circle(ex, ey, 9, fill=BG, stroke=POS, sw=2.0))
    f.append(dot(ex, ey, 2.5, col=POS, fill=POS))
    f.append(text(ex + 14, ey + 5, "East (на нас)", size=12, color=POS, anchor="start"))

    # опорна точка й ціль
    f.append(dot(rx, ry, 6, col=INK, fill="#eef2f7"))
    f.append(text(rx + 12, ry + 22, "опора (нуль ENU)", size=12.5, bold=True, anchor="start"))
    txp = rx + nx * 26 + ux * 20
    typ = ry + ny * 26 + uy * 20
    f.append(dot(txp, typ, 5, col=FIELD, fill="#eafaf0"))
    f.append(text(txp - 8, typ - 8, "ціль", size=12, color=FIELD, bold=True, anchor="end"))

    b, bw, bh = textbox(W / 2, 524,
                        ["Спершу віднімаємо ECEF-положення опори (трансляція),",
                         "тоді обертаємо на осі East-North-Up (поворот від φ₀, λ₀)."],
                        size=12.5, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "enu-ecef.svg"), W, H, *f)


if __name__ == "__main__":
    fig_radius_vector()
    fig_coordinate_systems()
    fig_origin_relative()
    fig_trajectory()
    fig_oresme_latitude()
    fig_coordinates_timeline()
    fig_frame_transform()
    fig_enu_ecef()
    print("OK: 8 фігур у", IMG)
