# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..','..','..','..','scripts')); from svgkit import *
import math, cmath

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


# ── Фігура 4: годограф L(jω) на комплексній площині, точка −1, обидва запаси ──

def fig_nyquist():
    W, H = 720, 560
    K = 3.4
    ppu = 106              # пікселів на одиницю комплексної площини
    cx, cy = 302, 250      # початок координат (зсунуто ліворуч-угору під форму годографа)
    m1x = cx - ppu         # точка −1 + j0

    def Lval(w):
        # три однакові полюси τ=1: класичний третій порядок
        return K / (1 + 1j * w) ** 3

    p = []

    # осі
    p.append(line(cx - 160, cy, cx + 280, cy, color=MUTED, sw=1.3))
    p.append(arrow(cx + 262, cy, cx + 282, cy, color=MUTED, sw=1.3))
    p.append(line(cx, cy - 150, cx, cy + 290, color=MUTED, sw=1.3))
    p.append(arrow(cx, cy - 132, cx, cy - 152, color=MUTED, sw=1.3))
    p.append(text(cx + 288, cy + 4, "Re", size=13, color=MUTED, anchor="start"))
    p.append(text(cx + 8, cy - 138, "Im", size=13, color=MUTED, anchor="start"))
    p.append(text(cx + 8, cy - 6, "0", size=12, color=MUTED, anchor="start"))

    # одиничне коло (|L|=1)
    p.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
             'stroke-width="1.3" stroke-dasharray="5 5"/>' % (cx, cy, ppu, MUTED))
    p.append(text(cx + ppu * 0.70 + 4, cy - ppu * 0.70 - 4, "|L|=1", size=11, color=MUTED, anchor="start"))

    # критична точка −1
    p.append(circle(m1x, cy, 5.5, fill=POS, stroke=POS))
    p.append(text(m1x - 4, cy - 12, "−1", size=14, color=POS, bold=True, anchor="end"))

    # годограф L(jω): трипольова система, з точки K на +Re осі вниз у ІІІ квадрант і назад до 0
    pts = []
    for i in range(0, 241):
        w = 0.02 + i / 240.0 * 4.2
        Lj = Lval(w)
        pts.append("%.1f,%.1f" % (cx + Lj.real * ppu, cy - Lj.imag * ppu))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(pts), INK))
    p.append(text(cx + K * ppu + 6, cy - 8, "ω→0", size=11, color=INK, anchor="start"))

    # ── частота кросовера (|L|=1): запас по фазі ──
    wlo, whi = 0.02, 9.0
    for _ in range(60):
        wm = 0.5 * (wlo + whi)
        if abs(Lval(wm)) > 1.0:
            wlo = wm
        else:
            whi = wm
    wc = 0.5 * (wlo + whi)
    Lc = Lval(wc)
    gx, gy = cx + Lc.real * ppu, cy - Lc.imag * ppu
    p.append(line(cx, cy, m1x - 6, cy, color=POS, sw=1.5, dash="4 3"))
    p.append(line(cx, cy, gx, gy, color=NEG, sw=1.8))
    p.append(circle(gx, gy, 5, fill=NEG, stroke=NEG))
    # дуга запасу по фазі — від −Re-піввісі до радіус-вектора
    r_arc = 60
    a0 = 180.0
    a1 = math.degrees(math.atan2(-(gy - cy), (gx - cx)))
    arc = []
    for k in range(41):
        a = math.radians(a0 + (a1 - a0) * k / 40.0)
        arc.append("%.1f,%.1f" % (cx + r_arc * math.cos(a), cy - r_arc * math.sin(a)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(arc), FIELD))
    bpm, wpm, hpm = textbox(cx - 128, cy + 150, "запас по фазі φ_m\n(кут до −1)",
                            size=12, color=FIELD, bold=True, fill="#eafaf0", stroke=FIELD)
    p.append(bpm)

    # ── частота фази −180° (перетин −Re-осі знизу вгору): запас по підсиленню ──
    # для трьох полюсів Im(L) від'ємне при ω<√3 і додатне трохи вище — шукаємо перехід
    def imL(w):
        return Lval(w).imag
    wlo, whi = 0.5, 3.5
    for _ in range(60):
        wm = 0.5 * (wlo + whi)
        if imL(wm) < 0:
            wlo = wm
        else:
            whi = wm
    wp = 0.5 * (wlo + whi)
    Lp = Lval(wp)
    px = cx + Lp.real * ppu
    p.append(circle(px, cy, 5, fill=POS, stroke=POS))
    # дужка запасу по підсиленню між точкою годографа (|Lp|<1) і точкою −1
    yb = cy - 44
    p.append(line(px, cy, px, yb, color=POS, sw=1.1, dash="3 3"))
    p.append(line(m1x, cy, m1x, yb, color=POS, sw=1.1, dash="3 3"))
    p.append(line(px, yb, m1x, yb, color=FIELD, sw=2.4))
    p.append(line(px, yb - 4, px, yb + 4, color=FIELD, sw=2.4))
    p.append(line(m1x, yb - 4, m1x, yb + 4, color=FIELD, sw=2.4))
    bgm, wgm, hgm = textbox((px + m1x) / 2, yb - 26, "запас по підсиленню = 1/|L|",
                            size=12, color=FIELD, bold=True, fill="#eafaf0", stroke=FIELD)
    p.append(bgm)

    render(os.path.join(OUT, "nyquist-plot.svg"), W, H, *p,
           title="Годограф L(jω): обидва запаси — це відстані до точки −1")


