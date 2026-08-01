# -*- coding: utf-8 -*-
"""Фігури до теми «Нормальна сила».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

WT   = "#27ae60"   # вага та її складові — зелене
NRM  = "#1a1a1a"   # нормальна сила — темна
PUSH = "#c0392b"   # натиск / прискорення вгору — гаряче
COOL = "#2457d6"   # холодне (падіння, «легше»)


def poly(pts, fill="none", stroke=LINE, sw=1.5, dash=None, close=False):
    d = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts)
    if close:
        d += " Z"
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>' % (d, fill, stroke, sw, da)


def path(d, fill="none", stroke=LINE, sw=1.5):
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (d, fill, stroke, sw)


def vspring(x, y1, y2, coils=5, amp=11):
    """Вертикальна пружина-зигзаг від (x,y1) до (x,y2)."""
    lead = 10
    ya, yb = y1 + lead, y2 - lead
    dy = (yb - ya) / (coils * 2)
    pts = [(x, y1), (x, ya)]
    for i in range(coils * 2):
        xx = x - amp if i % 2 == 0 else x + amp
        pts.append((xx, ya + dy * (i + 0.5)))
    pts += [(x, yb), (x, y2)]
    return poly(pts, stroke=NRM, sw=1.7)


# ── Фігура 1: нормальна сила сама підлаштовується — стіл як цупка пружина ──────
def fig_self_adjusting():
    W, H = 1000, 520
    f = [text(W / 2, 32, "Опора — цупка пружина: прогинається на дещицю й відпихає рівно на mg",
              size=16, bold=True)]

    # ── ліва сцена: книжка на столі + сили ──
    tabY = 300
    f.append(line(100, tabY, 470, tabY, color=INK, sw=2.6))          # стільниця
    f.append(line(140, tabY, 140, tabY + 62, color=INK, sw=2.4))     # ніжки
    f.append(line(430, tabY, 430, tabY + 62, color=INK, sw=2.4))
    # книжка
    bx, by, bw, bh = 214, 250, 132, 50
    f.append(rect(bx, by, bw, bh, fill="#eef1f4", stroke=INK, sw=2))
    f.append(text(bx + bw / 2, by + bh / 2 + 5, "книжка", size=13, color=MUTED))
    # нормальна сила N угору (ліва третина книжки)
    f.append(arrow(250, tabY, 250, 172, color=NRM, sw=3.4))
    f.append(text(250, 160, "N = mg", size=14.5, bold=True, color=NRM))
    # вага mg униз (права третина)
    f.append(arrow(312, 276, 312, 398, color=WT, sw=3.4))
    f.append(text(312, 418, "вага  mg", size=14.5, bold=True, color=WT))
    # позначка місця дотику + виноска до збільшення
    f.append(circle(280, tabY, 6, fill="none", stroke=MUTED, sw=1.6))
    f.append(line(286, tabY, 540, 246, color=MUTED, sw=1.3, dash="4,4"))

    # ── права вставка: атоми-пружини зблизька ──
    px, py, pw, ph = 540, 116, 400, 268
    f.append(rect(px, py, pw, ph, fill=BG, stroke=MUTED, sw=1.5, rx=10))
    cx = px + pw / 2
    f.append(text(cx, py + 30, "поверхня зблизька: пружні зв'язки між атомами", size=13, bold=True))
    xs = [px + 42 + i * 63 for i in range(6)]
    topY, botY = py + 78, py + 196
    for xx in xs:                                   # пружини між рядами атомів
        f.append(vspring(xx, topY + 12, botY - 12, coils=4, amp=10))
    for xx in xs:                                   # атоми книжки (верх) і стола (низ)
        f.append(circle(xx, topY, 11, fill="#eef1f4", stroke=INK, sw=1.5))
        f.append(circle(xx, botY, 11, fill="#e7ebef", stroke=INK, sw=1.5))
    f.append(text(px + pw - 14, topY + 5, "книжка", size=11.5, color=MUTED, anchor="end"))
    f.append(text(px + pw - 14, botY + 5, "стіл", size=11.5, color=MUTED, anchor="end"))
    f.append(text(cx, py + ph - 18, "стиснулися на непомітну дещицю → відсіч = mg",
                  size=12.5, color=MUTED))

    # ── підсумкова рамка ──
    box, bwd, bhd = textbox(W / 2, 476,
                            "Нормальна сила сама набирає те значення, якого вимагає умова "
                            "«тіло не провалюється крізь опору»",
                            size=14, pad=12, fill="#eef7f0", stroke=WT, sw=1.6)
    f.append(box)
    render(os.path.join(IMG, "self-adjusting.svg"), W, H, *f)


# ── Фігура 2: на схилі у поверхню тисне лише mg·cosθ → N = mg·cosθ ─────────────
def fig_incline():
    W, H = 940, 520
    f = [text(W / 2, 32, "На схилі у поверхню вдавлює лише перпендикулярна частина ваги",
              size=16, bold=True)]

    A = (150, 402)               # вершина кута θ (низ-ліворуч)
    B = (772, 402)
    C = (772, 150)               # прямий кут унизу праворуч
    f.append(poly([A, B, C], fill="#eef1f4", stroke=INK, sw=2, close=True))

    dx, dy = C[0] - A[0], C[1] - A[1]
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L                       # угору по схилу
    nx, ny = -uy, ux
    if ny > 0:
        nx, ny = -nx, -ny                          # нормаль дивиться назовні (вгору)
    th = math.atan2(-dy, dx)

    # брусок на схилі
    c = (452, 268)
    c = (c[0] + nx * 22, c[1] + ny * 22)
    hh = 27
    P = [(c[0] + ux * hh + nx * hh, c[1] + uy * hh + ny * hh),
         (c[0] + ux * hh - nx * hh, c[1] + uy * hh - ny * hh),
         (c[0] - ux * hh - nx * hh, c[1] - uy * hh - ny * hh),
         (c[0] - ux * hh + nx * hh, c[1] - uy * hh + ny * hh)]
    f.append(poly(P, fill="#f4f6f8", stroke=INK, sw=2, close=True))

    Lw = 132
    wtip = (c[0], c[1] + Lw)
    comp_s = Lw * math.sin(th)                     # уздовж схилу
    comp_n = Lw * math.cos(th)                     # упоперек схилу
    # вага прямовисно вниз (підпис під вістрям, щоб не збігтися зі складовою mg·cosθ)
    f.append(arrow(c[0], c[1], wtip[0], wtip[1], color=WT, sw=3.4))
    f.append(text(wtip[0], wtip[1] + 22, "вага  mg", size=14, bold=True, color=WT))
    # складова вздовж схилу (котить униз)
    d1 = (c[0] - ux * comp_s, c[1] - uy * comp_s)
    f.append(arrow(c[0], c[1], d1[0], d1[1], color=WT, sw=2.0))
    f.append(line(d1[0], d1[1], wtip[0], wtip[1], color=MUTED, sw=1.2, dash="4,4"))
    f.append(text(d1[0] - 12, d1[1] + 20, "mg·sinθ", size=12.5, color=WT, anchor="end"))
    f.append(text(d1[0] - 12, d1[1] + 37, "котить униз", size=11.5, color=MUTED, anchor="end"))
    # складова у поверхню (вдавлює) — пунктирна, всередину
    d2 = (c[0] - nx * comp_n, c[1] - ny * comp_n)
    f.append(arrow(c[0], c[1], d2[0], d2[1], color=WT, sw=2.0))
    f.append(line(d2[0], d2[1], wtip[0], wtip[1], color=MUTED, sw=1.2, dash="4,4"))
    f.append(text(d2[0] + 16, d2[1] + 16, "mg·cosθ", size=12.5, color=WT, anchor="start"))
    f.append(text(d2[0] + 16, d2[1] + 33, "вдавлює", size=11.5, color=MUTED, anchor="start"))
    # нормальна сила назовні = mg·cosθ
    ntip = (c[0] + nx * comp_n, c[1] + ny * comp_n)
    f.append(arrow(c[0], c[1], ntip[0], ntip[1], color=NRM, sw=3.0))
    f.append(text(ntip[0] - 8, ntip[1] - 8, "N = mg·cosθ", size=13.5, bold=True, color=NRM, anchor="end"))

    # дуга кута θ
    r = 70
    a1 = (A[0] + r, A[1])
    a2 = (A[0] + r * math.cos(th), A[1] - r * math.sin(th))
    f.append(path("M %.1f %.1f A %d %d 0 0 0 %.1f %.1f" % (a1[0], a1[1], r, r, a2[0], a2[1]),
                  stroke=INK, sw=1.6))
    f.append(text(A[0] + r + 10, A[1] - 8, "θ", size=17, bold=True))

    box, bwd, bhd = textbox(W / 2, 484,
                            "у поверхню тисне лише mg·cosθ → N = mg·cosθ, менша за вагу;\n"
                            "чим крутіший схил, тим менша N (до нуля на прямовисній стіні)",
                            size=13.5, pad=12, fill="#eef7f0", stroke=WT, sw=1.5)
    f.append(box)
    render(os.path.join(IMG, "incline.svg"), W, H, *f)


# ── Фігура 3: ліфт — ваги показують N, а не mg ────────────────────────────────
def fig_elevator():
    W, H = 1050, 520
    f = [text(W / 2, 32, "Ваги показують нормальну силу N — тому уявна вага змінюється в ліфті",
              size=16, bold=True)]

    panels = [
        (60,  "спокій:  a = 0",        1.0, "N = mg",       "ваги: mg",        None,  MUTED),
        (390, "розгін угору:  a",      1.5, "N = m(g + a)", "важче",           "up",  PUSH),
        (720, "вільне падіння:  a = g", 0.0, "N = 0",        "ширяє",           "down", COOL),
    ]
    pw, ptop, ph = 270, 84, 300
    scaleY = ptop + ph - 44
    for x0, title, kN, nlab, read, adir, acol in panels:
        cx = x0 + pw / 2
        f.append(rect(x0, ptop, pw, ph, fill="#fbfcfd", stroke=MUTED, sw=1.6, rx=8))
        f.append(text(cx, ptop - 12, title, size=13.5, bold=True))
        # ваги + людина
        f.append(rect(cx - 52, scaleY, 104, 14, fill="#e7ebef", stroke=INK, sw=1.6, rx=3))
        lift = 16 if adir == "down" else 0          # у падінні тіло відірване від ваг
        f.append(rect(cx - 30, scaleY - 82 - lift, 60, 78, fill="#eef1f4", stroke=INK, sw=1.8, rx=4))
        f.append(text(cx, scaleY - 40 - lift, "m", size=20, bold=True))
        pcy = scaleY - 42 - lift
        # вага mg — стала в усіх панелях (зелена, праворуч)
        f.append(arrow(cx + 62, pcy - 6, cx + 62, pcy + 74, color=WT, sw=3.0))
        f.append(text(cx + 70, pcy + 34, "mg", size=13, bold=True, color=WT, anchor="start"))
        # нормальна сила N — ліворуч, довжина ∝ kN
        if kN > 0:
            Nlen = 60 * kN
            f.append(arrow(cx - 62, scaleY, cx - 62, scaleY - Nlen, color=NRM, sw=3.2))
            f.append(text(cx - 70, scaleY - Nlen - 8, "N", size=14, bold=True, color=NRM, anchor="end"))
        else:
            f.append(text(cx - 62, scaleY - 6, "N = 0", size=12.5, bold=True, color=COOL, anchor="middle"))
        # покажчик прискорення збоку від панелі
        axx = x0 + pw - 16
        if adir == "up":
            f.append(arrow(axx, ptop + 96, axx, ptop + 40, color=acol, sw=3.4))
            f.append(text(axx, ptop + 116, "a", size=14, bold=True, color=acol))
        elif adir == "down":
            f.append(arrow(axx, ptop + 40, axx, ptop + 96, color=acol, sw=3.4))
            f.append(text(axx, ptop + 30, "a = g", size=13, bold=True, color=acol))
        else:
            f.append(text(axx, ptop + 44, "a = 0", size=12.5, color=MUTED))
        # табло ваг
        bcol = PUSH if kN > 1.01 else (COOL if kN < 0.99 else INK)
        f.append(fitbox(cx - 78, scaleY + 26, 156, 46, nlab + "\n" + read,
                        size=13, pad=6, fill=BG, stroke=bcol, sw=1.5, bold=True, color=bcol))

    box, bwd, bhd = textbox(W / 2, 494,
                            "У спокої N = mg; при розгоні вгору N = m(g+a) — важче; "
                            "у вільному падінні N = 0 — тіло ширяє. Маса та сама, змінюється N",
                            size=13, pad=11, fill="#eef7f0", stroke=WT, sw=1.5)
    f.append(box)
    render(os.path.join(IMG, "elevator.svg"), W, H, *f)


ACC = "#2457d6"   # прискорення — холодне синє
CTR = "#c0392b"   # центр кривини, критична точка


def arcpts(cx, cy, r, a1, a2, n=64):
    """Точки дуги кола: кут відлічується від ВЕРХУ, додатний — праворуч."""
    out = []
    for i in range(n + 1):
        a = math.radians(a1 + (a2 - a1) * i / n)
        out.append((cx + r * math.sin(a), cy - r * math.cos(a)))
    return out


def arcpts_dn(cx, cy, r, a1, a2, n=64):
    """Те саме, але кут від НИЗУ (для увігнутої западини: центр зверху)."""
    out = []
    for i in range(n + 1):
        a = math.radians(a1 + (a2 - a1) * i / n)
        out.append((cx + r * math.sin(a), cy + r * math.cos(a)))
    return out


# ── Фігура 4: рецепт — N = m(a⊥ + g·cos β) ────────────────────────────────────
def fig_recipe():
    W, H = 1040, 520
    f = [text(W / 2, 34, "Нормальна сила з однієї проєкції: куди дивиться нормаль і що дозволяє в'язь",
              size=16.5, bold=True)]

    # ── ліворуч: геометрія нормалі й кут β ──
    f.append(text(280, 74, "геометрія: кут нормалі β", size=14.5, bold=True))
    A, B, Cv = (100, 398), (460, 398), (460, 190)
    f.append(poly([A, B, Cv], fill="#eef1f4", stroke=INK, sw=2, close=True))

    th = math.radians(30.0)
    ux, uy = math.cos(th), -math.sin(th)          # угору по схилу
    nx, ny = -math.sin(th), -math.cos(th)         # нормаль назовні (угору-ліворуч)
    P = (280.0, 294.0)
    pc = (P[0] + nx * 26, P[1] + ny * 26)
    h = 25.0
    f.append(poly([(pc[0] + ux * h + nx * h, pc[1] + uy * h + ny * h),
                   (pc[0] + ux * h - nx * h, pc[1] + uy * h - ny * h),
                   (pc[0] - ux * h - nx * h, pc[1] - uy * h - ny * h),
                   (pc[0] - ux * h + nx * h, pc[1] - uy * h + ny * h)],
                  fill="#f4f6f8", stroke=INK, sw=2, close=True))

    f.append(line(pc[0], pc[1], pc[0], 156, color=MUTED, sw=1.3, dash="5,4"))   # прямовисна
    f.append(arrow(pc[0], pc[1], pc[0] + nx * 118, pc[1] + ny * 118, color=NRM, sw=3.2))
    f.append(text(pc[0] + nx * 142, pc[1] + ny * 142 + 4, "N · n̂", size=15, bold=True, color=NRM))
    f.append(arrow(pc[0], pc[1], pc[0], pc[1] + 92, color=WT, sw=3.2))
    f.append(text(pc[0] + 20, pc[1] + 97, "m·g", size=14.5, bold=True, color=WT, anchor="start"))

    f.append(poly(arcpts(pc[0], pc[1], 78, -30, 0, 24), stroke=INK, sw=1.6))
    f.append(text(pc[0] + 96 * math.sin(math.radians(-15)),
                  pc[1] - 96 * math.cos(math.radians(-15)) + 5, "β", size=18, bold=True))
    f.append(text(280, 432, "β — кут між нормаллю та прямовисною", size=13, color=MUTED))

    # ── праворуч: що в'язь дозволяє для a⊥ ──
    f.append(text(784, 74, "яке a⊥ допускає в'язь", size=14.5, bold=True))
    f.append(fitbox(560, 92, 448, 72, "нерухома пряма опора\na⊥ = 0", size=14.5,
                    fill=BG, stroke=MUTED))
    f.append(fitbox(560, 180, 448, 72,
                    "опора йде з прискоренням a вздовж нормалі\na⊥ = a", size=14.5,
                    fill=BG, stroke=MUTED))
    f.append(fitbox(560, 268, 448, 94,
                    "крива опора: швидкість v, радіус кривини R\n"
                    "центр кривини з боку нормалі:  a⊥ = +v²/R\n"
                    "з протилежного боку:  a⊥ = −v²/R", size=14.5, fill=BG, stroke=MUTED))

    box, bw, bh = textbox(W / 2, 480, "N = m · ( a⊥ + g · cos β )",
                          size=22, pad=14, bold=True, fill="#eef7f0", stroke=WT, sw=1.8)
    f.append(box)
    render(os.path.join(IMG, "constraint-recipe.svg"), W, H, *f)


# ── Фігура 5: знак a⊥ задає бік центра кривини ────────────────────────────────
def fig_curvature_cases():
    W, H = 1040, 430
    f = [text(W / 2, 34, "Кривина сама диктує a⊥ — і разом із нею змінюється N",
              size=16.5, bold=True)]

    xs = [30, 370, 710]
    titles = ["Горб", "Западина", "Верх петлі (колія зверху)"]
    boxes = [
        "нормаль — угору, центр знизу\na⊥ = −v²/R,   N = m·(g − v²/R)\nвідрив при v = √(gR)",
        "нормаль — угору, центр зверху\na⊥ = +v²/R,   N = m·(g + v²/R)\nпритиск більший за вагу",
        "нормаль — униз, центр знизу\na⊥ = +v²/R,   N = m·(v²/R − g)\nвідрив при v = √(gR)",
    ]
    for i, x0 in enumerate(xs):
        cx = x0 + 160
        f.append(rect(x0, 66, 320, 226, fill="#fbfcfd", stroke=MUTED, sw=1.5, rx=8))
        f.append(text(cx, 92, titles[i], size=14, bold=True))

        if i == 0:                                   # опуклий горб
            cc, R = (cx, 272), 95
            f.append(poly(arcpts(cc[0], cc[1], R, -58, 58), stroke=INK, sw=2.6))
            f.append(rect(cx - 22, 155, 44, 22, fill="#eef1f4", stroke=INK, sw=1.8, rx=3))
            f.append(line(cx, 177, cc[0], cc[1], color=MUTED, sw=1.2, dash="4,4"))
            f.append(arrow(cx - 16, 155, cx - 16, 108, color=NRM, sw=3.0))
            f.append(text(cx - 24, 112, "N", size=14.5, bold=True, color=NRM, anchor="end"))
            f.append(arrow(cx + 42, 100, cx + 42, 148, color=ACC, sw=3.0))
            f.append(text(cx + 50, 128, "a⊥", size=14, bold=True, color=ACC, anchor="start"))
            f.append(circle(cc[0], cc[1], 4.5, fill=CTR, stroke=CTR, sw=1))
        elif i == 1:                                 # увігнута западина
            cc, R = (cx, 150), 95
            f.append(poly(arcpts_dn(cc[0], cc[1], R, -58, 58), stroke=INK, sw=2.6))
            f.append(rect(cx - 22, 223, 44, 22, fill="#eef1f4", stroke=INK, sw=1.8, rx=3))
            f.append(line(cx, 223, cc[0], cc[1], color=MUTED, sw=1.2, dash="4,4"))
            f.append(arrow(cx - 16, 223, cx - 16, 180, color=NRM, sw=3.0))
            f.append(text(cx - 24, 184, "N", size=14.5, bold=True, color=NRM, anchor="end"))
            f.append(arrow(cx + 44, 225, cx + 44, 178, color=ACC, sw=3.0))
            f.append(text(cx + 52, 200, "a⊥", size=14, bold=True, color=ACC, anchor="start"))
            f.append(circle(cc[0], cc[1], 4.5, fill=CTR, stroke=CTR, sw=1))
        else:                                        # верх петлі: колія над тілом
            cc, R = (cx, 268), 88
            f.append(poly(arcpts(cc[0], cc[1], R, -58, 58), stroke=INK, sw=2.6))
            f.append(rect(cx - 22, 184, 44, 22, fill="#eef1f4", stroke=INK, sw=1.8, rx=3))
            f.append(line(cx, 206, cc[0], cc[1], color=MUTED, sw=1.2, dash="4,4"))
            f.append(arrow(cx - 16, 206, cx - 16, 248, color=NRM, sw=3.0))
            f.append(text(cx - 24, 252, "N", size=14.5, bold=True, color=NRM, anchor="end"))
            f.append(arrow(cx + 44, 206, cx + 44, 250, color=ACC, sw=3.0))
            f.append(text(cx + 52, 232, "a⊥", size=14, bold=True, color=ACC, anchor="start"))
            f.append(circle(cc[0], cc[1], 4.5, fill=CTR, stroke=CTR, sw=1))

        f.append(fitbox(x0 + 8, 300, 304, 70, boxes[i], size=13, fill=BG, stroke=MUTED))

    f.append(text(W / 2, 406,
                  "Центр кривини з того боку, куди дивиться нормаль → a⊥ = +v²/R; "
                  "з протилежного → a⊥ = −v²/R", size=13, color=MUTED))
    render(os.path.join(IMG, "curvature-cases.svg"), W, H, *f)


# ── Фігура 6: увігнута петля проти опуклого купола ────────────────────────────
def fig_concave_convex():
    W, H = 1040, 560
    f = [text(W / 2, 34, "Та сама алгебра з двома знаками: петля зсередини й купол іззовні",
              size=16.5, bold=True)]

    # ── ліворуч: мертва петля на найменшій швидкості ──
    f.append(text(270, 74, "мертва петля, найменша можлива швидкість", size=14, bold=True))
    lc, R = (270.0, 310.0), 118.0
    f.append(poly(arcpts(lc[0], lc[1], R, 0, 360), stroke=INK, sw=3.0, close=True))
    f.append(line(lc[0], lc[1], lc[0], lc[1] - R, color=MUTED, sw=1.2, dash="5,4"))
    a60 = math.radians(60)
    f.append(line(lc[0], lc[1], lc[0] + R * math.sin(a60), lc[1] - R * math.cos(a60),
                  color=MUTED, sw=1.2, dash="5,4"))
    f.append(poly(arcpts(lc[0], lc[1], 44, 0, 60, 20), stroke=INK, sw=1.5))
    f.append(text(lc[0] + 60 * math.sin(math.radians(30)),
                  lc[1] - 60 * math.cos(math.radians(30)) + 5, "θ", size=17, bold=True))

    for ang, k, lab, lx, ly, anc in [(0, 0.0, "N = 0", 270, 172, "middle"),
                                     (60, 1.5, "1.5 mg", 0, 0, "start"),
                                     (120, 4.5, "4.5 mg", 0, 0, "start"),
                                     (180, 6.0, "6 mg", 270, 454, "middle")]:
        a = math.radians(ang)
        px, py = lc[0] + R * math.sin(a), lc[1] - R * math.cos(a)
        ox, oy = math.sin(a), -math.cos(a)                    # назовні
        f.append(circle(px, py, 9, fill="#eef1f4", stroke=INK, sw=1.8))
        if k > 0:
            f.append(arrow(px, py, px - ox * 15 * k, py - oy * 15 * k, color=NRM, sw=3.0))
        if anc == "start":
            lx, ly = px + ox * 26, py + oy * 26 + 5
        f.append(text(lx, ly, lab, size=13.5, bold=True,
                      color=(CTR if k == 0 else NRM), anchor=anc))

    box, bw, bh = textbox(270, 520, "N(θ) = 3mg · (1 − cos θ)", size=17, pad=12,
                          bold=True, fill="#eef7f0", stroke=WT, sw=1.6)
    f.append(box)

    # ── праворуч: куля з'їжджає з купола ──
    f.append(text(770, 74, "куля з'їжджає з купола, старт зі спокою", size=14, bold=True))
    dc, Rd = (770.0, 430.0), 150.0
    f.append(poly(arcpts(dc[0], dc[1], Rd, -78, 78), stroke=INK, sw=3.0))
    f.append(line(dc[0], dc[1], dc[0], dc[1] - Rd, color=MUTED, sw=1.2, dash="5,4"))
    arel = math.radians(48.19)
    px_r, py_r = dc[0] + Rd * math.sin(arel), dc[1] - Rd * math.cos(arel)
    f.append(line(dc[0], dc[1], px_r, py_r, color=MUTED, sw=1.2, dash="5,4"))
    f.append(poly(arcpts(dc[0], dc[1], 64, 0, 48.19, 20), stroke=INK, sw=1.5))
    f.append(text(dc[0] + 92 * math.sin(math.radians(24)),
                  dc[1] - 92 * math.cos(math.radians(24)) + 5, "48.2°", size=13.5, bold=True))

    for ang, lab, anc in [(0, "N = mg", "middle"), (20, "0.82 mg", "start"),
                          (35, "0.46 mg", "start")]:
        a = math.radians(ang)
        px, py = dc[0] + Rd * math.sin(a), dc[1] - Rd * math.cos(a)
        ox, oy = math.sin(a), -math.cos(a)
        ln = 40 * (3 * math.cos(a) - 2)
        f.append(circle(px, py, 9, fill="#eef1f4", stroke=INK, sw=1.8))
        f.append(arrow(px, py, px + ox * ln, py + oy * ln, color=NRM, sw=3.0))
        lx, ly = px + ox * (ln + 18), py + oy * (ln + 18) + 4
        f.append(text(lx, ly, lab, size=13.5, bold=True, color=NRM, anchor=anc))

    f.append(circle(px_r, py_r, 8, fill=BG, stroke=CTR, sw=2.6))
    fly = []                                   # вільний політ після відриву
    p0, p1, p2 = (px_r + 8, py_r + 8), (928.0, 352.0), (952.0, 404.0)
    for i in range(25):
        t = i / 24.0
        fly.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
                    (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]))
    f.append(poly(fly, stroke=CTR, sw=1.6, dash="6,5"))
    f.append(fitbox(838, 424, 178, 52, "N = 0\nвідрив на 48.2°", size=13,
                    fill=BG, stroke=CTR, color=CTR, bold=True))

    box2, bw2, bh2 = textbox(700, 520, "N(α) = mg · (3·cos α − 2)", size=17, pad=12,
                             bold=True, fill="#eef7f0", stroke=WT, sw=1.6)
    f.append(box2)
    render(os.path.join(IMG, "concave-convex.svg"), W, H, *f)


if __name__ == "__main__":
    fig_self_adjusting()
    fig_incline()
    fig_elevator()
    fig_recipe()
    fig_curvature_cases()
    fig_concave_convex()
    print("OK: figs written to", IMG)


# ═══ Фігури до вставки «Чому тверде тіло непроникне» ═══════════════════════════

def fig_solidity_timeline():
    """Часова смуга: як питання про непроникність здобувало відповідь."""
    rows = [
        ("1687", "Ісаак Ньютон, «Начала»",
                 "непроникність оголошено первинною властивістю тіл"),
        ("1758", "Руджер Бошкович, «Теорія натуральної філософії»",
                 "дотику немає: відсіч росте без меж, тіла не стикаються"),
        ("1842", "Семюел Ерншоу",
                 "самі кулонівські сили не дають стійкої рівноваги"),
        ("1873", "Йоганнес ван дер Ваальс",
                 "тверду серцевину молекули вставлено в теорію руками"),
        ("1911", "Ернест Резерфорд",
                 "атом майже порожній — а речовина далі непроникна"),
        ("1913–1927", "Нільс Бор, Вернер Гайзенберг",
                 "невизначеність дає атомові розмір, але не дає твердості"),
        ("1925", "Вольфганг Паулі",
                 "заборона на однаковий стан; ішлося про спектри, не твердість"),
        ("1926", "Енріко Фермі, Поль Дірак, Ральф Фаулер",
                 "заборона обертається тиском: він тримає білого карлика"),
        ("1931", "Пауль Еренфест",
                 "питання названо прямо: чому камінь такий об'ємистий?"),
        ("1967", "Фрімен Дайсон і Ендрю Ленард",
                 "доведено: з ферміонами E ≥ −C·N, з бозонами — колапс"),
        ("1975", "Елліотт Ліб і Вальтер Тіррінг",
                 "коротке доведення; стала падає з 10¹⁴ приблизно до 5"),
    ]
    W, H = 1060, 1020
    f = [text(W / 2, 40, "Три століття питання «чому тверде не проходить крізь тверде»",
              size=17, bold=True)]
    xl, y0, step = 258, 122, 82
    f.append(line(xl, y0 - 44, xl, y0 + step * (len(rows) - 1) + 44,
                  color=MUTED, sw=2.2, dash="6 7"))
    for i, (year, who, claim) in enumerate(rows):
        cy = y0 + step * i
        f.append(text(xl - 30, cy + 6, year, size=16, bold=True))
        f.append(circle(xl, cy, 8, fill=BG, stroke=INK, sw=2.4))
        f.append(fitbox(xl + 26, cy - 33, 740, 66, who + "\n" + claim,
                        size=14, pad=10, fill=FILL, stroke=LINE, sw=1.4))
    render(os.path.join(IMG, "solidity-timeline.svg"), W, H, *f)


def _hump(cx, base, amp, w, x1, x2, color, sw=2.6):
    """Одногорба хвильова функція (без вузла) на осі base."""
    pts = []
    n = 90
    for i in range(n + 1):
        x = x1 + (x2 - x1) * i / n
        u = (x - cx) / w
        pts.append((x, base - amp * math.exp(-u * u)))
    return poly(pts, stroke=color, sw=sw)


def _node_wave(cx, base, amp, w, x1, x2, color, sw=2.6):
    """Непарна хвильова функція з вузлом у cx."""
    pts = []
    n = 120
    k = 1.6487  # нормування: пік u·exp(−u²/2) при u = 1
    for i in range(n + 1):
        x = x1 + (x2 - x1) * i / n
        u = (x - cx) / w
        pts.append((x, base - amp * k * u * math.exp(-u * u / 2.0)))
    return poly(pts, stroke=color, sw=sw)


def fig_solidity_exclusion_cost():
    """Чому накладання хмар коштує кінетичної енергії."""
    W, H = 1020, 566
    f = [text(W / 2, 38, "Ціна спільного простору: заборона Паулі викреслює стани",
              size=17, bold=True)]

    base, ntop = 265, 368          # рівень хвильової функції та рівень ядер
    panels = [(40, 450, "Атоми окремо"), (530, 450, "Хмари наклалися")]
    for px, pw, ttl in panels:
        f.append(rect(px, 80, pw, 320, fill="#fbfcfd", stroke=MUTED, sw=1.4))
        f.append(text(px + pw / 2, 68, ttl, size=15, bold=True))
        f.append(line(px + 16, base, px + pw - 16, base, color=MUTED, sw=1.2, dash="4 5"))

    # ── ліва панель: два далекі атоми, кожен у своєму найнижчому стані ──
    f.append(_hump(150, base, 88, 46, 60, 250, NEG))
    f.append(_hump(380, base, 88, 46, 290, 480, NEG))
    f.append(plus(150, ntop, 11))
    f.append(plus(380, ntop, 11))
    f.append(text(150, 152, "атом A", size=13, color=MUTED))
    f.append(text(380, 152, "атом B", size=13, color=MUTED))

    # ── права панель: спільна яма, найнижчий стан зайнятий ──
    cxm = 755
    f.append(_hump(cxm, base, 74, 88, 545, 965, NEG))
    f.append(_node_wave(cxm, base, 68, 62, 545, 965, POS))
    f.append(plus(690, ntop, 11))
    f.append(plus(820, ntop, 11))
    f.append(line(cxm, 175, cxm, 350, color=INK, sw=1.4, dash="5 5"))
    f.append(text(cxm, 166, "вузол", size=13, bold=True))

    # ── легенда правої панелі (два рядки, ліворуч угорі) ──
    lx, ly = 548, 112
    f.append(line(lx, ly - 4, lx + 34, ly - 4, color=NEG, sw=3.0))
    f.append(text(lx + 44, ly, "найнижчий стан — уже зайнятий", size=13, anchor="start"))
    f.append(line(lx, ly + 26, lx + 34, ly + 26, color=POS, sw=3.0))
    f.append(text(lx + 44, ly + 30, "стан із вузлом — дорожчий", size=13, anchor="start"))

    f.append(fitbox(40, 416, 450, 76,
                    "Далеко один від одного кожен електрон сидить\n"
                    "у найнижчому стані свого атома — вигин найменший",
                    size=13, pad=10, fill="#eaf0fd", stroke=NEG, sw=1.4))
    f.append(fitbox(530, 416, 450, 76,
                    "Хмари наклалися: найнижчий стан уже зайнятий, тож\n"
                    "другий електрон іде у стан із вузлом — вигин крутіший,\n"
                    "а кінетична енергія стрибає",
                    size=13, pad=10, fill="#fdecea", stroke=POS, sw=1.4))

    box, bw, bh = textbox(W / 2, 528,
                          "Нової сили не з'явилося — просто половина станів стала недосяжною, "
                          "і за спільний простір платять кінетичною енергією",
                          size=13, pad=11, fill=FILL, stroke=LINE, sw=1.4)
    f.append(box)
    render(os.path.join(IMG, "solidity-exclusion-cost.svg"), W, H, *f)


# Окремий блок запуску для фігур цієї вставки: головний блок вище стоїть
# посеред файлу, а ці функції означені після нього.
if __name__ == "__main__":
    fig_solidity_timeline()
    fig_solidity_exclusion_cost()
    print("OK: solidity figs written to", IMG)

# ═══ Фігури до вставки «Як рушій рахує силу контакту» ═══════════════


def fig_contact_solver_frame():
    """Один кадр розв'язувача: вільний крок → умова → поштовх → сила."""
    W, H = 1080, 560
    f = []

    pw, gap, x0, ytop, ph = 238, 20, 30, 58, 250
    xs = [x0 + i * (pw + gap) for i in range(4)]
    heads = ["1 · вільний крок", "2 · умова в'язі", "3 · поштовх", "4 · сила"]
    tints = ["#eaf0fd", "#f4f6f8", "#fdecea", "#eafaf0"]
    edges = [NEG, MUTED, POS, WT]

    for i, x in enumerate(xs):
        f.append(rect(x, ytop, pw, ph, fill=BG, stroke=edges[i], sw=1.6))
        f.append(rect(x, ytop, pw, 34, fill=tints[i], stroke=edges[i], sw=1.6))
        f.append(text(x + pw / 2, ytop + 23, heads[i], size=14, bold=True, color=edges[i]))

    # ── панель 1: тіло вже в підлозі ──
    x = xs[0]
    fy = ytop + 128
    f.append(line(x + 22, fy, x + pw - 22, fy, color=INK, sw=2.6))
    f.append(rect(x + 78, fy - 30, 82, 44, fill="#eef1f4", stroke=INK, sw=1.8))
    f.append(arrow(x + 119, ytop + 52, x + 119, ytop + 88, color=NEG, sw=2.6))
    f.append(text(x + 119, fy + 30, "перекриття d", size=12, color=MUTED))
    f.append(mtext(x + pw / 2, ytop + 190,
                   ["v ← v − g·Δt", "v*ₙ = −0.163 м/с", "тіло рухається в опору"],
                   size=13, lh=1.5))

    # ── панель 2: трійця умов ──
    x = xs[1]
    f.append(mtext(x + pw / 2, ytop + 84,
                   ["vₙ′ ≥ 0", "λ ≥ 0", "λ · vₙ′ = 0"], size=17, lh=1.7, bold=True))
    f.append(mtext(x + pw / 2, ytop + 190,
                   ["не рухатися в опору,", "опора лише штовхає,", "або дотик, або нуль"],
                   size=13, lh=1.5, color=MUTED))

    # ── панель 3: поштовх ──
    x = xs[2]
    fy = ytop + 128
    f.append(line(x + 22, fy, x + pw - 22, fy, color=INK, sw=2.6))
    f.append(rect(x + 78, fy - 44, 82, 44, fill="#eef1f4", stroke=INK, sw=1.8))
    f.append(arrow(x + 119, fy, x + 119, ytop + 60, color=POS, sw=3.0))
    f.append(text(x + 150, ytop + 74, "λ", size=16, bold=True, color=POS, anchor="start"))
    f.append(mtext(x + pw / 2, ytop + 190,
                   ["λ = max(0, −mₑ·v*ₙ)", "= 6 · 0.163", "= 0.98 Н·с"],
                   size=13, lh=1.5))

    # ── панель 4: сила ──
    x = xs[3]
    fy = ytop + 128
    f.append(line(x + 22, fy, x + pw - 22, fy, color=INK, sw=2.6))
    f.append(rect(x + 78, fy - 44, 82, 44, fill="#eef1f4", stroke=INK, sw=1.8))
    f.append(arrow(x + 100, fy, x + 100, ytop + 60, color=NRM, sw=3.0))
    f.append(text(x + 74, ytop + 74, "N", size=15, bold=True, color=NRM, anchor="end"))
    f.append(arrow(x + 138, fy - 44, x + 138, ytop + 118, color=WT, sw=3.0))
    f.append(text(x + 164, ytop + 112, "mg", size=15, bold=True, color=WT, anchor="start"))
    f.append(mtext(x + pw / 2, ytop + 190,
                   ["N = λ/Δt", "= 0.98 · 60", "= 58.8 Н = mg"],
                   size=13, lh=1.5))

    # ── стрілки між панелями ──
    for i in range(3):
        ax = xs[i] + pw + 2
        f.append(arrow(ax, ytop + ph / 2, ax + gap - 4, ytop + ph / 2, color=MUTED, sw=2.0))

    # ── три випадки з тим самим кодом ──
    cw, cgap = 330, 25
    cx0 = (W - (3 * cw + 2 * cgap)) / 2
    cases = [("рівна підлога", "v*ₙ = −g·Δt", "N = 58.8 Н = mg"),
             ("схил 30°", "v*ₙ = −g·Δt·cos30°", "N = 50.9 Н = mg·cos30°"),
             ("підлога ліфта, a = 2 м/с²", "v*ₙ = −(g+a)·Δt", "N = 70.8 Н = m(g+a)")]
    for i, (a, b, c) in enumerate(cases):
        cx = cx0 + i * (cw + cgap)
        f.append(rect(cx, 344, cw, 96, fill=FILL, stroke=LINE, sw=1.4))
        f.append(text(cx + cw / 2, 370, a, size=13.5, bold=True))
        f.append(text(cx + cw / 2, 396, b, size=13, color=MUTED))
        f.append(text(cx + cw / 2, 424, c, size=14, bold=True, color=NRM))

    box, bw, bh = textbox(W / 2, 486,
                          "У коді немає ні cos θ, ні (g + a): косинус дає проєкція на нахилену нормаль,\n"
                          "а (g + a) — те, що підлога ліфта за той самий крок теж набирає швидкості",
                          size=13.5, pad=12, fill="#eafaf0", stroke=WT, sw=1.4)
    f.append(box)

    render(os.path.join(IMG, "contact-solver-frame.svg"), W, H, *f,
           title="Один кадр: рушій не знає mg — він гасить рух, який тіло встигло зробити в опору")


