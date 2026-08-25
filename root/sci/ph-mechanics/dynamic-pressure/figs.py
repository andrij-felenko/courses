# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: точка гальмування й трубка Пито ────────────────────────────────
def fig_stagnation():
    W, H = 760, 430
    body = []
    cy = 210

    # набігаючий потік (стрілки зліва)
    for k, off in enumerate((-70, -35, 0, 35, 70)):
        y = cy + off
        body.append(arrow(70, y, 250, y, color=NEG, sw=2.0))
    body.append(text(150, cy - 96, "потік, швидкість v", size=14, color=NEG, bold=True))

    # тіло трубки Пито: горизонтальний циліндр, гирло дивиться ліворуч (у потік)
    tube_x0, tube_x1 = 300, 620
    tube_y0, tube_y1 = cy - 16, cy + 16
    body.append(rect(tube_x0, tube_y0, tube_x1 - tube_x0, tube_y1 - tube_y0,
                     fill="#eef2f7", stroke=LINE, sw=1.8, rx=8))
    # гирло (передній отвір) — точка гальмування
    body.append(circle(tube_x0, cy, 6, fill=POS, stroke=POS))
    body.append(text(tube_x0 - 6, cy - 40, "точка гальмування", size=12.5, color=POS, bold=True, anchor="middle"))
    body.append(text(tube_x0 - 6, cy - 24, "v = 0", size=12, color=POS))

    # бічний (статичний) отвір зверху
    sx = 470
    body.append(circle(sx, tube_y0, 5, fill=BG, stroke=INK, sw=1.8))

    # виносна лінія: повний тиск (від гирла вниз до підпису)
    body.append(line(tube_x0, cy + 40, tube_x0, cy + 84, color=POS, sw=1.2, dash="4 3"))
    body.append(text(tube_x0, cy + 100, "повний тиск", size=12.5, color=POS, bold=True))
    body.append(text(tube_x0, cy + 116, "p + q", size=12.5, color=POS))

    # виносна лінія: статичний тиск (від бічного отвору вгору)
    body.append(line(sx, tube_y0, sx, 96, color=INK, sw=1.2, dash="4 3"))
    body.append(text(sx, 84, "статичний тиск p", size=12.5, color=INK, bold=True))
    body.append(text(sx, 68, "(бічний отвір)", size=11.5, color=MUTED))

    # підсумкова рамка: різниця = динамічний тиск
    box = fitbox(W / 2 - 205, 356, 410, 48,
                 "різниця показів:  (p + q) − p  =  q  =  ½ ρ v²",
                 size=15, bold=True, fill="#fdecea", stroke=POS)
    body.append(box)

    render(os.path.join(OUT, "stagnation.svg"), W, H, *body,
           title="Динамічний тиск як надбавка гальмування (трубка Пито)")