# ── Фігура 5: як накопичується фаза — мертвий час vs полюси ───────────────────

def fig_phase_accum():
    W, H = 780, 440
    ox, oy = 96, 360
    Ax, Ay = 600, 300
    p = []
    # осі
    p.append(line(ox, oy, ox + Ax + 30, oy, color=MUTED, sw=1.3))
    p.append(arrow(ox + Ax + 12, oy, ox + Ax + 32, oy, color=MUTED, sw=1.3))
    p.append(line(ox, oy, ox, oy - Ay - 12, color=MUTED, sw=1.3))
    p.append(arrow(ox, oy - Ay + 6, ox, oy - Ay - 14, color=MUTED, sw=1.3))
    p.append(text(ox + Ax + 40, oy + 5, "частота ω", size=12, color=MUTED, italic=True, anchor="end"))
    p.append(text(ox - 10, oy - Ay - 18, "зсув фази −∠L", size=13, color=INK, bold=True, anchor="start"))

    # рівні −90 −180 −270
    def yof(deg):   # deg додатне = стільки градусів відставання
        return oy - (deg / 300.0) * Ay
    for d in (90, 180, 270):
        p.append(line(ox, yof(d), ox + Ax, yof(d), color=MUTED, sw=0.9, dash="2 5"))
        p.append(text(ox - 8, yof(d) + 4, "−%d°" % d, size=11, color=MUTED, anchor="end"))
    # лінія −180 — критична
    p.append(line(ox, yof(180), ox + Ax + 6, yof(180), color=POS, sw=1.4, dash="6 5"))
    p.append(text(ox + Ax + 8, yof(180) + 4, "межа −180°", size=11, color=POS, anchor="start"))

    wmax = 10.0
    def xof(w):
        return ox + (w / wmax) * Ax

    # один полюс: arctan(ω·τ), τ=0.6 → стеля 90°
    pts1 = []
    for i in range(201):
        w = wmax * i / 200.0
        deg = math.degrees(math.atan(w * 0.6))
        pts1.append("%.1f,%.1f" % (xof(w), yof(deg)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts1), NEG))
    p.append(text(xof(wmax) - 6, yof(88) - 6, "один полюс → стеля 90°", size=12, color=NEG, anchor="end"))

    # три полюси: сума трьох arctan → до 270°
    pts3 = []
    for i in range(201):
        w = wmax * i / 200.0
        deg = math.degrees(math.atan(w * 0.6) + math.atan(w * 0.3) + math.atan(w * 0.15))
        pts3.append("%.1f,%.1f" % (xof(w), yof(deg)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts3), INK))
    p.append(text(xof(5.2), yof(150), "три полюси → дійде до 180° і далі", size=12, color=INK, anchor="start"))

    # мертвий час: лінійно Δφ = ω·Δt (Δt дібрано так, щоб перегнати полюси й
    # злетіти за −180° до верху графіка — демонстрація «без стелі»)
    ptsd = []
    slope_deg = math.degrees(0.52)      # градусів на одиницю ω
    for i in range(201):
        w = wmax * i / 200.0
        deg = slope_deg * w
        if deg > 295:
            break
        ptsd.append("%.1f,%.1f" % (xof(w), yof(deg)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" stroke-dasharray="7 4"/>' % (" ".join(ptsd), POS))
    p.append(mtext(xof(2.9), yof(238), ["чистий мертвий час →", "росте без стелі"],
                   size=12, color=POS, anchor="start"))

    render(os.path.join(OUT, "phase-accum.svg"), W, H, *p,
           title="Звідки 180°: полюс дає до 90° зі стелею, мертвий час — необмежено")


# ── Фігура 6: дискретизація додає фазове відставання (пів-семпл + обчислення) ──

def fig_sampling_lag():
    W, H = 780, 380
    ox, oy = 70, 210
    Ax, Ay = 300, 120
    p = []

    # ЛІВА панель: неперервний сигнал і його ступінчаста утримка (ZOH)
    p.append(text(ox + Ax / 2, 52, "утримка нульового порядку зсуває на T/2", size=13, bold=True))
    p.append(line(ox - 6, oy, ox + Ax + 12, oy, color=MUTED, sw=1.2))
    p.append(arrow(ox + Ax - 2, oy, ox + Ax + 14, oy, color=MUTED, sw=1.2))
    # неперервна синусоїда
    span = 1.6 * TWO_PI
    sx = Ax / span
    p.append(wave(ox, oy, sx, Ay * 0.5, lambda th: math.sin(th), NEG, sw=2.4, t1=span))
    # ступінчаста утримана (семпли через dt, тримається до наступного)
    N = 12
    dt = span / N
    stair = []
    for k in range(N + 1):
        th = k * dt
        val = math.sin(th)
        x1 = ox + th * sx
        y1 = oy - val * Ay * 0.5
        x2 = ox + min((k + 1) * dt, span) * sx
        stair.append("%.1f,%.1f" % (x1, y1))
        stair.append("%.1f,%.1f" % (x2, y1))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(stair), POS))
    p.append(text(ox + Ax * 0.5, oy + Ay * 0.5 + 34, "сходинки відстають у середньому на T/2", size=11, color=POS))
    p.append(line(ox + 6, 66, ox + 34, 66, color=NEG, sw=2.2))
    p.append(text(ox + 40, 70, "справжній сигнал", size=11, color=NEG, anchor="start"))

    # ПРАВА панель: запас по фазі проти частоти дискретизації
    ox2 = 430
    Ax2, Ay2 = 300, 240
    oy2 = 300
    p.append(text(ox2 + Ax2 / 2, 52, "рідший семпл — менший запас по фазі", size=13, bold=True))
    p.append(line(ox2, oy2, ox2 + Ax2 + 20, oy2, color=MUTED, sw=1.3))
    p.append(arrow(ox2 + Ax2 + 4, oy2, ox2 + Ax2 + 22, oy2, color=MUTED, sw=1.3))
    p.append(line(ox2, oy2, ox2, oy2 - Ay2 - 10, color=MUTED, sw=1.3))
    p.append(arrow(ox2, oy2 - Ay2 + 4, ox2, oy2 - Ay2 - 12, color=MUTED, sw=1.3))
    p.append(text(ox2 + Ax2 + 22, oy2 + 16, "частота fs", size=11, color=MUTED, italic=True, anchor="end"))
    p.append(text(ox2 - 6, oy2 - Ay2 - 16, "запас по фазі", size=12, color=INK, bold=True, anchor="start"))
    # крива: запас росте з частотою семпла і виходить на плато (запас неперервної петлі)
    # свіп від fs, де запас саме 0 (межа зриву), угору — крива стартує на нуль-лінії
    ptsm = []
    for i in range(0, 201):
        t = i / 200.0
        fs = 1.5 + t * 18.5          # частота семпла (в кратних до кросовера); від межі вгору
        # відставання дискретизації ~ пропорційне 1/fs; запас = PMinf − k/fs
        pm = 60.0 - 90.0 / fs
        xx = ox2 + t * Ax2
        yy = oy2 - (pm / 70.0) * Ay2
        ptsm.append("%.1f,%.1f" % (xx, yy))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(ptsm), FIELD))
    # плато-рівень запасу неперервної петлі
    yinf = oy2 - (60.0 / 70.0) * Ay2
    p.append(line(ox2, yinf, ox2 + Ax2, yinf, color=MUTED, sw=1.0, dash="4 5"))
    p.append(text(ox2 + Ax2 - 4, yinf - 6, "запас неперервної петлі", size=10, color=MUTED, anchor="end"))
    # нуль-лінія (втрата стійкості)
    p.append(line(ox2, oy2, ox2 + Ax2, oy2, color=POS, sw=1.0))
    p.append(text(ox2 + 6, oy2 - 6, "0° — зрив", size=10, color=POS, anchor="start"))

    render(os.path.join(OUT, "sampling-lag.svg"), W, H, *p,
           title="Дискретизація з'їдає запас: пів-семпла затримки + такт обчислень")


