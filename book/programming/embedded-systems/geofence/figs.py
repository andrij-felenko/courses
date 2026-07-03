# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Геозона (geofence) в автопілоті».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── Фігура 1: види геозон — циліндр, стеля, полігон-впуск, полігон-заборона ───
# Ідея: геозона задає дозволену область кількома простими формами.
# Циліндр («бляшанка») навколо дому + стеля висоти; полігон-впуск — лишайся
# всередині; полігон-заборона — не заходь у цю пляму (їх можна поєднувати).
def fig_fence_kinds():
    W, H = 960, 430
    P = []
    P.append(text(W / 2, 30, "Види геозон: чим окреслюють дозволену область",
                  size=17, bold=True))

    # ── ліва панель: циліндр навколо дому + стеля висоти (вид збоку) ──
    lx, lw = 60, 360
    top, bot = 80, H - 60
    P.append(text(lx + lw / 2, top - 8, "циліндр навколо дому + стеля висоти",
                  size=12.5, bold=True, color=NEG))
    # земля
    ground_y = bot
    P.append(line(lx, ground_y, lx + lw, ground_y, color=INK, sw=2))
    # стеля висоти
    ceil_y = top + 30
    P.append(line(lx + 20, ceil_y, lx + lw - 20, ceil_y, color=NEG, sw=2, dash="7 5"))
    P.append(text(lx + lw - 20, ceil_y - 6, "стеля (FENCE_ALT_MAX)",
                  size=10.5, color=NEG, anchor="end"))
    # стінки циліндра
    cxl, cxr = lx + 70, lx + lw - 70
    P.append(line(cxl, ceil_y, cxl, ground_y, color=NEG, sw=2, dash="7 5"))
    P.append(line(cxr, ceil_y, cxr, ground_y, color=NEG, sw=2, dash="7 5"))
    # дім
    home_x = (cxl + cxr) / 2
    P.append(circle(home_x, ground_y, 5, fill=FIELD, stroke=FIELD))
    P.append(text(home_x, ground_y + 20, "дім (HOME)", size=10.5, color=FIELD, bold=True))
    # радіус
    P.append(arrow(home_x, ground_y - 22, cxr, ground_y - 22, color=MUTED, sw=1.4))
    P.append(text((home_x + cxr) / 2, ground_y - 28, "радіус", size=10.5, color=MUTED))
    # дрон усередині
    P.append(circle(home_x - 30, ceil_y + 55, 6, fill="#fdecea", stroke=POS, sw=2))
    P.append(text(home_x - 30, ceil_y + 42, "дрон", size=10, color=POS, bold=True))

    # ── права панель: полігон-впуск + полігон-заборона (вид згори) ──
    rx0 = 560
    P.append(text(rx0 + 180, top - 8, "полігони згори: впуск + заборона",
                  size=12.5, bold=True, color=FIELD))
    # полігон-впуск (лишайся всередині) — зелений контур
    poly = [(rx0 + 20, 150), (rx0 + 180, 110), (rx0 + 330, 160),
            (rx0 + 300, 320), (rx0 + 120, 350), (rx0 + 40, 250)]
    pts = " ".join("%.0f,%.0f" % (x, y) for x, y in poly)
    P.append('<polygon points="%s" fill="#e9f7ef" stroke="%s" stroke-width="2.2"/>' % (pts, FIELD))
    P.append(text(rx0 + 175, 135, "лишайся ВСЕРЕДИНІ", size=10.5, color=FIELD, bold=True))
    # полігон-заборона (не заходь) — червона пляма всередині
    ex = [(rx0 + 150, 210), (rx0 + 230, 200), (rx0 + 250, 270), (rx0 + 170, 290)]
    epts = " ".join("%.0f,%.0f" % (x, y) for x, y in ex)
    P.append('<polygon points="%s" fill="#fdecea" stroke="%s" stroke-width="2.2"/>' % (epts, POS))
    P.append(text(rx0 + 200, 248, "не заходь", size=10, color=POS, bold=True))
    # дрон-точка в дозволеному місці
    P.append(circle(rx0 + 90, 230, 6, fill="#eaf0fd", stroke=NEG, sw=2))
    P.append(text(rx0 + 90, 214, "дрон", size=10, color=NEG, bold=True))

    render("img/fence-kinds.svg", W, H, *P)


