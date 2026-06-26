# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..','..','..','..','scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

TWO_PI = 2 * math.pi


def wave(ox, oy, sx, Ay, fn, color, sw=2.6, n=320, t0=0.0, t1=None, env=None):
    """Полілінія fn(θ) на θ∈[t0..t1]; env(θ) — необов'язкова обвідна (множник амплітуди)."""
    if t1 is None:
        t1 = TWO_PI
    pts = []
    for i in range(n + 1):
        th = t0 + (t1 - t0) * i / n
        a = env(th) if env else 1.0
        x = ox + (th - t0) * sx
        y = oy - fn(th) * Ay * a
        pts.append("%.2f,%.2f" % (x, y))
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>'
            % (" ".join(pts), color, sw))


# ── Фігура 1: запізнення в петлі робить з гасіння підкачку ────────────────────

def fig_loop_delay():
    W, H = 760, 460
    ox = 86
    Ax = 600
    span = 2.0 * TWO_PI
    sx = Ax / span
    Ay = 78

    def panel(oy, lag, title_txt, helps):
        q = []
        # вісь часу
        q.append(line(ox - 12, oy, ox + Ax + 34, oy, color=MUTED, sw=1.3))
        q.append(arrow(ox + Ax + 16, oy, ox + Ax + 36, oy, color=MUTED, sw=1.3))
        q.append(text(ox - 20, oy - Ay - 18, title_txt, size=14, color=INK, bold=True, anchor="start"))
        # відхилення (що треба гасити) — суцільна
        q.append(wave(ox, oy, sx, Ay, lambda th: math.sin(th), INK, sw=2.6, t1=span))
        # виправлення, зсунуте на lag (запізнення в петлі); знак «−», бо зв'язок від'ємний
        cor_color = FIELD if helps else POS
        q.append(wave(ox, oy, sx, Ay * 0.82,
                      lambda th: -math.sin(th - lag), cor_color, sw=2.6, t1=span))
        return q

    p = []
    p += panel(118, math.radians(35), "мале запізнення — виправлення майже навпроти відхилення", True)
    b1, w1, h1 = textbox(ox + Ax * 0.5, 118 + Ay + 30,
                         "виправлення тягне ПРОТИ відхилення → гасить",
                         size=12, color=FIELD, bold=True, fill="#eafaf0", stroke=FIELD)
    p.append(b1)

    p += panel(330, math.pi, "запізнення сягнуло пів-періоду (зсув 180°)", False)
    b2, w2, h2 = textbox(ox + Ax * 0.5, 330 + Ay + 30,
                         "виправлення збіглося з відхиленням → підкачує",
                         size=12, color=POS, bold=True, fill="#fdecea", stroke=POS)
    p.append(b2)

    # легенда
    p.append(line(ox + 6, 60, ox + 40, 60, color=INK, sw=2.6))
    p.append(text(ox + 46, 64, "відхилення", size=12, color=INK, anchor="start"))
    p.append(line(ox + 220, 60, ox + 254, 60, color=FIELD, sw=2.6))
    p.append(text(ox + 260, 64, "виправлення (затримане в петлі)", size=12, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "loop-delay.svg"), W, H, *p,
           title="Чому зворотний зв'язок розгойдує: затримане виправлення міняє знак")


# ── Фігура 2: запас по підсиленню й по фазі на кривих петлі ───────────────────