# ── Фігура 7: принцип аргументу — вектор до нуля робить оберт, до полюса ні ─────

def fig_argument_principle():
    W, H = 780, 470
    cx, cy = 300, 250       # центр площини s
    p = []

    # осі площини s
    p.append(line(cx - 210, cy, cx + 230, cy, color=MUTED, sw=1.2))
    p.append(arrow(cx + 212, cy, cx + 232, cy, color=MUTED, sw=1.2))
    p.append(line(cx, cy + 175, cx, cy - 185, color=MUTED, sw=1.2))
    p.append(arrow(cx, cy - 167, cx, cy - 187, color=MUTED, sw=1.2))
    p.append(text(cx + 236, cy + 4, "Re s", size=12, color=MUTED, anchor="start"))
    p.append(text(cx + 8, cy - 172, "Im s", size=12, color=MUTED, anchor="start"))

    # замкнений контур Γ (еліпс) — оббігаємо ділянку площини
    a, b = 150, 128
    cont = []
    for i in range(0, 121):
        t = TWO_PI * i / 120.0
        cont.append("%.1f,%.1f" % (cx + a * math.cos(t), cy - b * math.sin(t)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join(cont), INK))
    # стрілка напряму (за годинниковою) на контурі
    ta = math.radians(58)
    axp, ayp = cx + a * math.cos(ta), cy - b * math.sin(ta)
    tb = math.radians(50)
    bxp, byp = cx + a * math.cos(tb), cy - b * math.sin(tb)
    p.append(arrow(axp, ayp, bxp, byp, color=INK, sw=2.0))
    p.append(text(cx + a * 0.72 + 6, cy - b * 0.72 - 8, "Γ", size=15, color=INK, bold=True, anchor="start"))

    # нуль z0 ВСЕРЕДИНІ контуру
    z0x, z0y = cx - 46, cy - 24
    p.append(circle(z0x, z0y, 6, fill="#eafaf0", stroke=FIELD, sw=2.2))
    p.append(text(z0x - 10, z0y - 10, "нуль z₀", size=12, color=FIELD, bold=True, anchor="end"))

    # полюс p0 ЗЗОВНІ контуру
    p0x, p0y = cx + 220, cy + 128
    p.append(text(p0x, p0y + 4, "×", size=22, color=POS, bold=True))
    p.append(text(p0x, p0y + 24, "полюс p₀ (зовні)", size=12, color=POS, anchor="middle"))

    # вектори (s − z0) у кількох положеннях s на контурі — показати повний оберт
    for t in (10, 70, 130, 190, 250, 310):
        r = math.radians(t)
        sx = cx + a * math.cos(r)
        sy = cy - b * math.sin(r)
        p.append(line(z0x, z0y, sx, sy, color=FIELD, sw=1.3, dash="3 3"))
        p.append(circle(sx, sy, 2.6, fill=INK, stroke=INK))
    # виділений вектор
    r = math.radians(10)
    sx = cx + a * math.cos(r); sy = cy - b * math.sin(r)
    p.append(arrow(z0x, z0y, sx, sy, color=FIELD, sw=2.0))

    # пояснення праворуч
    b1, w1, h1 = textbox(cx + 150, cy - 150,
                         "s біжить по Γ →\nвектор (s − z₀) робить\nПОВНИЙ оберт (360°)",
                         size=12, color=FIELD, bold=True, fill="#eafaf0", stroke=FIELD)
    p.append(b1)
    b2, w2, h2 = textbox(cx + 12, cy + 205,
                         "вектор (s − p₀) від зовнішнього полюса лише погойдується — 0 обертів",
                         size=12, color=POS, bold=True, fill="#fdecea", stroke=POS)
    p.append(b2)

    render(os.path.join(OUT, "argument-principle.svg"), W, H, *p,
           title="Принцип аргументу: кожен обведений нуль — один оберт, полюс — мінус один")