# ── Фігура 2: запас (margin), порушення межі та реакція ──────────────────────
# Ідея: перевірка — де дрон відносно межі. Смуга запасу дає РАННЄ попередження
# ще до порушення; перетин самої межі — це breach → failsafe-дія (RTL/посадка).
def fig_margin_breach():
    W, H = 1000, 470
    P = []
    P.append(text(W / 2, 30, "Запас, порушення межі та реакція автопілота",
                  size=17, bold=True))

    cx, cy = 300, 260
    R = 150            # межа геозони
    Rm = 112           # внутрішня смуга запасу
    # зовнішнє поле (за межею) — небезпека
    P.append(circle(cx, cy, R + 34, fill="#fdecea", stroke="none"))
    # дозволена область
    P.append(circle(cx, cy, R, fill="#ffffff", stroke=FIELD, sw=2.4))
    P.append(text(cx, cy - R - 12, "МЕЖА геозони", size=12, color=FIELD, bold=True))
    # смуга запасу
    P.append(circle(cx, cy, Rm, fill="none", stroke="#b08900", sw=1.8, ))
    # dash на смузі запасу через окреме коло
    P.append('<circle cx="%.0f" cy="%.0f" r="%.0f" fill="none" stroke="#b08900" '
             'stroke-width="1.8" stroke-dasharray="6 5"/>' % (cx, cy, Rm))
    P.append(text(cx, cy + 6, "смуга ЗАПАСУ", size=11, color="#b08900", bold=True))
    P.append(text(cx, cy + 22, "(FENCE_MARGIN)", size=10, color="#b08900"))
    P.append(text(cx, cy - R - 30, "за межею — порушення (breach)", size=10.5,
                  color=POS, bold=True, anchor="middle"))

    # три положення дрона: у нормі / у запасі (попередження) / за межею (breach)
    import math
    def dot(ang, r, col, fillc, lbl, lbl2=None):
        x = cx + r * math.cos(ang)
        y = cy + r * math.sin(ang)
        P.append(circle(x, y, 7, fill=fillc, stroke=col, sw=2.2))
        P.append(text(x, y - 14, lbl, size=10, color=col, bold=True))
        if lbl2:
            P.append(text(x, y + 20, lbl2, size=9.5, color=col))
        return x, y
    dot(math.radians(158), Rm - 42, FIELD, "#e9f7ef", "норма")                 # глибоко всередині
    dot(math.radians(-58), (Rm + R) / 2, "#b08900", "#fdf6e3", "у запасі", "попередження")
    dot(math.radians(38), R + 24, POS, "#fdecea", "ЗА МЕЖЕЮ", "breach!")

    # права колонка: сходинки реакції
    bx = 590
    P.append(text(bx + 195, 80, "реакція за близькістю до межі", size=12.5, bold=True))
    rows = [
        ("глибоко всередині", "нормальний політ", FIELD, "#e9f7ef"),
        ("увійшов у смугу запасу", "попередити оператора", "#b08900", "#fdf6e3"),
        ("перетнув межу (breach)", "failsafe: RTL / посадка", POS, "#fdecea"),
    ]
    y = 135
    for cond, act, col, fill in rows:
        fr, w, h = textbox(bx + 95, y, cond, size=11, bold=True, color=col,
                           fill=fill, stroke=col, min_w=180)
        P.append(fr)
        P.append(arrow(bx + 190, y, bx + 232, y, color=MUTED))
        fr, w, h = textbox(bx + 312, y, act, size=11, bold=True, color=col,
                           fill=fill, stroke=col, min_w=165)
        P.append(fr)
        y += 82

    render("img/margin-breach.svg", W, H, *P)


# ── Фігура 3: метод променя (ray casting) — парність перетинів ────────────────
# Ідея: пускаємо з точки промінь праворуч і рахуємо перетини межі багатокутника.
# Непарно = всередині, парно = зовні. Показуємо дві точки: внутрішню (1 перетин)
# і зовнішню (2 перетини крізь виступ).
def fig_ray_casting():
    W, H = 900, 470
    P = []
    P.append(text(W / 2, 30, "Метод променя: парність перетинів межі",
                  size=17, bold=True))

    # неопуклий багатокутник із виступом праворуч (щоб зовнішній промінь дав 2)
    poly = [(150, 110), (470, 90), (470, 220), (620, 260),
            (470, 300), (480, 410), (170, 400), (120, 250)]
    pts = " ".join("%.0f,%.0f" % (x, y) for x, y in poly)
    P.append('<polygon points="%s" fill="#e9f7ef" stroke="%s" stroke-width="2.4"/>'
             % (pts, FIELD))
    P.append(text(300, 78, "багатокутник (дозволена зона)", size=11.5,
                  color=FIELD, bold=True))

    import math

    def crossings_right(px, py):
        """Точки перетину горизонталі y=py, x>=px зі сторонами полігона."""
        xs = []
        n = len(poly)
        j = n - 1
        for i in range(n):
            xi, yi = poly[i]
            xj, yj = poly[j]
            if (yi > py) != (yj > py):
                xc = xi + (py - yi) * (xj - xi) / (yj - yi)
                if px < xc:
                    xs.append(xc)
            j = i
        return sorted(xs)

    # промінь із точки: лінія праворуч + позначки перетинів + підпис парності
    def ray(px, py, col, fillc, label):
        xs = crossings_right(px, py)
        xend = W - 40
        P.append(circle(px, py, 6.5, fill=fillc, stroke=col, sw=2.4))
        # сам промінь (пунктир до краю)
        P.append('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="%s" '
                 'stroke-width="1.8" stroke-dasharray="6 5" marker-end="url(#arrow)"/>'
                 % (px, py, xend, py, col))
        # точки перетину — маленькі гарячі кружки
        for xc in xs:
            P.append(circle(xc, py, 4.5, fill=BG, stroke=POS, sw=2.2))
        parity = "непарно → ВСЕРЕДИНІ" if len(xs) % 2 else "парно → ЗЗОВНІ"
        P.append(text(px, py - 14, label, size=10.5, color=col, bold=True))
        P.append(text(xend, py - 8, "%d перетин(и) — %s" % (len(xs), parity),
                      size=10.5, color=col, bold=True, anchor="end"))

    ray(250, 190, NEG, "#eaf0fd", "точка A (в зоні)")     # внутрішня → 1 перетин
    ray(60, 330, POS, "#fdecea", "точка B (поза)")         # зовнішня → 2 перетини

    # легенда перетину
    P.append(circle(160, 445, 4.5, fill=BG, stroke=POS, sw=2.2))
    P.append(text(172, 449, "— перетин променя зі стороною межі",
                  size=10.5, color=MUTED, anchor="start"))

    render("img/ray-casting.svg", W, H, *P)


if __name__ == "__main__":
    fig_fence_kinds()
    fig_margin_breach()
    fig_ray_casting()
    print("OK: 3 figures -> img/")
