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


def polyfill(pts, fill=FIELD, op=0.14):
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polygon points="%s" fill="%s" fill-opacity="%.2f" stroke="none"/>' % (p, fill, op))


def cap(cx, cy, lead=18, gap=9, plate=30, color=INK, sw=2.4):
    return "".join([
        line(cx, cy - lead - gap / 2, cx, cy - gap / 2, color=color, sw=sw),
        line(cx - plate / 2, cy - gap / 2, cx + plate / 2, cy - gap / 2, color=color, sw=sw),
        line(cx - plate / 2, cy + gap / 2, cx + plate / 2, cy + gap / 2, color=color, sw=sw),
        line(cx, cy + gap / 2, cx, cy + lead + gap / 2, color=color, sw=sw)])


def cap_h(cx, cy, lead=16, gap=9, plate=28, color=INK, sw=2.4):
    """Горизонтальний конденсатор (виводи ліворуч-праворуч)."""
    return "".join([
        line(cx - lead - gap / 2, cy, cx - gap / 2, cy, color=color, sw=sw),
        line(cx - gap / 2, cy - plate / 2, cx - gap / 2, cy + plate / 2, color=color, sw=sw),
        line(cx + gap / 2, cy - plate / 2, cx + gap / 2, cy + plate / 2, color=color, sw=sw),
        line(cx + gap / 2, cy, cx + lead + gap / 2, cy, color=color, sw=sw)])


def battery(cx, top, bot, color=INK, sw=2.4):
    y1 = (top + bot) / 2 - 6
    y2 = y1 + 12
    return "".join([
        line(cx, top, cx, y1, color=color, sw=sw),
        line(cx - 18, y1, cx + 18, y1, color=color, sw=sw),
        line(cx - 8, y2, cx + 8, y2, color=color, sw=sw),
        line(cx, y2, cx, bot, color=color, sw=sw)])


def resistor(x1, x2, y, color=INK, sw=2.4, h=13):
    """Зигзаг-резистор між x1 і x2 на висоті y."""
    n = 6
    seg = (x2 - x1) / (n + 1.0)
    pts = [(x1, y)]
    for i in range(n):
        pts.append((x1 + seg * (i + 1), y + (h if i % 2 == 0 else -h)))
    pts.append((x2, y))
    return poly(pts, color=color, sw=sw)


def switch_open(x1, x2, y, color=INK, sw=2.4):
    a, b = x1 + 8, x2 - 8
    return "".join([
        line(x1, y, a, y, color=color, sw=sw),
        circle(a, y, 3.2, fill=color, stroke=color),
        line(a, y, b - 3, y - 17, color=color, sw=sw),
        circle(b, y, 3.2, fill=color, stroke=color),
        line(b, y, x2, y, color=color, sw=sw)])


def dot(x, y):
    return circle(x, y, 3.6, fill=INK, stroke=INK)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 1 — дві топології послідовного м'якого старту