# ── Фігура 8: контур Найквіста — уся уявна вісь + нескінченне півколо на праву ─

def fig_nyquist_contour():
    W, H = 720, 540
    cx, cy = 250, 270
    Rax = 150               # «нескінченне» півколо (умовний радіус)
    p = []

    # осі s
    p.append(line(cx - 120, cy, cx + 300, cy, color=MUTED, sw=1.2))
    p.append(arrow(cx + 282, cy, cx + 302, cy, color=MUTED, sw=1.2))
    p.append(line(cx, cy + 210, cx, cy - 220, color=MUTED, sw=1.2))
    p.append(arrow(cx, cy - 202, cx, cy - 222, color=MUTED, sw=1.2))
    p.append(text(cx + 300, cy + 18, "Re s", size=12, color=MUTED, anchor="end"))
    p.append(text(cx + 10, cy - 206, "Im s", size=12, color=MUTED, anchor="start"))

    # заливка правої півплощини (легка)
    p.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 0 %.1f %.1f L %.1f %.1f Z" '
             'fill="#fdecea" opacity="0.5"/>'
             % (cx, cy - Rax, Rax, Rax, cx, cy + Rax, cx, cy - Rax))

    # уявна вісь як частина контуру (згори вниз — стрілки вниз = за годинниковою)
    p.append(line(cx, cy - Rax, cx, cy + Rax, color=INK, sw=2.6))
    p.append(arrow(cx, cy - 40, cx, cy + 4, color=INK, sw=2.4))
    p.append(arrow(cx, cy + 70, cx, cy + 112, color=INK, sw=2.4))
    p.append(text(cx - 10, cy - Rax + 6, "+j∞", size=12, color=INK, anchor="end", bold=True))
    p.append(text(cx - 10, cy + Rax + 2, "−j∞", size=12, color=INK, anchor="end", bold=True))

    # нескінченне півколо праворуч (охоплює праву півплощину)
    semi = []
    for i in range(0, 81):
        ang = math.radians(90 - 180.0 * i / 80.0)   # від +90° до −90°
        semi.append("%.1f,%.1f" % (cx + Rax * math.cos(ang), cy - Rax * math.sin(ang)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(semi), INK))
    # стрілка на півколі (напрям за годинниковою, праворуч)
    a0 = math.radians(6); a1 = math.radians(-6)
    p.append(arrow(cx + Rax * math.cos(a0), cy - Rax * math.sin(a0),
                   cx + Rax * math.cos(a1), cy - Rax * math.sin(a1), color=INK, sw=2.4))
    p.append(text(cx + Rax * 0.80 + 4, cy - Rax * 0.62,
                  "R → ∞", size=12, color=INK, anchor="start", bold=True))

    # нестійкий полюс замкненої системи (нуль 1+L) у правій півплощині
    zx, zy = cx + 66, cy - 52
    p.append(circle(zx, zy, 6, fill="#eafaf0", stroke=FIELD, sw=2.2))
    p.append(mtext(zx + 12, zy - 4, ["нуль 1+L", "(= нестійкий полюс)"], size=11, color=FIELD, anchor="start"))

    # напівколова виїмка навколо полюса L на осі (для інтегратора в нулі)
    ind = []
    for i in range(0, 41):
        ang = math.radians(90 - 180.0 * i / 40.0)
        ind.append("%.1f,%.1f" % (cx + 16 * math.cos(ang), cy - 16 * math.sin(ang)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="4 3"/>'
             % (" ".join(ind), NEG))
    p.append(mtext(cx + 22, cy + 44, ["виїмка навколо", "полюса на осі", "(інтегратор)"],
                   size=10, color=NEG, anchor="start"))

    # підпис правої півплощини
    p.append(text(cx + Rax * 0.5, cy - Rax - 12, "уся права півплощина — зона нестійкості",
                  size=12, color=POS, bold=True))

    render(os.path.join(OUT, "nyquist-contour.svg"), W, H, *p,
           title="Контур Найквіста: обвести всю праву півплощину за годинниковою")


# ── Фігура 9: умовно стійка система — менше підсилення охоплює −1 ──────────────

def fig_conditional():
    W, H = 780, 430
    ppu = 62
    m1x_off = -ppu          # −1 у пікселях від центру

    def hodo(cx, cy, K, col, lab):
        # годограф із «пірнанням» — форма, що за великого K обходить −1 справа,
        # а за меншого K стягується так, що охоплює −1 (умовна стійкість).
        q = []
        # осі
        q.append(line(cx - 150, cy, cx + 110, cy, color=MUTED, sw=1.1))
        q.append(arrow(cx + 94, cy, cx + 112, cy, color=MUTED, sw=1.1))
        q.append(line(cx, cy - 95, cx, cy + 95, color=MUTED, sw=1.1))
        q.append(text(cx + 116, cy + 4, "Re", size=11, color=MUTED, anchor="start"))
        # точка −1
        q.append(circle(cx + m1x_off, cy, 4.5, fill=POS, stroke=POS))
        q.append(text(cx + m1x_off, cy + 18, "−1", size=12, color=POS, bold=True))
        # параметрична крива з подвійним завитком (умовно-стійка форма)
        pts = []
        for i in range(0, 201):
            th = math.pi * i / 200.0            # 0..π
            # базова форма: велика петля + мала внутрішня
            re = -math.cos(th) * (1.0 - 0.55 * math.sin(2 * th))
            im = -math.sin(th) * (1.0 - 0.75 * math.sin(th))
            pts.append("%.1f,%.1f" % (cx + K * re * ppu, cy - K * im * ppu))
        # дзеркальна нижня половина (спряжена)
        for i in range(200, -1, -1):
            th = math.pi * i / 200.0
            re = -math.cos(th) * (1.0 - 0.55 * math.sin(2 * th))
            im = -math.sin(th) * (1.0 - 0.75 * math.sin(th))
            pts.append("%.1f,%.1f" % (cx + K * re * ppu, cy + K * im * ppu))
        q.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join(pts), col))
        q.append(text(cx - 20, cy - 78, lab, size=12, color=col, bold=True))
        return q

    p = []
    p += hodo(220, 235, 1.10, FIELD, "номінальне K — повз −1 (стійко)")
    b1, w1, h1 = textbox(220, 388, "крива обходить −1 справа → N=0",
                         size=11, color=FIELD, bold=True, fill="#eafaf0", stroke=FIELD)
    p.append(b1)

    p += hodo(560, 235, 0.66, POS, "менше K — охопило −1 (зрив!)")
    b2, w2, h2 = textbox(560, 388, "стягнута крива охопила −1 → N=2",
                         size=11, color=POS, bold=True, fill="#fdecea", stroke=POS)
    p.append(b2)

    render(os.path.join(OUT, "conditional-stability.svg"), W, H, *p,
           title="Умовна стійкість: зменшення підсилення стягує криву НА −1")


