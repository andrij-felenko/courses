# -*- coding: utf-8 -*-
# Фігури математичної вкладки «Теперішня вартість» (math-npv.md).
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def polyline(pts, color=INK, sw=2.6, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s '
            'stroke-linejoin="round" stroke-linecap="round"/>' % (p, color, sw, d))


def A(r, N=5):
    return N if r == 0 else (1 - (1 + r) ** (-N)) / r


# ── Фігура 1: множник ануїтету A(r) — форма, границя й корінь беззбитковості ──
def fig_annuity_r():
    W, H = 780, 470
    x_l, x_r = 120, 715
    y0, y_top = 395, 90
    plotH = y0 - y_top
    rmax, amax = 0.55, 5.2
    els = []

    def px(r):
        return x_l + r / rmax * (x_r - x_l)

    def py(a):
        return y0 - a / amax * plotH

    # осі
    els.append(line(x_l, y0, x_r, y0, color=INK, sw=1.6))
    els.append(line(x_l, y0, x_l, y_top, color=INK, sw=1.6))

    # горизонталь A = N = 5 (границя r → 0)
    els.append(line(x_l, py(5), px(0.155), py(5), color=MUTED, sw=1.3, dash="6,5"))
    els.append(text(px(0.165), py(5) + 4, "A → N = 5  при  r → 0", size=12, color=MUTED, anchor="start"))

    # крива A(r)
    pts = [(px(rmax * i / 240), py(A(rmax * i / 240))) for i in range(241)]
    els.append(polyline(pts, color=NEG, sw=2.6))

    # рівень беззбитковості A = 3.75 → r*
    rstar = 0.10425
    els.append(line(x_l, py(3.75), px(rstar), py(3.75), color=POS, sw=1.4, dash="6,5"))
    els.append(line(px(rstar), py(3.75), px(rstar), y0, color=POS, sw=1.4, dash="6,5"))
    els.append(circle(px(rstar), py(3.75), 4.6, fill=POS, stroke=POS, sw=1))
    els.append(text(px(rstar) + 10, py(3.75) - 12, "A(r*) = 3.75", size=12.5, color=POS, bold=True, anchor="start"))
    els.append(text(px(rstar), y0 + 22, "r* ≈ 10.4 %", size=12.5, color=POS, bold=True))

    # підпис кривої
    els.append(text(px(0.345), py(3.5), "A(r) = (1 − (1+r)⁻ᴺ) / r", size=13.5, color=NEG, anchor="start", bold=True))

    # підписи осей
    els.append(text(x_l + 4, y_top - 8, "множник ануїтету  A  (N = 5)", size=12, color=MUTED, anchor="start"))
    els.append(text(W / 2, y0 + 46, "ставка дисконтування  r  →", size=13, color=MUTED))

    # позначки по X (10% віддано під r*)
    for rr in (0.2, 0.3, 0.4, 0.5):
        els.append(line(px(rr), y0, px(rr), y0 + 5, color=INK, sw=1.2))
        els.append(text(px(rr), y0 + 20, "%d%%" % (rr * 100), size=11, color=MUTED))
    els.append(line(px(0.1), y0, px(0.1), y0 + 5, color=POS, sw=1.2))

    render(os.path.join(OUT, 'annuity-r.svg'), W, H, *els,
           title="Множник ануїтету: спадає з r, при r → 0 сходиться до N")