# ─────────────────────────────────────────────────────────────────────────────
def fig_topologies():
    W, H = 1120, 470
    f = []
    f.append(line(560, 60, 560, 448, color=MUTED, sw=1.3, dash="3 7"))
    f.append(text(285, 58, "Резистор + обхідний ключ", size=15.5, color=MUTED, bold=True))
    f.append(text(838, 58, "Послідовний MOSFET", size=15.5, color=MUTED, bold=True))

    topY, botY = 180, 350

    # ── ПАНЕЛЬ A ──
    bx = 80
    f.append(battery(bx, topY, botY))
    f.append(text(bx - 28, (topY + botY) / 2 + 5, "V", size=15, color=INK, anchor="end", bold=True))

    # верхній провід + вузол A
    f.append(line(bx, topY, 175, topY, color=INK, sw=2.2))
    f.append(dot(175, topY))
    # резистор на головному проводі
    f.append(line(175, topY, 210, topY, color=INK, sw=2.2))
    f.append(resistor(210, 300, topY, color=POS, sw=2.4))
    f.append(text(255, topY + 34, "R  передзаряд", size=12.5, color=POS, anchor="middle", bold=True))
    f.append(line(300, topY, 362, topY, color=INK, sw=2.2))
    f.append(dot(362, topY))
    # обхід зверху з контактором
    f.append(line(175, topY, 175, 122, color=INK, sw=2.2))
    f.append(line(175, 122, 232, 122, color=INK, sw=2.2))
    f.append(switch_open(232, 305, 122))
    f.append(line(305, 122, 362, 122, color=INK, sw=2.2))
    f.append(line(362, 122, 362, topY, color=INK, sw=2.2))
    f.append(text(268, 104, "K  контактор", size=12.5, color=INK, anchor="middle", bold=True))
    f.append(text(268, 88, "(замкнути, коли C заряджений)", size=11, color=MUTED, anchor="middle"))
    # вузол C → конденсатор → навантаження
    f.append(line(362, topY, 430, topY, color=INK, sw=2.2))
    f.append(dot(430, topY))
    f.append(cap(430, topY + 52, lead=16, gap=10, plate=34))
    f.append(text(452, topY + 44, "C", size=13, color=INK, anchor="start", bold=True))
    f.append(text(452, topY + 62, "буфер", size=11.5, color=MUTED, anchor="start"))
    f.append(line(430, topY + 78, 430, botY, color=INK, sw=2.2))
    # навантаження
    f.append(rect(474, topY - 10, 62, 120, fill=FILL, stroke=INK, sw=1.6))
    f.append(mtext(505, topY + 46, ["наван-", "таження"], size=11.5, color=INK))
    f.append(line(430, topY, 474, topY, color=INK, sw=2.2))
    f.append(line(474, botY, 505, botY, color=INK, sw=2.2))
    f.append(line(505, botY, 505, topY + 110, color=INK, sw=2.2))
    # нижній провід
    f.append(line(bx, botY, 430, botY, color=INK, sw=2.2))
    f.append(box(285, 418, "R гріється лише на старті · тепло ½·C·V² осідає в резисторі",
                 size=12, min_w=470, fill="#fff5f5", stroke=POS, sw=1.4))

    # ── ПАНЕЛЬ B ──
    bx2 = 640
    f.append(battery(bx2, topY, botY))
    f.append(text(bx2 - 28, (topY + botY) / 2 + 5, "V", size=15, color=INK, anchor="end", bold=True))
    f.append(line(bx2, topY, 712, topY, color=INK, sw=2.2))
    # транзистор-ключ
    f.append(rect(712, topY - 26, 84, 52, fill=FILL, stroke=INK, sw=1.8))
    f.append(text(754, topY - 3, "MOSFET", size=12.5, color=INK, bold=True))
    f.append(text(722, topY + 18, "D", size=10.5, color=MUTED, anchor="start"))
    f.append(text(786, topY + 18, "S", size=10.5, color=MUTED, anchor="end"))
    # вихідний вузол
    f.append(line(796, topY, 858, topY, color=INK, sw=2.2))
    f.append(dot(858, topY))
    f.append(cap(858, topY + 52, lead=16, gap=10, plate=34))
    f.append(text(880, topY + 44, "C", size=13, color=INK, anchor="start", bold=True))
    f.append(text(880, topY + 62, "буфер", size=11.5, color=MUTED, anchor="start"))
    f.append(line(858, topY + 78, 858, botY, color=INK, sw=2.2))
    f.append(rect(902, topY - 10, 62, 120, fill=FILL, stroke=INK, sw=1.6))
    f.append(mtext(933, topY + 46, ["наван-", "таження"], size=11.5, color=INK))
    f.append(line(858, topY, 902, topY, color=INK, sw=2.2))
    f.append(line(902, botY, 933, botY, color=INK, sw=2.2))
    f.append(line(933, botY, 933, topY + 110, color=INK, sw=2.2))
    f.append(line(bx2, botY, 858, botY, color=INK, sw=2.2))

    # затворне коло: Rз від входу, Cзс від затвора до виходу
    gx = 754
    f.append(line(gx, topY + 26, gx, 288, color=INK, sw=2.2))          # затвор униз
    f.append(text(gx + 8, 300, "G", size=10.5, color=MUTED, anchor="start"))
    # Rз від +рейки (тап при 680)
    f.append(line(680, topY, 680, 288, color=NEG, sw=2.0))
    f.append(resistor(680, gx, 288, color=NEG, sw=2.2, h=11))
    f.append(text(716, 312, "Rз", size=12.5, color=NEG, anchor="middle", bold=True))
    # Cзс від затвора до вихідного вузла (міллерівський)
    f.append(line(gx, 288, 820, 288, color=FIELD, sw=2.0))
    f.append(cap(820, 262, lead=12, gap=9, plate=26, color=FIELD))
    f.append(line(820, 244, 820, topY, color=FIELD, sw=2.0))
    f.append(text(838, 280, "Cзс", size=12.5, color=FIELD, anchor="start", bold=True))
    f.append(box(802, 418, "фронт задає Rз·Cзс · тепло ½·C·V² осідає в транзисторі",
                 size=12, min_w=470, fill="#eafaf0", stroke=FIELD, sw=1.4))

    render(os.path.join(IMG, "soft-start-topologies.svg"), W, H, *f,
           title="Дві родини послідовного м'якого старту")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 2 — часові діаграми активного м'якого старту
