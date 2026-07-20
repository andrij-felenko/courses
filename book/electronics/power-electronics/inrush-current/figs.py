# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def box(cx, cy, s, **kw):
    body, _, _ = textbox(cx, cy, s, **kw)
    return body


def poly(pts, color=INK, sw=2.6, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" '
            'stroke-width="%.1f"%s/>' % (p, color, sw, d))


def polyfill(pts, fill=FIELD, stroke=None, sw=2.4, op=0.14, dash=None):
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    st = stroke if stroke else fill
    return ('<polygon points="%s" fill="%s" fill-opacity="%.2f" stroke="%s" '
            'stroke-width="%.1f"%s/>' % (p, fill, op, st, sw, d))


def cap(cx, cy, lead=18, gap=9, plate=30, color=INK, sw=2.4):
    out = [line(cx, cy - lead - gap / 2, cx, cy - gap / 2, color=color, sw=sw),
           line(cx - plate / 2, cy - gap / 2, cx + plate / 2, cy - gap / 2, color=color, sw=sw),
           line(cx - plate / 2, cy + gap / 2, cx + plate / 2, cy + gap / 2, color=color, sw=sw),
           line(cx, cy + gap / 2, cx, cy + lead + gap / 2, color=color, sw=sw)]
    return "".join(out)


def gnd(cx, cy, w=24, color=INK, sw=2.2):
    out = [line(cx, cy, cx, cy + 9, color=color, sw=sw)]
    yy = cy + 9
    for i, ww in enumerate((w, w * 0.6, w * 0.25)):
        out.append(line(cx - ww / 2, yy + i * 5, cx + ww / 2, yy + i * 5, color=color, sw=sw))
    return "".join(out)


def battery(cx, top, bot, color=INK, sw=2.4):
    y1 = (top + bot) / 2 - 6
    y2 = y1 + 12
    out = [line(cx, top, cx, y1, color=color, sw=sw),
           line(cx - 17, y1, cx + 17, y1, color=color, sw=sw),          # +
           line(cx - 8, y2, cx + 8, y2, color=color, sw=sw),            # −
           line(cx, y2, cx, bot, color=color, sw=sw)]
    return "".join(out)


def switch_open(x1, x2, y, color=INK, sw=2.4):
    """Розімкнений вимикач між x1 і x2 на висоті y."""
    a = x1 + 8
    b = x2 - 8
    out = [line(x1, y, a, y, color=color, sw=sw),
           circle(a, y, 3.2, fill=color, stroke=color),
           line(a, y, b - 4, y - 18, color=color, sw=sw),               # важіль
           circle(b, y, 3.2, fill=color, stroke=color),
           line(b, y, x2, y, color=color, sw=sw)]
    return "".join(out)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 1 — коло (джерело→ключ→R→розряджений C) + форма струму в часі
