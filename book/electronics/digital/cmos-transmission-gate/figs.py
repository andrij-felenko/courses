# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def nmos(cx, cy, label="N", gate_txt=None):
    """Спрощений символ n-канального МОН-ключа: вертикальний канал, затвор зліва."""
    out = []
    # канал (стік зверху, витік знизу)
    out.append(line(cx, cy - 34, cx, cy + 34, color=INK, sw=2.4))
    # затвор
    out.append(line(cx - 30, cy, cx - 10, cy, color=INK, sw=2))
    out.append(line(cx - 10, cy - 16, cx - 10, cy + 16, color=INK, sw=2.4))
    out.append(circle(cx, cy, 22, fill="none", stroke=MUTED, sw=1))
    out.append(text(cx + 14, cy - 24, label, size=13, color=MUTED, bold=True, anchor="start"))
    if gate_txt:
        out.append(text(cx - 34, cy + 4, gate_txt, size=13, color=INK, anchor="end"))
    return "".join(out)


def pmos(cx, cy, label="P", gate_txt=None):
    """Спрощений символ p-канального МОН-ключа: кружок на затворі."""
    out = []
    out.append(line(cx, cy - 34, cx, cy + 34, color=INK, sw=2.4))
    out.append(line(cx - 30, cy, cx - 16, cy, color=INK, sw=2))
    out.append(circle(cx - 13, cy, 5, fill=BG, stroke=INK, sw=2))
    out.append(line(cx - 8, cy - 16, cx - 8, cy + 16, color=INK, sw=2.4))
    out.append(circle(cx, cy, 22, fill="none", stroke=MUTED, sw=1))
    out.append(text(cx + 14, cy - 24, label, size=13, color=MUTED, bold=True, anchor="start"))
    if gate_txt:
        out.append(text(cx - 34, cy + 4, gate_txt, size=13, color=INK, anchor="end"))
    return "".join(out)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 1 — проблема: одинокий ключ не дотягує до однієї з шин