def fig_margins():
    W, H = 770, 500
    # дві осі частоти (логарифмічної на вигляд), спільна горизонтальна шкала
    ox = 92
    Ax = 600
    # частота кросовера підсилення (де |L|=1) і частота фази 180°
    x_gco = ox + Ax * 0.52      # тут підсилення падає до 1
    x_pco = ox + Ax * 0.70      # тут фаза доходить до −180°

    p = []

    # ── верх: підсилення в дБ ──
    oy1 = 150
    Hb = 150
    top1 = oy1 - Hb * 0.5
    bot1 = oy1 + Hb * 0.5
    p.append(text(ox - 24, top1 - 20, "Підсилення петлі |L|", size=14, bold=True, anchor="start"))
    # осі
    p.append(line(ox, top1 - 6, ox, bot1 + 6, color=MUTED, sw=1.3))
    p.append(line(ox - 6, bot1, ox + Ax + 30, bot1, color=MUTED, sw=1.3))
    p.append(arrow(ox + Ax + 14, bot1, ox + Ax + 32, bot1, color=MUTED, sw=1.3))
    p.append(text(ox + Ax + 40, bot1 + 5, "частота", size=12, color=MUTED, italic=True, anchor="end"))
    # лінія 0 дБ (|L| = 1)
    y0 = oy1
    p.append(line(ox, y0, ox + Ax + 6, y0, color=NEG, sw=1.4, dash="6 5"))
    p.append(text(ox + Ax + 8, y0 + 4, "0 дБ (|L|=1)", size=11, color=NEG, anchor="start"))
    # спадна крива підсилення (падає зліва направо)
    pts = []
    for i in range(0, 121):
        t = i / 120.0
        xx = ox + Ax * t
        # від +такого до −такого, перетинає 0 дБ у x_gco
        db = 1.0 - t / 0.52        # 1 на старті, 0 у t=0.52
        yy = y0 - db * (Hb * 0.42)
        pts.append("%.1f,%.1f" % (xx, yy))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(pts), INK))
    # вертикаль на частоті фази 180° (x_pco): запас по підсиленню = провал нижче 0 дБ
    p.append(line(x_pco, top1 - 6, x_pco, bot1 + 24, color=POS, sw=1.3, dash="4 4"))
    # точка кривої на x_pco
    t_pco = (x_pco - ox) / Ax
    db_pco = 1.0 - t_pco / 0.52
    y_pco = y0 - db_pco * (Hb * 0.42)
    p.append(circle(x_pco, y_pco, 4.5, fill=POS, stroke=POS))
    # дужка запасу по підсиленню між кривою (нижче 0) і лінією 0 дБ
    p.append(line(x_pco - 26, y0, x_pco - 26, y_pco, color=FIELD, sw=2.2))
    p.append(line(x_pco - 30, y0, x_pco - 22, y0, color=FIELD, sw=2.2))
    p.append(line(x_pco - 30, y_pco, x_pco - 22, y_pco, color=FIELD, sw=2.2))
    bg, wbg, hbg = textbox(x_pco - 100, (y0 + y_pco) / 2, "запас по\nпідсиленню",
                           size=12, color=FIELD, bold=True, fill="#eafaf0", stroke=FIELD)
    p.append(bg)

    # ── низ: фаза в градусах ──
    oy2 = 360
    Hb2 = 150
    top2 = oy2 - Hb2 * 0.5
    bot2 = oy2 + Hb2 * 0.5
    p.append(text(ox - 24, top2 - 20, "Зсув фази петлі ∠L", size=14, bold=True, anchor="start"))
    p.append(line(ox, top2 - 6, ox, bot2 + 6, color=MUTED, sw=1.3))
    p.append(line(ox - 6, bot2, ox + Ax + 30, bot2, color=MUTED, sw=1.3))
    p.append(arrow(ox + Ax + 14, bot2, ox + Ax + 32, bot2, color=MUTED, sw=1.3))
    p.append(text(ox + Ax + 40, bot2 + 5, "частота", size=12, color=MUTED, italic=True, anchor="end"))
    # лінія −180°
    y180 = oy2 + Hb2 * 0.36
    p.append(line(ox, y180, ox + Ax + 6, y180, color=POS, sw=1.4, dash="6 5"))
    p.append(text(ox + Ax + 8, y180 + 4, "−180°", size=11, color=POS, anchor="start"))
    # спадна крива фази (від 0 до за −180)
    pts2 = []
    for i in range(0, 121):
        t = i / 120.0
        xx = ox + Ax * t
        # фаза від 0 до приблизно −210°, доходить до −180 у t=0.70
        ph = -210.0 * (t ** 1.25)
        yy = oy2 - (ph / 210.0) * (Hb2 * 0.42) - (Hb2 * 0.0)
        # масштаб: 0° біля top, −180 на y180
        yy = top2 + (-ph / 210.0) * (bot2 - top2) * 0.95
        pts2.append("%.1f,%.1f" % (xx, yy))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(pts2), INK))
    # вертикаль на частоті кросовера підсилення (x_gco): запас по фазі = відстань кривої до −180°
    p.append(line(x_gco, top2 - 24, x_gco, bot2 + 6, color=NEG, sw=1.3, dash="4 4"))
    # також продовжимо цю вертикаль угору на верхню панель — це частота |L|=1
    p.append(line(x_gco, top1 - 6, x_gco, bot1 + 6, color=NEG, sw=1.1, dash="2 4"))
    t_gco = (x_gco - ox) / Ax
    ph_gco = -210.0 * (t_gco ** 1.25)
    y_gco = top2 + (-ph_gco / 210.0) * (bot2 - top2) * 0.95
    p.append(circle(x_gco, y_gco, 4.5, fill=NEG, stroke=NEG))
    # дужка запасу по фазі між кривою і лінією −180°
    p.append(line(x_gco + 26, y_gco, x_gco + 26, y180, color=FIELD, sw=2.2))
    p.append(line(x_gco + 22, y_gco, x_gco + 30, y_gco, color=FIELD, sw=2.2))
    p.append(line(x_gco + 22, y180, x_gco + 30, y180, color=FIELD, sw=2.2))
    bf, wbf, hbf = textbox(x_gco + 108, (y_gco + y180) / 2, "запас\nпо фазі",
                           size=12, color=FIELD, bold=True, fill="#eafaf0", stroke=FIELD)
    p.append(bf)

    # підписи частот унизу
    p.append(text(x_gco, bot2 + 22, "частота, де |L|=1", size=11, color=NEG))
    p.append(text(x_pco, bot1 + 38, "частота, де фаза = −180°", size=11, color=POS))

    render(os.path.join(OUT, "margins.svg"), W, H, *p,
           title="Два запаси стійкості: скільки лишилося до |L|=1 при −180°")