# ── Фігура 2: беззбитковість за ставкою — дві теперішні вартості перетинаються ─
def fig_breakeven_rate():
    W, H = 800, 480
    x_l, x_r = 120, 720
    y0, y_top = 395, 95
    plotH = y0 - y_top
    rmax, vmax = 0.5, 320.0
    els = []

    def px(r):
        return x_l + r / rmax * (x_r - x_l)

    def py(v):
        return y0 - v / vmax * plotH

    def build(r):
        return 150 + 20 * A(r)

    def buy(r):
        return 60 * A(r)

    rstar = 0.10425
    # смуги рішення (за спиною осей)
    els.append(rect(x_l, y_top, px(rstar) - x_l, y0 - y_top, fill="#eafaf0", stroke="none", sw=0, rx=0))
    els.append(rect(px(rstar), y_top, x_r - px(rstar), y0 - y_top, fill="#fdecea", stroke="none", sw=0, rx=0))

    # осі
    els.append(line(x_l, y0, x_r, y0, color=INK, sw=1.6))
    els.append(line(x_l, y0, x_l, y_top, color=INK, sw=1.6))

    bp = [(px(rmax * i / 200), py(build(rmax * i / 200))) for i in range(201)]
    sp = [(px(rmax * i / 200), py(buy(rmax * i / 200))) for i in range(201)]
    els.append(polyline(bp, color=FIELD, sw=2.8))
    els.append(polyline(sp, color=NEG, sw=2.8))

    # r* — вертикаль і точка перетину
    els.append(line(px(rstar), py(build(rstar)), px(rstar), y0, color=MUTED, sw=1.3, dash="6,5"))
    els.append(circle(px(rstar), py(build(rstar)), 4.6, fill=INK, stroke=INK, sw=1))
    els.append(text(px(rstar), y0 + 22, "r* ≈ 10.4 %", size=12.5, bold=True))

    # розрив на r = 35 %
    rg = 0.35
    els.append(line(px(rg), py(build(rg)), px(rg), py(buy(rg)), color=INK, sw=1.5))
    els.append(text(px(rg) + 9, (py(build(rg)) + py(buy(rg))) / 2 + 4,
                    "розрив ≈ 61 тис.", size=12, color=INK, anchor="start"))

    # підписи кривих
    els.append(text(px(0.29), py(build(0.29)) - 15, "будувати:  150 + 20·A(r)", size=12, color=FIELD, bold=True))
    els.append(text(px(0.29), py(buy(0.29)) + 22, "купити:  60·A(r)", size=12, color=NEG, bold=True))

    # мітки смуг
    els.append(text((x_l + px(rstar)) / 2, y_top + 20, "будувати", size=11.5, color=FIELD, bold=True))
    els.append(text((x_l + px(rstar)) / 2, y_top + 36, "дешевше", size=11.5, color=FIELD, bold=True))
    els.append(text(px(0.42), y_top + 20, "купити дешевше", size=11.5, color=POS, bold=True))

    # осі-підписи
    els.append(text(x_l + 4, y_top - 10, "теперішня вартість витрат, тис. $", size=12, color=MUTED, anchor="start"))
    els.append(text(W / 2, y0 + 46, "ставка дисконтування  r  →", size=13, color=MUTED))
    for rr in (0.2, 0.3, 0.4, 0.5):
        els.append(line(px(rr), y0, px(rr), y0 + 5, color=INK, sw=1.2))
        els.append(text(px(rr), y0 + 20, "%d%%" % (rr * 100), size=11, color=MUTED))
    els.append(line(px(0.1), y0, px(0.1), y0 + 5, color=INK, sw=1.2))

    render(os.path.join(OUT, 'breakeven-rate.svg'), W, H, *els,
           title="Беззбитковість за ставкою: біля r* — нічия, далі рішення тверде")


# ── Фігура 3: як обрати r — вартість капіталу плюс ризик не дожити ────────────
def fig_choose_r():
    W, H = 800, 470
    y0, y_top = 395, 95
    plotH = y0 - y_top
    rmax = 0.60
    els = []

    def py(r):
        return y0 - r / rmax * plotH

    # осі
    els.append(line(122, y0, 122, y_top, color=INK, sw=1.6))
    els.append(line(122, y0, 705, y0, color=INK, sw=1.6))
    for rr in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6):
        els.append(line(118, py(rr), 122, py(rr), color=INK, sw=1.2))
        els.append(text(114, py(rr) + 4, "%d%%" % (rr * 100), size=11, color=MUTED, anchor="end"))

    # поріг r*
    rstar = 0.10425
    els.append(line(122, py(rstar), 705, py(rstar), color=POS, sw=1.5, dash="7,5"))
    els.append(text(128, py(rstar) - 12, "поріг r* ≈ 10.4 %", size=12, color=POS, bold=True, anchor="start"))

    bw = 130
    # зріла контора: капітал 10 %, ризику майже нема
    cx1 = 300
    els.append(rect(cx1 - bw / 2, py(0.10), bw, y0 - py(0.10), fill="#eaf0fd", stroke=NEG, sw=1.6))
    els.append(text(cx1, (py(0.10) + y0) / 2 + 4, "капітал 10%", size=12, color=NEG, bold=True))
    els.append(text(cx1, y0 + 24, "зріла контора", size=13, bold=True))
    els.append(text(cx1, y0 + 44, "r ≈ 10% → будувати", size=11.5, color=FIELD, bold=True))

    # стартап на межі: капітал 10 % + ризик 30 %
    cx2 = 560
    els.append(rect(cx2 - bw / 2, py(0.10), bw, y0 - py(0.10), fill="#eaf0fd", stroke=NEG, sw=1.6))
    els.append(text(cx2, (py(0.10) + y0) / 2 + 4, "капітал 10%", size=12, color=NEG, bold=True))
    seg_top, seg_bot = py(0.40), py(0.10)
    els.append(rect(cx2 - bw / 2, seg_top, bw, seg_bot - seg_top, fill="#fdecea", stroke=POS, sw=1.6))
    els.append(text(cx2, (seg_top + seg_bot) / 2 - 4, "ризик не", size=12, color=POS, bold=True))
    els.append(text(cx2, (seg_top + seg_bot) / 2 + 14, "дожити +30%", size=12, color=POS, bold=True))
    els.append(text(cx2, y0 + 24, "стартап на межі", size=13, bold=True))
    els.append(text(cx2, y0 + 44, "r ≈ 40% → купити", size=11.5, color=POS, bold=True))

    render(os.path.join(OUT, 'choose-r.svg'), W, H, *els,
           title="Ставка r = вартість капіталу + ризик не дожити до вигоди")


if __name__ == '__main__':
    fig_annuity_r()
    fig_breakeven_rate()
    fig_choose_r()
    print("figs_math done")
