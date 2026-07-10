# -*- coding: utf-8 -*-
# Фігури детальної статті «Вартість як атрибут».
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def polyline(pts, color=INK, sw=2.4, dash=None, fill="none"):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s '
            'stroke-linejoin="round" stroke-linecap="round"/>' % (p, fill, color, sw, d))


def polygon(pts, fill, opacity=0.16):
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return '<polygon points="%s" fill="%s" fill-opacity="%.2f" stroke="none"/>' % (p, fill, opacity)


# ── Фігура 1: гроші в часі — номінал проти теперішньої вартості ──────────────
def fig_discount():
    W, H = 760, 430
    y0 = 360
    els = []
    els.append(text(W / 2, 60, "сірий — номінал 1000 $ · синій — теперішня вартість (PV), r = 10 %",
                    size=12, color=MUTED, italic=True))

    gx = [140, 255, 370, 485, 600]
    bw = 64
    nom_h = 250                       # висота, що зображує 1000 $
    pv = [909, 826, 751, 683, 621]    # 1000/1.1^n, n=1..5
    els.append(line(100, y0, 700, y0, color=INK, sw=1.6))   # базова лінія

    for i, x in enumerate(gx):
        # сірий стовпчик номіналу (повна висота)
        els.append(rect(x - bw / 2, y0 - nom_h, bw, nom_h, fill="#e5e7eb", stroke="#c8ccd2", sw=1.2))
        # синій стовпчик теперішньої вартості (нижча частина, попереду)
        h = pv[i] / 1000.0 * nom_h
        els.append(rect(x - bw / 2, y0 - h, bw, h, fill="#dbe6fb", stroke=NEG, sw=1.6))
        els.append(text(x, y0 - h - 9, "%d" % pv[i], size=12, color=NEG, bold=True))
        els.append(text(x, y0 + 22, "рік %d" % (i + 1), size=13))

    els.append(text(W / 2, H - 14,
                    "що дальша витрата, то менша її вага сьогодні — синій тане, сірий проміжок росте",
                    size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, 'discount.svg'), W, H, *els,
           title="Гроші в часі: однаковий номінал важить сьогодні по-різному")


# ── Фігура 2: крива вартості зміни — жорстка проти гнучкої ───────────────────
def fig_change_curve():
    W, H = 760, 440
    x_l, x_r = 100, 690
    y0, y_top = 360, 70
    plotH = y0 - y_top
    els = []

    def px(t):
        return x_l + t * (x_r - x_l)

    def py(v):
        return y0 - v * plotH

    a = math.log(12.5)                         # exp(a)=12.5 при t=1
    exp_pts = [(px(t / 40.0), py(0.08 * math.exp(a * t / 40.0))) for t in range(41)]
    lin_pts = [(px(t / 40.0), py(0.08 + 0.32 * t / 40.0)) for t in range(41)]

    # заштрихований проміжок = технічний борг
    els.append(polygon(exp_pts + lin_pts[::-1], POS, opacity=0.12))

    els.append(line(x_l, y0, x_r, y0, color=INK, sw=1.6))          # вісь X
    els.append(line(x_l, y0, x_l, y_top, color=INK, sw=1.6))       # вісь Y
    els.append(polyline(exp_pts, color=POS, sw=2.6))
    els.append(polyline(lin_pts, color=FIELD, sw=2.6))

    els.append(text(x_l + 6, y_top - 4, "вартість однієї зміни", size=12, color=MUTED, anchor="start"))
    els.append(text(W / 2, y0 + 34, "час життя / зростання системи  →", size=13, color=MUTED))

    b1, _, _ = textbox(612, 96, "жорстка\n(зчеплення)", size=12, bold=True,
                       min_w=132, fill="#fdecea", stroke=POS, color=POS)
    els.append(b1)
    b2, _, _ = textbox(600, 300, "гнучка\n(межі)", size=12, bold=True,
                       min_w=120, fill="#eafaf0", stroke=FIELD, color=FIELD)
    els.append(b2)
    els.append(text(545, 246, "технічний борг", size=12, color=POS, italic=True))

    render(os.path.join(OUT, 'change-curve.svg'), W, H, *els,
           title="Крива вартості зміни: складний відсоток проти пологого росту")


