# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

CODE = "#1f47b5"   # кодове слово (синє коло)
CODEFILL = "#eef2fb"
GOLD = "#caa24a"
GOLDFILL = "#faf3e0"
GREEN = "#1f8a3b"
GREENFILL = "#eef7f0"
RED = "#c0271e"
REDFILL = "#fbeceb"
GREY = "#8a8a8a"


def dcircle(cx, cy, r, fill=FILL, stroke=LINE, sw=1.5, dash="6 4"):
    """Коло з пунктирним обведенням (svgkit.circle не має dash)."""
    return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s" '
            'stroke-width="%.1f" stroke-dasharray="%s"/>' % (cx, cy, r, fill, stroke, sw, dash))


def markers():
    """Кольорові наконечники стрілок (render() додає лише #arrow)."""
    out = ["<defs>"]
    for mid, col in (("mInk", INK), ("mRed", RED), ("mGreen", GREEN), ("mBlue", CODE)):
        out.append('<marker id="%s" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
                   'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" '
                   'fill="%s"/></marker>' % (mid, col))
    out.append("</defs>")
    return "".join(out)


def mono(x, y, s, size=13, color=INK, anchor="middle", bold=False):
    """Моноширинний текст (формули/біти)."""
    w = ' font-weight="700"' if bold else ''
    return ('<text x="%.1f" y="%.1f" font-family="Consolas, \'DejaVu Sans Mono\', '
            "'Courier New', monospace\" font-size=\"%d\" fill=\"%s\" text-anchor=\"%s\"%s>%s</text>"
            % (x, y, size, color, anchor, w, esc(s)))


# ── cube: відстань Геммінга як геометрія куба + порозрядний підрахунок ─────────
# Ідея: усі 3-бітні слова — вершини куба, ребро = один біт; відстань = найкоротший
# шлях ребрами; праворуч — як рахувати відстань через різні позиції (XOR).

def fig_cube():
    W, H = 940, 560
    p = []
    p.append(text(W / 2, 32, "Відстань Геммінга — це геометрія: куб усіх слів, ребро = один біт", size=19, bold=True))
    p.append(text(W / 2, 53, "вершини — всі 3-бітні рядки; кожне ребро змінює рівно один біт; відстань = довжина найкоротшого шляху",
                  size=12, color=GREY, italic=True))

    # вершини куба (екранні координати) за мітками
    V = {
        "000": (120, 300), "001": (270, 300), "010": (120, 150), "011": (270, 150),
        "100": (240, 214), "101": (390, 214), "110": (240, 64), "111": (390, 64),
    }
    edges = [("000", "001"), ("000", "010"), ("000", "100"), ("001", "011"),
             ("001", "101"), ("010", "011"), ("010", "110"), ("011", "111"),
             ("100", "101"), ("100", "110"), ("101", "111"), ("110", "111")]
    for a, b in edges:
        (x1, y1), (x2, y2) = V[a], V[b]
        p.append(line(x1, y1, x2, y2, color="#e4e4e4", sw=2.2))

    # червоний шлях 000 → 100 → 110 → 111 (три ребра)
    path = ["000", "100", "110", "111"]
    for a, b in zip(path, path[1:]):
        (x1, y1), (x2, y2) = V[a], V[b]
        p.append(line(x1, y1, x2, y2, color=RED, sw=3.4))

    # вершини
    for lab, (x, y) in V.items():
        code = lab in ("000", "111")
        r = 21 if code else 17
        p.append(circle(x, y, r, fill=CODEFILL if code else BG,
                        stroke=CODE if code else GREY, sw=2.6 if code else 1.6))
        p.append(mono(x, y + 5, lab, size=13 if code else 12, color=CODE if code else INK, bold=True))
    p.append(text(90, 334, "кодове слово", size=11.5, color=CODE, bold=True))
    p.append(text(396, 36, "кодове слово", size=11.5, color=CODE, bold=True))

    p.append(mono(560, 250, "d(000,111) = 3", size=16, color=RED, anchor="start", bold=True))
    p.append(text(560, 272, "(три ребра наскрізь через куб)", size=12, color=RED, anchor="start"))

    # ── права панель: порозрядний підрахунок d(u,v) ──
    bx, by, bw, bh = 560, 300, 350, 232
    p.append(rect(bx, by, bw, bh, fill=GOLDFILL, stroke=GOLD, sw=1.5, rx=12))
    cx = bx + bw / 2
    p.append(text(cx, by + 26, "Відстань Геммінга d(u, v)", size=15, bold=True))
    p.append(text(cx, by + 46, "(Hamming distance)", size=11.5, color=GREY, italic=True))
    p.append(text(bx + 18, by + 74, "= кількість позицій, де u і v різні", size=13, anchor="start", bold=True))

    u = "1011010"
    v = "1001110"
    cols = [597 + i * 30 for i in range(7)]
    yU, yV = by + 114, by + 142
    p.append(mono(bx + 18, yU, "u:", size=12, color=CODE, anchor="end", bold=True))
    p.append(mono(bx + 18, yV, "v:", size=12, color=CODE, anchor="end", bold=True))
    for i, x in enumerate(cols):
        diff = u[i] != v[i]
        if diff:
            p.append(rect(x - 13, yU - 14, 26, 56, fill=REDFILL, stroke=RED, sw=1.4, rx=4))
        p.append(mono(x, yU, u[i], size=14, bold=True))
        p.append(mono(x, yV, v[i], size=14, bold=True))
        if diff:
            p.append(text(x, yV + 30, "↕", size=13, color=RED, bold=True))
    p.append(text(bx + 18, by + 200, "різних позицій: 2  ⇒  d(u, v) = 2", size=13.5, color=RED, anchor="start", bold=True))

    render(os.path.join(OUT, "cube.svg"), W, H, markers(), *p)


