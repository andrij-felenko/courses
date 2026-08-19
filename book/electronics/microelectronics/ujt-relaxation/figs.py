# -*- coding: utf-8 -*-
"""Генератор фігур до теми «Одноперехідний транзистор (UJT) і релаксаційний генератор».
Створює 7 SVG-ілюстрацій у ./img/:
  1. ujt-structure-cross-section.svg — Фізична будова монокристалічного UJT
  2. ujt-equivalent-circuit.svg      — Еквівалентна електрична схема UJT
  3. ujt-emitter-iv-curve.svg        — Вольт-амперна характеристика емітера з ділянкою NDR
  4. ujt-relaxation-schematic.svg    — Схема класичного релаксаційного генератора на UJT
  5. ujt-waveforms.svg               — Часові діаграми напруг (пилка VE, імпульси VB1 та VB2)
  6. ujt-scr-trigger-circuit.svg     — Схема фазоімпульсного керування тиристором/симістором
  7. put-structure-and-biasing.svg   — Програмований одноперехідний транзистор (PUT)

Запуск: python figs.py
"""
import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# ── Загальні допоміжні елементи схемотехніки ──────────────────────────────
def gnd(cx, y, label="GND"):
    """Символ заземлення."""
    out = [line(cx, y, cx, y + 7, color=LINE, sw=1.8)]
    out.append(line(cx - 14, y + 7, cx + 14, y + 7, color=LINE, sw=2.4))
    out.append(line(cx - 8, y + 12, cx + 8, y + 12, color=LINE, sw=2.0))
    out.append(line(cx - 3, y + 17, cx + 3, y + 17, color=LINE, sw=1.8))
    if label:
        out.append(text(cx, y + 31, label, size=11, color=MUTED, bold=True))
    return "".join(out)

def res_v(cx, cy, h=44, w=16, label="", side="right"):
    """Вертикальний резистор."""
    yt, yb = cy - h / 2, cy + h / 2
    out = [rect(cx - w / 2, yt, w, h, fill="#ffffff", stroke=LINE, sw=1.6, rx=2)]
    if label:
        lx = cx + w / 2 + 7 if side == "right" else cx - w / 2 - 7
        anch = "start" if side == "right" else "end"
        out.append(text(lx, cy + 4, label, size=12, color=INK, anchor=anch))
    return "".join(out), yt, yb

def res_h(cx, cy, w=44, h=16, label="", pos="top"):
    """Горизонтальний резистор."""
    xl, xr = cx - w / 2, cx + w / 2
    out = [rect(xl, cy - h / 2, w, h, fill="#ffffff", stroke=LINE, sw=1.6, rx=2)]
    if label:
        ly = cy - h / 2 - 6 if pos == "top" else cy + h / 2 + 15
        out.append(text(cx, ly, label, size=12, color=INK, anchor="middle"))
    return "".join(out), xl, xr

def cap_v(cx, cy, h=24, w=22, label="", side="right"):
    """Вертикальний конденсатор."""
    d = 7
    yt = cy - d / 2
    yb = cy + d / 2
    out = [
        line(cx - w / 2, yt, cx + w / 2, yt, color=LINE, sw=2.2),
        line(cx - w / 2, yb, cx + w / 2, yb, color=LINE, sw=2.2),
        line(cx, cy - h / 2, cx, yt, color=LINE, sw=1.6),
        line(cx, yb, cx, cy + h / 2, color=LINE, sw=1.6),
    ]
    if label:
        lx = cx + w / 2 + 7 if side == "right" else cx - w / 2 - 7
        anch = "start" if side == "right" else "end"
        out.append(text(lx, cy + 4, label, size=12, color=INK, anchor=anch))
    return "".join(out), cy - h / 2, cy + h / 2

def diode_d(cx, cy, direction="down", label=""):
    """Діод (direction: 'down', 'up', 'right')."""
    out = []
    s = 10
    if direction == "down":
        p = [(cx, cy + s), (cx - s, cy - s), (cx + s, cy - s)]
        out.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" stroke="%s" stroke-width="1.5"/>' % (
            p[0][0], p[0][1], p[1][0], p[1][1], p[2][0], p[2][1], FILL, LINE))
        out.append(line(cx - s, cy + s, cx + s, cy + s, color=LINE, sw=2.0))
        out.append(line(cx, cy - s - 10, cx, cy - s, color=LINE, sw=1.6))
        out.append(line(cx, cy + s, cx, cy + s + 10, color=LINE, sw=1.6))
    elif direction == "right":
        p = [(cx + s, cy), (cx - s, cy - s), (cx - s, cy + s)]
        out.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" stroke="%s" stroke-width="1.5"/>' % (
            p[0][0], p[0][1], p[1][0], p[1][1], p[2][0], p[2][1], FILL, LINE))
        out.append(line(cx + s, cy - s, cx + s, cy + s, color=LINE, sw=2.0))
        out.append(line(cx - s - 10, cy, cx - s, cy, color=LINE, sw=1.6))
        out.append(line(cx + s, cy, cx + s + 10, cy, color=LINE, sw=1.6))
    if label:
        out.append(text(cx + s + 6, cy + 4, label, size=12, color=INK, anchor="start"))
    return "".join(out)


