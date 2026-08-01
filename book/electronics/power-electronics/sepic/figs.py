# -*- coding: utf-8 -*-
"""Фігури до статті «SEPIC-перетворювач».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники нижчого рівня — зі спільного svgkit (НЕ переписувати його тут);
локальні символи схеми (котушка, діод, конденсатор, ключ) — місцеві."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

COIL = "#b5763a"   # колір котушки (мідь)


# ── локальні символи схеми ──────────────────────────────────────────────────
def vsource(cx, cy, label="Vвх", color=POS):
    out = [circle(cx, cy, 10, fill=BG, stroke=color, sw=2.2)]
    out.append(line(cx - 5, cy, cx + 5, cy, color=color, sw=2.2))
    out.append(line(cx, cy - 5, cx, cy + 5, color=color, sw=2.2))
    out.append(text(cx, cy - 22, label, size=13, bold=True))
    return "".join(out)


def coil_h(x1, x2, y, color=COIL, sw=2.8):
    n = 4
    step = (x2 - x1) / n
    r = step / 2
    d = "M %.1f %.1f " % (x1, y)
    for i in range(n):
        cx0 = x1 + step * i
        d += "A %.1f %.1f 0 0 1 %.1f %.1f " % (r, 10.0, cx0 + step, y)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, color, sw)


def coil_v(x, y1, y2, color=COIL, sw=2.8):
    n = 4
    step = (y2 - y1) / n
    r = step / 2
    d = "M %.1f %.1f " % (x, y1)
    for i in range(n):
        cy0 = y1 + step * i
        d += "A %.1f %.1f 0 0 1 %.1f %.1f " % (10.0, r, x, cy0 + step)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, color, sw)


def diode(x, y, color=INK, sw=2.0):
    """Діод: трикутник + планка, провідність зліва направо, від x до x+22."""
    out = ['<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="none" '
           'stroke="%s" stroke-width="%.1f"/>' % (x, y - 11, x, y + 11, x + 22, y, color, sw)]
    out.append(line(x + 22, y - 11, x + 22, y + 11, color=color, sw=sw + 0.6))
    return "".join(out), x + 22


def cap_v(cx, y_top, y_bot, color=INK, sw=2.0):
    midhi, midlo = (y_top + y_bot) / 2 - 6, (y_top + y_bot) / 2 + 6
    out = [line(cx, y_top, cx, midhi, color=color, sw=sw)]
    out.append(line(cx - 15, midhi, cx + 15, midhi, color=color, sw=sw + 0.6))
    out.append(line(cx - 15, midlo, cx + 15, midlo, color=color, sw=sw + 0.6))
    out.append(line(cx, midlo, cx, y_bot, color=color, sw=sw))
    return "".join(out)


def cap_h(x_l, x_r, y, color=INK, sw=2.0):
    midl, midr = (x_l + x_r) / 2 - 6, (x_l + x_r) / 2 + 6
    out = [line(x_l, y, midl, y, color=color, sw=sw)]
    out.append(line(midl, y - 15, midl, y + 15, color=color, sw=sw + 0.6))
    out.append(line(midr, y - 15, midr, y + 15, color=color, sw=sw + 0.6))
    out.append(line(midr, y, x_r, y, color=color, sw=sw))
    return "".join(out)


def load(x, y_top, y_bot, color=INK, sw=1.8):
    out = [line(x, y_top, x, y_top + 12, color=color, sw=sw)]
    out.append(rect(x - 11, y_top + 12, 22, 50, fill="none", stroke=color, sw=sw, rx=0))
    out.append(line(x, y_top + 62, x, y_bot, color=color, sw=sw))
    return "".join(out)


def switch_box(cx, cy, on, label="", color_on=NEG, color_off=MUTED):
    c = color_on if on else color_off
    out = [rect(cx - 13, cy - 13, 26, 26, fill=BG, stroke=c, sw=1.8, rx=4)]
    if on:
        out.append(line(cx - 8, cy, cx + 8, cy, color=c, sw=3.0))
    else:
        out.append(line(cx - 8, cy + 6, cx + 8, cy - 6, color=c, sw=2.4))
    if label:
        out.append(text(cx, cy + 32, label, size=11, color=c, bold=True))
    return "".join(out)


def cross(x, y, color=POS):
    """Червоний хрестик «закрито» поверх елемента."""
    return (line(x - 15, y - 15, x + 15, y + 15, color=color, sw=2.6) +
            line(x - 15, y + 15, x + 15, y - 15, color=color, sw=2.6))


# ── Фіг.1 — топологія ───────────────────────────────────────────────────────
def fig_topology():
    W, H = 960, 440
    f = [text(W / 2, 30, "SEPIC: дві котушки й послідовний конденсатор Cs", size=17, bold=True)]
    out = []
    yt, yb = 180, 350
    vx = 70
    out.append(vsource(vx, yt))
    out.append(line(vx, yt + 10, vx, yb, color=INK, sw=2))
    out.append(line(vx, yt, 112, yt, color=INK, sw=2))
    # L1
    out.append(coil_h(112, 242, yt))
    out.append(text(177, yt - 18, "L1", size=13, color=COIL, bold=True))
    node1 = 278
    out.append(line(242, yt, node1, yt, color=INK, sw=2))
    out.append(circle(node1, yt, 3.5, fill=INK, stroke=INK, sw=0))
    # ключ донизу від node1
    midy = (yt + yb) / 2 + 4
    out.append(line(node1, yt, node1, midy - 13, color=INK, sw=2))
    out.append(switch_box(node1, midy, True, "", color_on=INK))
    out.append(text(node1 - 20, midy + 4, "ключ Q", size=12, anchor="end", bold=True))
    out.append(line(node1, midy + 13, node1, yb, color=INK, sw=2))
    # Cs послідовно
    out.append(cap_h(node1, 442, yt, color=POS))
    out.append(text(360, yt - 20, "Cs", size=13, color=POS, bold=True))
    out.append(text(360, yt + 30, "= Vвх, не пропускає DC", size=11, color=POS, bold=True))
    node2 = 480
    out.append(line(442, yt, node2, yt, color=INK, sw=2))
    out.append(circle(node2, yt, 3.5, fill=INK, stroke=INK, sw=0))
    # L2 донизу
    out.append(coil_v(node2, yt, yb - 8))
    out.append(line(node2, yb - 8, node2, yb, color=INK, sw=2))
    out.append(text(node2 + 16, (yt + yb) / 2 + 4, "L2", size=13, color=COIL, anchor="start", bold=True))
    # діод праворуч від node2
    out.append(line(node2, yt, 524, yt, color=INK, sw=2))
    dfrag, dend = diode(524, yt, color=INK)
    out.append(dfrag)
    out.append(text(535, yt - 16, "діод D", size=12, bold=True))
    node_out = 668
    out.append(line(dend, yt, node_out, yt, color=INK, sw=2))
    out.append(circle(node_out, yt, 3.5, fill=INK, stroke=INK, sw=0))
    out.append(cap_v(node_out, yt, yb))
    out.append(text(node_out + 16, (yt + yb) / 2 + 4, "Cвих", size=11, color=MUTED, anchor="start"))
    out.append(line(node_out, yt, 718, yt, color=INK, sw=2))
    out.append(load(718, yt, yb))
    out.append(text(720, yt - 8, "Vвих > 0", size=12.5, color=POS, anchor="start", bold=True))
    # земля
    out.append(line(vx, yb, 718, yb, color=INK, sw=2))
    out.append(text(node_out / 2 + 40, yb + 18, "спільна земля", size=10.5, color=MUTED))
    # підпис-висновок
    out.append(fitbox(80, 388, 800, 42,
                      "Послідовний Cs розриває постійний шлях вхід→вихід (на відміну від boost): "
                      "SEPIC вимикається начисто й переживає коротке на виході.\n"
                      "Друга котушка L2 дає діоду й навантаженню зворотний шлях до землі після конденсатора",
                      size=11, fill="#eef8ef", stroke=FIELD))
    f.extend(out)
    render(os.path.join(IMG, "topology.svg"), W, H, *f)


# ── Фіг.2 — два такти ───────────────────────────────────────────────────────
def fig_phases():
    W, H = 980, 480
    f = [text(W / 2, 30, "Два такти SEPIC: як енергія доходить до виходу", size=17, bold=True)]

    def panel(x0, title_txt, title_color, on):
        act = FIELD          # активний (провідний) шлях — зелений
        idle = "#c7ccd2"     # неактивна вітка — світло-сіра
        out = [rect(x0, 58, 452, 336, fill="none", stroke="#d8dde3", sw=2, rx=10)]
        out.append(text(x0 + 226, 84, title_txt, size=13, color=title_color, bold=True))
        yt, yb = 190, 336
        vx = x0 + 42
        out.append(vsource(vx, yt))
        out.append(line(vx, yt + 10, vx, yb, color=INK, sw=2))
        # L1 завжди проводить
        out.append(line(vx, yt, x0 + 66, yt, color=act, sw=2.6))
        out.append(coil_h(x0 + 66, x0 + 156, yt, color=act, sw=3.0))
        node1 = x0 + 190
        out.append(line(x0 + 156, yt, node1, yt, color=act, sw=2.6))
        out.append(circle(node1, yt, 3.5, fill=INK, stroke=INK, sw=0))
        midy = (yt + yb) / 2
        # ключ донизу
        sw_col = act if on else idle
        out.append(line(node1, yt, node1, midy - 13, color=sw_col, sw=2.6 if on else 2))
        out.append(switch_box(node1, midy, on, "", color_on=act, color_off=MUTED))
        out.append(text(node1 - 20, midy + 4, "замкнено" if on else "розімкнено",
                        size=11, color=act if on else MUTED, anchor="end", bold=True))
        out.append(line(node1, midy + 13, node1, yb, color=sw_col, sw=2.6 if on else 2))
        # Cs
        cs_col = POS
        out.append(cap_h(node1, x0 + 288, yt, color=cs_col))
        out.append(text((node1 + x0 + 288) / 2, yt - 18, "Cs", size=12, color=POS, bold=True))
        node2 = x0 + 320
        # у такті ВКЛ Cs→L2 активні; у ВИКЛ L1→Cs→діод активні (обидва такти Cs проводить)
        out.append(line(x0 + 288, yt, node2, yt, color=act, sw=2.6))
        out.append(circle(node2, yt, 3.5, fill=INK, stroke=INK, sw=0))
        # L2 завжди проводить
        out.append(coil_v(node2, yt, yb - 8, color=act, sw=3.0))
        out.append(line(node2, yb - 8, node2, yb, color=act, sw=2.6))
        out.append(text(node2 + 15, midy + 6, "L2", size=12, color=COIL, anchor="start", bold=True))
        # діод
        d_col = idle if on else act
        out.append(line(node2, yt, x0 + 356, yt, color=d_col, sw=2.6 if not on else 2))
        dfrag, dend = diode(x0 + 356, yt, color=d_col)
        out.append(dfrag)
        node_out = x0 + 410
        out.append(line(dend, yt, node_out, yt, color=d_col, sw=2.6 if not on else 2))
        out.append(circle(node_out, yt, 3.5, fill=INK, stroke=INK, sw=0))
        out.append(cap_v(node_out, yt, yb, color=INK))
        out.append(text(node_out + 8, yt - 8, "Vвих", size=11.5, color=POS, anchor="start", bold=True))
        out.append(line(vx, yb, node_out, yb, color=INK, sw=2))
        if on:
            out.append(cross(x0 + 367, yt))     # діод закрито
            note = "Вхід заряджає L1,\nCs розряджається в L2. Діод закрито."
        else:
            out.append(arrow(dend + 4, yt, node_out - 6, yt, color=act, sw=2.4))
            note = "L1 і L2 віддають у вихід крізь діод.\nCs підзаряджається до Vвх."
        out.append(fitbox(x0 + 14, 348, 424, 40, note, size=11, fill=BG, stroke="#d8dde3"))
        return "".join(out)

    f.append(panel(24, "ТАКТ 1 — ключ замкнено", FIELD, True))
    f.append(panel(504, "ТАКТ 2 — ключ розімкнено", INK, False))
    f.append(fitbox(80, 410, 820, 44,
                    "Зелений — провідний шлях у цьому такті. Котушки L1 і L2 несуть струм безперервно; "
                    "перемикається лише те, куди він тече — у землю крізь ключ (такт 1) "
                    "чи у вихід крізь діод (такт 2). Вихід весь час додатний.",
                    size=11, fill="#eef8ef", stroke=FIELD))
    render(os.path.join(IMG, "phases.svg"), W, H, *f)


# ── фігури до математичної вставки (вольт-секундний баланс) ─────────────────
def _ruler(x_a, x_b, x_c, y, lab1, lab2):
    """Часова лінійка під панеллю: |—— D·T ——|—— (1−D)·T ——|"""
    out = [line(x_a, y, x_c, y, color=MUTED, sw=1.4)]
    for xx in (x_a, x_b, x_c):
        out.append(line(xx, y - 5, xx, y + 5, color=MUTED, sw=1.4))
    out.append(text((x_a + x_b) / 2, y + 20, lab1, size=12, color=MUTED, bold=True))
    out.append(text((x_b + x_c) / 2, y + 20, lab2, size=12, color=MUTED, bold=True))
    return "".join(out)


def fig_vs_balance():
    """Вольт-секундний баланс на обох котушках: дзеркальні площі."""
    W, H = 980, 660
    f = []

    X0, PW = 140.0, 420.0            # початок і ширина періоду
    D = 0.44
    XS = X0 + PW * D                 # момент перемикання
    XE = X0 + PW
    SV = 20.0                        # px на вольт
    HIN, HOUT = 4.2 * SV, 3.3 * SV   # 84 і 66 px

    # спільна пунктирна вертикаль «момент перемикання» (позаду всього)
    f.append(line(XS, 95, XS, 532, color="#c8ccd2", sw=1.4, dash="5 5"))

    def panel(y_ax, name, note, up_in):
        """up_in=True → у такті ВКЛ прямокутник угору (+Vвх), інакше вниз."""
        o = [line(X0 - 10, y_ax, XE + 30, y_ax, color=INK, sw=1.6),
             text(XE + 36, y_ax + 5, "t", size=13, color=MUTED, italic=True),
             text(X0 - 18, y_ax + 5, "0", size=12, color=MUTED, anchor="end"),
             text(80, y_ax - 4, name, size=17, color=COIL, bold=True),
             text(80, y_ax + 16, note, size=11, color=MUTED)]
        if up_in:
            r1 = (X0, y_ax - HIN, XS - X0, HIN, "#fdecea", POS, ["+Vвх", "4.2 В", "площа = 1.848·T"])
            r2 = (XS, y_ax, XE - XS, HOUT, "#eaf0fd", NEG, ["−Vвих", "3.3 В", "площа = 1.848·T"])
        else:
            r1 = (X0, y_ax, XS - X0, HIN, "#eaf0fd", NEG, ["−Vвх", "4.2 В", "площа = 1.848·T"])
            r2 = (XS, y_ax - HOUT, XE - XS, HOUT, "#fdecea", POS, ["+Vвих", "3.3 В", "площа = 1.848·T"])
        for x, y, w, h, fill, col, lines in (r1, r2):
            o.append(rect(x, y, w, h, fill=fill, stroke=col, sw=2.0, rx=0))
            cy = y + h / 2
            o.append(mtext(x + w / 2, cy - (len(lines) - 1) * 12 * 1.3 / 2 + 12 * 0.35,
                           lines, size=12, color=col, bold=True))
        return "".join(o)

    f.append(panel(190, "Vл1", "(на котушці L1)", True))
    f.append(_ruler(X0, XS, XE, 272, "D·T", "(1−D)·T"))
    f.append(panel(420, "Vл2", "(на котушці L2)", False))
    f.append(_ruler(X0, XS, XE, 524, "D·T", "(1−D)·T"))

    f.append(fitbox(620, 120, 336, 130,
                    ["КОТУШКА L1", "",
                     "(+Vвх)·D·T + (−Vвих)·(1−D)·T = 0",
                     "4.2·0.44 − 3.3·0.56 = 0"],
                    size=13, fill="#fbfcfd", stroke="#c8ccd2"))
    f.append(fitbox(620, 350, 336, 130,
                    ["КОТУШКА L2", "",
                     "(−Vвх)·D·T + (+Vвих)·(1−D)·T = 0",
                     "те саме рівняння, взяте зі знаком −"],
                    size=13, fill="#fbfcfd", stroke="#c8ccd2"))

    f.append(fitbox(24, 578, 932, 58,
                    ["Прямокутники в кожній панелі однакові за площею: скільки вольт-секунд котушка набрала за такт «ключ замкнено» —",
                     "стільки ж мусить віддати за такт «ключ розімкнено». Панелі дзеркальні: у кожну мить напруги на L1 і L2 рівні за величиною."],
                    size=12, fill="#eef8ef", stroke=FIELD))

    render(os.path.join(IMG, "vs-balance.svg"), W, H, *f,
           title="Вольт-секундний баланс на обох котушках (Vвх = 4.2 В, Vвих = 3.3 В, D = 0.44)")


def fig_transfer_curve():
    """Крива M(D) = D/(1−D): вісь D = 0.5 і крутизна праворуч."""
    W, H = 980, 620
    f = []
    PX0, PX1 = 110.0, 660.0          # D від 0 до 0.8
    PY0, PYT = 500.0, 95.0           # M від 0 до 4.5
    KX = (PX1 - PX0) / 0.8
    KY = (PY0 - PYT) / 4.5

    def px(d):
        return PX0 + KX * d

    def py(m):
        return PY0 - KY * m

    # сітка
    for m in (1, 2, 3, 4):
        y = py(m)
        f.append(line(PX0, y, PX1, y, color="#dfe3e8", sw=1.2, dash="4 4"))
        f.append(text(PX0 - 12, y + 5, str(m), size=12, color=MUTED, anchor="end"))
    for d in (0.2, 0.4, 0.6, 0.8):
        x = px(d)
        f.append(line(x, PY0, x, PYT, color="#dfe3e8", sw=1.2, dash="4 4"))
        f.append(text(x, 522, ("%.1f" % d), size=12, color=MUTED))
    f.append(text(PX0 - 12, PY0 + 5, "0", size=12, color=MUTED, anchor="end"))

    # вікно Li-ion (D = 0.44…0.52)
    f.append(rect(px(0.44), py(0.52 / 0.48), px(0.52) - px(0.44), PY0 - py(0.52 / 0.48),
                  fill="#eaf7ee", stroke="#bfe3c9", sw=1.2, rx=0))

    # осі
    f.append(line(PX0, PY0, PX1 + 20, PY0, color=INK, sw=1.8))
    f.append(line(PX0, PY0, PX0, PYT - 12, color=INK, sw=1.8))
    f.append(text(PX1 + 34, 526, "D", size=14, color=INK, bold=True))
    f.append(text(PX0 + 6, PYT - 22, "Vвих / Vвх", size=14, color=INK, bold=True, anchor="start"))

    # крива
    pts = []
    d = 0.0
    while d <= 0.8001:
        pts.append("%.1f %.1f" % (px(d), py(d / (1 - d))))
        d += 0.004
    f.append('<path d="M %s" fill="none" stroke="%s" stroke-width="3"/>'
             % (" L ".join(pts), POS))

    # точка D = 0.5
    f.append(circle(px(0.5), py(1.0), 6, fill=POS, stroke=BG, sw=2))
    f.append(text(px(0.5) - 18, py(1.0) - 10, "M = 1 при D = 0.5", size=12.5,
                  color=INK, anchor="end", bold=True))

    # підпис вікна Li-ion
    f.append(fitbox(150, 250, 232, 52, ["вікно однієї банки Li-ion:", "D = 0.44…0.52"],
                    size=12, fill=BG, stroke="#bfe3c9"))
    f.append(arrow(330, 304, 424, 392, color="#7fae8d", sw=1.8))

    f.append(fitbox(706, 130, 250, 152,
                    ["НАХИЛ КРИВОЇ", "dM/dD = 1/(1−D)²", "",
                     "D = 0.50  →  4", "D = 0.75  →  16", "D = 0.90  →  100"],
                    size=13, fill="#fbfcfd", stroke="#c8ccd2"))
    f.append(fitbox(706, 320, 250, 152,
                    ["ОБЕРНЕНО", "D = M / (1 + M)", "",
                     "M = 1  →  D = 0.50", "M = 3  →  D = 0.75", "M = 9  →  D = 0.90"],
                    size=13, fill="#fbfcfd", stroke="#c8ccd2"))

    f.append(fitbox(24, 550, 932, 52,
                    ["Крива перетинає одиницю рівно при D = 0.5 — це вісь, довкола якої SEPIC переходить зі зниження на підвищення.",
                     "Праворуч вона задирається: біля D = 0.9 зсув заповнення на 0.01 додає до виходу цілий Vвх."],
                    size=12, fill="#eef8ef", stroke=FIELD))

    render(os.path.join(IMG, "transfer-curve.svg"), W, H, *f,
           title="Коефіцієнт передачі M = D/(1−D): вісь D = 0.5 і крутизна праворуч")


# ── Фіг.5 — дві доповіді PESC '77 (до вставки hist-sepic) ───────────────────
def fig_hist_pesc77():
    W, H = 1000, 580
    f = [text(W / 2, 34, "PESC '77: дві доповіді підряд в одному томі", size=17, bold=True)]
    f.append(fitbox(60, 56, 880, 44,
                    "IEEE Power Electronics Specialists Conference · "
                    "Пало-Альто, Каліфорнія · 14–16 червня 1977",
                    size=13, fill="#f4f6f8", stroke=MUTED, bold=True))

    def panel(x0, rows):
        out = [rect(x0, 118, 420, 300, fill=BG, stroke="#d8dde3", sw=2, rx=10)]
        tx = x0 + 24
        for (y, s, size_, col, bold_, ital) in rows:
            if s is None:
                out.append(line(tx, y, x0 + 396, y, color="#d8dde3", sw=1.4))
            else:
                out.append(text(tx, y, s, size=size_, color=col,
                                anchor="start", bold=bold_, italic=ital))
        return "".join(out)

    left = [
        (150, "с. 156–159", 12, MUTED, True, False),
        (178, "Р. П. Мессі · Е. К. Снайдер", 14, INK, True, False),
        (204, "«High voltage single-ended", 12, MUTED, False, True),
        (222, "DC-DC converter»", 12, MUTED, False, True),
        (240, None, 0, INK, False, False),
        (266, "замовлення промисловості", 12, MUTED, False, False),
        (292, "1800 В · 130 Вт · ККД 82 %", 13, INK, True, False),
        (318, "на 25 % дешевше за двотактний", 13, INK, False, False),
        (340, "трансформаторний, один ключ", 13, INK, False, False),
        (366, "мало деталей у силовому тракті", 13, INK, False, False),
    ]
    right = [
        (150, "с. 160–179", 12, MUTED, True, False),
        (178, "С. Ћук · Р. Д. Мідлбрук", 14, INK, True, False),
        (204, "«A new optimum topology switching", 12, MUTED, False, True),
        (222, "DC-to-DC converter»", 12, MUTED, False, True),
        (240, None, 0, INK, False, False),
        (266, "докторська робота в Caltech", 12, MUTED, False, False),
        (292, "непульсуючий струм з обох боків", 13, INK, True, False),
        (318, "четверта фундаментальна топологія", 13, INK, False, False),
        (340, "патент US 4 184 197 (28.09.1977)", 13, INK, False, False),
        (366, "енергію переносить конденсатор", 13, INK, False, False),
    ]
    f.append(panel(60, left))
    f.append(panel(520, right))

    f.append(arrow(270, 424, 270, 448, color=FIELD, sw=2.4))
    f.append(arrow(730, 424, 730, 448, color=NEG, sw=2.4))
    f.append(fitbox(110, 452, 320, 42, "SEPIC — вихід ДОДАТНИЙ",
                    size=14, bold=True, fill="#eef8ef", stroke=FIELD))
    f.append(fitbox(570, 452, 320, 42, "Ћук — вихід ВІД'ЄМНИЙ",
                    size=14, bold=True, fill="#eaf0fd", stroke=NEG))

    f.append(fitbox(60, 512, 880, 52,
                    ["Обидві схеми з одного кореня: енергію на вихід переносить послідовний конденсатор, а не котушка.",
                     "Мессі й Снайдера вело здешевлення конкретного виробу, Ћука з Мідлбруком — пошук найкращої топології;",
                     "звідси й різні за походженням назви — абревіатура з заголовка доповіді проти прізвища автора."],
                    size=12, fill="#f4f6f8", stroke=MUTED))
    render(os.path.join(IMG, "hist-pesc77.svg"), W, H, *f)


# ── Фіг.6 — single-ended проти push-pull (до вставки hist-sepic) ────────────
def fig_hist_single_ended():
    W, H = 980, 580
    f = [text(W / 2, 34, "Однотактний проти двотактного: скільки осердя дістається схемі",
              size=17, bold=True)]

    def panel(x0, title_txt, band_top, band_h, band_fill, band_stroke, swing, bullets, accent):
        ax = x0 + 130
        out = [rect(x0, 60, 400, 340, fill=BG, stroke="#d8dde3", sw=2, rx=10)]
        out.append(text(x0 + 200, 92, title_txt, size=14, color=accent, bold=True))
        out.append(line(ax, 118, ax, 388, color=INK, sw=1.6))
        out.append(rect(ax - 15, band_top, 30, band_h, fill=band_fill,
                        stroke=band_stroke, sw=1.5, rx=3))
        for yy, lab in ((126, "+B_нас"), (248, "0"), (374, "−B_нас")):
            out.append(line(ax - 10, yy, ax + 10, yy, color=INK, sw=1.4))
            out.append(text(ax - 24, yy + 5, lab, size=12, color=MUTED, anchor="end"))
        out.append(text(x0 + 162, 152, swing, size=15, color=accent, anchor="start", bold=True))
        for yy, s, bold_ in bullets:
            out.append(text(x0 + 162, yy, s, size=12, color=INK, anchor="start", bold=bold_))
        return "".join(out)

    f.append(panel(60, "Однотактний (single-ended)", 126, 122, "#eef8ef", FIELD,
                   "ΔB ≤ B_нас",
                   [(188, "потік ходить лише в один бік:", False),
                    (208, "друга половина петлі осердя", False),
                    (228, "весь час простоює", False),
                    (264, "один ключ, і той — на землю", True),
                    (292, "простий драйвер, нема чим", False),
                    (312, "розбалансувати осердя", False)], FIELD))
    f.append(panel(520, "Двотактний (push-pull)", 126, 248, "#eaf0fd", NEG,
                   "ΔB ≤ 2·B_нас",
                   [(188, "потік гойдається симетрично:", False),
                    (208, "осердя віддає вдвічі більше", False),
                    (228, "за той самий об'єм", False),
                    (264, "два ключі, плечі треба зрівняти", True),
                    (292, "найменша нерівність плечей", False),
                    (312, "жене потік у насичення", False)], NEG))

    f.append(fitbox(110, 420, 300, 46, ["90 витків", "на ті самі вольт·секунди"],
                    size=13, bold=True, fill="#eef8ef", stroke=FIELD))
    f.append(fitbox(570, 420, 300, 46, ["45 витків", "на ті самі вольт·секунди"],
                    size=13, bold=True, fill="#eaf0fd", stroke=NEG))

    f.append(fitbox(60, 486, 860, 66,
                    ["Приклад: 300 В на обмотці, 50 кГц, D = 0.45, переріз осердя 100 мм², робоче B_нас = 0.3 Тл.",
                     "Однотактна схема веде потік від нуля вгору й мусить його скидати — їй лишається половина петлі.",
                     "Двотактна гойдає потік симетрично й обходиться вдвічі меншими витками — ціною двох узгоджених ключів."],
                    size=12, fill="#f4f6f8", stroke=MUTED))
    render(os.path.join(IMG, "hist-single-ended.svg"), W, H, *f)


if __name__ == "__main__":
    fig_topology()
    fig_phases()
    fig_vs_balance()
    fig_transfer_curve()
    fig_hist_pesc77()
    fig_hist_single_ended()
    print("OK: 6 фігур у", IMG)