# ── spheres: кулі декодування — дві сцени (d=2 і d=3) + формули + таблиця ──────
# Ідея: довкола кодового слова — куля радіуса t; поки кулі не злипаються,
# помилки до t виправні. d=2 лише виявляє, d=3 виправляє один біт.

def fig_spheres():
    W, H = 940, 688
    p = []
    p.append(text(W / 2, 32, "Кулі декодування: скільки помилок видно, а скільки виправно", size=19, bold=True))
    p.append(text(W / 2, 53, "довкола кожного кодового слова — куля радіуса t; поки кулі не злипаються, помилки до t виправні",
                  size=12, color=GREY, italic=True))

    # ── сцена d = 2 (ліворуч): кулі стиснуті в точки, стикаються ──
    p.append(text(250, 172, "d = 2: лише виявлення (1 біт)", size=14, bold=True))
    p.append(line(100, 250, 400, 250, color=INK, sw=2))
    for x in (100, 250, 400):
        p.append(line(x, 244, x, 256, color=GREY, sw=1.4))
    p.append(text(250, 280, "відстань d = 2", size=13.5, bold=True))
    for x, lab in ((100, "A"), (400, "B")):
        p.append(circle(x, 250, 13, fill=CODEFILL, stroke=CODE, sw=2.4))
        p.append(text(x, 254, lab, size=13, color=CODE, bold=True))
    p.append(text(250, 314, "кулі стикаються →", size=11.5, color=RED, bold=True))
    p.append(text(250, 330, "виправити не можна", size=11.5, color=RED, bold=True))

    # ── сцена d = 3 (праворуч): кулі радіуса t=1 не торкаються ──
    p.append(text(680, 172, "d = 3: виявлення 2, виправлення 1", size=14, bold=True))
    p.append(line(530, 250, 830, 250, color=INK, sw=2))
    for x in (530, 630, 730, 830):
        p.append(line(x, 244, x, 256, color=GREY, sw=1.4))
    p.append(text(680, 280, "відстань d = 3", size=13.5, bold=True))
    for x in (530, 830):
        p.append(dcircle(x, 250, 100, fill=GREENFILL, stroke=GREEN, sw=2, dash="6 4"))
    for x, lab in ((530, "A"), (830, "B")):
        p.append(circle(x, 250, 13, fill=CODEFILL, stroke=CODE, sw=2.4))
        p.append(text(x, 254, lab, size=13, color=CODE, bold=True))
    p.append('<line x1="530.0" y1="246.0" x2="630.0" y2="246.0" stroke="%s" stroke-width="1.8" marker-end="url(#mGreen)"/>' % GREEN)
    p.append(mono(580, 238, "t=1", size=11.5, color=GREEN, bold=True))
    p.append(text(680, 314, "кулі не торкаються →", size=11.5, color=GREEN, bold=True))
    p.append(text(680, 330, "1 помилку видно й виправно", size=11.5, color=GREEN, bold=True))

    # ── панель формул ──
    p.append(rect(60, 360, 820, 150, fill=BG, stroke=INK, sw=1.6, rx=12))
    p.append(text(470, 390, "Дві межі через мінімальну відстань d_min", size=16, bold=True))
    p.append(rect(90, 410, 370, 78, fill=GOLDFILL, stroke=GOLD, sw=1.4, rx=10))
    p.append(text(275, 436, "ВИЯВЛЕННЯ (detect)", size=13.5, bold=True))
    p.append(mono(275, 462, "помилок ловимо до:  d_min − 1", size=15, bold=True))
    p.append(text(275, 480, "(будь-яка зміна < d не дотягне до іншого слова)", size=10.5, color=GREY))
    p.append(rect(480, 410, 370, 78, fill=GREENFILL, stroke=GREEN, sw=1.4, rx=10))
    p.append(text(665, 436, "ВИПРАВЛЕННЯ (correct)", size=13.5, bold=True))
    p.append(mono(665, 462, "помилок чинимо до:  t = ⌊(d_min − 1) / 2⌋", size=15, color=GREEN, bold=True))
    p.append(text(665, 480, "(куля радіуса t навколо кожного слова не перетинає сусідню)", size=10.5, color=GREY))

    # ── таблиця для типових d ──
    p.append(text(470, 528, "Як це читати для типових d:", size=13, bold=True))
    heads = [(90, 120, "d_min"), (210, 150, "виявляє"), (360, 170, "виправляє t"), (530, 320, "приклад коду")]
    for x, w, lab in heads:
        p.append(rect(x, 542, w, 26, fill=CODEFILL, stroke=CODE, sw=1.3, rx=5))
        p.append(text(x + w / 2, 560, lab, size=12, bold=True))
    rows = [
        ("1", "0", "0", "без захисту", BG, "#e4e4e4", INK, INK),
        ("2", "1", "0", "біт парності", BG, "#e4e4e4", RED, INK),
        ("3", "2", "1", "код Геммінга (7,4)", GOLDFILL, GOLD, GREEN, INK),
        ("4", "3", "1", "SECDED — виправ один, познач два", BG, "#e4e4e4", GREEN, INK),
    ]
    yy = 568
    for d, det, cor, ex, fill, stroke, corcol, excol in rows:
        p.append(rect(90, yy, 120, 24, fill=fill, stroke=stroke, sw=1.2, rx=4))
        p.append(mono(150, yy + 17, d, size=12, bold=True))
        p.append(rect(210, yy, 150, 24, fill=fill, stroke=stroke, sw=1.2, rx=4))
        p.append(mono(285, yy + 17, det, size=12, bold=True))
        p.append(rect(360, yy, 170, 24, fill=fill, stroke=stroke, sw=1.2, rx=4))
        p.append(mono(445, yy + 17, cor, size=12, color=corcol, bold=True))
        p.append(rect(530, yy, 320, 24, fill=fill, stroke=stroke, sw=1.2, rx=4))
        p.append(text(690, yy + 17, ex, size=12, color=excol))
        yy += 24

    render(os.path.join(OUT, "spheres.svg"), W, H, markers(), *p)