# ════════════════════════════════════════════════════════════════════════════
# 1. Фізична будова UJT (ujt-structure-cross-section.svg)
# ════════════════════════════════════════════════════════════════════════════
def fig1_ujt_structure():
    w, h = 760, 480
    out = []
    
    # Заголовок блоку
    out.append(text(w / 2, 28, "Внутрішня напівпровідникова структура UJT", size=16, bold=True))
    
    # Область кристала кремнію n-типу
    bx, by, bw, bh = 220, 70, 160, 310
    out.append(rect(bx, by, bw, bh, fill="#e8f4fd", stroke=LINE, sw=2.0, rx=4))
    out.append(text(bx + bw / 2, by + 190, "Кремнієвий брусок n-типу", size=13, color=NEG, bold=True))
    out.append(text(bx + bw / 2, by + 210, "(слабко легований, опір R_BB)", size=11, color=MUTED))

    # Контакт B2 (зверху, n+)
    out.append(rect(bx + 20, by, bw - 40, 22, fill="#d0e1fd", stroke=LINE, sw=1.5, rx=2))
    out.append(text(bx + bw / 2, by + 15, "Омічний контакт n⁺ (B2)", size=11, color=INK, bold=True))
    out.append(line(bx + bw / 2, by, bx + bw / 2, by - 35, color=LINE, sw=2.0))
    out.append(circle(bx + bw / 2, by - 35, 4, fill=INK))
    out.append(text(bx + bw / 2 + 15, by - 32, "База 2 (B2)", size=13, bold=True, anchor="start"))

    # Контакт B1 (знизу, n+)
    out.append(rect(bx + 20, by + bh - 22, bw - 40, 22, fill="#d0e1fd", stroke=LINE, sw=1.5, rx=2))
    out.append(text(bx + bw / 2, by + bh - 7, "Омічний контакт n⁺ (B1)", size=11, color=INK, bold=True))
    out.append(line(bx + bw / 2, by + bh, bx + bw / 2, by + bh + 35, color=LINE, sw=2.0))
    out.append(circle(bx + bw / 2, by + bh + 35, 4, fill=INK))
    out.append(text(bx + bw / 2 + 15, by + bh + 38, "База 1 (B1, GND)", size=13, bold=True, anchor="start"))

    # Емітер p+ (збоку, ближче до B2)
    ey = by + 90
    ew, eh = 45, 55
    out.append(rect(bx - ew + 10, ey, ew, eh, fill="#fdecea", stroke=POS, sw=2.0, rx=4))
    out.append(text(bx - 12, ey + 32, "p⁺", size=14, color=POS, bold=True))
    out.append(line(bx - ew + 10, ey + eh / 2, bx - ew - 45, ey + eh / 2, color=POS, sw=2.2))
    out.append(circle(bx - ew - 45, ey + eh / 2, 4, fill=POS))
    out.append(text(bx - ew - 52, ey + eh / 2 + 4, "Емітер (E)", size=13, color=POS, bold=True, anchor="end"))

    # Збіднена область p-n переходу
    out.append('<path d="M %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="4,3"/>' % (
        bx + 10, ey - 10, bx + 35, ey + eh / 2, bx + 10, ey + eh + 10, MUTED))
    out.append(text(bx + 40, ey + 18, "Збіднена", size=10, color=MUTED, anchor="start"))
    out.append(text(bx + 40, ey + 30, "зона p-n", size=10, color=MUTED, anchor="start"))

    # Розподіл опорів R_B1 та R_B2
    # Стрілка розміру R_B2
    out.append(line(bx + bw + 25, by + 10, bx + bw + 25, ey + eh / 2, color=MUTED, sw=1.5))
    out.append(line(bx + bw + 20, by + 10, bx + bw + 30, by + 10, color=MUTED, sw=1.5))
    out.append(line(bx + bw + 20, ey + eh / 2, bx + bw + 30, ey + eh / 2, color=MUTED, sw=1.5))
    out.append(text(bx + bw + 36, by + 55, "R_B2 (верхнє плече)", size=12, color=INK, anchor="start"))
    out.append(text(bx + bw + 36, by + 72, "сталий опір", size=10, color=MUTED, anchor="start"))

    # Стрілка розміру R_B1
    out.append(line(bx + bw + 25, ey + eh / 2, bx + bw + 25, by + bh - 10, color=MUTED, sw=1.5))
    out.append(line(bx + bw + 20, by + bh - 10, bx + bw + 30, by + bh - 10, color=MUTED, sw=1.5))
    out.append(text(bx + bw + 36, by + 230, "R_B1 (нижнє плече)", size=12, color=INK, anchor="start"))
    out.append(text(bx + bw + 36, by + 248, "модульований опір", size=10, color=POS, bold=True, anchor="start"))

    # Інжекція дірок при спрацюванні
    out.append(arrow(bx + 5, ey + eh / 2, bx + 50, by + 260, color=POS, sw=2.2))
    out.append(text(bx + 75, by + 270, "Інжекція дірок", size=11, color=POS, bold=True, anchor="start"))
    out.append(text(bx + 75, by + 285, "у нижню базу", size=10, color=POS, anchor="start"))

    # Інформаційна плашка знизу
    infotext = "Внутрішній дільник:  η = R_B1 / (R_B1 + R_B2) ≈ 0.55 ... 0.82\nПри V_E > η·V_BB + V_D дірки затоплюють R_B1, опір падає з 5 кОм до 50 Ом"
    out.append(fitbox(70, 405, 620, 60, infotext, size=12, pad=8, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, "ujt-structure-cross-section.svg"), w, h, *out)


