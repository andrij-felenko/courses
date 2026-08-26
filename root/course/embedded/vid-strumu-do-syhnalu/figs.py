# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def resistor_h(x, y, w=50, h=14, label=None, lblsize=13, lblpos="top"):
    """Горизонтальний резистор-зигзаг."""
    n = 6
    seg = w / n
    pts = [(x, y)]
    for i in range(n):
        px = x + seg * (i + 0.5)
        py = y - h / 2 if i % 2 == 0 else y + h / 2
        pts.append((px, py))
    pts.append((x + w, y))
    d = "M " + " L ".join("%.1f %.1f" % p for p in pts)
    out = '<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (d, INK)
    if label:
        ly = y - h / 2 - 8 if lblpos == "top" else y + h / 2 + 16
        out += text(x + w / 2, ly, label, size=lblsize, bold=True)
    return out


def resistor_v(x, y, h=50, w=14, label=None, lblsize=13, lblpos="right"):
    """Вертикальний резистор-зигзаг."""
    n = 6
    seg = h / n
    pts = [(x, y)]
    for i in range(n):
        py = y + seg * (i + 0.5)
        px = x - w / 2 if i % 2 == 0 else x + w / 2
        pts.append((px, py))
    pts.append((x, y + h))
    d = "M " + " L ".join("%.1f %.1f" % p for p in pts)
    out = '<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (d, INK)
    if label:
        lx = x + w / 2 + 10 if lblpos == "right" else x - w / 2 - 10
        anchor = "start" if lblpos == "right" else "end"
        out += text(lx, y + h / 2 + 4, label, size=lblsize, bold=True, anchor=anchor)
    return out


def cap_v(x, y, label=None, lblsize=13, lblpos="right"):
    """Вертикальний конденсатор."""
    out = line(x, y, x, y + 14, INK, 1.8)
    out += line(x - 12, y + 14, x + 12, y + 14, INK, 2.2)
    out += line(x - 12, y + 20, x + 12, y + 20, INK, 2.2)
    out += line(x, y + 20, x, y + 34, INK, 1.8)
    if label:
        lx = x + 18 if lblpos == "right" else x - 18
        anchor = "start" if lblpos == "right" else "end"
        out += text(lx, y + 20, label, size=lblsize, bold=True, anchor=anchor)
    return out


def gnd(x, y):
    """Символ заземлення."""
    out = line(x, y, x, y + 10, INK, 1.8)
    out += line(x - 12, y + 10, x + 12, y + 10, INK, 2)
    out += line(x - 8, y + 15, x + 8, y + 15, INK, 2)
    out += line(x - 4, y + 20, x + 4, y + 20, INK, 2)
    return out


def node_dot(x, y, r=3.2):
    return circle(x, y, r, fill=INK, stroke=INK, sw=1)


def opamp_sym(cx, cy, w=50, h=44, invert_top=True):
    """Трикутник операційного підсилювача з виводами."""
    x1, y1 = cx - w / 2, cy - h / 2
    x2, y2 = cx - w / 2, cy + h / 2
    x3, y3 = cx + w / 2, cy
    d = "M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" % (x1, y1, x2, y2, x3, y3)
    out = '<path d="%s" fill="%s" stroke="%s" stroke-width="2"/>' % (d, FILL, INK)
    
    in1_y = cy - h / 4
    in2_y = cy + h / 4
    lbl1 = "−" if invert_top else "+"
    lbl2 = "+" if invert_top else "−"
    col1 = NEG if invert_top else POS
    col2 = POS if invert_top else NEG
    
    out += text(x1 + 8, in1_y + 4, lbl1, size=14, bold=True, color=col1)
    out += text(x1 + 8, in2_y + 4, lbl2, size=14, bold=True, color=col2)
    return out, (x1, in1_y), (x1, in2_y), (x3, y3)


