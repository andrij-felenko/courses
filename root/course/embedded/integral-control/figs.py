# -*- coding: utf-8 -*-
"""Фігури теми «І-складова». Запуск: python figs.py
svgkit імпортуємо зі scripts/ (не переписуємо). Імена файлів — за slug, без номерів."""
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
    """Осі: час → праворуч, величина ↑."""
    q = [line(ox, oy, ox, oy - ax_h, color=INK, sw=1.6),
         arrow(ox, oy - ax_h + 14, ox, oy - ax_h, color=INK, sw=1.6),
         line(ox, oy, ox + ax_w, oy, color=INK, sw=1.6),
         arrow(ox + ax_w - 14, oy, ox + ax_w, oy, color=INK, sw=1.6)]
    if xlabel:
        q.append(text(ox + ax_w, oy + 18, xlabel, size=12, color=MUTED, italic=True, anchor="end"))
    if ylabel:
        q.append(text(ox - 4, oy - ax_h + 4, ylabel, size=12, color=MUTED, anchor="end"))
    return q


def legend_row(x, y, color, label, sw=2.6):
    return (line(x, y, x + 26, y, color=color, sw=sw) +
            text(x + 32, y + 4, label, size=11, color=color, anchor="start", bold=True))


# ── 1: інтеграл = площа під кривою помилки ────────────────────────────────────
def fig_integral_area():
    W, H = 720, 300
    ox, oy = 92, 238
    ax_w, ax_h = 556, 192
    p = axes(ox, oy, ax_w, ax_h, ylabel="помилка e")

    def err(t):                       # спадає до малого СТІЙКОГО залишку (не нуль)
        return 0.18 + 0.82 * math.exp(-3.4 * t)
    top = oy - ax_h + 26
    base = oy
    span = base - top
    curve = [(ox + ax_w * (i / 200.0), base - span * err(i / 200.0)) for i in range(201)]

    area = list(curve) + [(curve[-1][0], base), (ox, base)]
    p.append(polygon(area, fill="#fbe4e1"))
    p.append(polyline(curve, color=POS, sw=2.8))

    p.append(text(ox + ax_w * 0.28, base - span * 0.28, "∫ e dt", size=18, color=POS, bold=True))
    p.append(text(ox + ax_w * 0.28, base - span * 0.28 + 20, "накопичена площа", size=11, color=MUTED))

    tx = ox + ax_w * 0.88
    ty = base - span * err(0.88)
    b, bw, bh = textbox(ox + ax_w * 0.71, top + 18,
                        "навіть малий стійкий залишок\nусе накопичується",
                        size=11, color=INK, fill="#f4f6f8", stroke=MUTED)
    p.append(b)
    p.append(arrow(ox + ax_w * 0.71, top + 18 + bh / 2 - 2, tx - 4, ty - 6, color=MUTED, sw=1.4))

    render(os.path.join(OUT, "integral-area.svg"), W, H, *p,
           title="Що накопичує інтеграл: площу під кривою помилки")


# ── 2: P лишає зсув, P+I доводить вихід точно до завдання ──────────────────────
def fig_offset_removed():
    W, H = 720, 320
    ox, oy = 92, 256
    ax_w, ax_h = 556, 210
    p = axes(ox, oy, ax_w, ax_h, ylabel="вихід")

    base = oy
    top = oy - ax_h + 28
    sp = base - top
    sp_lvl = base - sp * 0.82          # завдання (setpoint)
    off_lvl = base - sp * 0.62         # де застигає чистий P (сталий зсув)

    # завдання
    p.append(line(ox, sp_lvl, ox + ax_w, sp_lvl, color=MUTED, sw=1.5, dash="6 5"))
    p.append(text(ox + ax_w + 2, sp_lvl + 4, "завдання", size=11, color=MUTED, anchor="end"))

    def approach(t, target_lvl, k):    # експоненційний підхід знизу до target_lvl
        return base - (base - target_lvl) * (1 - math.exp(-k * t))

    # лише P — застигає на off_lvl
    pcurve = [(ox + ax_w * (i / 200.0), approach(i / 200.0, off_lvl, 5.2)) for i in range(201)]
    p.append(polyline(pcurve, color=NEG, sw=2.6))

    # P+I — спершу йде як P, тоді інтеграл доводить до завдання (повільніший доїзд)
    picurve = []
    for i in range(201):
        t = i / 200.0
        y_fast = approach(t, off_lvl, 5.2)              # швидка P-частина
        extra = (off_lvl - sp_lvl) * (1 - math.exp(-1.7 * t))  # повільний доїзд інтеграла
        picurve.append((ox + ax_w * t, y_fast + extra))
    p.append(polyline(picurve, color=FIELD, sw=2.8))

    # дужка сталого зсуву (між P і завданням) справа
    xb = ox + ax_w * 0.93
    p.append(line(xb, sp_lvl, xb, off_lvl, color=POS, sw=2.0))
    p.append(line(xb - 4, sp_lvl, xb + 4, sp_lvl, color=POS, sw=2.0))
    p.append(line(xb - 4, off_lvl, xb + 4, off_lvl, color=POS, sw=2.0))
    bo, wo, ho = textbox(xb - 78, (sp_lvl + off_lvl) / 2, "сталий\nзсув",
                         size=11, color=POS, bold=True, fill="#fdecea", stroke=POS)
    p.append(bo)

    p.append(legend_row(ox + 14, top + 8, NEG, "лише P — застигає нижче"))
    p.append(legend_row(ox + 14, top + 28, FIELD, "P + I — сідає точно на завдання"))

    render(os.path.join(OUT, "offset-removed.svg"), W, H, *p,
           title="Інтеграл прибирає зсув: P застигає нижче, P+I доходить точно")