# ── Фігура 2: труба Вентурі — обмін тисків, а сума стала ──────────────────────
def fig_venturi():
    W, H = 780, 470
    body = []

    # ── труба, що звужується (силует) ──
    px0, px1 = 150, 610
    pcx = (px0 + px1) / 2          # центр горла
    pcy = 120                       # вісь труби
    span = (px1 - px0) / 2

    def half_h(x):
        t = abs(x - pcx) / span     # 0 у горлі, 1 на краях
        return 18 + 28 * t * t      # 18 у горлі, 46 на краях

    top_pts, bot_pts = [], []
    n = 48
    for i in range(n + 1):
        x = px0 + (px1 - px0) * i / n
        h = half_h(x)
        top_pts.append((x, pcy - h))
        bot_pts.append((x, pcy + h))
    d = "M%.1f %.1f " % top_pts[0]
    d += " ".join("L%.1f %.1f" % p for p in top_pts[1:])
    d += " " + " ".join("L%.1f %.1f" % p for p in reversed(bot_pts))
    d += " Z"
    body.append('<path d="%s" fill="%s" stroke="%s" stroke-width="1.8"/>' % (d, "#eef2f7", LINE))

    # стрілка потоку крізь трубу
    body.append(arrow(px0 + 24, pcy, px1 - 24, pcy, color=NEG, sw=2.4))
    body.append(text(px0 + 4, pcy - 60, "широкий переріз", size=12.5, color=MUTED, anchor="start"))
    body.append(text(px0 + 4, pcy - 44, "повільно", size=12, color=MUTED, anchor="start"))
    body.append(text(pcx, pcy - 40, "горло", size=12.5, color=POS, bold=True))
    body.append(text(pcx, pcy - 25, "швидко", size=12, color=POS))
    body.append(text(pcx, pcy + 60, "A · v = const", size=12.5, color=INK))

    # ── два стовпчики балансу тисків ──
    base = 430                      # спільна лінія «підлоги»
    unit = 2.0                      # px на одиницю тиску
    total = 100                     # повний тиск (стала Бернуллі)
    top_y = base - total * unit     # спільна вершина
    bw = 96

    def stacked(cx, p_stat, p_dyn, label):
        out = []
        hs, hd = p_stat * unit, p_dyn * unit
        x = cx - bw / 2
        # статичний (низ, синій)
        out.append(rect(x, base - hs, bw, hs, fill="#dbe4fb", stroke=NEG, sw=1.6, rx=3))
        out.append(text(cx, base - hs / 2 + 4, "p", size=14, color=NEG, bold=True))
        # динамічний (верх, червоний)
        out.append(rect(x, base - hs - hd, bw, hd, fill="#fbdcd7", stroke=POS, sw=1.6, rx=3))
        out.append(text(cx, base - hs - hd / 2 + 4, "½ρv²", size=12.5, color=POS, bold=True))
        # підпис перерізу
        out.append(text(cx, base + 22, label, size=12.5, color=INK, bold=True))
        return out

    cxL, cxR = 250, 520
    body += stacked(cxL, 82, 18, "широкий переріз")
    body += stacked(cxR, 40, 60, "горло")

    # зелена лінія повного тиску — та сама висота над обома стовпчиками
    body.append(line(cxL - bw / 2 - 26, top_y, cxR + bw / 2 + 26, top_y,
                     color=FIELD, sw=2.6))
    body.append(text(W / 2, top_y - 12,
                     "стала Бернуллі = p + ½ρv²  —  та сама скрізь",
                     size=13, color=FIELD, bold=True))

    # підпис-висновок під стовпчиками
    body.append(text(W / 2, base + 44,
                     "у горлі: p падає, ½ρv² росте, а сума не міняється",
                     size=12.5, color=MUTED))

    render(os.path.join(OUT, "venturi.svg"), W, H, *body,
           title="Труба Вентурі: тиск і рух міняються, сума стала")


# ── Фігура 3: динамічний тиск росте як квадрат швидкості ──────────────────────
def fig_q_vs_v():
    W, H = 660, 440
    ox, oy = 88, 360            # початок осей
    axl, ayl = 500, 280         # довжини осей
    rho = 1.225
    vmax = 45.0
    qmax = 0.5 * rho * vmax * vmax    # ≈ 1240 Па

    body = []
    body.append(line(ox, oy, ox + axl, oy, color=INK, sw=1.8))   # X
    body.append(line(ox, oy, ox, oy - ayl, color=INK, sw=1.8))   # Y
    body.append(text(ox + axl - 4, oy + 30, "швидкість v, м/с", size=13, anchor="end"))
    body.append(text(ox - 54, oy - ayl + 6, "q, Па", size=13, bold=True, anchor="start"))

    def X(v):
        return ox + v / vmax * axl

    def Y(q):
        return oy - q / qmax * ayl

    # риски осі X
    for v in (10, 20, 30, 40):
        body.append(line(X(v), oy, X(v), oy + 6, color=INK, sw=1.4))
        body.append(text(X(v), oy + 22, str(v), size=12))

    # крива q = ½ρv²
    pts = []
    for i in range(0, 91):
        v = vmax * i / 90.0
        pts.append("%.1f,%.1f" % (X(v), Y(0.5 * rho * v * v)))
    body.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                % (" ".join(pts), FIELD))

    # характерні точки з підписами
    def mark(v, txt, dx, dy):
        q = 0.5 * rho * v * v
        body.append(line(X(v), oy, X(v), Y(q), color=MUTED, sw=1.0, dash="4 3"))
        body.append(line(ox, Y(q), X(v), Y(q), color=MUTED, sw=1.0, dash="4 3"))
        body.append(circle(X(v), Y(q), 5, fill=POS, stroke=POS))
        body.append(text(X(v) + dx, Y(q) + dy, txt, size=12.5, color=INK, bold=True, anchor="start"))

    mark(10, "10 м/с → 61 Па", 8, 26)
    mark(20, "20 м/с → 245 Па", 8, 20)
    mark(40, "40 м/с → 980 Па", -160, -10)

    # виноска про подвоєння
    body.append(fitbox(ox + 40, oy - ayl - 4, 250, 34,
                       "×2 швидкість  →  ×4 тиск",
                       size=13, bold=True, fill="#fdecea", stroke=POS))

    render(os.path.join(OUT, "q-vs-v.svg"), W, H, *body,
           title="Динамічний тиск ½ρv² проти швидкості (повітря)")