# ─────────────────────────────────────────────────────────────────────────────
def fig_timing():
    W, H = 1060, 590
    f = []
    ox, rgt = 190, 1000
    PW = rgt - ox
    t1 = ox + 0.17 * PW
    t2 = ox + 0.70 * PW
    trise = t2 + 0.10 * PW

    rows = [
        ("Uзатв", 175, 78),   # (мітка, base y, span)
        ("Uвих", 300, 78),
        ("Iзаряд", 425, 78),
        ("Pтранз", 550, 78),
    ]
    # спільні вертикалі фронту
    for xx in (t1, t2):
        f.append(line(xx, 92, xx, 566, color=MUTED, sw=1.2, dash="4 6"))
    f.append(text((t1 + t2) / 2, 84, "T — фронт напруги", size=13, color=INK, bold=True))
    f.append(line(t1 + 6, 88, t2 - 6, 88, color=INK, sw=1.0))

    for name, base, span in rows:
        f.append(line(ox, base, rgt, base, color="#d0d5db", sw=1.2))          # базова лінія
        f.append(line(ox, base + 10, ox, base - span - 6, color=INK, sw=1.4)) # ось трасу
        f.append(text(ox - 16, base - span * 0.5, name, size=13, color=INK, anchor="end", bold=True))

    def yv(base, span, frac):
        return base - frac * span

    # Uзатв: наростання до плато Міллера, потім до повного
    b, sp = 175, 78
    vg = [(ox, b), (t1, yv(b, sp, 0.52)), (t2, yv(b, sp, 0.52)),
          (trise, yv(b, sp, 0.92)), (rgt, yv(b, sp, 0.92))]
    f.append(poly(vg, color=NEG, sw=2.8))
    f.append(text((t1 + t2) / 2, yv(b, sp, 0.52) - 9, "плато Міллера", size=11.5, color=NEG))
    f.append(text(t1 - 6, yv(b, sp, 0.30), "поріг", size=11, color=MUTED, anchor="end"))

    # Uвих: 0 до t1, лінійний фронт, потім повна V
    b, sp = 300, 78
    vo = [(ox, b), (t1, b), (t2, yv(b, sp, 0.90)), (rgt, yv(b, sp, 0.90))]
    f.append(poly(vo, color=INK, sw=2.8))
    f.append(line(ox, yv(b, sp, 0.90), t2, yv(b, sp, 0.90), color=MUTED, sw=1.0, dash="3 6"))
    f.append(text(rgt - 4, yv(b, sp, 0.90) - 8, "V", size=12.5, color=INK, anchor="end", bold=True))
    f.append(text((t1 + t2) / 2 + 18, yv(b, sp, 0.42), "лінійний фронт", size=11.5, color=INK))

    # Iзаряд: поличка Iкид під час фронту
    b, sp = 425, 78
    ii = [(ox, b), (t1, b), (t1, yv(b, sp, 0.62)), (t2, yv(b, sp, 0.62)),
          (t2, yv(b, sp, 0.08)), (rgt, yv(b, sp, 0.08))]
    f.append(polyfill([(t1, b), (t1, yv(b, sp, 0.62)), (t2, yv(b, sp, 0.62)), (t2, b)], FIELD, 0.15))
    f.append(poly(ii, color=FIELD, sw=2.8))
    f.append(text((t1 + t2) / 2, yv(b, sp, 0.62) - 9, "Iкид = C·dV/dt  (рівна поличка)", size=11.5, color=FIELD, bold=True))

    # Pтранз: трикутник, пік на t1, до нуля на t2
    b, sp = 550, 78
    pp = [(ox, b), (t1, b), (t1, yv(b, sp, 0.86)), (t2, b), (rgt, b)]
    f.append(polyfill([(t1, b), (t1, yv(b, sp, 0.86)), (t2, b)], POS, 0.16))
    f.append(poly(pp, color=POS, sw=2.8))
    f.append(text(t1 + 8, yv(b, sp, 0.86) - 6, "Pпік = V·Iкид", size=11.5, color=POS, anchor="start", bold=True))
    f.append(text((t1 + t2) / 2 + 30, yv(b, sp, 0.30), "площа = ½·C·V²", size=11.5, color=POS))

    f.append(text(rgt, 582, "час", size=12, color=INK, anchor="end"))

    render(os.path.join(IMG, "mosfet-softstart-timing.svg"), W, H, *f,
           title="Активний м'який старт у часі: фронт напруги тримає струм рівним")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 3 — SOA й компроміс тривалості фронту
# ─────────────────────────────────────────────────────────────────────────────
def cnum(cx, cy, n, col):
    return (circle(cx, cy, 10, fill=BG, stroke=col, sw=2.2) +
            text(cx, cy + 4.5, str(n), size=13, color=col, bold=True))