# ─────────────────────────────────────────────────────────────────────────────
def fig_spike():
    W, H = 1000, 470
    f = []
    f.append(line(495, 62, 495, 430, color=MUTED, sw=1.4, dash="3 6"))
    f.append(text(255, 60, "коло", size=14.5, color=MUTED, bold=True))
    f.append(text(745, 60, "струм у часі", size=14.5, color=MUTED, bold=True))

    # ── ліворуч: коло ──
    topY, botY = 170, 340
    srcX = 105
    f.append(battery(srcX, topY, botY))
    f.append(text(srcX - 30, (topY + botY) / 2 + 4, "V", size=14, color=INK, anchor="end", bold=True))
    f.append(text(srcX - 30, (topY + botY) / 2 + 22, "5 В", size=12, color=MUTED, anchor="end"))

    # верхній провід: ключ, R, вузол
    f.append(line(srcX, topY, 160, topY, color=INK, sw=2.2))
    f.append(switch_open(160, 232, topY))
    f.append(text(196, topY - 30, "вимикач", size=12, color=INK, anchor="middle"))
    f.append(line(232, topY, 288, topY, color=INK, sw=2.2))
    f.append(rect(288, topY - 15, 74, 30, fill="#fff5f5", stroke=POS, sw=1.8))
    f.append(text(325, topY + 5, "R", size=13.5, color=POS, anchor="middle", bold=True))
    f.append(text(325, topY - 26, "ESR + доріжки ≈ 0.1 Ом", size=11.5, color=POS, anchor="middle"))
    f.append(line(362, topY, 420, topY, color=INK, sw=2.2))

    # вузол → конденсатор → нижній провід
    nodeX = 420
    f.append(circle(nodeX, topY, 3.4, fill=INK, stroke=INK))
    f.append(cap(nodeX, topY + 58, lead=16, gap=10, plate=34))
    f.append(text(nodeX + 20, topY + 50, "C = 470 мкФ", size=12, color=INK, anchor="start"))
    f.append(text(nodeX + 20, topY + 68, "розряджений: 0 В", size=11.5, color=NEG, anchor="start"))
    f.append(line(nodeX, topY + 84, nodeX, botY, color=INK, sw=2.2))
    f.append(line(srcX, botY, nodeX, botY, color=INK, sw=2.2))

    # кидок струму — червона стрілка вздовж верхнього проводу
    f.append(arrow(250, topY - 48, 285, topY - 48, color=POS, sw=3.2))
    f.append(text(250, topY - 56, "iпік ≈ V/R", size=12.5, color=POS, anchor="middle", bold=True))

    # ── праворуч: I(t) ──
    ox, oy = 555, 375
    rgt, topA = 925, 130
    f.append(arrow(ox, oy, rgt, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, topA, color=INK, sw=1.8))
    f.append(text(rgt, oy + 22, "час", size=12, color=INK, anchor="end"))
    f.append(text(ox + 4, topA - 8, "струм", size=12, color=INK, anchor="start"))

    PW = rgt - ox - 20
    peakY, issFrac = 150.0, 0.03

    def yf(frac):
        return oy - frac * (oy - peakY)

    def xt(tu):
        return ox + (tu / 5.0) * PW

    # крива спаду
    pts = []
    N = 120
    for k in range(N + 1):
        tu = 5.0 * k / N
        frac = issFrac + (1.0 - issFrac) * math.exp(-tu)
        pts.append((xt(tu), yf(frac)))
    # заливка під піком (заряд)
    fillpts = [(ox, oy)] + pts + [(xt(5.0), oy)]
    f.append(polyfill(fillpts, FIELD, None, sw=0, op=0.12))
    # вертикальний фронт t=0 і сама крива
    f.append(line(ox, oy, ox, yf(1.0), color=POS, sw=2.8))
    f.append(poly(pts, color=POS, sw=2.8))

    # Iпік
    f.append(line(ox, peakY, xt(0.0) + 6, peakY, color=MUTED, sw=1.2, dash="4 5"))
    f.append(text(ox + 14, peakY - 8, "Iпік = V/R = 50 А", size=12.5, color=POS, anchor="start", bold=True))
    # робочий струм
    workY = yf(issFrac)
    f.append(line(xt(1.6), workY, rgt - 6, workY, color=NEG, sw=1.6))
    f.append(text(rgt - 6, workY - 8, "Iроб = 0.5 А", size=12, color=NEG, anchor="end"))
    # τ на осі
    f.append(line(xt(1.0), oy, xt(1.0), oy + 7, color=INK, sw=1.5))
    f.append(text(xt(1.0), oy + 22, "τ = R·C", size=12, color=INK, anchor="middle"))
    f.append(text(xt(2.9), yf(0.45), "спад за експонентою", size=12, color=MUTED, anchor="middle"))
    f.append(text(xt(2.9), yf(0.30), "(площа = влитий заряд)", size=11, color=MUTED, anchor="middle"))

    render(os.path.join(IMG, "inrush-spike.svg"), W, H, *f,
           title="Кидок при зарядженні вхідного конденсатора")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 2 — три механізми одного симптому