# ── Фігура 4: часова вісь суперечки за першість ──────────────────────────────
def fig_timeline():
    W, H = 840, 450
    ax = 250                         # рівень осі часу
    x0, x1 = 72, 800
    y0, y1 = 1730, 1760

    def X(yr):
        return x0 + (yr - y0) / (y1 - y0) * (x1 - x0 - 8)

    body = []
    # вісь часу (стрілка праворуч) + риски років
    body.append(arrow(x0, ax, x1, ax, color=INK, sw=1.8))
    body.append(text(x1, ax - 10, "рік", size=12, color=MUTED, anchor="end"))
    for yr in range(1730, 1761, 5):
        body.append(line(X(yr), ax - 4, X(yr), ax + 4, color=INK, sw=1.3))
        body.append(text(X(yr), ax + 22, str(yr), size=11, color=MUTED))

    # ── справжні книжки (над віссю) ──
    # 1738 «Гідродинаміка» — Данило
    body.append(circle(X(1738), ax, 6, fill=FIELD, stroke=FIELD))
    body.append(line(X(1738), ax, X(1738), 126, color=FIELD, sw=1.4))
    body.append(fitbox(X(1738) - 96, 62, 192, 64,
                       "1738 — «Гідродинаміка»\nДанило Бернуллі\nзвідси й термін",
                       size=13, fill="#eaf6ec", stroke=FIELD, bold=True))
    # 1755–57 рівняння руху — Ойлер
    body.append(circle(X(1755), ax, 6, fill=FIELD, stroke=FIELD))
    body.append(line(X(1755), ax, X(1755), 126, color=FIELD, sw=1.4))
    body.append(fitbox(X(1755) - 112, 62, 224, 64,
                       "1755–57 — рівняння руху\nЛеонард Ойлер\nсучасна форма рівняння",
                       size=13, fill="#eaf6ec", stroke=FIELD, bold=True))
    # 1743 «Гідравліка» надрукована — Йоганн (нижчий ряд над віссю)
    body.append(circle(X(1743), ax, 6, fill=POS, stroke=POS))
    body.append(line(X(1743), ax, X(1743), 214, color=POS, sw=1.4))
    body.append(fitbox(X(1743) - 105, 160, 210, 52,
                       "1743 — «Гідравліка»\nЙоганн Бернуллі (друк)",
                       size=13, fill="#fdecea", stroke=POS, bold=True))

    # ── підробка (під віссю) ──
    # привид-мітка «1732»
    body.append(circle(X(1732), ax, 7, fill=BG, stroke=POS, sw=2))
    body.append(fitbox(X(1732) - 94, 306, 188, 74,
                       "«датовано 1732»\nнасправді — 1743\n(задня дата)",
                       size=12.5, fill="#fdecea", stroke=POS, bold=True))
    # штрихова стрілка: реальна 1743 → фальшива дата 1732
    body.append('<path d="M%.1f 260 Q%.1f 332 %.1f 262" fill="none" '
                'stroke="%s" stroke-width="1.8" stroke-dasharray="6 4" '
                'marker-end="url(#arrow)"/>'
                % (X(1743), (X(1743) + X(1732)) / 2, X(1732) + 11, POS))

    render(os.path.join(OUT, "bernoulli-timeline.svg"), W, H, *body,
           title="Суперечка за першість: що вийшло коли (і що датовано заднім числом)")


# ── Вставка math-bernoulli-derivation ─────────────────────────────────────────