# ── Фігура (вставка proj): розгортка фази — сира atan2 стрибає, unwrap робить неперервною ─

def fig_phase_unwrap():
    W, H = 780, 460
    ox, oy = 84, 250
    Ax, Ay = 610, 150
    p = []

    # осі
    p.append(line(ox - 8, oy, ox + Ax + 30, oy, color=MUTED, sw=1.3))
    p.append(arrow(ox + Ax + 12, oy, ox + Ax + 32, oy, color=MUTED, sw=1.3))
    p.append(line(ox, oy - Ay - 12, ox, oy + Ay + 12, color=MUTED, sw=1.3))
    p.append(arrow(ox, oy - Ay + 4, ox, oy - Ay - 14, color=MUTED, sw=1.3))
    p.append(text(ox + Ax + 40, oy + 5, "частота (лог)", size=12, color=MUTED, italic=True, anchor="end"))
    p.append(text(ox - 10, oy - Ay - 18, "фаза ∠L", size=13, color=INK, bold=True, anchor="start"))

    # шкала фази: рівні +180 / 0 / −180 / −360
    def yof(deg):                    # -360..+180 у вікні
        return oy - (deg / 360.0) * Ay
    for d, lab in ((180, "+180°"), (0, "0°"), (-180, "−180°"), (-360, "−360°")):
        col = POS if d == -180 else MUTED
        dash = "6 5" if d == -180 else "2 6"
        p.append(line(ox, yof(d), ox + Ax + 6, yof(d), color=col, sw=(1.4 if d == -180 else 0.9), dash=dash))
        p.append(text(ox - 8, yof(d) + 4, lab, size=11, color=col, anchor="end"))

    # справжня (неперервно спадна) фаза: від 0 до −300°, монотонно
    def phi_true(t):                 # t∈[0,1]
        return -300.0 * (t ** 1.15)

    # РОЗГОРНУТА (суцільна, FIELD): просто phi_true
    ptsU = []
    for i in range(0, 201):
        t = i / 200.0
        ptsU.append("%.1f,%.1f" % (ox + Ax * t, yof(phi_true(t))))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(ptsU), FIELD))

    # СИРА (пунктир, POS): та сама фаза, згорнута в (−180,+180] → стрибок угору
    def wrap(d):
        while d <= -180.0: d += 360.0
        while d > 180.0:   d -= 360.0
        return d
    # малюємо сегментами, розриваючи там, де відбувається стрибок
    seg = []
    prev = None
    for i in range(0, 201):
        t = i / 200.0
        w = wrap(phi_true(t))
        if prev is not None and abs(w - prev) > 180.0:
            # завершити сегмент до стрибка й почати новий
            p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="7 4"/>' % (" ".join(seg), POS))
            seg = []
        seg.append("%.1f,%.1f" % (ox + Ax * t, yof(w)))
        prev = w
    if seg:
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="7 4"/>' % (" ".join(seg), POS))

    # позначка стрибка на +180
    # знайти t, де сира перескакує
    for i in range(1, 201):
        t0 = (i - 1) / 200.0; t1 = i / 200.0
        if abs(wrap(phi_true(t1)) - wrap(phi_true(t0))) > 180.0:
            xj = ox + Ax * t1
            p.append(line(xj, yof(180) - 6, xj, yof(-180) + 6, color=POS, sw=1.0, dash="2 3"))
            bj, wj, hj = textbox(xj + 4, yof(150) - 6, "стрибок 360°\n(розрив atan2)",
                                 size=11, color=POS, bold=True, fill="#fdecea", stroke=POS)
            p.append(bj)
            break

    # легенда
    p.append(line(ox + 8, oy + Ay + 30, ox + 42, oy + Ay + 30, color=FIELD, sw=2.8))
    p.append(text(ox + 48, oy + Ay + 34, "розгорнута (unwrap) — неперервна", size=12, color=FIELD, anchor="start"))
    p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.2" stroke-dasharray="7 4"/>'
             % (ox + 360, oy + Ay + 30, ox + 394, oy + Ay + 30, POS))
    p.append(text(ox + 400, oy + Ay + 34, "сира atan2 — стрибає на 360°", size=12, color=POS, anchor="start"))

    render(os.path.join(OUT, "phase-unwrap.svg"), W, H, *p,
           title="Розгортка фази: сира atan2 стрибає, unwrap робить криву неперервною")