# ── Фігура 3: точка беззбитковості за обсягом ────────────────────────────────
def fig_breakeven():
    W, H = 760, 440
    x_l, x_r = 100, 690
    y0, y_top = 360, 70
    plotH = y0 - y_top
    vmax = 3000.0                # млн запитів/міс
    cmax = 12000.0               # $ (стеля шкали)
    els = []

    def px(v):
        return x_l + v / vmax * (x_r - x_l)

    def py(c):
        return y0 - c / cmax * plotH

    A = [(px(0), py(0)), (px(vmax), py(4 * vmax))]            # F=0, m=4
    B = [(px(0), py(5000)), (px(vmax), py(5000 + 1 * vmax))]  # F=5000, m=1
    vstar = 5000 / (4 - 1)       # 1666.7

    els.append(line(x_l, y0, x_r, y0, color=INK, sw=1.6))
    els.append(line(x_l, y0, x_l, y_top, color=INK, sw=1.6))
    # вертикаль беззбитковості (не проходить крізь написи)
    els.append(line(px(vstar), 118, px(vstar), y0, color=MUTED, sw=1.4, dash="6,5"))
    els.append(polyline(A, color=POS, sw=2.6))
    els.append(polyline(B, color=NEG, sw=2.6))

    els.append(text(x_l + 6, y_top - 4, "місячна вартість, $", size=12, color=MUTED, anchor="start"))
    els.append(text(W / 2, y0 + 34, "обсяг v — запитів на місяць  →", size=13, color=MUTED))

    els.append(text(px(vstar), 104, "беззбитковість  v* ≈ 1.67 млрд", size=12, color=INK, bold=True))
    b1, _, _ = textbox(628, 92, "A: поштучно", size=12, bold=True,
                       min_w=128, fill="#fdecea", stroke=POS, color=POS)
    els.append(b1)
    b2, _, _ = textbox(612, 300, "B: зарезервовано", size=12, bold=True,
                       min_w=170, fill="#eaf0fd", stroke=NEG, color=NEG)
    els.append(b2)
    els.append(text(250, 336, "A дешевша", size=12, color=POS, italic=True))
    els.append(text(560, 336, "B дешевша", size=12, color=NEG, italic=True))

    render(os.path.join(OUT, 'breakeven.svg'), W, H, *els,
           title="Точка беззбитковості: постійна проти граничної вартості")


# ── Фігура 4: стійкість під невизначеністю — крихкий проти стійкого ──────────
def fig_robustness():
    W, H = 760, 440
    x_l, x_r = 100, 690
    y0, y_top = 360, 70
    plotH = y0 - y_top
    cmax = 70.0                  # тис. $
    els = []

    def px(load):
        return x_l + load * (x_r - x_l)

    def py(c):
        return y0 - c / cmax * plotH

    def fragile(load):
        return 8 + 4 * load + 500 * max(0.0, load - 0.55) ** 2

    def robust(load):
        return 11 + 13 * load

    frag_pts = [(px(t / 44.0 * 0.88), py(fragile(t / 44.0 * 0.88))) for t in range(45)]
    rob_pts = [(px(t / 44.0 * 0.88), py(robust(t / 44.0 * 0.88))) for t in range(45)]

    els.append(line(x_l, y0, x_r, y0, color=INK, sw=1.6))
    els.append(line(x_l, y0, x_l, y_top, color=INK, sw=1.6))
    els.append(line(px(0.5), 116, px(0.5), y0, color=MUTED, sw=1.4, dash="6,5"))
    els.append(polyline(frag_pts, color=POS, sw=2.6))
    els.append(polyline(rob_pts, color=FIELD, sw=2.6))

    els.append(text(x_l + 6, y_top - 4, "вартість, тис. $", size=12, color=MUTED, anchor="start"))
    els.append(text(W / 2, y0 + 34, "навантаження — гірше  →", size=13, color=MUTED))

    els.append(text(px(0.5), 102, "очікувана точка", size=12, color=INK, bold=True))
    b1, _, _ = textbox(548, 108, "крихкий", size=12, bold=True,
                       min_w=112, fill="#fdecea", stroke=POS, color=POS)
    els.append(b1)
    b2, _, _ = textbox(612, 306, "стійкий", size=12, bold=True,
                       min_w=112, fill="#eafaf0", stroke=FIELD, color=FIELD)
    els.append(b2)
    els.append(text(196, 336, "низьке", size=11, color=MUTED))
    els.append(text(602, 336, "високе", size=11, color=MUTED))

    render(os.path.join(OUT, 'robustness.svg'), W, H, *els,
           title="Стійкість під невизначеністю: дешеве в точці ≠ дешеве в діапазоні")


if __name__ == '__main__':
    fig_discount()
    fig_change_curve()
    fig_breakeven()
    fig_robustness()
    print("figs_d done")