# Фігура A: рівнодійна на скибку рідини вздовж цівки (виведення Ойлера F = ma)
def fig_bernoulli_element():
    W, H = 900, 500
    body = []
    cx, cy = 430, 250
    th = math.radians(20)
    sx, sy = math.cos(th), -math.sin(th)     # напрям течії s (екран: вгору = -y)
    nx, ny = math.sin(th), math.cos(th)      # нормаль до s
    L, w = 190, 46
    hl = L / 2
    Bc = (cx - hl * sx, cy - hl * sy)        # центр задньої грані
    Fc = (cx + hl * sx, cy + hl * sy)        # центр передньої грані

    def pt(c, sgn):
        return (c[0] + sgn * w * nx, c[1] + sgn * w * ny)

    bt, bb = pt(Bc, -1), pt(Bc, +1)
    ft, fb = pt(Fc, -1), pt(Fc, +1)

    # лінія течії крізь елемент
    body.append('<path d="M70,405 Q430,250 845,150" fill="none" stroke="%s" '
                'stroke-width="2" marker-end="url(#arrow)"/>' % MUTED)
    body.append(text(792, 132, "лінія течії (цівка)", size=13, color=MUTED, anchor="middle"))

    # сам елемент
    d = "M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f Z" % (
        bt[0], bt[1], ft[0], ft[1], fb[0], fb[1], bb[0], bb[1])
    body.append('<path d="%s" fill="#eef2f7" stroke="%s" stroke-width="2"/>' % (d, LINE))
    # підпис маси — над верхньою гранню, поза тілом елемента
    mt = ((bt[0] + ft[0]) / 2, (bt[1] + ft[1]) / 2)
    body.append(text(mt[0] - 34 * nx, mt[1] - 34 * ny, "маса = ρ·A·ds",
                     size=13, color=INK, bold=True, anchor="middle"))

    # тиск на задню грань: штовхає вперед (+s), сила p·A
    p1 = (Bc[0] - 84 * sx, Bc[1] - 84 * sy)
    p2 = (Bc[0] - 12 * sx, Bc[1] - 12 * sy)
    body.append(arrow(p1[0], p1[1], p2[0], p2[1], color=NEG, sw=2.6))
    body.append(text(p1[0] - 4, p1[1] + 26, "p·A", size=14, color=NEG, bold=True, anchor="middle"))

    # тиск на передню грань: штовхає назад (−s), сила (p+dp)·A (більша)
    q1 = (Fc[0] + 96 * sx, Fc[1] + 96 * sy)
    q2 = (Fc[0] + 12 * sx, Fc[1] + 12 * sy)
    body.append(arrow(q1[0], q1[1], q2[0], q2[1], color=POS, sw=2.6))
    body.append(text(q1[0] + 40, q1[1] - 12, "(p+dp)·A", size=14, color=POS, bold=True, anchor="middle"))

    # вага вниз
    gx = cx + 66
    body.append(arrow(gx, cy + 44, gx, cy + 126, color=INK, sw=2.2))
    body.append(text(gx + 92, cy + 96, "вага = ρg·A·ds", size=13, color=INK, anchor="middle"))

    # dz — підйом за висотою між гранями
    dzx = 700
    body.append(line(Fc[0], Fc[1], dzx, Fc[1], color=MUTED, sw=1.0, dash="4 3"))
    body.append(line(Bc[0], Bc[1], dzx, Bc[1], color=MUTED, sw=1.0, dash="4 3"))
    body.append(line(dzx, Fc[1], dzx, Bc[1], color=FIELD, sw=2.2))
    body.append(text(dzx + 22, (Fc[1] + Bc[1]) / 2 + 5, "dz", size=14, color=FIELD, bold=True, anchor="middle"))

    # кут θ до горизонталі біля задньої грані
    body.append(line(Bc[0], Bc[1], Bc[0] + 78, Bc[1], color=MUTED, sw=1.0, dash="3 3"))
    body.append(text(Bc[0] + 52, Bc[1] - 9, "θ", size=13, color=MUTED, anchor="middle"))

    # прискорення a уздовж +s (над елементом, у вільній зоні)
    a1 = (545, 178)
    a2 = (a1[0] + 66 * sx, a1[1] + 66 * sy)
    body.append(arrow(a1[0], a1[1], a2[0], a2[1], color=FIELD, sw=2.6))
    body.append(text(a2[0] + 20, a2[1] + 2, "a", size=15, color=FIELD, bold=True, anchor="middle"))

    # формула F = ma
    body.append(fitbox(W / 2 - 335, 432, 670, 48,
                       "рівнодійна вздовж s:   p·A − (p+dp)·A − ρg·A·dz = (ρ·A·ds)·a",
                       size=15, bold=True, fill="#eef7f0", stroke=FIELD))

    render(os.path.join(OUT, "bernoulli-element.svg"), W, H, *body,
           title="Рівняння Ойлера: F = ma на скибці рідини вздовж цівки")


