# -*- coding: utf-8 -*-
"""Фігури до статті «Buck-boost».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

COIL = "#b5763a"   # колір котушки (мідь)


# ── спільні символи схеми ───────────────────────────────────────────────────
def vsource(cx, cy, label="Vвх", color=POS):
    """Джерело: кружок із «+»/«−» рисками, підпис над ним."""
    out = [circle(cx, cy, 10, fill=BG, stroke=color, sw=2.2)]
    out.append(line(cx - 5, cy, cx + 5, cy, color=color, sw=2.2))          # «−»
    out.append(line(cx, cy - 5, cx, cy + 5, color=color, sw=2.2))          # «+»
    out.append(text(cx, cy - 22, label, size=13, bold=True))
    return "".join(out)


def coil_h(x1, x2, y, color=COIL, sw=2.8):
    """Котушка дугами між x1 і x2 на висоті y (горизонтальна)."""
    n = 4
    step = (x2 - x1) / n
    r = step / 2
    d = "M %.1f %.1f " % (x1, y)
    for i in range(n):
        cx0 = x1 + step * i
        d += "A %.1f %.1f 0 0 1 %.1f %.1f " % (r, 10.0, cx0 + step, y)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, color, sw)


def coil_v(x, y1, y2, color=COIL, sw=2.8):
    """Котушка дугами між y1 і y2 на вертикалі x."""
    n = 4
    step = (y2 - y1) / n
    r = step / 2
    d = "M %.1f %.1f " % (x, y1)
    for i in range(n):
        cy0 = y1 + step * i
        d += "A %.1f %.1f 0 0 1 %.1f %.1f " % (10.0, r, x, cy0 + step)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, color, sw)


def diode(x, y, color=INK, sw=2.0):
    """Діод (трикутник + планка), провідність зліва направо, від x до x+22."""
    out = ['<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="none" '
           'stroke="%s" stroke-width="%.1f"/>' % (x, y - 11, x, y + 11, x + 22, y, color, sw)]
    out.append(line(x + 22, y - 11, x + 22, y + 11, color=color, sw=sw + 0.6))
    return "".join(out), x + 22


def diode_v(x, y, color=INK, sw=2.0, up=True):
    """Діод на вертикалі від y до y+22; провідність донизу (up=False) або вгору."""
    if up:   # провідність знизу вгору: трикутник вістрям угору
        out = ['<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="none" '
               'stroke="%s" stroke-width="%.1f"/>' % (x - 11, y + 22, x + 11, y + 22, x, y, color, sw)]
        out.append(line(x - 11, y, x + 11, y, color=color, sw=sw + 0.6))
    else:
        out = ['<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="none" '
               'stroke="%s" stroke-width="%.1f"/>' % (x - 11, y, x + 11, y, x, y + 22, color, sw)]
        out.append(line(x - 11, y + 22, x + 11, y + 22, color=color, sw=sw + 0.6))
    return "".join(out), y + 22


def cap_v(cx, y_top, y_bot, color=INK, sw=2.0):
    """Конденсатор двома планками між y_top..y_bot (вертикальна гілка)."""
    midhi, midlo = (y_top + y_bot) / 2 - 6, (y_top + y_bot) / 2 + 6
    out = [line(cx, y_top, cx, midhi, color=color, sw=sw)]
    out.append(line(cx - 15, midhi, cx + 15, midhi, color=color, sw=sw + 0.6))
    out.append(line(cx - 15, midlo, cx + 15, midlo, color=color, sw=sw + 0.6))
    out.append(line(cx, midlo, cx, y_bot, color=color, sw=sw))
    return "".join(out)


def cap_h(x_l, x_r, y, color=INK, sw=2.0, label=None):
    """Конденсатор двома планками між x_l..x_r (горизонтальна гілка)."""
    midl, midr = (x_l + x_r) / 2 - 6, (x_l + x_r) / 2 + 6
    out = [line(x_l, y, midl, y, color=color, sw=sw)]
    out.append(line(midl, y - 15, midl, y + 15, color=color, sw=sw + 0.6))
    out.append(line(midr, y - 15, midr, y + 15, color=color, sw=sw + 0.6))
    out.append(line(midr, y, x_r, y, color=color, sw=sw))
    if label:
        out.append(text((x_l + x_r) / 2, y - 22, label, size=12, bold=True))
    return "".join(out)


def load(x, y_top, y_bot, color=INK, sw=1.8):
    """Навантаження — прямокутник-резистор на вертикальній гілці."""
    out = [line(x, y_top, x, y_top + 12, color=color, sw=sw)]
    out.append(rect(x - 11, y_top + 12, 22, 50, fill="none", stroke=color, sw=sw, rx=0))
    out.append(line(x, y_top + 62, x, y_bot, color=color, sw=sw))
    return "".join(out)


def switch_box(cx, cy, on, label="", color_on=NEG, color_off=MUTED):
    """Ключ як квадратик: замкнений (товста риска) чи розімкнений (нахилена планка)."""
    c = color_on if on else color_off
    out = [rect(cx - 13, cy - 13, 26, 26, fill=BG, stroke=c, sw=1.8, rx=4)]
    if on:
        out.append(line(cx - 8, cy, cx + 8, cy, color=c, sw=3.0))
    else:
        out.append(line(cx - 8, cy + 6, cx + 8, cy - 6, color=c, sw=2.4))
    if label:
        out.append(text(cx, cy + 30, label, size=10.5, color=c, bold=True))
    return "".join(out)


# ── Фіг.1 — батарея перетинає ціль ──────────────────────────────────────────
def fig_problem():
    W, H = 900, 420
    f = [text(W / 2, 32, "Напруга банки перетинає вихідну ціль", size=18, bold=True)]
    ox, oy = 90, 330       # початок осей
    rx, ty = 800, 70
    out = [arrow(ox, oy + 6, ox, ty, color=INK), arrow(ox, oy, rx + 20, oy, color=INK)]
    out.append(text(ox - 8, ty + 8, "В", size=12, anchor="end", bold=True))
    out.append(text(rx + 24, oy + 4, "розряд →", size=11, color=MUTED, anchor="start"))

    vmin, vmax = 2.9, 4.3

    def Y(v):
        return oy - (v - vmin) / (vmax - vmin) * (oy - ty)

    for v, lab in [(3.0, "3.0"), (3.3, "3.3"), (3.7, "3.7"), (4.2, "4.2")]:
        yy = Y(v)
        out.append(line(ox, yy, rx, yy, color="#e4e4e4", sw=1))
        out.append(text(ox - 8, yy + 4, lab, size=10, color=MUTED, anchor="end"))

    # крива розряду LiPo 4.2 → 3.0
    pts = [(ox, 4.2), (ox + 42, 4.05), (ox + 140, 3.8), (ox + 350, 3.55),
           (ox + 525, 3.3), (ox + 616, 3.15), (ox + 672, 3.02), (ox + 700, 2.95)]
    poly = " ".join("%.1f,%.1f" % (x, Y(v)) for x, v in pts)
    out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3" '
               'stroke-linejoin="round" stroke-linecap="round"/>' % (poly, COIL))
    # ціль 3.3
    out.append(line(ox, Y(3.3), rx, Y(3.3), color=FIELD, sw=2.2, dash="7,5"))
    out.append(text(rx + 6, Y(3.3) + 4, "ціль 3.3 В", size=12, color=FIELD, anchor="start", bold=True))
    # точка перетину
    xc = ox + 525
    out.append(circle(xc, Y(3.3), 5, fill="#caa24a", stroke="#caa24a", sw=0))
    out.append(line(xc, oy, xc, Y(3.3), color=MUTED, sw=1.2, dash="4,4"))
    out.append(text(320, Y(3.3) - 95, "Vбат > ціль → ЗНИЖУВАТИ (buck)", size=12, color=NEG, bold=True))
    out.append(text(690, Y(3.3) + 36, "Vбат < ціль →", size=11.5, color=POS, bold=True))
    out.append(text(690, Y(3.3) + 52, "ПІДВИЩУВАТИ (boost)", size=11.5, color=POS, bold=True))
    out.append(fitbox(70, 382, 760, 26,
                      "Одна банка LiPo сповзає 4.2 → 3.0 В і перетинає 3.3 В: спершу треба знижувати, під кінець підвищувати. Чистий buck чи boost не покриє весь розряд",
                      size=11, fill="#fbf7ec", stroke="#caa24a"))
    f.extend(out)
    render(os.path.join(IMG, "problem.svg"), W, H, *f)


# ── Фіг.2 — інвертувальний buck-boost: дві фази ─────────────────────────────
def fig_inverting():
    W, H = 920, 440
    f = [text(W / 2, 30, "Інвертувальний buck-boost: котушка — єдиний місток", size=17, bold=True)]

    def panel(x0, title_txt, title_color, on):
        out = [rect(x0, 60, 400, 300, fill="none", stroke="#d8dde3", sw=2, rx=10)]
        out.append(text(x0 + 200, 84, title_txt, size=13, color=title_color, bold=True))
        yt, yb = 150, 300            # верхня гілка, земля
        vx = x0 + 32
        out.append(vsource(vx, yt))
        out.append(line(vx, yt + 10, vx, yb, color=INK, sw=2))
        out.append(line(vx, yt, x0 + 60, yt, color=INK, sw=2))
        # ключ (горизонтальний) від входу до вузла перемикання
        sw_on = on
        out.append(switch_box(x0 + 90, yt, sw_on, "ключ ВКЛ" if on else "ВИКЛ"))
        out.append(line(x0 + 103, yt, x0 + 150, yt, color=INK if on else MUTED, sw=2))
        node_sw = x0 + 150
        out.append(circle(node_sw, yt, 3.5, fill=INK, stroke=INK, sw=0))
        # котушка ВНИЗ від вузла перемикання до землі
        coil_color = FIELD if on else COIL
        out.append(coil_v(node_sw, yt, yb - 8, color=coil_color))
        out.append(line(node_sw, yb - 8, node_sw, yb, color=INK, sw=2))
        out.append(text(node_sw + 14, (yt + yb) / 2,
                        "котушка", size=11, color=coil_color, anchor="start", bold=True))
        # діод від вузла перемикання ПРАВОРУЧ до виходу; катод до котушки → вихід стає −
        dcolor = MUTED if on else FIELD
        out.append(line(node_sw, yt, x0 + 205, yt, color=dcolor, sw=2))
        # катод ліворуч (планка), вістря праворуч → струм може текти лише з виходу в котушку
        out.append(line(x0 + 205, yt - 11, x0 + 205, yt + 11, color=dcolor, sw=dcolor and 2.6))
        out.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="none" '
                   'stroke="%s" stroke-width="2.0"/>' % (x0 + 227, yt - 11, x0 + 227, yt + 11, x0 + 205, yt, dcolor))
        if on:   # закритий діод — перекреслити
            out.append(line(x0 + 201, yt - 16, x0 + 231, yt + 14, color=POS, sw=2.4))
        out.append(text(x0 + 216, yt - 18, "діод", size=10.5, color=dcolor))
        node_out = x0 + 300
        out.append(line(x0 + 227, yt, node_out, yt, color=dcolor, sw=2))
        out.append(circle(node_out, yt, 3.5, fill=INK, stroke=INK, sw=0))
        out.append(cap_v(node_out, yt, yb))
        out.append(line(node_out, yt, x0 + 350, yt, color=INK, sw=2))
        out.append(load(x0 + 350, yt, yb))
        out.append(text(x0 + 352, yt - 6, "Vвих<0", size=11.5, color=NEG, anchor="start", bold=True))
        out.append(line(node_sw, yb, x0 + 350, yb, color=INK, sw=2))
        out.append(line(vx, yb, node_sw, yb, color=INK, sw=2))
        cap_txt = ("вхід заганяє струм у котушку; вихід живить лише C"
                   if on else "котушка тягне струм З виходу → вузол стає від'ємним")
        out.append(fitbox(x0 + 12, 330, 376, 24, cap_txt, size=10, fill=BG, stroke="#d8dde3"))
        return "".join(out)

    f.append(panel(20, "ФАЗА ВКЛ (ключ замкнено)", NEG, True))
    f.append(panel(500, "ФАЗА ВИКЛ (ключ розімкнено)", MUTED, False))
    f.append(fitbox(70, 400, 780, 28,
                    "Вхід і вихід ніколи не з'єднані напряму — усе переносить котушка; геометрія робить вихід ВІД'ЄМНИМ",
                    size=11.5, fill="#eaf0fd", stroke=NEG))
    render(os.path.join(IMG, "inverting.svg"), W, H, *f)


# ── Фіг.3 — коефіцієнт D/(1−D) ──────────────────────────────────────────────
def fig_ratio():
    W, H = 900, 420
    f = [text(W / 2, 30, "Коефіцієнт buck-boost: |Vвих| / Vвх = D / (1 − D)", size=17, bold=True)]
    ox, oy = 110, 340
    rx, ty = 800, 80
    ymax = 4.0
    out = [arrow(ox, oy, ox, ty, color=INK), arrow(ox, oy, rx + 20, oy, color=INK)]
    out.append(text(ox - 10, ty + 8, "|Vвих|/Vвх", size=12, anchor="end", bold=True))
    out.append(text(rx + 24, oy + 4, "D", size=12, anchor="start", bold=True))

    def Y(v):
        return oy - v / ymax * (oy - ty)

    def X(d):
        return ox + d * (rx - ox)

    for v in range(0, 5):
        yy = Y(v)
        out.append(line(ox, yy, rx, yy, color="#e4e4e4", sw=1))
        out.append(text(ox - 8, yy + 4, "%d×" % v, size=10.5, color=MUTED, anchor="end"))
    for d in (0.0, 0.25, 0.5, 0.75):
        xx = X(d)
        out.append(line(xx, oy, xx, oy + 5, color=MUTED, sw=1.2))
        out.append(text(xx, oy + 20, "%.2f" % d, size=10.5, color=MUTED))
    # лінія «=Vвх» на 1×
    out.append(line(ox, Y(1), rx, Y(1), color=MUTED, sw=1.2, dash="5,5"))
    # межа D=0.5
    out.append(line(X(0.5), oy, X(0.5), ty + 10, color=NEG, sw=1.4, dash="5,5"))
    out.append(text(X(0.5) + 6, ty + 26, "D=0.5: вихід = вхід", size=10.5, color=NEG, bold=True))
    # крива D/(1−D)
    pts = []
    d = 0.0
    while d <= 0.82:
        v = d / (1.0 - d)
        if v > ymax:
            break
        pts.append("%.1f,%.1f" % (X(d), Y(v)))
        d += 0.01
    out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3" '
               'stroke-linejoin="round" stroke-linecap="round"/>' % (" ".join(pts), COIL))
    # зони знижує / підвищує
    out.append(text(X(0.25), Y(0.33) + 26, "D<0.5 → ЗНИЖУЄ", size=11, color=NEG, bold=True))
    out.append(text(X(0.68), Y(2.0) - 12, "D>0.5 → ПІДВИЩУЄ", size=11, color=POS, bold=True))
    for d, lbl in [(0.5, "0.5 → 1×"), (2 / 3, "0.67 → 2×"), (0.75, "0.75 → 3×")]:
        v = d / (1 - d)
        out.append(circle(X(d), Y(v), 4, fill=COIL, stroke=COIL, sw=0))
        out.append(text(X(d) + 8, Y(v) - 6, lbl, size=10, anchor="start", bold=True))
    out.append(fitbox(70, 384, 760, 26,
                      "Одна топологія покриває обидва напрямки: нижче D=0.5 знижує, вище — підвищує. Рівно те, що треба батареї, яка перетинає ціль",
                      size=11, fill="#eef8ef", stroke=FIELD))
    f.extend(out)
    render(os.path.join(IMG, "ratio.svg"), W, H, *f)


# ── Фіг.4 — неінвертувальний 4-ключовий ─────────────────────────────────────
def fig_fourswitch():
    W, H = 920, 430
    f = [text(W / 2, 30, "Неінвертувальний 4-ключовий: додатний вихід вгору й вниз", size=17, bold=True)]
    out = []
    yt, yb = 150, 300
    # вузли
    vx = 70
    xL = 250          # лівий вузол перемикання (ліве плече)
    xR = 620          # правий вузол перемикання (праве плече)
    out.append(vsource(vx, yt))
    out.append(line(vx, yt + 10, vx, yb, color=INK, sw=2))
    out.append(line(vx, yt, xL, yt, color=INK, sw=2))
    # ЛІВЕ плече: верхній ключ (вхід→вузол), нижній ключ (вузол→земля)
    out.append(switch_box((vx + xL) / 2, yt, True, "Q1"))
    out.append(circle(xL, yt, 3.5, fill=INK, stroke=INK, sw=0))
    out.append(switch_box(xL, (yt + yb) / 2 + 8, False, ""))
    out.append(text(xL - 22, (yt + yb) / 2 + 12, "Q2", size=10.5, color=MUTED, anchor="end", bold=True))
    out.append(line(xL, yt, xL, (yt + yb) / 2 - 5, color=INK, sw=2))
    out.append(line(xL, (yt + yb) / 2 + 21, xL, yb, color=INK, sw=2))
    out.append(text((vx + xL) / 2, yt - 30, "ліве плече", size=11, color=NEG, bold=True))
    # котушка між лівим і правим вузлами
    out.append(coil_h(xL, xR, yt))
    # ПРАВЕ плече
    out.append(circle(xR, yt, 3.5, fill=INK, stroke=INK, sw=0))
    out.append(switch_box((xR + 800) / 2, yt, True, "Q4"))
    out.append(line(xR, yt, (xR + 800) / 2 - 13, yt, color=INK, sw=2))
    out.append(switch_box(xR, (yt + yb) / 2 + 8, False, ""))
    out.append(text(xR + 22, (yt + yb) / 2 + 12, "Q3", size=10.5, color=MUTED, anchor="start", bold=True))
    out.append(line(xR, yt, xR, (yt + yb) / 2 - 5, color=INK, sw=2))
    out.append(line(xR, (yt + yb) / 2 + 21, xR, yb, color=INK, sw=2))
    out.append(text((xR + 800) / 2, yt - 30, "праве плече", size=11, color=POS, bold=True))
    # вихід
    node_out = 800
    out.append(line((xR + 800) / 2 + 13, yt, node_out, yt, color=INK, sw=2))
    out.append(circle(node_out, yt, 3.5, fill=INK, stroke=INK, sw=0))
    out.append(cap_v(node_out, yt, yb))
    out.append(line(node_out, yt, node_out + 50, yt, color=INK, sw=2))
    out.append(load(node_out + 50, yt, yb))
    out.append(text(node_out + 52, yt - 6, "Vвих>0", size=11.5, color=POS, anchor="start", bold=True))
    out.append(line(vx, yb, node_out + 50, yb, color=INK, sw=2))
    # три режими — картки
    modes = [
        ("Vвх > Vвих", "buck: ліве плече перемикає,", "праве тримає прохід", NEG),
        ("Vвх ≈ Vвих", "змішаний: усі чотири", "працюють злагоджено", MUTED),
        ("Vвх < Vвих", "boost: праве плече перемикає,", "ліве тримає прохід", POS),
    ]
    xs = [40, 330, 620]
    for x0, (cond, l1, l2, c) in zip(xs, modes):
        out.append(rect(x0, 336, 270, 64, fill=BG, stroke=c, sw=1.6, rx=8))
        out.append(text(x0 + 135, 356, cond, size=12, color=c, bold=True))
        out.append(text(x0 + 135, 374, l1, size=10, color=INK))
        out.append(text(x0 + 135, 390, l2, size=10, color=INK))
    f.extend(out)
    render(os.path.join(IMG, "fourswitch.svg"), W, H, *f)


# ── Фіг.5 — SEPIC якісно ────────────────────────────────────────────────────
def fig_sepic():
    W, H = 920, 420
    f = [text(W / 2, 30, "SEPIC: звʼязувальний Cs розриває постійний шлях", size=17, bold=True)]
    out = []
    yt, yb = 150, 320
    vx = 70
    out.append(vsource(vx, yt))
    out.append(line(vx, yt + 10, vx, yb, color=INK, sw=2))
    out.append(line(vx, yt, 110, yt, color=INK, sw=2))
    # L1 на вході
    out.append(coil_h(110, 230, yt))
    out.append(text(170, yt - 16, "L1", size=12, color=COIL, bold=True))
    node1 = 260
    out.append(line(230, yt, node1, yt, color=INK, sw=2))
    out.append(circle(node1, yt, 3.5, fill=INK, stroke=INK, sw=0))
    # ключ донизу від node1
    out.append(switch_box(node1, (yt + yb) / 2 + 6, True, "ключ"))
    out.append(line(node1, yt, node1, (yt + yb) / 2 - 7, color=INK, sw=2))
    out.append(line(node1, (yt + yb) / 2 + 19, node1, yb, color=INK, sw=2))
    # Cs послідовно праворуч (звʼязувальний)
    out.append(cap_h(node1, 420, yt, color=POS, label="Cs"))
    node2 = 450
    out.append(line(420, yt, node2, yt, color=INK, sw=2))
    out.append(circle(node2, yt, 3.5, fill=INK, stroke=INK, sw=0))
    out.append(text(node1 + 80, yt + 26, "не пропускає DC", size=10.5, color=POS, bold=True))
    # L2 від node2 донизу на землю
    out.append(coil_v(node2, yt, yb - 8, color=COIL))
    out.append(line(node2, yb - 8, node2, yb, color=INK, sw=2))
    out.append(text(node2 + 14, (yt + yb) / 2, "L2", size=12, color=COIL, anchor="start", bold=True))
    # діод від node2 праворуч до виходу
    out.append(line(node2, yt, 520, yt, color=INK, sw=2))
    dfrag, dend = diode(520, yt, color=INK)
    out.append(dfrag)
    out.append(text(531, yt - 16, "діод", size=10.5))
    node_out = 640
    out.append(line(dend, yt, node_out, yt, color=INK, sw=2))
    out.append(circle(node_out, yt, 3.5, fill=INK, stroke=INK, sw=0))
    out.append(cap_v(node_out, yt, yb))
    out.append(line(node_out, yt, node_out + 50, yt, color=INK, sw=2))
    out.append(load(node_out + 50, yt, yb))
    out.append(text(node_out + 52, yt - 6, "Vвих>0", size=11.5, color=POS, anchor="start", bold=True))
    out.append(line(vx, yb, node_out + 50, yb, color=INK, sw=2))
    out.append(fitbox(70, 360, 780, 50,
                      "Дві котушки (L1 на вході, L2 на землю) і послідовний конденсатор Cs між ними.\n"
                      "Cs не пропускає постійний струм — тож прямого шляху вхід → вихід НЕМАЄ:\n"
                      "на відміну від boost, SEPIC по-справжньому вимикається й переживає КЗ на виході",
                      size=11, fill="#eef8ef", stroke=FIELD))
    f.extend(out)
    render(os.path.join(IMG, "sepic.svg"), W, H, *f)


# ── Фіг.6 — чотири топології поряд ──────────────────────────────────────────
def fig_compare():
    W, H = 920, 430
    f = [text(W / 2, 30, "Чотири топології поряд: за універсальність платять складністю", size=17, bold=True)]
    out = []
    # таблиця-картки: топологія | напрямок | полярність | захист виходу | складність
    rows = [
        ("buck", "лише вниз", "додатна", "так", "проста", NEG),
        ("boost", "лише вгору", "додатна", "НІ (прозорий для КЗ)", "проста", POS),
        ("інвертувальний\nbuck-boost", "вгору й вниз", "ВІД'ЄМНА", "так", "проста", COIL),
        ("4-ключовий\nbuck-boost", "вгору й вниз", "додатна", "так", "складний", FIELD),
        ("SEPIC", "вгору й вниз", "додатна", "так (Cs)", "складний", "#7e57c2"),
    ]
    cols = ["топологія", "напрямок", "полярність", "захист виходу", "складність"]
    cx = [40, 230, 400, 560, 760]
    cw = [190, 170, 160, 200, 130]
    y0 = 70
    rh = 62
    # заголовок
    for c, x, w in zip(cols, cx, cw):
        out.append(text(x + w / 2, y0 + 4, c, size=12, color=MUTED, bold=True))
    yy = y0 + 18
    for name, dirn, pol, prot, cmpx, col in rows:
        out.append(line(40, yy, 890, yy, color="#e4e4e4", sw=1))
        cy = yy + rh / 2 + 4
        # назва (може бути 2 рядки)
        nlines = name.split("\n")
        ny = cy - (len(nlines) - 1) * 7
        for i, ln in enumerate(nlines):
            out.append(text(cx[0] + cw[0] / 2, ny + i * 15, ln, size=12.5, color=col, bold=True))
        out.append(text(cx[1] + cw[1] / 2, cy, dirn, size=11.5))
        pol_color = NEG if "ВІД" in pol else INK
        out.append(text(cx[2] + cw[2] / 2, cy, pol, size=11.5, color=pol_color,
                        bold="ВІД" in pol))
        prot_color = POS if prot.startswith("НІ") else INK
        # захист може бути довгим — fitbox
        out.append(fitbox(cx[3], cy - 12, cw[3], 22, prot, size=11, fill=BG,
                          stroke=BG, color=prot_color, bold=prot.startswith("НІ")))
        out.append(text(cx[4] + cw[4] / 2, cy, cmpx, size=11.5,
                        color=POS if cmpx == "складний" else FIELD, bold=True))
        yy += rh
    out.append(line(40, yy, 890, yy, color="#e4e4e4", sw=1))
    out.append(fitbox(70, yy + 10, 780, 26,
                      "boost — єдиний, хто не вміє розірвати шлях до власного виходу; за хід в обидва боки платять полярністю або зайвими деталями",
                      size=11, fill="#fbe9e7", stroke=POS))
    f.extend(out)
    render(os.path.join(IMG, "compare.svg"), W, H, *f)


# ── Фіг.7 — інтегрований buck-boost IC: блок-схема ──────────────────────────
def fig_ic_block():
    W, H = 940, 470
    f = [text(W / 2, 30, "Інтегрований buck-boost: чотири ключі всередині, одна котушка зовні",
              size=17, bold=True)]
    out = []
    # корпус IC
    out.append(rect(250, 195, 440, 177, fill="#fafbfc", stroke="#9aa3ad", sw=2.2, rx=12))
    out.append(text(470, 214, "один кристал", size=11, color=MUTED))
    out.append(text(360, 214, "ліве плече", size=11, color=NEG, bold=True))
    out.append(text(580, 214, "праве плече", size=11, color=POS, bold=True))
    # два півмостові «плечі» — кожне з парою FET-значків
    out.append(rect(315, 222, 90, 108, fill=BG, stroke="#cdd3da", sw=1.6, rx=8))
    out.append(rect(535, 222, 90, 108, fill=BG, stroke="#cdd3da", sw=1.6, rx=8))
    out.append(switch_box(360, 252, False))
    out.append(switch_box(360, 300, False))
    out.append(switch_box(580, 252, False))
    out.append(switch_box(580, 300, False))
    out.append(text(338, 256, "Q1", size=10, color=MUTED, anchor="end", bold=True))
    out.append(text(338, 304, "Q2", size=10, color=MUTED, anchor="end", bold=True))
    out.append(text(602, 256, "Q4", size=10, color=POS, anchor="start", bold=True))
    out.append(text(602, 304, "Q3", size=10, color=POS, anchor="start", bold=True))
    # SW-відводи вгору до СПІЛЬНОЇ котушки
    out.append(line(360, 222, 360, 150, color=INK, sw=2))
    out.append(line(580, 222, 580, 150, color=INK, sw=2))
    out.append(circle(360, 222, 3.2, fill=INK, stroke=INK, sw=0))
    out.append(circle(580, 222, 3.2, fill=INK, stroke=INK, sw=0))
    out.append(coil_h(360, 580, 150))
    out.append(text(470, 134, "одна котушка L", size=12, color=COIL, bold=True))
    out.append(text(351, 184, "SW1", size=11, color=INK, anchor="end", bold=True))
    out.append(text(589, 184, "SW2", size=11, color=INK, anchor="start", bold=True))
    # контролер у центрі
    out.append(rect(425, 248, 90, 82, fill="#eef2f7", stroke="#9aa3ad", sw=1.6, rx=8))
    out.append(mtext(470, 280, ["контролер,", "драйвери,", "логіка режиму"], size=10, color=INK))
    out.append(line(425, 270, 405, 270, color=MUTED, sw=1.3, dash="4,3"))
    out.append(line(515, 270, 535, 270, color=MUTED, sw=1.3, dash="4,3"))
    # VIN ліворуч + вхідний конденсатор
    out.append(line(150, 265, 315, 265, color=INK, sw=2))
    out.append(text(140, 269, "VIN", size=12, color=INK, anchor="end", bold=True))
    out.append(circle(210, 265, 3.2, fill=INK, stroke=INK, sw=0))
    out.append(cap_v(210, 265, 430))
    # VOUT праворуч + вихідний конденсатор
    out.append(line(625, 265, 800, 265, color=INK, sw=2))
    out.append(text(810, 269, "VOUT", size=12, color=INK, anchor="start", bold=True))
    out.append(circle(745, 265, 3.2, fill=INK, stroke=INK, sw=0))
    out.append(cap_v(745, 265, 430))
    # земляна шина
    out.append(line(180, 430, 770, 430, color=INK, sw=2.4))
    # сигнальні ніжки знизу
    for x, lab in [(405, "FB"), (460, "EN"), (525, "MODE"), (600, "PG")]:
        out.append(line(x, 372, x, 405, color=INK, sw=2))
        out.append(text(x, 420, lab, size=11, color=INK, bold=True))
    # ніжка землі
    out.append(line(300, 372, 300, 430, color=INK, sw=2))
    out.append(text(286, 396, "GND", size=11, color=INK, anchor="end", bold=True))
    out.append(fitbox(150, 442, 640, 24,
                      "Обидва кінці котушки — вузли перемикання SW1/SW2: напряму вхід із виходом не зʼєднані, усе несе одна котушка",
                      size=11, fill="#fbf7ec", stroke="#caa24a"))
    f.extend(out)
    render(os.path.join(IMG, "ic-block.svg"), W, H, *f)


# ── Фіг.8 — провал ефективності в перехідній зоні ───────────────────────────
def fig_eff_dip():
    W, H = 900, 420
    f = [text(W / 2, 30, "Перехідна зона: ефективність провисає при Vвх ≈ Vвих", size=17, bold=True)]
    ox, oy = 110, 330
    rx, ty = 800, 80
    out = [arrow(ox, oy, ox, ty, color=INK), arrow(ox, oy, rx + 20, oy, color=INK)]
    out.append(text(ox - 10, ty + 8, "ККД, %", size=12, anchor="end", bold=True))
    out.append(text(rx + 24, oy + 4, "Vвх", size=12, anchor="start", bold=True))
    emin, emax = 84.0, 98.0
    vmin, vmax = 2.4, 5.6

    def Y(e):
        return oy - (e - emin) / (emax - emin) * (oy - ty)

    def X(v):
        return ox + (v - vmin) / (vmax - vmin) * (rx - ox)

    for e in (85, 88, 91, 94, 97):
        out.append(line(ox, Y(e), rx, Y(e), color="#e4e4e4", sw=1))
        out.append(text(ox - 8, Y(e) + 4, "%d" % e, size=10.5, color=MUTED, anchor="end"))
    for v in (2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5):
        out.append(line(X(v), oy, X(v), oy + 5, color=MUTED, sw=1.2))
        out.append(text(X(v), oy + 20, "%.1f" % v, size=10.5, color=MUTED))
    # Vвих = 3.3 В — межа buck/boost
    out.append(line(X(3.3), oy, X(3.3), ty + 16, color=FIELD, sw=1.6, dash="6,5"))
    out.append(text(X(3.3), ty + 10, "Vвих = 3.3 В", size=11, color=FIELD, bold=True))
    # крива ККД
    pts = [(5.5, 96.5), (5.0, 96.6), (4.5, 96.3), (4.0, 95.6), (3.75, 94.8), (3.55, 92.8),
           (3.4, 90.6), (3.3, 89.6), (3.2, 90.4), (3.05, 92.0), (2.85, 93.4), (2.6, 93.9), (2.4, 94.0)]
    poly = " ".join("%.1f,%.1f" % (X(v), Y(e)) for v, e in pts)
    out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3" '
               'stroke-linejoin="round" stroke-linecap="round"/>' % (poly, COIL))
    out.append(circle(X(3.3), Y(89.6), 4.5, fill=POS, stroke=POS, sw=0))
    out.append(text(X(3.3), Y(89.6) + 24, "усі 4 ключі клацають", size=10.5, color=POS, bold=True))
    out.append(text(X(4.7), Y(97) - 10, "BUCK (Vвх > Vвих)", size=11, color=NEG, bold=True))
    out.append(text(X(2.75), Y(94) - 14, "BOOST (Vвх < Vвих)", size=11, color=POS, bold=True))
    out.append(fitbox(70, 364, 760, 42,
                      "У чистому buck чи boost працює лише одне плече — ККД високий.\n"
                      "У зоні Vвх ≈ Vвих модулюють усі чотири ключі, і втрати на перемиканні дають провал",
                      size=11, fill="#fbe9e7", stroke=POS))
    f.extend(out)
    render(os.path.join(IMG, "eff-dip.svg"), W, H, *f)


if __name__ == "__main__":
    fig_problem()
    fig_inverting()
    fig_ratio()
    fig_fourswitch()
    fig_sepic()
    fig_compare()
    fig_ic_block()
    fig_eff_dip()
    print("OK: 8 фігур у", IMG)