# ════════════════════════════════════════════════════════════════════════════
# 2. Еквівалентна схема UJT (ujt-equivalent-circuit.svg)
# ════════════════════════════════════════════════════════════════════════════
def fig2_ujt_equivalent():
    w, h = 740, 460
    out = []
    
    out.append(text(w / 2, 28, "Еквівалентна електрична схема одноперехідного транзистора", size=16, bold=True))

    # Рамка еквівалента UJT
    out.append(rect(140, 65, 460, 310, fill="#fdfdfd", stroke=MUTED, sw=1.5, rx=8))
    out.append(text(155, 88, "Еквівалентна модель UJT", size=12, color=MUTED, bold=True, anchor="start"))

    # Вузол B2
    x_b = 400
    out.append(line(x_b, 40, x_b, 100, color=LINE, sw=2.0))
    out.append(circle(x_b, 40, 4, fill=INK))
    out.append(text(x_b + 12, 44, "B2 (+V_BB)", size=13, bold=True, anchor="start"))

    # Резистор R_B2
    r2_svg, r2_yt, r2_yb = res_v(x_b, 130, h=50, w=18, label="R_B2 (сталий)", side="right")
    out.append(r2_svg)
    out.append(line(x_b, 100, x_b, r2_yt, color=LINE, sw=2.0))

    # Середня точка А
    y_mid = 210
    out.append(line(x_b, r2_yb, x_b, y_mid, color=LINE, sw=2.0))
    out.append(circle(x_b, y_mid, 4, fill=INK))
    out.append(text(x_b + 14, y_mid + 4, "Вузол A  (V_A = η·V_BB)", size=12, color=NEG, bold=True, anchor="start"))

    # Резистор R_B1 (змінний зі стрілкою)
    r1_svg, r1_yt, r1_yb = res_v(x_b, 290, h=60, w=18, label="R_B1 (модульований)", side="right")
    out.append(r1_svg)
    out.append(line(x_b, y_mid, x_b, r1_yt, color=LINE, sw=2.0))
    # Стрілка регулювання (діагональна)
    out.append(arrow(x_b - 22, 320, x_b + 22, 260, color=POS, sw=1.8))

    # Вузол B1
    out.append(line(x_b, r1_yb, x_b, 400, color=LINE, sw=2.0))
    out.append(circle(x_b, 400, 4, fill=INK))
    out.append(text(x_b + 12, 404, "B1 (Спільний / GND)", size=13, bold=True, anchor="start"))

    # Емітерний ланцюг
    x_em = 100
    out.append(circle(x_em, y_mid, 4, fill=POS))
    out.append(text(x_em - 10, y_mid + 4, "Емітер (E)", size=13, color=POS, bold=True, anchor="end"))
    out.append(line(x_em, y_mid, 270, y_mid, color=LINE, sw=2.0))

    # Діод D
    d_svg = diode_d(310, y_mid, direction="right", label="D (p-n перехід)")
    out.append(d_svg)
    out.append(line(325, y_mid, x_b, y_mid, color=LINE, sw=2.0))

    # Формульні пояснення праворуч/знизу
    box_s = "Умова відмикання емітера:\n  V_E ≥ V_P = η·V_BB + V_D\nде V_D ≈ 0.6...0.7 В (падіння на p-n переході),\n   η = R_B1 / (R_B1 + R_B2) — коефіцієнт поділу."
    out.append(fitbox(140, 395, 460, 55, box_s, size=11, pad=6, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, "ujt-equivalent-circuit.svg"), w, h, *out)


# ════════════════════════════════════════════════════════════════════════════
# 3. ВАХ емітера UJT (ujt-emitter-iv-curve.svg)
# ════════════════════════════════════════════════════════════════════════════
def fig3_ujt_iv_curve():
    w, h = 760, 480
    out = []
    
    out.append(text(w / 2, 26, "Вольт-амперна характеристика емітера UJT (V_E від I_E)", size=16, bold=True))

    ox, oy = 100, 390
    gw, gh = 580, 320

    # Сітка та осі
    out.append(arrow(ox, oy, ox + gw, oy, color=LINE, sw=2.0))
    out.append(arrow(ox, oy, ox, oy - gh, color=LINE, sw=2.0))
    out.append(text(ox + gw + 10, oy + 4, "I_E (Струм емітера)", size=13, bold=True, anchor="start"))
    out.append(text(ox - 10, oy - gh - 8, "V_E (Напруга емітера)", size=13, bold=True, anchor="middle"))
    out.append(text(ox - 12, oy + 16, "0", size=12, color=MUTED))

    # Характерні точки на графіку
    # Пік: Ip (малий струм, x ~ 180), Vp (висока напруга, y ~ 120)
    # Западина: Iv (великий струм, x ~ 420), Vv (низька напруга, y ~ 320)
    xp, yp = 180, 130
    xv, yv = 430, 310

    # Область 1: Відсікання (від нуля до піку)
    # Крива відсікання
    out.append('<path d="M %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="2.5"/>' % (
        ox, oy - 20, ox + 60, yp + 40, xp, yp, NEG))
    
    # Область 2: Від'ємний опір NDR (від піку до западини)
    out.append('<path d="M %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="3.0"/>' % (
        xp, yp, (xp + xv) / 2 - 10, (yp + yv) / 2 + 30, xv, yv, POS))

    # Область 3: Насичення (після западини)
    out.append('<path d="M %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="2.5"/>' % (
        xv, yv, xv + 60, yv - 30, ox + gw - 30, 200, FIELD))

    # Лінії проєкцій для точки Піку
    out.append(line(xp, yp, xp, oy, color=MUTED, sw=1.2, dash="4,3"))
    out.append(line(ox, yp, xp, yp, color=MUTED, sw=1.2, dash="4,3"))
    out.append(circle(xp, yp, 5, fill=POS))
    out.append(text(xp - 10, yp - 12, "Точка піку (Peak Point)", size=12, color=POS, bold=True, anchor="end"))
    out.append(text(ox - 8, yp + 4, "V_P", size=12, color=POS, bold=True, anchor="end"))
    out.append(text(xp, oy + 20, "I_P (~2-5 мкА)", size=11, color=POS, bold=True, anchor="middle"))

    # Лінії проєкцій для точки Западини
    out.append(line(xv, yv, xv, oy, color=MUTED, sw=1.2, dash="4,3"))
    out.append(line(ox, yv, xv, yv, color=MUTED, sw=1.2, dash="4,3"))
    out.append(circle(xv, yv, 5, fill=NEG))
    out.append(text(xv + 10, yv + 18, "Точка западини (Valley Point)", size=12, color=NEG, bold=True, anchor="start"))
    out.append(text(ox - 8, yv + 4, "V_V (~1-2 В)", size=12, color=NEG, bold=True, anchor="end"))
    out.append(text(xv, oy + 20, "I_V (~2-10 мА)", size=11, color=NEG, bold=True, anchor="middle"))

    # Навантажувальна пряма (Load Line)
    # Проходить крізь зону NDR
    out.append(line(ox + 40, 80, ox + 500, oy - 15, color="#8e44ad", sw=1.8, dash="6,3"))
    out.append(text(ox + 480, oy - 28, "Навантажувальна пряма (R)", size=11, color="#8e44ad", bold=True, anchor="end"))

    # Підписи трьох областей
    out.append(textbox(135, 230, "Область відсікання\n(Cutoff / Off)\nI_E < I_P", size=11, pad=6, fill="#f4f6f8", stroke=NEG)[0])
    out.append(textbox(305, 200, "Область від'ємного\nдиференційного опору\n(NDR: dV/dI < 0)", size=11, pad=6, fill="#fdecea", stroke=POS)[0])
    out.append(textbox(575, 240, "Область насичення\n(Saturation)\nI_E > I_V", size=11, pad=6, fill="#e8f8f0", stroke=FIELD)[0])

    # Нижня інформаційна плашка
    out.append(fitbox(80, 425, 600, 45, "Умова релаксаційної генерації: навантажувальна пряма мусить перетинати ВАХ ЛИШЕ на ділянці NDR:\n(V_BB - V_P) / I_P  >  R  >  (V_BB - V_V) / I_V", size=11, pad=6, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, "ujt-emitter-iv-curve.svg"), w, h, *out)