# ── Фігура (вставка proj): годограф + векторний запас (найкоротша відстань до −1) ─

def fig_hodograph_vector():
    W, H = 720, 560
    K = 3.4
    ppu = 104
    cx, cy = 300, 250
    m1x = cx - ppu                   # точка −1

    def Lval(w):
        return K / (1 + 1j * w) ** 3  # три однакові полюси — класичний третій порядок

    p = []

    # осі
    p.append(line(cx - 160, cy, cx + 280, cy, color=MUTED, sw=1.3))
    p.append(arrow(cx + 262, cy, cx + 282, cy, color=MUTED, sw=1.3))
    p.append(line(cx, cy - 150, cx, cy + 290, color=MUTED, sw=1.3))
    p.append(arrow(cx, cy - 132, cx, cy - 152, color=MUTED, sw=1.3))
    p.append(text(cx + 288, cy + 4, "Re L", size=13, color=MUTED, anchor="start"))
    p.append(text(cx + 8, cy - 138, "Im L", size=13, color=MUTED, anchor="start"))
    p.append(text(cx + 8, cy - 6, "0", size=12, color=MUTED, anchor="start"))

    # одиничне коло |L|=1
    p.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
             'stroke-width="1.2" stroke-dasharray="5 5"/>' % (cx, cy, ppu, MUTED))
    p.append(text(cx + ppu * 0.68 + 6, cy - ppu * 0.68 - 6, "|L|=1", size=11, color=MUTED, anchor="start"))

    # критична точка −1
    p.append(circle(m1x, cy, 5.5, fill=POS, stroke=POS))
    p.append(text(m1x - 6, cy - 12, "−1", size=14, color=POS, bold=True, anchor="end"))

    # годограф
    ws = [0.02 + i / 260.0 * 4.4 for i in range(0, 261)]
    pts = []
    for w in ws:
        Lj = Lval(w)
        pts.append("%.1f,%.1f" % (cx + Lj.real * ppu, cy - Lj.imag * ppu))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(pts), INK))
    p.append(text(cx + K * ppu + 6, cy - 8, "ω→0", size=11, color=INK, anchor="start"))

    # ── ВЕКТОРНИЙ ЗАПАС: найкоротша відстань годографа до −1 ──
    best = None
    for w in ws:
        Lj = Lval(w)
        d = abs(complex(Lj.real + 1.0, Lj.imag))
        if best is None or d < best[0]:
            best = (d, Lj)
    Lbest = best[1]
    bx, by = cx + Lbest.real * ppu, cy - Lbest.imag * ppu
    # зелений відрізок від −1 до найближчої точки кривої
    p.append(line(m1x, cy, bx, by, color=FIELD, sw=2.8))
    p.append(circle(bx, by, 4.6, fill=FIELD, stroke=FIELD))
    bsm, wsm, hsm = textbox(cx - 150, cy + 168, "векторний запас Sₘ\n= найкоротша відстань до −1",
                            size=12, color=FIELD, bold=True, fill="#eafaf0", stroke=FIELD)
    p.append(bsm)

    # для контрасту — тонко показати, де класичні запаси міряють (осі)
    # кросовер |L|=1
    wlo, whi = 0.02, 9.0
    for _ in range(60):
        wm = 0.5 * (wlo + whi)
        if abs(Lval(wm)) > 1.0: wlo = wm
        else: whi = wm
    wc = 0.5 * (wlo + whi); Lc = Lval(wc)
    gx, gy = cx + Lc.real * ppu, cy - Lc.imag * ppu
    p.append(circle(gx, gy, 4.0, fill=NEG, stroke=NEG))
    p.append(mtext(gx + 8, gy - 6, ["тут міряють", "запас по фазі"], size=10, color=NEG, anchor="start"))
    # −180° (перетин від'ємної дійсної осі)
    def imL(w): return Lval(w).imag
    wlo, whi = 0.5, 3.5
    for _ in range(60):
        wm = 0.5 * (wlo + whi)
        if imL(wm) < 0: wlo = wm
        else: whi = wm
    wp = 0.5 * (wlo + whi); Lp = Lval(wp)
    px = cx + Lp.real * ppu
    p.append(circle(px, cy, 4.0, fill=NEG, stroke=NEG))
    p.append(mtext(px - 6, cy + 20, ["тут міряють запас", "по підсиленню"], size=10, color=NEG, anchor="middle"))

    render(os.path.join(OUT, "hodograph-vector.svg"), W, H, *p,
           title="Годограф і векторний запас: найкоротша відстань кривої до −1")


if __name__ == "__main__":
    fig_loop_delay()
    fig_margins()
    fig_three_regimes()
    fig_nyquist()
    fig_phase_accum()
    fig_sampling_lag()
    fig_argument_principle()
    fig_nyquist_contour()
    fig_conditional()
    fig_phase_unwrap()
    fig_hodograph_vector()
    print("OK: figures written to", OUT)
