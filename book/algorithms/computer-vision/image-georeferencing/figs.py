# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

RAY    = "#94a3b8"      # промінь погляду
GROUND = "#8b5e3c"      # рельєф
FLAT   = "#6b7280"      # плоска модель


# ── 1. Промінь крізь піксель і дві різні відповіді на землі ───────────────────
def fig_ray_to_ground():
    W, H = 900, 490
    p = []
    C = (150.0, 130.0)          # оптичний центр
    k = 0.6                     # нахил променя (dy/dx)

    yg = 395.0                  # плоска модель землі
    x_dem, y_dem = 520.0, 352.0                 # влучання в рельєф
    x_flat = C[0] + (yg - C[1]) / k             # влучання в площину

    # рельєф — ламана, що проходить рівно через точку влучання
    terr = [(90, 395), (200, 391), (300, 393), (400, 383), (470, 362),
            (x_dem, y_dem), (560, 357), (620, 371), (700, 388), (790, 393), (860, 395)]

    # плоска модель
    p.append(line(90, yg, 860, yg, color=FLAT, sw=1.6, dash="7,5"))
    # рельєф
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
             % (" ".join("%.0f,%.0f" % q for q in terr), GROUND))

    # висота над поверхнею
    p.append(line(C[0], C[1], C[0], yg, color=MUTED, sw=1.2, dash="4,4"))

    # промінь: суцільний до першого влучання, далі — пунктир «під землею»
    p.append(line(C[0], C[1], x_dem, y_dem, color=NEG, sw=2.2))
    p.append(line(x_dem, y_dem, x_flat, yg, color=NEG, sw=1.6, dash="5,4"))

    # площина знімка — короткий відрізок упоперек променя
    L = math.hypot(450.0, 270.0)
    ux, uy = 450.0 / L, 270.0 / L
    mx, my = C[0] + 75 * ux, C[1] + 75 * uy
    p.append(line(mx + 19 * (-uy), my + 19 * ux, mx - 19 * (-uy), my - 19 * ux,
                  color=MUTED, sw=3))
    p.append(circle(mx, my, 4.5, fill=POS, stroke=BG, sw=1.2))
    p.append(circle(C[0], C[1], 6, fill=INK, stroke=BG, sw=1.5))

    # точки перетину
    p.append(circle(x_dem, y_dem, 6.5, fill=FIELD, stroke=INK, sw=1.4))
    p.append(circle(x_flat, yg, 6.5, fill=POS, stroke=INK, sw=1.4))

    # мірка розбіжності
    p.append(line(x_dem, y_dem, x_dem, 415, color=MUTED, sw=1, dash="3,3"))
    p.append(line(x_flat, yg, x_flat, 415, color=MUTED, sw=1, dash="3,3"))
    p.append(arrow(x_dem, 415, x_flat, 415, color=MUTED, sw=1.4))
    p.append(arrow(x_flat, 415, x_dem, 415, color=MUTED, sw=1.4))

    # написи
    p.append(text(150, 112, "оптичний центр", size=12, color=INK))
    p.append(text(252, 140, "піксель (u, v)", size=12, color=POS, anchor="start"))
    p.append(text(230, 300, "промінь погляду", size=13, color=NEG, anchor="start", bold=True))
    p.append(mtext(162, 262, ["h — висота", "над поверхнею"], size=12, color=MUTED, anchor="start"))
    p.append(text(430, 340, "рельєф", size=12, color=GROUND, anchor="end"))
    p.append(text(545, 330, "влучання в рельєф", size=12, color=FIELD, anchor="start", bold=True))
    p.append(text(95, 420, "плоска модель землі", size=12, color=FLAT, anchor="start"))
    p.append(text(620, 425, "влучання в площину", size=12, color=POS, anchor="start", bold=True))
    p.append(text(500, 440, "розбіжність", size=12, color=MUTED, anchor="end"))

    render(os.path.join(OUT, "ray-to-ground.svg"), W, H, *p,
           title="Піксель задає лише напрямок — координату дає поверхня")