# ════════════════════════════════════════════════════════════════════════════
# 4. Схема релаксаційного генератора на UJT (ujt-relaxation-schematic.svg)
# ════════════════════════════════════════════════════════════════════════════
def fig4_ujt_relaxation_schematic():
    w, h = 760, 480
    out = []
    
    out.append(text(w / 2, 26, "Схема класичного релаксаційного генератора на UJT", size=16, bold=True))

    # Живлення зверху
    y_rail_top = 70
    y_rail_bot = 400
    x_left = 180
    x_ujt = 400
    x_out = 600

    # Шина +V_BB
    out.append(line(x_left - 40, y_rail_top, x_ujt + 80, y_rail_top, color=LINE, sw=2.0))
    out.append(circle(x_left - 40, y_rail_top, 4, fill=POS))
    out.append(text(x_left - 50, y_rail_top + 4, "+V_BB", size=13, color=POS, bold=True, anchor="end"))

    # Шина GND
    out.append(line(x_left - 40, y_rail_bot, x_ujt + 80, y_rail_bot, color=LINE, sw=2.0))
    out.append(gnd(x_left + 100, y_rail_bot, label="GND"))

    # Ліве плече: часозадавальне коло R-C
    # Резистор заряду R
    r_svg, r_yt, r_yb = res_v(x_left, 150, h=60, w=18, label="R (10k...100k)", side="left")
    out.append(r_svg)
    out.append(line(x_left, y_rail_top, x_left, r_yt, color=LINE, sw=1.8))

    # Вузол емітера
    y_em_node = 240
    out.append(line(x_left, r_yb, x_left, y_em_node, color=LINE, sw=1.8))
    out.append(circle(x_left, y_em_node, 4, fill=POS))

    # Конденсатор C
    c_svg, c_yt, c_yb = cap_v(x_left, 320, h=30, w=24, label="C (10n...1uF)", side="left")
    out.append(c_svg)
    out.append(line(x_left, y_em_node, x_left, c_yt, color=LINE, sw=1.8))
    out.append(line(x_left, c_yb, x_left, y_rail_bot, color=LINE, sw=1.8))

    # Вихід пилки з конденсатора
    out.append(line(x_left, y_em_node, x_left + 40, y_em_node, color=LINE, sw=1.8))
    out.append(circle(x_left + 40, y_em_node, 4, fill=POS))
    out.append(text(x_left + 48, y_em_node - 8, "V_вих (пилкоподібна)", size=11, color=POS, bold=True, anchor="start"))
    out.append(text(x_left + 48, y_em_node + 10, "на конденсаторі", size=10, color=MUTED, anchor="start"))

    # З'єднання з емітером UJT
    out.append(line(x_left, y_em_node, x_ujt - 40, y_em_node, color=LINE, sw=1.8))

    # UJT символ у центрі (x_ujt, y_em_node)
    # Вертикальна планка бази
    out.append(line(x_ujt, y_em_node - 35, x_ujt, y_em_node + 35, color=LINE, sw=3.0))
    # Похилий емітер зі стрілкою
    out.append(line(x_ujt - 40, y_em_node, x_ujt - 10, y_em_node, color=LINE, sw=2.0))
    out.append(arrow(x_ujt - 10, y_em_node, x_ujt, y_em_node - 15, color=LINE, sw=2.0))
    out.append(circle(x_ujt - 15, y_em_node, 36, fill="none", stroke=LINE, sw=1.5))
    out.append(text(x_ujt + 38, y_em_node - 2, "UJT", size=13, bold=True, anchor="start"))
    out.append(text(x_ujt + 38, y_em_node + 14, "(2N2646)", size=10, color=MUTED, anchor="start"))

    # Верхнє коло B2: резистор R2 (температурна компенсація)
    r2_svg, r2_yt, r2_yb = res_v(x_ujt, 120, h=44, w=16, label="R2 (100...470 Ом)", side="right")
    out.append(r2_svg)
    out.append(line(x_ujt, y_rail_top, x_ujt, r2_yt, color=LINE, sw=1.8))
    out.append(line(x_ujt, r2_yb, x_ujt, y_em_node - 35, color=LINE, sw=1.8))

    # Нижнє коло B1: резистор R1 (формування вихідних імпульсів)
    r1_svg, r1_yt, r1_yb = res_v(x_ujt, 340, h=44, w=16, label="R1 (20...100 Ом)", side="right")
    out.append(r1_svg)
    out.append(line(x_ujt, y_em_node + 35, x_ujt, r1_yt, color=LINE, sw=1.8))
    out.append(line(x_ujt, r1_yb, x_ujt, y_rail_bot, color=LINE, sw=1.8))

    # Вихід імпульсів з B1
    y_b1_out = 300
    out.append(line(x_ujt, y_b1_out, x_out, y_b1_out, color=LINE, sw=1.8))
    out.append(circle(x_out, y_b1_out, 4, fill=FIELD))
    out.append(text(x_out + 10, y_b1_out + 4, "V_вих (імпульси на B1)", size=12, color=FIELD, bold=True, anchor="start"))

    # Пояснювальний блок унизу
    calc_box = "Період коливань:  T ≈ R · C · ln(1 / (1 − η))\nЧастота:  f = 1 / T  (типово від 0.1 Гц до 100 кГц)\nКороткий імпульс струму на R1 збуджує керувальний електрод тиристора."
    out.append(fitbox(80, 415, 600, 55, calc_box, size=11, pad=6, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, "ujt-relaxation-schematic.svg"), w, h, *out)


