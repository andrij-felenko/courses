# -*- coding: utf-8 -*-
"""Фігури до теми «Активна підтяжка і струмове джерело».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Вада резистора: струм підтяжки згасає саме вгорі ───────────────────────
# Ідея: показати, що резистор тягне за законом I=(VDD−V)/R — сильно біля нуля,
# кволо біля VDD. А підняти лінію треба саме ВГОРІ. Стовпчики струму на трьох
# рівнях + пряма I(V), що падає до нуля в VDD.
def fig_resistor_flaw():
    W, H = 760, 420
    f = []
    f.append(text(W / 2, 30, "Резистор тягне найслабше саме там, де треба найдужче", size=16, bold=True))

    # осі графіка I(V)
    ox, oy = 110, 340          # початок осей
    ax_w, ax_h = 300, 250
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))          # вісь V
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=2))          # вісь I
    f.append(text(ox + ax_w, oy + 22, "напруга на лінії V", size=11, color=MUTED, anchor="end"))
    f.append(text(ox - 8, oy - ax_h + 4, "струм", size=11, color=MUTED, anchor="end"))
    f.append(text(ox - 8, oy - ax_h + 18, "підтяжки", size=11, color=MUTED, anchor="end"))
    f.append(text(ox, oy + 22, "0", size=10, color=MUTED))
    f.append(text(ox + ax_w, oy + 40, "VDD", size=11, color=POS, anchor="middle", bold=True))

    # пряма I = (VDD - V)/R : від (0, Imax) до (VDD, 0)
    x0, y0 = ox, oy - ax_h * 0.9       # V=0 → максимум струму
    x1, y1 = ox + ax_w, oy             # V=VDD → нуль
    f.append(line(x0, y0, x1, y1, color=NEG, sw=3))
    f.append(text(x0 + 96, y0 + 6, "I = (VDD − V) / R", size=12, color=NEG, bold=True, anchor="start"))

    # три контрольні точки: низ / середина / майже VDD
    pts = [(0.0, "V низько", "сильно тягне"),
           (0.5, "V посередині", "удвічі слабше"),
           (0.85, "V майже VDD", "майже не тягне")]
    for frac, lbl, note in pts:
        px = ox + ax_w * frac
        py = oy - (ax_h * 0.9) * (1 - frac)
        f.append(line(px, oy, px, py, color=MUTED, sw=1, dash="3,3"))
        f.append(circle(px, py, 5, fill=NEG, stroke=NEG, sw=1))

    # праворуч: три стовпчики струму на цих рівнях (наочно спадання)
    bx = 470
    top = 90
    bh_max = 210
    base = top + bh_max
    bw = 56
    gap = 34
    labels = ["внизу\n(V≈0)", "посеред\n(V≈½VDD)", "вгорі\n(V→VDD)"]
    heights = [1.0, 0.5, 0.13]
    cols = [POS, "#e08a2b", MUTED]
    for i, (h_frac, lab, col) in enumerate(zip(heights, labels, cols)):
        x = bx + i * (bw + gap)
        h = bh_max * h_frac
        f.append(rect(x, base - h, bw, h, fill=col, stroke=col, sw=1, rx=3))
        f.append(mtext(x + bw / 2, base + 20, lab, size=10.5, color=INK, lh=1.15))
    f.append(line(bx - 10, base, bx + 3 * (bw + gap) - gap + 10, base, color=INK, sw=2))
    f.append(text(bx + (3 * (bw + gap) - gap) / 2, top - 12, "струм, яким резистор тягне вгору", size=11, color=MUTED))

    bd, bw2, bh2 = textbox(bx + (3 * (bw + gap) - gap) / 2, base + 62,
                           "Підняти лінію в HIGH треба ВГОРІ —\nа саме там резистор майже здався.",
                           size=11.5, pad=10, fill="#fdecea", stroke=POS, color=INK)
    f.append(bd)

    render(os.path.join(IMG, "resistor-flaw.svg"), W, H, *f)


# ── 2. Струмове джерело: пряма рампа замість «повзе й не долазить» ────────────
# Ідея: та сама ємність, той самий середній струм — але резистор дає згасальну
# експоненту (крізь VIH продирається пізно), а джерело — пряму лінію, що
# приходить вчасно. Дві криві V(t) на спільних осях + позначка VIH і Δt.
def fig_current_source_ramp():
    W, H = 760, 400
    f = []
    f.append(text(W / 2, 30, "Струмове джерело жене напругу прямою рампою, а не згасальним «повзе»", size=15, bold=True))

    ox, oy = 90, 330
    ax_w, ax_h = 580, 250
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=2))
    f.append(text(ox + ax_w, oy + 22, "час t", size=11, color=MUTED, anchor="end"))
    f.append(text(ox - 10, oy - ax_h + 6, "V", size=12, color=MUTED, anchor="end"))

    Vdd_y = oy - ax_h * 0.94
    f.append(line(ox, Vdd_y, ox + ax_w, Vdd_y, color=POS, sw=1, dash="5,4"))
    f.append(text(ox + ax_w + 2, Vdd_y + 4, "VDD", size=11, color=POS, anchor="start", bold=True))

    # поріг VIH
    vih_y = oy - ax_h * 0.66
    f.append(line(ox, vih_y, ox + ax_w, vih_y, color=FIELD, sw=1.4, dash="4,4"))
    f.append(text(ox + ax_w + 2, vih_y + 4, "VIH", size=11, color=FIELD, anchor="start", bold=True))
    f.append(text(ox + ax_w + 2, vih_y + 18, "«вже 1»", size=9.5, color=FIELD, anchor="start"))

    N = 90
    # резистор: V = VDD*(1 - e^{-t/τ}) — згасальна експонента
    tau = 0.32
    r_pts = []
    for i in range(N + 1):
        t = i / N
        v = 1 - math.exp(-t / tau)
        x = ox + ax_w * t
        y = oy - ax_h * 0.94 * v
        r_pts.append("%.1f,%.1f" % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(r_pts), NEG))

    # струмове джерело: пряма рампа до VDD за той самий «бюджет» струму,
    # приходить до VDD раніше (constant I заряджає ємність рівномірно)
    t_reach = 0.62
    x_end = ox + ax_w * t_reach
    f.append(line(ox, oy, x_end, Vdd_y, color=POS, sw=3))
    f.append(line(x_end, Vdd_y, ox + ax_w, Vdd_y, color=POS, sw=3))

    # підписи кривих
    f.append(text(ox + ax_w * 0.80, oy - ax_h * 0.94 * (1 - math.exp(-0.80 / tau)) + 20,
                  "резистор: V=VDD(1−e^(−t/τ))", size=11, color=NEG, anchor="middle", bold=True))
    f.append(text(ox + ax_w * 0.30, oy - ax_h * 0.94 * (0.30 / t_reach) - 12,
                  "джерело: пряма рампа", size=11.5, color=POS, anchor="middle", bold=True))

    # де кожен перетнув VIH → різниця в часі
    # резистор перетинає 0.66 при t = -tau*ln(1-0.66)
    tr_r = -tau * math.log(1 - 0.66)
    tr_i = 0.66 * t_reach
    xr = ox + ax_w * tr_r
    xi = ox + ax_w * tr_i
    f.append(circle(xr, vih_y, 5, fill=NEG, stroke=NEG, sw=1))
    f.append(circle(xi, vih_y, 5, fill=POS, stroke=POS, sw=1))
    f.append(line(xi, vih_y, xr, vih_y, color=INK, sw=1.4))
    f.append(text((xi + xr) / 2, vih_y - 8, "виграш у часі", size=10.5, color=INK, anchor="middle"))

    bd, _, _ = textbox(ox + ax_w * 0.5, oy - 26,
                       "Той самий середній струм — але резистор «розмазує» останню чверть,\nа джерело жене рівно й перетинає поріг раніше.",
                       size=11, pad=9, fill="#eaf6ee", stroke=FIELD, color=INK)
    f.append(bd)

    render(os.path.join(IMG, "current-source-ramp.svg"), W, H, *f)


# ── 3. Активна підтяжка-прискорювач: сильний ключ на фронт, тоді назад до кволого
# Ідея: idle тримає слабкий резистор (ощадно). Датчик ловить, що лінію відпустили
# й вона поповзла вгору → на мить умикає сильний транзистор (буст) → долетіли до
# HIGH → вимикає буст, знову кволий резистор. Часова діаграма трьох смуг.
def fig_bus_accelerator():
    W, H = 760, 430
    f = []
    f.append(text(W / 2, 30, "Прискорювач: кволий резистор у спокої, сильний ключ — лише на злеті", size=15, bold=True))

    ox = 70
    ax_w = 610
    lane_x = ox + 150
    lane_w = ax_w - 150

    # три смуги часу
    def lane(y, title, color):
        f.append(text(ox, y + 4, title, size=11.5, color=INK, anchor="start", bold=True))
        f.append(line(lane_x, y, lane_x + lane_w, y, color="#cfd4da", sw=1))
        return y

    # межі етапів по осі часу
    t_release = lane_x + lane_w * 0.22   # лінію відпустили
    t_detect = lane_x + lane_w * 0.30    # датчик помітив злет
    t_high = lane_x + lane_w * 0.52      # долетіли до HIGH
    yb = 90

    # смуга А: напруга на лінії
    yA = yb
    lane(yA, "лінія (V)", INK)
    lo = yA + 34
    hi = yA - 26
    # LOW до release
    f.append(line(lane_x, lo, t_release, lo, color=NEG, sw=3))
    # без буста повзло б повільно (пунктир), з бустом — крутий фронт (суцільний)
    slow_pts = []
    for i in range(31):
        t = i / 30
        x = t_release + (lane_x + lane_w - t_release) * t
        v = 1 - math.exp(-t / 0.30)
        y = lo - (lo - hi) * v
        slow_pts.append("%.1f,%.1f" % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="4,4"/>' % (" ".join(slow_pts), MUTED))
    f.append(line(t_release, lo, t_high, hi, color=POS, sw=3))
    f.append(line(t_high, hi, lane_x + lane_w, hi, color=POS, sw=3))
    f.append(text(lane_x + lane_w * 0.86, hi - 8, "HIGH вчасно", size=10, color=POS, anchor="middle", bold=True))
    f.append(text(lane_x + lane_w * 0.86, lo + 14, "без буста — повзло б", size=9.5, color=MUTED, anchor="middle"))

    # смуга Б: слабкий резистор — завжди ON
    yB = yb + 120
    lane(yB, "кволий резистор", NEG)
    f.append(rect(lane_x, yB - 12, lane_w, 24, fill="#eaf0fd", stroke=NEG, sw=1.4, rx=4))
    f.append(text(lane_x + lane_w / 2, yB + 5, "увімкнений завжди (тримає рівень, ощадно)", size=10.5, color=NEG))

    # смуга В: сильний ключ-буст — лише вікно фронту
    yC = yb + 210
    lane(yC, "сильний ключ (буст)", POS)
    boost_x0 = t_detect
    boost_x1 = t_high
    f.append(rect(lane_x, yC - 12, lane_w, 24, fill="#f7f8fa", stroke="#cfd4da", sw=1, rx=4))
    f.append(rect(boost_x0, yC - 12, boost_x1 - boost_x0, 24, fill="#fdecea", stroke=POS, sw=1.8, rx=4))
    f.append(text((boost_x0 + boost_x1) / 2, yC + 5, "ON: жене вгору", size=10.5, color=POS, bold=True))
    f.append(text(lane_x + (boost_x0 - lane_x) / 2, yC + 5, "OFF", size=10, color=MUTED))
    f.append(text(boost_x1 + (lane_x + lane_w - boost_x1) / 2, yC + 5, "OFF", size=10, color=MUTED))

    # вертикальні маркери подій крізь усі смуги
    for xx, lab, col in [(t_release, "лінію відпущено", NEG),
                         (t_detect, "датчик помітив злет", POS),
                         (t_high, "досягнуто HIGH → буст геть", POS)]:
        f.append(line(xx, yb - 40, xx, yC + 26, color=col, sw=1, dash="3,4"))
        f.append(text(xx, yC + 46, lab, size=9.5, color=col, anchor="middle"))

    render(os.path.join(IMG, "bus-accelerator.svg"), W, H, *f)


# ── 4. Три роди підтяжки вгору: резистор / струмове джерело / ключ-прискорювач ─
# Ідея: одна порівняльна картка — що тягне вгору, як поводиться, ціна.
def fig_three_families():
    W, H = 780, 360
    f = []
    f.append(text(W / 2, 30, "Три способи задати «верх»: пасивний, струмовий, перемикальний", size=15, bold=True))

    cols = [
        ("Резистор\n(пасивна підтяжка)", "#eaf0fd", NEG,
         ["тягне I=(VDD−V)/R", "слабшає вгорі", "простий, дешевий", "компроміс швидкість↔струм"]),
        ("Струмове джерело\n(транзистор-навантаження)", "#eaf6ee", FIELD,
         ["тягне сталим струмом", "пряма рампа до VDD", "фронт не «розмазаний»", "у чипах як активне навантаження"]),
        ("Ключ-прискорювач\n(активна підтяжка)", "#fdecea", POS,
         ["сильний ключ на фронт", "потім віддає кволому", "швидко І ощадно", "окрема мікросхема на шину"]),
    ]
    cw = 236
    gap = 20
    x0 = (W - (3 * cw + 2 * gap)) / 2
    top = 60
    ch = 250
    for i, (title, fill, col, rows) in enumerate(cols):
        x = x0 + i * (cw + gap)
        f.append(rect(x, top, cw, ch, fill=BG, stroke=col, sw=2, rx=10))
        f.append(rect(x, top, cw, 46, fill=fill, stroke=col, sw=0, rx=10))
        f.append(mtext(x + cw / 2, top + 20, title, size=12, color=INK, bold=True, lh=1.15))
        yy = top + 74
        for r in rows:
            f.append(circle(x + 20, yy - 4, 3.5, fill=col, stroke=col, sw=1))
            f.append(text(x + 34, yy, r, size=11, color=INK, anchor="start"))
            yy += 40

    render(os.path.join(IMG, "three-families.svg"), W, H, *f)


# ── 5. Звідки 0.847: відрізок 30%→70% на згасальній експоненті ────────────────
# Ідея (для math-вставки): показати експоненту V=VDD(1−e^(−t/RC)) з двома
# горизонталями 0.3·VDD і 0.7·VDD; вертикалі з точок перетину вниз на вісь часу
# дають t₃₀ і t₇₀; підсвітити відрізок Δt=t₇₀−t₃₀ = RC·ln(7/3) ≈ 0.847·RC.
# Праворуч — чому саме ці рівні: пласкі «хвости» внизу (VIL) і вгорі (біля VDD)
# викидаємо, лишаємо чисту серединну ділянку.
def fig_thirty_seventy():
    W, H = 780, 430
    f = []
    f.append(text(W / 2, 28, "Звідки береться 0.847: відрізок 30%→70% згасальної експоненти", size=15, bold=True))

    ox, oy = 92, 340
    ax_w, ax_h = 470, 260
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=2))
    f.append(text(ox + ax_w, oy + 22, "час t (в одиницях RC)", size=11, color=MUTED, anchor="end"))
    f.append(text(ox - 10, oy - ax_h + 6, "V", size=12, color=MUTED, anchor="end"))

    # рівні VDD, 0.7, 0.3
    def yv(frac):
        return oy - ax_h * 0.92 * frac
    Vdd_y = yv(1.0)
    f.append(line(ox, Vdd_y, ox + ax_w, Vdd_y, color=POS, sw=1, dash="5,4"))
    f.append(text(ox + ax_w + 3, Vdd_y + 4, "VDD", size=11, color=POS, anchor="start", bold=True))

    # згасальна експонента до t=3·RC
    T = 3.0
    N = 120
    pts = []
    for i in range(N + 1):
        t = T * i / N
        v = 1 - math.exp(-t)
        x = ox + ax_w * (t / T)
        y = oy - ax_h * 0.92 * v
        pts.append("%.1f,%.1f" % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(pts), NEG))
    f.append(text(ox + ax_w * 0.62, yv(1 - math.exp(-1.86)) + 22,
                  "V = VDD(1 − e^(−t/RC))", size=11.5, color=NEG, bold=True))

    # горизонталі 0.3 і 0.7, вертикалі в точках перетину
    t30 = -math.log(1 - 0.3)   # 0.3567
    t70 = -math.log(1 - 0.7)   # 1.2040
    for frac, tt, lab, col in [(0.3, t30, "0.3·VDD", "#e08a2b"), (0.7, t70, "0.7·VDD", FIELD)]:
        yy = yv(frac)
        xx = ox + ax_w * (tt / T)
        f.append(line(ox, yy, xx, yy, color=col, sw=1.4, dash="4,3"))
        f.append(line(xx, yy, xx, oy, color=col, sw=1.4, dash="4,3"))
        f.append(circle(xx, yy, 4.5, fill=col, stroke=col, sw=1))
        f.append(text(ox - 6, yy + 4, lab, size=10, color=col, anchor="end", bold=True))
        f.append(text(xx, oy + 16, "t=%.3f·RC" % tt, size=9.5, color=col, anchor="middle"))

    # підсвічений відрізок Δt на осі часу
    x30 = ox + ax_w * (t30 / T)
    x70 = ox + ax_w * (t70 / T)
    f.append(rect(x30, oy - 3, x70 - x30, 6, fill="#ffe9c7", stroke="#e08a2b", sw=1, rx=2))
    f.append(line(x30, oy - 30, x70, oy - 30, color=INK, sw=1.6))
    f.append(line(x30, oy - 34, x30, oy - 26, color=INK, sw=1.6))
    f.append(line(x70, oy - 34, x70, oy - 26, color=INK, sw=1.6))
    f.append(text((x30 + x70) / 2, oy - 38, "Δt = RC·ln(7/3) ≈ 0.847·RC", size=11, color=INK, anchor="middle", bold=True))

    # праворуч: чому саме ці рівні
    bx = ox + ax_w + 66
    bd, bw, bh = textbox(bx + 62, 150,
                         "Чому 30% і 70%:\n\n• нижче 0.3·VDD ще «нуль»\n   (запас від завад унизу)\n• вище 0.7·VDD вже «одиниця»\n   (запас від завад угорі)\n• пласкі хвости кривої —\n   поза вимірюванням\n\nМіряють чистий підйом\nміж порогами, а не\n«розмазані» краї.",
                         size=10.5, pad=11, fill="#f7f8fa", stroke=MUTED, color=INK)
    f.append(bd)

    render(os.path.join(IMG, "thirty-seventy.svg"), W, H, *f)


# ── 6. Однаковий ПІКОВИЙ струм: рампа й експонента стартують з тієї самої крутості
# Ідея (ядро math-вставки, чесна версія): дати обом однаковий СТАРТОВИЙ струм —
# тобто однакову крутість dV/dt при t=0 (у резистора пік саме на старті: VDD/R).
# Джерело тримає цю крутість весь час → пряма рампа. Резистор одразу вичахає, бо
# з ростом V струм (VDD−V)/R падає → крива загинається ВНИЗ від рампи. Тож до
# порога VIH рампа доходить помітно раніше, дарма що стартова сила в них РІВНА.
# Дотична до експоненти при 0 = сама рампа: наочно, що спершу вони йдуть разом.
def fig_where_current_wasted():
    W, H = 780, 430
    f = []
    f.append(text(W / 2, 26, "Однаковий стартовий струм: рампа тримає крутість, експонента одразу вичахає", size=14, bold=True))

    ox, oy = 90, 330
    ax_w, ax_h = 560, 262
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=2))
    f.append(text(ox + ax_w, oy + 22, "час t (в одиницях RC)", size=11, color=MUTED, anchor="end"))
    f.append(text(ox - 10, oy - ax_h + 6, "V", size=12, color=MUTED, anchor="end"))

    def yv(frac):
        return oy - ax_h * 0.92 * frac
    Vdd_y = yv(1.0)
    f.append(line(ox, Vdd_y, ox + ax_w, Vdd_y, color=POS, sw=1, dash="5,4"))
    f.append(text(ox + ax_w + 3, Vdd_y + 4, "VDD", size=11, color=POS, anchor="start", bold=True))

    # поріг VIH = 0.7·VDD
    vih_y = yv(0.7)
    f.append(line(ox, vih_y, ox + ax_w, vih_y, color=FIELD, sw=1.4, dash="4,4"))
    f.append(text(ox + ax_w + 3, vih_y + 4, "VIH", size=11, color=FIELD, anchor="start", bold=True))
    f.append(text(ox + ax_w + 3, vih_y + 18, "0.7·VDD", size=9, color=FIELD, anchor="start"))

    T = 2.2
    N = 140
    # резистор: V=VDD(1-e^{-t}); стартова крутість dV/dt|0 = VDD (за RC=1)
    r_pts = []
    for i in range(N + 1):
        t = T * i / N
        v = 1 - math.exp(-t)
        r_pts.append("%.1f,%.1f" % (ox + ax_w * (t / T), oy - ax_h * 0.92 * v))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(r_pts), NEG))

    # рампа = дотична до експоненти при t=0: V=VDD·t (та сама стартова крутість),
    # обрізана на VDD. Досягає VDD при t=RC (тобто t=1 в наших одиницях).
    x_reach = ox + ax_w * (1.0 / T)
    f.append(line(ox, oy, x_reach, Vdd_y, color=POS, sw=3))
    f.append(line(x_reach, Vdd_y, ox + ax_w, Vdd_y, color=POS, sw=3))

    # спільна стартова крутість — маленька позначка «однаковий старт»
    f.append(circle(ox, oy, 4, fill=INK, stroke=INK, sw=1))
    f.append(text(ox + 150, oy - 8, "однаковий стартовий струм (та сама крутість)", size=10, color=MUTED, anchor="middle"))

    # підписи кривих
    f.append(text(ox + ax_w * 0.66, yv(1 - math.exp(-1.45)) + 20, "резистор: V=VDD(1−e^(−t/RC))", size=11, color=NEG, anchor="middle", bold=True))
    f.append(text(ox + ax_w * (0.42 / T), oy - ax_h * 0.92 * 0.42 - 12, "джерело: пряма рампа", size=11, color=POS, anchor="middle", bold=True))

    # точки перетину VIH: рампа при t=0.7, резистор при t=1.204 → виграш
    t_ramp = 0.7
    t_res = -math.log(1 - 0.7)   # 1.204
    xr = ox + ax_w * (t_ramp / T)
    xe = ox + ax_w * (t_res / T)
    f.append(circle(xr, vih_y, 5, fill=POS, stroke=POS, sw=1))
    f.append(circle(xe, vih_y, 5, fill=NEG, stroke=NEG, sw=1))
    f.append(line(xr, vih_y, xe, vih_y, color=INK, sw=1.6))
    f.append(line(xr, vih_y, xr, oy, color=POS, sw=1, dash="3,3"))
    f.append(line(xe, vih_y, xe, oy, color=NEG, sw=1, dash="3,3"))
    f.append(text(xr, oy + 15, "0.70·RC", size=9, color=POS, anchor="middle"))
    f.append(text(xe, oy + 15, "1.20·RC", size=9, color=NEG, anchor="middle"))
    f.append(text((xr + xe) / 2, vih_y - 9, "рампа тут раніше на 0.50·RC", size=10, color=INK, anchor="middle", bold=True))

    # рамка-висновок
    bd, _, _ = textbox(ox + ax_w * 0.5, oy + 62,
                       "Стартова сила РІВНА — але резистор одразу починає вичахати (струм (VDD−V)/R\nпадає з ростом V), тож крива загинається вниз. Джерело тримає ту крутість весь час.\nПік резистора змарнований унизу, де V мала й поріг далеко; до VIH рампа приходить раніше.",
                       size=10.5, pad=10, fill="#eef1f6", stroke=INK, color=INK)
    f.append(bd)

    render(os.path.join(IMG, "where-current-wasted.svg"), W, H, *f)


if __name__ == "__main__":
    fig_resistor_flaw()
    fig_current_source_ramp()
    fig_bus_accelerator()
    fig_three_families()
    fig_thirty_seventy()
    fig_where_current_wasted()
    print("OK: figures written to", IMG)