def fig_soa():
    W, H = 1160, 660
    f = []
    ox, oy = 150, 470
    rgt, topA = 900, 95
    PW, PH = rgt - ox, oy - topA

    Vmin, Vmax = 2.0, 100.0
    Imin, Imax = 0.05, 60.0
    lVmin, lVmax = math.log10(Vmin), math.log10(Vmax)
    lImin, lImax = math.log10(Imin), math.log10(Imax)

    def xV(V):
        return ox + (math.log10(V) - lVmin) / (lVmax - lVmin) * PW

    def yI(I):
        return oy - (math.log10(I) - lImin) / (lImax - lImin) * PH

    # сітка
    for V in (2, 5, 10, 20, 50, 100):
        f.append(line(xV(V), oy, xV(V), topA, color="#eceff3", sw=1.0))
        f.append(text(xV(V), oy + 20, str(V), size=11.5, color=MUTED))
    for I in (0.1, 0.3, 1, 3, 10, 30):
        f.append(line(ox, yI(I), rgt, yI(I), color="#eceff3", sw=1.0))
        f.append(text(ox - 12, yI(I) + 4, ("%g" % I), size=11.5, color=MUTED, anchor="end"))
    # осі
    f.append(arrow(ox, oy, rgt + 6, oy, color=INK, sw=1.6))
    f.append(arrow(ox, oy, ox, topA - 6, color=INK, sw=1.6))
    f.append(text(rgt + 4, oy + 38, "Vds, В (лог)", size=12.5, color=INK, anchor="end", bold=True))
    f.append(text(ox + 6, topA - 14, "Id, А (лог)", size=12.5, color=INK, anchor="start", bold=True))

    Idmax = 40.0
    Vlim = 80.0

    def curve(Pbase, Vk=None, m=0.0):
        pts = []
        V = Vmin
        while V <= Vlim + 1e-9:
            I = Pbase / V
            if Vk and V > Vk:
                I *= (Vk / V) ** m
            I = min(I, Idmax)
            if I >= Imin:
                pts.append((xV(V), yI(I)))
            V *= 1.06
        return pts

    # межі SOA: що довший імпульс, то нижча крива; DC ще й прогинається при високій V
    families = [
        (400.0, None, 0.0, "1 мс", 20.0, MUTED),
        (180.0, None, 0.0, "10 мс", 12.0, MUTED),
        (45.0, 20.0, 0.6, "100 мс", 6.0, MUTED),
        (14.0, 12.0, 0.9, "DC (постійно)", 3.0, POS),
    ]
    # верхня поличка максимального струму
    f.append(line(ox, yI(Idmax), xV(400.0 / Idmax), yI(Idmax), color=INK, sw=2.0))
    f.append(text(xV(2.15), yI(Idmax) - 9, "макс. струм", size=11, color=INK, anchor="start"))
    for Pbase, Vk, m, lab, Ilab, col in families:
        pts = curve(Pbase, Vk, m)
        f.append(poly(pts, color=col, sw=(2.8 if col == POS else 1.8),
                      dash=None if col == POS else "7 5"))
        # мітку ставимо на похилій частині кривої (за струмом Ilab) — криві там рознесені
        Vl = Pbase / Ilab
        f.append(text(xV(Vl) + 6, yI(Ilab) - 7, lab, size=11.5, color=col,
                      anchor="start", bold=(col == POS)))
    # вертикальна межа напруги
    f.append(line(xV(Vlim), oy, xV(Vlim), yI(Idmax), color=INK, sw=1.6, dash="4 5"))
    f.append(text(xV(Vlim) - 6, topA + 16, "Vds max", size=11, color=INK, anchor="end"))
    f.append(text(xV(58), topA + 46, "зона поза SOA", size=12, color=POS, anchor="middle", bold=True))

    # робочі точки при повній напрузі Vfull = 48 В (найгостріший кут фронту)
    Vf = 48.0
    ops = [(1, 2.0, FIELD), (2, 0.5, FIELD), (3, 0.28, POS)]
    for n, I, col in ops:
        px, py = xV(Vf), yI(I)
        # локус фронту: за сталого струму Vds спадає (рух ліворуч)
        f.append(line(xV(16.0), py, px, py, color=col, sw=1.4, dash="2 5"))
        f.append(arrow(xV(24.0), py, xV(16.5), py, color=col, sw=1.4))
        f.append(circle(px, py, 6.0, fill=("#eafaf0" if col == FIELD else "#fdecea"),
                        stroke=col, sw=2.4))
        f.append(cnum(px + 22, py - 2, n, col))
    # короткий підпис локусу — в порожньому лівому низу площини
    f.append(text(ox + 8, oy - 12, "точки 1-3 — кут ключа при 48 В;  штрих <- рух Vds за час фронту",
                  size=11, color=MUTED, anchor="start"))

    # ── пояснення точок — рядком під графіком, без ліній-виносок ──
    cy = 560
    bw = 340
    xs = [40, 40 + bw + 30, 40 + 2 * (bw + 30)]
    notes = [
        (1, FIELD, "#eafaf0", ["Короткий фронт  T≈11 мс",
                               "Струм великий (2 А), але фронт короткий —",
                               "точку тримає ВИСОКА короткоімпульсна крива.",
                               "Безпечно, із запасом."]),
        (2, FIELD, "#eafaf0", ["Середній фронт  T≈40 мс",
                               "Струм менший (0.5 А), крива — 100 мс.",
                               "Ще під межею, але запас тане.",
                               "Десь тут оптимум."]),
        (3, POS, "#fdecea", ["Надто довгий фронт  T≈110 мс",
                             "Струм НАЙменший (0.28 А) — та фронт такий",
                             "довгий, що рівняється до DC-кривої, а вона",
                             "при 48 В прогнулась. Точка ЗА межею SOA."]),
    ]
    for (n, col, fill, lines), x in zip(notes, xs):
        f.append(rect(x, cy, bw, 96, fill=fill, stroke=col, sw=1.6, rx=8))
        f.append(cnum(x + 20, cy + 22, n, col))
        f.append(mtext(x + 40, cy + 20, [lines[0]], size=12.5, color=col, anchor="start", bold=True))
        f.append(mtext(x + 16, cy + 44, lines[1:], size=11.3, color=INK, anchor="start", lh=1.32))

    render(os.path.join(IMG, "soa-ramp-tradeoff.svg"), W, H, *f,
           title="Компроміс фронту: повільніше — не завжди безпечніше")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 4 — дві історичні лінії до м'якого старту (для вставки hist-)