# ════════════════════════════════════════════════════════════════════════════
# 5. Часові діаграми генератора (ujt-waveforms.svg)
# ════════════════════════════════════════════════════════════════════════════
def fig5_ujt_waveforms():
    w, h = 760, 500
    out = []
    
    out.append(text(w / 2, 26, "Часові діаграми напруг релаксаційного генератора на UJT", size=16, bold=True))

    ox = 120
    t_len = 560
    t_end = ox + t_len

    # --- Діаграма 1: Напруга на емітері / конденсаторі VE(t) ---
    y1_base = 160
    h1 = 90
    out.append(arrow(ox, y1_base, t_end + 20, y1_base, color=LINE, sw=1.5))
    out.append(arrow(ox, y1_base, ox, y1_base - h1 - 15, color=LINE, sw=1.5))
    out.append(text(ox - 10, y1_base - h1 / 2, "V_E(t)", size=13, color=POS, bold=True, anchor="end"))
    out.append(text(t_end + 25, y1_base + 4, "t", size=12, italic=True))

    # Рівні V_P та V_V
    y_vp = y1_base - h1 + 10
    y_vv = y1_base - 18
    out.append(line(ox, y_vp, t_end, y_vp, color=MUTED, sw=1.0, dash="4,3"))
    out.append(line(ox, y_vv, t_end, y_vv, color=MUTED, sw=1.0, dash="4,3"))
    out.append(text(ox - 8, y_vp + 4, "V_P", size=11, color=POS, bold=True, anchor="end"))
    out.append(text(ox - 8, y_vv + 4, "V_V", size=11, color=NEG, bold=True, anchor="end"))

    # Періоди заряду/розряду
    # Період T ~ 170 px
    pts1 = [
        (ox, y_vv),
        (ox + 160, y_vp), (ox + 165, y_vv),
        (ox + 325, y_vp), (ox + 330, y_vv),
        (ox + 490, y_vp), (ox + 495, y_vv),
        (t_end, y_vv + (y_vp - y_vv) * 0.4)
    ]
    # Будуємо форму пилки (експоненційне зростання)
    path_ve = ["M %d %d" % pts1[0]]
    for i in range(1, len(pts1) - 1, 2):
        x_start, y_start = pts1[i-1]
        x_peak, y_peak = pts1[i]
        x_low, y_low = pts1[i+1]
        path_ve.append("Q %d %d %d %d" % ((x_start + x_peak) / 2 - 15, y_start - (y_start - y_peak) * 0.7, x_peak, y_peak))
        path_ve.append("L %d %d" % (x_low, y_low))
    # Хвіст
    path_ve.append("Q %d %d %d %d" % ((pts1[-2][0] + pts1[-1][0]) / 2, pts1[-2][1] - 20, pts1[-1][0], pts1[-1][1]))
    out.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(path_ve), POS))

    # Стрілка періоду T
    out.append(line(ox + 165, y_vp - 18, ox + 330, y_vp - 18, color=INK, sw=1.5))
    out.append(line(ox + 165, y_vp - 24, ox + 165, y_vp - 12, color=INK, sw=1.5))
    out.append(line(ox + 330, y_vp - 24, ox + 330, y_vp - 12, color=INK, sw=1.5))
    out.append(text(ox + 248, y_vp - 24, "Період T", size=11, bold=True, anchor="middle"))

    # --- Діаграма 2: Напруга на базі B1 VB1(t) (гострі додатні імпульси) ---
    y2_base = 310
    h2 = 80
    out.append(arrow(ox, y2_base, t_end + 20, y2_base, color=LINE, sw=1.5))
    out.append(arrow(ox, y2_base, ox, y2_base - h2 - 10, color=LINE, sw=1.5))
    out.append(text(ox - 10, y2_base - h2 / 2, "V_B1(t)", size=13, color=FIELD, bold=True, anchor="end"))
    out.append(text(t_end + 25, y2_base + 4, "t", size=12, italic=True))

    # Імпульси в моменти розряду (x = 162, 327, 492)
    path_vb1 = ["M %d %d" % (ox, y2_base)]
    for xp in [ox + 162, ox + 327, ox + 492]:
        path_vb1.append("L %d %d" % (xp - 2, y2_base))
        path_vb1.append("L %d %d" % (xp, y2_base - h2 + 10))
        path_vb1.append("L %d %d" % (xp + 4, y2_base))
    path_vb1.append("L %d %d" % (t_end, y2_base))
    out.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(path_vb1), FIELD))
    out.append(text(ox + 195, y2_base - h2 + 25, "Короткий пусковий імпульс (t_p ≈ 1-10 мкс)", size=10, color=FIELD, bold=True, anchor="start"))

    # --- Діаграма 3: Напруга на базі B2 VB2(t) (негативні провали) ---
    y3_base = 430
    h3 = 50
    out.append(arrow(ox, y3_base, t_end + 20, y3_base, color=LINE, sw=1.5))
    out.append(arrow(ox, y3_base, ox, y3_base - h3 - 10, color=LINE, sw=1.5))
    out.append(text(ox - 10, y3_base - h3 / 2, "V_B2(t)", size=13, color=NEG, bold=True, anchor="end"))
    out.append(text(t_end + 25, y3_base + 4, "t", size=12, italic=True))

    y_vbb_level = y3_base - h3 + 5
    out.append(line(ox, y_vbb_level, t_end, y_vbb_level, color=MUTED, sw=1.0, dash="4,3"))
    out.append(text(ox - 8, y_vbb_level + 4, "V_BB", size=11, color=INK, anchor="end"))

    # Провали в ті самі моменти
    path_vb2 = ["M %d %d" % (ox, y_vbb_level)]
    for xp in [ox + 162, ox + 327, ox + 492]:
        path_vb2.append("L %d %d" % (xp - 2, y_vbb_level))
        path_vb2.append("L %d %d" % (xp, y_vbb_level + 30))
        path_vb2.append("L %d %d" % (xp + 4, y_vbb_level))
    path_vb2.append("L %d %d" % (t_end, y_vbb_level))
    out.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(path_vb2), NEG))

    # Вертикальні лінії синхронізації
    for xp in [ox + 162, ox + 327, ox + 492]:
        out.append(line(xp, y_vp, xp, y3_base, color=MUTED, sw=1.0, dash="2,3"))

    render(os.path.join(IMG, "ujt-waveforms.svg"), w, h, *out)