# Фігура B: стисливість — ½ρv² лише перший доданок гальмівного тиску
def fig_bernoulli_compressibility():
    W, H = 780, 480
    ox, oy = 104, 388
    axl, ayl = 566, 306
    body = []

    body.append(line(ox, oy, ox + axl, oy, color=INK, sw=1.8))
    body.append(line(ox, oy, ox, oy - ayl, color=INK, sw=1.8))
    body.append(text(ox + axl - 4, oy + 34, "число Маха  M = v / a", size=13, anchor="end"))
    body.append(text(ox - 30, oy - ayl - 14, "(p₀ − p) ÷ ½ρv²", size=13, bold=True, anchor="start"))

    Mmax = 0.8
    ymin, ymax = 1.0, 1.20

    def X(M):
        return ox + M / Mmax * axl

    def Y(r):
        return oy - (r - ymin) / (ymax - ymin) * ayl

    for M in (0.2, 0.4, 0.6, 0.8):
        body.append(line(X(M), oy, X(M), oy + 6, color=INK, sw=1.4))
        body.append(text(X(M), oy + 24, "%.1f" % M, size=12))
    for r in (1.00, 1.05, 1.10, 1.15, 1.20):
        body.append(line(ox, Y(r), ox - 6, Y(r), color=INK, sw=1.4))
        body.append(text(ox - 12, Y(r) + 4, "%.2f" % r, size=11, anchor="end"))

    # нестислива опорна лінія (=1.0)
    body.append(line(ox, Y(1.0), ox + axl, Y(1.0), color=NEG, sw=2.4))
    body.append(text(ox + axl - 6, Y(1.0) - 11, "нестислива  ½ρv²  (= 1)",
                     size=12.5, color=NEG, bold=True, anchor="end"))

    def ratio(M):
        if M < 1e-4:
            return 1.0
        return ((1 + 0.2 * M * M) ** 3.5 - 1) / (0.7 * M * M)

    pts = []
    i = 0
    while i <= 160:
        M = Mmax * i / 160.0
        pts.append("%.1f,%.1f" % (X(M), Y(min(ratio(M), ymax))))
        i += 1
    body.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
                % (" ".join(pts), FIELD))
    body.append(text(X(0.75), Y(ratio(0.75)) - 16, "стислива (точна)",
                     size=12.5, color=FIELD, bold=True, anchor="middle"))

    # межа M = 0.3 — callout у вільній зоні вгорі-ліворуч + тонкий поводок
    r03 = ratio(0.3)
    body.append(line(X(0.3), oy, X(0.3), Y(r03), color=POS, sw=1.4, dash="5 3"))
    body.append(circle(X(0.3), Y(r03), 5, fill=POS, stroke=POS))
    bx, by, bwid, bht = 128, 150, 250, 52
    body.append(line(bx + bwid, by + bht, X(0.3), Y(r03) - 6, color=POS, sw=1.0, dash="4 3"))
    body.append(fitbox(bx, by, bwid, bht,
                       "M = 0.3:  ½ρv² занижує\nгальмівний тиск на ≈ 2.3 %",
                       size=12.5, bold=True, fill="#fdecea", stroke=POS))

    # виноска M = 0.6
    r06 = ratio(0.6)
    body.append(circle(X(0.6), Y(r06), 4, fill=POS, stroke=POS))
    body.append(text(X(0.6) + 30, Y(r06) + 10, "≈ +9 %", size=12, color=POS, bold=True, anchor="start"))

    render(os.path.join(OUT, "bernoulli-compressibility.svg"), W, H, *body,
           title="Стисливість: ½ρv² — лише перший доданок гальмівного тиску")