# ── Фігура 3: три режими за одного зростання підсилення ───────────────────────

def fig_three_regimes():
    W, H = 800, 260
    Ax = 200
    span = 3.0 * TWO_PI
    sx = Ax / span
    Ay = 44
    oy = 142
    gap = 248
    x0 = 60
    CAP = 1.95              # стеля амплітуди в частках Ay (щоб хвиля не вилазила за панель)

    def panel(ox, decay, title_txt, color, note):
        q = []
        q.append(line(ox - 8, oy, ox + Ax + 16, oy, color=MUTED, sw=1.2))
        # обвідна: decay<0 згасає, =0 стала, >0 росте; обмежена стелею CAP
        env = lambda th: min(math.exp(decay * th), CAP)
        q.append(wave(ox, oy, sx, Ay, lambda th: math.sin(th), color, sw=2.4, t1=span, env=env))
        # пунктирна обвідна зверху
        epts_top, epts_bot = [], []
        for i in range(81):
            th = span * i / 80.0
            a = env(th)
            xx = ox + th * sx
            epts_top.append("%.1f,%.1f" % (xx, oy - Ay * a))
            epts_bot.append("%.1f,%.1f" % (xx, oy + Ay * a))
        q.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.0" stroke-dasharray="3 4"/>' % (" ".join(epts_top), MUTED))
        q.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.0" stroke-dasharray="3 4"/>' % (" ".join(epts_bot), MUTED))
        q.append(text(ox + Ax / 2, 52, title_txt, size=13, color=color, bold=True))
        q.append(text(ox + Ax / 2, oy + Ay + 40, note, size=11, color=MUTED))
        return q

    p = []
    p += panel(x0, -0.14, "запас є", FIELD, "коливання згасають")
    p += panel(x0 + gap, 0.0, "запасу нема (межа)", NEG, "сталі коливання")
    p += panel(x0 + 2 * gap, 0.10, "запас від'ємний", POS, "коливання ростуть")

    render(os.path.join(OUT, "three-regimes.svg"), W, H, *p,
           title="Той самий контур, що більше підсилення: згасає → дзвенить → іде вразнос")


if __name__ == "__main__":
    fig_loop_delay()
    fig_margins()
    fig_three_regimes()
    print("OK: figures written to", OUT)
