# -*- coding: utf-8 -*-
"""Фігури ДЕТАЛЬНОЇ статті «І-складова» (integral-control-d.md). Запуск: python figs_detailed.py
svgkit імпортуємо зі scripts/ (не переписуємо). Базові фігури — у figs.py; тут — лише ті,
що потрібні глибшій статті: reset-time, антивіндап-схеми, tracking-time, правила дискретного
інтегрування, інтеграл на лінійно змінному завданні."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def polyline(pts, color=INK, sw=2.6, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.2f,%.2f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"%s/>' % (s, color, sw, d))


def polygon(pts, fill, stroke="none", sw=1.0):
    s = " ".join("%.2f,%.2f" % (x, y) for x, y in pts)
    return '<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (s, fill, stroke, sw)


def axes(ox, oy, ax_w, ax_h, xlabel="час", ylabel=None):
    q = [line(ox, oy, ox, oy - ax_h, color=INK, sw=1.6),
         arrow(ox, oy - ax_h + 14, ox, oy - ax_h, color=INK, sw=1.6),
         line(ox, oy, ox + ax_w, oy, color=INK, sw=1.6),
         arrow(ox + ax_w - 14, oy, ox + ax_w, oy, color=INK, sw=1.6)]
    if xlabel:
        q.append(text(ox + ax_w, oy + 18, xlabel, size=12, color=MUTED, italic=True, anchor="end"))
    if ylabel:
        q.append(text(ox - 4, oy - ax_h + 4, ylabel, size=12, color=MUTED, anchor="end"))
    return q


def legend_row(x, y, color, label, sw=2.6, dash=None):
    return (line(x, y, x + 26, y, color=color, sw=sw, dash=dash) +
            text(x + 32, y + 4, label, size=11, color=color, anchor="start", bold=True))


# ── 1: reset-time Ti — інтеграл повторює пропорційну дію за Ti секунд ──────────
def fig_reset_time():
    W, H = 720, 340
    ox, oy = 92, 250
    ax_w, ax_h = 556, 200
    p = axes(ox, oy, ax_w, ax_h, ylabel="вплив u")

    base = oy
    top = oy - ax_h + 30
    sp = base - top

    P_jump = sp * 0.30                       # висота пропорційного стрибка Kp·e
    x0 = ox + ax_w * 0.10                     # момент появи сталої помилки

    # пропорційний внесок — сходинка на рівні P_jump
    pP = [(ox, base), (x0, base), (x0, base - P_jump), (ox + ax_w, base - P_jump)]
    p.append(polyline(pP, color=NEG, sw=2.4))

    # інтегральний внесок — нахилена пряма (рампа Ki·∫e)
    Ti = ax_w * 0.40                          # за Ti інтеграл набирає рівно P_jump
    def integ_y(x):
        return base - P_jump * ((x - x0) / Ti)
    pI = [(ox, base), (x0, base)]
    for i in range(0, 121):
        x = x0 + (ox + ax_w - x0) * (i / 120.0)
        pI.append((x, integ_y(x)))
    p.append(polyline(pI, color=FIELD, sw=2.6))

    # позначка Ti: де інтеграл зрівнявся з P
    x_ti = x0 + Ti
    y_ti = base - P_jump
    p.append(line(x_ti, base, x_ti, y_ti, color=MUTED, sw=1.2, dash="3 4"))
    p.append(line(x0, y_ti, x_ti, y_ti, color=MUTED, sw=1.0, dash="2 4"))

    # дужка Ti знизу
    yb = base + 22
    p.append(line(x0, yb, x_ti, yb, color=INK, sw=1.4))
    p.append(line(x0, yb - 4, x0, yb + 4, color=INK, sw=1.4))
    p.append(line(x_ti, yb - 4, x_ti, yb + 4, color=INK, sw=1.4))
    p.append(text((x0 + x_ti) / 2, yb + 16, "Ti — час інтегрування", size=11, color=INK, bold=True))

    p.append(text(ox + ax_w - 6, base - P_jump - 8, "Kp·e — пропорційний стрибок", size=11, color=NEG, anchor="end"))
    p.append(text(x_ti + 10, y_ti - 26, "за Ti інтеграл\nнабрав стільки ж", size=11, color=FIELD))

    render(os.path.join(OUT, "reset-time.svg"), W, H, *p,
           title="Час інтегрування Ti: за скільки інтеграл повторює пропорційний внесок")


# ── 2: три антивіндап-схеми — сигнальні структури ─────────────────────────────
def fig_antiwindup_schemes():
    W, H = 720, 430

    def box(cx, cy, w, h, s, fill=FILL, stroke=INK, color=INK, size=12, bold=False):
        x, y = cx - w / 2, cy - h / 2
        r = rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.6)
        lines = s.split("\n")
        cy0 = cy - (len(lines) - 1) * size * 0.65 + size * 0.35
        r += mtext(cx, cy0, lines, size=size, color=color, bold=bold)
        return r

    p = []
    ys = [100, 222, 348]
    titles = ["Умовне інтегрування", "Затиск (clamping)", "Зворотний перерахунок"]

    for band, (yc, ttl) in enumerate(zip(ys, titles)):
        p.append(text(56, yc - 56, ttl, size=13, color=INK, bold=True, anchor="start"))
        xe = 118
        x_int = 248
        x_sum = 428
        x_sat = 556
        x_out = 664
        p.append(text(xe - 24, yc + 4, "e", size=13, color=POS, bold=True))
        p.append(arrow(xe - 12, yc, x_int - 47, yc, color=INK, sw=1.6))
        p.append(box(x_int, yc, 90, 42, "∫  (I)", fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True))
        p.append(arrow(x_int + 45, yc, x_sum - 22, yc, color=INK, sw=1.6))
        p.append(circle(x_sum, yc, 15, fill=FILL, stroke=INK, sw=1.6))
        p.append(text(x_sum, yc + 5, "Σ", size=15, color=INK, bold=True))
        p.append(arrow(x_sum, yc - 42, x_sum, yc - 16, color=NEG, sw=1.4))
        p.append(text(x_sum + 8, yc - 32, "Kp·e", size=10, color=NEG, anchor="start"))
        p.append(arrow(x_sum + 16, yc, x_sat - 45, yc, color=INK, sw=1.6))
        p.append(box(x_sat, yc, 84, 42, "насичення", fill="#fdecea", stroke=POS, color=POS, size=11))
        p.append(arrow(x_sat + 44, yc, x_out - 6, yc, color=INK, sw=1.6))
        p.append(text(x_out + 2, yc + 4, "u", size=13, color=INK, bold=True, anchor="start"))

        if band == 0:
            p.append(line(x_sat, yc + 21, x_sat, yc + 50, color=MUTED, sw=1.2, dash="3 4"))
            p.append(line(x_sat, yc + 50, x_int, yc + 50, color=MUTED, sw=1.4, dash="3 4"))
            p.append(arrow(x_int, yc + 50, x_int, yc + 23, color=MUTED, sw=1.4))
            p.append(text((x_int + x_sat) / 2, yc + 64, "у насиченні — перестати додавати до I", size=10, color=MUTED))
        elif band == 1:
            p.append(text(x_int, yc + 40, "тримати I у [I_min , I_max]", size=10, color=MUTED))
        else:
            p.append(line(x_out, yc, x_out, yc + 52, color=POS, sw=1.4))
            p.append(line(x_out, yc + 52, x_int + 105, yc + 52, color=POS, sw=1.6))
            p.append(box(x_int + 70, yc + 52, 70, 28, "×1/Tt", fill="#fdecea", stroke=POS, color=POS, size=11))
            p.append(arrow(x_int + 35, yc + 52, x_int, yc + 52, color=POS, sw=1.6))
            p.append(arrow(x_int, yc + 52, x_int, yc + 23, color=POS, sw=1.6))
            p.append(text((x_out + x_int) / 2, yc + 68, "(u_sat − u) — назад у інтегратор", size=10, color=POS))

    render(os.path.join(OUT, "antiwindup-schemes.svg"), W, H, *p,
           title="Три прийоми антивіндапу: що саме вони роблять з інтегратором")


# ── 3: tracking-time Tt — швидкість «розкручування» інтеграла ─────────────────
def fig_tracking_time():
    W, H = 720, 320
    ox, oy = 92, 250
    ax_w, ax_h = 556, 200
    p = axes(ox, oy, ax_w, ax_h, ylabel="інтеграл I")

    base = oy
    top = oy - ax_h + 30
    sp = base - top
    I_wind = base - sp * 0.90        # роздутий рівень
    I_final = base - sp * 0.34       # правильний рівень у рівновазі

    t_sat = 0.30
    xs = ox + ax_w * t_sat
    p.append(line(xs, base, xs, top + 4, color=MUTED, sw=1.2, dash="3 4"))
    p.append(text(xs, base + 22, "вихід з насичення", size=11, color=MUTED))
    p.append(line(ox, I_final, ox + ax_w, I_final, color=MUTED, sw=1.2, dash="6 5"))
    p.append(text(ox + ax_w + 2, I_final + 4, "правильний рівень", size=11, color=MUTED, anchor="end"))

    def curve(rate, color, dash=None):
        pts = []
        for i in range(241):
            t = i / 240.0
            if t < t_sat:
                y = base - (base - I_wind) * (t / t_sat)
            else:
                tt = (t - t_sat)
                y = I_final + (I_wind - I_final) * math.exp(-rate * tt)
            pts.append((ox + ax_w * t, y))
        return polyline(pts, color=color, sw=2.6, dash=dash)

    p.append(curve(3.0, POS))                 # малий Tt — швидко розкручує
    p.append(curve(9.0, FIELD))               # добрий Tt
    p.append(curve(28.0, NEG, dash="7 4"))    # великий Tt — майже не розкручує

    p.append(legend_row(ox + 214, top + 6, POS, "малий Tt — швидко розкручує"))
    p.append(legend_row(ox + 214, top + 26, FIELD, "добрий Tt — плавно"))
    p.append(legend_row(ox + 214, top + 46, NEG, "великий Tt — майже не діє", dash="7 4"))

    render(os.path.join(OUT, "tracking-time.svg"), W, H, *p,
           title="Час відстеження Tt: як швидко зворотний перерахунок здуває інтеграл")


# ── 4: правила дискретного інтегрування — прямокутники під кривою помилки ──────
def fig_discrete_rules():
    W, H = 720, 300

    def panel(ox, title, mode):
        oy = 232
        ax_w, ax_h = 168, 148
        q = axes(ox, oy, ax_w, ax_h, xlabel="", ylabel=None)
        base = oy
        top = oy - ax_h + 26
        sp = base - top
        q.append(text(ox + ax_w / 2, top - 12, title, size=12, color=INK, bold=True))

        def err(t):
            return 0.30 + 0.58 * math.exp(-2.2 * t)
        curve = [(ox + ax_w * (i / 120.0), base - sp * err(i / 120.0)) for i in range(121)]

        n = 6
        for k in range(n):
            t0 = k / n
            t1 = (k + 1) / n
            x0 = ox + ax_w * t0
            x1 = ox + ax_w * t1
            if mode == "fwd":
                yy = base - sp * err(t0)
                q.append(rect(x0, yy, x1 - x0, base - yy, fill="#eafaf0", stroke=FIELD, sw=1.0, rx=0))
            elif mode == "bwd":
                yy = base - sp * err(t1)
                q.append(rect(x0, yy, x1 - x0, base - yy, fill="#eafaf0", stroke=FIELD, sw=1.0, rx=0))
            else:
                yl = base - sp * err(t0)
                yr = base - sp * err(t1)
                q.append(polygon([(x0, base), (x0, yl), (x1, yr), (x1, base)],
                                 fill="#eafaf0", stroke=FIELD, sw=1.0))
        q.append(polyline(curve, color=POS, sw=2.4))
        return q

    p = []
    p += panel(70, "прямокутники ліворуч", "fwd")
    p += panel(285, "прямокутники праворуч", "bwd")
    p += panel(500, "трапеції", "trap")

    render(os.path.join(OUT, "discrete-rules.svg"), W, H, *p,
           title="Три способи порахувати ∫e·dt у прошивці: ліва, права, трапеція")


# ── 5: інтеграл на лінійно змінному завданні — лишається стала похибка ────────
def fig_ramp_reference():
    W, H = 720, 320
    ox, oy = 92, 250
    ax_w, ax_h = 556, 200
    p = axes(ox, oy, ax_w, ax_h, ylabel="положення")

    base = oy
    top = oy - ax_h + 30
    sp = base - top

    def ref(t):
        return base - sp * (0.12 + 0.72 * t)
    rpts = [(ox + ax_w * (i / 200.0), ref(i / 200.0)) for i in range(201)]
    p.append(polyline(rpts, color=MUTED, sw=2.0, dash="6 5"))
    p.append(text(ox + ax_w + 2, ref(1.0) - 8, "завдання (рампа)", size=11, color=MUTED, anchor="end"))

    lag = sp * 0.14
    def out(t):
        settle = 1 - math.exp(-6.0 * t)
        return ref(t) + lag * settle
    opts = [(ox + ax_w * (i / 200.0), out(i / 200.0)) for i in range(201)]
    p.append(polyline(opts, color=FIELD, sw=2.8))

    xg = ox + ax_w * 0.82
    yr = ref(0.82)
    yo = out(0.82)
    p.append(line(xg, yr, xg, yo, color=POS, sw=2.0))
    p.append(line(xg - 4, yr, xg + 4, yr, color=POS, sw=2.0))
    p.append(line(xg - 4, yo, xg + 4, yo, color=POS, sw=2.0))
    bo, wo, ho = textbox(xg - 96, (yr + yo) / 2, "стала похибка\nстеження",
                         size=11, color=POS, bold=True, fill="#fdecea", stroke=POS)
    p.append(bo)

    p.append(legend_row(ox + 14, top + 6, MUTED, "завдання весь час росте", dash="6 5"))
    p.append(legend_row(ox + 14, top + 26, FIELD, "вихід ПІ — доганяє, але відстає"))

    render(os.path.join(OUT, "ramp-reference.svg"), W, H, *p,
           title="Межа обіцянки: на рухомій цілі ПІ лишає сталу похибку стеження")


if __name__ == "__main__":
    fig_reset_time()
    fig_antiwindup_schemes()
    fig_tracking_time()
    fig_discrete_rules()
    fig_ramp_reference()
    print("OK: figures written to", OUT)