# ── 2. Ланцюг систем координат: від пікселя до широти й довготи ───────────────
def fig_frames_chain():
    W, H = 960, 360
    p = []
    bw, bh = 220, 56
    yA, yB = 110, 262

    def box(cx, cy, s, **kw):
        return fitbox(cx - bw / 2, cy - bh / 2, bw, bh, s, size=13, **kw)

    p.append(box(140, yA, "Піксель (u, v)"))
    p.append(box(460, yA, "Напрямок\nу системі камери"))
    p.append(box(800, yA, "Напрямок\nу системі корпуса"))
    p.append(box(800, yB, "Напрямок\nу місцевому NED"))
    p.append(box(330, yB, "Точка на землі:\nφ, λ, висота", fill="#eaf7ef", stroke=FIELD))

    p.append(arrow(250, yA, 350, yA, color=NEG))
    p.append(arrow(570, yA, 690, yA, color=NEG))
    p.append(arrow(800, yA + bh / 2, 800, yB - bh / 2, color=NEG))
    p.append(arrow(690, yB, 440, yB, color=FIELD, sw=2.2))

    p.append(text(300, 48, "K⁻¹, дисторсія", size=12, color=INK))
    p.append(text(630, 48, "R_bc — підвіс і вивірка", size=12, color=INK))
    p.append(mtext(785, 176, ["R_nb — орієнтація корпуса", "(крен, тангаж, курс)"],
                   size=12, color=INK, anchor="end"))
    p.append(mtext(565, 312, ["перетин променя з поверхнею;",
                              "початок координат — від GNSS"], size=12, color=INK))

    render(os.path.join(OUT, "frames-chain.svg"), W, H, *p,
           title="Ланцюг перетворень: чотири повороти й один перетин")


# ── 3. Чутливість до кута: та сама похибка кута коштує різного ────────────────
def fig_angle_sensitivity():
    W, H = 820, 470
    p = []
    x0, y0 = 110.0, 380.0        # початок осей
    xr, yt = 760.0, 80.0
    h_cam, dg = 120.0, math.radians(1.0)

    def X(g):   return x0 + g * (xr - x0) / 90.0
    def Y(d):   return y0 - d * (y0 - yt) / 80.0
    def dD(g):  return h_cam * dg / math.sin(math.radians(g)) ** 2

    # осі
    p.append(arrow(x0, y0, xr + 18, y0, color=INK, sw=1.6))
    p.append(arrow(x0, y0, x0, yt - 14, color=INK, sw=1.6))

    for g in (10, 20, 30, 45, 60, 90):
        p.append(line(X(g), y0, X(g), y0 + 6, color=INK, sw=1.4))
        p.append(text(X(g), y0 + 22, str(g), size=12, color=INK))
    for d in (0, 20, 40, 60, 80):
        p.append(line(x0 - 6, Y(d), x0, Y(d), color=INK, sw=1.4))
        p.append(text(x0 - 12, Y(d) + 4, str(d), size=12, color=INK, anchor="end"))

    # крива
    pts, g = [], 9.56
    while g <= 90.0001:
        pts.append((X(g), Y(dD(g))))
        g += 0.4
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join("%.1f,%.1f" % q for q in pts), POS))

    for g, lab, tx, ty, anc in ((10, "70 м", 205, 118, "start"),
                                (20, "18 м", 275, 300, "start"),
                                (30, "8 м", 327, 332, "middle"),
                                (45, "4 м", 435, 348, "middle"),
                                (90, "2 м", 752, 352, "end")):
        p.append(circle(X(g), Y(dD(g)), 5, fill=POS, stroke=BG, sw=1.4))
        p.append(text(tx, ty, lab, size=12, color=POS, bold=True, anchor=anc))

    p.append(fitbox(300, 104, 400, 50,
                    "δD = h · δγ / sin²γ      (h = 120 м, δγ = 1°)",
                    size=13, fill=FILL, stroke=INK, sw=1.1))
    p.append(text(110, 62, "зсув точки на землі, м", size=12, color=MUTED, anchor="start"))
    p.append(text(435, 430, "кут між променем і землею γ, градуси", size=12, color=MUTED))

    render(os.path.join(OUT, "angle-sensitivity.svg"), W, H, *p,
           title="Ціна одного градуса: похибка на землі проти кута зйомки")


