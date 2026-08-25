# -*- coding: utf-8 -*-
"""Фігури до теми «Швидкість».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

VEL  = "#c0392b"   # швидкість / рух — гаряче червоне
BOAT = "#2457d6"   # напрямок керування — синє
CUR  = "#27ae60"   # знос / зовнішнє поле — зелене


def ball(cx, cy, r=9, col=VEL):
    return circle(cx, cy, r, fill="#fef6e7", stroke=col, sw=2)


# ── Фігура 1: миттєва швидкість = нахил дотичної (січні → дотична) ────────────
def fig_instantaneous():
    W, H = 820, 486
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Миттєва швидкість — нахил дотичної до графіка положення", size=15.5, bold=True))

    ox, oy = 96, 392
    sx = 88.6                       # px на одиницю часу
    sy = 7.79                       # px на одиницю положення

    def X(t): return ox + t * sx
    def Y(fv): return oy - fv * sy
    def fpos(t): return 0.55 * t * t + 1.2 * t          # положення x(t) — опукле, росте
    def fder(t): return 1.1 * t + 1.2                   # dx/dt

    # осі
    f.append(arrow(ox, oy, X(7.0) + 12, oy, color=LINE, sw=1.6))
    f.append(arrow(ox, oy, ox, Y(37.0), color=LINE, sw=1.6))
    f.append(text(X(7.0) + 8, oy + 22, "час  t", size=12.5, color=INK, anchor="end"))
    f.append(text(ox + 8, Y(37.0) + 2, "положення  x", size=12.5, color=INK, anchor="start"))

    # крива x(t)
    pts, t = [], 0.0
    while t <= 6.7 + 1e-9:
        pts.append("%.1f,%.1f" % (X(t), Y(fpos(t))))
        t += 0.05
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts), INK))

    tP = 2.0
    xP, yP = X(tP), Y(fpos(tP))

    # січні до точок, що наближаються до P
    sec = [(3.5, "#8aa0d8"), (2.2, "#5f7fce"), (1.1, BOAT)]
    for i, (d, col) in enumerate(sec):
        tQ = tP + d
        xQ, yQ = X(tQ), Y(fpos(tQ))
        f.append(line(xP, yP, xQ, yQ, color=col, sw=1.8))
        f.append(circle(xQ, yQ, 4.2, fill=BG, stroke=col, sw=1.8))

    # трикутник приростів для найбільшої січної
    tQ0 = tP + 3.5
    xQ0, yQ0 = X(tQ0), Y(fpos(tQ0))
    f.append(line(xP, yP, xQ0, yP, color=MUTED, sw=1.2, dash="4,4"))
    f.append(line(xQ0, yP, xQ0, yQ0, color=MUTED, sw=1.2, dash="4,4"))
    f.append(text((xP + xQ0) / 2, yP + 18, "Δt", size=12.5, bold=True, color=MUTED))
    f.append(text(xQ0 + 12, (yP + yQ0) / 2 + 4, "Δx", size=12.5, bold=True, color=MUTED, anchor="start"))
    f.append(text(xQ0 + 12, yQ0 + 4, "січна: середня швидкість Δx/Δt", size=11.5, color=BOAT, anchor="start"))

    # дотична в P
    tta, ttb = 0.9, 4.9
    f.append(line(X(tta), Y(fpos(tP) + fder(tP) * (tta - tP)),
                  X(ttb), Y(fpos(tP) + fder(tP) * (ttb - tP)), color=FIELD, sw=3))
    f.append(text(X(ttb) + 70, Y(fpos(tP) + fder(tP) * (ttb - tP)) - 2,
                  "дотична: миттєва v = dx/dt", size=12.5, bold=True, color=FIELD, anchor="start"))

    # точка P
    f.append(ball(xP, yP, 6, col=VEL))
    f.append(text(xP - 12, yP + 4, "P", size=13, bold=True, color=VEL, anchor="end"))
    f.append(text(X(3.4), Y(3.0), "Δt → 0", size=12.5, bold=True, color=INK, anchor="middle"))

    b, bw, bh = textbox(W / 2, 458,
                        ["Нахил січної через дві точки — середня швидкість за проміжок Δt.",
                         "Стягуючи Δt до нуля, січна лягає на дотичну: її нахил і є миттєва швидкість."],
                        size=12, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "instantaneous-velocity.svg"), W, H, *f)


# ── Фігура 2: швидкість — вектор уздовж траєкторії; коло зі сталим модулем ────
def fig_velocity_vector():
    W, H = 920, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Швидкість — вектор: спрямований уздовж руху, з довжиною = модуль", size=15, bold=True))
    f.append(line(468, 58, 468, 388, color="#dfe4ea", sw=1.2, dash="4,6"))

    # ── ЛІВОРУЧ: хвиляста траєкторія, стрілки по дотичній ──
    f.append(text(240, 78, "Уздовж траєкторії", size=13.5, bold=True))
    x0 = 70
    A, mid, k = 66.0, 218.0, 0.0242
    def cy(x): return mid + A * math.sin(k * (x - x0))
    def dydx(x): return A * k * math.cos(k * (x - x0))
    pts = []
    x = x0
    while x <= 430:
        pts.append("%.1f,%.1f" % (x, cy(x)))
        x += 4
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(pts), MUTED))
    for xb in (120, 245, 370):
        yb = cy(xb)
        dx, dy = 1.0, dydx(xb)
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        f.append(ball(xb, yb, 7))
        f.append(arrow(xb, yb, xb + 48 * ux, yb + 48 * uy, color=VEL, sw=3))
    f.append(text(240, 372, "стрілка завжди по дотичній до шляху", size=11.5, color=MUTED))

    # ── ПРАВОРУЧ: коло, сталий модуль, різний напрямок ──
    f.append(text(694, 78, "Стала швидкість по колу", size=13.5, bold=True))
    ccx, ccy, R = 694, 226, 96
    f.append(circle(ccx, ccy, R, fill='none', stroke="#cfd6df", sw=1.8))
    f.append(circle(ccx, ccy, 3, fill=INK, stroke=INK, sw=1))
    for deg in (90, 0, 270, 180):
        th = math.radians(deg)
        px, py = ccx + R * math.cos(th), ccy - R * math.sin(th)
        # напрям руху проти годинникової: (-sinθ, -cosθ) в екранних координатах
        vx, vy = -math.sin(th), -math.cos(th)
        f.append(line(ccx, ccy, px, py, color=MUTED, sw=1.1, dash="3,4"))
        f.append(ball(px, py, 6))
        f.append(arrow(px, py, px + 52 * vx, py + 52 * vy, color=VEL, sw=3))
    f.append(text(694, 372, "|v| однаковий, напрямок різний", size=11.5, color=MUTED))

    b, bw, bh = textbox(W / 2, 440,
                        ["Миттєва швидкість завжди дивиться вздовж руху.",
                         "По колу зі сталим модулем тіло щомиті змінює напрямок — отже, змінює швидкість (звідси й прискорення)."],
                        size=12, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "velocity-vector.svg"), W, H, *f)


# ── Фігура 3: відносність — човен через річку, додавання швидкостей ───────────
def fig_relative():
    W, H = 860, 486
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Швидкість відносна: човен відносно берега — сума двох швидкостей", size=15, bold=True))

    top, bot = 96, 356
    # вода
    f.append(rect(60, top, 740, bot - top, fill="#eef4fd", stroke='none', sw=0, rx=0))
    for by in (top, bot):
        f.append(line(60, by, 800, by, color=LINE, sw=2))
    f.append(text(792, top - 8, "берег", size=11.5, color=MUTED, anchor="end"))
    f.append(text(792, bot + 20, "берег", size=11.5, color=MUTED, anchor="end"))

    # течія — зелені стрілки вниз за руслом (управо), у правій частині, щоб не чіпати трикутник
    for cyv in (150, 230, 306):
        f.append(arrow(560, cyv, 660, cyv, color=CUR, sw=2.4))
    f.append(text(610, 132, "течія (вода відносно берега)", size=11.5, bold=True, color=CUR, anchor="middle"))

    # старт човна на нижньому березі
    sx, sy = 190, bot
    # трикутник швидкостей
    tip_boat = (sx, sy - 96)                 # v_boat угору
    tip_res = (sx + 128, sy - 96)            # + v_water управо → вершина суми
    f.append(arrow(sx, sy, tip_boat[0], tip_boat[1], color=BOAT, sw=3.2))
    f.append(arrow(tip_boat[0], tip_boat[1], tip_res[0], tip_res[1], color=CUR, sw=3.2))
    f.append(arrow(sx, sy, tip_res[0], tip_res[1], color=VEL, sw=3.4))
    f.append(ball(sx, sy, 7, col=VEL))

    # справжній знесений шлях (продовження суми пунктиром до верхнього берега)
    dxr, dyr = tip_res[0] - sx, tip_res[1] - sy
    scale = (top - sy) / dyr
    ex, ey = sx + dxr * scale, top
    f.append(line(sx, sy, ex, ey, color=VEL, sw=1.3, dash="5,6"))
    f.append(ball(ex, ey, 6, col=VEL))
    f.append(text(ex + 8, ey + 18, "куди справді припливе", size=11, color=VEL, anchor="start"))

    # підписи векторів (з запасом, осторонь ліній)
    f.append(mtext(sx - 14, sy - 52, ["човен", "відносно води"], size=11.5, color=BOAT, anchor="end"))
    f.append(text((tip_boat[0] + tip_res[0]) / 2, tip_boat[1] - 12, "знос водою", size=11.5, color=CUR))
    f.append(mtext(tip_res[0] + 12, sy - 58, ["відносно берега", "= сума векторів"], size=11.5, color=VEL, anchor="start"))

    b, bw, bh = textbox(W / 2, 456,
                        ["Швидкості складаються як вектори: човен‑берег = човен‑вода + вода‑берег.",
                         "Та сама подія має різну швидкість у різних системах відліку — «абсолютної» швидкості немає."],
                        size=12, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "relative-velocity.svg"), W, H, *f)


def _poly(pts, fill, stroke="none", sw=0, opacity=1.0):
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    op = ' fill-opacity="%.2f"' % opacity if opacity < 1 else ''
    return '<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>' % (s, fill, stroke, sw, op)


# ── Фігура 4 (hist): доведення Орема — площа під v–t = шлях; теорема середньої ─
def fig_oresme_mean_speed():
    W, H = 880, 548
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Орем малює швидкість: площа під графіком v–час = пройдений шлях",
                  size=15.5, bold=True))

    ox, oy = 120, 406               # початок координат
    tmax, vmax = 6.0, 10.0
    sx, sy = 84.0, 26.6             # px на одиницю часу / швидкості
    def X(t): return ox + t * sx
    def Y(v): return oy - v * sy

    xF, yF = X(tmax), Y(vmax)       # кінцева точка (t, v_кінц)
    xB, yB = X(tmax), oy            # основа на осі часу
    vmean = vmax / 2.0
    yM = Y(vmean)                   # рівень середньої швидкості
    xMid, yMid = X(tmax / 2.0), yM  # де лінія перетинає середній рівень

    O = (ox, oy)
    F = (xF, yF)
    B = (xB, yB)
    Mid = (xMid, yMid)
    TLm = (ox, yM)                  # лівий кут прямокутника на середній висоті
    TRm = (xB, yM)                  # правий кут прямокутника на середній висоті

    # прямокутник на середній висоті — легка заливка
    f.append(_poly([O, B, TRm, TLm], fill="#eef0f2"))
    # два рівні трикутнички: лівий «брак» (у прямокутнику, над лінією) і правий «надлишок»
    f.append(_poly([O, TLm, Mid], fill="#fdecea", stroke=POS, sw=1.4, opacity=0.9))   # брак
    f.append(_poly([Mid, TRm, F], fill="#eafaf0", stroke=FIELD, sw=1.4, opacity=0.9)) # надлишок

    # осі
    f.append(arrow(ox, oy, X(tmax) + 54, oy, color=LINE, sw=1.6))
    f.append(arrow(ox, oy, ox, Y(vmax) - 26, color=LINE, sw=1.6))
    f.append(text(X(tmax) + 50, oy + 22, "час  t", size=12.5, color=INK, anchor="end"))
    f.append(text(ox - 8, Y(vmax) - 30, "швидкість  v", size=12.5, color=INK, anchor="start"))

    # середній рівень — пунктир через увесь прямокутник, трохи виступає праворуч
    f.append(line(ox, yM, xB + 40, yM, color=MUTED, sw=1.4, dash="6,5"))
    # вертикаль від середини лінії до осі часу
    f.append(line(xMid, yM, xMid, oy, color=MUTED, sw=1.1, dash="3,4"))

    # лінія швидкості (гіпотенуза трикутника розгону) — жирна
    f.append(line(ox, oy, xF, yF, color=VEL, sw=3.2))
    # основа й права сторона трикутника
    f.append(line(ox, oy, xB, oy, color=INK, sw=1.6))
    f.append(line(xB, oy, xF, yF, color=INK, sw=1.6))

    # точки
    f.append(ball(ox, oy, 5, col=INK))
    f.append(ball(xF, yF, 6, col=VEL))
    f.append(circle(xMid, yM, 4.5, fill=BG, stroke=VEL, sw=1.8))

    # підписи (осторонь ліній, із запасом)
    f.append(text(xF + 10, yF - 4, "v — кінцева", size=12.5, bold=True, color=VEL, anchor="start"))
    f.append(text(xB + 46, yM - 8, "½·v", size=12.5, bold=True, color=MUTED, anchor="start"))
    f.append(text(xB + 46, yM + 12, "(середня)", size=11, color=MUTED, anchor="start"))
    f.append(text(X(1.55), oy - 22, "площа = шлях", size=12.5, bold=True, color=INK, anchor="middle"))
    f.append(text(X(0.75), yM - 44, "брак", size=11, color=POS, anchor="middle"))
    f.append(text(X(4.55), Y(6.4), "надлишок", size=11, color=FIELD, anchor="middle"))
    f.append(text(xMid, oy + 22, "середина", size=11, color=MUTED, anchor="middle"))

    b, bw, bh = textbox(W / 2, 516,
                        "Правий надлишок точно заповнює лівий брак → площа трикутника розгону\n"
                        "дорівнює площі прямокутника на півшвидкості. Отже, розігнане зі спокою тіло\n"
                        "проходить стільки ж, скільки на сталій половині кінцевої швидкості.",
                        size=12, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "oresme-mean-speed.svg"), W, H, *f)


# ── Фігура 5 (hist): Зенонів парадокс стріли — низка застиглих митей ──────────
def _arrow_glyph(cx, cy, half=52, col=VEL):
    """Стріла: держак зі вістрям + оперення хвостом."""
    s = [arrow(cx - half, cy, cx + half, cy, color=col, sw=3)]
    tail = cx - half
    s.append(line(tail, cy, tail + 14, cy - 9, color=col, sw=2))
    s.append(line(tail, cy, tail + 14, cy + 9, color=col, sw=2))
    s.append(line(tail + 8, cy, tail + 22, cy - 9, color=col, sw=2))
    s.append(line(tail + 8, cy, tail + 22, cy + 9, color=col, sw=2))
    return "".join(s)


def fig_zeno_arrow():
    W, H = 880, 384
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Парадокс стріли: у кожну застиглу мить стріла нерухома",
                  size=15.5, bold=True))

    fw, fh = 218, 176
    gap = 30
    total = 3 * fw + 2 * gap
    x0 = (W - total) / 2.0
    ytop = 74
    ymid = ytop + fh / 2.0

    # слабка «лінія польоту» через усі кадри
    f.append(line(x0 - 6, ymid, x0 + total + 6, ymid, color="#dfe4ea", sw=1.4, dash="2,6"))

    labels = ("мить t₁", "мить t₂", "мить t₃")
    # у кожному кадрі стріла на дедалі дальшій позиції лінії польоту (застигла в межах кадру)
    for i in range(3):
        fx = x0 + i * (fw + gap)
        f.append(rect(fx, ytop, fw, fh, fill="#fbfcfd", stroke=LINE, sw=1.6, rx=10))
        f.append(text(fx + fw / 2, ytop - 10, labels[i], size=12.5, bold=True, color=INK))
        # позиція стріли поступово посувається вправо від кадру до кадру
        ax = fx + fw * (0.34 + 0.16 * i)
        f.append(_arrow_glyph(ax, ymid, half=48, col=VEL))
        f.append(text(fx + fw / 2, ytop + fh - 16, "стріла стоїть", size=11.5, color=MUTED))
        f.append(text(fx + fw / 2, ytop + fh - 34, "Δx = 0 за Δt = 0", size=11, color=POS))

    # стрілочки-переходи між кадрами
    for i in range(2):
        mx = x0 + fw + i * (fw + gap) + gap / 2.0
        f.append(text(mx, ymid - 4, "?", size=20, bold=True, color=MUTED))

    b, bw, bh = textbox(W / 2, 354,
                        "Зенон: у будь-яку окрему мить стріла займає рівно свій обсяг і не рухається —\n"
                        "вона стоїть. Але з суми таких стоянь нізвідки взятися рухові. Знак біди\n"
                        "поставлено точно: що таке швидкість у мить, за яку не пройдено відстані?",
                        size=12, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "zeno-arrow.svg"), W, H, *f)


# ── (proj-вставка) Оцінка швидкості з відліків: наївна різниця vs МНК ─────────
def fig_velocity_estimates():
    import random
    random.seed(7)
    W, H = 900, 540
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Оцінка швидкості з відліків: наївна різниця тоне в шумі, МНК — ні",
                  size=15, bold=True))

    dt = 0.1
    ts = [i * dt for i in range(61)]
    def v_true(t): return 0.5 + 3.0 * math.exp(-((t - 3.0) / 1.2) ** 2)
    x_true = [0.0]
    for i in range(1, len(ts)):
        x_true.append(x_true[-1] + v_true(ts[i - 1]) * dt)
    sigma = 0.15
    xs = [x_true[i] + random.gauss(0, sigma) for i in range(len(ts))]

    v_naive = [0.0] * len(ts)
    for i in range(1, len(ts)):
        v_naive[i] = (xs[i] - xs[i - 1]) / dt
    Mw = 4
    S = Mw * (Mw + 1) * (2 * Mw + 1) // 3
    v_lsq = {}
    for i in range(Mw, len(ts) - Mw):
        num = 0.0
        for k in range(-Mw, Mw + 1):
            num += k * xs[i + k]
        v_lsq[i] = num / S / dt

    ox, x1 = 96, 812
    vmin, vmax = -3.2, 6.6
    pyt, pyb = 100, 452
    def X(t): return ox + (t / 6.0) * (x1 - ox)
    def Y(v):
        v = max(vmin, min(vmax, v))
        return pyt + (vmax - v) / (vmax - vmin) * (pyb - pyt)

    f.append(line(ox, pyt - 6, ox, pyb, color=LINE, sw=1.6))
    f.append(arrow(ox, pyt - 4, ox, pyt - 22, color=LINE, sw=1.6))
    f.append(arrow(ox, Y(0), x1 + 16, Y(0), color=LINE, sw=1.6))
    f.append(text(x1 + 12, Y(0) + 20, "час t, с", size=12.5, color=INK, anchor="end"))
    f.append(text(ox - 6, pyt - 10, "v, м/с", size=12, color=INK, anchor="start"))
    leg_top, leg_bot, leg_left = 100, 192, 604   # легенда (нижче) перекриває цю смугу — не тягнути лінію під неї
    for gv in (2, 4, 6):
        yy = Y(gv)
        xend = leg_left - 4 if leg_top <= yy <= leg_bot else x1
        f.append(line(ox, yy, xend, yy, color="#eef1f4", sw=1))
        f.append(text(ox - 8, yy + 4, str(gv), size=11, color=MUTED, anchor="end"))
    f.append(text(ox - 8, Y(0) + 4, "0", size=11, color=MUTED, anchor="end"))

    pn = " ".join("%.1f,%.1f" % (X(ts[i]), Y(v_naive[i])) for i in range(1, len(ts)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.3"/>' % (pn, "#d9796b"))
    idxs = sorted(v_lsq)
    pl = " ".join("%.1f,%.1f" % (X(ts[i]), Y(v_lsq[i])) for i in idxs)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (pl, BOAT))
    pt = " ".join("%.1f,%.1f" % (X(ts[i]), Y(v_true(ts[i]))) for i in range(len(ts)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.2"/>' % (pt, CUR))

    lx, ly = 620, 122
    f.append(rect(lx - 16, ly - 22, 218, 92, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    rows = [(CUR, 3.2, "істинна швидкість"),
            ("#d9796b", 1.8, "наївна Δx/Δt (назад)"),
            (BOAT, 2.8, "МНК, ковзне вікно 9")]
    for j, (col, sw, lab) in enumerate(rows):
        yy = ly + j * 26
        f.append(line(lx, yy, lx + 34, yy, color=col, sw=sw))
        f.append(text(lx + 44, yy + 4, lab, size=12, color=INK, anchor="start"))

    f.append(text(X(1.2), Y(-2.35), "шум підсилений на √2/Δt", size=11.5, color="#c0392b", anchor="middle"))
    f.append(text(X(3.0), Y(4.75), "МНК ледь згладжує пік", size=11.5, color=BOAT, anchor="middle"))

    b, bw, bh = textbox(W / 2, 508,
                        ["Ті самі зашумлені відліки положення. Наївна різниця сусідніх відліків стрибає на метри за секунду там,",
                         "де істинна швидкість — частки; МНК-нахил у вікні з 9 відліків тримається правди, лише злегка розмиваючи пік."],
                        size=12, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "velocity-estimates.svg"), W, H, *f)


# ── (proj-вставка) Ковзне вікно: нахил прямої МНК = швидкість ─────────────────
def fig_lsq_window():
    import random
    random.seed(3)
    W, H = 860, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Ковзне вікно: пряма найменших квадратів, її нахил — оцінка швидкості",
                  size=15, bold=True))

    n = 22
    dt = 0.3
    ts = [i * dt for i in range(n)]
    def x_true(t): return 0.8 * t + 0.10 * t * t
    sigma = 0.28
    xs = [x_true(ts[i]) + random.gauss(0, sigma) for i in range(n)]

    ox, x1 = 78, 612
    pyt, pyb = 88, 380
    tmax = ts[-1]
    xmn = min(xs) - 0.6
    xmx = max(xs) + 0.6
    def X(t): return ox + t / tmax * (x1 - ox)
    def Y(xx): return pyb - (xx - xmn) / (xmx - xmn) * (pyb - pyt)

    f.append(arrow(ox, pyb, x1 + 14, pyb, color=LINE, sw=1.6))
    f.append(arrow(ox, pyb, ox, pyt - 12, color=LINE, sw=1.6))
    f.append(text(x1 + 10, pyb + 20, "час t", size=12.5, color=INK, anchor="end"))
    f.append(text(ox + 4, pyt - 14, "положення x", size=12.5, color=INK, anchor="start"))

    Mw = 4
    ci = 11
    lo, hi = ci - Mw, ci + Mw
    f.append(rect(X(ts[lo]) - 6, pyt - 2, X(ts[hi]) - X(ts[lo]) + 12, pyb - pyt + 2,
                  fill="#eaf0fb", stroke="#cdd9f1", sw=1, rx=6))
    f.append(text((X(ts[lo]) + X(ts[hi])) / 2, pyt + 12, "вікно з N = 9 відліків",
                  size=11.5, color=BOAT))

    win_t = ts[lo:hi + 1]
    win_x = xs[lo:hi + 1]
    tb = sum(win_t) / len(win_t)
    xb = sum(win_x) / len(win_x)
    num = sum((win_t[i] - tb) * (win_x[i] - xb) for i in range(len(win_t)))
    den = sum((win_t[i] - tb) ** 2 for i in range(len(win_t)))
    b = num / den
    a = xb - b * tb
    def fit(t): return a + b * t
    tL, tR = ts[lo] - 0.16, ts[hi] + 0.16
    f.append(line(X(tL), Y(fit(tL)), X(tR), Y(fit(tR)), color=BOAT, sw=3))

    t_a, t_b = ts[ci - 2], ts[ci + 2]
    f.append(line(X(t_a), Y(fit(t_a)), X(t_b), Y(fit(t_a)), color=MUTED, sw=1.2, dash="4,4"))
    f.append(line(X(t_b), Y(fit(t_a)), X(t_b), Y(fit(t_b)), color=MUTED, sw=1.2, dash="4,4"))
    f.append(text((X(t_a) + X(t_b)) / 2, Y(fit(t_a)) + 18, "Δt", size=12, bold=True, color=MUTED))
    f.append(text(X(t_b) + 10, (Y(fit(t_a)) + Y(fit(t_b))) / 2, "Δx", size=12, bold=True,
                  color=MUTED, anchor="start"))
    f.append(text(X(t_b) + 10, Y(fit(t_b)) - 10, "нахил b = v", size=12.5, bold=True,
                  color=BOAT, anchor="start"))

    for i in range(n):
        inw = lo <= i <= hi
        f.append(circle(X(ts[i]), Y(xs[i]), 4.6 if inw else 3.4,
                        fill=(BG if inw else "#eef1f4"),
                        stroke=(VEL if inw else MUTED), sw=2 if inw else 1.4))

    px = 646
    f.append(mtext(px, 116,
                   ["Ширше вікно:", "• менше шуму (~ 1/√Σk²)", "• більша затримка", "• розмиття різких",
                    "  змін швидкості"],
                   size=12.5, color=INK, anchor="start", lh=1.55))
    f.append(mtext(px, 258,
                   ["Рівні проміжки →", "нахил = зважена сума", "зі сталими вагами (FIR):",
                    "wₖ = k /(Δt·Σk²)"],
                   size=12.5, color=INK, anchor="start", lh=1.55))

    b2, bw, bh = textbox(W / 2, 470,
                         ["Пряму кладемо на відліки методом найменших квадратів; її нахил і є оцінка швидкості в центрі вікна.",
                          "Для рівних проміжків ваги сталі — це згортка (FIR), яку на МК рахують кількома множеннями за такт."],
                         size=12, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b2)
    return render(os.path.join(IMG, "lsq-window.svg"), W, H, *f)


# ── (math-вставка) Похідна вектора положення: хорда Δr → дотична ──────────────
def fig_chord_tangent():
    W, H = 880, 520
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Похідна вектора положення: хорда Δr у границі лягає на дотичну", size=15, bold=True))

    Ox, Oy = 92, 452                      # початок відліку O
    x0 = 150
    def cy(x):   return 316 - 128 * math.sin((x - x0) / 300.0)
    def dydx(x): return -128 * math.cos((x - x0) / 300.0) / 300.0

    pts, x = [], x0
    while x <= 664:
        pts.append("%.1f,%.1f" % (x, cy(x)))
        x += 4
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts), MUTED))

    xP, yP = 384, cy(384)
    xQ, yQ = 548, cy(548)
    xQ2, yQ2 = 470, cy(470)               # ближча точка Q' — натяк Δt → 0

    f.append(circle(Ox, Oy, 3.4, fill=INK, stroke=INK, sw=1))
    f.append(text(Ox - 8, Oy + 6, "O", size=13, bold=True, color=INK, anchor="end"))

    f.append(arrow(Ox, Oy, xP, yP, color=BOAT, sw=2.4))
    f.append(arrow(Ox, Oy, xQ, yQ, color="#8aa0d8", sw=2.0))
    f.append(text(246, 348, "r(t)", size=13, bold=True, color=BOAT, italic=True))
    f.append(text(500, 250, "r(t+Δt)", size=12.5, color="#5f7fce", italic=True, anchor="start"))

    f.append(line(xP, yP, xQ2, yQ2, color="#9fd8b6", sw=1.6, dash="5,5"))
    f.append(circle(xQ2, yQ2, 4.0, fill=BG, stroke="#9fd8b6", sw=1.6))
    f.append(text(xQ2 + 8, yQ2 + 20, "Δt → 0", size=11.5, color="#3f9e6b", anchor="start"))

    f.append(arrow(xP, yP, xQ, yQ, color=CUR, sw=3.0))
    f.append(text(528, 192, "Δr", size=13.5, bold=True, color=CUR, anchor="start"))

    dy = dydx(xP)
    n = math.hypot(1.0, dy)
    ux, uy = 1.0 / n, dy / n
    f.append(line(xP - 120 * ux, yP - 120 * uy, xP + 152 * ux, yP + 152 * uy, color="#d0aa55", sw=1.4, dash="2,4"))
    f.append(arrow(xP, yP, xP + 118 * ux, yP + 118 * uy, color=VEL, sw=3.2))
    f.append(text(xP + 118 * ux + 14, yP + 118 * uy - 22, "v = dr/dt", size=13, bold=True, color=VEL, anchor="start"))

    f.append(ball(xP, yP, 6, col=VEL))
    f.append(text(xP - 12, yP + 16, "P", size=13, bold=True, color=VEL, anchor="end"))
    f.append(ball(xQ, yQ, 5.5))
    f.append(text(xQ + 10, yQ - 6, "Q", size=13, bold=True, color=INK, anchor="start"))

    b, bw, bh = textbox(W / 2, 494,
                        ["Хорда Δr з'єднує два близькі положення на траєкторії.",
                         "Стягуючи Δt, підводимо Q до P: напрямок хорди прямує до дотичної, а Δr/Δt — до швидкості v уздовж неї."],
                        size=12, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "math-chord-tangent.svg"), W, H, *f)


# ── (math-вставка) Складові й модуль — гіпотенуза за Піфагором ────────────────
def fig_components():
    W, H = 720, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Модуль швидкості — гіпотенуза за складовими", size=15.5, bold=True))

    Ax, Ay = 190, 340
    Bx, By = 470, 150
    Cx, Cy = Bx, Ay                       # прямий кут унизу праворуч

    f.append(arrow(Ax, Ay, Cx, Cy, color=BOAT, sw=2.6))       # vx горизонтальний
    f.append(arrow(Cx, Cy, Bx, By, color=CUR, sw=2.6))        # vy вертикальний
    s = 14
    f.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" stroke-width="1.4"/>'
             % (Cx - s, Cy, Cx - s, Cy - s, Cx, Cy - s, MUTED))
    f.append(arrow(Ax, Ay, Bx, By, color=VEL, sw=3.4))
    f.append(ball(Ax, Ay, 6, col=VEL))

    f.append(text((Ax + Cx) / 2, Ay + 26, "vx = dx/dt", size=12.5, bold=True, color=BOAT))
    f.append(text(Cx + 12, (Cy + By) / 2 + 4, "vy = dy/dt", size=12.5, bold=True, color=CUR, anchor="start"))
    f.append(text((Ax + Bx) / 2 - 30, (Ay + By) / 2 - 16, "v", size=15, bold=True, color=VEL, italic=True, anchor="end"))
    f.append(text((Ax + Bx) / 2 - 30, (Ay + By) / 2 + 8, "|v| = √(vx² + vy²)", size=12.5, bold=True, color=VEL, anchor="end"))
    f.append(text(Ax - 10, Ay + 6, "точка на траєкторії", size=11, color=MUTED, anchor="end"))

    b, bw, bh = textbox(W / 2, 442,
                        ["Складові vx, vy — похідні координат, катети прямокутного трикутника.",
                         "Вектор швидкості — гіпотенуза; його довжина за Піфагором і є модуль |v|, число на спідометрі."],
                        size=12, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "math-velocity-components.svg"), W, H, *f)


# ── (math-вставка) Переміщення = площа під v(t); теорема про середнє ──────────
def fig_integral():
    W, H = 880, 512
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Переміщення — площа під графіком швидкості (зі знаком)", size=15, bold=True))

    ox, y0, sx, sy = 96, 300, 63.0, 42.0
    def X(t): return ox + t * sx
    def Y(v): return y0 - v * sy
    def fv(t): return 2.6 * math.sin(0.62 * t) + 0.7
    T0, T1 = 0.0, 10.0
    tz1, tz2 = 5.51, 9.70                 # нулі швидкості
    vbar, tstar = 0.70, 5.07              # середня й мить, де v = v̄

    def area_pts(ta, tb):
        p = [(X(ta), y0)]
        t = ta
        while t <= tb + 1e-9:
            p.append((X(t), Y(fv(t))))
            t += 0.1
        p.append((X(tb), y0))
        return p

    f.append(line(ox, Y(3.6), ox, Y(-2.4), color=LINE, sw=1.6))
    f.append(arrow(ox, y0, X(10.5), y0, color=LINE, sw=1.6))
    f.append(text(X(10.5) + 2, y0 - 8, "t", size=13, color=INK, anchor="end", italic=True))
    f.append(text(ox - 8, Y(3.6) + 4, "v", size=13, color=INK, anchor="end", italic=True))

    f.append(_poly(area_pts(T0, tz1), "#e7f6ee"))
    f.append(_poly(area_pts(tz1, tz2), "#eaf0fd"))
    f.append(_poly(area_pts(tz2, T1), "#e7f6ee"))

    pts, t = [], T0
    while t <= T1 + 1e-9:
        pts.append("%.1f,%.1f" % (X(t), Y(fv(t))))
        t += 0.05
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(pts), INK))

    f.append(line(ox, Y(vbar), X(10.2), Y(vbar), color=VEL, sw=1.8, dash="7,5"))
    f.append(text(X(10.2) + 2, Y(vbar) - 8, "v̄ (середня)", size=12, bold=True, color=VEL, anchor="end"))

    f.append(line(X(tstar), Y(vbar), X(tstar), y0, color=MUTED, sw=1.2, dash="3,4"))
    f.append(circle(X(tstar), Y(vbar), 5, fill=BG, stroke=VEL, sw=2.2))
    f.append(text(X(tstar), y0 + 20, "t*", size=12.5, bold=True, color=VEL))

    f.append(mtext(X(2.5), Y(1.75), ["площа +", "(уперед)"], size=12, bold=True, color="#2f8f5b"))
    f.append(mtext(X(7.55), Y(-0.75), ["площа −", "(назад)"], size=12, bold=True, color=BOAT))

    b, bw, bh = textbox(W / 2, 484,
                        ["Переміщення = ∫ v dt — площа під кривою зі знаком: над віссю додатна, під віссю від'ємна.",
                         "Теорема про середнє: у якусь мить t* миттєва v дорівнює середній v̄."],
                        size=12, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "math-velocity-integral.svg"), W, H, *f)


if __name__ == "__main__":
    fig_instantaneous()
    fig_velocity_vector()
    fig_relative()
    fig_oresme_mean_speed()
    fig_zeno_arrow()
    fig_velocity_estimates()
    fig_lsq_window()
    fig_chord_tangent()
    fig_components()
    fig_integral()
    print("OK: фігури у", IMG)