# ── 3: інтеграл росте, поки є помилка, і застигає, коли вона зникає ────────────
def fig_accumulator():
    W, H = 720, 320
    ox, oy = 92, 256
    ax_w, ax_h = 556, 210
    p = axes(ox, oy, ax_w, ax_h)

    base = oy
    top = oy - ax_h + 30
    sp = base - top

    # помилка: спадає до нуля до моменту t≈0.62, далі нуль
    t_zero = 0.62
    def err(t):
        if t >= t_zero:
            return 0.0
        return 0.9 * (1 - t / t_zero) ** 1.6
    ecurve = [(ox + ax_w * (i / 240.0), base - sp * err(i / 240.0)) for i in range(241)]
    p.append(polyline(ecurve, color=POS, sw=2.6))

    # накопичувач: інтеграл помилки — росте, поки err>0, тоді застигає
    acc = []
    s = 0.0
    n = 240
    vals = []
    for i in range(n + 1):
        t = i / n
        if i > 0:
            s += err(t) * (1.0 / n)
        vals.append(s)
    mx = max(vals)
    for i in range(n + 1):
        t = i / n
        y = base - sp * 0.92 * (vals[i] / mx)
        acc.append((ox + ax_w * t, y))
    p.append(polyline(acc, color=FIELD, sw=2.8))

    # вертикаль у момент e=0
    xz = ox + ax_w * t_zero
    p.append(line(xz, base, xz, top + 6, color=MUTED, sw=1.2, dash="3 4"))
    p.append(text(xz, base + 30, "e = 0 → інтеграл застигає", size=11, color=MUTED))

    p.append(legend_row(ox + 14, top + 6, POS, "помилка e — спадає до нуля"))
    p.append(legend_row(ox + 14, top + 26, FIELD, "накопичувач I — росте, тоді застигає"))

    render(os.path.join(OUT, "accumulator.svg"), W, H, *p,
           title="Робота інтеграла в часі: росте, поки є помилка")


# ── 4: вплив Ki — малий / добрий / завеликий ──────────────────────────────────
def fig_ki_effect():
    W, H = 720, 320
    ox, oy = 92, 256
    ax_w, ax_h = 556, 210
    p = axes(ox, oy, ax_w, ax_h, ylabel="вихід")

    base = oy
    top = oy - ax_h + 30
    sp = base - top
    sp_lvl = base - sp * 0.70

    p.append(line(ox, sp_lvl, ox + ax_w, sp_lvl, color=MUTED, sw=1.5, dash="6 5"))
    p.append(text(ox + ax_w + 2, sp_lvl + 4, "завдання", size=11, color=MUTED, anchor="end"))

    A = base - sp_lvl                  # висота завдання над базою

    def resp(t, k_speed, damp, osc):
        """Підхід до завдання з можливим перельотом: 1 - e^{-damp t} (1 + ... cos)."""
        if osc <= 0:
            return base - A * (1 - math.exp(-k_speed * t))
        w = osc
        env = math.exp(-damp * t)
        return base - A * (1 - env * math.cos(w * t))

    small = [(ox + ax_w * (i / 240.0), base - A * (1 - math.exp(-1.5 * (i / 240.0)))) for i in range(241)]
    good = [(ox + ax_w * (i / 240.0), base - A * (1 - math.exp(-4.2 * (i / 240.0)))) for i in range(241)]
    big = []
    for i in range(241):
        t = i / 240.0 * 4.2
        tt = i / 240.0
        env = math.exp(-1.1 * t)
        big.append((ox + ax_w * tt, base - A * (1 - env * math.cos(2.6 * t))))

    p.append(polyline(small, color=FIELD, sw=2.6))
    p.append(polyline(good, color=NEG, sw=2.6))
    p.append(polyline(big, color=POS, sw=2.6))

    p.append(legend_row(ox + 14, top + 6, FIELD, "малий Ki — повільно й м'яко"))
    p.append(legend_row(ox + 14, top + 26, NEG, "добрий Ki — швидко, без зайвого"))
    p.append(legend_row(ox + 14, top + 46, POS, "завеликий Ki — переліт і коливання"))

    render(os.path.join(OUT, "ki-effect.svg"), W, H, *p,
           title="Вплив Ki: повільно · добре · переповнення й коливання")