# Фігура C: стала Бернуллі — уздовж цівки завжди, на все поле лише без вихору
def fig_bernoulli_streamline():
    W, H = 880, 400
    body = []
    midx = W / 2
    body.append(line(midx, 62, midx, H - 26, color=MUTED, sw=1.2, dash="6 4"))

    ys = [122, 188, 254]

    # ліва панель: загальна (вихрова) течія
    body.append(text(225, 50, "загальна течія (з вихором)", size=14, bold=True))
    left = [(NEG, "C₁"), (INK, "C₂"), (POS, "C₃")]
    for (col, lab), y in zip(left, ys):
        body.append('<path d="M74,%d Q225,%d 398,%d" fill="none" stroke="%s" '
                    'stroke-width="2.4" marker-end="url(#arrow)"/>' % (y, y - 30, y - 8, col))
        body.append(text(62, y + 4, lab, size=14, color=col, bold=True, anchor="end"))
    body.append(text(225, 306, "ω = ∇×v ≠ 0", size=13, color=MUTED, anchor="middle"))
    body.append(text(225, 336, "стала своя на кожній цівці:", size=13, anchor="middle"))
    body.append(text(225, 358, "C₁ ≠ C₂ ≠ C₃", size=14, bold=True, anchor="middle"))

    # права панель: безвихрова течія
    body.append(text(655, 50, "безвихрова течія", size=14, bold=True))
    for y in ys:
        body.append('<path d="M502,%d Q655,%d 828,%d" fill="none" stroke="%s" '
                    'stroke-width="2.4" marker-end="url(#arrow)"/>' % (y, y - 30, y - 8, FIELD))
        body.append(text(490, y + 4, "C", size=14, color=FIELD, bold=True, anchor="end"))
    body.append(text(655, 306, "ω = ∇×v = 0", size=13, color=FIELD, anchor="middle"))
    body.append(text(655, 336, "одна стала на все поле:", size=13, anchor="middle"))
    body.append(text(655, 358, "C однакова скрізь", size=14, bold=True, anchor="middle"))

    render(os.path.join(OUT, "bernoulli-streamline.svg"), W, H, *body,
           title="Стала Бернуллі: уздовж цівки завжди, на все поле — лише без вихору")


# ── Вставка proj-pitot-airspeed ───────────────────────────────────────────────

# Фігура P1: корінь роздуває похибку швидкості на малих швидкостях
def fig_pitot_lowspeed_noise():
    W, H = 720, 470
    ox, oy = 96, 388            # початок осей
    axl, ayl = 540, 300
    rho = 1.225
    dpn = 2.0                   # шум давача, Па
    vmin_plot = 1.6
    vmax = 40.0
    ytop = 1.2                  # верх осі δv, м/с

    body = []

    def X(v):
        return ox + v / vmax * axl

    def Y(dv):
        return oy - dv / ytop * ayl

    # заштрихована зона нечутливості v < 5 м/с
    vdb = 5.0
    xdb = X(vdb)
    body.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fdecea" opacity="0.7"/>'
                % (ox, oy - ayl, xdb - ox, ayl))
    body.append(text((ox + xdb) / 2, oy - ayl + 168, "зона", size=12.5, color=POS, bold=True))
    body.append(text((ox + xdb) / 2, oy - ayl + 186, "нечутливості", size=11.5, color=POS))

    # осі
    body.append(line(ox, oy, ox + axl, oy, color=INK, sw=1.8))
    body.append(line(ox, oy, ox, oy - ayl, color=INK, sw=1.8))
    body.append(text(ox + axl - 4, oy + 30, "швидкість v, м/с", size=13, anchor="end"))
    body.append(text(ox - 66, oy - ayl + 4, "δv, м/с", size=13, bold=True, anchor="start"))

    # риски осей
    for v in (10, 20, 30, 40):
        body.append(line(X(v), oy, X(v), oy + 6, color=INK, sw=1.4))
        body.append(text(X(v), oy + 22, str(v), size=12))
    for dv in (0.25, 0.5, 0.75, 1.0):
        body.append(line(ox - 6, Y(dv), ox, Y(dv), color=INK, sw=1.4))
        body.append(text(ox - 12, Y(dv) + 4, "%.2f" % dv, size=11, anchor="end"))

    # крива δv = δp/(ρ·v)
    pts = []
    n = 180
    for k in range(n + 1):
        v = vmin_plot + (vmax - vmin_plot) * k / n
        pts.append("%.1f,%.1f" % (X(v), Y(dpn / (rho * v))))
    body.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                % (" ".join(pts), FIELD))

    # характерні точки
    def mark(v, txt, dx, dy):
        dv = dpn / (rho * v)
        body.append(circle(X(v), Y(dv), 5, fill=POS, stroke=POS))
        body.append(text(X(v) + dx, Y(dv) + dy, txt, size=12.5, color=INK, bold=True, anchor="start"))

    mark(3, "3 м/с → δv ≈ 0.54 м/с", 14, -6)
    mark(10, "10 → 0.16", 10, -8)
    mark(30, "30 → 0.05", 8, -8)

    # підпис-виноска у вільному верхньому правому куті
    body.append(fitbox(X(17), oy - ayl + 6, 300, 46,
                       "той самий шум ±2 Па:\nбіля нуля — велика δv, на швидкості — мала",
                       size=12, fill=FILL, stroke=MUTED))

    render(os.path.join(OUT, "lowspeed-noise.svg"), W, H, *body,
           title="Корінь роздуває похибку: δv = δp/(ρv)")