# ════════════════════════════════════════════════════════════════════════════
# 6. Схема фазоімпульсного керування SCR/TRIAC (ujt-scr-trigger-circuit.svg)
# ════════════════════════════════════════════════════════════════════════════
def fig6_ujt_scr_trigger():
    w, h = 780, 500
    out = []
    
    out.append(text(w / 2, 26, "Схема фазового керування симістором/тиристором на UJT", size=16, bold=True))

    # Ліва частина: Мережа AC 230 В та випрямляч
    # Джерело змінного струму
    x_ac = 70
    y_ac = 180
    out.append(circle(x_ac, y_ac, 22, fill="#fdfdfd", stroke=LINE, sw=1.8))
    out.append(text(x_ac, y_ac + 4, "~ 230 В", size=11, bold=True))
    out.append(text(x_ac, y_ac + 40, "50 Гц", size=10, color=MUTED))

    # Діодний міст (прямокутний блок для простоти сприйняття)
    x_br = 160
    out.append(rect(x_br, y_ac - 35, 70, 70, fill=FILL, stroke=LINE, sw=1.8, rx=4))
    out.append(text(x_br + 35, y_ac - 8, "Діодний", size=11, bold=True))
    out.append(text(x_br + 35, y_ac + 8, "міст", size=11, bold=True))
    out.append(text(x_br + 35, y_ac + 22, "(AC → DC)", size=9, color=MUTED))
    out.append(line(x_ac + 22, y_ac - 12, x_br, y_ac - 12, color=LINE, sw=1.5))
    out.append(line(x_ac + 22, y_ac + 12, x_br, y_ac + 12, color=LINE, sw=1.5))

    # Стабілітрон Zener + баластний резистор R_drop
    x_drop = 290
    y_top = 100
    y_bot = 380

    out.append(line(x_br + 70, y_ac - 15, x_drop - 30, y_top, color=LINE, sw=1.8))
    rdr_svg, _, _ = res_h(x_drop, y_top, w=44, h=16, label="R_баласт", pos="top")
    out.append(rdr_svg)

    # Стабілітрон паралельно шині
    x_zen = 360
    out.append(line(x_drop + 22, y_top, x_zen, y_top, color=LINE, sw=1.8))
    out.append(line(x_zen, y_top, x_zen, y_top + 30, color=LINE, sw=1.5))
    # Стабілітрон
    out.append(diode_d(x_zen, y_top + 50, direction="up", label="ZD (20 В)"))
    out.append(line(x_zen, y_top + 70, x_zen, y_bot, color=LINE, sw=1.5))

    # Нижня шина
    out.append(line(x_br + 70, y_ac + 15, x_zen, y_bot, color=LINE, sw=1.8))
    out.append(line(x_zen, y_bot, 570, y_bot, color=LINE, sw=1.8))

    # Трапецієподібна синхронізована напруга живлення UJT
    out.append(line(x_zen, y_top, 570, y_top, color=LINE, sw=1.8))
    out.append(text(x_zen + 35, y_top - 12, "V_синк (трапеція +20 В)", size=11, color=POS, bold=True, anchor="start"))

    # UJT генератор
    x_pot = 430
    # Потенціометр фази
    rpot_svg, _, _ = res_v(x_pot, y_top + 60, h=46, w=16, label="R_фаза (пот.)", side="left")
    out.append(rpot_svg)
    out.append(line(x_pot, y_top, x_pot, y_top + 37, color=LINE, sw=1.5))

    # Конденсатор C
    c_svg, _, _ = cap_v(x_pot, y_top + 160, h=26, w=22, label="C", side="left")
    out.append(c_svg)
    out.append(line(x_pot, y_top + 83, x_pot, y_top + 147, color=LINE, sw=1.5))
    out.append(line(x_pot, y_top + 173, x_pot, y_bot, color=LINE, sw=1.5))

    # Вузол емітера
    y_em = y_top + 115
    out.append(line(x_pot, y_em, x_pot + 50, y_em, color=LINE, sw=1.5))

    # UJT
    x_uj = 510
    out.append(line(x_uj, y_em - 25, x_uj, y_em + 25, color=LINE, sw=2.5))
    out.append(line(x_pot + 50, y_em, x_uj - 5, y_em, color=LINE, sw=1.5))
    out.append(arrow(x_uj - 5, y_em, x_uj, y_em - 12, color=LINE, sw=1.8))
    out.append(circle(x_uj - 8, y_em, 28, fill="none", stroke=LINE, sw=1.5))

    # Підключення B2
    out.append(line(x_uj, y_top, x_uj, y_em - 25, color=LINE, sw=1.5))

    # Первинна обмотка імпульсного трансформатора в колі B1
    y_tr = y_top + 190
    out.append(line(x_uj, y_em + 25, x_uj, y_tr - 20, color=LINE, sw=1.5))
    out.append(rect(x_uj - 8, y_tr - 20, 16, 40, fill="#fdfdfd", stroke=LINE, sw=1.5, rx=2))
    out.append(text(x_uj + 14, y_tr + 4, "T1 (первинна)", size=10, color=MUTED, anchor="start"))
    out.append(line(x_uj, y_tr + 20, x_uj, y_bot, color=LINE, sw=1.5))

    # Силова частина праворуч (Симістор / Навантаження)
    x_pwr = 670
    # Вторинна обмотка трансформатора
    out.append(rect(x_pwr - 55, y_tr - 20, 16, 40, fill="#fdfdfd", stroke=LINE, sw=1.5, rx=2))
    out.append(text(x_pwr - 47, y_tr + 30, "T1 (втор.)", size=10, color=MUTED, anchor="middle"))
    # Сердечник трансформатора (дві лінії)
    out.append(line(x_uj + 12, y_tr - 18, x_uj + 12, y_tr + 18, color=MUTED, sw=1.2))
    out.append(line(x_uj + 16, y_tr - 18, x_uj + 16, y_tr + 18, color=MUTED, sw=1.2))

    # Символ симістора/тиристора
    out.append(circle(x_pwr, y_ac + 40, 26, fill=FILL, stroke=LINE, sw=1.5))
    out.append(text(x_pwr, y_ac + 44, "TRIAC", size=11, bold=True))

    # Керувальний електрод (Gate)
    out.append(line(x_pwr - 39, y_tr - 10, x_pwr - 20, y_ac + 30, color=FIELD, sw=1.8))
    out.append(line(x_pwr - 39, y_tr + 10, x_pwr, y_ac + 66, color=LINE, sw=1.5))

    # Навантаження (Лампа / Двигун)
    out.append(rect(x_pwr - 25, y_top, 50, 36, fill="#fef9e7", stroke=LINE, sw=1.5, rx=4))
    out.append(text(x_pwr, y_top + 22, "Навантаження", size=10, bold=True))

    # Силове коло змінної напруги
    out.append(line(x_ac, y_ac - 22, x_ac, y_top - 30, color=LINE, sw=1.8))
    out.append(line(x_ac, y_top - 30, x_pwr, y_top - 30, color=LINE, sw=1.8))
    out.append(line(x_pwr, y_top - 30, x_pwr, y_top, color=LINE, sw=1.8))
    out.append(line(x_pwr, y_top + 36, x_pwr, y_ac + 14, color=LINE, sw=1.8))
    out.append(line(x_pwr, y_ac + 66, x_pwr, y_bot + 40, color=LINE, sw=1.8))
    out.append(line(x_ac, y_ac + 22, x_ac, y_bot + 40, color=LINE, sw=1.8))
    out.append(line(x_ac, y_bot + 40, x_pwr, y_bot + 40, color=LINE, sw=1.8))

    # Нижня інформаційна плашка
    out.append(fitbox(70, 440, 640, 48, "Принцип фазового регулювання: у кожному напівперіоді мережі напруга ZD скидає конденсатор на нуль.\nЗміна R_фаза змінює кут відмикання симістора від 0° до 180°, плавно регулюючи середню потужність.", size=11, pad=6, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, "ujt-scr-trigger-circuit.svg"), w, h, *out)