# ─────────────────────────────────────────────────────────────────────────────
def fig_history_timeline():
    W, H = 1250, 700
    f = []

    yT, yB = 252, 448          # осьові лінії двох ліній
    xL, xR = 110, 1185

    # ── ВЕРХНЯ ЛІНІЯ (пасивна, тепла — POS) ──
    f.append(text(xL, 66, "①  ПАСИВНА ЛІНІЯ", size=15, color=POS, anchor="start", bold=True))
    f.append(text(xL + 200, 66, "·  термістор прибирає опір сам, нагрівом",
                  size=12.5, color=MUTED, anchor="start"))
    f.append(line(xL, yT, xR, yT, color=POS, sw=2.4))

    top = [
        (250, "1833", ["Фарадей", "NTC-ефект", "у Ag₂S"]),
        (470, "1930", ["Рубен", "1-й практичний", "NTC-прилад", "(пірометр)"]),
        (690, "1946", ["Bell Labs", "Беккер · Ґрін ·", "Пірсон:", "«термістор»"]),
        (910, "1950–70-ті", ["силові NTC —", "обмежувачі", "кидка"]),
        (1120, "1994", ["Ametherm", "потужні", "обмежувачі", "кидка"]),
    ]
    for x, yr, lines in top:
        cy = 158
        f.append(box(x, cy, "\n".join(lines), size=11.5, fill="#fff5f5",
                     stroke=POS, sw=1.5, color=INK))
        f.append(line(x, 214, x, yT, color=MUTED, sw=1.3))
        f.append(circle(x, yT, 6.2, fill=POS, stroke=POS))
        f.append(text(x, yT + 26, yr, size=13, color=POS, bold=True))

    # ── ТЕЗА посередині ──
    f.append(text(W / 2, 352,
                  "різні фізики — та сама мета: пом'якшити стрибок від t = 0 до роботи",
                  size=13, color=INK, bold=True))

    # ── НИЖНЯ ЛІНІЯ (активна, електронна — NEG) ──
    f.append(text(xL, 402, "②  АКТИВНА ЛІНІЯ", size=15, color=NEG, anchor="start", bold=True))
    f.append(text(xL + 195, 402, "·  вивід навмисно вповільнює регулятор",
                  size=12.5, color=MUTED, anchor="start"))
    f.append(line(xL, yB, xR, yB, color=NEG, sw=2.4))

    bot = [
        (365, "1976", ["SG1524 · Silicon General", "Мамано: 1-й монолітний",
                       "ШІМ; м'який старт —", "зовнішньо на виводі COMP"]),
        (720, "≈1980", ["SG1525A", "окремий вивід", "soft-start", "(нога 8)"]),
        (1035, "1981 →", ["Unitrode UC384x /", "UC1846 (Мамано):",
                               "струмовий режим;", "вивід soft-start"]),
    ]
    for x, yr, lines in bot:
        cy = 556
        f.append(text(x, yB - 16, yr, size=13, color=NEG, bold=True))
        f.append(circle(x, yB, 6.2, fill=NEG, stroke=NEG))
        f.append(line(x, yB, x, 500, color=MUTED, sw=1.3))
        f.append(box(x, cy, "\n".join(lines), size=11.5, fill="#eef3fd",
                     stroke=NEG, sw=1.5, color=INK))

    f.append(text(W / 2, 682,
                  "лінії — у хронологічному порядку зліва направо; дати підписані, вісь не в масштабі часу",
                  size=11, color=MUTED))

    render(os.path.join(IMG, "soft-start-history-timeline.svg"), W, H, *f,
           title="Дві історичні лінії, що привели до м'якого старту")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 5 (math) — струмовий баланс на вузлі затвора: чому фронт лінійний
# ─────────────────────────────────────────────────────────────────────────────
def fig_gate_integrator():
    W, H = 1040, 470
    f = []
    yc = 210

    # ── джерело затвора ──
    f.append(box(150, yc, ["Iзатв", "майже сталий"], size=13, min_w=150,
                 fill="#eaf0fd", stroke=NEG, sw=1.5))
    f.append(arrow(232, yc, 362, yc, color=NEG, sw=2.2))
    f.append(text(297, yc - 12, "Iзатв", size=12.5, color=NEG, bold=True))

    # ── вузол затвора ──
    gx = 372
    f.append(dot(gx, yc))
    f.append(text(gx + 10, yc + 28, "вузол G", size=12, color=INK, anchor="start", bold=True))

    # ── гілка вгору: Cзв, струм ≈ 0 (плато Міллера) ──
    f.append(line(gx, yc, gx, 147, color=INK, sw=2.0))
    f.append(cap(gx, 124, lead=18, gap=9, plate=28, color=MUTED))
    f.append(line(gx, 101, gx, 87, color=INK, sw=2.0))
    f.append(box(gx, 62, ["Vзв тримається сталим", "(плато Міллера)"], size=12, min_w=240,
                 fill=FILL, stroke=MUTED, sw=1.4))
    f.append(text(gx + 20, 128, "Cзв:  I ≈ 0", size=12, color=MUTED, anchor="start"))

    # ── гілка праворуч: Cзс несе увесь Iзатв ──
    f.append(line(gx, yc, 535, yc, color=INK, sw=2.0))
    f.append(cap_h(556, yc, lead=16, gap=9, plate=28, color=FIELD))
    f.append(line(577, yc, 706, yc, color=INK, sw=2.0))
    f.append(text(556, yc - 26, "Cзс", size=13, color=FIELD, anchor="middle", bold=True))
    f.append(text(556, yc + 30, "увесь Iзатв тече крізь Cзс", size=12, color=FIELD, anchor="middle"))

    # ── вихідний вузол + буферний конденсатор ──
    ox2 = 706
    f.append(dot(ox2, yc))
    f.append(box(832, yc, ["Вихід:  Vвих ↑", "нахил dVвих/dt"], size=12.5, min_w=200,
                 fill="#eafaf0", stroke=FIELD, sw=1.5))
    f.append(line(ox2, yc, 732, yc, color=INK, sw=2.0))
    f.append(line(ox2, yc, ox2, 300, color=INK, sw=2.0))
    f.append(cap(ox2, 320, lead=18, gap=10, plate=32))
    f.append(text(ox2 + 20, 320, "C  буфер", size=12, color=INK, anchor="start", bold=True))
    f.append(line(ox2, 342, ox2, 378, color=INK, sw=2.0))
    f.append(line(606, 378, 806, 378, color=INK, sw=2.0))

    # ── банери-рівняння ──
    f.append(box(300, 432, "Iзатв = Cзс · dVвих/dt   ⇒   dVвих/dt = Iзатв / Cзс = const",
                 size=13, min_w=520, fill="#f4f6f8", stroke=INK, sw=1.5, bold=True))
    f.append(box(802, 432, "Iзаряд = C · dVвих/dt = (C / Cзс) · Iзатв",
                 size=12, min_w=380, fill="#eafaf0", stroke=FIELD, sw=1.4))

    render(os.path.join(IMG, "gate-integrator.svg"), W, H, *f,
           title="Вузол затвора як інтегратор: сталий струм → лінійний фронт")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 6 (math) — незалежність ½·C·V² від форми фронту