def fig_pgs_stack():
    """Стос із трьох ящиків: збіжність послідовних поштовхів і теплий старт."""
    W, H = 1080, 560
    f = []

    # ── ліворуч: стос і три контакти ──
    gy = 400
    f.append(line(52, gy, 330, gy, color=INK, sw=3.0))
    for i in range(6):
        f.append(line(60 + i * 46, gy, 46 + i * 46, gy + 16, color=MUTED, sw=1.4))
    bw, bh, bx = 118, 60, 92
    labels = [("λ₀", "3mg = 29.4 Н", NRM), ("λ₁", "2mg = 19.6 Н", NRM), ("λ₂", "mg = 9.8 Н", NRM)]
    for i in range(3):
        by = gy - (i + 1) * bh
        f.append(rect(bx, by, bw, bh, fill="#eef1f4", stroke=INK, sw=1.8))
        f.append(text(bx + bw / 2, by + bh / 2 + 5, "1 кг", size=13, color=MUTED))
        cy = gy - i * bh
        f.append(line(bx - 14, cy, bx + bw + 14, cy, color=POS, sw=2.2, dash="5 4"))
        f.append(arrow(bx + bw + 22, cy, bx + bw + 46, cy, color=POS, sw=1.8))
        f.append(text(bx + bw + 54, cy - 8, labels[i][0], size=15, bold=True,
                      color=POS, anchor="start"))
        f.append(text(bx + bw + 54, cy + 14, labels[i][1], size=13,
                      color=labels[i][2], anchor="start"))
    f.append(text(200, 168, "три контакти,", size=13.5, color=MUTED))
    f.append(text(200, 190, "кожен псує сусідній", size=13.5, color=MUTED))

    # ── праворуч: збіжність сили під низом ──
    gx0, gx1, gy0, gy1 = 600, 1010, 430, 130      # gy0 — нуль, gy1 — верх шкали
    NMAX = 32.0
    def sy(v):
        return gy0 - (gy0 - gy1) * v / NMAX
    f.append(line(gx0, gy0, gx1, gy0, color=INK, sw=1.8))
    f.append(line(gx0, gy0, gx0, gy1, color=INK, sw=1.8))
    for v in (0, 10, 20, 30):
        f.append(line(gx0 - 6, sy(v), gx0, sy(v), color=INK, sw=1.4))
        f.append(text(gx0 - 12, sy(v) + 5, str(v), size=12, color=MUTED, anchor="end"))
    f.append(text(gx0 - 44, sy(16) + 5, "N₀, Н", size=13, color=MUTED, anchor="middle"))

    cold = [9.800, 14.700, 18.375, 21.131, 23.198, 24.749]
    px = [gx0 + 34 + i * 62 for i in range(6)]
    for i, x in enumerate(px):
        f.append(line(x, gy0, x, gy0 + 6, color=INK, sw=1.4))
        f.append(text(x, gy0 + 24, str(i + 1), size=12, color=MUTED))
    f.append(text((gx0 + gx1) / 2, gy0 + 48, "прохід розв'язувача за кадр", size=13, color=MUTED))

    ty = sy(29.4)
    f.append(line(gx0, ty, gx1, ty, color=MUTED, sw=1.4, dash="6 5"))
    f.append(text(gx1, ty - 10, "точна відповідь 3mg = 29.4 Н", size=12.5,
                  color=MUTED, anchor="end"))

    f.append(poly([(x, sy(v)) for x, v in zip(px, cold)], stroke=POS, sw=2.6))
    for x, v in zip(px, cold):
        f.append(circle(x, sy(v), 4.5, fill=POS, stroke=POS, sw=1.2))
    f.append(text(px[-1] + 12, sy(cold[-1]) + 5, "холодний старт", size=13,
                  color=POS, anchor="start"))

    f.append(poly([(px[0], ty), (px[-1], ty)], stroke=WT, sw=2.8))
    for x in px:
        f.append(circle(x, ty, 4.5, fill=WT, stroke=WT, sw=1.2))
    f.append(text(px[0] - 10, ty - 14, "теплий старт: λ з минулого кадру",
                  size=13, color=WT, anchor="start"))

    box, bw2, bh2 = textbox(W / 2, 500,
                            ["Гаусс–Зейдель локальний: за прохід звістка про вагу згори опускається на один контакт.",
                             "У стосі з десяти ящиків холодний розв'язувач за 8 проходів доводить силу під низом",
                             "лише до 31 % справжньої — тому теплий старт не оптимізація, а умова того, що стос стоїть"],
                            size=13, pad=12, fill=FILL, stroke=LINE, sw=1.4)
    f.append(box)

    render(os.path.join(IMG, "pgs-stack.svg"), W, H, *f,
           title="Послідовні поштовхи: скільки проходів треба, щоб підлога дізналася вагу стосу")


if __name__ == "__main__":
    fig_contact_solver_frame()
    fig_pgs_stack()
    print("OK: contact-solver figs written to", IMG)