# ════════════════════════════════════════════════════════════════════════════
# 7. Програмований одноперехідний транзистор PUT (put-structure-and-biasing.svg)
# ════════════════════════════════════════════════════════════════════════════
def fig7_put_structure_and_biasing():
    w, h = 760, 480
    out = []
    
    out.append(text(w / 2, 26, "Програмований одноперехідний транзистор (PUT): будова та зміщення", size=16, bold=True))

    # Ліва панель: 4-шарова напівпровідникова структура (p-n-p-n)
    lx = 140
    ly = 80
    lw, lh = 120, 220
    out.append(rect(lx, ly, lw, lh, fill="#fdfdfd", stroke=LINE, sw=1.8, rx=4))
    
    # 4 шари
    sh = lh / 4
    out.append(rect(lx, ly, lw, sh, fill="#fdecea", stroke=LINE, sw=1.2))
    out.append(text(lx + lw / 2, ly + sh / 2 + 5, "p⁺ (Анод A)", size=12, color=POS, bold=True))
    
    out.append(rect(lx, ly + sh, lw, sh, fill="#e8f4fd", stroke=LINE, sw=1.2))
    out.append(text(lx + lw / 2, ly + sh + sh / 2 + 5, "n (Керувальний G)", size=12, color=NEG, bold=True))
    
    out.append(rect(lx, ly + 2 * sh, lw, sh, fill="#fdecea", stroke=LINE, sw=1.2))
    out.append(text(lx + lw / 2, ly + 2 * sh + sh / 2 + 5, "p (База)", size=12, color=POS))
    
    out.append(rect(lx, ly + 3 * sh, lw, sh, fill="#e8f4fd", stroke=LINE, sw=1.2))
    out.append(text(lx + lw / 2, ly + 3 * sh + sh / 2 + 5, "n⁺ (Катод K)", size=12, color=NEG, bold=True))

    # Виводи 4-шарової структури
    # Анод зверху
    out.append(line(lx + lw / 2, ly, lx + lw / 2, ly - 30, color=POS, sw=2.0))
    out.append(circle(lx + lw / 2, ly - 30, 4, fill=POS))
    out.append(text(lx + lw / 2, ly - 38, "Анод (A)", size=12, color=POS, bold=True))

    # Затвор з n-шару
    out.append(line(lx + lw, ly + 1.5 * sh, lx + lw + 35, ly + 1.5 * sh, color=NEG, sw=2.0))
    out.append(circle(lx + lw + 35, ly + 1.5 * sh, 4, fill=NEG))
    out.append(text(lx + lw + 42, ly + 1.5 * sh + 4, "Затвор (G, n-база)", size=11, color=NEG, bold=True, anchor="start"))

    # Катод знизу
    out.append(line(lx + lw / 2, ly + lh, lx + lw / 2, ly + lh + 30, color=LINE, sw=2.0))
    out.append(circle(lx + lw / 2, ly + lh + 30, 4, fill=INK))
    out.append(text(lx + lw / 2, ly + lh + 42, "Катод (K)", size=12, bold=True))

    # Права панель: Схема увімкнення PUT із зовнішнім подільником R1-R2
    rx = 480
    y_top = 70
    y_bot = 350

    # Шина живлення
    out.append(line(rx - 50, y_top, rx + 130, y_top, color=LINE, sw=1.8))
    out.append(circle(rx - 50, y_top, 4, fill=POS))
    out.append(text(rx - 60, y_top + 4, "+V_S", size=13, color=POS, bold=True, anchor="end"))

    out.append(line(rx - 50, y_bot, rx + 130, y_bot, color=LINE, sw=1.8))
    out.append(gnd(rx + 100, y_bot, label="GND"))

    # Зовнішній дільник програмування: R2 (верхній) та R1 (нижній)
    x_div = rx + 80
    r2_svg, _, _ = res_v(x_div, y_top + 65, h=46, w=16, label="R2 (верхній)", side="right")
    out.append(r2_svg)
    out.append(line(x_div, y_top, x_div, y_top + 42, color=LINE, sw=1.5))

    y_g_node = y_top + 140
    out.append(line(x_div, y_top + 88, x_div, y_g_node, color=LINE, sw=1.5))
    out.append(circle(x_div, y_g_node, 4, fill=NEG))
    out.append(text(x_div + 12, y_g_node + 4, "V_G = η·V_S", size=11, color=NEG, bold=True, anchor="start"))

    r1_svg, _, _ = res_v(x_div, y_top + 215, h=46, w=16, label="R1 (нижній)", side="right")
    out.append(r1_svg)
    out.append(line(x_div, y_g_node, x_div, y_top + 192, color=LINE, sw=1.5))
    out.append(line(x_div, y_top + 238, x_div, y_bot, color=LINE, sw=1.5))

    # Схема PUT у центрі
    x_put = rx
    y_put = y_top + 140

    # Символ PUT (діод зі зміщеним затвором на анодному боці)
    out.append(circle(x_put, y_put, 26, fill=FILL, stroke=LINE, sw=1.5))
    out.append(diode_d(x_put, y_put, direction="down"))
    # Затвор під кутом до анода
    out.append(line(x_put - 8, y_put - 10, x_put + 30, y_put - 10, color=NEG, sw=1.8))
    out.append(line(x_put + 30, y_put - 10, x_div, y_g_node, color=NEG, sw=1.8))

    # Анод підключено до часового кола RA-C
    out.append(line(x_put, y_top, x_put, y_put - 26, color=LINE, sw=1.5))
    # Катод на резистор навантаження RK
    out.append(line(x_put, y_put + 26, x_put, y_bot - 40, color=LINE, sw=1.5))
    rk_svg, _, _ = res_v(x_put, y_bot - 20, h=36, w=14, label="R_K", side="left")
    out.append(rk_svg)
    out.append(line(x_put, y_bot - 2, x_put, y_bot, color=LINE, sw=1.5))

    # Нижня інформаційна плашка
    summary = "Перевага PUT (2N6027) над класичним UJT (2N2646):\nКоефіцієнт η = R1 / (R1 + R2) задається зовнішніми прецизійними резисторами, а не технологічним розкидом кремнію.\nПоріг спрацьовування: V_A ≥ V_G + V_D = η·V_S + 0.6 В."
    out.append(fitbox(60, 400, 640, 65, summary, size=11, pad=6, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, "put-structure-and-biasing.svg"), w, h, *out)


if __name__ == "__main__":
    fig1_ujt_structure()
    fig2_ujt_equivalent()
    fig3_ujt_iv_curve()
    fig4_ujt_relaxation_schematic()
    fig5_ujt_waveforms()
    fig6_ujt_scr_trigger()
    fig7_put_structure_and_biasing()
    print("Всі 7 фігур для ujt-relaxation успішно згенеровано.")