# ─────────────────────────────────────────────────────────────────────────────
def fig_weak_rail():
    W, H = 720, 360
    f = []
    f.append(text(W / 2, 26, "Чому одного транзистора замало", size=17, bold=True))

    # ---- ліва панель: NMOS пропускає 1 кволо ----
    cx = 185
    f.append(text(cx, 60, "Сам NMOS пропускає «1»", size=14, bold=True))
    # вхід 1
    f.append(line(cx - 120, 150, cx - 30, 150, color=POS, sw=2.2))
    f.append(text(cx - 120, 138, "вхід = Vdd", size=12, color=POS, anchor="start"))
    f.append(nmos(cx, 150, label="NMOS", gate_txt="затвор=1"))
    # вихід
    f.append(line(cx, 116, cx, 95, color=INK, sw=2))
    f.append(line(cx, 184, cx, 205, color=INK, sw=2))
    f.append(line(cx + 30, 150, cx + 95, 150, color=INK, sw=2.2))
    f.append(circle(cx + 95, 150, 4, fill=INK, stroke=INK))
    f.append(text(cx + 100, 146, "вихід", size=12, color=INK, anchor="start"))
    b = fitbox(cx - 95, 235, 190, 70,
               "застрягає на\nVdd − Vth\n(квола «1»)", size=13, bold=True,
               fill="#fdecea", stroke=POS, color=POS)
    f.append(b)

    # роздільник
    f.append(line(W / 2, 50, W / 2, 318, color=MUTED, sw=1, dash="4 4"))

    # ---- права панель: PMOS пропускає 0 кволо ----
    cx = 535
    f.append(text(cx, 60, "Сам PMOS пропускає «0»", size=14, bold=True))
    f.append(line(cx - 120, 150, cx - 30, 150, color=NEG, sw=2.2))
    f.append(text(cx - 120, 138, "вхід = 0 В", size=12, color=NEG, anchor="start"))
    f.append(pmos(cx, 150, label="PMOS", gate_txt="затвор=0"))
    f.append(line(cx, 116, cx, 95, color=INK, sw=2))
    f.append(line(cx, 184, cx, 205, color=INK, sw=2))
    f.append(line(cx + 30, 150, cx + 95, 150, color=INK, sw=2.2))
    f.append(circle(cx + 95, 150, 4, fill=INK, stroke=INK))
    f.append(text(cx + 100, 146, "вихід", size=12, color=INK, anchor="start"))
    b = fitbox(cx - 95, 235, 190, 70,
               "застрягає на\n|Vtp| над нулем\n(кволий «0»)", size=13, bold=True,
               fill="#eaf0fd", stroke=NEG, color=NEG)
    f.append(b)

    render(os.path.join(OUT, "weak-rail.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 2 — будова прохідного ключа: N || P, керування C та C̄
# ─────────────────────────────────────────────────────────────────────────────
def fig_structure():
    W, H = 700, 380
    f = []
    f.append(text(W / 2, 26, "Прохідний ключ: NMOS і PMOS пліч-о-пліч", size=17, bold=True))

    xin, xout = 120, 580
    ymid = 200
    # вхідний/вихідний вузли
    f.append(line(xin, ymid, 250, ymid, color=INK, sw=2.4))
    f.append(circle(xin, ymid, 5, fill=INK, stroke=INK))
    f.append(text(xin - 8, ymid + 5, "A", size=15, bold=True, anchor="end"))
    f.append(text(xin - 8, ymid + 24, "сигнал", size=11, color=MUTED, anchor="end"))
    f.append(line(450, ymid, xout, ymid, color=INK, sw=2.4))
    f.append(circle(xout, ymid, 5, fill=INK, stroke=INK))
    f.append(text(xout + 10, ymid + 5, "B", size=15, bold=True, anchor="start"))
    f.append(text(xout + 10, ymid + 24, "сигнал", size=11, color=MUTED, anchor="start"))

    # дві гілки: NMOS згори, PMOS знизу
    yN, yP = 135, 265
    for y in (yN, yP):
        f.append(line(250, ymid, 250, y, color=INK, sw=2))
        f.append(line(250, y, 300, y, color=INK, sw=2))
        f.append(line(400, y, 450, y, color=INK, sw=2))
        f.append(line(450, y, 450, ymid, color=INK, sw=2))

    # NMOS (горизонтальний канал між 300..400 на yN)
    f.append(line(300, yN, 400, yN, color=INK, sw=2.4))
    f.append(line(350, yN - 18, 350, yN - 4, color=INK, sw=2.4))   # затвор-пластина
    f.append(line(350, yN - 18, 350, yN - 40, color=INK, sw=2))
    f.append(text(312, yN - 6, "NMOS", size=12, color=MUTED, bold=True, anchor="start"))
    # PMOS
    f.append(line(300, yP, 400, yP, color=INK, sw=2.4))
    f.append(circle(350, yP + 9, 5, fill=BG, stroke=INK, sw=2))    # кружок-інверсія
    f.append(line(350, yP + 14, 350, yP + 40, color=INK, sw=2))
    f.append(text(312, yP + 22, "PMOS", size=12, color=MUTED, bold=True, anchor="start"))

    # керування: C на NMOS, C̄ на PMOS через інвертор
    f.append(line(350, yN - 40, 350, 70, color=POS, sw=2))
    f.append(text(356, 66, "C  (керування)", size=13, color=POS, bold=True, anchor="start"))
    f.append(line(350, yP + 40, 350, 330, color=NEG, sw=2))
    # інвертор-трикутник
    ix, iy = 350, 330
    f.append("".join([
        '<path d="M%d %d L%d %d L%d %d Z" fill="%s" stroke="%s" stroke-width="1.5"/>'
        % (ix - 16, iy - 14, ix - 16, iy + 14, ix + 12, iy, FILL, INK),
        circle(ix + 17, iy, 4, fill=BG, stroke=INK, sw=1.5),
    ]))
    f.append(line(ix - 16, iy, ix - 70, iy, color=POS, sw=2))
    f.append(line(ix - 70, iy, ix - 70, 70, color=POS, sw=2))   # той самий C на вхід інвертора
    f.append(line(ix - 70, 70, ix, 70, color=POS, sw=2))        # тай-вузол: інвертор бере той самий C
    f.append(circle(ix, 70, 4, fill=POS, stroke=POS))
    f.append(text(ix - 6, iy + 4, "не", size=10, color=MUTED, anchor="middle"))
    f.append(text(ix + 26, iy + 4, "C̄", size=13, color=NEG, bold=True, anchor="start"))

    # підпис-станова рамка
    b = fitbox(40, 318, 220, 48,
               "C = 1 → обидва відкриті (замкнено)\nC = 0 → обидва закриті (розрив)",
               size=11, fill=FILL, stroke=LINE)
    f.append(b)

    render(os.path.join(OUT, "structure.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 3 — опір відкритого ключа: два горби, що доповнюють один одного
# ─────────────────────────────────────────────────────────────────────────────
def fig_ron():
    W, H = 700, 400
    f = []
    f.append(text(W / 2, 26, "Опір відкритого ключа в межах розмаху сигналу", size=17, bold=True))

    # осі
    ox, oy = 110, 320          # початок (низ-ліво)
    axw, axh = 480, 230
    f.append(arrow(ox, oy, ox + axw + 10, oy, color=INK, sw=1.8))   # X
    f.append(arrow(ox, oy, ox, oy - axh - 10, color=INK, sw=1.8))   # Y
    f.append(text(ox + axw + 14, oy + 5, "Vсигн", size=12, anchor="start"))
    f.append(text(ox - 8, oy - axh - 14, "Ron", size=12, anchor="middle"))
    f.append(text(ox - 6, oy + 18, "0", size=11, color=MUTED, anchor="end"))
    f.append(text(ox + axw, oy + 18, "Vdd", size=11, color=MUTED, anchor="middle"))

    import math
    def curve(fn, color, sw=2.2, dash=None):
        pts = []
        for i in range(0, 101):
            vx = i / 100.0
            x = ox + vx * axw
            y = oy - fn(vx) * axh
            pts.append("%.1f,%.1f" % (x, y))
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
                % (" ".join(pts), color, sw, d))

    # NMOS: опір малий біля 0, росте до Vdd
    fn = lambda v: 0.18 + 0.72 * (v ** 2.2)
    # PMOS: дзеркально — малий біля Vdd, росте до 0
    fp = lambda v: 0.18 + 0.72 * ((1 - v) ** 2.2)
    # паралель двох провідностей -> сумарний опір (нормований, лишається обмеженим)
    def fpar(v):
        gn = 1.0 / fn(v)
        gp = 1.0 / fp(v)
        r = 1.0 / (gn + gp)
        return r * 1.9   # масштаб для видимості

    f.append(curve(fn, NEG, sw=1.8, dash="5 4"))
    f.append(curve(fp, POS, sw=1.8, dash="5 4"))
    f.append(curve(fpar, FIELD, sw=2.8))

    # підписи кривих
    f.append(text(ox + axw - 4, oy - fn(0.97) * axh - 8, "NMOS", size=12, color=NEG, bold=True, anchor="end"))
    f.append(text(ox + 6, oy - fp(0.03) * axh - 8, "PMOS", size=12, color=POS, bold=True, anchor="start"))
    f.append(text(ox + axw / 2, oy - fpar(0.5) * axh - 12, "разом (паралель)", size=12.5, color=FIELD, bold=True))

    b = fitbox(ox + axw - 188, oy - axh + 4, 188, 56,
               "сумарний опір лишається\nневеликим в УСЬОМУ\nдіапазоні сигналу",
               size=11, fill="#eafaf1", stroke=FIELD, color="#1e8449")
    f.append(b)

    render(os.path.join(OUT, "ron.svg"), W, H, *f)


if __name__ == "__main__":
    fig_weak_rail()
    fig_structure()
    fig_ron()
    print("figs written to", OUT)