# ── 5: windup — за насичення інтеграл накручується й дає величезний переліт ────
def fig_windup():
    W, H = 720, 360
    ox = 92
    ax_w = 556

    # дві панелі: вгорі вихід+завдання, внизу інтеграл+насичення
    base1, ah1 = 168, 122
    base2, ah2 = 326, 116
    p = []
    p += axes(ox, base1, ax_w, ah1, xlabel="", ylabel="вихід")
    p += axes(ox, base2, ax_w, ah2, ylabel="інтеграл")

    sp1 = base1 - ah1 + 24
    A1 = base1 - sp1
    sp_lvl = base1 - A1 * 0.62
    p.append(line(ox, sp_lvl, ox + ax_w, sp_lvl, color=MUTED, sw=1.5, dash="6 5"))
    p.append(text(ox + ax_w + 2, sp_lvl + 4, "завдання", size=11, color=MUTED, anchor="end"))

    # вихід: довго в насиченні (повзе), тоді стрімко проскакує далеко ЗА завдання, потім гойдається
    t_sat = 0.46                       # доки виходимо з насичення
    out = []
    for i in range(241):
        t = i / 240.0
        if t < t_sat:
            y = base1 - (base1 - sp_lvl) * 0.78 * (t / t_sat)   # повільний підйом у насиченні
        else:
            tt = (t - t_sat) / (1 - t_sat)
            # вистрілив над завданням і загойдався (переліт угору = менший y)
            y = sp_lvl - (A1 * 0.42) * (math.exp(-2.4 * tt) * math.cos(3.2 * tt))
        out.append((ox + ax_w * t, y))
    p.append(polyline(out, color=POS, sw=2.8))

    # нижня панель: інтеграл накручується (затінено), тоді розкручується
    sp2 = base2 - ah2 + 22
    A2 = base2 - sp2
    integ = []
    for i in range(241):
        t = i / 240.0
        if t < t_sat:
            v = (t / t_sat) ** 0.9          # накручується до максимуму
        else:
            tt = (t - t_sat) / (1 - t_sat)
            v = 1.0 - 0.85 * (1 - math.exp(-2.2 * tt))   # повільно розкручується
        integ.append((ox + ax_w * t, base2 - A2 * 0.92 * v))
    fill_area = list(integ) + [(integ[-1][0], base2), (ox, base2)]
    p.append(polygon(fill_area, fill="#fbe4e1"))
    p.append(polyline(integ, color=POS, sw=2.6))

    # зона насичення
    xs = ox + ax_w * t_sat
    for by in (base1, base2):
        ah = ah1 if by == base1 else ah2
        p.append(line(xs, by, xs, by - ah + 6, color=MUTED, sw=1.2, dash="3 4"))
    p.append(text(ox + ax_w * t_sat / 2, base2 + 30, "виконавчий орган у насиченні", size=11, color=MUTED))
    p.append(text(xs + (ax_w - ax_w * t_sat) / 2, base2 + 30, "вихід з насичення", size=11, color=MUTED))

    bb, wbb, hbb = textbox(ox + ax_w * 0.74, base1 - A1 * 0.78,
                           "роздутий інтеграл\nжене вихід ЗА ціль", size=11,
                           color=POS, bold=True, fill="#fdecea", stroke=POS)
    p.append(bb)

    render(os.path.join(OUT, "windup.svg"), W, H, *p,
           title="Накопичувальне насичення (windup): інтеграл накрутився → дикий переліт")


