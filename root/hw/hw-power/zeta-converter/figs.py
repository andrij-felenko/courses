# -*- coding: utf-8 -*-
"""Фігури до теми «Zeta-перетворювач».
Запуск: python figs.py  → генерує SVG у теці ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

COIL = "#b5763a"   # мідний колір індуктивностей


# ── Спільні символи схеми ───────────────────────────────────────────────────
def vsource(cx, cy, label="Vвх", color=POS):
    out = [circle(cx, cy, 10, fill=BG, stroke=color, sw=2.2)]
    out.append(line(cx - 5, cy, cx + 5, cy, color=color, sw=2.2))
    out.append(line(cx, cy - 5, cx, cy + 5, color=color, sw=2.2))
    out.append(text(cx, cy - 22, label, size=13, bold=True))
    return "".join(out)


def coil_h(x1, x2, y, color=COIL, sw=2.8):
    n = 4
    step = (x2 - x1) / n
    r = step / 2
    d = "M %.1f %.1f " % (x1, y)
    for i in range(n):
        cx0 = x1 + step * i
        d += "A %.1f %.1f 0 0 1 %.1f %.1f " % (r, 10.0, cx0 + step, y)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, color, sw)


def coil_v(x, y1, y2, color=COIL, sw=2.8):
    n = 4
    step = (y2 - y1) / n
    r = step / 2
    d = "M %.1f %.1f " % (x, y1)
    for i in range(n):
        cy0 = y1 + step * i
        d += "A %.1f %.1f 0 0 1 %.1f %.1f " % (10.0, r, x, cy0 + step)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, color, sw)


def diode_v(x, y_top, y_bot, color=INK, sw=2.0):
    """Діод вертикальний: анод знизу (y_bot), катод зверху (y_top)."""
    midy = (y_top + y_bot) / 2
    out = [line(x, y_bot, x, midy + 11, color=color, sw=sw)]
    out.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="none" '
               'stroke="%s" stroke-width="%.1f"/>' % (x - 11, midy + 11, x + 11, midy + 11, x, midy - 11, color, sw))
    out.append(line(x - 11, midy - 11, x + 11, midy - 11, color=color, sw=sw + 0.6))
    out.append(line(x, midy - 11, x, y_top, color=color, sw=sw))
    return "".join(out)


def cap_v(cx, y_top, y_bot, color=INK, sw=2.0):
    midhi, midlo = (y_top + y_bot) / 2 - 6, (y_top + y_bot) / 2 + 6
    out = [line(cx, y_top, cx, midhi, color=color, sw=sw)]
    out.append(line(cx - 15, midhi, cx + 15, midhi, color=color, sw=sw + 0.6))
    out.append(line(cx - 15, midlo, cx + 15, midlo, color=color, sw=sw + 0.6))
    out.append(line(cx, midlo, cx, y_bot, color=color, sw=sw))
    return "".join(out)


def cap_h(x_l, x_r, y, color=INK, sw=2.0):
    midl, midr = (x_l + x_r) / 2 - 6, (x_l + x_r) / 2 + 6
    out = [line(x_l, y, midl, y, color=color, sw=sw)]
    out.append(line(midl, y - 15, midl, y + 15, color=color, sw=sw + 0.6))
    out.append(line(midr, y - 15, midr, y + 15, color=color, sw=sw + 0.6))
    out.append(line(midr, y, x_r, y, color=color, sw=sw))
    return "".join(out)


def load_resistor(x, y_top, y_bot, color=INK, sw=1.8):
    out = [line(x, y_top, x, y_top + 12, color=color, sw=sw)]
    out.append(rect(x - 11, y_top + 12, 22, 50, fill="none", stroke=color, sw=sw, rx=0))
    out.append(line(x, y_top + 62, x, y_bot, color=color, sw=sw))
    return "".join(out)


def switch_h(x1, x2, y, on=True, label="Q1", color=INK):
    cx = (x1 + x2) / 2
    out = [line(x1, y, cx - 13, y, color=color, sw=2)]
    out.append(rect(cx - 13, y - 13, 26, 26, fill=BG, stroke=color, sw=1.8, rx=4))
    if on:
        out.append(line(cx - 8, y, cx + 8, y, color=color, sw=3.0))
    else:
        out.append(line(cx - 8, y + 6, cx + 8, y - 6, color=color, sw=2.4))
    out.append(line(cx + 13, y, x2, y, color=color, sw=2))
    if label:
        out.append(text(cx, y - 20, label, size=12, color=color, bold=True))
    return "".join(out)


# ── Фігура 1: Принципова схема Zeta-перетворювача ───────────────────────────
def fig_topology():
    W, H = 960, 450
    f = [text(W / 2, 30, "Топологія Zeta: неінвертувальний перетворювач із неперервним вихідним струмом", size=16, bold=True)]
    out = []
    yt, yb = 160, 330
    vx = 70

    # Джерело живлення
    out.append(vsource(vx, yt))
    out.append(line(vx, yt + 10, vx, yb, color=INK, sw=2))

    # Верхній ключ Q1
    out.append(switch_h(vx, 210, yt, on=True, label="Ключ Q1 (High-Side)", color=INK))

    # Вузол SW1
    sw1_x = 240
    out.append(line(210, yt, sw1_x, yt, color=INK, sw=2))
    out.append(circle(sw1_x, yt, 4, fill=POS, stroke=POS, sw=0))
    out.append(text(sw1_x, yt - 18, "SW1", size=13, color=POS, bold=True))

    # Індуктивність L1 на землю
    out.append(coil_v(sw1_x, yt, yb - 8, color=COIL, sw=2.8))
    out.append(line(sw1_x, yb - 8, sw1_x, yb, color=INK, sw=2))
    out.append(text(sw1_x - 22, (yt + yb) / 2, "L1", size=13, color=COIL, bold=True, anchor="end"))

    # Розділовий конденсатор Cc
    sw2_x = 450
    out.append(cap_h(sw1_x, sw2_x, yt, color=NEG, sw=2.2))
    out.append(text((sw1_x + sw2_x) / 2, yt - 20, "Cc (розділовий)", size=13, color=NEG, bold=True))
    out.append(text((sw1_x + sw2_x) / 2, yt + 26, "⟨V_Cc⟩ = Vвих", size=11, color=NEG, bold=True))

    # Вузол SW2
    out.append(circle(sw2_x, yt, 4, fill=FIELD, stroke=FIELD, sw=0))
    out.append(text(sw2_x, yt - 18, "SW2", size=13, color=FIELD, bold=True))

    # Діод D1 (анод на GND, катод на SW2)
    out.append(diode_v(sw2_x, yt, yb, color=INK, sw=2.0))
    out.append(text(sw2_x - 22, (yt + yb) / 2, "D1", size=13, color=INK, bold=True, anchor="end"))

    # Вихідна індуктивність L2
    out_node_x = 650
    out.append(coil_h(sw2_x, out_node_x, yt, color=COIL, sw=2.8))
    out.append(text((sw2_x + out_node_x) / 2, yt - 18, "L2 (вихідний дросель)", size=13, color=COIL, bold=True))

    # Вузол виходу
    out.append(circle(out_node_x, yt, 4, fill=POS, stroke=POS, sw=0))

    # Вихідний конденсатор Cout
    out.append(cap_v(out_node_x, yt, yb, color=INK, sw=2.0))
    out.append(text(out_node_x + 18, (yt + yb) / 2, "Свих", size=12, color=MUTED, anchor="start"))

    # Навантаження
    load_x = 760
    out.append(line(out_node_x, yt, load_x, yt, color=INK, sw=2))
    out.append(load_resistor(load_x, yt, yb, color=INK, sw=1.8))
    out.append(text(load_x + 18, (yt + yb) / 2, "Rнав", size=12, color=MUTED, anchor="start"))
    out.append(text(load_x, yt - 18, "+Vвих > 0", size=13, color=POS, bold=True))

    # Земля
    out.append(line(vx, yb, load_x, yb, color=INK, sw=2))
    out.append(text((vx + load_x) / 2, yb + 20, "Спільна земля (GND, 0 В)", size=11, color=MUTED))

    # Пояснювальний блок
    out.append(fitbox(50, 375, 860, 52,
                      "Zeta є дуалом SEPIC: вихідна котушка L2 увімкнена послідовно з виходом (як у знижувачі Buck), "
                      "забезпечуючи неперервний вихідний струм і наднизькі пульсації напруги на навантаженні.\n"
                      "Проміжний конденсатор Cc ізолює постійний струм між портами та заряджений до напруги V_Cc = Vвих.",
                      size=11, fill="#eef8ef", stroke=FIELD))
    f.extend(out)
    render(os.path.join(IMG, "topology.svg"), W, H, *f)


# ── Фігура 2: Два такти комутації Zeta ───────────────────────────────────────
def fig_two_phases():
    W, H = 980, 500
    f = [text(W / 2, 28, "Два комутаційні стани Zeta-перетворювача в режимі CCM", size=16, bold=True)]

    def draw_phase(x0, title, color_title, is_phase1):
        act = FIELD
        idle = "#c7ccd2"
        out = [rect(x0, 50, 460, 360, fill="none", stroke="#d8dde3", sw=2, rx=10)]
        out.append(text(x0 + 230, 78, title, size=13, color=color_title, bold=True))

        yt, yb = 180, 320
        vx = x0 + 35

        # Джерело
        out.append(vsource(vx, yt))
        out.append(line(vx, yt + 10, vx, yb, color=INK, sw=2))

        # Ключ Q1
        q_col = act if is_phase1 else idle
        out.append(switch_h(vx, x0 + 130, yt, on=is_phase1, label="Q1", color=q_col))

        # SW1
        sw1_x = x0 + 150
        out.append(line(x0 + 130, yt, sw1_x, yt, color=q_col, sw=2))
        out.append(circle(sw1_x, yt, 3.5, fill=INK, stroke=INK, sw=0))

        # L1
        out.append(coil_v(sw1_x, yt, yb - 8, color=act, sw=2.8))
        out.append(line(sw1_x, yb - 8, sw1_x, yb, color=act, sw=2))
        out.append(text(sw1_x - 14, (yt + yb) / 2, "L1", size=11, color=COIL, anchor="end", bold=True))

        # Cc
        sw2_x = x0 + 270
        out.append(cap_h(sw1_x, sw2_x, yt, color=POS, sw=2))
        out.append(text((sw1_x + sw2_x) / 2, yt - 18, "Cc", size=11, color=POS, bold=True))

        # SW2
        out.append(circle(sw2_x, yt, 3.5, fill=INK, stroke=INK, sw=0))

        # D1
        d_col = idle if is_phase1 else act
        out.append(diode_v(sw2_x, yt, yb, color=d_col, sw=2))
        out.append(text(sw2_x - 14, (yt + yb) / 2, "D1", size=11, color=d_col, anchor="end", bold=True))

        # L2
        out_x = x0 + 370
        out.append(coil_h(sw2_x, out_x, yt, color=act, sw=2.8))
        out.append(text((sw2_x + out_x) / 2, yt - 16, "L2", size=11, color=COIL, bold=True))

        # Cout і навантаження
        out.append(circle(out_x, yt, 3.5, fill=INK, stroke=INK, sw=0))
        out.append(cap_v(out_x, yt, yb, color=INK, sw=2))
        load_x = x0 + 420
        out.append(line(out_x, yt, load_x, yt, color=INK, sw=2))
        out.append(load_resistor(load_x, yt, yb, color=INK, sw=1.8))
        out.append(line(vx, yb, load_x, yb, color=INK, sw=2))

        if is_phase1:
            desc = "Фаза 1 (Q1 замкнено, D1 закрито):\n" \
                   "• v_L1 = +Vвх (струм i_L1 зростає)\n" \
                   "• v_SW2 = Vвх + Vвих, D1 закритий напругою -(Vвх+Vвих)\n" \
                   "• v_L2 = +Vвх (Cc розряджається в L2 та вихід)"
        else:
            desc = "Фаза 2 (Q1 розімкнено, D1 відкрито):\n" \
                   "• v_SW2 = 0 В (діод D1 фіксує вузол на землі)\n" \
                   "• v_L2 = -Vвих (L2 віддає енергію в навантаження)\n" \
                   "• v_SW1 = -Vвих, v_L1 = -Vвих (L1 дозаряджає Cc)"
        out.append(fitbox(x0 + 12, 335, 436, 68, desc, size=11, fill="#fbfcfd", stroke="#d8dde3"))
        return "".join(out)

    f.append(draw_phase(20, "ФАЗА 1: Ключ Q1 ON (інтервал D · T)", FIELD, True))
    f.append(draw_phase(500, "ФАЗА 2: Ключ Q1 OFF (інтервал (1−D) · T)", INK, False))
    f.append(fitbox(40, 425, 900, 48,
                    "В обох фазах струм котушки L2 безперервно протікає у вихідний вузол. "
                    "У Фазі 1 обидві індуктивності L1 і L2 бачать напругу +Vвх, а у Фазі 2 — напругу -Vвих. "
                    "Ідентичність змінних напруг дозволяє об'єднати L1 та L2 на єдиному магнітному осерді.",
                    size=11, fill="#eef8ef", stroke=FIELD))

    render(os.path.join(IMG, "two-phases.svg"), W, H, *f)


# ── Фігура 3: Часові епюри струмів і напруг ──────────────────────────────────
def fig_waveforms():
    W, H = 960, 680
    f = [text(W / 2, 26, "Часові епюри струмів і напруг у перетворювачі Zeta (CCM)", size=16, bold=True)]

    X0, PW = 140.0, 480.0
    D = 0.45
    XS = X0 + PW * D
    XE = X0 + PW
    X2 = XE + PW * D
    X3 = XE + PW

    # Вертикальні розділові лінії тактів
    for xx in (X0, XS, XE, X2, X3):
        f.append(line(xx, 50, xx, 600, color="#d8dde3", sw=1.2, dash="4 4"))

    # Позначення тактів угорі
    f.append(text((X0 + XS) / 2, 45, "D·T (Q1 ON)", size=11, color=FIELD, bold=True))
    f.append(text((XS + XE) / 2, 45, "(1−D)·T (Q1 OFF)", size=11, color=MUTED, bold=True))
    f.append(text((XE + X2) / 2, 45, "D·T", size=11, color=FIELD, bold=True))
    f.append(text((X2 + X3) / 2, 45, "(1−D)·T", size=11, color=MUTED, bold=True))

    def plot_row(y_base, label, sub_label, color, draw_func):
        out = [line(X0 - 10, y_base, X3 + 20, y_base, color=INK, sw=1.4)]
        out.append(text(X0 - 15, y_base - 8, label, size=13, color=color, anchor="end", bold=True))
        out.append(text(X0 - 15, y_base + 12, sub_label, size=10, color=MUTED, anchor="end"))
        out.append(draw_func(y_base))
        return "".join(out)

    # 1. v_SW1: Vвх при ON, -Vвих при OFF
    def wave_sw1(yb):
        h_pos, h_neg = 24.0, 16.0
        p = ["M %.1f %.1f" % (X0, yb - h_pos)]
        p.append("L %.1f %.1f L %.1f %.1f" % (XS, yb - h_pos, XS, yb + h_neg))
        p.append("L %.1f %.1f L %.1f %.1f" % (XE, yb + h_neg, XE, yb - h_pos))
        p.append("L %.1f %.1f L %.1f %.1f" % (X2, yb - h_pos, X2, yb + h_neg))
        p.append("L %.1f %.1f" % (X3, yb + h_neg))
        s = ['<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(p), POS)]
        s.append(text(X0 + 30, yb - h_pos - 4, "+Vвх", size=10, color=POS))
        s.append(text(XS + 30, yb + h_neg + 12, "−Vвих", size=10, color=NEG))
        return "".join(s)

    # 2. v_SW2: Vвх+Vвих при ON, 0 при OFF
    def wave_sw2(yb):
        h_top = 34.0
        p = ["M %.1f %.1f" % (X0, yb - h_top)]
        p.append("L %.1f %.1f L %.1f %.1f" % (XS, yb - h_top, XS, yb))
        p.append("L %.1f %.1f L %.1f %.1f" % (XE, yb, XE, yb - h_top))
        p.append("L %.1f %.1f L %.1f %.1f" % (X2, yb - h_top, X2, yb))
        p.append("L %.1f %.1f" % (X3, yb))
        s = ['<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(p), FIELD)]
        s.append(text(X0 + 30, yb - h_top - 4, "Vвх + Vвих", size=10, color=FIELD))
        return "".join(s)

    # 3. i_L1: трикутник навколо Івх
    def wave_il1(yb):
        y_mid = yb - 18
        dy = 12
        p = ["M %.1f %.1f" % (X0, y_mid + dy)]
        p.append("L %.1f %.1f L %.1f %.1f" % (XS, y_mid - dy, XE, y_mid + dy))
        p.append("L %.1f %.1f L %.1f %.1f" % (X2, y_mid - dy, X3, y_mid + dy))
        s = ['<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(p), COIL)]
        s.append(line(X0, y_mid, X3, y_mid, color=MUTED, sw=1.0, dash="3 3"))
        s.append(text(X3 + 10, y_mid + 4, "⟨i_L1⟩ = Івх", size=10, color=COIL, anchor="start"))
        return "".join(s)

    # 4. i_L2: неперервний трикутник навколо Івих
    def wave_il2(yb):
        y_mid = yb - 20
        dy = 10
        p = ["M %.1f %.1f" % (X0, y_mid + dy)]
        p.append("L %.1f %.1f L %.1f %.1f" % (XS, y_mid - dy, XE, y_mid + dy))
        p.append("L %.1f %.1f L %.1f %.1f" % (X2, y_mid - dy, X3, y_mid + dy))
        s = ['<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(p), FIELD)]
        s.append(line(X0, y_mid, X3, y_mid, color=MUTED, sw=1.0, dash="3 3"))
        s.append(text(X3 + 10, y_mid + 4, "⟨i_L2⟩ = Івих (НЕПЕРЕРВНИЙ)", size=10.5, color=FIELD, bold=True, anchor="start"))
        return "".join(s)

    # 5. i_Cc: -Івих при ON, +Івх при OFF
    def wave_icc(yb):
        h_pos, h_neg = 16.0, 20.0
        p = ["M %.1f %.1f" % (X0, yb + h_neg)]
        p.append("L %.1f %.1f L %.1f %.1f" % (XS, yb + h_neg, XS, yb - h_pos))
        p.append("L %.1f %.1f L %.1f %.1f" % (XE, yb - h_pos, XE, yb + h_neg))
        p.append("L %.1f %.1f L %.1f %.1f" % (X2, yb + h_neg, X2, yb - h_pos))
        p.append("L %.1f %.1f" % (X3, yb - h_pos))
        s = ['<path d="%s" fill="none" stroke="%s" stroke-width="2.0"/>' % (" ".join(p), NEG)]
        s.append(text(X0 + 30, yb + h_neg + 12, "−Івих", size=10, color=NEG))
        s.append(text(XS + 30, yb - h_pos - 4, "+Івх", size=10, color=POS))
        return "".join(s)

    # 6. i_Q1: струм ключа (імпульсний)
    def wave_iq1(yb):
        h_top = 28.0
        p = ["M %.1f %.1f" % (X0, yb)]
        p.append("L %.1f %.1f L %.1f %.1f L %.1f %.1f" % (X0, yb - h_top + 4, XS, yb - h_top - 4, XS, yb))
        p.append("L %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f" % (XE, yb, XE, yb - h_top + 4, X2, yb - h_top - 4, X2, yb))
        p.append("L %.1f %.1f" % (X3, yb))
        s = ['<path d="%s" fill="none" stroke="%s" stroke-width="2.0"/>' % (" ".join(p), INK)]
        s.append(text(X0 + 30, yb - h_top - 4, "i_L1 + i_L2", size=10, color=INK))
        return "".join(s)

    f.append(plot_row(115, "v_SW1", "Вузол 1", POS, wave_sw1))
    f.append(plot_row(205, "v_SW2", "Вузол 2", FIELD, wave_sw2))
    f.append(plot_row(300, "i_L1", "Котушка L1", COIL, wave_il1))
    f.append(plot_row(395, "i_L2", "Вихід L2", FIELD, wave_il2))
    f.append(plot_row(490, "i_Cc", "Конденсатор Cc", NEG, wave_icc))
    f.append(plot_row(580, "i_Q1", "Ключ Q1", INK, wave_iq1))

    f.append(fitbox(50, 615, 860, 48,
                    "Ключова перевага: струм i_L2 є абсолютно гладким і неперервним, без розривів комутації. "
                    "Вхідний струм ключа i_Q1 та діода i_D1 є переривчастим із амплітудою Івх + Івих.",
                    size=11, fill="#eef8ef", stroke=FIELD))

    render(os.path.join(IMG, "waveforms.svg"), W, H, *f)


# ── Фігура 4: Порівняння топологій (Stress Comparison) ──────────────────────
def fig_stress_comparison():
    W, H = 960, 520
    f = [text(W / 2, 28, "Порівняння топологій: напруга, струм та полярність", size=16, bold=True)]

    headers = ["Топологія", "Полярність", "Вхідний струм", "Вихідний струм", "Напруга на ключах", "Напруга на Cc / C1"]
    cols_x = [30, 160, 270, 420, 580, 750, 930]

    # Шапка таблиці
    f.append(rect(30, 50, 900, 36, fill="#2c3e50", stroke="#2c3e50", sw=0, rx=4))
    for i, h in enumerate(headers):
        cx = (cols_x[i] + cols_x[i + 1]) / 2
        f.append(text(cx, 73, h, size=11.5, color=BG, bold=True))

    rows = [
        ("Buck", "Додатна (+)", "Переривчастий", "Неперервний", "Vвх", "—", False),
        ("Boost", "Додатна (+)", "Неперервний", "Переривчастий", "Vвих", "—", False),
        ("Buck-Boost", "Інвертована (−)", "Переривчастий", "Переривчастий", "Vвх + |Vвих|", "—", False),
        ("SEPIC", "Додатна (+)", "Неперервний", "Переривчастий", "Vвх + Vвих", "V_Cs = Vвх", False),
        ("Ćuk", "Інвертована (−)", "Неперервний", "Неперервний", "Vвх + |Vвих|", "V_C1 = Vвх + |Vвих|", False),
        ("Zeta", "Додатна (+)", "Переривчастий", "Неперервний", "Vвх + Vвих", "V_Cc = Vвих", True),
    ]

    y = 90
    for name, pol, i_in, i_out, v_sw, v_c, is_zeta in rows:
        bg_col = "#eef8ef" if is_zeta else (BG if (rows.index((name, pol, i_in, i_out, v_sw, v_c, is_zeta)) % 2 == 0) else "#f8fafc")
        border_col = FIELD if is_zeta else "#e2e8f0"
        sw = 2 if is_zeta else 1

        f.append(rect(30, y, 900, 42, fill=bg_col, stroke=border_col, sw=sw, rx=4))

        vals = [name, pol, i_in, i_out, v_sw, v_c]
        for i, val in enumerate(vals):
            cx = (cols_x[i] + cols_x[i + 1]) / 2
            col = FIELD if is_zeta else (POS if "-" in val or "Інверт" in val else INK)
            b = True if is_zeta or i == 0 else False
            f.append(text(cx, y + 26, val, size=11, color=col, bold=b))
        y += 46

    f.append(fitbox(30, 395, 900, 100,
                    "Чому обирають Zeta замість SEPIC та Ćuk:\n"
                    "1. Порівняно з SEPIC: вихідний струм неперервний, що усуває імпульсний удар по вихідному конденсатору та дає у 10–25 разів менші пульсації напруги.\n"
                    "2. Порівняно з Ćuk: зберігається пряма (додатна) полярність вихідної напруги без потреби інвертувати шину.\n"
                    "3. Напруга на проміжному конденсаторі становить лише Vвих (у SEPIC — Vвх, у Ćuk — Vвх + Vвих), що критично вигідно при високих вхідних напругах.",
                    size=11, fill="#f4f6f8", stroke=MUTED))

    render(os.path.join(IMG, "stress-comparison.svg"), W, H, *f)


# ── Фігура 5: Зв'язані індуктивності та керування пульсаціями ──────────────
def fig_coupled_core():
    W, H = 960, 460
    f = [text(W / 2, 28, "Магнітне об'єднання L1 та L2 на спільному осерді (Ripple Steering)", size=16, bold=True)]

    # Осердя дроселя
    # Спрощена і чиста геометрія осердя з двома окремими кернами
    core_left = 60
    core_top = 80
    core_w = 340
    core_h = 270

    # Зовнішній контур
    f.append(rect(core_left, core_top, core_w, core_h, fill="#4a5568", stroke="#2d3748", sw=2, rx=8))
    # Внутрішнє вікно осердя
    f.append(rect(core_left + 80, core_top + 45, core_w - 160, core_h - 90, fill=BG, stroke="#2d3748", sw=2, rx=4))

    # Позначення зазору у центральній області (верхнє/нижнє ярмо суцільне)
    # Позначимо немагнітний зазор на правому стовпчику
    gap_y = core_top + core_h / 2
    f.append(rect(core_left + core_w - 75, gap_y - 6, 70, 12, fill="#e2e8f0", stroke="#a0aec0", sw=1, rx=0))
    f.append(text(core_left + core_w - 40, gap_y + 4, "зазор g", size=10, color="#2d3748", bold=True))

    # Обмотка 1 (L1) - накладений ізольований блок ззовні лівого керна
    f.append(rect(core_left + 10, core_top + 50, 60, 160, fill="#b5763a", stroke="#8c4b1d", sw=2, rx=6))
    f.append(text(core_left + 40, core_top + 130, "Обмотка L1", size=11, color=BG, bold=True))
    f.append(text(core_left + 40, core_top + 150, "N1 витків", size=10, color=BG))
    # Крапка початку фази L1
    f.append(circle(core_left + 25, core_top + 65, 4, fill=POS, stroke=POS, sw=0))

    # Обмотка 2 (L2) - накладений блок на правому керні
    f.append(rect(core_left + core_w - 70, core_top + 50, 60, 60, fill="#b5763a", stroke="#8c4b1d", sw=2, rx=6))
    f.append(text(core_left + core_w - 40, core_top + 80, "L2 (верх)", size=10, color=BG, bold=True))
    # Крапка початку фази L2
    f.append(circle(core_left + core_w - 55, core_top + 62, 4, fill=POS, stroke=POS, sw=0))

    f.append(rect(core_left + core_w - 70, core_top + 150, 60, 60, fill="#b5763a", stroke="#8c4b1d", sw=2, rx=6))
    f.append(text(core_left + core_w - 40, core_top + 180, "L2 (низ)", size=10, color=BG, bold=True))

    # Стрілка магнітного потоку у вікні
    f.append(text(core_left + 170, core_top + 130, "Магнітний потік Φ", size=11, color="#4a5568", bold=True))
    f.append(text(core_left + 170, core_top + 150, "Спільне осердя", size=10, color=MUTED))

    # Текстова панель праворуч
    panel_x = 430
    f.append(rect(panel_x, 60, 500, 310, fill="#fbfcfd", stroke="#d8dde3", sw=1.8, rx=8))
    f.append(text(panel_x + 250, 88, "Фізика явища керування пульсаціями", size=13, color=INK, bold=True))

    lines = [
        "1. Змінна напруга на обох обмотках строго однакова щомиті:",
        "   v_L1(t) = v_L2(t) = +Vвх (у Фазі 1),  −Vвих (у Фазі 2).",
        "",
        "2. Рівняння струмів через взаємоіндуктивність M = k·√(L1·L2):",
        "   di_L2 / dt = (L1 · v_L2 − M · v_L1) / (L1·L2 − M²)",
        "              = v_ac · (L1 − M) / [L1·L2 · (1 − k²)]",
        "",
        "3. При виборі співвідношення витків n = N2/N1 = k:",
        "   Чисельник перетворюється на точний нуль: di_L2 / dt = 0!",
        "",
        "4. Результат: пульсація вихідного струму Δi_L2 спадає до 0,",
        "   а вся змінна складова перенаправляється у вхідний дросель L1."
    ]

    ty = 114
    for ln in lines:
        col = FIELD if "di_L2 / dt = 0" in ln or "n = N2/N1 = k" in ln or "Результат:" in ln else INK
        b = True if "di_L2 / dt = 0" in ln or "Результат:" in ln else False
        f.append(text(panel_x + 18, ty, ln, size=10.5, color=col, anchor="start", bold=b))
        ty += 18

    f.append(fitbox(30, 385, 900, 56,
                    "Об'єднання індуктивностей на єдиному осерді скорочує габарити друкованої плати вдвічі. "
                    "Завдяки ефекту ripple steering вихідний струм стає абсолютно гладким постійним струмом, "
                    "що робить перетворювач Zeta рекордсменом за чистотою вихідного живлення серед усіх комбінованих топологій.",
                    size=11, fill="#eef8ef", stroke=FIELD))

    render(os.path.join(IMG, "coupled-core.svg"), W, H, *f)


if __name__ == "__main__":
    fig_topology()
    fig_two_phases()
    fig_waveforms()
    fig_stress_comparison()
    fig_coupled_core()
    print("OK: 5 фігур успішно згенеровано в", IMG)
