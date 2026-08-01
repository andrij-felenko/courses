# -*- coding: utf-8 -*-
"""Фігури до статті «Закон Гука» (book/physics/mechanics/hookes-law)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def polyline(pts, color=INK, sw=2.5, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" '
            'stroke-width="%.1f"%s stroke-linecap="round" stroke-linejoin="round"/>'
            % (p, color, sw, d))


# ── Фігура 1: сила проти видовження — прямий закон і його межа ───────────────
def fig_force_extension():
    W, H = 720, 470
    O = (100, 388)          # початок координат (0,0)
    xax_end = (668, 388)
    yax_top = (100, 78)

    # лінійна ділянка O -> E (границя пружності)
    E = (372, 150)
    slope = (E[1] - O[1]) / (E[0] - O[0])   # px/px, від'ємний (вгору)

    def liny(x):
        return O[1] + slope * (x - O[0])

    # пластична ділянка: за E крива згинається і виположується
    plastic = []
    for i in range(0, 61):
        x = E[0] + (632 - E[0]) * i / 60.0
        y = E[1] - 46 * (1 - math.exp(-(x - E[0]) / 68.0))
        plastic.append((x, y))

    frags = []
    # осі
    frags.append(arrow(O[0], O[1], xax_end[0], xax_end[1]))
    frags.append(arrow(O[0], O[1], yax_top[0], yax_top[1]))
    frags.append(text(636, 414, "видовження  x", size=15, anchor="middle", color=INK))
    frags.append(text(110, 70, "сила  F", size=15, anchor="start", color=INK))
    frags.append(text(O[0] - 12, O[1] + 6, "0", size=13, anchor="end", color=MUTED))

    # вертикаль-роздільник на границі пружності
    frags.append(line(E[0], E[1], E[0], O[1], color=MUTED, sw=1.2, dash="5 5"))

    # трикутник нахилу (k = ΔF/Δx)
    ax1, ax2 = 168, 288
    ry1, ry2 = liny(ax1), liny(ax2)
    frags.append(line(ax1, ry1, ax2, ry1, color=NEG, sw=1.4, dash="4 4"))
    frags.append(line(ax2, ry1, ax2, ry2, color=NEG, sw=1.4, dash="4 4"))
    frags.append(text((ax1 + ax2) / 2, ry1 + 20, "Δx", size=14, color=NEG))
    frags.append(text(ax2 + 18, (ry1 + ry2) / 2 + 5, "ΔF", size=14, color=NEG, anchor="start"))
    frags.append(text(150, 150, "нахил  k = ΔF ⁄ Δx", size=15, color=INK, anchor="start", bold=True))

    # лінійна (пружна) ділянка
    frags.append(line(O[0], O[1], E[0], E[1], color=INK, sw=3))
    # пластична ділянка
    frags.append(polyline(plastic, color=POS, sw=3))

    # точка границі пружності + підпис (з відступом, винесений угору-праворуч)
    frags.append(circle(E[0], E[1], 5, fill=BG, stroke=INK, sw=2))
    frags.append(line(E[0] + 6, E[1] - 4, 452, 112, color=MUTED, sw=1.1))
    frags.append(text(458, 108, "границя", size=14, color=INK, anchor="start", bold=True))
    frags.append(text(458, 126, "пружності", size=14, color=INK, anchor="start", bold=True))

    # підписи ділянок під віссю
    frags.append(text((O[0] + E[0]) / 2, 438, "пружна: F = k·x", size=14, color=INK))
    frags.append(text(515, 438, "пластична", size=14, color=POS))

    render(os.path.join(IMG, "force-extension.svg"), W, H, *frags)


# ── Фігура 2: дно будь-якої долини енергії — парабола ────────────────────────
def fig_energy_valley():
    W, H = 720, 470
    # межі рисувальної області (в пікселях)
    px0, px1 = 96, 664
    py0, py1 = 96, 372        # py1 — базова лінія V=0
    De, alpha = 1.0, 1.25
    rL, rR = -0.95, 2.35      # діапазон зміщення від рівноваги (r0=0)

    def morse(u):
        return De * (1 - math.exp(-alpha * u)) ** 2

    def para(u):
        return De * alpha * alpha * u * u    # ½k u² з k = 2·De·α²

    Vmax = 1.55
    def X(u): return px0 + (u - rL) / (rR - rL) * (px1 - px0)
    def Y(v): return py1 - (v / Vmax) * (py1 - py0)

    real = [(X(rL + (rR - rL) * i / 240.0), Y(morse(rL + (rR - rL) * i / 240.0)))
            for i in range(0, 241)]
    # парабола — лише поки лишається в межах поля
    par = []
    for i in range(0, 241):
        u = rL + (rR - rL) * i / 240.0
        v = para(u)
        if v <= Vmax:
            par.append((X(u), Y(v)))

    xmin, ymin = X(0.0), Y(0.0)

    frags = []
    # осі
    frags.append(arrow(px0 - 6, py1, px1 + 4, py1))
    frags.append(arrow(px0, py1 + 6, px0, py0 - 18))
    frags.append(text(px1 - 4, py1 + 26, "зміщення  x", size=15, anchor="end"))
    frags.append(text(px0 + 10, py0 - 22, "енергія  V", size=15, anchor="start"))

    # справжня яма і парабола
    frags.append(polyline(par, color=POS, sw=2.4, dash="7 5"))
    frags.append(polyline(real, color=INK, sw=3))

    # позначки кривих (винесені, не на лініях)
    frags.append(text(px1 - 6, Y(morse(1.75)) - 14, "справжня яма  V(x)", size=14,
                      color=INK, anchor="end"))
    frags.append(text(X(0.62) + 96, Y(para(0.62)) - 6, "парабола  ½k·x²", size=14,
                      color=POS, anchor="start"))
    frags.append(line(X(0.62) + 4, Y(para(0.62)), X(0.62) + 92, Y(para(0.62)) - 8,
                      color=POS, sw=1.0))

    # точка рівноваги
    frags.append(circle(xmin, ymin, 5, fill=BG, stroke=INK, sw=2))
    frags.append(text(xmin, ymin + 26, "стійка рівновага", size=14, color=FIELD, bold=True))

    # відновлювальна сила = мінус нахил: стрілки назад до мінімуму
    def slope_arrow(u, length, side):
        h = 1e-3
        dvdx_px = (Y(morse(u + h)) - Y(morse(u - h)))  # напрям дотичної в px
        # сила спрямована «під гору вниз до мінімуму» — горизонтально до центру
        y = Y(morse(u)) - 26
        x = X(u)
        frags.append(circle(x, Y(morse(u)), 3.5, fill=NEG, stroke=NEG, sw=1))
        if side < 0:
            frags.append(arrow(x + 6, y, x + 6 + length, y, color=NEG, sw=2.2))
        else:
            frags.append(arrow(x - 6, y, x - 6 - length, y, color=NEG, sw=2.2))
    slope_arrow(-0.62, 46, -1)   # ліва стінка -> штовхає праворуч (до центру)
    slope_arrow(0.95, 46, +1)    # права стінка -> штовхає ліворуч (до центру)
    frags.append(text(xmin, py0 - 30, "сила = −нахил кривої → назад до рівноваги",
                      size=13, color=NEG))

    render(os.path.join(IMG, "energy-valley.svg"), W, H, *frags)


# ── Фігура 3 (вставка math): вікно лінійності — симетрична яма vs несиметрична ──
def fig_linearity_window():
    W, H = 780, 520
    px0, px1 = 152, 726          # поле графіка по x
    py0, py1 = 92, 396           # py0 — верх (100 %), py1 — низ (0.0001 %)
    xdec = (-3.0, 0.0)           # log10 зміщення у частках масштабу
    ydec = (-6.0, 0.0)           # log10 відносної похибки

    def X(lx): return px0 + (lx - xdec[0]) / (xdec[1] - xdec[0]) * (px1 - px0)
    def Y(ly): return py1 - (ly - ydec[0]) / (ydec[1] - ydec[0]) * (py1 - py0)

    frags = []

    # осі + позначки поділок (винесені НАЗОВНІ поля, щоб не різати написи)
    frags.append(line(px0, py0, px0, py1, color=LINE, sw=1.8))
    frags.append(line(px0, py1, px1, py1, color=LINE, sw=1.8))
    for d in range(int(ydec[0]), int(ydec[1]) + 1):
        frags.append(line(px0 - 7, Y(d), px0, Y(d), color=LINE, sw=1.4))
    for d in range(int(xdec[0]), int(xdec[1]) + 1):
        frags.append(line(X(d), py1, X(d), py1 + 7, color=LINE, sw=1.4))

    ylab = {0: "100 %", -1: "10 %", -2: "1 %", -3: "0.1 %",
            -4: "0.01 %", -5: "0.001 %", -6: "0.0001 %"}
    for d, s in ylab.items():
        frags.append(text(px0 - 14, Y(d) + 5, s, size=14, color=MUTED, anchor="end"))
    xlab = {-3: "0.1 %", -2: "1 %", -1: "10 %", 0: "100 %"}
    for d, s in xlab.items():
        frags.append(text(X(d), py1 + 26, s, size=14, color=MUTED))

    frags.append(text(px0 - 14, py0 - 34, "похибка сили −k·x", size=15, bold=True, anchor="start"))
    frags.append(text((px0 + px1) / 2, py1 + 56,
                      "зміщення у частках власного масштабу системи", size=15))

    # лінії: несиметрична яма (нахил 1) і симетрична (нахил 2)
    def curve(f, color, sw=3.0, dash=None):
        pts = []
        for i in range(0, 241):
            lx = xdec[0] + (xdec[1] - xdec[0]) * i / 240.0
            v = f(10 ** lx)
            if v <= 0:
                continue
            ly = math.log10(v)
            if ydec[0] <= ly <= ydec[1]:
                pts.append((X(lx), Y(ly)))
        return polyline(pts, color=color, sw=sw, dash=dash)

    asym = lambda t: 9.354 * t          # ½·|U‴|/U″ · s для ями Леннард-Джонса
    sym = lambda t: t * t / 6.0         # θ²/6 для маятника

    frags.append(curve(asym, POS))
    frags.append(curve(sym, NEG))

    # рівень 1 % і точки перетину
    frags.append(line(px0, Y(-2), px1, Y(-2), color=INK, sw=1.6, dash="7 5"))
    xa = math.log10(0.01 / 9.354)       # −2.97
    xs = math.log10(math.sqrt(0.06))    # −0.611
    for lx, col in ((xa, POS), (xs, NEG)):
        frags.append(line(X(lx), Y(-2), X(lx), Y(-2.55), color=col, sw=1.4, dash="4 4"))
        frags.append(circle(X(lx), Y(-2), 5, fill=BG, stroke=col, sw=2.2))

    # підписи кривих — у вільних зонах над/під своїми лініями
    frags.append(text(X(-2.92), Y(-0.30), "несиметрична яма:", size=14, color=POS, anchor="start"))
    frags.append(text(X(-2.92), Y(-0.30) + 19, "похибка ~ зміщення", size=14, color=POS, anchor="start"))

    frags.append(text(X(-0.02), Y(-3.55), "симетрична яма:", size=14, color=NEG, anchor="end"))
    frags.append(text(X(-0.02), Y(-3.55) + 19, "похибка ~ зміщення²", size=14, color=NEG, anchor="end"))

    # виноски до точок 1 %
    frags.append(text(X(xa) + 10, Y(-2.90), "0.1 % довжини зв'язку", size=13,
                      color=POS, anchor="start"))
    frags.append(text(X(xs) + 10, Y(-2.90), "кут 14°", size=13, color=NEG, anchor="start"))
    frags.append(text(px1 - 4, Y(-2) - 16, "рівень похибки 1 %", size=13, color=INK, anchor="end"))

    render(os.path.join(IMG, "linearity-window.svg"), W, H, *frags)


# ── Фігура 4 (вставка math): пласке дно — коли другої похідної немає ──────────
def fig_flat_bottom():
    W, H = 780, 440

    def coil(x1, y1, x2, y2, n=11, amp=9, color=INK, sw=2.2):
        dx, dy = x2 - x1, y2 - y1
        ln = math.hypot(dx, dy)
        ux, uy = dx / ln, dy / ln
        nx, ny = -uy, ux
        pts = [(x1, y1)]
        lead = 14.0
        for i in range(n + 1):
            t = lead + (ln - 2 * lead) * i / float(n)
            s = amp if i % 2 == 0 else -amp
            if i in (0, n):
                s = 0
            pts.append((x1 + ux * t + nx * s, y1 + uy * t + ny * s))
        pts.append((x2, y2))
        return polyline(pts, color=color, sw=sw)

    frags = []

    # ── ліва панель: два поперечні пружини ──
    ax, ay = 92, 128
    bx, by = 372, 128
    mx, my = 232, 248            # маса, зміщена вниз на y

    frags.append(text(232, 62, "два ненатягнені пружини, зміщення впоперек",
                      size=14, bold=True))
    frags.append(rect(ax - 16, ay - 34, 14, 68, fill="#e6e8ea", stroke=LINE, sw=1.5, rx=3))
    frags.append(rect(bx + 2, by - 34, 14, 68, fill="#e6e8ea", stroke=LINE, sw=1.5, rx=3))
    frags.append(line(ax, ay, bx, by, color=MUTED, sw=1.2, dash="5 5"))
    frags.append(coil(ax, ay, mx, my, color=POS))
    frags.append(coil(bx, by, mx, my, color=POS))
    frags.append(circle(mx, my, 12, fill=NEG, stroke=NEG, sw=1.5))

    frags.append(line(mx, ay, mx, my, color=NEG, sw=1.3, dash="4 4"))
    frags.append(text(mx + 12, (ay + my) / 2 + 5, "y", size=15, color=NEG, anchor="start", bold=True))
    frags.append(text((ax + mx) / 2 - 6, ay - 46, "вільна довжина L", size=13, color=MUTED))
    frags.append(text(232, 312, "видовження кожної: √(L²+y²) − L ≈ y² ⁄ 2L", size=14))
    frags.append(text(232, 340, "енергія: U = k₁·y⁴ ⁄ 4L²", size=14, color=POS, bold=True))
    frags.append(text(232, 368, "сила: F = −k₁·y³ ⁄ L²", size=14, color=POS, bold=True))

    # ── права панель: дно параболічне vs дно четвертого степеня ──
    px0, px1 = 470, 730
    py0, py1 = 96, 320
    frags.append(text((px0 + px1) / 2, 62, "форма дна поблизу нуля", size=14, bold=True))
    frags.append(line(px0, py1, px1, py1, color=LINE, sw=1.6))
    xc = (px0 + px1) / 2
    frags.append(line(xc, py1, xc, py0 - 8, color=LINE, sw=1.6))

    def C(fn, color, dash=None):
        pts = []
        for i in range(0, 161):
            u = -1.0 + 2.0 * i / 160.0
            v = fn(u)
            if v <= 1.02:
                pts.append((xc + u * (px1 - px0) / 2.0, py1 - v * (py1 - py0)))
        return polyline(pts, color=color, sw=3.0, dash=dash)

    frags.append(C(lambda u: u * u, NEG, dash="8 5"))
    frags.append(C(lambda u: u ** 4, POS))

    frags.append(text(px0 - 8, py0 + 4, "½k·x²", size=14, color=NEG, anchor="end"))
    frags.append(text(px1 + 8, py0 + 4, "∝ x⁴", size=14, color=POS, anchor="start"))
    frags.append(text((px0 + px1) / 2, py1 + 34, "пласке дно: U″(0) = 0", size=14, color=POS, bold=True))
    frags.append(text((px0 + px1) / 2, py1 + 58, "жорсткість у нулі зникає,", size=13))
    frags.append(text((px0 + px1) / 2, py1 + 78, "закону Гука немає", size=13))

    render(os.path.join(IMG, "flat-bottom.svg"), W, H, *frags)


# ── Фігура 5 (вставка hist): хронологія мовчання Гука ────────────────────────
def fig_hooke_timeline():
    W, H = 1020, 430
    AX = 250                       # рівень осі часу

    nodes = [
        (112, "1660",       ["Гук знаходить закон", "— за його ж словами"], INK),
        (248, "1664",       ["переговори про патент", "зриваються"],        INK),
        (384, "лютий 1675", ["Гюйгенс оголошує", "баланс-пружину"],         INK),
        (520, "1676",       ["анаграма в кінці", "«Геліоскопів»"],          POS),
        (656, "1678",       ["«Ut tensio, sic vis»", "надруковано"],        POS),
        (792, "1680",       ["Маріотт незалежно —", "і одразу до балок"],   INK),
        (928, "1705",       ["Воллер відкриває", "анаграму про арку"],      INK),
    ]

    frags = [line(60, AX, 990, AX, color=LINE, sw=2)]

    for i, (x, year, lines_, col) in enumerate(nodes):
        top_row = (i % 2 == 0)
        y_year = 76 if top_row else 158
        frags.append(text(x, y_year, year, size=15, color=col, bold=True))
        frags.append(mtext(x, y_year + 22, lines_, size=13, color=MUTED, lh=1.45))
        y_leader = y_year + 50
        frags.append(line(x, y_leader, x, AX - 8, color="#c8ccd2", sw=1.2, dash="4 4"))
        frags.append(circle(x, AX, 6, fill=BG, stroke=col, sw=2.4))

    # смуга «18 років мовчання»: 1660 → 1678
    x1, x2 = nodes[0][0], nodes[4][0]
    frags.append(line(x1, 300, x2, 300, color=MUTED, sw=5))
    for x in (x1, x2):
        frags.append(line(x, 292, x, 308, color=MUTED, sw=2))
        frags.append(line(x, AX + 8, x, 296, color="#c8ccd2", sw=1.2, dash="4 4"))
    frags.append(text((x1 + x2) / 2, 326, "18 років мовчання", size=14, color=MUTED, bold=True))
    frags.append(text((x1 + x2) / 2, 346, "закон знає лише автор", size=12, color=MUTED))

    # смуга «два роки під шифром»: 1676 → 1678
    x3, x4 = nodes[3][0], nodes[4][0]
    frags.append(line(x3, 364, x4, 364, color=POS, sw=5))
    for x in (x3, x4):
        frags.append(line(x, 356, x, 372, color=POS, sw=2))
        frags.append(line(x, 306, x, 360, color="#e6b3ab", sw=1.2, dash="4 4"))
    frags.append(text((x3 + x4) / 2, 394, "два роки під шифром",
                      size=14, color=POS, bold=True))

    render(os.path.join(IMG, "hooke-secrecy-timeline.svg"), W, H, *frags)


# ── Фігура 6 (вставка hist): три досліди з лекції 1678 року ──────────────────
def spring_line(x1, y1, x2, y2, n=9, amp=13, color=POS, sw=2.4):
    """Пружина-зигзаг між двома точками."""
    dx, dy = x2 - x1, y2 - y1
    ln = math.hypot(dx, dy)
    ux, uy = dx / ln, dy / ln
    nx, ny = -uy, ux
    lead = 12.0
    pts = [(x1, y1)]
    for i in range(n + 1):
        t = lead + (ln - 2 * lead) * i / float(n)
        s = 0 if i in (0, n) else (amp if i % 2 == 0 else -amp)
        pts.append((x1 + ux * t + nx * s, y1 + uy * t + ny * s))
    pts.append((x2, y2))
    return polyline(pts, color=color, sw=sw)


def fig_hooke_experiments():
    W, H = 860, 430
    frags = []

    for xs in (290, 570):
        frags.append(line(xs, 48, xs, 382, color="#dfe3e8", sw=1.2))

    def scale(x, y0, step, color=MUTED):
        """Шкала однакових поділок 1·2·3 праворуч від тіла."""
        out = [line(x, y0, x, y0 + 3 * step, color=color, sw=1.4)]
        for k in range(0, 4):
            ty = y0 + k * step
            out.append(line(x - 6, ty, x + 6, ty, color=color, sw=1.4))
            if k:
                out.append(text(x + 12, ty + 5, str(k), size=13, color=color, anchor="start"))
        out.append(text(x, y0 - 14, "поділки", size=12, color=color))
        return out

    # ── 1. спіральна пружина ──
    frags.append(text(150, 64, "спіральна пружина", size=14, bold=True))
    frags.append(rect(84, 88, 132, 12, fill="#e6e8ea", stroke=LINE, sw=1.4, rx=3))
    frags.append(spring_line(150, 100, 150, 194))
    frags.append(rect(132, 194, 36, 24, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=3))
    frags.extend(scale(238, 194, 32))
    frags.append(mtext(150, 330, ["спіраль із рівно тягненого",
                                  "дроту — сталь, залізо, мідь"], size=13, color=INK, lh=1.5))

    # ── 2. прямий дріт ──
    frags.append(text(430, 64, "прямий дріт", size=14, bold=True))
    frags.append(rect(364, 88, 132, 12, fill="#e6e8ea", stroke=LINE, sw=1.4, rx=3))
    frags.append(line(430, 100, 430, 234, color=POS, sw=2.6))
    frags.append(rect(412, 234, 36, 24, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=3))
    frags.extend(scale(516, 234, 18))
    frags.append(mtext(430, 330, ["довгий прямий дріт,",
                                  "підвішений із висоти"], size=13, color=INK, lh=1.5))

    # ── 3. затиснена деревина ──
    frags.append(text(710, 64, "затиснена деревина", size=14, bold=True))
    frags.append(rect(596, 110, 20, 96, fill="#e6e8ea", stroke=LINE, sw=1.4, rx=3))
    frags.append(line(616, 152, 818, 152, color=MUTED, sw=1.2, dash="5 5"))
    beam = [(616 + 170 * (i / 40.0), 152 + 46 * (i / 40.0) ** 2) for i in range(0, 41)]
    frags.append(polyline(beam, color=POS, sw=3))
    frags.append(rect(768, 198, 36, 24, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=3))
    frags.append(line(804, 198, 818, 198, color=MUTED, sw=1.2, dash="4 4"))
    frags.append(arrow(818, 152, 818, 198, color=INK, sw=1.8))
    frags.append(text(818, 140, "прогин", size=12, color=MUTED))
    frags.append(mtext(710, 330, ["суха деревина, затиснена",
                                  "одним кінцем горизонтально"], size=13, color=INK, lh=1.5))

    frags.append(text(430, 404, "одна гиря — один поділок, дві — два, три — три",
                      size=15, bold=True, color=INK))

    render(os.path.join(IMG, "hooke-experiments.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_force_extension()
    fig_energy_valley()
    fig_linearity_window()
    fig_flat_bottom()
    fig_hooke_timeline()
    fig_hooke_experiments()
    print("OK: force-extension.svg, energy-valley.svg, linearity-window.svg, "
          "flat-bottom.svg, hooke-secrecy-timeline.svg, hooke-experiments.svg")