# ─────────────────────────────────────────────────────────────────────────────
def fig_three():
    W, H = 1120, 470
    f = []
    PW = 350
    x0 = [30, 30 + 360, 30 + 720]
    titles = ["Конденсатор", "Трансформатор", "Навантаження"]
    for i, x in enumerate(x0):
        f.append(rect(x, 60, PW, 380, fill=BG, stroke=MUTED, sw=1.5, rx=10))
        f.append(text(x + PW / 2, 92, titles[i], size=16, bold=True))

    # ── Панель A: розряджений конденсатор ≈ коротке ──
    ax = x0[0] + PW / 2
    f.append(cap(ax, 190, lead=22, gap=13, plate=52, sw=3))
    f.append(text(ax, 245, "0 В — розряджений", size=12.5, color=NEG, anchor="middle"))
    f.append(arrow(ax - 95, 165, ax - 40, 165, color=POS, sw=3.2))
    f.append(text(ax - 68, 150, "великий i", size=12.5, color=POS, anchor="middle", bold=True))
    f.append(fitbox(x0[0] + 24, 300, PW - 48, 112,
                    ["i = C·dV/dt.", "Напруга не стрибає миттєво,",
                     "тож у першу мить розряджений",
                     "конденсатор бере струм як",
                     "коротке замикання."],
                    size=13, pad=12))

    # ── Панель B: потік ×2 → насичення ──
    bx = x0[1]
    ox, oy = bx + 55, 250
    rgt, topB = bx + PW - 30, 120
    # смуга насичення
    satY = 150
    f.append(rect(ox, topB, rgt - ox, satY - topB, fill="#fdecea", stroke="#fdecea", sw=0))
    f.append(text(rgt - 6, topB + 18, "насичення", size=11.5, color=POS, anchor="end", bold=True))
    f.append(arrow(ox, oy, rgt, oy, color=INK, sw=1.6))
    f.append(arrow(ox, oy + 42, ox, topB, color=INK, sw=1.6))
    f.append(text(ox - 8, topB + 2, "потік φ", size=11.5, color=INK, anchor="end"))
    f.append(text(rgt, oy + 18, "час", size=11, color=INK, anchor="end"))

    def bx_t(u):
        return ox + u * (rgt - ox) / 6.0

    def by_phi(p):  # p у частках нормального піку; 2 → рівень насичення
        return oy - (p / 2.0) * (oy - satY)

    # нормальний потік (пунктир, амплітуда 1, навколо нуля — тут показуємо |φ| хвилею вгору)
    npts = [(bx_t(u), by_phi(1.0 * (1 - math.cos(u * math.pi / 3.0)) / 1.0)) for u in [x * 0.1 for x in range(0, 61)]]
    # інраш-потік: стартує з 0, за півперіоду до 2×
    ipts = []
    for j in range(0, 61):
        u = j * 0.1
        p = 1.0 - math.cos(u * math.pi / 3.0)   # 0→2 за u=3 (півперіоду)
        ipts.append((bx_t(u), by_phi(p)))
    f.append(poly([(bx_t(u), by_phi(1.0)) for u in (0.0, 6.0)], color=MUTED, sw=1.6, dash="5 5"))
    f.append(text(bx_t(4.4), by_phi(1.0) - 8, "норма ×1", size=11, color=MUTED, anchor="middle"))
    f.append(poly(ipts, color=POS, sw=3.0))
    f.append(text(bx_t(3.0), by_phi(2.0) - 12, "×2", size=13, color=POS, anchor="middle", bold=True))
    f.append(fitbox(bx + 24, 300, PW - 48, 112,
                    ["Увімкнення в нулі напруги:",
                     "потік стартує з нуля й росте",
                     "вдвічі — осердя насичується,",
                     "індуктивність обвалюється,",
                     "струм намагнічування злітає."],
                    size=13, pad=12))

    # ── Панель C: холодна нитка / нерухомий ротор ──
    cx = x0[2] + PW / 2
    # лампа-нитка (зигзаг у колі)
    lx = cx - 70
    f.append(circle(lx, 175, 30, fill=FILL, stroke=INK, sw=2))
    zz = []
    for j in range(7):
        zz.append((lx - 18 + j * 6, 175 + (10 if j % 2 else -10)))
    f.append(poly(zz, color=POS, sw=2.4))
    f.append(text(lx, 228, "холодна нитка", size=11.5, color=INK, anchor="middle"))
    f.append(text(lx, 245, "R мале", size=11.5, color=POS, anchor="middle", bold=True))
    # мотор
    mx = cx + 70
    f.append(circle(mx, 175, 30, fill=FILL, stroke=INK, sw=2))
    f.append(text(mx, 181, "M", size=22, color=INK, anchor="middle", bold=True))
    f.append(text(mx, 228, "нерухомий ротор", size=11.5, color=INK, anchor="middle"))
    f.append(text(mx, 245, "протиЕРС = 0", size=11.5, color=POS, anchor="middle", bold=True))
    f.append(fitbox(x0[2] + 24, 300, PW - 48, 112,
                    ["Малий опір (чи нульова",
                     "зустрічна напруга) пускає",
                     "великий струм на старті.",
                     "Він спадає, коли нитка",
                     "нагріється, а ротор — розкрутиться."],
                    size=13, pad=12))

    render(os.path.join(IMG, "three-mechanisms.svg"), W, H, *f,
           title="Один симптом — три різні механізми кидка")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 3 — приборкання: форма струму без і з заходами + три способи
