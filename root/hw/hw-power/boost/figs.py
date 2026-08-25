# -*- coding: utf-8 -*-
"""Фігури до статті «Boost-перетворювач».
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


def coil(x1, x2, y, color=COIL, sw=2.8):
    """Котушка дугами між x1 і x2 на висоті y."""
    n = 4
    step = (x2 - x1) / n
    r = step / 2
    d = "M %.1f %.1f " % (x1, y)
    for i in range(n):
        cx0 = x1 + step * i
        d += "A %.1f %.1f 0 0 1 %.1f %.1f " % (r, 10.0, cx0 + step, y)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, color, sw)


def diode(x, y, color=INK, sw=2.0):
    """Діод (трикутник + планка), провідність зліва направо, від x до x+22."""
    out = ['<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="none" '
           'stroke="%s" stroke-width="%.1f"/>' % (x, y - 11, x, y + 11, x + 22, y, color, sw)]
    out.append(line(x + 22, y - 11, x + 22, y + 11, color=color, sw=sw + 0.6))
    return "".join(out), x + 22


def cap(cx, y_top, y_bot, color=INK, sw=2.0):
    """Конденсатор двома планками між y_top..y_bot (вертикальна гілка)."""
    midhi, midlo = (y_top + y_bot) / 2 - 6, (y_top + y_bot) / 2 + 6
    out = [line(cx, y_top, cx, midhi, color=color, sw=sw)]
    out.append(line(cx - 15, midhi, cx + 15, midhi, color=color, sw=sw + 0.6))
    out.append(line(cx - 15, midlo, cx + 15, midlo, color=color, sw=sw + 0.6))
    out.append(line(cx, midlo, cx, y_bot, color=color, sw=sw))
    return "".join(out)


def load(x, y_top, y_bot, color=INK, sw=1.8):
    """Навантаження — прямокутник-резистор на вертикальній гілці."""
    out = [line(x, y_top, x, y_top + 12, color=color, sw=sw)]
    out.append(rect(x - 11, y_top + 12, 22, 50, fill="none", stroke=color, sw=sw, rx=0))
    out.append(line(x, y_top + 62, x, y_bot, color=color, sw=sw))
    return "".join(out)


def switch_open(cx, y, color=MUTED, sw=2.0):
    """Розімкнений ключ (нахилена планка) — вертикальна гілка від вузла вниз."""
    out = [line(cx, y, cx, y + 26, color=color, sw=sw)]
    out.append(line(cx, y + 26, cx + 18, y + 12, color=color, sw=sw + 0.4))
    out.append(line(cx, y + 44, cx, y + 90, color=color, sw=sw))
    return "".join(out)


def switch_closed(cx, y, color=NEG, sw=3.0):
    """Замкнений ключ — суцільна вертикальна гілка."""
    return line(cx, y, cx, y + 90, color=color, sw=sw)


# ── Фіг.1 — дві фази boost ──────────────────────────────────────────────────
def fig_phases():
    W, H = 920, 430
    f = [text(W / 2, 30, "Boost: накопичити в котушці, тоді «підкинути» до входу", size=17, bold=True)]

    def panel(x0, title_txt, title_color, on):
        out = [rect(x0, 64, 400, 280, fill="none", stroke="#d8dde3", sw=2, rx=10)]
        cxc = x0 + 360
        out.append(text(x0 + 200, 88, title_txt, size=13, color=title_color, bold=True))
        # рівні: верх гілки y=170, земля y=300
        vx = x0 + 30
        out.append(vsource(vx, 170))
        out.append(line(vx, 180, vx, 300, color=INK, sw=2))           # ліва до землі
        out.append(line(vx, 170, x0 + 55, 170, color=INK, sw=2))
        out.append(coil(x0 + 55, x0 + 160, 170))
        node_sw = x0 + 195
        out.append(line(x0 + 160, 170, node_sw, 170, color=INK, sw=2))
        out.append(circle(node_sw, 170, 3.5, fill=INK, stroke=INK, sw=0))
        # ключ донизу від node_sw
        if on:
            out.append(switch_closed(node_sw, 170))
            out.append(text(node_sw - 30, 235, "ключ", size=11, color=NEG, bold=True))
            out.append(text(node_sw - 30, 250, "ВКЛ", size=11, color=NEG, bold=True))
            out.append(text(x0 + 110, 152, "Vл = +Vвх", size=12, color=FIELD, bold=True))
        else:
            out.append(switch_open(node_sw, 170))
            out.append(text(node_sw - 28, 243, "ВИКЛ", size=11, color=MUTED, bold=True))
            out.append(text(x0 + 110, 152, "Vл = Vвх−Vвих", size=12, color=POS, bold=True))
        # діод від node_sw праворуч
        dcolor = MUTED if on else FIELD
        out.append(line(node_sw, 170, x0 + 230, 170, color=dcolor, sw=2))
        dfrag, dend = diode(x0 + 230, 170, color=dcolor)
        out.append(dfrag)
        if on:  # перекреслити закритий діод
            out.append(line(x0 + 226, 154, x0 + 258, 186, color=POS, sw=2.4))
        out.append(text(x0 + 248, 154, "діод", size=11, color=dcolor))
        node_out = x0 + 305
        out.append(line(dend, 170, node_out, 170, color=dcolor, sw=2))
        out.append(circle(node_out, 170, 3.5, fill=INK, stroke=INK, sw=0))
        # конденсатор і навантаження
        out.append(cap(node_out, 170, 300))
        out.append(line(node_out, 170, x0 + 350, 170, color=INK, sw=2))
        out.append(load(x0 + 350, 170, 300))
        out.append(text(x0 + 352, 162, "Vвих", size=12, color=POS, anchor="start", bold=True))
        out.append(line(vx, 300, x0 + 350, 300, color=INK, sw=2))       # земля
        # підпис-пояснення
        cap_txt = ("котушка запасає; вихід живить лише C" if on
                   else "струм преться крізь діод; Vл додається до Vвх")
        out.append(text(x0 + 200, 326, cap_txt, size=10.5, color=INK))
        return "".join(out)

    f.append(panel(20, "ФАЗА ВКЛ (ключ замкнено)", NEG, True))
    f.append(panel(500, "ФАЗА ВИКЛ (ключ розімкнено)", MUTED, False))
    f.append(fitbox(70, 388, 780, 30,
                    "Секрет підвищення — «брикання» котушки: різке розмикання дає на ній викид напруги, що ДОДАЄТЬСЯ до Vвх",
                    size=11.5, fill="#eef8ef", stroke=FIELD))
    render(os.path.join(IMG, "phases.svg"), W, H, *f)


# ── Фіг.2 — коефіцієнт Vвих/Vвх = 1/(1−D) ───────────────────────────────────
def fig_ratio():
    W, H = 900, 430
    f = [text(W / 2, 30, "Коефіцієнт boost: Vвих / Vвх = 1 / (1 − D)", size=17, bold=True)]
    ox, oy = 110, 350     # початок осей
    rx, ty = 800, 80      # права/верхня межі
    ymax = 6.0            # вісь до 6×
    out = []
    out.append(arrow(ox, oy, ox, ty, color=INK))
    out.append(arrow(ox, oy, rx + 20, oy, color=INK))
    out.append(text(ox - 10, ty + 8, "Vвих/Vвх", size=12, anchor="end", bold=True))
    out.append(text(rx + 24, oy + 4, "D", size=12, anchor="start", bold=True))

    def Y(v):
        return oy - (v - 1) / (ymax - 1) * (oy - ty)

    def X(d):
        return ox + d * (rx - ox)

    for v in range(1, 7):
        yy = Y(v)
        out.append(line(ox, yy, rx, yy, color="#e4e4e4", sw=1))
        out.append(text(ox - 8, yy + 4, "%d×" % v, size=10.5, color=MUTED, anchor="end"))
    for d in (0.0, 0.25, 0.5, 0.75):
        xx = X(d)
        out.append(line(xx, oy, xx, oy + 5, color=MUTED, sw=1.2))
        out.append(text(xx, oy + 20, "%.2f" % d, size=10.5, color=MUTED))
    # крива 1/(1−D), обрізана на ymax
    pts = []
    d = 0.0
    while d <= 0.85:
        v = 1.0 / (1.0 - d)
        if v > ymax:
            break
        pts.append("%.1f,%.1f" % (X(d), Y(v)))
        d += 0.02
    out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3" '
               'stroke-linejoin="round" stroke-linecap="round"/>' % (" ".join(pts), FIELD))
    # асимптота D→1
    xa = X(0.84)
    out.append(line(xa, oy, xa, ty + 10, color=POS, sw=1.4, dash="5,5"))
    out.append(text(xa + 6, ty + 30, "D→1 ⇒ Vвих→∞", size=11, color=POS, bold=True))
    out.append(text(xa + 6, ty + 48, "(реально ~5–10×:", size=10, color=MUTED, anchor="start"))
    out.append(text(xa + 6, ty + 62, "паразити обмежують)", size=10, color=MUTED, anchor="start"))
    # маркери
    for d, v, lbl in [(0.0, 1, "D=0 → 1×"), (0.5, 2, "0.5 → 2×"),
                      (2 / 3, 3, "0.67 → 3×"), (0.8, 5, "0.8 → 5×")]:
        out.append(circle(X(d), Y(v), 4, fill=FIELD, stroke=FIELD, sw=0))
        out.append(text(X(d) + 8, Y(v) - 6, lbl, size=10.5, anchor="start", bold=True))
    out.append(fitbox(70, 392, 760, 26,
                      "Vвих ЗАВЖДИ ≥ Vвх: навіть при D=0 вихід дорівнює входу. Знизити напругу boost не вміє в принципі",
                      size=11, fill="#eef8ef", stroke=FIELD))
    f.extend(out)
    render(os.path.join(IMG, "ratio.svg"), W, H, *f)


# ── Фіг.3 — струми: вхід гладкий, вихід рваний ──────────────────────────────
def fig_currents():
    W, H = 920, 430
    f = [text(W / 2, 30, "У boost вхід гладкий, вихід рваний", size=17, bold=True)]
    out = []
    x0, x1 = 100, 720
    # верхній графік: iвх = iл (трикутна хвиля, безперервна)
    out.append(text(x0 - 16, 95, "iвх=iл", size=11, anchor="end", bold=True))
    out.append(line(x0, 150, x1, 150, color="#cfcfcf", sw=1.2))
    saw = []
    seg = (x1 - x0) / 5
    for i in range(6):
        xx = x0 + seg * i
        saw.append("%.1f,%.1f" % (xx, 168 if i % 2 == 0 else 132))
    out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8" '
               'stroke-linejoin="round" stroke-linecap="round"/>' % (" ".join(saw), COIL))
    out.append(text(x1 + 6, 150, "безперервний", size=11, color=FIELD, anchor="start", bold=True))
    out.append(text(x1 + 6, 165, "(добре для входу/завад)", size=9.5, color=MUTED, anchor="start"))
    # нижній графік: iдіод (імпульси лише у фазі ВИКЛ)
    out.append(text(x0 - 16, 240, "iдіод", size=11, anchor="end", bold=True))
    base = 290
    out.append(line(x0, base, x1, base, color="#cfcfcf", sw=1.2))
    seg2 = (x1 - x0) / 4
    pulse = []
    for i in range(2):
        a = x0 + seg2 * (2 * i)
        b = a + seg2
        c = b + seg2
        out.append(line(a, base, b, base, color=COIL, sw=2.8))
        pulse = "%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" % (b, base, b, base - 30, c, base - 18, c, base)
        out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8" '
                   'stroke-linejoin="round" stroke-linecap="round"/>' % (pulse, COIL))
    out.append(text(x1 + 6, base, "імпульсами", size=11, color=POS, anchor="start", bold=True))
    out.append(text(x1 + 6, base + 15, "(лише у фазі ВИКЛ)", size=9.5, color=MUTED, anchor="start"))
    out.append(text((x0 + x1) / 2, base + 34,
                    "вихідний конденсатор працює важче — бере весь рваний струм", size=11))
    out.append(fitbox(70, 390, 780, 28,
                      "Збереження потужності: Iвх = Iвих/(1−D) — котушка несе ВЕСЬ вхідний струм, більший за вихідний",
                      size=11, fill="#fbf7ec", stroke="#caa24a"))
    f.extend(out)
    render(os.path.join(IMG, "currents.svg"), W, H, *f)


# ── Фіг.4 — прозорість для КЗ ───────────────────────────────────────────────
def fig_short():
    W, H = 920, 440
    f = [text(W / 2, 30, "Вхід boost завжди з'єднаний із виходом", size=17, bold=True)]
    out = []
    y = 180
    out.append(vsource(90, y))
    out.append(line(90, y + 10, 90, 320, color=INK, sw=2))
    out.append(line(90, y, 120, y, color=POS, sw=3))
    out.append(coil(120, 250, y, color=POS, sw=3))
    out.append(line(250, y, 300, y, color=POS, sw=3))
    out.append(circle(300, y, 4, fill=INK, stroke=INK, sw=0))
    out.append(switch_open(300, y))
    out.append(text(300, 338, "ключ ВИМКНЕНО", size=11, color=MUTED, bold=True))
    out.append(line(300, y, 330, y, color=POS, sw=2))
    dfrag, dend = diode(330, y, color=POS)
    out.append(dfrag)
    out.append(text(341, 164, "діод", size=11, color=POS))
    out.append(line(dend, y, 490, y, color=POS, sw=3))
    out.append(line(490, y, 490, 320, color=POS, sw=3))   # КЗ-перемичка
    out.append(text(490, 158, "КЗ!", size=15, color=POS, bold=True))
    out.append('<path d="M 478 210 L 496 230 L 484 230 L 502 254" fill="none" '
               'stroke="%s" stroke-width="2.6"/>' % POS)
    out.append(line(90, 320, 490, 320, color=INK, sw=2))
    out.append('<line x1="160" y1="150" x2="230" y2="150" stroke="%s" stroke-width="3" '
               'marker-end="url(#arrow)"/>' % POS)
    out.append(text(250, 146, "струм тече Vвх → котушка → діод → КЗ, попри вимкнений ключ",
                    size=11.5, color=POS, anchor="start", bold=True))
    out.append(fitbox(70, 366, 780, 24,
                      "Шлях Vвх → котушка → діод → вихід існує ЗАВЖДИ — його не розриває жоден ключ контролера",
                      size=11.5, fill="#fbe9e7", stroke=POS, bold=True))
    out.append(text(W / 2, 408,
                    "Тому boost: не вміє Vвих < Vвх · не гасить КЗ вимиканням ключа · б'є інрашем при старті",
                    size=11))
    out.append(text(W / 2, 426, "Контролер тут безсилий — захист має стояти ОКРЕМО",
                    size=11, color=POS, bold=True))
    f.extend(out)
    render(os.path.join(IMG, "short.svg"), W, H, *f)


# ── Фіг.5 — зовнішній захист ────────────────────────────────────────────────
def fig_fixes():
    W, H = 920, 400
    f = [text(W / 2, 30, "Захист boost додають ЗЗОВНІ", size=17, bold=True)]
    out = []
    cards = [
        ("Послідовний роз'єднувач",
         ["окремий MOSFET-ключ", "після виходу — фізично", "рве шлях на КЗ і в спокої"]),
        ("Запобіжник / ліміт",
         ["запобіжник чи eFuse", "на вході обмежує струм,", "коли все інше не встигло"]),
        ("М'який старт",
         ["плавно піднімати вихід", "(ramp / NTC) проти", "інрашу при увімкненні"]),
    ]
    xs = [20, 325, 630]
    for x0, (title_txt, body) in zip(xs, cards):
        out.append(rect(x0, 64, 270, 200, fill="#f6f9fc", stroke=NEG, sw=1.8, rx=12))
        out.append(text(x0 + 135, 122, title_txt, size=13, color=NEG, bold=True))
        for i, ln in enumerate(body):
            out.append(text(x0 + 135, 160 + i * 22, ln, size=11))
    out.append(fitbox(70, 320, 780, 26,
                      "Boost сам по собі вихід не захистить — багато boost-мікросхем мають вбудований роз'єднувач і захист від КЗ; нема його — ставлять самотужки",
                      size=11, fill="#eef8ef", stroke=FIELD))
    f.extend(out)
    render(os.path.join(IMG, "fixes.svg"), W, H, *f)


if __name__ == "__main__":
    fig_phases()
    fig_ratio()
    fig_currents()
    fig_short()
    fig_fixes()
    print("OK: 5 фігур у", IMG)
