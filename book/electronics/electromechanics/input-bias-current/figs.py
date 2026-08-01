# -*- coding: utf-8 -*-
"""Фігури до статті «Вхідний струм зсуву (input bias current)».
Генерує SVG у ./img/. Запуск: python figs.py (з теки теми)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── допоміжні примітиви ─────────────────────────────────────────────────────
def npn(cx, cy, inward, r=24):
    """NPN-транзистор: база назовні (−inward), колектор/емітер усередину (+inward).
    Повертає (svg, base_pin, coll_pin, emit_pin)."""
    bx = cx
    parts = [circle(cx, cy, r)]
    # вертикальна планка бази
    parts.append(line(bx, cy - 14, bx, cy + 14, sw=2.6))
    # вивід бази — назовні
    base_pin = (cx - inward * (r + 10), cy)
    parts.append(line(bx, cy, base_pin[0], cy, sw=1.8))
    # колектор — усередину й угору
    cx2 = bx + inward * 16
    parts.append(line(bx, cy - 8, cx2, cy - 20, sw=1.8))
    coll_pin = (cx2, cy - (r + 20))
    parts.append(line(cx2, cy - 20, coll_pin[0], coll_pin[1], sw=1.8))
    # емітер — усередину й униз, зі стрілкою (NPN: назовні від бази)
    ex2 = bx + inward * 16
    parts.append(arrow(bx, cy + 8, ex2, cy + 20))
    emit_pin = (ex2, cy + (r + 20))
    parts.append(line(ex2, cy + 20, emit_pin[0], emit_pin[1], sw=1.8))
    return "".join(parts), base_pin, coll_pin, emit_pin


def opamp(cx, cy, hh=46, w=92):
    """Трикутник ОП вершиною праворуч. Повертає (svg, in_p, in_n, out)."""
    left = cx - w / 2
    right = cx + w / 2
    poly = ('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" '
            'stroke="%s" stroke-width="1.8"/>' %
            (left, cy - hh, left, cy + hh, right, cy, FILL, LINE))
    in_p = (left, cy - 22)
    in_n = (left, cy + 22)
    out = (right, cy)
    svg = poly + plus(left + 15, cy - 22, r=7) + minus(left + 15, cy + 22, r=7)
    return svg, in_p, in_n, out


def res_v(x, ytop, h=64, label="", lx=14):
    """Вертикальний резистор (коробка IEC) від (x,ytop) донизу; підпис праворуч."""
    w = 16
    svg = rect(x - w / 2, ytop, w, h, fill="#fff")
    if label:
        svg += text(x + lx, ytop + h / 2 + 4, label, size=13, anchor="start")
    return svg, (x, ytop), (x, ytop + h)


def gnd(x, y):
    return (line(x - 13, y, x + 13, y, sw=1.8) +
            line(x - 8, y + 5, x + 8, y + 5, sw=1.8) +
            line(x - 3, y + 10, x + 3, y + 10, sw=1.8))


# ── Фігура 1: звідки у входу струм (диференційна пара) ───────────────────────
def fig_origin():
    W, H = 792, 494
    f = []
    # шини живлення
    yVp, yVm = 112, 398
    f.append(line(300, yVp, 486, yVp, sw=2))
    f.append(text(506, yVp + 5, "V+", size=14, color=MUTED, anchor="start"))
    f.append(line(300, yVm, 486, yVm, sw=2))
    f.append(text(506, yVm + 5, "V−", size=14, color=MUTED, anchor="start"))

    # транзистори пари
    q1, b1, c1, e1 = npn(312, 232, +1)
    q2, b2, c2, e2 = npn(474, 232, -1)
    f.append(q1)
    f.append(q2)

    # колектори — угору через маленькі навантаження до шини
    for cx in (c1[0], c2[0]):
        f.append(line(cx, c1[1], cx, 180, sw=1.8))
        f.append(rect(cx - 8, 150, 16, 30, fill="#fff"))
        f.append(line(cx, 150, cx, yVp, sw=1.8))
    f.append(text(c1[0] - 26, 145, "R", size=12, color=MUTED, anchor="end"))
    f.append(text(c2[0] + 26, 145, "R", size=12, color=MUTED, anchor="start"))

    # емітери — до спільного вузла й джерела хвостового струму
    ytail = 300
    f.append(line(e1[0], e1[1], e1[0], ytail, sw=1.8))
    f.append(line(e2[0], e2[1], e2[0], ytail, sw=1.8))
    f.append(line(e1[0], ytail, e2[0], ytail, sw=1.8))
    mid = (e1[0] + e2[0]) / 2
    f.append(line(mid, ytail, mid, 322, sw=1.8))
    f.append(circle(mid, 340, 17))
    f.append(arrow(mid, 350, mid, 331))  # стрілка струму вгору
    f.append(text(mid + 26, 344, "I_хв", size=12, color=MUTED, anchor="start"))
    f.append(line(mid, 357, mid, yVm, sw=1.8))

    # бази — назовні до входів
    f.append(line(b1[0], b1[1], 168, 232, sw=1.8))
    f.append(plus(150, 232, r=10))
    f.append(line(b2[0], b2[1], 618, 232, sw=1.8))
    f.append(minus(636, 232, r=10))

    # стрілки струму зсуву — у бази
    f.append(arrow(192, 232, 262, 232))
    f.append(text(227, 219, "I_B⁺", size=14, color=POS, anchor="middle", bold=True))
    f.append(arrow(594, 232, 524, 232))
    f.append(text(559, 219, "I_B⁻", size=14, color=NEG, anchor="middle", bold=True))

    # підпис знизу
    cap = ["Кожен вхід ОП — це база вхідного транзистора: щоб пара підсилювала,",
           "у бази мусить текти струм. Цей неминучий струм — вхідний струм зсуву."]
    box, bw, bh = textbox(W / 2, 452, cap, size=13, pad=12, fill="#f0f7f2", stroke=FIELD)
    f.append(box)

    render(os.path.join(IMG, "diff-pair-bias-origin.svg"), W, H, *f,
           title="Звідки в «нескінченно високоомного» входу струм")


# ── Фігура 2: компенсаційний резистор ───────────────────────────────────────
def fig_compensation():
    W, H = 936, 388
    f = []

    def panel(x0, ptitle, rp_label, rn_label, res1, res2):
        p = [text(x0 + 210, 60, ptitle, size=15, bold=True)]
        oa, in_p, in_n, out = opamp(x0 + 300, 190)
        p.append(oa)
        # вихід
        p.append(line(out[0], out[1], out[0] + 46, out[1], sw=1.8))
        p.append(text(out[0] + 52, out[1] + 5, "вихід", size=12, color=MUTED, anchor="start"))
        # + вхід: провід ліворуч, резистор на землю, стрілка I_B у вхід
        yP = in_p[1]
        p.append(line(in_p[0], yP, x0 + 116, yP, sw=1.8))
        rv, top, bot = res_v(x0 + 116, yP + 6, h=60, label=rp_label)
        p.append(rv)
        p.append(gnd(bot[0], bot[1] + 4))
        p.append(arrow(x0 + 150, yP, x0 + 232, yP))
        p.append(text(x0 + 191, yP - 11, "I_B⁺", size=13, color=POS, bold=True))
        # − вхід
        yN = in_n[1]
        p.append(line(in_n[0], yN, x0 + 170, yN, sw=1.8))
        rv2, top2, bot2 = res_v(x0 + 170, yN + 6, h=52, label=rn_label)
        p.append(rv2)
        p.append(gnd(bot2[0], bot2[1] + 4))
        p.append(arrow(x0 + 204, yN, x0 + 262, yN))
        p.append(text(x0 + 233, yN + 20, "I_B⁻", size=13, color=NEG, bold=True))
        # результат
        box, bw, bh = textbox(x0 + 210, 332, [res1, res2], size=13, pad=10,
                              fill="#f7f7f9", stroke=MUTED)
        p.append(box)
        return "".join(p)

    f.append(panel(14, "Опори на входах не зрівняні", "Rₚ (мале)", "Rₙ (велике)",
                   "V₊ = I_B⁺·Rₚ ,  V₋ = I_B⁻·Rₙ",
                   "Rₚ ≠ Rₙ  →  різниця  →  похибка"))
    f.append(line(468, 48, 468, 360, color="#d0d4da", sw=1.4, dash="5,5"))
    f.append(panel(486, "Опори зрівняні (Rc = R1 ‖ Rf)", "R", "R",
                   "I_B⁺·R  ≈  I_B⁻·R  →  спільне гаситься",
                   "лишок = (I_B⁺−I_B⁻)·R = I_os·R"))

    render(os.path.join(IMG, "bias-error-compensation.svg"), W, H, *f,
           title="Компенсаційний резистор: рівні опори гасять струм зсуву")


# ── Фігура 3: I_B vs температура ────────────────────────────────────────────
def fig_temperature():
    W, H = 988, 520
    left, right = 128, 742
    top, bot = 72, 432
    pw, ph = right - left, bot - top
    ymax, ymin = 1e-6, 1e-14
    lgmax, lgmin = math.log10(ymax), math.log10(ymin)

    def xf(T):
        return left + (T - 25) / (125 - 25) * pw

    def yf(v):
        return top + (lgmax - math.log10(v)) / (lgmax - lgmin) * ph

    f = []
    # рамка
    f.append(rect(left, top, pw, ph, fill="#fff", stroke=MUTED, sw=1.4))
    # декадні лінії й підписи
    decs = [(1e-6, "1 мкА"), (1e-7, "100 нА"), (1e-8, "10 нА"), (1e-9, "1 нА"),
            (1e-10, "100 пА"), (1e-11, "10 пА"), (1e-12, "1 пА"),
            (1e-13, "100 фА"), (1e-14, "10 фА")]
    for v, lab in decs:
        y = yf(v)
        f.append(line(left, y, right, y, color="#e6e8ec", sw=1))
        f.append(text(left - 10, y + 4, lab, size=12, color=MUTED, anchor="end"))
    # вісь X — температура
    for T in (25, 45, 65, 85, 105, 125):
        x = xf(T)
        f.append(line(x, bot, x, bot + 6, color=MUTED, sw=1.2))
        f.append(text(x, bot + 22, "%d" % T, size=12, color=MUTED))
    f.append(text((left + right) / 2, bot + 44, "температура кристала, °C",
                  size=13, color=INK))
    f.append(text(left - 14, top - 16, "|I_B|", size=13, color=INK, anchor="start", bold=True))

    def curve(pts, color, sw=2.6):
        d = " ".join("%.1f,%.1f" % (xf(T), yf(v)) for T, v in pts)
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>'
                % (d, color, sw))

    Ts = list(range(25, 126, 10))
    bifet = [(T, 30e-12 * 2 ** ((T - 25) / 10)) for T in Ts]
    electro = [(T, 60e-15 * 2 ** ((T - 25) / 10)) for T in Ts]
    bipolar = [(25, 8e-8), (125, 5.5e-8)]
    precision = [(25, 2.5e-9), (125, 3.0e-9)]

    f.append(curve(bipolar, INK))
    f.append(curve(precision, "#8a6d1f", sw=2.4))
    f.append(curve(bifet, FIELD))
    f.append(curve(electro, POS))

    # підписи пласких кривих — ліворуч, над лінією, у вільному полі
    f.append(text(xf(30), yf(8e-8) - 10, "µA741  ~80 нА  (біполярний вхід)",
                  size=12.5, color=INK, anchor="start", bold=True))
    f.append(text(xf(30), yf(2.5e-9) - 10, "LM108 / OP07  ~одиниці нА  (суперβ, зі скасуванням)",
                  size=12.5, color="#8a6d1f", anchor="start", bold=True))
    # підписи зростаючих кривих — праворуч біля правого кінця
    f.append(text(right + 8, yf(bifet[-1][1]) + 4, "BiFET LF356", size=12.5,
                  color=FIELD, anchor="start", bold=True))
    f.append(text(right + 8, yf(bifet[-1][1]) + 22, "30 пА, ×2 на 10 °C", size=11.5,
                  color=FIELD, anchor="start"))
    f.append(text(right + 8, yf(electro[-1][1]) + 4, "електрометр AD549", size=12.5,
                  color=POS, anchor="start", bold=True))
    f.append(text(right + 8, yf(electro[-1][1]) + 22, "60 фА (Topgate JFET)", size=11.5,
                  color=POS, anchor="start"))

    # точка перетину green×precision (~89 °C)
    Tx = 25 + 10 * math.log2(2.5e-9 / 30e-12)
    f.append(circle(xf(Tx), yf(2.5e-9), 5, fill="#fff", stroke=INK, sw=2))
    f.append(line(xf(Tx), yf(2.5e-9), xf(Tx) - 6, yf(3e-7) + 16, color=MUTED, sw=1, dash="4,4"))
    note, nw, nh = textbox(xf(Tx) - 6, yf(3e-7),
                           ["вище ≈90 °C витік JFET-затвора", "переростає струм бази"],
                           size=11.5, pad=8, fill="#fffdf5", stroke="#caa94a")
    f.append(note)

    render(os.path.join(IMG, "bias-current-vs-temperature.svg"), W, H, *f,
           title="Вхідний струм зсуву проти температури: біполярний вхід і JFET-вхід")


# ── допоміжні примітиви для вставки math-bias-compensation ──────────────────
def opamp2(cx, cy, hh=64, w=124, pin=34):
    """Трикутник ОП із рознесеними виводами (для великої схеми виведення)."""
    left, right = cx - w / 2.0, cx + w / 2.0
    poly = ('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" '
            'stroke="%s" stroke-width="1.8"/>' %
            (left, cy - hh, left, cy + hh, right, cy, FILL, LINE))
    svg = poly + plus(left + 18, cy - pin, r=8) + minus(left + 18, cy + pin, r=8)
    return svg, (left, cy - pin), (left, cy + pin), (right, cy)


def res_h(cx, cy, w=60, h=20, label="", dy=-10):
    """Горизонтальний резистор (коробка IEC); підпис над коробкою."""
    svg = rect(cx - w / 2.0, cy - h / 2.0, w, h, fill="#fff")
    if label:
        svg += text(cx, cy - h / 2.0 + dy, label, size=13, anchor="middle")
    return svg, (cx - w / 2.0, cy), (cx + w / 2.0, cy)


def dot(x, y, r=4.5):
    return circle(x, y, r, fill=INK, stroke=INK, sw=1)


# ── Фігура 4 (вставка): карта величин, що входять у виведення ────────────────
def fig_derivation_map():
    W, H = 980, 560
    yP, yN = 216, 284
    f = []

    oa, in_p, in_n, out = opamp2(640, 250)
    f.append(oa)

    # ── гілка «плюс»: джерело → R_s → Rc → вивід
    f.append(circle(78, yP, 11, fill="#fff"))
    f.append(text(78, yP - 22, "V_s", size=13, bold=True))
    f.append(line(89, yP, 120, yP, sw=1.8))
    rs, _, _ = res_h(150, yP, label="R_s")
    f.append(rs)
    f.append(line(180, yP, 270, yP, sw=1.8))
    rc, _, _ = res_h(300, yP, label="Rc")
    f.append(rc)
    f.append(line(330, yP, in_p[0], yP, sw=1.8))
    f.append(arrow(430, yP, 500, yP))
    f.append(text(465, yP - 12, "I_B⁺", size=13, color=POS, bold=True))
    f.append(text(556, yP - 12, "V⁺", size=13, bold=True))

    # ── гілка «мінус»: вузол, R1 на землю, Rf на вихід
    f.append(line(400, yN, in_n[0], yN, sw=1.8))
    f.append(dot(400, yN))
    f.append(dot(470, yN))
    f.append(arrow(500, yN, 565, yN))
    f.append(text(532, yN + 24, "I_B⁻", size=13, color=NEG, bold=True))
    f.append(text(556, yN - 12, "V⁻", size=13, bold=True))

    f.append(line(400, yN, 400, 310, sw=1.8))
    f.append(rect(392, 310, 16, 64, fill="#fff"))
    f.append(text(420, 348, "R1", size=13, anchor="start"))
    f.append(line(400, 374, 400, 398, sw=1.8))
    f.append(gnd(400, 402))

    f.append(line(470, yN, 470, 450, sw=1.8))
    f.append(line(470, 450, 628, 450, sw=1.8))
    rf, _, _ = res_h(660, 450, w=64, label="Rf")
    f.append(rf)
    f.append(line(692, 450, 800, 450, sw=1.8))
    f.append(line(800, 450, 800, 250, sw=1.8))
    f.append(dot(800, 250))
    f.append(line(out[0], out[1], 852, out[1], sw=1.8))
    f.append(text(864, out[1] + 5, "V_вих", size=13, anchor="start", bold=True))

    # ── два опори, що вирішують усе
    b1, w1, h1 = textbox(230, 140, ["R⁺ = R_s + Rc", "— що бачить «плюс»"],
                         size=13, pad=10, fill="#fdecea", stroke=POS)
    f.append(b1)
    f.append(line(230, 140 + h1 / 2 + 4, 230, yP - 8, color=POS, sw=1.2, dash="4,4"))

    b2, w2, h2 = textbox(215, 352, ["R⁻ = R1 ‖ Rf", "— що бачить «мінус»"],
                         size=13, pad=10, fill="#eaf0fd", stroke=NEG)
    f.append(b2)
    f.append(line(215 + w2 / 2 + 4, 344, 390, 292, color=NEG, sw=1.2, dash="4,4"))

    cap, _, _ = textbox(490, 505,
                        ["вузол «мінус»:  (0 − V⁻)/R1 + (V_вих − V⁻)/Rf = I_B⁻",
                         "зворотний зв'язок:  V⁻ = V⁺ = V_s − I_B⁺·(R_s + Rc)"],
                        size=13, pad=11, fill="#f7f7f9", stroke=MUTED)
    f.append(cap)

    render(os.path.join(IMG, "math-bias-derivation-map.svg"), W, H, *f,
           title="Схема виведення: два опори, два струми, одне рівняння")


# ── Фігура 5 (вставка): похибка на вході проти Rc ────────────────────────────
def fig_error_vs_rc():
    W, H = 900, 540
    left, right, top, bot = 120, 760, 80, 400
    pw, ph = right - left, bot - top
    xmax = 12.0            # Rc, кОм
    ymax, ymin = 850.0, -450.0   # ε, мкВ

    def xf(r):
        return left + r / xmax * pw

    def yf(v):
        return top + (ymax - v) / (ymax - ymin) * ph

    f = [rect(left, top, pw, ph, fill="#fff", stroke=MUTED, sw=1.4)]

    for v in (-400, -200, 0, 200, 400, 600, 800):
        y = yf(v)
        col = "#b8bcc4" if v == 0 else "#e6e8ec"
        f.append(line(left, y, right, y, color=col, sw=1.4 if v == 0 else 1))
        f.append(text(left - 10, y + 4, "%d" % v, size=12, color=MUTED, anchor="end"))
    for r in (0, 2, 4, 6, 8, 10, 12):
        x = xf(r)
        f.append(line(x, bot, x, bot + 6, color=MUTED, sw=1.2))
        f.append(text(x, bot + 22, "%d" % r, size=12, color=MUTED))
    f.append(text(left, top - 14, "ε — похибка, зведена до входу, мкВ",
                  size=12.5, color=INK, anchor="start"))
    f.append(text((left + right) / 2, bot + 46, "Rc — компенсаційний резистор, кОм",
                  size=13, color=INK))

    def poly(a, b, color, dash=None):
        """ε(Rc) = a − b·Rc на всьому проміжку."""
        pts = " ".join("%.1f,%.1f" % (xf(r), yf(a - b * r)) for r in (0.0, xmax))
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"%s/>'
                % (pts, color, d))

    # I_B⁺ = 88 нА, I_B⁻ = 72 нА → ε = 72·9 − 88·Rc (мкВ, Rc у кОм)
    f.append(poly(648.0, 88.0, POS))
    # I_B⁺ = 72 нА, I_B⁻ = 88 нА → ε = 88·9 − 72·Rc
    f.append(poly(792.0, 72.0, NEG))
    # паспортний номінал: I_B⁺ = I_B⁻ = 80 нА → ε = 80·9 − 80·Rc
    f.append(poly(720.0, 80.0, MUTED, dash="7,5"))

    x9 = xf(9.0)
    f.append(line(x9, top, x9, bot, color="#8a6d1f", sw=1.4, dash="5,5"))
    f.append(text(x9, top - 12, "Rc = R1 ‖ Rf = 9 кОм", size=12.5,
                  color="#8a6d1f", bold=True))
    for v, col in ((144.0, NEG), (0.0, MUTED), (-144.0, POS)):
        f.append(circle(x9, yf(v), 5, fill="#fff", stroke=col, sw=2.2))

    # легенда — у порожньому верхньому правому куті
    f.append(rect(572, 96, 186, 88, fill="#ffffff", stroke="#d0d4da", sw=1.2))
    for i, (lab, col, dash) in enumerate((
            ("I_os = +16 нА", POS, None),
            ("I_os = −16 нА", NEG, None),
            ("номінал: I_os = 0", MUTED, "7,5"))):
        y = 120 + i * 26
        f.append(line(584, y, 616, y, color=col, sw=2.6, dash=dash))
        f.append(text(624, y + 4, lab, size=12, color=INK, anchor="start"))

    note, nw, nh = textbox(280, 360, ["|ε| = 144 мкВ = I_os·R"], size=13, pad=10,
                           fill="#fffdf5", stroke="#caa94a")
    f.append(note)
    f.append(line(280 + nw / 2 + 4, 364, 594, 332, color="#caa94a", sw=1.2, dash="4,4"))

    cap, _, _ = textbox(450, 492,
                        ["Rc = 0 — компенсації немає: 648…792 мкВ, залежно від того, "
                         "який вхід «жадібніший».",
                         "Rc = 9 кОм — обидва входи бачать 9 кОм: лишається ±144 мкВ "
                         "= I_os·R, знак наперед невідомий."],
                        size=12.5, pad=10, fill="#f7f7f9", stroke=MUTED)
    f.append(cap)

    render(os.path.join(IMG, "math-bias-error-vs-rc.svg"), W, H, *f,
           title="Похибка на вході залежно від компенсаційного резистора")


# ── Фігура 6 (вставка hist): родовід вхідного струму ────────────────────────
def fig_lineage():
    W, H = 1040, 670
    left, right = 430, 960
    y0, step = 136, 48
    axis_y = 88
    f = []

    def xf(v):
        return left + (-6 - math.log10(v)) / 9.0 * (right - left)

    # верхня вісь-шкала: горизонтальна лінія + короткі зарубки вниз
    f.append(line(left, axis_y, right, axis_y, color=MUTED, sw=1.4))
    decs = [(1e-6, "1 мкА"), (1e-7, "100 нА"), (1e-8, "10 нА"), (1e-9, "1 нА"),
            (1e-10, "100 пА"), (1e-11, "10 пА"), (1e-12, "1 пА"),
            (1e-13, "100 фА"), (1e-14, "10 фА"), (1e-15, "1 фА")]
    for v, lab in decs:
        x = xf(v)
        f.append(line(x, axis_y, x, axis_y + 8, color=MUTED, sw=1.2))
        f.append(text(x, axis_y - 12, lab, size=11.5, color=MUTED))

    rows = [
        ("електрометрична лампа FP-54 · 1930", 1e-15, "10⁻¹⁵ А", POS),
        ("µA741 · 1968 · біполярний вхід",     8e-8,  "80 нА",   INK),
        ("LM108 · 1969 · суперβ-транзистори",  1e-9,  "< 1 нА",  INK),
        ("варакторний міст 310/311 · 1970-ті", 1e-14, "10 фА",   NEG),
        ("OP07 · 1975 · скасування струму",    4e-9,  "±4 нА",   INK),
        ("LF356 · BI-FET · JFET-вхід",         3e-11, "30 пА",   FIELD),
        ("AD549 · Topgate JFET",               6e-14, "60 фА",   FIELD),
        ("LMP7721 · 2008 · CMOS-вхід",         3e-15, "3 фА",    FIELD),
        ("ADA4530-1 · 2016 · guard на кристалі", 2e-14, "±20 фА", FIELD),
    ]
    for i, (lab, v, val, col) in enumerate(rows):
        y = y0 + i * step
        f.append(text(left - 20, y + 5, lab, size=13, color=INK, anchor="end"))
        x = xf(v)
        f.append(line(left - 12, y, x, y, color="#d7dbe0", sw=1.2, dash="4,4"))
        f.append(circle(x, y, 7, fill=col, stroke=col, sw=1.5))
        f.append(text(x, y - 13, val, size=12, color=col, bold=True))

    note, nw, nh = textbox(
        520, 600,
        ["Електрометрична лампа 1930 року вже тримала 10⁻¹⁵ А —",
         "менше, ніж будь-який серійний ОП аж до 1980-х років."],
        size=13, pad=12, fill="#fffdf5", stroke="#caa94a")
    f.append(note)

    render(os.path.join(IMG, "bias-current-lineage.svg"), W, H, *f,
           title="Родовід вхідного струму: від електрометричної лампи до фемтоамперних ОП")


# ── Фігура 7 (вставка hist): утеча в змінний струм ──────────────────────────
def fig_ac_escape():
    W, H = 1020, 360
    bw, bh, gap = 168, 108, 32
    x0, ytop = 26, 92
    f = []

    boxes = [
        ["джерело сигналу", "~10⁻¹⁵ А"],
        ["модулятор:", "вібраційний", "конденсатор,", "варактор,", "чоппер"],
        ["підсилювач", "змінного струму"],
        ["синхронний", "детектор"],
        ["вихід:", "постійна напруга"],
    ]
    centers = []
    for i, lines in enumerate(boxes):
        x = x0 + i * (bw + gap)
        centers.append(x + bw / 2.0)
        fill = "#eaf5ee" if i in (1, 3) else FILL
        f.append(fitbox(x, ytop, bw, bh, lines, size=13, pad=10, fill=fill))
        if i:
            f.append(arrow(x - gap + 3, ytop + bh / 2.0, x - 4, ytop + bh / 2.0))

    f.append(text(centers[1], ytop + bh + 32, "постійне → змінне",
                  size=12, color=FIELD, bold=True))
    f.append(text(centers[3], ytop + bh + 32, "змінне → постійне",
                  size=12, color=FIELD, bold=True))

    f.append(text(centers[1], 58, "нижній поріг задає витік самого модулятора",
                  size=11.5, color=POS))
    f.append(arrow(centers[1], 66, centers[1], ytop - 4, color=POS))

    cap, cw, ch = textbox(
        510, 292,
        ["Зсув і дрейф підсилювача сидять на постійному струмі, а сигнал уже на змінному —",
         "тож похибки підсилювача його не торкаються. Ціна — несуча, смуга і зайва механіка."],
        size=13, pad=12, fill="#f7f7f9", stroke=MUTED)
    f.append(cap)

    render(os.path.join(IMG, "dc-to-ac-escape.svg"), W, H, *f,
           title="Утеча в змінний струм: як обійти власний струм входу")


# ── Фігура (вставка proj): карта вибору входу за опором джерела ──────────────
# Модель зі зрівняними опорами на входах: E(R) = V_os(T) + I_os(T)·R,
# паспортні МАКСИМУМИ; T_flat — температура, вище якої струм подвоюється / 10 °C.
BUDGET_AMPS = [
    # назва,                 Vos25,  TCVos,    Ios25,   T_flat, колір
    ("µA741",                6e-3,   20e-6,    200e-9,  None,   MUTED),
    ("OP07E",                75e-6,  1.3e-6,   3.8e-9,  None,   "#8a6d1f"),
    ("LF356 (BiFET)",        10e-3,  5e-6,     50e-12,  25.0,   FIELD),
    ("OPA333 (чопер)",       10e-6,  0.05e-6,  400e-12, 85.0,   NEG),
    ("ADA4530-1 (електрометр)", 50e-6, 0.13e-6, 40e-15, 85.0,   POS),
]


def _budget_err(amp, R, T):
    _, vos, tc, ios, tflat, _ = amp
    k = 1.0 if tflat is None or T <= tflat else 2.0 ** ((T - tflat) / 10.0)
    return vos + tc * abs(T - 25.0) + ios * k * R


def fig_choice_map():
    W, H = 1060, 1010
    xmin, xmax = 1e2, 1e9          # опір, Ом
    ymin, ymax = 1e-6, 1e1         # похибка, В
    left, right = 152, 1012
    pw, ph = right - left, 296
    lgx = math.log10(xmax) - math.log10(xmin)
    lgy = math.log10(ymax) - math.log10(ymin)

    def xf(R):
        return left + (math.log10(R) - math.log10(xmin)) / lgx * pw

    def panel(top, T, ptitle, zone_note):
        bot = top + ph

        def yf(v):
            return top + (math.log10(ymax) - math.log10(max(v, ymin))) / lgy * ph

        p = [text(left, top - 14, ptitle, size=15, bold=True, anchor="start")]
        p.append(rect(left, top, pw, ph, fill="#fff", stroke=MUTED, sw=1.4))
        for v, lab in ((1e-6, "1 мкВ"), (1e-5, "10 мкВ"), (1e-4, "100 мкВ"), (1e-3, "1 мВ"),
                       (1e-2, "10 мВ"), (1e-1, "100 мВ"), (1e0, "1 В"), (1e1, "10 В")):
            y = yf(v)
            p.append(line(left, y, right, y, color="#e9ebef", sw=1))
            p.append(text(left - 12, y + 4, lab, size=12, color=MUTED, anchor="end"))
        for v, lab in ((1e2, "100 Ом"), (1e3, "1 кОм"), (1e4, "10 кОм"), (1e5, "100 кОм"),
                       (1e6, "1 МОм"), (1e7, "10 МОм"), (1e8, "100 МОм"), (1e9, "1 ГОм")):
            x = xf(v)
            p.append(line(x, top, x, bot, color="#e9ebef", sw=1))
            p.append(line(x, bot, x, bot + 6, color=MUTED, sw=1.2))
            p.append(text(x, bot + 22, lab, size=12, color=MUTED))

        for amp in BUDGET_AMPS:                       # криві, відсічені зверху
            pts = []
            for i in range(141):
                R = 10 ** (math.log10(xmin) + i * lgx / 140.0)
                e = _budget_err(amp, R, T)
                if e > ymax:
                    break
                pts.append((xf(R), yf(e)))
            if len(pts) > 1:
                p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                         % (" ".join("%.1f,%.1f" % q for q in pts), amp[5]))

        Rx = 1e5                                      # перетин чопера й електрометра
        sy, sh = bot + 38, 22
        p.append(rect(left, sy, xf(Rx) - left, sh, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=3))
        p.append(text((left + xf(Rx)) / 2, sy + 15, "виграє чопер", size=12.5, color=NEG, bold=True))
        p.append(rect(xf(Rx), sy, right - xf(Rx), sh, fill="#fdecea", stroke=POS, sw=1.2, rx=3))
        p.append(text((xf(Rx) + right) / 2, sy + 15, "виграє електрометр", size=12.5,
                      color=POS, bold=True))
        p.append(text(left, sy + 48, zone_note, size=12.5, color=INK, anchor="start"))
        return "".join(p)

    # спільна легенда — над панелями, поза полем графіка (щоб не лягала на сітку)
    leg = []
    lx = left - 2
    for name, _, _, _, _, col in BUDGET_AMPS:
        leg.append(line(lx, 54, lx + 30, 54, color=col, sw=3.4))
        leg.append(text(lx + 38, 58, name, size=12.5, color=INK, anchor="start"))
        lx += 30 + 38 + text_width(name, 12.5) * 0.92 + 18

    f = [text(W / 2, 88, "опір, який бачать обидва входи (зрівняні: R⁺ = R⁻ = R)",
              size=13.5, color=INK)]
    f.extend(leg)
    f.append(panel(132, 25.0, "25 °C — кімната",
                   "Злам кривої стоїть на R* = V_os / I_os: ліворуч панує зсув напруги, "
                   "праворуч — струм неузгодженості."))
    f.append(panel(592, 85.0, "85 °C — гаряча техніка",
                   "Витік JFET-затвора виріс у 64 рази — крива BiFET піднялася вище "
                   "за прецизійний біполярний вхід."))
    render(os.path.join(IMG, "dc-error-vs-source-resistance.svg"), W, H, *f,
           title="Сумарна DC-похибка проти опору джерела: чий вхід брати")


if __name__ == "__main__":
    fig_origin()
    fig_compensation()
    fig_temperature()
    fig_derivation_map()
    fig_error_vs_rc()
    fig_lineage()
    fig_ac_escape()
    fig_choice_map()
    print("OK: figures written to", IMG)