# ── 6: антивіндап спиняє накручування — переліт зникає ────────────────────────
def fig_anti_windup():
    W, H = 720, 320
    ox, oy = 92, 256
    ax_w, ax_h = 556, 210
    p = axes(ox, oy, ax_w, ax_h, ylabel="вихід")

    base = oy
    top = oy - ax_h + 30
    sp = base - top
    sp_lvl = base - sp * 0.66
    A = base - sp_lvl

    p.append(line(ox, sp_lvl, ox + ax_w, sp_lvl, color=MUTED, sw=1.5, dash="6 5"))
    p.append(text(ox + ax_w + 2, sp_lvl + 4, "завдання", size=11, color=MUTED, anchor="end"))

    t_sat = 0.42
    # без захисту — великий переліт і гойдання
    no = []
    for i in range(241):
        t = i / 240.0
        if t < t_sat:
            y = base - A * 0.78 * (t / t_sat)
        else:
            tt = (t - t_sat) / (1 - t_sat)
            y = sp_lvl - (A * 0.40) * (math.exp(-2.3 * tt) * math.cos(3.1 * tt))
        no.append((ox + ax_w * t, y))
    p.append(polyline(no, color=POS, sw=2.6))

    # з антивіндапом — плавний експоненційний доїзд від рівня насичення, без перельоту
    y_sat = base - A * 0.78                     # рівень, з якого виходимо з насичення
    yes = []
    for i in range(241):
        t = i / 240.0
        if t < t_sat:
            y = base - A * 0.78 * (t / t_sat)
        else:
            tt = (t - t_sat) / (1 - t_sat)
            y = sp_lvl - (sp_lvl - y_sat) * math.exp(-3.2 * tt)
        yes.append((ox + ax_w * t, y))
    p.append(polyline(yes, color=FIELD, sw=2.8))

    xs = ox + ax_w * t_sat
    p.append(line(xs, base, xs, top + 6, color=MUTED, sw=1.2, dash="3 4"))
    p.append(text(xs, base + 30, "вихід з насичення", size=11, color=MUTED))

    p.append(legend_row(ox + 14, top + 6, POS, "без захисту — величезний переліт"))
    p.append(legend_row(ox + 14, top + 26, FIELD, "з антивіндапом — чисто, без перельоту"))

    render(os.path.join(OUT, "anti-windup.svg"), W, H, *p,
           title="Антивіндап: накручування спинене — на завдання виходимо чисто")


# ── 7 (hist): часова смуга — від «скидача» до антивіндапу ─────────────────────
def fig_reset_timeline():
    """Історична смуга: народження інтегральної дії, назва «reset», антивіндап."""
    W, H = 760, 340
    ox = 70
    axw = W - 2 * ox
    y0 = 150                              # рівень осі часу

    # роки → x лінійно від 1918 до 1988
    t_lo, t_hi = 1918, 1988
    def X(year):
        return ox + axw * (year - t_lo) / (t_hi - t_lo)

    p = [line(ox, y0, ox + axw, y0, color=INK, sw=2.0),
         arrow(ox + axw - 12, y0, ox + axw, y0, color=INK, sw=2.0)]

    # десятилітні позначки
    for yr in range(1920, 1990, 10):
        x = X(yr)
        p.append(line(x, y0 - 5, x, y0 + 5, color=MUTED, sw=1.4))
        p.append(text(x, y0 + 22, str(yr), size=11, color=MUTED))

    # віхи: (рік, підпис, вгору?, колір)
    marks = [
        (1922, ["Мінорський", "інтеграл у стерні", "USS New Mexico"], True,  NEG),
        (1931, ["Мейсон · Stabilog", "«automatic reset»"],            False, POS),
        (1967, ["Фертик і Росс", "back-calculation"],                 True,  FIELD),
        (1970, ["«reset» → ", "«integral»"],                          False, MUTED),
        (1984, ["Åström &", "Wittenmark", "спостерігач"],             True,  NEG),
    ]
    for yr, lines, up, col in marks:
        x = X(yr)
        p.append(circle(x, y0, 5.5, fill=col, stroke=col, sw=1.5))
        if up:
            ytop = y0 - 30
            p.append(line(x, y0 - 6, x, ytop, color=col, sw=1.4, dash="2 3"))
            b, bw, bh = textbox(x, ytop - 6 - 8 * len(lines), "\n".join(lines),
                                size=11, color=col, bold=True, fill=BG, stroke=col)
            p.append(b)
        else:
            ybot = y0 + 44
            p.append(line(x, y0 + 6, x, ybot, color=col, sw=1.4, dash="2 3"))
            b, bw, bh = textbox(x, ybot + 8 * len(lines), "\n".join(lines),
                                size=11, color=col, bold=True, fill=BG, stroke=col)
            p.append(b)

    render(os.path.join(OUT, "reset-timeline.svg"), W, H, *p,
           title="Від «скидача» до антивіндапу: як дозрівала інтегральна дія")


if __name__ == "__main__":
    fig_integral_area()
    fig_offset_removed()
    fig_accumulator()
    fig_ki_effect()
    fig_windup()
    fig_anti_windup()
    fig_reset_timeline()
    print("OK: figures written to", OUT)