# ─────────────────────────────────────────────────────────────────────────────
def fig_taming():
    W, H = 1060, 540
    f = []

    # ── верх: порівняння форм струму ──
    ox, oy = 120, 300
    rgt, topA = 660, 110
    f.append(arrow(ox, oy, rgt, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, topA, color=INK, sw=1.8))
    f.append(text(rgt, oy + 22, "час", size=12, color=INK, anchor="end"))
    f.append(text(ox + 4, topA - 8, "струм", size=12, color=INK, anchor="start"))

    PW = rgt - ox - 20

    def xt(u):
        return ox + (u / 5.0) * PW

    # межа
    limY = 235
    f.append(line(ox, limY, rgt - 6, limY, color=MUTED, sw=1.5, dash="6 5"))
    f.append(text(rgt - 6, limY - 8, "розумна межа", size=11.5, color=MUTED, anchor="end"))

    # без заходів — гострий пік
    peakY = 130.0
    upts = []
    N = 120
    for k in range(N + 1):
        u = 5.0 * k / N
        frac = 0.03 + 0.97 * math.exp(-u * 3.2)
        upts.append((xt(u), oy - frac * (oy - peakY)))
    f.append(line(ox, oy, ox, peakY, color=POS, sw=2.6, dash="5 4"))
    f.append(poly(upts, color=POS, sw=2.6, dash="5 4"))
    f.append(text(xt(0.5), peakY + 6, "без заходів:", size=12.5, color=POS, anchor="start", bold=True))
    f.append(text(xt(0.5), peakY + 24, "сотні ампер", size=12, color=POS, anchor="start"))

    # із приборканням — пологий горб під межею
    tpts = []
    for k in range(N + 1):
        u = 5.0 * k / N
        # горб: наростає й спадає, не вище межі
        val = math.exp(-((u - 1.2) ** 2) / 0.9)
        frac = 0.03 + 0.62 * val
        tpts.append((xt(u), oy - frac * (oy - peakY)))
    f.append(polyfill([(ox, oy)] + tpts + [(xt(5.0), oy)], FIELD, None, sw=0, op=0.13))
    f.append(poly(tpts, color=FIELD, sw=3.0))
    f.append(text(xt(2.6), oy - 0.55 * (oy - peakY), "із приборканням:", size=12.5,
                  color=FIELD, anchor="start", bold=True))
    f.append(text(xt(2.6), oy - 0.42 * (oy - peakY), "струм під межею", size=12,
                  color=FIELD, anchor="start"))

    f.append(text(390, oy + 44, "площа під обома кривими однакова — той самий заряд, лише розтягнутий у часі",
                  size=12, color=MUTED, anchor="middle"))

    # ── праворуч від графіка: коротка теза ──
    f.append(box(855, 200, "Суть скрізь одна:\nне дати струму злетіти —\nдодати опору на час старту,\nпідняти напругу повільно\nабо влучити в слушну фазу.",
                 size=12.5, min_w=290))

    # ── низ: три способи ──
    by = 372
    bw, bh = 320, 128
    gap = (W - 3 * bw) / 4.0
    xs = [gap, 2 * gap + bw, 3 * gap + 2 * bw]

    f.append(fitbox(xs[0], by, bw, bh,
                    ["NTC-термістор",
                     "",
                     "холодний — опір великий, зрізає пік;",
                     "нагрівся — опір малий, не заважає.",
                     "Мінус: гарячий, треба охолонути."],
                    size=13, pad=12, fill=FILL, stroke=FIELD, sw=1.8))
    f.append(fitbox(xs[1], by, bw, bh,
                    ["Резистор + обхідний ключ",
                     "",
                     "R обмежує перший сплеск, а коли",
                     "конденсатор зарядився — реле чи",
                     "тиристор коротить R геть."],
                    size=13, pad=12, fill=FILL, stroke=INK, sw=1.6))
    f.append(fitbox(xs[2], by, bw, bh,
                    ["Активний плавний пуск",
                     "",
                     "MOSFET піднімає напругу повільним",
                     "фронтом: Iкид = C·dV/dt, тож пік",
                     "падає рівно так, як пологіший фронт."],
                    size=13, pad=12, fill=FILL, stroke=NEG, sw=1.8))

    render(os.path.join(IMG, "taming-inrush.svg"), W, H, *f,
           title="Приборкання кидка: та сама енергія, розтягнута в часі")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 4 — момент увімкнення: форма потоку (подвоєння) проти напруги