# ── 4. Два джерела пози: аеротріангуляція проти прямої геоприв'язки ──────────
def fig_pose_sources():
    W, H = 960, 470
    p = []

    LX, RX, CW = 55, 505, 400          # ліва й права колонки, ширина
    Lc, Rc = LX + CW / 2, RX + CW / 2

    p.append(fitbox(LX, 26, CW, 42, "Класична аеротріангуляція",
                    size=15, bold=True, fill="#eef2f7", stroke=INK, sw=1.4))
    p.append(fitbox(RX, 26, CW, 42, "Пряма геоприв'язка",
                    size=15, bold=True, fill="#eef7ef", stroke=INK, sw=1.4))

    left = ["знімки з перекриттям",
            "опорні точки, поміряні на землі",
            "зрівнювання блоку рівнянь"]
    right = ["GNSS: де була камера",
             "інерціальний блок: як повернута",
             "вивірка й спільний годинник"]
    for i, (a, b) in enumerate(zip(left, right)):
        y = 92 + i * 58
        p.append(fitbox(LX + 20, y, CW - 40, 44, a, size=13, sw=1.2))
        p.append(fitbox(RX + 20, y, CW - 40, 44, b, size=13, sw=1.2))

    p.append(arrow(Lc, 264, 400, 306, color=INK, sw=2.0))
    p.append(arrow(Rc, 264, 560, 306, color=INK, sw=2.0))
    p.append(text(LX + 6, 296, "позу ВИВОДЯТЬ із зображення",
                  size=12, color=MUTED, anchor="start"))
    p.append(text(RX + CW - 6, 296, "позу МІРЯЮТЬ давачами",
                  size=12, color=MUTED, anchor="end"))

    p.append(fitbox(300, 318, 360, 48, "поза камери: шість чисел",
                    size=15, bold=True, fill="#fdf3ec", stroke=POS, sw=1.6))
    p.append(arrow(480, 366, 480, 396, color=INK, sw=2.0))
    p.append(fitbox(210, 400, 540, 46,
                    "промінь крізь піксель → перетин із поверхнею → координата",
                    size=13, sw=1.2))

    render(os.path.join(OUT, "pose-sources.svg"), W, H, *p,
           title="Що змінилося: не обчислення, а джерело пози камери")