# ─────────────────────────────────────────────────────────────────────────────
def fig_energy_invariance():
    W, H = 1160, 560
    f = []
    f.append(line(597, 92, 597, 470, color=MUTED, sw=1.2, dash="3 7"))

    # ── Панель ЛІВОРУЧ: P(t), два фронти, однакова площа ──
    ox, oy, top, rgt = 110, 440, 110, 545
    f.append(text((ox + rgt) / 2, 72, "У часі: форма фронту різна", size=14.5, color=INK, bold=True))
    f.append(arrow(ox, oy, 551, oy, color=INK, sw=1.6))
    f.append(arrow(ox, oy, ox, top - 6, color=INK, sw=1.6))
    f.append(text(549, oy + 26, "час t", size=12.5, color=INK, anchor="end", bold=True))
    f.append(text(ox + 8, top - 14, "P на транзисторі", size=12.5, color=INK, anchor="start", bold=True))

    Hp = oy - top - 16
    Wp = rgt - ox - 25
    # швидкий фронт: високий, вузький
    p1 = 0.92 * Hp
    w1 = 0.30 * Wp
    f.append(polyfill([(ox, oy), (ox, oy - p1), (ox + w1, oy)], POS, 0.20))
    f.append(poly([(ox, oy - p1), (ox + w1, oy)], color=POS, sw=2.8))
    f.append(text(ox + 18, oy - p1 + 9, "пік V·Iкид", size=12, color=POS, anchor="start", bold=True))
    # повільний фронт: низький, широкий (пік / 3, ширина × 3 → площа та сама)
    p2 = p1 / 3.0
    w2 = w1 * 3.0
    f.append(polyfill([(ox, oy), (ox, oy - p2), (ox + w2, oy)], NEG, 0.13))
    f.append(poly([(ox, oy - p2), (ox + w2, oy)], color=NEG, sw=2.6))
    f.append(text(ox + w2 * 0.66, oy - p2 - 10, "повільний фронт", size=12, color=NEG, anchor="middle"))
    f.append(box((ox + rgt) / 2, 508, "різні пік і тривалість — площа та сама  ½·C·V²",
                 size=12, min_w=330, fill=FILL, stroke=INK, sw=1.4))

    # ── Панель ПРАВОРУЧ: dW/dVвих vs Vвих — фіксований трикутник ──
    ox2, oy2, top2, rgt2 = 650, 440, 110, 1090
    f.append(text((ox2 + rgt2) / 2, 72, "На вольт виходу: та сама пряма", size=14.5, color=INK, bold=True))
    f.append(arrow(ox2, oy2, 1096, oy2, color=INK, sw=1.6))
    f.append(arrow(ox2, oy2, ox2, top2 - 6, color=INK, sw=1.6))
    f.append(text(1094, oy2 + 26, "Vвих  (0 → V)", size=12.5, color=INK, anchor="end", bold=True))
    f.append(text(ox2 + 8, top2 - 14, "dW/dVвих = C·(V − Vвих)", size=12.5, color=INK, anchor="start", bold=True))

    ax, ay = ox2, 132   # Vвих = 0  → C·V
    bx, by = 1050, oy2  # Vвих = V  → 0
    f.append(polyfill([(ox2, oy2), (ax, ay), (bx, by)], FIELD, 0.16))
    f.append(poly([(ax, ay), (bx, by)], color=FIELD, sw=3.0))
    f.append(text(ax - 10, ay + 4, "C·V", size=12.5, color=FIELD, anchor="end", bold=True))
    f.append(text(bx, oy2 + 22, "V", size=12.5, color=INK, anchor="middle", bold=True))
    f.append(text(772, 352, "площа = ½·C·V²", size=13.5, color=FIELD, anchor="middle", bold=True))
    f.append(box((ox2 + rgt2) / 2, 508, "dVвих/dt тут не з'являється — площа та сама за будь-якого фронту",
                 size=12, min_w=460, fill="#eafaf0", stroke=FIELD, sw=1.4))

    render(os.path.join(IMG, "energy-invariance.svg"), W, H, *f,
           title="Транзистор з'їдає ½·C·V² незалежно від форми фронту")


# ─────────────────────────────────────────────────────────────────────────────
# Дрібні помічники для фігур секвенсора (proj-precharge-sequencer)
# ─────────────────────────────────────────────────────────────────────────────
def gnd_sym(cx, cy, col=INK):
    return "".join([
        line(cx, cy, cx, cy + 7, color=col, sw=2.0),
        line(cx - 11, cy + 7, cx + 11, cy + 7, color=col, sw=2.2),
        line(cx - 7, cy + 12, cx + 7, cy + 12, color=col, sw=2.0),
        line(cx - 3, cy + 17, cx + 3, cy + 17, color=col, sw=1.8)])