# ─────────────────────────────────────────────────────────────────────────────
def fig_pow_flux():
    W, H = 1060, 560
    f = []
    ox, rgt = 110, 950
    PW = rgt - ox

    def xw(wt):
        return ox + (wt / (2 * math.pi)) * PW

    # ── верх: напруга мережі ──
    vY, vA = 120, 46
    f.append(line(ox, vY, rgt, vY, color=MUTED, sw=1.0, dash="3 7"))
    vpts = [(xw(2 * math.pi * k / 200), vY - vA * math.sin(2 * math.pi * k / 200)) for k in range(201)]
    f.append(poly(vpts, color=NEG, sw=2.4))
    f.append(text(ox, vY - vA - 12, "напруга мережі  v = Vпік·sin ωt", size=13, color=NEG, anchor="start", bold=True))
    f.append(circle(xw(0), vY, 4.4, fill=NEG, stroke=NEG))
    f.append(text(xw(0) + 10, vY - 12, "вмикаємо: v = 0", size=12, color=NEG, anchor="start", bold=True))

    # ── низ: потік ──
    zY, U = 380, 74

    def yphi(p):
        return zY - U * p

    # смуга насичення
    f.append(rect(ox, yphi(2.35), PW, yphi(1.33) - yphi(2.35), fill="#fdecea", stroke="#fdecea", sw=0))
    f.append(text(rgt - 8, yphi(2.28) + 4, "зона насичення (B > Bsat ≈ 2 Тл)", size=11.5, color=POS, anchor="end", bold=True))
    # напрямні рівні
    for p, lab, bold in [(2.0, "2·Φпік", True), (1.0, "Φпік", False), (-1.0, "−Φпік", False)]:
        f.append(line(ox, yphi(p), rgt, yphi(p), color=MUTED, sw=1.0, dash="2 8"))
        f.append(text(ox - 10, yphi(p) + 4, lab, size=12, color=(POS if bold else MUTED), anchor="end", bold=bold))
    # осі
    f.append(arrow(ox, yphi(-1.35), ox, yphi(2.45), color=INK, sw=1.5))
    f.append(arrow(ox, zY, rgt + 6, zY, color=INK, sw=1.5))
    f.append(text(ox - 10, zY + 4, "0", size=12, color=MUTED, anchor="end"))
    f.append(text(ox + 6, yphi(2.45) - 4, "потік φ", size=12.5, color=INK, anchor="start", bold=True))
    # часові позначки
    for wt, lab in [(0, "0"), (math.pi / 2, "T/4"), (math.pi, "T/2"), (3 * math.pi / 2, "3T/4"), (2 * math.pi, "T")]:
        f.append(line(xw(wt), zY, xw(wt), zY + 6, color=INK, sw=1.3))
        f.append(text(xw(wt), H - 22, lab, size=12, color=INK))

    # усталений потік (пунктир): −cos
    spts = [(xw(2 * math.pi * k / 200), yphi(-math.cos(2 * math.pi * k / 200))) for k in range(201)]
    f.append(poly(spts, color=MUTED, sw=1.8, dash="6 5"))
    # кидок-потік (жирний): 1−cos
    ipts = [(xw(2 * math.pi * k / 200), yphi(1 - math.cos(2 * math.pi * k / 200))) for k in range(201)]
    f.append(poly(ipts, color=POS, sw=3.0))

    # вертикальний зв'язок: нуль напруги → пік потоку
    f.append(line(xw(0), vY, xw(0), yphi(0), color=NEG, sw=1.0, dash="2 6"))
    f.append(line(xw(math.pi), zY, xw(math.pi), yphi(2.0), color=POS, sw=1.0, dash="2 6"))

    # мітки на кривих
    f.append(circle(xw(0), yphi(0), 4.2, fill=POS, stroke=POS))
    f.append(text(xw(0) + 8, yphi(0) + 22, "старт із 0", size=12, color=POS, anchor="start", bold=True))
    f.append(circle(xw(math.pi), yphi(2.0), 4.6, fill=POS, stroke=POS))
    f.append(text(xw(math.pi) + 12, yphi(2.0) - 8, "2·Φпік за півперіоду", size=12.5, color=POS, anchor="start", bold=True))
    f.append(text(xw(0.9), yphi(0.30) - 12, "кидок — увімкнення в нулі", size=12, color=POS, anchor="start"))
    f.append(text(xw(2.15), yphi(0.62) - 10, "усталений потік ±Φпік", size=11.5, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "pow-flux-doubling.svg"), W, H, *f,
           title="Момент увімкнення: потік стартує з нуля й подвоюється за півперіоду")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 5 — протилежні найгірші фази для конденсатора й трансформатора
