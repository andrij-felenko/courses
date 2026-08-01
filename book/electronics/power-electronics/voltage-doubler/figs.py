# -*- coding: utf-8 -*-
"""Фігури до статті «Помножувач напруги».
Запуск: python figs.py  → пише .svg у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GREEN_FILL = "#eef7ee"
GREY_FILL = "#f0f0f0"


def diode_right(xa, xc, y, color, fill):
    """Діод анодом ліворуч (xa), катодом праворуч (xc). Трикутник → бар."""
    apex = xc - 3
    out = ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" '
           'stroke-width="2"/>' % (xa, y - 12, xa, y + 12, apex, y, fill, color))
    out += line(xc, y - 13, xc, y + 13, color=color, sw=2.6)
    return out


def diode_up(x, yb, yt, color, fill):
    """Діод катодом угорі (yt), анодом унизу (yb). Трикутник вершиною вгору."""
    apex = yt + 3
    out = ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" '
           'stroke-width="2"/>' % (x - 12, yb, x + 12, yb, x, apex, fill, color))
    out += line(x - 13, yt, x + 13, yt, color=color, sw=2.6)
    return out


def cap_v(x, y1, y2, color=INK):
    """Конденсатор у серії (горизонтальна вітка) — дві вертикальні пластини на x."""
    # тут використовується для послідовного C1: пластини вертикальні, розрив по x
    pass


# ── Фігура 1: дві півхвилі подвоювача ────────────────────────────────────────
def fig_phases():
    W, H = 980, 500
    els = [text(W / 2, 30, "Помножувач-подвоювач: одна півхвиля заряджає C1, друга — доливає 2Vₚ",
                size=17, bold=True)]

    def panel(dx, phase):
        e = []
        gnd = 380          # рівень землі
        rail = 200         # верхня шина
        sx = dx + 70       # джерело
        ax = dx + 120      # вузол A
        c1 = dx + 180      # центр C1
        bx = dx + 250      # вузол B
        cx = dx + 355      # вузол C (вихід)
        outx = dx + 415

        neg = (phase == "neg")
        d1_col, d1_fill = (FIELD, GREEN_FILL) if neg else (MUTED, GREY_FILL)
        d2_col, d2_fill = (MUTED, GREY_FILL) if neg else (FIELD, GREEN_FILL)

        # заголовок панелі
        head = ("Мінусова півхвиля" if neg else "Плюсова півхвиля")
        e.append(fitbox(dx + 40, 52, 400, 34, head,
                        size=14, bold=True,
                        fill=("#eef4ff" if neg else "#fdeeee"),
                        stroke=(NEG if neg else POS)))

        # земляна шина
        e.append(line(dx + 40, gnd, dx + 430, gnd, color=INK, sw=2))
        for gx in (sx, bx, cx):
            e.append(line(gx, gnd - 5, gx, gnd + 5, color=INK, sw=1))

        # джерело AC
        e.append(circle(sx, 290, 22, fill=BG, stroke=INK, sw=2))
        e.append(text(sx, 296, "∼", size=26, color=INK, bold=True))
        e.append(line(sx, gnd, sx, 312, color=INK, sw=2))
        e.append(line(sx, 268, sx, rail, color=INK, sw=2))
        e.append(line(sx, rail, ax, rail, color=INK, sw=2))
        src_lbl = ("Vдж = −Vₚ" if neg else "Vдж = +Vₚ")
        e.append(text(sx - 30, 250, src_lbl, size=13, color=(NEG if neg else POS),
                      anchor="end", bold=True))

        # C1 — послідовний конденсатор (дві вертикальні пластини)
        e.append(line(ax, rail, c1 - 8, rail, color=INK, sw=2))
        e.append(line(c1 - 8, rail - 16, c1 - 8, rail + 16, color=INK, sw=2.5))
        e.append(line(c1 + 8, rail - 16, c1 + 8, rail + 16, color=INK, sw=2.5))
        e.append(line(c1 + 8, rail, bx, rail, color=INK, sw=2))
        c1_lbl = ("C1 набирає Vₚ" if neg else "C1 тримає Vₚ")
        e.append(text(c1, rail - 28, "C1", size=13, color=NEG, bold=True))
        e.append(text(c1, rail + 40, c1_lbl, size=11.5,
                      color=(FIELD if neg else MUTED)))

        # вузол B
        e.append(circle(bx, rail, 4.5, fill=INK, stroke=INK))
        e.append(text(bx, rail - 26, "B", size=13, color=INK, bold=True))

        # D1 — від B донизу до землі (катод угорі, біля B)
        e.append(line(bx, rail, bx, 246, color=d1_col, sw=2))
        e.append(diode_up(bx, 300, 250, d1_col, d1_fill))
        e.append(line(bx, 302, bx, gnd, color=d1_col, sw=2))
        d1_lbl = ("D1 ▶ відкритий" if neg else "D1 ✕ закритий")
        e.append(text(bx - 18, 290, d1_lbl, size=11.5, color=d1_col,
                      anchor="end", bold=True))

        # D2 — від B праворуч до C (анод біля B)
        e.append(line(bx, rail, bx + 26, rail, color=d2_col, sw=2))
        e.append(diode_right(bx + 26, cx - 40, rail, d2_col, d2_fill))
        e.append(line(cx - 40, rail, cx, rail, color=d2_col, sw=2))
        d2_lbl = ("D2 ✕ закритий" if neg else "D2 ▶ відкритий")
        e.append(text((bx + cx) / 2, rail - 24, "D2", size=13, color=d2_col, bold=True))
        e.append(text((bx + cx) / 2, rail + 26, d2_lbl, size=11.5, color=d2_col, bold=True))

        # вузол C + вихідний конденсатор C2
        e.append(circle(cx, rail, 4.5, fill=INK, stroke=INK))
        e.append(line(cx, rail, cx, 260, color=INK, sw=2))
        e.append(line(cx - 16, 260, cx + 16, 260, color=INK, sw=2.5))
        e.append(line(cx - 16, 272, cx + 16, 272, color=INK, sw=2.5))
        e.append(line(cx, 272, cx, gnd, color=INK, sw=2))
        e.append(text(cx + 24, 258, "C2", size=13, color=NEG, anchor="start", bold=True))
        c2_lbl = ("тримає 2Vₚ" if neg else "набирає 2Vₚ")
        e.append(text(cx + 24, 274, c2_lbl, size=11, color=MUTED, anchor="start"))

        # вихід
        e.append(line(cx, rail, outx, rail, color=INK, sw=2))
        e.append(circle(outx, rail, 4, fill=BG, stroke=INK, sw=1.5))
        e.append(text(outx + 8, rail - 8, "Vвих", size=12.5, color=INK,
                      anchor="start", bold=True))
        e.append(text(outx + 8, rail + 8, "≈ 2Vₚ", size=12.5, color=POS, anchor="start", bold=True))

        # позначка вузла B у плюсову півхвилю
        if not neg:
            e.append(text(bx, 150, "Vₚ + Vₚ = 2Vₚ", size=13, color=POS, bold=True))
            e.append(arrow(bx, 158, bx, rail - 34, color=POS, sw=1.6))
        else:
            e.append(text(bx + 4, 150, "B притиснено до ~0", size=12, color=NEG, anchor="middle"))
            e.append(arrow(bx, 158, bx, rail - 34, color=NEG, sw=1.4))

        return e

    els += panel(10, "neg")
    # роздільник між панелями
    els.append(line(W / 2, 60, W / 2, H - 30, color="#dfe3e8", sw=1.4, dash="4,5"))
    els += panel(500, "pos")
    render(os.path.join(IMG, "phases.svg"), W, H, *els)


# ── Фігура 2: каскад Кокрофта–Волтона — сходинки напруги ─────────────────────
def fig_ladder():
    W, H = 860, 500
    els = [text(W / 2, 32, "Каскад: кожна сходинка додає ще 2Vₚ — але під струмом верхівка просідає",
                size=16, bold=True)]

    ox, oy = 90, 410           # початок осей
    top = 90
    els.append(arrow(ox, oy, ox, top - 6, color=INK, sw=1.6))   # вісь напруги
    els.append(arrow(ox, oy, 800, oy, color=INK, sw=1.6))       # вісь каскадів
    els.append(text(ox - 16, top + 4, "напруга", size=13, anchor="end", color=INK))
    els.append(text(ox - 16, top + 20, "виходу", size=13, anchor="end", color=INK))
    els.append(text(790, oy + 26, "число каскадів n", size=13, anchor="end", color=INK))

    n_max = 5
    step = 120                 # крок по x на каскад
    unit = 56                  # px на кожні 2Vₚ (висота сходинки)

    # ідеальні сходинки 2n·Vₚ (сині стовпці)
    for n in range(1, n_max + 1):
        x = ox + n * step
        h_ideal = n * unit
        y = oy - h_ideal
        els.append(rect(x - 34, y, 46, h_ideal, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=3))
        els.append(text(x - 11, y - 10, "%d·Vₚ" % (2 * n) if n > 1 else "2Vₚ",
                        size=12.5, color=NEG, bold=True))
        els.append(text(x - 11, oy + 20, "%d" % n, size=12, color=INK))

    # реальна (навантажена) верхівка — просідання росте з n (штрихова червона)
    pts = []
    for n in range(0, n_max + 1):
        x = ox + n * step - 11
        # просідання ~ квадратично-кубічно з n: ідеал − droop
        droop = 0.06 * (n ** 2) + 0.015 * (n ** 3)
        y = oy - max(0.0, (n - droop)) * unit
        pts.append("%.1f,%.1f" % (x, y))
    els.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
               'stroke-dasharray="7,4"/>' % (" ".join(pts), POS))
    els.append(circle(ox + n_max * step - 11,
                      oy - max(0.0, (n_max - (0.06 * n_max ** 2 + 0.015 * n_max ** 3))) * unit,
                      4, fill=POS, stroke=POS))

    # легенда
    frag, w, h = textbox(640, 150, "── ідеал: ≈ 2n·Vₚ", size=12.5, bold=True,
                         stroke=NEG, fill="#eaf0fd", min_w=210, color=NEG)
    els.append(frag)
    frag, w, h = textbox(640, 190, "– – під навантаженням:\nпросідання ∝ n³",
                         size=12.5, bold=True, stroke=POS, fill="#fdeeee", min_w=210, color=POS)
    els.append(frag)

    render(os.path.join(IMG, "ladder.svg"), W, H, *els)


# ── Фігура 3 (вставка hist): кулонівський бар'єр і тунелювання ───────────────
def fig_barrier():
    W, H = 960, 540
    els = [text(W / 2, 34, "Чому 1932 року вистачило кількох сотень кіловольтів",
                size=17, bold=True)]

    x0 = 250          # вісь енергії
    r0 = 260          # центр ядра по x
    SX = 24.0         # px на 1 фм
    y0 = 300          # рівень E = 0
    SY = 130.0        # px на 1 МеВ

    def X(r):
        return r0 + r * SX

    def Y(e):
        return y0 - e * SY

    R_nuc = 3.4       # радіус дотику, фм
    E_bar = 4.32 / R_nuc      # ≈ 1.27 МеВ
    E_p = 0.3                 # енергія протона з каскаду
    r_out = 4.32 / E_p        # точка виходу з-під бар'єра, ≈ 14.4 фм

    # вісь енергії
    els.append(arrow(x0, 440, x0, 96, color=INK, sw=1.6))
    els.append(text(x0, 78, "енергія протона, МеВ", size=13, color=INK))

    # рівень E = 0 і вісь відстані
    els.append(line(x0, y0, 700, y0, color="#c8ccd2", sw=1.4, dash="5,5"))
    els.append(text(x0 - 12, y0 + 5, "0", size=12.5, color=MUTED, anchor="end"))
    for rr in (5, 10, 15):
        els.append(line(X(rr), y0 - 5, X(rr), y0 + 5, color="#c8ccd2", sw=1.2))
        els.append(text(X(rr), y0 + 22, "%d" % rr, size=12, color=MUTED))
    els.append(text(X(11), y0 + 44, "відстань до ядра, фм", size=13, color=MUTED))

    # яма ядра
    els.append(rect(X(0), Y(E_bar), X(R_nuc) - X(0), 440 - Y(E_bar),
                    fill="#eef4ff", stroke=NEG, sw=1.8, rx=2))
    els.append(text((X(0) + X(R_nuc)) / 2, 415, "ядро", size=13, color=NEG, bold=True))

    # кулонівський хвіст 4.32/r
    pts = []
    rr = R_nuc
    while rr <= 15.01:
        pts.append("%.1f,%.1f" % (X(rr), Y(4.32 / rr)))
        rr += 0.2
    els.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
               % (" ".join(pts), POS))

    # горизонталь класичного порогу
    els.append(line(x0, Y(E_bar), X(R_nuc) + 14, Y(E_bar), color=POS, sw=1.8, dash="6,4"))
    els.append(text(x0 - 12, Y(E_bar) - 8, "класичний поріг", size=12.5,
                    color=POS, anchor="end", bold=True))
    els.append(text(x0 - 12, Y(E_bar) + 10, "≈ 1.3 МеВ", size=12.5,
                    color=POS, anchor="end", bold=True))

    # горизонталь енергії протона
    els.append(line(x0, Y(E_p), X(r_out), Y(E_p), color=FIELD, sw=1.8, dash="6,4"))
    els.append(text(x0 - 12, Y(E_p) - 8, "протон із каскаду", size=12.5,
                    color=FIELD, anchor="end", bold=True))
    els.append(text(x0 - 12, Y(E_p) + 10, "≈ 0.3 МеВ", size=12.5,
                    color=FIELD, anchor="end", bold=True))

    # стрілка тунелювання — крізь тіло бар'єра, справа наліво
    els.append(arrow(X(r_out) - 6, Y(E_p), X(R_nuc) + 8, Y(E_p), color=FIELD, sw=2.4))
    els.append(text((X(R_nuc) + X(r_out)) / 2, Y(E_p) + 26,
                    "тунелювання крізь бар'єр", size=13, color=FIELD, bold=True))

    # пояснювальні рамки праворуч
    frag, w, h = textbox(795, 165,
                         "Класично: горб треба\nперелізти зверху —\nа це мільйон вольтів",
                         size=12.5, bold=True, stroke=POS, fill="#fdeeee",
                         min_w=280, color=POS)
    els.append(frag)
    frag, w, h = textbox(795, 385,
                         "Квантово: горб напівпрозорий.\nПучок 1 мкА — це 6·10¹²\nпротонів щосекунди, тож\nнавіть рідкісний успіх\nдає тисячі подій за секунду",
                         size=12.5, bold=True, stroke=FIELD, fill="#eef7ee",
                         min_w=280, color=FIELD)
    els.append(frag)

    render(os.path.join(IMG, "barrier.svg"), W, H, *els)


if __name__ == "__main__":
    fig_phases()
    fig_ladder()
    fig_barrier()
    print("done")


# ── Фігури до вставки «Просідання і пульсація каскаду» ───────────────────────

def _polyline(pts, color, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (" ".join("%.1f,%.1f" % p for p in pts), color, sw, d))


def fig_droop_ripple():
    """Три числа виходу: ідеал, верхівка, середнє, западина."""
    W, H = 1000, 400
    els = [text(W / 2, 30, "Під навантаженням вихід каскаду — пилка, а не число",
                size=17, bold=True)]

    x0, x1 = 300, 720
    y_ideal, y_max, y_mean, y_min = 100, 180, 222, 264
    xl_end, xl_start = 280, 295          # де кінчається підпис / починається лінія
    xr = 820                             # праворуч лінії тягнуться сюди

    # ідеал
    els.append(line(xl_start, y_ideal, xr, y_ideal, color=NEG, sw=2.2, dash="8,5"))
    els.append(text(xl_end, y_ideal + 5, "ідеал 2n·Vₚ", size=13, color=NEG,
                    anchor="end", bold=True))

    # три рівні пилки
    for yy, lbl, col, bold in ((y_max, "верхівка", POS, False),
                               (y_mean, "середнє U_вих", INK, True),
                               (y_min, "западина", MUTED, False)):
        els.append(line(xl_start, yy, xr, yy, color=MUTED, sw=1.2, dash="3,4"))
        els.append(text(xl_end, yy + 5, lbl, size=13, color=col, anchor="end", bold=bold))

    # сама пилка
    teeth = 4
    w = (x1 - x0) / teeth
    pts = []
    for i in range(teeth):
        pts.append((x0 + i * w, y_max))
        pts.append((x0 + (i + 1) * w, y_min))
        pts.append((x0 + (i + 1) * w, y_max))
    els.append(_polyline(pts, POS, sw=2.8))

    # вісь часу
    els.append(arrow(x0, 320, 745, 320, color=INK, sw=1.5))
    els.append(text(752, 326, "час", size=12.5, color=MUTED, anchor="start"))

    # моменти доливання
    for i in range(1, teeth + 1):
        xx = x0 + i * w
        els.append(arrow(xx, 340, xx, 300, color=NEG, sw=1.4))
    els.append(text(x0 + w, 362, "доливання", size=12.5, color=NEG))

    # просідання: подвійна стрілка від ідеалу до середнього
    xa = 760
    els.append(arrow(xa, (y_ideal + y_mean) / 2, xa, y_ideal, color=INK, sw=1.6))
    els.append(arrow(xa, (y_ideal + y_mean) / 2, xa, y_mean, color=INK, sw=1.6))
    els.append(mtext(828, 140, ["просідання", "2n·Vₚ − U_вих"], size=12.5,
                     color=INK, anchor="start", bold=True))

    # пульсація: подвійна стрілка від верхівки до западини
    xb = 810
    els.append(arrow(xb, y_mean, xb, y_max, color=POS, sw=1.6))
    els.append(arrow(xb, y_mean, xb, y_min, color=POS, sw=1.6))
    els.append(mtext(828, 242, ["пульсація", "U_пульс"], size=12.5,
                     color=POS, anchor="start", bold=True))

    render(os.path.join(IMG, "droop-ripple.svg"), W, H, *els)


def _diode_seg(x1, y1, x2, y2, color, fill):
    """Провід із діодом посередині; трикутник дивиться від (x1,y1) до (x2,y2)."""
    import math
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    px, py = -uy, ux
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    s = 9.0
    ax, ay = mx + ux * s, my + uy * s                       # вершина (катод)
    b1 = (mx - ux * s + px * s, my - uy * s + py * s)
    b2 = (mx - ux * s - px * s, my - uy * s - py * s)
    out = line(x1, y1, x2, y2, color=color, sw=2)
    out += ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" '
            'stroke-width="1.8"/>' % (b1[0], b1[1], b2[0], b2[1], ax, ay, fill, color))
    out += line(ax + px * s * 1.15, ay + py * s * 1.15,
                ax - px * s * 1.15, ay - py * s * 1.15, color=color, sw=2.4)
    return out


def fig_cascade_charge():
    """Скільки заряду проходить крізь конденсатор кожного щабля."""
    W, H = 980, 645
    n = 4
    els = [text(W / 2, 30, "За півперіод крізь k-й конденсатор проходить (n+1−k)·q",
                size=17, bold=True)]

    xo, xs = 380, 620                     # гойдливий / згладжувальний стовпці
    y0, step = 490, 80
    node = [y0 - k * step for k in range(n + 1)]        # node[0] — низ

    els.append(text(xo, 118, "гойдливий стовпець", size=13.5, color=NEG, bold=True))
    els.append(text(xs, 118, "згладжувальний стовпець", size=13.5, color=INK, bold=True))

    def cap(x, ytop, ybot, color):
        cy = (ytop + ybot) / 2
        e = line(x, ybot, x, cy + 9, color=color, sw=2)
        e += line(x - 23, cy + 9, x + 23, cy + 9, color=color, sw=2.6)
        e += line(x - 23, cy - 9, x + 23, cy - 9, color=color, sw=2.6)
        e += line(x, cy - 9, x, ytop, color=color, sw=2)
        return e

    for k in range(1, n + 1):
        els.append(cap(xo, node[k], node[k - 1], NEG))
        els.append(cap(xs, node[k], node[k - 1], INK))

    # діоди: доливання (горизонтальні) і розряд (навскіс угору)
    for k in range(1, n + 1):
        els.append(_diode_seg(xo, node[k], xs, node[k], POS, "#fdeeee"))
        els.append(_diode_seg(xs, node[k - 1], xo, node[k], NEG, "#eaf0fd"))

    for k in range(n + 1):
        els.append(circle(xo, node[k], 4, fill=INK, stroke=INK))
        els.append(circle(xs, node[k], 4, fill=INK, stroke=INK))

    # скільки заряду проходить
    for k in range(1, n + 1):
        cy = (node[k] + node[k - 1]) / 2
        amount = "%d·q" % (n + 1 - k) if k < n else "q"
        frag, _, _ = textbox(238, cy, "C′%d:  %s" % (k, amount), size=12.5,
                             bold=True, color=NEG, fill="#eaf0fd", stroke=NEG, min_w=126)
        els.append(frag)
        frag, _, _ = textbox(757, cy, "C%d:  %s" % (k, amount), size=12.5,
                             bold=True, color=INK, fill=FILL, stroke=LINE, min_w=126)
        els.append(frag)

    # джерело внизу гойдливого стовпця
    els.append(line(xo, node[0], xo, 530, color=NEG, sw=2))
    els.append(line(xo, 530, 300, 530, color=NEG, sw=2))
    els.append(text(292, 535, "∼ джерело", size=12.5, color=NEG, anchor="end", bold=True))

    # земля під згладжувальним стовпцем
    els.append(line(xs, node[0], xs, 528, color=INK, sw=2))
    for i, hw in enumerate((20, 13, 6)):
        els.append(line(xs - hw, 528 + i * 6, xs + hw, 528 + i * 6, color=INK, sw=2))

    # вихід
    els.append(arrow(xs, node[n], 762, node[n], color=POS, sw=2))
    els.append(text(772, node[n] + 5, "q → навантаження", size=12.5, color=POS,
                    anchor="start", bold=True))

    els.append(text(W / 2, 578, "червоні діоди — фаза доливання, сині — фаза розряду",
                    size=12.5, color=MUTED))
    els.append(text(W / 2, 602, "за ПОВНИЙ період крізь кожен діод проходить рівно q,",
                    size=12.5, color=INK))
    els.append(text(W / 2, 626, "тож усі 2n діодів проводять однаковий середній струм I",
                    size=12.5, color=INK))

    render(os.path.join(IMG, "cascade-charge.svg"), W, H, *els)


def fig_stages_optimum():
    """Вихід як функція числа щаблів: максимум і спад за ним."""
    W, H = 900, 500
    els = [text(W / 2, 30, "Ідеал росте як n, просідання — як n³: у кривої є максимум",
                size=17, bold=True)]

    ox, oy, top = 110, 420, 100
    n_max, v_max = 40.0, 190000.0
    sx = (800 - ox) / n_max
    sy = (oy - top) / v_max
    Vp, qc = 2000.0, 3.3333            # пік живлення і q/C з прикладу у тексті

    def X(nn):
        return ox + nn * sx

    def Y(v):
        return oy - v * sy

    def V(nn):
        return 2 * nn * Vp - (2.0 / 3.0) * nn ** 3 * qc

    # осі
    els.append(arrow(ox, oy, ox, top - 12, color=INK, sw=1.6))
    els.append(arrow(ox, oy, 812, oy, color=INK, sw=1.6))
    els.append(text(ox, top - 26, "вихід, кВ", size=12.5, color=INK))
    els.append(text(800, 466, "число щаблів n", size=12.5, color=INK, anchor="end"))

    for v in (50000, 100000, 150000):
        els.append(line(ox - 6, Y(v), ox, Y(v), color=INK, sw=1.4))
        els.append(text(ox - 12, Y(v) + 5, "%d" % (v / 1000), size=12,
                        color=MUTED, anchor="end"))
    for k in (0, 10, 20, 30, 40):
        els.append(line(X(k), oy, X(k), oy + 6, color=INK, sw=1.4))
        els.append(text(X(k), oy + 24, "%d" % k, size=12, color=MUTED))

    # ідеальна пряма
    els.append(line(X(0), Y(0), X(n_max), Y(2 * n_max * Vp), color=NEG, sw=2.4))

    # реальна крива
    pts = []
    nn = 0.0
    while nn <= n_max + 0.01:
        v = V(nn)
        if v < 0:
            v = 0.0
        pts.append((X(nn), Y(v)))
        nn += 0.5
    els.append(_polyline(pts, POS, sw=2.8))

    n_opt = (Vp / qc) ** 0.5
    els.append(line(X(n_opt), oy, X(n_opt), Y(V(n_opt)), color=MUTED, sw=1.3, dash="4,4"))
    els.append(circle(X(n_opt), Y(V(n_opt)), 5, fill=POS, stroke=POS))
    els.append(text(X(n_opt), 464, "n_опт ≈ %d" % round(n_opt), size=12.5,
                    color=POS, bold=True))

    # провал у точці оптимуму
    ymid = (Y(2 * n_opt * Vp) + Y(V(n_opt))) / 2
    els.append(arrow(X(n_opt), ymid, X(n_opt), Y(2 * n_opt * Vp), color=INK, sw=1.5))
    els.append(arrow(X(n_opt), ymid, X(n_opt), Y(V(n_opt)), color=INK, sw=1.5))
    frag, bw, bh = textbox(682, 272, "втрачено ⅓ ідеалу", size=12.5, bold=True,
                           color=INK, fill=FILL, stroke=LINE)
    els.append(line(682 - bw / 2, 277, X(n_opt) + 9, ymid + 15, color=MUTED, sw=1.2))
    els.append(frag)

    # легенда
    frag, _, _ = textbox(292, 136, ["синя пряма — ідеал 2n·Vₚ",
                                    "червона крива — реальний вихід"],
                         size=12.5, color=INK, fill=BG, stroke=MUTED)
    els.append(frag)
    els.append(text(292, 196, "після n_опт кожен новий щабель ЗНИЖУЄ вихід",
                    size=12.5, color=POS, bold=True))

    render(os.path.join(IMG, "stages-optimum.svg"), W, H, *els)


if __name__ == "__main__":
    fig_droop_ripple()
    fig_cascade_charge()
    fig_stages_optimum()
    print("done: droop-ripple, cascade-charge, stages-optimum")