def diode_v(cx, y_anode, y_cath, col=INK):
    """Вертикальний діод: анод унизу (y_anode), катод угорі (y_cath), вістря вгору."""
    mid = (y_anode + y_cath) / 2.0
    tri = ('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
           % (cx - 8, mid + 7, cx + 8, mid + 7, cx, mid - 7, col))
    return "".join([
        line(cx, y_anode, cx, mid + 7, color=col, sw=2.2),
        tri,
        line(cx - 9, mid - 7, cx + 9, mid - 7, color=col, sw=2.6),
        line(cx, mid - 7, cx, y_cath, color=col, sw=2.2)])


def npn(cx, cy, r=17, col=INK):
    """Транзистор-ключ: коло + виводи (колектор угорі, емітер унизу, база праворуч)."""
    out = circle(cx, cy, r, fill=BG, stroke=col, sw=2.2)
    out += line(cx, cy - r, cx, cy - r - 14, color=col, sw=2.2)   # колектор угору
    out += line(cx, cy + r, cx, cy + r + 14, color=col, sw=2.2)   # емітер униз
    out += line(cx + r, cy, cx + r + 16, cy, color=col, sw=2.2)   # база праворуч
    out += text(cx, cy + 4.5, "Q", size=12.5, color=col, bold=True)
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Фігура (proj) — автомат станів секвенсора передзаряду
# ─────────────────────────────────────────────────────────────────────────────
def fig_precharge_fsm():
    W, H = 1080, 600
    f = []

    def node(cx, cy, w, h, title, sub, col, fillc):
        out = rect(cx - w / 2, cy - h / 2, w, h, fill=fillc, stroke=col, sw=2.6, rx=13)
        out += text(cx, cy - 12, title, size=18, color=col, bold=True)
        out += mtext(cx, cy + 12, sub, size=12, color=INK, lh=1.28)
        return out

    IY, FY = 165, 450
    xi, xp, xr = 175, 540, 905
    wI, wP, wR = 214, 262, 210
    hN = 106

    f.append(node(xi, IY, wI, hN, "IDLE",
                  ["усе розімкнено —", "чекає команди «пуск»"], MUTED, "#f4f6f8"))
    f.append(node(xp, IY, wP, hN, "PRECHARGE",
                  ["Kпз замкнено · Kгол розімкнено", "R заряджає C, стежимо Uшини"],
                  FIELD, "#eafaf0"))
    f.append(node(xr, IY, wR, hN, "RUN",
                  ["Kгол замкнено,", "Kпз розімкнено"], NEG, "#eaf0fd"))
    f.append(node(xp, FY, wP, hN, "FAULT",
                  ["усе розімкнено · ЗАСУВ —", "потрібен скид оператора"], POS, "#fdecea"))

    # IDLE -> PRECHARGE
    ax1, ax2 = xi + wI / 2, xp - wP / 2
    f.append(arrow(ax1, IY, ax2, IY, color=INK, sw=2.6))
    f.append(text((ax1 + ax2) / 2, IY - 12, "пуск", size=13.5, color=INK, bold=True))

    # PRECHARGE -> RUN
    bx1, bx2 = xp + wP / 2, xr - wR / 2
    f.append(arrow(bx1, IY, bx2, IY, color=FIELD, sw=2.8))
    f.append(text((bx1 + bx2) / 2, IY - 28, "Uшини ≥ 95%·Uвх", size=12.5, color=FIELD, bold=True))
    f.append(text((bx1 + bx2) / 2, IY - 12, "→ Kгол ON, тоді Kпз OFF", size=10.5, color=MUTED))

    # PRECHARGE -> FAULT (вертикаль)
    f.append(arrow(xp, IY + hN / 2, xp, FY - hN / 2, color=POS, sw=2.8))
    my = (IY + hN / 2 + FY - hN / 2) / 2
    f.append(text(xp + 16, my - 7, "таймаут:", size=12.5, color=POS, bold=True, anchor="start"))
    f.append(text(xp + 16, my + 11, "шина не зарядилась", size=11.5, color=POS, anchor="start"))

    # RUN -> FAULT (діагональ)
    f.append(arrow(xr - wR / 2 + 4, IY + hN / 2, xp + wP / 2 + 6, FY - hN / 2 - 4,
                   color=POS, sw=2.0))
    f.append(text(xr - 18, FY - 84, "втрата шини /", size=11.5, color=POS, anchor="middle"))
    f.append(text(xr - 18, FY - 68, "неможливе значення", size=11.5, color=POS, anchor="middle"))

    # FAULT -> IDLE (діагональ угору-ліворуч)
    f.append(arrow(xp - wP / 2 - 6, FY - hN / 2 - 4, xi + 26, IY + hN / 2,
                   color=MUTED, sw=2.0))
    f.append(text(xi + 30, FY - 84, "скид +", size=11.5, color=MUTED, anchor="middle"))
    f.append(text(xi + 30, FY - 68, "витримка", size=11.5, color=MUTED, anchor="middle"))

    # легенда
    f.append(text(W / 2, H - 20,
                  "Kпз — передзарядне реле (в колі з резистором R) · Kгол — головний контактор",
                  size=12, color=MUTED))

    render(os.path.join(IMG, "precharge-fsm.svg"), W, H, *f,
           title="Автомат станів секвенсора передзаряду")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура (proj) — дві межі прошивки із залізом: вимір напруги і драйв котушок