# ─────────────────────────────────────────────────────────────────────────────
def fig_pow_phase():
    W, H = 1060, 520
    f = []
    ox, rgt = 120, 940
    PW = rgt - ox

    def xw(wt):
        return ox + (wt / (2 * math.pi)) * PW

    midY, A = 258, 104
    # вісь і синус
    f.append(line(ox, midY, rgt, midY, color=MUTED, sw=1.0, dash="3 8"))
    f.append(arrow(ox, midY, rgt + 6, midY, color=INK, sw=1.4))
    f.append(text(rgt + 2, midY + 26, "фаза θ", size=12.5, color=INK, anchor="end"))
    pts = [(xw(2 * math.pi * k / 220), midY - A * math.sin(2 * math.pi * k / 220)) for k in range(221)]
    f.append(poly(pts, color=NEG, sw=2.6))
    f.append(text(ox + 6, midY - A - 12, "v(t)", size=13, color=NEG, anchor="start", bold=True))

    key = [0, math.pi / 2, math.pi, 3 * math.pi / 2, 2 * math.pi]
    for wt in key:
        x = xw(wt)
        y = midY - A * math.sin(wt)
        f.append(line(x, 102, x, 440, color=MUTED, sw=1.0, dash="2 6"))
        f.append(circle(x, y, 4.6, fill=BG, stroke=INK, sw=2))

    def tag(cx, y, txt, good):
        col = FIELD if good else POS
        mark = "✓ найкраще" if good else "✗ найгірше"
        return fitbox(cx - 80, y, 160, 42, [txt, mark], size=11.5, pad=6,
                      fill=("#eafaf0" if good else "#fdecea"), stroke=col, sw=1.6, color=col, bold=True)

    # КОНДЕНСАТОР — над синусом: найгірше в піку, найкраще в нулі
    f.append(text(ox - 4, 48, "Конденсатор   iпік = v/R  — за миттєвою напругою", size=13, color=INK, anchor="start", bold=True))
    f.append(tag(xw(0), 58, "у нулі", True))
    f.append(tag(xw(math.pi / 2), 58, "у піку +", False))
    f.append(tag(xw(math.pi), 58, "у нулі", True))
    f.append(tag(xw(3 * math.pi / 2), 58, "у піку −", False))

    # ТРАНСФОРМАТОР — під синусом: навпаки
    yb = 442
    f.append(tag(xw(0), yb, "у нулі", False))
    f.append(tag(xw(math.pi / 2), yb, "у піку +", True))
    f.append(tag(xw(math.pi), yb, "у нулі", False))
    f.append(tag(xw(3 * math.pi / 2), yb, "у піку −", True))
    f.append(text(ox - 4, 500, "Трансформатор   φ ~ ∫v·dt  — зсув на 90° від напруги", size=13, color=INK, anchor="start", bold=True))

    render(os.path.join(IMG, "pow-phase-opposition.svg"), W, H, *f,
           title="Протилежні найгірші фази: пік для конденсатора — нуль для трансформатора")


if __name__ == "__main__":
    fig_spike()
    fig_three()
    fig_taming()
    fig_pow_flux()
    fig_pow_phase()
    print("figs OK")