# ── 1. Порівняння передачі напругою проти струму ──────────────────────────
def fig_voltage_vs_current():
    W, H = 760, 440
    f = []
    f.append(text(W / 2, 24, "Передача інформації: напруга проти струму на довгій лінії", size=17, bold=True))

    # Ліва колонка — Передача напругою (помилки)
    box_w, box_h = 340, 370
    bx1, by1 = 30, 48
    f.append(rect(bx1, by1, box_w, box_h, fill="#fff8f8", stroke=POS, sw=1.5, rx=8))
    f.append(text(bx1 + box_w / 2, by1 + 22, "1. Сигнал напругою (0–10 В)", size=15, bold=True, color=POS))

    # Схема напруги
    y_sig = by1 + 80
    y_ret = by1 + 170
    # Джерело напруги
    f.append(circle(bx1 + 45, (y_sig + y_ret) / 2, 18, fill="#ffffff", stroke=POS, sw=2))
    f.append(text(bx1 + 45, (y_sig + y_ret) / 2 + 5, "V_sig", size=11, bold=True, color=POS))
    f.append(line(bx1 + 45, y_sig, bx1 + 45, (y_sig + y_ret) / 2 - 18, POS, 1.8))
    f.append(line(bx1 + 45, y_ret, bx1 + 45, (y_sig + y_ret) / 2 + 18, POS, 1.8))
    f.append(line(bx1 + 45, y_ret, bx1 + 45, y_ret + 15, INK, 1.8))
    f.append(gnd(bx1 + 45, y_ret + 15))
    f.append(text(bx1 + 45, y_ret + 45, "GND 1", size=11, bold=True))

    # Дріт з опором R_line1
    f.append(line(bx1 + 45, y_sig, bx1 + 85, y_sig, INK, 1.8))
    f.append(resistor_h(bx1 + 85, y_sig, 50, label="R_line"))
    f.append(line(bx1 + 135, y_sig, bx1 + 270, y_sig, INK, 1.8))

    # Зворотний дріт з R_line2
    f.append(line(bx1 + 45, y_ret, bx1 + 85, y_ret, INK, 1.8))
    f.append(resistor_h(bx1 + 85, y_ret, 50, label="R_line", lblpos="bottom"))
    f.append(line(bx1 + 135, y_ret, bx1 + 270, y_ret, INK, 1.8))

    # Приймач напруги (АЦП / Вольтметр)
    f.append(rect(bx1 + 270, y_sig - 10, 50, (y_ret - y_sig) + 20, fill="#ffffff", stroke=LINE, sw=1.8))
    f.append(text(bx1 + 295, (y_sig + y_ret) / 2 + 4, "АЦП", size=12, bold=True))
    f.append(line(bx1 + 295, y_ret + 10, bx1 + 295, y_ret + 25, INK, 1.8))
    f.append(gnd(bx1 + 295, y_ret + 25))
    f.append(text(bx1 + 295, y_ret + 55, "GND 2", size=11, bold=True))

    # Завада землі між GND 1 та GND 2
    f.append(arrow(bx1 + 85, y_ret + 45, bx1 + 255, y_ret + 45, color=POS, sw=1.5))
    f.append(text(bx1 + 170, y_ret + 38, "ΔV_gnd (земляна петля)", size=11, color=POS, bold=True))

    # Ємнісна завада
    f.append(cap_v(bx1 + 205, y_sig - 40, label="C_пар", lblsize=10, lblpos="right"))
    f.append(line(bx1 + 205, y_sig - 40, bx1 + 205, y_sig - 45, POS, 1.5))
    f.append(text(bx1 + 205, y_sig - 52, "Завада 230 В~", size=10, bold=True, color=POS))
    f.append(node_dot(bx1 + 205, y_sig))

    # Пояснювальний блок знизу
    f.append(fitbox(bx1 + 12, by1 + 255, box_w - 24, 100,
        "Вразливості сигналу напруги:\n"
        "• Падіння напруги: V_in = V_sig − I_витік · 2R_line\n"
        "• Земляні петлі: різниця ΔV_gnd додається до виміру\n"
        "• Високий R_вх АЦП ловить усі ємнісні наведення",
        size=11, fill="#ffffff", stroke=POS))

    # Права колонка — Передача струмом (переваги)
    bx2 = 390
    f.append(rect(bx2, by1, box_w, box_h, fill="#f2f9f4", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(bx2 + box_w / 2, by1 + 22, "2. Струмова петля (4–20 мА)", size=15, bold=True, color=FIELD))

    # Джерело струму
    f.append(circle(bx2 + 45, (y_sig + y_ret) / 2, 18, fill="#ffffff", stroke=FIELD, sw=2))
    f.append(text(bx2 + 45, (y_sig + y_ret) / 2 + 5, "I_sig", size=12, bold=True, color=FIELD))
    f.append(line(bx2 + 45, y_sig, bx2 + 45, (y_sig + y_ret) / 2 - 18, FIELD, 1.8))
    f.append(line(bx2 + 45, y_ret, bx2 + 45, (y_sig + y_ret) / 2 + 18, FIELD, 1.8))

    # Верхній дріт із стрілкою струму
    f.append(line(bx2 + 45, y_sig, bx2 + 85, y_sig, INK, 1.8))
    f.append(resistor_h(bx2 + 85, y_sig, 50, label="R_line"))
    f.append(arrow(bx2 + 145, y_sig - 10, bx2 + 195, y_sig - 10, color=FIELD, sw=2))
    f.append(text(bx2 + 170, y_sig - 20, "I = 4..20 мА", size=11, bold=True, color=FIELD))
    f.append(line(bx2 + 135, y_sig, bx2 + 270, y_sig, INK, 1.8))

    # Приймач із шунтом R_shunt (розміщуємо напис ліворуч)
    f.append(line(bx2 + 270, y_sig, bx2 + 270, y_sig + 15, INK, 1.8))
    f.append(resistor_v(bx2 + 270, y_sig + 15, 50, label="R_шунт", lblpos="left"))
    f.append(line(bx2 + 270, y_sig + 65, bx2 + 270, y_ret, INK, 1.8))
    f.append(line(bx2 + 45, y_ret, bx2 + 85, y_ret, INK, 1.8))
    f.append(resistor_h(bx2 + 85, y_ret, 50, label="R_line", lblpos="bottom"))
    f.append(line(bx2 + 135, y_ret, bx2 + 270, y_ret, INK, 1.8))
    f.append(arrow(bx2 + 205, y_ret + 12, bx2 + 155, y_ret + 12, color=FIELD, sw=2))

    # Вимірювання на шунті
    f.append(node_dot(bx2 + 270, y_sig + 10))
    f.append(node_dot(bx2 + 270, y_sig + 70))
    f.append(line(bx2 + 270, y_sig + 10, bx2 + 300, y_sig + 10, LINE, 1.2, dash="3 3"))
    f.append(line(bx2 + 270, y_sig + 70, bx2 + 300, y_sig + 70, LINE, 1.2, dash="3 3"))
    f.append(arrow(bx2 + 300, y_sig + 70, bx2 + 300, y_sig + 10, color=NEG, sw=1.5))
    f.append(text(bx2 + 308, y_sig + 42, "V_вих", size=11, bold=True, color=NEG, anchor="start"))

    # Пояснювальний блок знизу
    f.append(fitbox(bx2 + 12, by1 + 255, box_w - 24, 100,
        "Переваги струмової петлі:\n"
        "• KCL: струм однаковий у кожному перерізі петлі\n"
        "• R_line не спотворює струм (компенсується джерелом)\n"
        "• R_шунт малий (100–250 Ом) — завади миттєво зливаються\n"
        "• Немає чутливості до різниці потенціалів земель",
        size=11, fill="#ffffff", stroke=FIELD))

    render(os.path.join(OUT, "voltage-vs-current-line.svg"), W, H, *f)


# ── 2. Схемотехніка промислової петлі 4–20 мА ─────────────────────────────
def fig_current_loop_4_20ma():
    W, H = 760, 480
    f = []
    f.append(text(W / 2, 24, "Двопровідна струмова петля 4–20 мА з живленням від лінії", size=17, bold=True))

    # Блок живлення та приймач (ліворуч)
    rx0, ry0 = 30, 55
    rw, rh = 210, 310
    f.append(rect(rx0, ry0, rw, rh, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(rx0 + rw / 2, ry0 + 22, "Щит керування (Приймач)", size=13, bold=True))

    # Джерело живлення 24 В
    f.append(circle(rx0 + 50, ry0 + 75, 18, fill="#ffffff", stroke=POS, sw=2))
    f.append(text(rx0 + 50, ry0 + 80, "+24 В", size=11, bold=True, color=POS))

    # Шунт 250 Ом
    f.append(resistor_v(rx0 + 150, ry0 + 170, 50, label="250 Ом", lblpos="right"))
    f.append(text(rx0 + 150, ry0 + 235, "0.1% ТКС", size=10, color=MUTED))
    f.append(gnd(rx0 + 150, ry0 + 250))
    f.append(line(rx0 + 50, ry0 + 93, rx0 + 50, ry0 + 250, INK, 1.8))
    f.append(line(rx0 + 50, ry0 + 250, rx0 + 150, ry0 + 250, INK, 1.8))
    f.append(gnd(rx0 + 50, ry0 + 250))

    # Вихід на АЦП
    f.append(node_dot(rx0 + 150, ry0 + 165))
    f.append(line(rx0 + 150, ry0 + 165, rx0 + 195, ry0 + 165, NEG, 1.8))
    f.append(arrow(rx0 + 175, ry0 + 165, rx0 + 195, ry0 + 165, color=NEG, sw=1.8))
    f.append(text(rx0 + 150, ry0 + 150, "1..5 В (до АЦП)", size=11, bold=True, color=NEG))

    # Вита пара
    lw_x1 = rx0 + rw
    lw_x2 = lw_x1 + 180
    y_top = ry0 + 75
    y_bot = ry0 + 165
    f.append(line(rx0 + 68, y_top, lw_x1, y_top, POS, 1.8))
    f.append(line(lw_x1, y_top, lw_x2, y_top, POS, 1.8, dash="6 3"))
    f.append(line(lw_x1, y_bot, lw_x2, y_bot, NEG, 1.8, dash="6 3"))
    f.append(text((lw_x1 + lw_x2) / 2, y_top - 12, "Кабель вита пара (до 1000 м)", size=11, bold=True))
    f.append(arrow(lw_x1 + 30, y_top - 4, lw_x1 + 80, y_top - 4, color=POS, sw=1.8))
    f.append(text(lw_x1 + 55, y_top + 16, "4–20 мА", size=11, bold=True, color=POS))

    # Давач у полі (Loop-powered transmitter)
    tx0, ty0 = lw_x2, ry0
    tw, th = 310, rh
    f.append(rect(tx0, ty0, tw, th, fill="#f2f9f4", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(tx0 + tw / 2, ty0 + 22, "Давач у полі (Передавач 4–20 мА)", size=13, bold=True, color=FIELD))

    # Внутрішнє живлення давача (LDO 3.3 В споживає < 3.5 мА)
    f.append(rect(tx0 + 25, ty0 + 55, 110, 45, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    f.append(mtext(tx0 + 80, ty0 + 72, "LDO 3.3 В\n(I_вл < 3.5 мА)", size=11, bold=True))
    f.append(line(tx0, y_top, tx0 + 25, y_top, POS, 1.8))

    # Сенсор + МК
    f.append(rect(tx0 + 25, ty0 + 125, 110, 55, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    f.append(mtext(tx0 + 80, ty0 + 147, "Сенсор тиску\n+ МК / ЦАП", size=11, bold=True))
    f.append(line(tx0 + 80, ty0 + 100, tx0 + 80, ty0 + 125, INK, 1.5))

    # Керований регулятор струму (ОП + BJT/MOSFET)
    op_cx, op_cy = tx0 + 200, ty0 + 180
    op_body, in_neg, in_pos, out_p = opamp_sym(op_cx, op_cy, w=44, h=40, invert_top=True)
    f.append(op_body)

    # ЦАП подає напругу на V+ ОП
    f.append(line(tx0 + 135, ty0 + 150, in_pos[0], in_pos[1], FIELD, 1.5))
    f.append(text(tx0 + 155, ty0 + 140, "V_dac", size=10, bold=True, color=FIELD))

    # Транзистор BJT
    bx, by = tx0 + 250, ty0 + 180
    f.append(line(out_p[0], out_p[1], bx - 10, by, INK, 1.8))
    f.append(line(bx - 10, by - 14, bx - 10, by + 14, INK, 2.2)) # база
    f.append(line(bx - 10, by - 8, bx + 10, by - 22, INK, 1.8))  # колектор
    f.append(line(bx - 10, by + 8, bx + 10, by + 22, INK, 1.8))  # емітер
    f.append(arrow(bx, by + 15, bx + 10, by + 22, color=INK, sw=1.5))

    # Колектор з'єднаний з шиною +24 В через LDO/навантаження
    f.append(line(tx0 + 135, y_top, bx + 10, y_top, POS, 1.8))
    f.append(line(bx + 10, y_top, bx + 10, by - 22, POS, 1.8))

    # Емітер на R_sense
    f.append(line(bx + 10, by + 22, bx + 10, by + 50, INK, 1.8))
    f.append(resistor_v(bx + 10, by + 50, 40, label="R_s", lblpos="right"))
    f.append(line(bx + 10, by + 90, bx + 10, ty0 + 280, INK, 1.8))
    f.append(line(bx + 10, ty0 + 280, tx0, ty0 + 280, NEG, 1.8))
    f.append(line(tx0, ty0 + 280, tx0, y_bot, NEG, 1.8))

    # Зворотний зв'язок на V- ОП
    f.append(node_dot(bx + 10, by + 40))
    f.append(line(bx + 10, by + 40, op_cx - 35, by + 40, INK, 1.5))
    f.append(line(op_cx - 35, by + 40, op_cx - 35, in_neg[1], INK, 1.5))
    f.append(line(op_cx - 35, in_neg[1], in_neg[0], in_neg[1], INK, 1.5))

    # Текст підсумку знизу (повністю поза межами верхніх блоків)
    f.append(fitbox(rx0, ry0 + rh + 20, W - 60, 65,
        "Принцип регулювання: ОП утримує I_loop · R_s = V_dac. Струм петлі змінюється від 4 до 20 мА\n"
        "незалежно від коливань напруги та опору дротів. Живлення всієї електроніки давача вкладається у 3.5 мА.",
        size=12, fill="#ffffff", stroke=LINE))

    render(os.path.join(OUT, "current-loop-4-20ma.svg"), W, H, *f)


# ── 3. Low-Side проти High-Side вимірювання струму ────────────────────────
def fig_shunt_topologies():
    W, H = 760, 420
    f = []
    f.append(text(W / 2, 24, "Топології включення шунта струму: Low-Side проти High-Side", size=17, bold=True))

    bw, bh = 340, 355
    bx1, by1 = 30, 50

    # Low-Side
    f.append(rect(bx1, by1, bw, bh, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(bx1 + bw / 2, by1 + 22, "Low-Side (Шунт біля землі)", size=14, bold=True))

    # Шина живлення V_bus
    f.append(line(bx1 + 30, by1 + 55, bx1 + 120, by1 + 55, POS, 2))
    f.append(text(bx1 + 30, by1 + 48, "+V_bus", size=11, bold=True, color=POS))
    f.append(line(bx1 + 120, by1 + 55, bx1 + 120, by1 + 75, POS, 1.8))

    # Навантаження
    f.append(rect(bx1 + 95, by1 + 75, 50, 60, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    f.append(text(bx1 + 120, by1 + 108, "Load", size=12, bold=True))
    f.append(line(bx1 + 120, by1 + 135, bx1 + 120, by1 + 155, INK, 1.8))

    # Шунт
    f.append(resistor_v(bx1 + 120, by1 + 155, 45, label="R_shunt", lblpos="left"))
    f.append(line(bx1 + 120, by1 + 200, bx1 + 120, by1 + 220, INK, 1.8))
    f.append(gnd(bx1 + 120, by1 + 220))

    # ОП підсилювач
    op_cx, op_cy = bx1 + 230, by1 + 175
    op_body, in_neg, in_pos, out_p = opamp_sym(op_cx, op_cy, w=44, h=40, invert_top=False)
    f.append(op_body)
    f.append(node_dot(bx1 + 120, by1 + 150))
    f.append(line(bx1 + 120, by1 + 150, in_pos[0], in_pos[1], POS, 1.5))
    f.append(line(in_neg[0], in_neg[1], in_neg[0] - 15, in_neg[1], INK, 1.5))
    f.append(gnd(in_neg[0] - 15, in_neg[1]))
    f.append(line(out_p[0], out_p[1], bx1 + 310, out_p[1], FIELD, 1.8))
    f.append(text(bx1 + 310, out_p[1] - 8, "V_out", size=11, bold=True, color=FIELD, anchor="end"))

    # Опис Low-Side
    f.append(fitbox(bx1 + 12, by1 + 245, bw - 24, 98,
        "Плюси: V_cm ≈ 0 В — підходить звичайний дешевий ОП.\n"
        "Мінуси: 'Підстрибування' землі навантаження на I·R_shunt,\n"
        "що спотворює зв'язок по UART/I2C. Не бачить КЗ навантаження\n"
        "на корпус (струм мине шунт).",
        size=11, fill="#ffffff", stroke=LINE))

    # High-Side
    bx2 = 390
    f.append(rect(bx2, by1, bw, bh, fill="#f2f9f4", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(bx2 + bw / 2, by1 + 22, "High-Side (Шунт у шині живлення)", size=14, bold=True, color=FIELD))

    # Шина живлення
    f.append(line(bx2 + 30, by1 + 55, bx2 + 85, by1 + 55, POS, 2))
    f.append(text(bx2 + 30, by1 + 48, "+V_bus (до 80 В)", size=11, bold=True, color=POS))

    # Шунт
    f.append(resistor_h(bx2 + 85, by1 + 55, 50, label="R_shunt", lblpos="top"))
    f.append(line(bx2 + 135, by1 + 55, bx2 + 175, by1 + 55, POS, 1.8))

    # Навантаження
    f.append(line(bx2 + 175, by1 + 55, bx2 + 175, by1 + 80, POS, 1.8))
    f.append(rect(bx2 + 150, by1 + 80, 50, 60, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    f.append(text(bx2 + 175, by1 + 113, "Load", size=12, bold=True))
    f.append(line(bx2 + 175, by1 + 140, bx2 + 175, by1 + 165, INK, 1.8))
    f.append(gnd(bx2 + 175, by1 + 165))
    f.append(text(bx2 + 175, by1 + 185, "Справжня GND", size=10, bold=True))

    # Current Sense Amplifier (INA180 / INA240)
    csa_x, csa_y = bx2 + 225, by1 + 65
    f.append(rect(csa_x, csa_y, 90, 75, fill="#ffffff", stroke=FIELD, sw=1.8, rx=6))
    f.append(mtext(csa_x + 45, csa_y + 32, "Current Sense\nAmplifier\n(INA180)", size=10, bold=True, color=FIELD))

    # Підключення Кельвіна
    f.append(node_dot(bx2 + 80, by1 + 55))
    f.append(node_dot(bx2 + 140, by1 + 55))
    f.append(line(bx2 + 80, by1 + 55, bx2 + 80, csa_y + 20, POS, 1.5))
    f.append(line(bx2 + 80, csa_y + 20, csa_x, csa_y + 20, POS, 1.5))
    f.append(line(bx2 + 140, by1 + 55, bx2 + 140, csa_y + 45, POS, 1.5))
    f.append(line(bx2 + 140, csa_y + 45, csa_x, csa_y + 45, POS, 1.5))
    f.append(text(bx2 + 105, csa_y + 15, "IN+", size=9, bold=True))
    f.append(text(bx2 + 155, csa_y + 42, "IN−", size=9, bold=True))

    # Вихід підсилювача
    f.append(line(csa_x + 90, csa_y + 35, bx2 + 330, csa_y + 35, FIELD, 1.8))
    f.append(text(bx2 + 330, csa_y + 25, "OUT (до МК)", size=10, bold=True, color=FIELD, anchor="end"))

    # Опис High-Side
    f.append(fitbox(bx2 + 12, by1 + 245, bw - 24, 98,
        "Плюси: Земля навантаження непорушна. Надійно виявляє КЗ\n"
        "навантаження на землю. Підключення Кельвіна усуває опір доріжок.\n"
        "Мінуси: Вимагає спеціалізованого підсилювача (CSA) з високим\n"
        "CMRR та синфазною напругою V_cm >> V_живлення МК.",
        size=11, fill="#ffffff", stroke=FIELD))

    render(os.path.join(OUT, "shunt-low-vs-high-side.svg"), W, H, *f)


# ── 4. Трансімпедансний підсилювач (TIA) та стабільність ──────────────────
def fig_tia_stability():
    W, H = 760, 430
    f = []
    f.append(text(W / 2, 24, "Трансімпедансний підсилювач (TIA): схема та компенсація ємності", size=17, bold=True))

    # Ліва половина: Схема TIA
    bx1, by1 = 30, 50
    bw1, bh1 = 350, 365
    f.append(rect(bx1, by1, bw1, bh1, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(bx1 + bw1 / 2, by1 + 22, "Схема TIA на фотодіоді", size=14, bold=True))

    # Фотодіод на вході
    pdx, pdy = bx1 + 55, by1 + 165
    f.append(circle(pdx, pdy, 20, fill="#ffffff", stroke=LINE, sw=1.5))
    # Стрілки світла
    f.append(arrow(pdx - 28, pdy - 25, pdx - 12, pdy - 12, color=FIELD, sw=1.5))
    f.append(arrow(pdx - 22, pdy - 32, pdx - 6, pdy - 19, color=FIELD, sw=1.5))
    # Символ діода
    f.append(line(pdx - 10, pdy + 8, pdx + 10, pdy + 8, INK, 1.8))
    f.append(line(pdx - 10, pdy - 8, pdx + 10, pdy - 8, INK, 1.8))
    f.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.5"/>' %
             (pdx - 8, pdy + 8, pdx + 8, pdy + 8, pdx, pdy - 8, FILL, INK))
    f.append(line(pdx, pdy + 20, pdx, pdy + 45, INK, 1.8))
    f.append(gnd(pdx, pdy + 45))
    f.append(line(pdx, pdy - 20, pdx, by1 + 120, INK, 1.8))
    f.append(line(pdx, by1 + 120, bx1 + 175, by1 + 120, INK, 1.8))
    f.append(arrow(bx1 + 95, by1 + 112, bx1 + 135, by1 + 112, color=POS, sw=1.8))
    f.append(text(bx1 + 115, by1 + 104, "I_pd", size=11, bold=True, color=POS))

    # Операційний підсилювач
    op_cx, op_cy = bx1 + 215, by1 + 135
    op_body, in_neg, in_pos, out_p = opamp_sym(op_cx, op_cy, w=50, h=45, invert_top=True)
    f.append(op_body)
    f.append(line(in_pos[0], in_pos[1], in_pos[0] - 15, in_pos[1], INK, 1.5))
    f.append(gnd(in_pos[0] - 15, in_pos[1]))
    f.append(text(in_pos[0] - 20, in_pos[1] - 8, "0 В", size=10, bold=True))

    # Віртуальна земля (зсуваємо напис ліворуч, щоб не перетинати вертикальний дріт)
    f.append(node_dot(bx1 + 165, by1 + 120))
    f.append(text(bx1 + 155, by1 + 140, "Віртуальна земля (0 В)", size=10, bold=True, color=NEG, anchor="end"))

    # Зворотний зв'язок: Rf та Cf паралельно
    fb_y = by1 + 65
    f.append(line(bx1 + 165, by1 + 120, bx1 + 165, fb_y, INK, 1.5))
    f.append(line(bx1 + 165, fb_y, bx1 + 185, fb_y, INK, 1.5))
    f.append(resistor_h(bx1 + 185, fb_y - 12, 50, label="R_f (1 МОм)", lblsize=10, lblpos="top"))
    f.append(line(bx1 + 185, fb_y + 12, bx1 + 200, fb_y + 12, INK, 1.5))
    f.append(cap_v(bx1 + 210, fb_y - 5, label="C_f", lblsize=10, lblpos="top"))
    f.append(line(bx1 + 210, fb_y + 29, bx1 + 235, fb_y + 29, INK, 1.5))
    f.append(line(bx1 + 235, fb_y - 12, bx1 + 255, fb_y - 12, INK, 1.5))
    f.append(line(bx1 + 235, fb_y + 29, bx1 + 255, fb_y + 29, INK, 1.5))
    f.append(line(bx1 + 255, fb_y - 12, bx1 + 255, fb_y + 29, INK, 1.5))
    f.append(line(bx1 + 255, fb_y + 8, bx1 + 275, fb_y + 8, INK, 1.5))
    f.append(line(bx1 + 275, fb_y + 8, bx1 + 275, out_p[1], INK, 1.5))
    f.append(line(out_p[0], out_p[1], bx1 + 330, out_p[1], FIELD, 1.8))
    f.append(node_dot(bx1 + 275, out_p[1]))
    f.append(text(bx1 + 330, out_p[1] - 8, "V_out = −I_pd · R_f", size=11, bold=True, color=FIELD, anchor="end"))

    # Пояснення зліва знизу
    f.append(fitbox(bx1 + 12, by1 + 245, bw1 - 24, 108,
        "Фізика роботи TIA:\n"
        "• Віртуальна земля тримає напругу на діоді = 0 В\n"
        "• Немає перезаряду ємності діода C_in сигналом\n"
        "• C_f компенсує фазовий зсув і запобігає автогенерації:\n"
        "  C_f = √( C_in / (2π · R_f · GBW) )",
        size=11, fill="#ffffff", stroke=LINE))

    # Права половина: Графік шумового підсилення (Noise Gain 1/beta)
    bx2 = 390
    bw2 = 340
    f.append(rect(bx2, by1, bw2, bh1, fill="#f2f9f4", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(bx2 + bw2 / 2, by1 + 22, "Діаграма Боде: шумове підсилення 1/β", size=13, bold=True, color=FIELD))

    # Осі графіка
    gx0, gy0 = bx2 + 45, by1 + 210
    gw, gh = 265, 140
    f.append(line(gx0, gy0, gx0 + gw, gy0, INK, 1.5))  # вісь X (частота)
    f.append(line(gx0, gy0, gx0, gy0 - gh, INK, 1.5))  # вісь Y (дБ)
    f.append(text(gx0 + gw - 10, gy0 + 16, "lg(f)", size=11, bold=True))
    f.append(text(gx0 - 10, gy0 - gh + 10, "|A|, дБ", size=11, bold=True, anchor="end"))

    # Крива підсилення ОП без ЗЗ (Aol)
    f.append(line(gx0 + 10, gy0 - 130, gx0 + 240, gy0 - 10, POS, 2))
    f.append(text(gx0 + 200, gy0 - 50, "A_ol (ОП)", size=11, bold=True, color=POS))

    # Шумове підсилення без компенсації (Cf = 0) - підйом на +20 дБ/дек до перетину
    f.append(line(gx0, gy0 - 20, gx0 + 60, gy0 - 20, NEG, 1.8))
    f.append(line(gx0 + 60, gy0 - 20, gx0 + 185, gy0 - 95, NEG, 1.8, dash="4 3"))
    f.append(text(gx0 + 195, gy0 - 100, "Без C_f (генерація!)", size=10, bold=True, color=NEG))
    f.append(circle(gx0 + 175, gy0 - 90, 6, fill="none", stroke=NEG, sw=2))

    # Шумове підсилення з компенсацією Cf - вирівнювання на частоті f_z
    f.append(line(gx0 + 60, gy0 - 20, gx0 + 120, gy0 - 60, FIELD, 2))
    f.append(line(gx0 + 120, gy0 - 60, gx0 + 210, gy0 - 60, FIELD, 2))
    f.append(text(gx0 + 155, gy0 - 70, "З компенсацією C_f", size=10, bold=True, color=FIELD))

    # Позначки частот f_p та f_z
    f.append(line(gx0 + 60, gy0, gx0 + 60, gy0 - 20, LINE, 1, dash="2 2"))
    f.append(text(gx0 + 60, gy0 + 15, "f_p1", size=10, bold=True))
    f.append(line(gx0 + 120, gy0, gx0 + 120, gy0 - 60, LINE, 1, dash="2 2"))
    f.append(text(gx0 + 120, gy0 + 15, "f_z", size=10, bold=True))

    # Опис графіка
    f.append(fitbox(bx2 + 12, by1 + 245, bw2 - 24, 108,
        "Без Cf вхідна ємність створює нуль у 1/β (f_p1), підсилення\n"
        "зростає на +20 дБ/дек, і на перетині з A_ol швидкість закриття\n"
        "становить 40 дБ/дек (фазовий запас 0° → автогенерація).\n"
        "Конденсатор Cf вводить полюс f_z, стабілізуючи петлю.",
        size=11, fill="#ffffff", stroke=FIELD))

    render(os.path.join(OUT, "tia-circuit-stability.svg"), W, H, *f)


# ── 5. Струмові дзеркала та генератори струму ─────────────────────────────
def fig_current_mirrors():
    W, H = 760, 420
    f = []
    f.append(text(W / 2, 24, "Генератори стабільного струму та струмові дзеркала", size=17, bold=True))

    bw, bh = 340, 355
    bx1, by1 = 30, 50

    # Ліва половина: Кероване джерело струму на ОП та BJT
    f.append(rect(bx1, by1, bw, bh, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(bx1 + bw / 2, by1 + 22, "1. Прецизійне джерело струму (sink)", size=13, bold=True))

    # Навантаження в колекторі
    f.append(line(bx1 + 210, by1 + 50, bx1 + 210, by1 + 70, POS, 1.8))
    f.append(text(bx1 + 210, by1 + 45, "+V_cc", size=11, bold=True, color=POS))
    f.append(rect(bx1 + 185, by1 + 70, 50, 50, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    f.append(text(bx1 + 210, by1 + 98, "Load", size=11, bold=True))
    f.append(line(bx1 + 210, by1 + 120, bx1 + 210, by1 + 140, INK, 1.8))

    # Транзистор BJT NPN
    tx, ty = bx1 + 210, by1 + 155
    f.append(line(tx - 20, ty - 12, tx - 20, ty + 12, INK, 2.2)) # база
    f.append(line(tx - 20, ty - 8, tx, ty - 18, INK, 1.8))       # колектор
    f.append(line(tx - 20, ty + 8, tx, ty + 18, INK, 1.8))       # емітер
    f.append(arrow(tx - 10, ty + 13, tx, ty + 18, color=INK, sw=1.5))
    f.append(line(tx, ty - 18, tx, by1 + 140, INK, 1.8))

    # Резистор емітера
    f.append(line(tx, ty + 18, tx, by1 + 185, INK, 1.8))
    f.append(resistor_v(tx, by1 + 185, 40, label="R_e", lblpos="right"))
    f.append(line(tx, by1 + 225, tx, by1 + 245, INK, 1.8))
    f.append(gnd(tx, by1 + 245))

    # ОП
    op_cx, op_cy = bx1 + 120, by1 + 155
    op_body, in_neg, in_pos, out_p = opamp_sym(op_cx, op_cy, w=44, h=40, invert_top=True)
    f.append(op_body)
    f.append(line(out_p[0], out_p[1], tx - 20, ty, INK, 1.8))

    # Опорна напруга V_ref на V+
    f.append(line(bx1 + 35, in_pos[1], in_pos[0], in_pos[1], FIELD, 1.8))
    f.append(text(bx1 + 35, in_pos[1] - 8, "V_ref", size=11, bold=True, color=FIELD))

    # Зворотний зв'язок з емітера на V-
    f.append(node_dot(tx, by1 + 180))
    f.append(line(tx, by1 + 180, bx1 + 75, by1 + 180, INK, 1.5))
    f.append(line(bx1 + 75, by1 + 180, bx1 + 75, in_neg[1], INK, 1.5))
    f.append(line(bx1 + 75, in_neg[1], in_neg[0], in_neg[1], INK, 1.5))

    # Опис
    f.append(fitbox(bx1 + 12, by1 + 255, bw - 24, 88,
        "ОП утримує напругу на емітері рівною V_ref.\n"
        "Струм навантаження I = V_ref / R_e є абсолютно стабільним\n"
        "і не залежить від опору Load та напруги V_cc.",
        size=11, fill="#ffffff", stroke=LINE))

    # Права половина: Струмове дзеркало на BJT (Matched Pair)
    bx2 = 390
    f.append(rect(bx2, by1, bw, bh, fill="#f2f9f4", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(bx2 + bw / 2, by1 + 22, "2. Струмове дзеркало (Current Mirror)", size=13, bold=True, color=FIELD))

    # Шина живлення
    f.append(line(bx2 + 60, by1 + 50, bx2 + 280, by1 + 50, POS, 1.8))
    f.append(text(bx2 + 40, by1 + 54, "+V_cc", size=11, bold=True, color=POS))

    # Еталонна гілка з R_ref
    f.append(line(bx2 + 90, by1 + 50, bx2 + 90, by1 + 75, POS, 1.8))
    f.append(resistor_v(bx2 + 90, by1 + 75, 45, label="R_ref", lblpos="left"))
    f.append(arrow(bx2 + 105, by1 + 75, bx2 + 105, by1 + 115, color=POS, sw=1.5))
    f.append(text(bx2 + 120, by1 + 95, "I_ref", size=11, bold=True, color=POS))

    # Транзистор Q1 (діодне включення)
    q1_x, q1_y = bx2 + 90, by1 + 160
    f.append(line(q1_x - 15, q1_y - 12, q1_x - 15, q1_y + 12, INK, 2.2))
    f.append(line(q1_x - 15, q1_y - 8, q1_x, q1_y - 18, INK, 1.8))
    f.append(line(q1_x - 15, q1_y + 8, q1_x, q1_y + 18, INK, 1.8))
    f.append(arrow(q1_x - 8, q1_y + 13, q1_x, q1_y + 18, color=INK, sw=1.5))
    f.append(line(q1_x, by1 + 120, q1_x, q1_y - 18, INK, 1.8))
    f.append(line(q1_x, q1_y + 18, q1_x, by1 + 225, INK, 1.8))
    f.append(gnd(q1_x, by1 + 225))
    # Закоротка колектор-база Q1
    f.append(node_dot(q1_x, q1_y - 10))
    f.append(line(q1_x, q1_y - 10, q1_x - 30, q1_y - 10, INK, 1.5))
    f.append(line(q1_x - 30, q1_y - 10, q1_x - 30, q1_y, INK, 1.5))
    f.append(line(q1_x - 30, q1_y, q1_x - 15, q1_y, INK, 1.5))
    f.append(text(q1_x - 18, q1_y + 25, "Q1", size=12, bold=True))

    # З'єднання баз Q1 та Q2
    q2_x, q2_y = bx2 + 240, by1 + 160
    f.append(line(q1_x - 15, q1_y, q2_x - 15, q2_y, FIELD, 1.8))
    f.append(text((q1_x + q2_x) / 2 - 15, q1_y - 8, "V_be однакова", size=10, bold=True, color=FIELD))

    # Транзистор Q2 (вихідне дзеркало)
    f.append(line(q2_x - 15, q2_y - 12, q2_x - 15, q2_y + 12, INK, 2.2))
    f.append(line(q2_x - 15, q2_y - 8, q2_x, q2_y - 18, INK, 1.8))
    f.append(line(q2_x - 15, q2_y + 8, q2_x, q2_y + 18, INK, 1.8))
    f.append(arrow(q2_x - 8, q2_y + 13, q2_x, q2_y + 18, color=INK, sw=1.5))
    f.append(line(q2_x, q2_y + 18, q2_x, by1 + 225, INK, 1.8))
    f.append(gnd(q2_x, by1 + 225))
    f.append(text(q2_x + 18, q2_y + 25, "Q2", size=12, bold=True))

    # Навантаження у вихідній гілці
    f.append(line(bx2 + 240, by1 + 50, bx2 + 240, by1 + 75, POS, 1.8))
    f.append(rect(bx2 + 215, by1 + 75, 50, 45, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    f.append(text(bx2 + 240, by1 + 101, "Load", size=11, bold=True))
    f.append(line(bx2 + 240, by1 + 120, bx2 + 240, q2_y - 18, INK, 1.8))
    f.append(arrow(bx2 + 255, by1 + 75, bx2 + 255, by1 + 115, color=FIELD, sw=1.5))
    f.append(text(bx2 + 295, by1 + 95, "I_out ≈ I_ref", size=11, bold=True, color=FIELD, anchor="end"))

    # Опис
    f.append(fitbox(bx2 + 12, by1 + 255, bw - 24, 88,
        "Принцип струмового дзеркала:\n"
        "Струм I_ref задає напругу V_be на діодному транзисторі Q1.\n"
        "Оскільки база Q2 під'єднана туди ж, Q2 відтворює точну копію\n"
        "струму I_out = I_ref незалежно від напруги на навантаженні.",
        size=11, fill="#ffffff", stroke=FIELD))

    render(os.path.join(OUT, "current-mirror-basic.svg"), W, H, *f)


if __name__ == "__main__":
    fig_voltage_vs_current()
    fig_current_loop_4_20ma()
    fig_shunt_topologies()
    fig_tia_stability()
    fig_current_mirrors()
    print("Усі 5 фігур успішно згенеровано в %s" % OUT)
