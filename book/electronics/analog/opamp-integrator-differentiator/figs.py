# -*- coding: utf-8 -*-
"""Фігури до теми «Інтегратор і диференціатор на ОП» (аналогова, кутом теорії кіл).
Чотири фігури:
  integrator-circuit.svg  — інвертуючий ОП-інтегратор: R на вході, C у зворотному зв'язку,
                            віртуальна земля на «−»; струм входу йде лише в C
  ramp-compare.svg        — прямокутник на вході: пасивний RC дає прогнуту (діряву) криву,
                            ОП-інтегратор — рівну пряму до самого насичення
  differentiator-circuit.svg — ОП-диференціатор: C на вході, R у ЗЗ; +послідовний Rs і
                            паралельний Cf, що приборкують шум і дзвін
  practical-integrator.svg — практичний інтегратор: Rf || C обмежує підсилення на сталому,
                            щоб дрейф зсуву не загнав вихід у стелю
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def opamp(ox, oy, w=86, h=72):
    """Трикутник ОП вершиною праворуч. Повертає (svg, in_minus, in_plus, out_pt)."""
    out = []
    out.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.8"/>'
               % (ox, oy, ox, oy + h, ox + w, oy + h / 2, BG, LINE))
    in_minus = (ox, oy + h * 0.28)
    in_plus = (ox, oy + h * 0.72)
    out_pt = (ox + w, oy + h / 2)
    out.append(text(ox + 12, in_minus[1] + 5, "−", size=16, bold=True, color=NEG))
    out.append(text(ox + 12, in_plus[1] + 5, "+", size=16, bold=True, color=POS))
    return "".join(out), in_minus, in_plus, out_pt


def _cap_h(cx, cy, gap=8, plate=22, label=None):
    """Конденсатор горизонтальний (пластини вертикальні), центр (cx,cy)."""
    out = []
    out.append(line(cx - gap / 2, cy - plate / 2, cx - gap / 2, cy + plate / 2, color=LINE, sw=2.6))
    out.append(line(cx + gap / 2, cy - plate / 2, cx + gap / 2, cy + plate / 2, color=LINE, sw=2.6))
    return "".join(out)


def _res_h(x, y, w=46, h=15):
    """Резистор-прямокутник горизонтальний; повертає (svg, лів_x, прав_x)."""
    return rect(x, y - h / 2, w, h, fill=BG, stroke=LINE, sw=1.6, rx=2), x, x + w


def _gnd(x, y):
    out = []
    for i, ww in enumerate((16, 10, 4)):
        out.append(line(x - ww, y + i * 5, x + ww, y + i * 5, color=LINE, sw=1.6))
    return "".join(out)


# ───────────────────────────────────────────────────────────────────────────
def integrator_circuit():
    """Інвертуючий ОП-інтегратор: R вхід → вузол «−» (віртуальна земля) → C у ЗЗ → вихід."""
    W, H = 720, 380
    p = []
    ax, ay = 350, 150           # ОП
    amp, m, pl, o = opamp(ax, ay)
    p.append(amp)

    # вхід ліворуч -> R -> вузол «−»
    inx = 70
    p.append(circle(inx, m[1], 3, fill=BG, stroke=LINE, sw=1.6))
    p.append(text(inx, m[1] - 12, "вхід", size=12, color=MUTED))
    rsvg, rl, rr = _res_h(inx + 30, m[1])
    p.append(line(inx, m[1], inx + 30, m[1], color=LINE, sw=1.6))
    p.append(rsvg)
    p.append(text(inx + 53, m[1] - 12, "R", size=14, bold=True))
    p.append(line(rr, m[1], m[0], m[1], color=LINE, sw=1.6))
    p.append(circle(m[0], m[1], 2.6, fill=INK, stroke=INK))     # вузол «−»

    # «+» на землю
    p.append(line(pl[0], pl[1], pl[0] - 26, pl[1], color=LINE, sw=1.6))
    p.append(line(pl[0] - 26, pl[1], pl[0] - 26, pl[1] + 22, color=LINE, sw=1.6))
    p.append(_gnd(pl[0] - 26, pl[1] + 22))

    # зворотний зв'язок: від виходу через C назад у вузол «−»
    fbY = ay - 56
    p.append(line(o[0], o[1], o[0] + 24, o[1], color=LINE, sw=1.6))   # вихід трохи праворуч
    outx = o[0] + 24
    p.append(circle(outx, o[1], 2.6, fill=INK, stroke=INK))
    p.append(line(outx, o[1], outx, fbY, color=LINE, sw=1.6))
    p.append(line(m[0], m[1], m[0], fbY, color=LINE, sw=1.6))
    # C на верхній гілці
    midfb = (m[0] + outx) / 2
    p.append(line(m[0], fbY, midfb - 6, fbY, color=LINE, sw=1.6))
    p.append(line(midfb - 6, fbY - 11, midfb - 6, fbY + 11, color=LINE, sw=2.6))
    p.append(line(midfb + 6, fbY - 11, midfb + 6, fbY + 11, color=LINE, sw=2.6))
    p.append(line(midfb + 6, fbY, outx, fbY, color=LINE, sw=1.6))
    p.append(text(midfb, fbY - 16, "C", size=14, bold=True))

    # вихід далі праворуч
    p.append(line(outx, o[1], outx + 60, o[1], color=LINE, sw=1.6))
    p.append(circle(outx + 60, o[1], 3, fill=BG, stroke=LINE, sw=1.6))
    p.append(text(outx + 70, o[1] + 4, "вихід", size=12, color=MUTED, anchor="start"))

    # позначки струмів
    p.append(text(inx + 53, m[1] + 22, "i = V_вх/R", size=12, color=NEG))
    p.append(text(midfb, fbY + 22, "той самий i → в C", size=12, color=FIELD))
    p.append(text(m[0] - 4, m[1] + 26, "0 В (вірт. земля)", size=11, color=MUTED, anchor="middle"))

    b, _, _ = textbox(W / 2, 330,
                      "Резистор перетворює вхід на струм i = V_вх/R; у входи ОП струм не тече, тож увесь i\n"
                      "ллється в C. Вузол «−» тримається на 0 В — струм не залежить від заряду: чесний інтеграл.",
                      size=12, fill="#eaf0fd", stroke=NEG)
    p.append(b)
    render(os.path.join(OUT, 'integrator-circuit.svg'), W, H, *p,
           title="ОП-інтегратор: R на вході, C у зворотному зв'язку, віртуальна земля")


# ───────────────────────────────────────────────────────────────────────────
def ramp_compare():
    """Прямокутник на вході; пасивний RC прогинається (дірявий), ОП-інтегратор — пряма до насичення."""
    W, H = 720, 380
    p = []
    ox, oy = 80, 64
    plot_w, plot_h = 560, 96

    # вхід — прямокутник (півперіоду високий)
    midy_in = oy + plot_h / 2
    p.append(line(ox, midy_in, ox + plot_w, midy_in, color=MUTED, sw=1))
    p.append(text(ox - 10, oy + 4, "вхід", size=12, bold=True, anchor="end", color=INK))
    hi = midy_in - 32
    seq = [(0, midy_in), (0, hi), (plot_w, hi)]
    d = "M%.1f %.1f" % (ox + seq[0][0], seq[0][1])
    for x, y in seq[1:]:
        d += " L%.1f %.1f" % (ox + x, y)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d, INK))
    p.append(text(ox + plot_w * 0.5, hi - 8, "стале значення", size=11, color=MUTED))

    # вихід
    oy2 = oy + plot_h + 56
    base = oy2 + plot_h - 6
    p.append(line(ox, base, ox + plot_w, base, color=MUTED, sw=1))
    p.append(text(ox - 10, oy2 + 4, "вихід", size=12, bold=True, anchor="end", color=INK))

    # ОП-інтегратор: ідеальна пряма (вниз, бо інвертує) до насичення
    sat = oy2 + 6                     # рівень стелі (насичення)
    p.append(line(ox, base, ox + plot_w * 0.74, sat, color=NEG, sw=2.6))
    p.append(line(ox + plot_w * 0.74, sat, ox + plot_w, sat, color=NEG, sw=2.6))
    p.append(line(ox, sat, ox + plot_w, sat, color=NEG, sw=1, dash="3 4"))
    p.append(text(ox + plot_w + 6, sat + 4, "стеля", size=11, color=NEG, anchor="start"))
    p.append(text(ox + plot_w * 0.30, (base + sat) / 2 - 22, "ОП: рівна пряма", size=12, bold=True, color=NEG))
    p.append(text(ox + plot_w * 0.30, (base + sat) / 2 - 6, "(чесний інтеграл)", size=11, color=NEG))

    # пасивний RC: експонента, що загинається (дірявий) — менший розмах
    pts = []
    A = base - (oy2 + 26)
    for k in range(0, 200):
        xx = ox + k * (plot_w / 199.0)
        t = k / 199.0
        yy = base - A * (1 - math.exp(-2.6 * t))   # експонента-насичення
        pts.append((xx, yy))
    d2 = "M%.1f %.1f" % pts[0]
    for x, y in pts[1:]:
        d2 += " L%.1f %.1f" % (x, y)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d2, POS))
    p.append(text(ox + plot_w * 0.62, base - A + 30, "пасивний RC: загинається", size=12, bold=True, color=POS))
    p.append(text(ox + plot_w * 0.62, base - A + 46, "(дірявий — заряд гальмує сам себе)", size=11, color=POS))

    b, _, _ = textbox(W / 2, 348,
                      "На той самий сталий вхід пасивний RC дає експоненту: накопичена напруга сама зменшує\n"
                      "струм, і лінія гнеться. ОП тримає вузол на 0 В — струм сталий, вихід росте рівно, аж до стелі.",
                      size=12, fill="#f4f6f8", stroke=LINE)
    p.append(b)
    render(os.path.join(OUT, 'ramp-compare.svg'), W, H, *p,
           title="Пасивний RC гнеться, ОП-інтегратор тримає пряму")


# ───────────────────────────────────────────────────────────────────────────
def differentiator_circuit():
    """ОП-диференціатор: C на вході, R у ЗЗ; додано Rs (послідовно з C) і Cf (паралельно R)."""
    W, H = 720, 400
    p = []
    ax, ay = 360, 150
    amp, m, pl, o = opamp(ax, ay)
    p.append(amp)

    inx = 64
    p.append(circle(inx, m[1], 3, fill=BG, stroke=LINE, sw=1.6))
    p.append(text(inx, m[1] - 12, "вхід", size=12, color=MUTED))
    # C вхідний
    cx = inx + 40
    p.append(line(inx, m[1], cx - 6, m[1], color=LINE, sw=1.6))
    p.append(line(cx - 6, m[1] - 11, cx - 6, m[1] + 11, color=LINE, sw=2.6))
    p.append(line(cx + 6, m[1] - 11, cx + 6, m[1] + 11, color=LINE, sw=2.6))
    p.append(text(cx, m[1] - 18, "C", size=14, bold=True))
    # Rs послідовний (приборкання дзвону) — пунктирна рамка «практична добавка»
    rsx = cx + 6
    rssvg, rsl, rsr = _res_h(rsx + 8, m[1], w=38, h=14)
    p.append(line(rsx, m[1], rsx + 8, m[1], color=LINE, sw=1.6))
    p.append(rssvg)
    p.append(text(rsx + 27, m[1] + 20, "Rs", size=12, bold=True, color=FIELD))
    p.append(line(rsr, m[1], m[0], m[1], color=LINE, sw=1.6))
    p.append(circle(m[0], m[1], 2.6, fill=INK, stroke=INK))

    # «+» -> земля
    p.append(line(pl[0], pl[1], pl[0] - 24, pl[1], color=LINE, sw=1.6))
    p.append(line(pl[0] - 24, pl[1], pl[0] - 24, pl[1] + 22, color=LINE, sw=1.6))
    p.append(_gnd(pl[0] - 24, pl[1] + 22))

    # вихід
    p.append(line(o[0], o[1], o[0] + 24, o[1], color=LINE, sw=1.6))
    outx = o[0] + 24
    p.append(circle(outx, o[1], 2.6, fill=INK, stroke=INK))
    p.append(line(outx, o[1], outx + 56, o[1], color=LINE, sw=1.6))
    p.append(circle(outx + 56, o[1], 3, fill=BG, stroke=LINE, sw=1.6))
    p.append(text(outx + 66, o[1] + 4, "вихід", size=12, color=MUTED, anchor="start"))

    # ЗЗ: R від виходу у вузол «−»
    fbY = ay - 58
    p.append(line(m[0], m[1], m[0], fbY, color=LINE, sw=1.6))
    p.append(line(outx, o[1], outx, fbY, color=LINE, sw=1.6))
    rfsvg, rfl, rfr = _res_h((m[0] + outx) / 2 - 23, fbY)
    p.append(line(m[0], fbY, (m[0] + outx) / 2 - 23, fbY, color=LINE, sw=1.6))
    p.append(rfsvg)
    p.append(text((m[0] + outx) / 2, fbY - 14, "R", size=14, bold=True))
    p.append(line((m[0] + outx) / 2 + 23, fbY, outx, fbY, color=LINE, sw=1.6))

    # Cf паралельно R (обмеження ВЧ) — вище, пунктир «практична добавка»
    cfY = fbY - 34
    p.append(line(m[0], fbY, m[0], cfY, color=FIELD, sw=1.4, dash="3 3"))
    p.append(line(outx, fbY, outx, cfY, color=FIELD, sw=1.4, dash="3 3"))
    cfx = (m[0] + outx) / 2
    p.append(line(m[0], cfY, cfx - 6, cfY, color=FIELD, sw=1.4, dash="3 3"))
    p.append(line(cfx - 6, cfY - 10, cfx - 6, cfY + 10, color=FIELD, sw=2.4))
    p.append(line(cfx + 6, cfY - 10, cfx + 6, cfY + 10, color=FIELD, sw=2.4))
    p.append(line(cfx + 6, cfY, outx, cfY, color=FIELD, sw=1.4, dash="3 3"))
    p.append(text(cfx, cfY - 14, "Cf", size=12, bold=True, color=FIELD))

    p.append(text(m[0] - 2, m[1] + 30, "вірт. земля 0 В", size=11, color=MUTED))

    b1, _, _ = textbox(160, 322,
                       "Чистий диференціатор:\nC на вході, R у ЗЗ.\nV_вих = −RC·dV_вх/dt",
                       size=11, fill="#fdecea", stroke=POS)
    p.append(b1)
    b2, _, _ = textbox(540, 322,
                       "Зелене — практичні добавки:\nRs гасить дзвін, Cf ріже\nшум на високих частотах.",
                       size=11, fill="#eef7f0", stroke=FIELD)
    p.append(b2)
    render(os.path.join(OUT, 'differentiator-circuit.svg'), W, H, *p,
           title="ОП-диференціатор: C на вході, R у ЗЗ (+ Rs і Cf приборкують шум)")


# ───────────────────────────────────────────────────────────────────────────
def practical_integrator():
    """Чому потрібен Rf || C: без нього дрейф зсуву інтегрується й вихід повзе в стелю."""
    W, H = 720, 360
    p = []
    ox, oy = 90, 300
    aw, ah = 540, 232
    # осі
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.8))
    p.append(line(ox, oy, ox, oy - ah, color=INK, sw=1.8))
    p.append(text(ox + aw / 2, oy + 30, "частота (log)", size=13, bold=True))
    p.append(text(ox - 64, oy - ah / 2, "підсилення", size=13, bold=True))
    p.append(text(ox - 64, oy - ah / 2 + 18, "(log)", size=12, color=MUTED))

    fc = ox + aw * 0.30
    p.append(line(fc, oy, fc, oy - ah, color=MUTED, sw=1, dash="4 4"))
    p.append(text(fc, oy - ah - 6, "f_c = 1/(2π·Rf·C)", size=12, bold=True, color=MUTED))

    # без Rf: спад −6 дБ/окт через увесь діапазон, зліва йде в нескінченність (стрілка вгору)
    p.append(line(ox + 4, oy - ah + 6, ox + aw, oy - ah + 6 + ah * 0.86, color=POS, sw=2.6))
    p.append(text(ox + 40, oy - ah + 2, "без Rf: підсилення на сталому → ∞", size=12, bold=True, color=POS, anchor="start"))
    p.append(text(ox + 8, oy - ah + 30, "(дрейф зсуву інтегрується у стелю)", size=11, color=POS, anchor="start"))

    # з Rf: плато до fc (скінченне підсилення на DC = Rf/R), далі −6 дБ/окт паралельно
    yflat = oy - ah * 0.62
    p.append(line(ox, yflat, fc, yflat, color=NEG, sw=2.8))
    p.append(line(fc, yflat, ox + aw, yflat + (ox + aw - fc) * (ah * 0.86 / aw), color=NEG, sw=2.8))
    p.append(text(ox + 8, yflat - 8, "з Rf ‖ C: плато = Rf/R на сталому", size=12, bold=True, color=NEG, anchor="start"))
    p.append(text(fc + 60, yflat + 70, "−6 дБ/окт: інтегрує вище f_c", size=12, bold=True, color=NEG))

    b, _, _ = textbox(W / 2, 330,
                      "Без резистора в зворотному зв'язку інтегратор має нескінченне підсилення на сталому —\n"
                      "крихітний зсув ОП накопичується й садить вихід у стелю. Rf ‖ C обмежує підсилення на DC.",
                      size=12, fill="#f4f6f8", stroke=LINE)
    p.append(b)
    render(os.path.join(OUT, 'practical-integrator.svg'), W, H, *p,
           title="Практичний інтегратор: Rf ‖ C обмежує підсилення на сталому")


# ───────────────────────────────────────────────────────────────────────────
def pole_zero_map():
    """Карта полюсів і нулів у площині s для чотирьох схем — суть передавальних функцій."""
    W, H = 720, 470
    p = []

    def axes(cx, cy, ax_w, ax_h, caption, sub):
        out = []
        out.append(line(cx - ax_w, cy, cx + ax_w, cy, color=INK, sw=1.6))      # Re(s) — σ
        out.append(line(cx, cy + ax_h, cx, cy - ax_h, color=INK, sw=1.6))      # Im(s) — jω
        out.append(arrow(cx + ax_w - 16, cy, cx + ax_w, cy, color=INK, sw=1.4))
        out.append(arrow(cx, cy - ax_h + 16, cx, cy - ax_h, color=INK, sw=1.4))
        out.append(text(cx + ax_w + 4, cy + 4, "σ", size=12, color=MUTED, anchor="start", italic=True))
        out.append(text(cx + 6, cy - ax_h + 2, "jω", size=12, color=MUTED, anchor="start", italic=True))
        out.append(text(cx, cy + ax_h + 22, caption, size=12, bold=True))
        out.append(text(cx, cy + ax_h + 38, sub, size=11, color=MUTED))
        return out

    def pole(cx, cy):   # ×
        return (line(cx - 6, cy - 6, cx + 6, cy + 6, color=POS, sw=2.4) +
                line(cx - 6, cy + 6, cx + 6, cy - 6, color=POS, sw=2.4))

    def zero(cx, cy):   # ○
        return circle(cx, cy, 6, fill=BG, stroke=FIELD, sw=2.4)

    # розкладка 2×2
    col = [200, 540]
    row = [120, 320]
    ah_w, ah_h = 130, 66

    # 1) ідеальний інтегратор: полюс у нулі (на початку координат)
    p += axes(col[0], row[0], ah_w, ah_h, "Ідеальний інтегратор", "H = −1/(sRC) — полюс у 0")
    p.append(pole(col[0], row[0]))
    p.append(text(col[0] + 12, row[0] - 10, "полюс у 0\n(DC → ∞)".split("\n")[0], size=11, color=POS, anchor="start"))
    p.append(text(col[0] + 12, row[0] + 4, "(DC → ∞)", size=10, color=POS, anchor="start"))

    # 2) практичний інтегратор: полюс ліворуч на −1/(Rf·C)
    p += axes(col[1], row[0], ah_w, ah_h, "Практичний інтегратор", "полюс на −1/(Rf·C)")
    px = col[1] - 64
    p.append(pole(px, row[0]))
    p.append(line(px, row[0] + 4, px, row[0] + 16, color=POS, sw=1, dash="2 3"))
    p.append(text(px, row[0] + 30, "−1/(Rf·C)", size=10, color=POS))
    p.append(text(col[1] + 10, row[0] - 10, "полюс зсунувся\nз 0 уліво".split("\n")[0], size=11, color=POS, anchor="start"))
    p.append(text(col[1] + 10, row[0] + 4, "з 0 уліво", size=10, color=POS, anchor="start"))

    # 3) ідеальний диференціатор: нуль у нулі
    p += axes(col[0], row[1], ah_w, ah_h, "Ідеальний диференціатор", "H = −sRC — нуль у 0")
    p.append(zero(col[0], row[1]))
    p.append(text(col[0] + 12, row[1] - 10, "нуль у 0", size=11, color=FIELD, anchor="start"))
    p.append(text(col[0] + 12, row[1] + 4, "(росте з ω)", size=10, color=FIELD, anchor="start"))

    # 4) практичний диференціатор: нуль у 0 + два полюси ліворуч
    p += axes(col[1], row[1], ah_w, ah_h, "Практичний диференціатор", "нуль у 0 + два полюси")
    p.append(zero(col[1], row[1]))
    pz1 = col[1] - 50
    pz2 = col[1] - 92
    p.append(pole(pz1, row[1]))
    p.append(pole(pz2, row[1]))
    p.append(text(pz1, row[1] + 28, "−1/(R·Cf)", size=10, color=POS))
    p.append(text(pz2, row[1] - 14, "−1/(Rs·C)", size=10, color=POS))

    b, _, _ = textbox(W / 2, 452,
                      "× — полюс (підсилення прямує вгору),  ○ — нуль (прямує вниз). Інтегратор має полюс, диференціатор — нуль;\n"
                      "практичні варіанти лиш зсувають полюс із 0 уліво або додають полюси, що завертають підсилення згори.",
                      size=11, fill="#f4f6f8", stroke=LINE)
    p.append(b)
    render(os.path.join(OUT, 'pole-zero-map.svg'), W, H, *p,
           title="Полюси й нулі чотирьох схем у площині s")


# ───────────────────────────────────────────────────────────────────────────
def diff_bode():
    """Боде практичного диференціатора: +20 дБ/дек, плато Rf/Rs, спад −20 дБ/дек — два злами."""
    W, H = 720, 380
    p = []
    ox, oy = 96, 300
    aw, ah = 540, 236
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.8))
    p.append(line(ox, oy, ox, oy - ah, color=INK, sw=1.8))
    p.append(text(ox + aw / 2, oy + 30, "частота ω (log)", size=13, bold=True))
    p.append(text(ox - 70, oy - ah / 2, "|H| (log)", size=13, bold=True))

    # два зломи
    f1 = ox + aw * 0.30          # нижній: 1/(R·Cf) — кінець підйому, початок плато
    f2 = ox + aw * 0.62          # верхній: 1/(Rs·C) — кінець плато, початок спаду
    for fx, lab, dy in ((f1, "ω₁ = 1/(R·Cf)", -6), (f2, "ω₂ = 1/(Rs·C)", -6)):
        p.append(line(fx, oy, fx, oy - ah, color=MUTED, sw=1, dash="4 4"))
        p.append(text(fx, oy - ah - 6 + dy, lab, size=11, bold=True, color=MUTED))

    yplat = oy - ah * 0.66       # рівень плато
    # ділянка 1: підйом +20 дБ/дек (зростання з ω — справжнє диференціювання)
    p.append(line(ox + 6, oy - ah * 0.18, f1, yplat, color=NEG, sw=2.8))
    p.append(text(ox + 18, oy - ah * 0.10, "+20 дБ/дек", size=12, bold=True, color=NEG, anchor="start"))
    p.append(text(ox + 18, oy - ah * 0.10 + 16, "(чесна похідна, ∝ ω)", size=10, color=NEG, anchor="start"))
    # ділянка 2: плато Rf/Rs
    p.append(line(f1, yplat, f2, yplat, color=FIELD, sw=2.8))
    p.append(text((f1 + f2) / 2, yplat - 10, "плато ≈ R/Rs", size=12, bold=True, color=FIELD))
    p.append(text((f1 + f2) / 2, yplat - 26, "(стеля підсилення)", size=10, color=FIELD))
    # ділянка 3: спад −20 дБ/дек
    p.append(line(f2, yplat, ox + aw - 6, yplat + ah * 0.42, color=POS, sw=2.8))
    p.append(text(f2 + 70, yplat + ah * 0.30, "−20 дБ/дек", size=12, bold=True, color=POS))
    p.append(text(f2 + 70, yplat + ah * 0.30 + 16, "(шум придушено)", size=10, color=POS))

    # пунктир: куди йшов би ідеальний диф. без приборкання
    p.append(line(ox + 6, oy - ah * 0.18, ox + aw * 0.80, oy - ah * 1.02, color=MUTED, sw=1.4, dash="3 4"))
    p.append(text(ox + aw * 0.52, oy - ah * 0.94, "ідеальний: росте без стелі", size=10, color=MUTED, anchor="start"))

    b, _, _ = textbox(W / 2, 348,
                      "Практичний диференціатор диференціює (+20 дБ/дек) лише між двома зламами; вище ω₂ підсилення\n"
                      "виходить на плато R/Rs, а далі спадає (−20 дБ/дек) — саме це й рятує від шуму та дзвону.",
                      size=12, fill="#f4f6f8", stroke=LINE)
    p.append(b)
    render(os.path.join(OUT, 'diff-bode.svg'), W, H, *p,
           title="Боде практичного диференціатора: підйом → плато → спад")


# ───────────────────────────────────────────────────────────────────────────
def miller_multiply():
    """Серце ефекту Міллера: вхід +1 В → вихід −A В → різниця на C росте в (1+A) разів."""
    W, H = 720, 360
    p = []
    ax, ay = 330, 130
    amp, m, pl, o = opamp(ax, ay)
    p.append(amp)
    p.append(text(ax + 30, ay + 36 + 5, "A", size=15, bold=True, color=MUTED))

    # вхід ліворуч у вузол «−»
    inx = 80
    p.append(line(inx, m[1], m[0], m[1], color=LINE, sw=1.6))
    p.append(circle(inx, m[1], 3, fill=BG, stroke=LINE, sw=1.6))
    p.append(circle(m[0], m[1], 2.6, fill=INK, stroke=INK))
    p.append(text(inx - 4, m[1] - 14, "вхід", size=12, color=MUTED, anchor="start"))
    p.append(text(inx - 4, m[1] + 24, "+1 В", size=13, bold=True, color=POS, anchor="start"))
    p.append(arrow(inx + 18, m[1] + 14, inx + 18, m[1] - 2, color=POS, sw=2.0))

    # «+» на землю
    p.append(line(pl[0], pl[1], pl[0] - 24, pl[1], color=LINE, sw=1.6))
    p.append(line(pl[0] - 24, pl[1], pl[0] - 24, pl[1] + 22, color=LINE, sw=1.6))
    p.append(_gnd(pl[0] - 24, pl[1] + 22))

    # вихід праворуч
    outx = o[0] + 30
    p.append(line(o[0], o[1], outx, o[1], color=LINE, sw=1.6))
    p.append(circle(outx, o[1], 3, fill=BG, stroke=LINE, sw=1.6))
    p.append(line(outx, o[1], outx + 50, o[1], color=LINE, sw=1.6))
    p.append(text(outx + 56, o[1] + 4, "вихід", size=12, color=MUTED, anchor="start"))
    p.append(text(outx + 56, o[1] + 22, "−A В", size=13, bold=True, color=NEG, anchor="start"))
    p.append(arrow(outx + 76, o[1] - 12, outx + 76, o[1] + 18, color=NEG, sw=2.0))

    # ємність C з виходу у вузол «−» (верхня гілка)
    fbY = ay - 60
    p.append(line(m[0], m[1], m[0], fbY, color=FIELD, sw=1.8))
    p.append(line(outx, o[1], outx, fbY, color=FIELD, sw=1.8))
    midfb = (m[0] + outx) / 2
    p.append(line(m[0], fbY, midfb - 6, fbY, color=FIELD, sw=1.8))
    p.append(line(midfb - 6, fbY - 12, midfb - 6, fbY + 12, color=FIELD, sw=2.8))
    p.append(line(midfb + 6, fbY - 12, midfb + 6, fbY + 12, color=FIELD, sw=2.8))
    p.append(line(midfb + 6, fbY, outx, fbY, color=FIELD, sw=1.8))
    p.append(text(midfb, fbY - 18, "C (сітка-анод)", size=12, bold=True, color=FIELD))
    p.append(text(midfb, fbY + 30, "різниця напруг на C", size=11, color=FIELD))
    p.append(text(midfb, fbY + 46, "змінюється на (1+A) В", size=12, bold=True, color=FIELD))

    b, _, _ = textbox(W / 2, 318,
                      "Вхід піднявся на +1 В, вихід упав на −A В: різниця на ємності зросла в (1+A) разів,\n"
                      "тож стільки ж заряду треба прокачати з боку входу — крихітна C здається помноженою на (1+A).",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'miller-multiply.svg'), W, H, *p,
           title="Ефект Міллера: ємність між входом і виходом важить (1+A) разів")


# ───────────────────────────────────────────────────────────────────────────
def miller_two_faces():
    """Один механізм — два наслідки: ворог у підсилювачі, союзник в інтеграторі."""
    W, H = 720, 420
    p = []
    midx = W / 2
    p.append(line(midx, 70, midx, H - 70, color="#d8dce1", sw=1.4, dash="6 6"))

    # спільне ядро зверху
    core, _, _ = textbox(midx, 56,
                         "ЕФЕКТ МІЛЛЕРА:  C між входом і виходом інвертуючого каскаду  →  важить (1+A) разів",
                         size=12, bold=True, fill="#f4f6f8", stroke=INK)
    p.append(core)

    # ── ліва панель: ВОРОГ (підсилювач) ───────────────────────────────
    lx = midx / 2
    p.append(text(lx, 108, "у підсилювачі — ВОРОГ", size=14, bold=True, color=POS))
    bx, by, bw, bh = 60, 150, 250, 120
    p.append(line(bx, by + bh, bx + bw, by + bh, color=MUTED, sw=1.2))   # вісь частоти
    p.append(line(bx, by, bx, by + bh, color=MUTED, sw=1.2))             # вісь підсилення
    p.append(text(bx + bw / 2, by + bh + 18, "частота →", size=11, color=MUTED))
    p.append(line(bx + 4, by + 12, bx + bw - 4, by + 12, color=MUTED, sw=1.2, dash="4 4"))
    p.append(text(bx + bw - 6, by + 6, "без Міллера", size=10, color=MUTED, anchor="end"))
    p.append('<path d="M%.0f %.0f L%.0f %.0f Q %.0f %.0f %.0f %.0f" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (bx + 4, by + 12, bx + bw * 0.34, by + 12,
                bx + bw * 0.62, by + 14, bx + bw - 6, by + bh - 14, POS))
    p.append(text(bx + bw * 0.62, by + 40, "роздута C_вх", size=11, bold=True, color=POS))
    p.append(text(bx + bw * 0.62, by + 56, "ріже високі частоти", size=10, color=POS))
    b1, _, _ = textbox(lx, 322, "Велика ефективна ємність —\nбаласт, який важко розгойдати:\nсмуга падає, фаза гойдається.",
                       size=11, fill="#fdecea", stroke=POS)
    p.append(b1)

    # ── права панель: СОЮЗНИК (інтегратор) ────────────────────────────
    rx = midx + midx / 2
    p.append(text(rx, 108, "в інтеграторі — СОЮЗНИК", size=14, bold=True, color=NEG))
    aox, aoy = midx + 70, 150
    amp, m, pl, o = opamp(aox, aoy, w=72, h=60)
    p.append(amp)
    p.append(line(m[0] - 36, m[1], m[0], m[1], color=LINE, sw=1.5))
    p.append(circle(m[0], m[1], 2.4, fill=INK, stroke=INK))
    p.append(text(m[0] - 38, m[1] + 20, "0 В", size=11, bold=True, color=NEG, anchor="start"))
    p.append(text(m[0] - 38, m[1] + 35, "вірт. земля", size=10, color=MUTED, anchor="start"))
    p.append(line(pl[0], pl[1], pl[0] - 18, pl[1], color=LINE, sw=1.5))
    p.append(_gnd(pl[0] - 18, pl[1] + 6))
    outx = o[0] + 22
    p.append(line(o[0], o[1], outx, o[1], color=LINE, sw=1.5))
    p.append(circle(outx, o[1], 2.4, fill=INK, stroke=INK))
    fbY = aoy - 44
    p.append(line(m[0], m[1], m[0], fbY, color=FIELD, sw=1.6))
    p.append(line(outx, o[1], outx, fbY, color=FIELD, sw=1.6))
    midfb = (m[0] + outx) / 2
    p.append(line(m[0], fbY, midfb - 5, fbY, color=FIELD, sw=1.6))
    p.append(line(midfb - 5, fbY - 10, midfb - 5, fbY + 10, color=FIELD, sw=2.6))
    p.append(line(midfb + 5, fbY - 10, midfb + 5, fbY + 10, color=FIELD, sw=2.6))
    p.append(line(midfb + 5, fbY, outx, fbY, color=FIELD, sw=1.6))
    p.append(text(midfb, fbY - 14, "C", size=12, bold=True, color=FIELD))
    b2, _, _ = textbox(rx, 322, "Та сама велика ефективна ємність\nтримає вхід на 0 В —\nі конденсатор бере чесний інтеграл.",
                       size=11, fill="#eaf0fd", stroke=NEG)
    p.append(b2)

    b, _, _ = textbox(W / 2, 392,
                      "Одна й та сама фізика — множення ємності на підсилення. Змінюється тільки знак користі.",
                      size=12, bold=True, fill="#f4f6f8", stroke=INK)
    p.append(b)
    render(os.path.join(OUT, 'miller-two-faces.svg'), W, H, *p,
           title="Один ефект Міллера — два протилежні наслідки")


if __name__ == '__main__':
    integrator_circuit()
    ramp_compare()
    differentiator_circuit()
    practical_integrator()
    pole_zero_map()
    diff_bode()
    miller_multiply()
    miller_two_faces()
    print("OK: 8 figures ->", OUT)
