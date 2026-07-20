# -*- coding: utf-8 -*-
"""Фігури до статті «Биття». Запуск із теки теми:  python figs.py
Виводить SVG у ./img/. svgkit береться зі scripts/ у корені репо."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def curve(x0, W, fn, color, sw=1.6, n=720, dash=None):
    """Полілінія y=fn(t), t∈[0,1], x=x0+t·W. fn повертає піксельний y."""
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append("%.1f,%.1f" % (x0 + t * W, fn(t)))
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<polyline fill="none" stroke="%s" stroke-width="%.1f"%s points="%s"/>'
            % (color, sw, d, " ".join(pts)))


# ── Фігура 1: сума двох тонів + обвідна ─────────────────────────────────────
def fig_sum_envelope():
    W, H = 880, 520
    x0, wide = 80, 720
    n1, n2 = 20.0, 22.5            # цикли впоперек кадру; Δ = 2.5 биття
    dn = n2 - n1
    # верхня панель: два тони
    yc1, a1 = 120, 40
    wave1 = curve(x0, wide, lambda t: yc1 - a1 * math.sin(2 * math.pi * n1 * t), NEG, 1.5)
    wave2 = curve(x0, wide, lambda t: yc1 - a1 * math.sin(2 * math.pi * n2 * t), POS, 1.5)
    base1 = line(x0, yc1, x0 + wide, yc1, MUTED, 1.0, dash="3,4")
    cap1 = text(x0, 66, "Два тони близьких частот", size=15, color=INK, anchor="start", bold=True)
    leg1 = text(x0 + wide - 40, 66, "f₁", size=14, color=NEG, anchor="end", bold=True)
    leg2 = text(x0 + wide, 66, "f₂", size=14, color=POS, anchor="end", bold=True)

    # нижня панель: сума + обвідна
    yc2, sc = 350, 56
    env_max = sc * 2
    summ = curve(x0, wide, lambda t: yc2 - sc * (math.sin(2 * math.pi * n1 * t) + math.sin(2 * math.pi * n2 * t)), INK, 1.8)
    env_t = curve(x0, wide, lambda t: yc2 - env_max * abs(math.cos(math.pi * dn * t)), FIELD, 1.8, dash="6,5")
    env_b = curve(x0, wide, lambda t: yc2 + env_max * abs(math.cos(math.pi * dn * t)), FIELD, 1.8, dash="6,5")
    base2 = line(x0, yc2, x0 + wide, yc2, MUTED, 1.0, dash="3,4")
    cap2 = text(x0, 210, "Їхня сума — гучність пульсує", size=15, color=INK, anchor="start", bold=True)
    env_leg = text(x0 + wide, 210, "− − обвідна", size=14, color=FIELD, anchor="end", bold=True)

    # період биття T між двома максимумами обвідної (t=0.4 та t=0.8), знизу
    xa, xb = x0 + 0.4 * wide, x0 + 0.8 * wide
    ydim = yc2 + env_max + 30
    dim = (line(xa, ydim, xb, ydim, INK, 1.4)
           + line(xa, ydim - 6, xa, ydim + 6, INK, 1.4)
           + line(xb, ydim - 6, xb, ydim + 6, INK, 1.4))
    gl_a = line(xa, yc2 - env_max, xa, ydim, MUTED, 1.0, dash="2,5")
    gl_b = line(xb, yc2 - env_max, xb, ydim, MUTED, 1.0, dash="2,5")
    dim_lbl = text((xa + xb) / 2, ydim + 24, "період биття  T = 1 / fбиття", size=14, color=INK, bold=True)

    render(os.path.join(IMG, "sum-envelope.svg"), W, H,
           base1, wave1, wave2, cap1, leg1, leg2,
           base2, gl_a, gl_b, env_t, env_b, summ, cap2, env_leg,
           dim, dim_lbl,
           title="Биття: два тони складаються в пульсівну гучність")


# ── Фігура 2: спектр — дві лінії, а не третій тон ────────────────────────────
def fig_spectrum():
    W, H = 780, 380
    ax_y = 300
    x_l, x_r = 90, 700
    axis = arrow(x_l - 10, ax_y, x_r, ax_y, INK, 1.8)
    ax_lbl = text(x_r - 6, ax_y + 26, "частота", size=14, color=INK, anchor="end")
    zero = text(x_l - 10, ax_y + 22, "0", size=13, color=MUTED, anchor="middle")

    # дві близькі спектральні лінії
    xf1, xf2 = 400, 452
    top = 108
    st1 = line(xf1, ax_y, xf1, top, NEG, 3.0)
    st2 = line(xf2, ax_y, xf2, top, POS, 3.0)
    d1 = circle(xf1, top, 5, fill=NEG, stroke=NEG)
    d2 = circle(xf2, top, 5, fill=POS, stroke=POS)
    l1 = text(xf1, ax_y + 24, "f₁", size=15, color=NEG, bold=True)
    l2 = text(xf2, ax_y + 24, "f₂", size=15, color=POS, bold=True)

    # дужка «f_биття = |f1-f2|» між лініями
    by = top - 30
    br = (line(xf1, by, xf2, by, INK, 1.4)
          + line(xf1, by, xf1, by + 8, INK, 1.4)
          + line(xf2, by, xf2, by + 8, INK, 1.4))
    br_lbl = text((xf1 + xf2) / 2, by - 12, "fбиття = |f₁ − f₂|", size=14, color=INK, bold=True)

    # наголос: на позиції Δf (біля нуля) лінії немає
    xno = x_l + 80
    no_stem = line(xno, ax_y, xno, ax_y - 44, POS, 1.4, dash="4,4")
    no_x = text(xno, ax_y - 54, "✗", size=20, color=POS, bold=True)
    box = fitbox(x_l + 30, 150, 210, 56, "тут, на частоті Δf,\nлінії немає", size=13, color=POS, stroke=POS, fill="#fdecea")
    no_arr = arrow(x_l + 120, 206, xno + 2, ax_y - 38, POS, 1.5)

    render(os.path.join(IMG, "spectrum.svg"), W, H,
           axis, ax_lbl, zero, st1, st2, d1, d2, l1, l2,
           br, br_lbl, no_stem, no_x, box, no_arr,
           title="У спектрі суми — дві лінії, а не третій тон")


# ── Фігура 3: розходження фаз (верньє) ───────────────────────────────────────
def fig_phase_slip():
    W, H = 820, 320
    x_l, x_r = 70, 770
    wide = x_r - x_l
    na, nb = 15, 14               # A має на 1 гребінь більше → збіг на краях
    ya1, ya2 = 78, 116            # ряд A (синій)
    yb1, yb2 = 150, 188           # ряд B (червоний)

    # смуги: збіг (ліво/право, зелене) / протифаза (центр, сіре)
    band_w = 150
    bands = (rect(x_l, ya1 - 8, band_w, (yb2 - ya1) + 16, fill="#eafaf1", stroke="none", rx=8)
             + rect(x_r - band_w, ya1 - 8, band_w, (yb2 - ya1) + 16, fill="#eafaf1", stroke="none", rx=8)
             + rect((x_l + x_r) / 2 - band_w / 2, ya1 - 8, band_w, (yb2 - ya1) + 16, fill="#f0f1f3", stroke="none", rx=8))

    ticks = []
    for k in range(na + 1):
        x = x_l + wide * k / na
        ticks.append(line(x, ya1, x, ya2, NEG, 2.4))
    for k in range(nb + 1):
        x = x_l + wide * k / nb
        ticks.append(line(x, yb1, x, yb2, POS, 2.4))
    rowA = text(x_l - 14, (ya1 + ya2) / 2 + 5, "A", size=15, color=NEG, anchor="end", bold=True)
    rowB = text(x_l - 14, (yb1 + yb2) / 2 + 5, "B", size=15, color=POS, anchor="end", bold=True)

    # обвідна гучності під рядами: гучно-тихо-гучно
    ey = 250
    env = curve(x_l, wide, lambda t: ey - 26 * abs(math.cos(math.pi * t)), FIELD, 2.0)
    en_lbl = text(x_l - 14, ey - 6, "гучність", size=12, color=FIELD, anchor="end", bold=True)

    zl = text(x_l + band_w / 2, 300, "збіг → гучно", size=13, color=INK, bold=True)
    zc = text((x_l + x_r) / 2, 300, "протифаза → тихо", size=13, color=INK, bold=True)
    zr = text(x_r - band_w / 2, 300, "збіг → гучно", size=13, color=INK, bold=True)

    render(os.path.join(IMG, "phase-slip.svg"), W, H,
           bands, *ticks, rowA, rowB, env, en_lbl, zl, zc, zr,
           title="Чому виникає биття: гребені то збігаються, то розходяться")


# ── Фігура 4 (історія): як Совер здобув абсолютну частоту з биття ────────────
def fig_measure_logic():
    W, H = 860, 340
    base_y = 250
    # дві органні труби (довша — нижчий тон, коротша — вищий)
    p1x, p2x, pw = 175, 285, 58
    p1top, p2top = 100, 110
    pipe1 = rect(p1x, p1top, pw, base_y - p1top, fill="#eef2fb", stroke=NEG, sw=1.8, rx=3)
    pipe2 = rect(p2x, p2top, pw, base_y - p2top, fill="#fdeeee", stroke=POS, sw=1.8, rx=3)
    baseln = line(160, base_y, 358, base_y, INK, 1.6)
    c1, c2 = p1x + pw / 2, p2x + pw / 2
    t1 = text(c1, base_y + 22, "нижчий тон  f₁", size=13, color=NEG, bold=True)
    t2 = text(c2, base_y + 22, "вищий тон  f₂", size=13, color=POS, bold=True)
    # дужка «разом 6 биттів за секунду» над трубами
    bry = 88
    br = (line(p1x, bry, p2x + pw, bry, INK, 1.4)
          + line(p1x, bry, p1x, bry + 6, INK, 1.4)
          + line(p2x + pw, bry, p2x + pw, bry + 6, INK, 1.4))
    br_lbl = text((p1x + p2x + pw) / 2, bry - 10, "разом: 6 биттів за секунду", size=13, color=INK, bold=True)
    # напрямна стрілка до рівнянь
    guide = arrow(362, 168, 462, 148, MUTED, 1.5)
    # два відомих факти → результат
    eq1 = fitbox(470, 92, 312, 54, "Відомий інтервал (півтон):\nf₂ : f₁ = 16 : 15",
                 size=14, bold=True, color=INK, fill=FILL, stroke=MUTED)
    eq2 = fitbox(470, 162, 312, 54, "Полічені биття (на слух + маятник):\nf₂ − f₁ = 6 за секунду",
                 size=14, bold=True, color=INK, fill=FILL, stroke=MUTED)
    darr = arrow(626, 218, 626, 250, INK, 1.8)
    res = fitbox(470, 254, 312, 52, "f₁ = 90 Гц        f₂ = 96 Гц",
                 size=16, bold=True, color=FIELD, fill="#eafaf1", stroke=FIELD)
    render(os.path.join(IMG, "measure-logic.svg"), W, H,
           br, br_lbl, pipe1, pipe2, baseln, t1, t2, guide, eq1, eq2, darr, res,
           title="Як Совер здобув частоту з биття: відношення + рахунок")


# ── Фігура 5: два способи виділити обвідну ───────────────────────────────────
def fig_env_methods():
    W, H = 900, 540
    x0, wide = 110, 700
    cyc = 24.0
    beats = 2.0
    shape = lambda t: abs(math.cos(math.pi * beats * t))          # 0..1

    def panel(yc, amp, ripple, env_color):
        frags = [line(x0, yc, x0 + wide, yc, MUTED, 1.0, dash="3,4")]
        frags.append(curve(x0, wide,
                     lambda t: yc - amp * shape(t) * math.sin(2 * math.pi * cyc * t), MUTED, 1.0))
        rp = (lambda t: 0.05 * math.sin(2 * math.pi * cyc * t)) if ripple else (lambda t: 0.0)
        frags.append(curve(x0, wide, lambda t: yc - amp * (shape(t) + rp(t)), env_color, 2.4))
        frags.append(curve(x0, wide, lambda t: yc + amp * (shape(t) + rp(t)), env_color, 2.4))
        return frags

    a_ttl = text(x0, 58, "Спосіб 1:  |x| випрямлення + ФНЧ", size=15, color=INK, anchor="start", bold=True)
    a_note = text(x0 + wide, 58, "лишається брижа несучої", size=13, color=POS, anchor="end", bold=True)
    fa = panel(150, 66, True, POS)

    b_ttl = text(x0, 296, "Спосіб 2:  |x + j·H{x}| аналітичний сигнал", size=15, color=INK, anchor="start", bold=True)
    b_note = text(x0 + wide, 296, "точна обвідна, без брижі", size=13, color=FIELD, anchor="end", bold=True)
    fb = panel(388, 66, False, FIELD)

    render(os.path.join(IMG, "env-methods.svg"), W, H,
           a_ttl, a_note, *fa, b_ttl, b_note, *fb,
           title="Два способи відновити обвідну биття")


# ── Фігура 6: конвеєр вимірювання частоти биття ──────────────────────────────
def fig_beat_pipeline():
    W, H = 1000, 340
    bw, bh = 128, 54

    def box(cx, cy, s, stroke=INK, color=INK):
        return fitbox(cx - bw / 2, cy - bh / 2, bw, bh, s, size=13,
                      stroke=stroke, color=color, bold=True)

    y0, y1 = 80, 248
    ymid = (y0 + y1) / 2

    b_tones = box(80, ymid, "два тони\nf₁, f₂", stroke=NEG, color=NEG)
    b_sum = box(250, ymid, "Σ  сума\nx(t)")

    xa = [430, 600, 770]
    a1 = box(xa[0], y0, "|x|\nвипрямлення", stroke=POS, color=POS)
    a2 = box(xa[1], y0, "ФНЧ\n2–3 полюси", stroke=POS, color=POS)
    a3 = box(xa[2], y0, "лічити піки\nабо FFT", stroke=POS, color=POS)

    xb = [430, 620]
    b1 = box(xb[0], y1, "Гільберт\n|x+j·H{x}|", stroke=FIELD, color=FIELD)
    b2 = box(xb[1], y1, "FFT\nобвідної", stroke=FIELD, color=FIELD)

    b_out = box(920, ymid, "f_биття\n= |f₁−f₂|")

    A = [arrow(80 + bw / 2, ymid, 250 - bw / 2, ymid, INK),
         arrow(250 + bw / 2, ymid, xa[0] - bw / 2, y0, POS),
         arrow(250 + bw / 2, ymid, xb[0] - bw / 2, y1, FIELD),
         arrow(xa[0] + bw / 2, y0, xa[1] - bw / 2, y0, POS),
         arrow(xa[1] + bw / 2, y0, xa[2] - bw / 2, y0, POS),
         arrow(xb[0] + bw / 2, y1, xb[1] - bw / 2, y1, FIELD),
         arrow(xa[2] + bw / 2, y0, 920 - bw / 2, ymid, POS),
         arrow(xb[1] + bw / 2, y1, 920 - bw / 2, ymid, FIELD)]

    render(os.path.join(IMG, "beat-pipeline.svg"), W, H,
           b_tones, b_sum, a1, a2, a3, b1, b2, b_out, *A,
           title="Конвеєр: від двох тонів до частоти биття")


# ── Фігура (math): чому |cos| б'ється вдвічі частіше за cos ───────────────────
def fig_cos_abs():
    W, H = 860, 470
    x0, wide = 90, 690
    kcos = 2.0                     # періодів косинуса через кадр → 4 горби гучності

    # верхня панель: знаковий косинус
    yc1, a1 = 120, 52
    base1 = line(x0, yc1, x0 + wide, yc1, MUTED, 1.0, dash="3,4")
    cos1 = curve(x0, wide, lambda t: yc1 - a1 * math.cos(2 * math.pi * kcos * t), NEG, 2.0)
    cap1 = text(x0, 54, "обвідна  cos(2π·(Δf/2)·t)  —  один горб і одна яма", size=14, color=NEG, anchor="start", bold=True)
    yd1 = yc1 + a1 + 26
    xa1, xb1 = x0, x0 + 0.5 * wide
    dim1 = (line(xa1, yd1, xb1, yd1, INK, 1.4)
            + line(xa1, yd1 - 6, xa1, yd1 + 6, INK, 1.4)
            + line(xb1, yd1 - 6, xb1, yd1 + 6, INK, 1.4))
    dim1_lbl = text((xa1 + xb1) / 2, yd1 + 20, "період  2/Δf", size=13, color=INK, bold=True)

    # нота між панелями
    note = text(x0, 238, "від'ємна яма дає такий самий горб гучності, як додатна", size=13, color=MUTED, anchor="start", italic=True)

    # нижня панель: модуль (гучність)
    yc2, a2 = 340, 52
    base2 = line(x0, yc2, x0 + wide, yc2, MUTED, 1.0, dash="3,4")
    absc = curve(x0, wide, lambda t: yc2 - a2 * abs(math.cos(2 * math.pi * kcos * t)), FIELD, 2.3)
    cap2 = text(x0, 274, "гучність  |cos(2π·(Δf/2)·t)|  —  удвічі більше горбів", size=14, color=FIELD, anchor="start", bold=True)
    dots = ""
    for tk in (0.25, 0.5, 0.75):
        dots += circle(x0 + tk * wide, yc2 - a2, 4, fill=FIELD, stroke=FIELD)
    yd2 = yc2 + a2 + 26
    xa2, xb2 = x0 + 0.25 * wide, x0 + 0.5 * wide
    dim2 = (line(xa2, yd2, xb2, yd2, INK, 1.4)
            + line(xa2, yd2 - 6, xa2, yd2 + 6, INK, 1.4)
            + line(xb2, yd2 - 6, xb2, yd2 + 6, INK, 1.4))
    dim2_lbl = text((xa2 + xb2) / 2, yd2 + 20, "період  1/Δf  (удвічі коротший)", size=13, color=INK, bold=True)

    render(os.path.join(IMG, "cos-abs.svg"), W, H,
           base1, cos1, cap1, dim1, dim1_lbl, note,
           base2, absc, cap2, dots, dim2, dim2_lbl,
           title="Чому гучність б'ється вдвічі частіше за косинус-обвідну")


# ── Фігура (math): обвідна як довжина суми фазорів ────────────────────────────
def fig_phasor_envelope():
    W, H = 880, 360
    oy = 195
    LA, LB = 78, 48
    blue, red = NEG, POS

    def cell(ox, kind):
        p = [circle(ox, oy, 3.2, fill=INK, stroke=INK)]
        if kind == "aligned":
            p.append(arrow(ox, oy - 18, ox + LA, oy - 18, blue, 2.4))
            p.append(arrow(ox + LA, oy - 18, ox + LA + LB, oy - 18, red, 2.4))
            p.append(arrow(ox, oy, ox + LA + LB, oy, INK, 2.6))
            p.append(text(ox + LA / 2, oy - 26, "A", size=15, color=blue, bold=True))
            p.append(text(ox + LA + LB / 2, oy - 26, "B", size=15, color=red, bold=True))
            p.append(text(ox + (LA + LB) / 2, oy + 26, "R = A+B", size=14, color=INK, bold=True))
            p.append(text(ox + (LA + LB) / 2, oy + 48, "у фазі → гучно", size=13, color=FIELD, bold=True))
        elif kind == "right":
            p.append(arrow(ox, oy, ox + LA, oy, blue, 2.4))
            p.append(arrow(ox + LA, oy, ox + LA, oy - LB, red, 2.4))
            p.append(arrow(ox, oy, ox + LA, oy - LB, INK, 2.6))
            p.append(text(ox + LA / 2, oy + 20, "A", size=15, color=blue, bold=True))
            p.append(text(ox + LA + 14, oy - LB / 2, "B", size=15, color=red, bold=True, anchor="start"))
            p.append(text(ox + LA / 2 - 22, oy - LB / 2 - 8, "R = √(A²+B²)", size=14, color=INK, bold=True, anchor="end"))
            p.append(text(ox + LA / 2, oy + 48, "під кутом → середина", size=13, color=FIELD, bold=True))
        else:  # opposed
            p.append(arrow(ox, oy - 18, ox + LA, oy - 18, blue, 2.4))
            p.append(arrow(ox + LA, oy - 36, ox + LA - LB, oy - 36, red, 2.4))
            p.append(arrow(ox, oy, ox + (LA - LB), oy, INK, 2.6))
            p.append(text(ox + LA / 2, oy - 26, "A", size=15, color=blue, bold=True))
            p.append(text(ox + LA - LB / 2, oy - 44, "B", size=15, color=red, bold=True))
            p.append(text(ox + (LA - LB) / 2 + 4, oy + 26, "R = |A−B|", size=14, color=INK, bold=True))
            p.append(text(ox + (LA - LB) / 2 + 20, oy + 48, "у протифазі → тихо", size=13, color=FIELD, bold=True))
        return "".join(p)

    c1 = cell(110, "aligned")
    c2 = cell(410, "right")
    c3 = cell(690, "opposed")
    formula = text(W / 2, H - 20,
                   "R = √( A² + B² + 2·A·B·cos θ ),   θ = 2π·Δf·t   (від 0 до π за пів-биття)",
                   size=14, color=INK, bold=True)

    render(os.path.join(IMG, "phasor-envelope.svg"), W, H,
           c1, c2, c3, formula,
           title="Обвідна = довжина суми двох обертових фазорів")


# ── Фігура (math): різні амплітуди — глибина модуляції ───────────────────────
def fig_unequal_amp():
    W, H = 860, 440
    x0, wide = 90, 660
    n1, n2 = 18.0, 21.0            # Δ = 3 биття через кадр
    dn = n2 - n1
    sc = 30

    def panel(yc, A, B, cap, mlabel):
        p = [line(x0, yc, x0 + wide, yc, MUTED, 1.0, dash="3,4")]
        p.append(curve(x0, wide,
                       lambda t: yc - sc * (A * math.sin(2 * math.pi * n1 * t) + B * math.sin(2 * math.pi * n2 * t)),
                       INK, 1.3))
        envf = lambda t: sc * math.sqrt(A * A + B * B + 2 * A * B * math.cos(2 * math.pi * dn * t))
        p.append(curve(x0, wide, lambda t: yc - envf(t), FIELD, 2.0, dash="6,5"))
        p.append(curve(x0, wide, lambda t: yc + envf(t), FIELD, 2.0, dash="6,5"))
        rmax, rmin = sc * (A + B), sc * abs(A - B)
        p.append(line(x0, yc - rmax, x0 + wide, yc - rmax, MUTED, 1.0, dash="2,5"))
        p.append(line(x0, yc - rmin, x0 + wide, yc - rmin, MUTED, 1.0, dash="2,5"))
        p.append(text(x0 + wide + 6, yc - rmax + 4, "A+B", size=12, color=INK, anchor="start", bold=True))
        p.append(text(x0 + wide + 6, yc - rmin + 4, "A−B" if abs(A - B) > 1e-6 else "0", size=12, color=INK, anchor="start", bold=True))
        p.append(text(x0, yc - rmax - 12, cap, size=14, color=INK, anchor="start", bold=True))
        p.append(text(x0 + wide - 4, yc - rmax - 12, mlabel, size=13, color=FIELD, anchor="end", bold=True))
        return "".join(p)

    p1 = panel(150, 1.0, 1.0, "рівні амплітуди  A = B", "m = 1  (занулення)")
    p2 = panel(360, 1.0, 0.4, "нерівні  A > B", "m = B/A = 0.4")

    render(os.path.join(IMG, "unequal-amp.svg"), W, H, p1, p2,
           title="Різні амплітуди: глибина биття  m = B/A")


if __name__ == "__main__":
    fig_sum_envelope()
    fig_spectrum()
    fig_phase_slip()
    fig_measure_logic()
    fig_env_methods()
    fig_beat_pipeline()
    fig_cos_abs()
    fig_phasor_envelope()
    fig_unequal_amp()
    print("OK: 9 SVG у", IMG)