# ─────────────────────────────────────────────────────────────────────────────
def fig_control_wiring():
    W, H = 1200, 600
    f = []

    # ── МК у центрі ──
    mx1, mx2, my1, my2 = 470, 730, 210, 400
    f.append(rect(mx1, my1, mx2 - mx1, my2 - my1, fill="#eef2f7", stroke=INK, sw=2.2, rx=12))
    f.append(text((mx1 + mx2) / 2, 290, "Мікроконтролер", size=16, color=INK, bold=True))
    f.append(text((mx1 + mx2) / 2, 314, "секвенсор передзаряду", size=11.5, color=MUTED))

    # ── ДРАЙВЕР котушки: coil -> Q -> gnd, база праворуч до GPIO, діод скиду ──
    def driver(cx, coil_top, label, gpio_y, gpio_pin):
        g = []
        ct = coil_top
        cb = ct + 46            # низ котушки
        # +12
        g.append(text(cx, ct - 25, "+12 В", size=11, color=INK, bold=True))
        g.append(line(cx, ct - 17, cx, ct, color=INK, sw=2.2))
        # котушка
        g.append(rect(cx - 22, ct, 44, 46, fill="#f0f3f7", stroke=INK, sw=2.0, rx=7))
        g.append(text(cx, ct + 28, label, size=12, color=INK, bold=True))
        # діод скиду ліворуч, паралельно котушці
        g.append(line(cx, ct, cx - 45, ct, color=INK, sw=2.0))
        g.append(diode_v(cx - 45, cb, ct))
        g.append(line(cx - 45, cb, cx, cb, color=INK, sw=2.0))
        g.append(text(cx - 60, (ct + cb) / 2 - 6, "діод", size=9.5, color=MUTED, anchor="end"))
        g.append(text(cx - 60, (ct + cb) / 2 + 8, "скиду", size=9.5, color=MUTED, anchor="end"))
        # транзистор
        qy = cb + 42
        g.append(line(cx, cb, cx, qy - 31, color=INK, sw=2.2))    # низ котушки -> колектор
        g.append(npn(cx, qy))
        g.append(line(cx, qy + 31, cx, qy + 78, color=INK, sw=2.2))  # емітер -> gnd
        g.append(gnd_sym(cx, qy + 78))
        # база -> Rб -> GPIO МК
        bx = cx + 33
        g.append(resistor(bx, bx + 52, qy, color=INK, sw=2.2, h=8))
        g.append(text(bx + 26, qy - 13, "Rб", size=10.5, color=INK, anchor="middle"))
        g.append(line(bx + 52, qy, 430, qy, color=INK, sw=2.2))
        g.append(line(430, qy, 430, gpio_y, color=INK, sw=2.2))
        g.append(line(430, gpio_y, gpio_pin, gpio_y, color=INK, sw=2.2))
        g.append(circle(gpio_pin, gpio_y, 3.2, fill=INK, stroke=INK))
        g.append(text(452, gpio_y - 8, "GPIO", size=10, color=NEG, anchor="middle", bold=True))
        return "".join(g)

    f.append(driver(250, 120, "Kпз", 250, mx1))
    f.append(driver(250, 320, "Kгол", 360, mx1))

    # ── СЕНСОР: дільник напруги -> вхід АЦП ──
    sx = 1010
    f.append(text(sx, 110, "шина +400 В", size=12, color=POS, bold=True))
    f.append(circle(sx, 126, 3.4, fill=INK, stroke=INK))
    f.append(line(sx, 126, sx, 150, color=INK, sw=2.2))
    # Rв
    f.append(rect(sx - 20, 150, 40, 58, fill=FILL, stroke=INK, sw=1.8, rx=6))
    f.append(text(sx, 184, "Rв", size=12, color=INK, bold=True))
    f.append(text(sx + 30, 172, "990 кОм", size=9.5, color=MUTED, anchor="start"))
    # відвід
    f.append(line(sx, 208, sx, 232, color=INK, sw=2.2))
    f.append(circle(sx, 220, 3.4, fill=INK, stroke=INK))
    # Rн
    f.append(rect(sx - 20, 232, 40, 58, fill=FILL, stroke=INK, sw=1.8, rx=6))
    f.append(text(sx, 266, "Rн", size=12, color=INK, bold=True))
    f.append(text(sx + 30, 254, "8.2 кОм", size=9.5, color=MUTED, anchor="start"))
    f.append(line(sx, 290, sx, 306, color=INK, sw=2.2))
    f.append(gnd_sym(sx, 306))
    # відвід -> АЦП
    f.append(line(sx, 220, 780, 220, color=NEG, sw=2.2))
    f.append(line(780, 220, 780, 250, color=NEG, sw=2.2))
    f.append(line(780, 250, 730, 250, color=NEG, sw=2.2))
    f.append(circle(730, 250, 3.2, fill=NEG, stroke=NEG))
    f.append(text(710, 246, "АЦП", size=11, color=NEG, anchor="end", bold=True))
    f.append(text(870, 210, "→ на вхід АЦП", size=11.5, color=NEG, bold=True))
    f.append(text(870, 228, "(діоди-обмежувачі на вході)", size=9.5, color=MUTED))
    # формула
    f.append(text(sx, 340, "Uадц = Uшини · Rн/(Rв+Rн)", size=11.5, color=INK))
    f.append(text(sx, 357, "≈ 3.3 В при повній шині", size=10.5, color=MUTED))

    render(os.path.join(IMG, "precharge-control-wiring.svg"), W, H, *f,
           title="Дві межі прошивки із залізом: вимір шини і драйв котушок")


if __name__ == "__main__":
    fig_topologies()
    fig_timing()
    fig_soa()
    fig_history_timeline()
    fig_gate_integrator()
    fig_energy_invariance()
    fig_precharge_fsm()
    fig_control_wiring()
    print("figs OK")
