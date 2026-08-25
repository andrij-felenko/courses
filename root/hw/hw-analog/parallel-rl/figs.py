# -*- coding: utf-8 -*-
"""Фігури до теми «Паралельне RL-коло: двоїсті перехідні процеси».
Чотири фігури:
  parallel-rl.svg     — саме коло: джерело струму ∥ R ∥ L, спільна напруга
  natural-decay.svg   — джерело прибрали: струм котушки спадає за L/R, напруга теж
  dual-mirror.svg     — дзеркало послідовного RC: що з чим міняється місцями
  rise-fall.svg       — увімкнення джерела струму: розподіл струму між R і L у часі
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def polyline(pts, color=INK, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (s, color, sw, d))


def axes(x0, y0, w, h, xlabel, ylabel):
    out = [line(x0, y0, x0 + w, y0, color=MUTED, sw=1.5),
           line(x0, y0, x0, y0 - h, color=MUTED, sw=1.5)]
    out.append(text(x0 + w, y0 + 16, xlabel, size=11, color=MUTED, anchor="end"))
    out.append(text(x0 - 6, y0 - h, ylabel, size=11, color=MUTED, anchor="end"))
    return "".join(out)


def resistor(x, ytop, ybot, label=None, lcolor=MUTED):
    """Вертикальний резистор-зигзаг між ytop і ybot на координаті x."""
    out = [line(x, ytop, x, ytop + 8, color=INK, sw=2)]
    zz = [(x, ytop + 8)]
    n = 6
    span = (ybot - 8) - (ytop + 8)
    for i in range(n):
        yy = ytop + 8 + span * (i + 0.5) / n
        dx = 8 if i % 2 == 0 else -8
        zz.append((x + dx, yy))
    zz.append((x, ybot - 8))
    out.append(polyline(zz, color=INK, sw=2))
    out.append(line(x, ybot - 8, x, ybot, color=INK, sw=2))
    if label:
        out.append(text(x + 16, (ytop + ybot) / 2, label, size=12, color=lcolor, anchor="start"))
    return "".join(out)


def coil(x, ytop, ybot, label=None, lcolor=MUTED):
    """Вертикальна котушка (півкільця) між ytop і ybot на координаті x."""
    out = [line(x, ytop, x, ytop + 8, color=INK, sw=2)]
    n = 4
    span = (ybot - 8) - (ytop + 8)
    r = span / (2 * n)
    arcs = []
    for i in range(n):
        cy = ytop + 8 + r * (2 * i + 1)
        # півколо, що випинається праворуч
        arcs.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" '
                    'fill="none" stroke="%s" stroke-width="2"/>'
                    % (x, cy - r, r, r, x, cy + r, INK))
    out.extend(arcs)
    out.append(line(x, ybot - 8, x, ybot, color=INK, sw=2))
    if label:
        out.append(text(x + 16, (ytop + ybot) / 2, label, size=12, color=lcolor, anchor="start"))
    return "".join(out)


def ground(x, y):
    return (line(x, y - 14, x, y, color=INK, sw=2) +
            line(x - 14, y, x + 14, y, color=INK, sw=2.6) +
            line(x - 9, y + 5, x + 9, y + 5, color=INK, sw=2) +
            line(x - 4, y + 10, x + 4, y + 10, color=INK, sw=2))


# ── 1. Саме коло: джерело струму ∥ R ∥ L ─────────────────────────────────────
def fig_parallel_rl():
    W, H = 700, 330
    title = "Паралельне RL: усі бачать ту саму напругу"
    parts = []
    ytop, ybot = 80, 250
    xs = [150, 330, 510]            # джерело, резистор, котушка
    # верхня й нижня шини
    parts.append(line(xs[0], ytop, xs[-1], ytop, color=INK, sw=2.4))
    parts.append(line(xs[0], ybot, xs[-1], ybot, color=INK, sw=2.4))
    # вузли
    for x in xs:
        parts.append(circle(x, ytop, 3.5, fill=INK, stroke=INK))
        parts.append(circle(x, ybot, 3.5, fill=INK, stroke=INK))

    # джерело струму (коло зі стрілкою всередині) — гілка 1
    sx = xs[0]
    cy = (ytop + ybot) / 2
    parts.append(line(sx, ytop, sx, cy - 26, color=INK, sw=2))
    parts.append(line(sx, cy + 26, sx, ybot, color=INK, sw=2))
    parts.append(circle(sx, cy, 26, fill=BG, stroke=INK, sw=2))
    parts.append(arrow(sx, cy + 14, sx, cy - 14, color=POS, sw=2.4))
    parts.append(text(sx - 34, cy + 4, "I", size=14, color=POS, anchor="end", bold=True))
    parts.append(text(sx - 34, cy + 20, "дж", size=10, color=POS, anchor="end"))

    # резистор — гілка 2
    parts.append(resistor(xs[1], ytop, ybot, "R"))
    # котушка — гілка 3
    parts.append(coil(xs[2], ytop, ybot, "L"))

    # спільна напруга U на верхній шині
    parts.append(text((xs[0] + xs[-1]) / 2, ytop - 14, "спільна напруга U на всіх трьох",
                      size=13, bold=True))
    # підписи струмів гілок
    parts.append(text(xs[1] - 16, ybot + 22, "iR = U/R", size=11, color=NEG, anchor="middle"))
    parts.append(text(xs[2] - 16, ybot + 22, "iL (інерційний)", size=11, color=FIELD, anchor="middle"))
    parts.append(text(xs[0], ybot + 22, "I дж", size=11, color=POS, anchor="middle"))
    # KCL-підпис
    parts.append(text((xs[0] + xs[-1]) / 2, ybot + 44, "вузол: I дж = iR + iL  (закон струмів)",
                      size=11, color=MUTED))

    render(os.path.join(IMG, "parallel-rl.svg"), W, H, *parts, title=title)


# ── 2. Природна реакція: струм котушки спадає за L/R ─────────────────────────
def fig_natural_decay():
    W, H = 720, 340
    title = "Джерело прибрали: котушка живить резистор сама"
    parts = []

    # лівий бік — схема після від'єднання джерела (R ∥ L петля)
    lx, lt, lb = 95, 90, 250
    rx = 175
    parts.append(line(lx, lt, rx, lt, color=INK, sw=2.2))
    parts.append(line(lx, lb, rx, lb, color=INK, sw=2.2))
    parts.append(resistor(lx, lt, lb, "R", lcolor=NEG))
    parts.append(coil(rx, lt, lb, "L", lcolor=FIELD))
    parts.append(text((lx + rx) / 2, lt - 14, "лише R ∥ L", size=12, bold=True))
    # стрілка струму, що циркулює
    parts.append(arrow(rx, lb + 4, lx, lb + 4, color=FIELD, sw=2.2))
    parts.append(text((lx + rx) / 2, lb + 22, "iL", size=11, color=FIELD))
    parts.append(text((lx + rx) / 2, lb + 38, "тече ще", size=10, color=MUTED))

    # правий бік — графік спаду
    x0, y0, gw, gh = 300, 270, 380, 200
    top, bot = y0 - gh, y0
    parts.append(axes(x0, y0, gw, gh, "час", "iL"))
    I0 = top + 16
    # експонента спаду iL = I0·e^(-t/τ)
    pts = []
    for k in range(0, int(gw) - 4):
        t = k / 58.0
        y = bot - (bot - I0) * math.exp(-t)
        pts.append((x0 + k, y))
    parts.append(polyline(pts, color=FIELD, sw=2.6))
    parts.append(text(x0 + 6, I0 - 8, "I₀", size=12, color=FIELD, anchor="start", bold=True))
    # позначка однієї τ (на рівні 37%)
    xtau = x0 + 58.0
    y37 = bot - (bot - I0) * math.exp(-1)
    parts.append(line(xtau, bot, xtau, y37, color=MUTED, sw=1.0, dash="4,4"))
    parts.append(line(x0, y37, xtau, y37, color=MUTED, sw=1.0, dash="4,4"))
    parts.append(text(xtau, bot + 16, "τ = L/R", size=12, color=INK, bold=True))
    parts.append(text(x0 - 6, y37, "37%", size=10, color=MUTED, anchor="end"))
    # 5τ
    x5 = x0 + 58.0 * 5
    if x5 < x0 + gw - 4:
        parts.append(line(x5, bot, x5, bot - 6, color=MUTED, sw=1.2))
        parts.append(text(x5, bot + 16, "5τ ≈ 0", size=10, color=MUTED))
    # підпис: напруга на резисторі повторює форму iL
    parts.append(text(x0 + gw * 0.62, top + 18, "U = R·iL — теж", size=11, color=NEG))
    parts.append(text(x0 + gw * 0.62, top + 32, "падає за тим самим e", size=11, color=NEG))

    render(os.path.join(IMG, "natural-decay.svg"), W, H, *parts, title=title)


# ── 3. Дзеркало послідовного RC ──────────────────────────────────────────────
def fig_dual_mirror():
    W, H = 720, 300
    title = "Точне дзеркало: паралельне RL ↔ послідовне RC"
    parts = []
    # дві колонки відповідностей
    rows = [
        ("джерело СТРУМУ",        "джерело НАПРУГИ"),
        ("спільна НАПРУГА U",     "спільний СТРУМ i"),
        ("котушка L",            "конденсатор C"),
        ("струм iL не стрибає",  "напруга U_C не стрибає"),
        ("τ = L/R",              "τ = R·C"),
        ("R паралельно",         "R послідовно"),
    ]
    lx = 60
    cx = W / 2
    colL = 215
    colR = 505
    parts.append(text(colL, 64, "ПАРАЛЕЛЬНЕ RL", size=14, bold=True, color=FIELD))
    parts.append(text(colR, 64, "ПОСЛІДОВНЕ RC", size=14, bold=True, color=NEG))
    y = 92
    dy = 33
    for a, b in rows:
        parts.append(fitbox(colL - 130, y, 175, 26, a, size=12, fill="#eafaf0", stroke=FIELD))
        parts.append(text(cx, y + 17, "⇄", size=16, color=MUTED))
        parts.append(fitbox(colR - 45, y, 175, 26, b, size=12, fill="#eaf0fd", stroke=NEG))
        y += dy

    render(os.path.join(IMG, "dual-mirror.svg"), W, H, *parts, title=title)


# ── 4. Увімкнення джерела струму: розподіл між R і L ────────────────────────
def fig_rise_fall():
    W, H = 720, 340
    title = "Увімкнули струм: спершу весь у резистор, далі весь у котушку"
    parts = []
    x0, y0, gw, gh = 80, 270, 600, 205
    top, bot = y0 - gh, y0
    parts.append(axes(x0, y0, gw, gh, "час", "струм"))
    Ilev = top + 26                 # рівень повного струму джерела
    parts.append(line(x0, Ilev, x0 + gw - 4, Ilev, color=MUTED, sw=1.0, dash="5,4"))
    parts.append(text(x0 + gw - 8, Ilev - 6, "I джерела", size=11, color=POS, anchor="end"))

    xstep = x0 + gw * 0.10
    # iL: наростає від 0 до I (бере на себе весь струм)
    iL = []
    for k in range(0, int(gw) - 4):
        xx = x0 + k
        if xx < xstep:
            iL.append((xx, bot - 2))
        else:
            t = (xx - xstep) / 60.0
            y = bot - (bot - Ilev) * (1 - math.exp(-t))
            iL.append((xx, y))
    parts.append(polyline(iL, color=FIELD, sw=2.6))
    parts.append(text(x0 + gw * 0.74, Ilev + 26, "iL котушки → весь струм", size=11, color=FIELD))

    # iR: стрибає до I і спадає до 0 (доповнює iL до сталого I)
    iR = []
    for k in range(0, int(gw) - 4):
        xx = x0 + k
        if xx < xstep:
            iR.append((xx, bot - 2))
        else:
            t = (xx - xstep) / 60.0
            y = bot - (bot - Ilev) * math.exp(-t)
            iR.append((xx, y))
    parts.append(polyline(iR, color=NEG, sw=2.6))
    parts.append(text(x0 + gw * 0.30, top + 50, "iR резистора → спадає до 0", size=11, color=NEG))
    # вертикаль увімкнення
    parts.append(line(xstep, top + 4, xstep, bot, color=MUTED, sw=1.0, dash="3,3"))
    parts.append(text(xstep, bot + 18, "увімкнули", size=10, color=MUTED))
    # підпис суми
    parts.append(text(x0 + gw * 0.5, top + 14, "iR + iL = I джерела весь час", size=11, color=MUTED, bold=True))

    render(os.path.join(IMG, "rise-fall.svg"), W, H, *parts, title=title)


# ── 5. Два виведення поряд сходяться до однієї форми (до math-duality) ────────
def fig_duality_derivation():
    W, H = 760, 360
    title = "Два виведення сходяться до однієї форми"
    parts = []
    # дві колонки
    colL, colR = 200, 560
    bw = 270
    parts.append(text(colL, 60, "RC (послідовне)", size=14, bold=True, color=NEG))
    parts.append(text(colR, 60, "RL (паралельне)", size=14, bold=True, color=FIELD))

    stepsL = [
        "i = C · dV_C/dt",
        "E = i·R + V_C   (KVL)",
        "dV_C/dt = (E − V_C)/(R·C)",
    ]
    stepsR = [
        "U = L · diL/dt",
        "I = U/R + iL   (KCL)",
        "diL/dt = (I − iL)/(L/R)",
    ]
    y = 84
    dy = 52
    for a, b in zip(stepsL, stepsR):
        parts.append(fitbox(colL - bw / 2, y, bw, 38, a, size=13,
                            fill="#eaf0fd", stroke=NEG))
        parts.append(fitbox(colR - bw / 2, y, bw, 38, b, size=13,
                            fill="#eafaf0", stroke=FIELD))
        if y < 84 + dy * 2:
            parts.append(text(colL, y + 50, "↓", size=15, color=MUTED))
            parts.append(text(colR, y + 50, "↓", size=15, color=MUTED))
        y += dy

    # стрілки, що сходяться донизу до спільної рамки
    yj = y + 6
    parts.append(line(colL, y - 8, colL, yj, color=MUTED, sw=1.4))
    parts.append(line(colR, y - 8, colR, yj, color=MUTED, sw=1.4))
    parts.append(line(colL, yj, W / 2, yj, color=MUTED, sw=1.4))
    parts.append(line(colR, yj, W / 2, yj, color=MUTED, sw=1.4))
    parts.append(arrow(W / 2, yj, W / 2, yj + 18, color=MUTED, sw=1.6))
    # спільний підсумок
    cw = 430
    parts.append(fitbox(W / 2 - cw / 2, yj + 22, cw, 40,
                        "d(змінна)/dt = (мета − змінна) / (стала часу)",
                        size=14, bold=True, fill=FILL, stroke=INK, sw=2))

    render(os.path.join(IMG, "duality-derivation.svg"), W, H, *parts, title=title)


# ── 6. Протилежна роль резистора: послідовно гальмує, паралельно прискорює ────
def fig_resistor_role():
    W, H = 740, 320
    title = "Резистор: послідовно гальмо, паралельно прискорювач"
    parts = []

    # ── ліворуч: RC, R послідовно з C ──
    lt, lb = 95, 215
    ax, cxx = 110, 230            # резистор зверху, конденсатор знизу-праворуч
    parts.append(text(170, 56, "RC: R послідовно", size=13, bold=True, color=NEG))
    # контур: джерело(зліва) → R(верх) → C(право) → назад
    x1, x2 = 70, 290
    parts.append(line(x1, lt, x1, lb, color=INK, sw=2))           # ліва шина (джерело)
    parts.append(plus(x1, lt + 30))
    parts.append(minus(x1, lb - 30))
    parts.append(line(x1, lt, 150, lt, color=INK, sw=2))
    # резистор горизонтальний угорі
    parts.append(line(150, lt, 160, lt, color=INK, sw=2))
    zz = [(160, lt)]
    for i in range(6):
        zz.append((160 + 12 * (i + 0.5), lt + (8 if i % 2 == 0 else -8)))
    zz.append((232, lt))
    parts.append(polyline(zz, color=INK, sw=2))
    parts.append(line(232, lt, x2, lt, color=INK, sw=2))
    parts.append(text(196, lt - 12, "R", size=13, color=NEG, bold=True))
    # права гілка вниз до конденсатора
    parts.append(line(x2, lt, x2, lt + 55, color=INK, sw=2))
    parts.append(line(x2 - 16, lt + 55, x2 + 16, lt + 55, color=INK, sw=2.4))
    parts.append(line(x2 - 16, lt + 68, x2 + 16, lt + 68, color=INK, sw=2.4))
    parts.append(line(x2, lt + 68, x2, lb, color=INK, sw=2))
    parts.append(line(x1, lb, x2, lb, color=INK, sw=2))
    parts.append(text(x2 + 14, lt + 64, "C", size=13, color=NEG, bold=True, anchor="start"))
    # стрілка струму на шляху
    parts.append(arrow(175, lt, 215, lt, color=POS, sw=2))
    parts.append(text(196, lt + 22, "i на шляху", size=10, color=POS))
    parts.append(fitbox(45, lb + 18, 250, 46,
                        "більший R → менший струм →\nповільніше → τ = R·C росте з R",
                        size=11, color=NEG, fill="#eaf0fd", stroke=NEG))

    # ── праворуч: RL, R паралельно з L ──
    parts.append(text(560, 56, "RL: R паралельно", size=13, bold=True, color=FIELD))
    rt, rb = 95, 215
    bx1, bx2 = 470, 660
    rxR, rxL = 545, 625
    parts.append(line(bx1, rt, bx2, rt, color=INK, sw=2))         # верхня шина
    parts.append(line(bx1, rb, bx2, rb, color=INK, sw=2))         # нижня шина
    # джерело струму ліворуч
    parts.append(line(bx1, rt, bx1, (rt + rb) / 2 - 20, color=INK, sw=2))
    parts.append(line(bx1, (rt + rb) / 2 + 20, bx1, rb, color=INK, sw=2))
    parts.append(circle(bx1, (rt + rb) / 2, 20, fill=BG, stroke=INK, sw=2))
    parts.append(arrow(bx1, (rt + rb) / 2 + 11, bx1, (rt + rb) / 2 - 11, color=POS, sw=2))
    parts.append(text(bx1 - 26, (rt + rb) / 2 + 4, "I", size=12, color=POS, bold=True, anchor="end"))
    # резистор вертикальний
    parts.append(resistor(rxR, rt, rb, "R", lcolor=FIELD))
    # котушка вертикальна
    parts.append(coil(rxL, rt, rb, "L", lcolor=FIELD))
    parts.append(text((rxR + rxL) / 2, rt - 10, "U спільна", size=10, color=MUTED))
    parts.append(fitbox(450, rb + 18, 250, 46,
                        "більший R → вища U на L →\nшвидше → τ = L/R спадає з R",
                        size=11, color=FIELD, fill="#eafaf0", stroke=FIELD))

    render(os.path.join(IMG, "resistor-role.svg"), W, H, *parts, title=title)


if __name__ == "__main__":
    fig_parallel_rl()
    fig_natural_decay()
    fig_dual_mirror()
    fig_rise_fall()
    fig_duality_derivation()
    fig_resistor_role()
    print("OK: 6 figures ->", IMG)