# ── Як розв'язувач шукає перетин: марш кроком і половинне ділення ────────────
def fig_march_and_bisect():
    W, H = 900, 420
    p = []
    C = (100.0, 90.0)
    k = 0.32571                                  # нахил променя на полотні

    def ray(x):  return C[1] + (x - C[0]) * k

    terr_x = [100, 180, 260, 340, 420, 500, 580, 660, 740, 820, 870]
    terr_y = [341, 337, 331, 323, 314, 305, 297, 289, 281, 275, 272]

    def terr(x):
        for i in range(len(terr_x) - 1):
            if terr_x[i] <= x <= terr_x[i + 1]:
                a = (x - terr_x[i]) / (terr_x[i + 1] - terr_x[i])
                return terr_y[i] + a * (terr_y[i + 1] - terr_y[i])
        return terr_y[-1]

    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
             % (" ".join("%d,%d" % q for q in zip(terr_x, terr_y)), GROUND))
    p.append(line(C[0], C[1], 870, ray(870), color=NEG, sw=2.2))
    p.append(circle(C[0], C[1], 6, fill=INK, stroke=BG, sw=1.5))

    # проби вздовж променя: поки промінь вище рельєфу — «+», перша «−» замикає вилку
    for x in (260, 340, 420, 500, 580, 660):
        p.append(plus(x, ray(x), r=8))
    p.append(minus(740, ray(740), r=8))

    # що саме порівнюють на кожній пробі
    for x in (660, 740):
        p.append(line(x, ray(x) + 11, x, terr(x) - 5, color=MUTED, sw=1.1, dash="3,3"))

    # знайдений перетин
    xh = (C[1] - C[0] * k - 289.0 - 66.0) / (-0.1 - k)
    p.append(circle(xh, ray(xh), 6.5, fill=FIELD, stroke=INK, sw=1.5))

    # вилка — рівно один крок маршу
    p.append(line(660, 356, 740, 356, color=POS, sw=2))
    p.append(line(660, 350, 660, 362, color=POS, sw=2))
    p.append(line(740, 350, 740, 362, color=POS, sw=2))

    p.append(fitbox(596, 50, 292, 58,
                    "«+» — промінь ще вище рельєфу\n«−» — уже нижче: знак змінився",
                    size=12, fill=FILL, stroke=MUTED, sw=1.1))
    p.append(text(100, 70, "оптичний центр", size=12, color=INK))
    p.append(text(250, 172, "промінь погляду", size=13, color=NEG, anchor="start", bold=True))
    p.append(text(130, 380, "рельєф із сітки висот", size=12, color=GROUND, anchor="start"))
    p.append(text(700, 384, "вилка — один крок маршу", size=12, color=POS))
    p.append(text(716, 254, "перший перетин", size=12, color=FIELD, anchor="start", bold=True))

    render(os.path.join(OUT, "march-and-bisect.svg"), W, H, *p,
           title="Пошук перетину: крокуємо, ловимо зміну знака, ділимо навпіл")


# ── Звідки два множники 1/sin γ у похибці вздовж дальності ──────────────────
def fig_two_levers():
    W, H = 900, 470
    p = []
    C = (150.0, 96.0)
    yg = 392.0
    g1 = math.radians(40.0)          # кут променя до землі
    g2 = math.radians(33.0)          # той самий промінь, нахилений на δ

    def hit(g):
        t = (yg - C[1]) / math.sin(g)
        return (C[0] + t * math.cos(g), yg), t

    G, t1 = hit(g1)
    G2, _ = hit(g2)

    # земля й висота
    p.append(line(80, yg, 850, yg, color=GROUND, sw=2.2))
    p.append(line(C[0], C[1], C[0], yg, color=MUTED, sw=1.2, dash="4,4"))
    p.append(text(C[0] - 12, (C[1] + yg) / 2, "h", size=15, color=MUTED,
                  anchor="end", bold=True, italic=True))

    # два промені
    p.append(line(C[0], C[1], G[0], G[1], color=NEG, sw=2.4))
    p.append(line(C[0], C[1], G2[0], G2[1], color=POS, sw=2.0, dash="6,4"))
    p.append(circle(C[0], C[1], 6, fill=INK, stroke=BG, sw=1.5))
    p.append(circle(G[0], G[1], 6, fill=NEG, stroke=BG, sw=1.5))
    p.append(circle(G2[0], G2[1], 6, fill=POS, stroke=BG, sw=1.5))

    # основа перпендикуляра з G на нахилений промінь
    ux, uy = math.cos(g2), math.sin(g2)
    s = (G[0] - C[0]) * ux + (G[1] - C[1]) * uy
    F = (C[0] + s * ux, C[1] + s * uy)
    p.append(line(G[0], G[1], F[0], F[1], color=FIELD, sw=2.6))
    p.append(line(G[0], G[1], G2[0], G2[1], color=POS, sw=3.0))

    p.append(text(320, 214, "t = h / sin γ", size=14, color=NEG, bold=True, anchor="start"))
    p.append(text(560, 300, "t · δ", size=14, color=FIELD, bold=True, anchor="end"))
    p.append(text(700, 428, "t · δ / sin γ", size=14, color=POS, bold=True))
    p.append(text(G[0] + 46, yg - 12, "γ", size=15, bold=True, italic=True))
    p.append(text(C[0] + 92, C[1] + 20, "δ", size=15, color=POS, bold=True, italic=True))

    p.append(fitbox(430, 56, 440, 96,
                    "важіль: нахил на δ зсуває точку впоперек променя на t·δ\n"
                    "проєкція: цей зсув лягає на землю розтягнутим у 1/sin γ\n"
                    "разом  δD = h · δ / sin²γ",
                    size=13, fill=FILL, stroke=INK, sw=1.2))
    p.append(text(462, 452, "упоперек дальності другого множника немає: там зсув просто t·δ",
                  size=12, color=MUTED))

    render(os.path.join(OUT, "two-levers.svg"), W, H, *p,
           title="Два множники 1/sin γ: важіль дальності й косий погляд")