# ── cost: ціна надлишковості — пакування куль у 2ⁿ + таблиця R = k/n ───────────
# Ідея: непересічні кулі мусять уміститися в простір 2ⁿ слів; що більше d_min,
# то більше надлишкових бітів і нижча швидкість коду R = k/n.

def fig_cost():
    W, H = 940, 580
    p = []
    p.append(text(W / 2, 32, "Ціна надлишковості: за більшу відстань платять бітами", size=19, bold=True))
    p.append(text(W / 2, 53, "кулі декодування мусять уміститися в просторі 2ⁿ слів — звідси стеля на d при заданих n і k",
                  size=12, color=GREY, italic=True))

    # ── ліворуч: простір 2ⁿ з непересічними кулями ──
    p.append(rect(70, 90, 380, 300, fill="#fcfcff", stroke=CODE, sw=1.6, rx=12))
    p.append(text(260, 114, "Простір усіх слів: 2ⁿ точок", size=14, bold=True))
    p.append(text(260, 132, "(кожне слово — точка n-куба)", size=11, color=GREY, italic=True))
    centers = [(135, 150), (250, 135), (360, 175), (150, 250), (270, 235),
               (385, 285), (115, 330), (250, 330), (360, 360)]
    for cx, cy in centers:
        p.append(dcircle(cx, cy, 40, fill=GREENFILL, stroke=GREEN, sw=1.6, dash="5 4"))
    for cx, cy in centers:
        p.append(circle(cx, cy, 7, fill=CODEFILL, stroke=CODE, sw=2.2))
    p.append('<line x1="270.0" y1="235.0" x2="306.8" y2="219.8" stroke="%s" stroke-width="1.8" marker-end="url(#mInk)"/>' % GOLD)
    p.append(text(300, 209, "куля радіуса t", size=11.5, color=GOLD, anchor="start", bold=True))
    p.append(text(300, 223, "(виправні слова)", size=10.5, color=GOLD, anchor="start"))
    p.append(text(260, 378, "Кулі не перекриваються — інакше слово впало б у дві відразу", size=11, color=GREEN, bold=True))

    p.append(rect(70, 404, 380, 78, fill=GOLDFILL, stroke=GOLD, sw=1.4, rx=10))
    p.append(text(260, 428, "Межа пакування куль (Геммінгова межа):", size=12.5, bold=True))
    p.append(mono(260, 452, "2ᵏ · V(n, t)  ≤  2ⁿ", size=16, bold=True))
    p.append(text(260, 470, "(число слів × об'єм кулі вміщається в простір)", size=10.5, color=GREY))

    # ── праворуч: таблиця ціни (k = 4) ──
    p.append(text(500, 94, "Ціна за відстань (даних k = 4 біти):", size=14, anchor="start", bold=True))
    heads = [(500, 72, ["d_min"]), (572, 80, ["всього n"]), (652, 86, ["надлишок", "n−k"]),
             (738, 100, ["швидкість", "R = k/n"]), (838, 92, ["виправляє"])]
    for x, w, labs in heads:
        p.append(rect(x, 108, w, 46, fill=CODEFILL, stroke=CODE, sw=1.3, rx=5))
        if len(labs) == 1:
            p.append(text(x + w / 2, 127, labs[0], size=11, bold=True))
        else:
            p.append(text(x + w / 2, 127, labs[0], size=11, bold=True))
            p.append(text(x + w / 2, 142, labs[1], size=11, bold=True))
    rows = [
        ("1", "4", "0", "1.00", "0", BG, "#e4e4e4", RED, INK),
        ("2", "5", "1", "0.80", "0", BG, "#e4e4e4", RED, INK),
        ("3", "7", "3", "0.57", "1", GOLDFILL, GOLD, RED, GREEN),
        ("4", "8", "4", "0.50", "1", BG, "#e4e4e4", RED, GREEN),
    ]
    yy = 154
    geom = [(500, 72), (572, 80), (652, 86), (738, 100), (838, 92)]
    for d, n, red, rate, cor, fill, stroke, ratecol, corcol in rows:
        vals = [(d, INK), (n, INK), (red, INK), (rate, ratecol), (cor, corcol)]
        for (x, w), (val, col) in zip(geom, vals):
            p.append(rect(x, yy, w, 40, fill=fill, stroke=stroke, sw=1.2, rx=4))
            p.append(mono(x + w / 2, yy + 25, val, size=13, color=col, bold=True))
        yy += 40

    # стрілка «більше d → нижча швидкість» уздовж правого краю таблиці
    p.append('<line x1="912.0" y1="162.0" x2="912.0" y2="302.0" stroke="%s" stroke-width="2" marker-end="url(#mRed)"/>' % RED)
    p.append(text(715, 332, "більше d → більше надлишкових біт → нижча швидкість R", size=11.5, color=RED, anchor="middle", bold=True))

    p.append(rect(500, 352, 410, 96, fill=GREENFILL, stroke=GREEN, sw=1.5, rx=10))
    p.append(text(705, 376, "Безкоштовного захисту не буває.", size=13.5, bold=True))
    p.append(text(516, 400, "Кожен крок d угору з'їдає швидкість R: біти", size=11.5, anchor="start"))
    p.append(text(516, 418, "коду йдуть на контроль, а не на корисні дані.", size=11.5, anchor="start"))

    p.append(rect(60, 510, 820, 26, fill=REDFILL, stroke=RED, sw=1.4, rx=8))
    p.append(text(470, 528, "Сінглтонова межа ставить інший бік стелі: d_min ≤ n − k + 1 — більше d вимагає більше надлишку n−k.",
                  size=11.5, bold=True))

    render(os.path.join(OUT, "cost.svg"), W, H, markers(), *p)


if __name__ == "__main__":
    fig_cube()
    fig_spheres()
    fig_cost()
    print("OK: figures written to", OUT)