# Фігура P2: конвеєр обробки Δp у надійну швидкість
def fig_pitot_pipeline():
    W, H = 860, 660
    body = []
    cx = 250
    bw = 268
    bx = cx - bw / 2            # 116

    def pbox(y, s, h=46, fill=FILL, stroke=LINE, color=INK, size=13.5):
        body.append(fitbox(bx, y, bw, h, s, size=size, bold=True,
                           fill=fill, stroke=stroke, color=color))

    def sarrow(y0, y1, label):
        body.append(arrow(cx, y0, cx, y1, color=INK, sw=1.9))
        body.append(text(cx + 22, (y0 + y1) / 2 + 4, label, size=12, color=MUTED, anchor="start"))

    pbox(56, "Δp сирий — давач диференційного тиску")
    sarrow(102, 134, "− нуль-зсув (знятий на землі)")
    pbox(134, "Δp без зсуву")
    sarrow(180, 212, "ФНЧ на ЗНАКОВОМУ Δp — до відсікання")
    pbox(212, "Δp згладжений")
    sarrow(258, 290, "зона нечутливості: Δp < q_min")
    pbox(290, "Δp робочий")

    # бічний вхід густини
    body.append(fitbox(470, 296, 366, 46, "ρ = p /(R·T)   —   баро (p) + OAT (T)",
                       size=13, bold=True, fill="#eef7f0", stroke=FIELD, color=FIELD))
    body.append(arrow(468, 318, bx + bw + 4, 311, color=FIELD, sw=1.8))

    # ділення на дві швидкості
    body.append(text(cx + 22, 356, "v = √(2·Δp / ρ)", size=12.5, color=MUTED, anchor="start"))
    yout = 388
    body.append(arrow(cx, 336, cx - 104, yout, color=INK, sw=1.8))
    body.append(arrow(cx, 336, cx + 104, yout, color=INK, sw=1.8))
    body.append(fitbox(cx - 104 - 96, yout, 192, 54, "EAS — приладова\nρ₀ = 1.225",
                       size=13, bold=True, fill="#eaf0fd", stroke=NEG, color=NEG))
    body.append(fitbox(cx + 104 - 96, yout, 192, 54, "TAS — справжня\nреальна ρ",
                       size=13, bold=True, fill="#fdecea", stroke=POS, color=POS))

    # стислива поправка під TAS
    body.append(arrow(cx + 104, yout + 54, cx + 104, yout + 54 + 30, color=POS, sw=1.8))
    body.append(text(cx + 104 + 18, yout + 54 + 20, "M·a — стислива поправка",
                     size=12, color=MUTED, anchor="start"))
    body.append(fitbox(cx + 104 - 96, yout + 84, 192, 46, "TAS на великих\nдозвукових",
                       size=12.5, bold=True, fill="#fdecea", stroke=POS, color=POS))

    render(os.path.join(OUT, "pitot-pipeline.svg"), W, H, *body,
           title="Від сирого Δp до надійної швидкості")


if __name__ == "__main__":
    fig_stagnation()
    fig_venturi()
    fig_q_vs_v()
    fig_timeline()
    fig_bernoulli_element()
    fig_bernoulli_compressibility()
    fig_bernoulli_streamline()
    fig_pitot_lowspeed_noise()
    fig_pitot_pipeline()
    print("figs done")