# ── Еліпс похибки на землі для двох кутів зйомки ─────────────────────────────
def fig_error_ellipse():
    W, H = 900, 500
    p = []
    S = 13.0                                     # пікселів на метр
    cases = ((230.0, "γ = 60°", 3.540, 1.927, 3.181, "1.9 · σ орієнт. + 2.2 · GNSS + 8.3 · рельєф"),
             (652.0, "γ = 30°", 9.736, 2.576, 7.128, "17.5 · σ орієнт. + 2.2 · GNSS + 75.0 · рельєф"))
    cy = 268.0

    for cx, lab, sr, sc, cep, share in cases:
        rx, ry, rc = sr * S, sc * S, cep * S
        p.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
                 'stroke-width="1.6" stroke-dasharray="6,5"/>' % (cx, cy, rc, MUTED))
        p.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="#dbe6fb" '
                 'fill-opacity="0.75" stroke="%s" stroke-width="2.2"/>' % (cx, cy, rx, ry, NEG))
        p.append(circle(cx, cy, 4.5, fill=POS, stroke=BG, sw=1.2))
        p.append(text(cx, cy - rc - 14, lab, size=16, bold=True))
        p.append(text(cx, cy + ry + 22, "σ вздовж = %.2f м" % sr, size=12, color=NEG, bold=True))
        p.append(text(cx, cy + rc + 22, "CEP = %.2f м" % cep, size=12, color=MUTED, bold=True))
        p.append(text(cx - rx - 10, cy - 4, "σ упоперек", size=11, color=NEG, anchor="end"))
        p.append(text(cx - rx - 10, cy + 12, "%.2f м" % sc, size=11, color=NEG, anchor="end"))
        p.append(text(cx, 452, "дисперсія м²:  " + share, size=12, color=INK))

    p.append(arrow(80, 60, 190, 60, color=INK, sw=1.8))
    p.append(text(196, 64, "напрямок дальності (від надира в бік цілі)",
                  size=12, color=INK, anchor="start"))

    p.append(line(700, 484, 700 + 10 * S, 484, color=INK, sw=2.2))
    p.append(line(700, 478, 700, 490, color=INK, sw=2.2))
    p.append(line(700 + 10 * S, 478, 700 + 10 * S, 490, color=INK, sw=2.2))
    p.append(text(700 + 5 * S, 474, "10 м", size=12, color=INK))

    render(os.path.join(OUT, "error-ellipse.svg"), W, H, *p,
           title="Еліпс похибки на землі: h = 120 м, σ кутів 0.5°, GNSS 1.5 м, рельєф 5 м")


if __name__ == "__main__":
    fig_ray_to_ground()
    fig_frames_chain()
    fig_angle_sensitivity()
    fig_pose_sources()
    fig_march_and_bisect()
    fig_two_levers()
    fig_error_ellipse()
    print("ok")
