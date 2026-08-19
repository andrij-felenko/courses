# -*- coding: utf-8 -*-
"""Фігури до статті «Шумове підсилення (noise gain)» (book/electronics/analog/noise-gain).

Фігури:
  signal-vs-noise-gain.svg    — порівняння шляху сигналу та шляху внутрішнього шуму/зсуву: для власного шуму схема завжди неінвертувальна
  bode-rate-of-closure.svg    — графік Боде для A(f) та 1/beta: петльове підсилення, смуга f_cl = GBP/NG та швидкість зближення (ROC)
  noise-gain-peaking-tia.svg  — ємність на вході ОП / фотодіод: сплеск 1/beta, загроза самозбудження та компенсація через Cf
  noise-gain-manipulation.svg — стабілізація декомпенсованого ОП: штучне завищення шумового підсилення резистором Rdummy між входами

Запуск: python figs.py -> генерує SVG у ./img/
"""
import sys, os

# 4 рівні вгору до кореня репо / scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def opamp_symbol(cx, cy, scale=1.0):
    """Малює трикутник ОП із входами + (знизу або зверху) та - і виходом."""
    w = 60 * scale
    h = 60 * scale
    x1, y1 = cx - w / 2, cy - h / 2
    x2, y2 = cx - w / 2, cy + h / 2
    x3, y3 = cx + w / 2, cy
    pts = f"{x1:.1f},{y1:.1f} {x2:.1f},{y2:.1f} {x3:.1f},{y3:.1f}"
    out = [f'<polygon points="{pts}" fill="#ffffff" stroke="{INK}" stroke-width="2"/>']
    # Знаки + та -
    out.append(text(cx - w / 2 + 12 * scale, cy - h / 4 + 4 * scale, "−", size=int(16 * scale), color=NEG, bold=True))
    out.append(text(cx - w / 2 + 12 * scale, cy + h / 4 + 4 * scale, "+", size=int(14 * scale), color=POS, bold=True))
    return "".join(out)


# ════════════════════════════════════════════════════════════════════════════
# 1. signal-vs-noise-gain.svg: сигнал проти внутрішнього шуму/зсуву
# ════════════════════════════════════════════════════════════════════════════
def fig_signal_vs_noise_gain():
    W, H = 760, 420
    f = []

    # Заголовок / розділювач на дві колонки
    f.append(line(W / 2, 20, W / 2, H - 20, color=MUTED, sw=1.2, dash="5 5"))

    # ── Ліва половина: Шлях зовнішнього сигналу (інвертувальний підсилювач) ──
    f.append(text(W / 4, 32, "Шлях корисного сигналу", size=15, bold=True, color=INK))
    f.append(text(W / 4, 52, "Gсигн = −Rf / Rin  (може бути < 1)", size=12, color=NEG, bold=True))

    lx, ly = 230, 190
    f.append(opamp_symbol(lx, ly, scale=1.1))

    # Входи ОП
    in_neg_y = ly - 15
    in_pos_y = ly + 15
    out_x = lx + 33
    in_x = lx - 33

    # Неінвертувальний вхід (+) на землю
    f.append(line(in_x, in_pos_y, in_x - 30, in_pos_y, color=INK, sw=1.8))
    f.append(line(in_x - 30, in_pos_y, in_x - 30, in_pos_y + 25, color=INK, sw=1.8))
    # земля
    f.append(line(in_x - 42, in_pos_y + 25, in_x - 18, in_pos_y + 25, color=INK, sw=2))
    f.append(line(in_x - 37, in_pos_y + 29, in_x - 23, in_pos_y + 29, color=INK, sw=1.5))
    f.append(line(in_x - 33, in_pos_y + 33, in_x - 27, in_pos_y + 33, color=INK, sw=1))

    # Інвертувальний вхід (-) через Rin до Vin
    f.append(line(in_x, in_neg_y, in_x - 50, in_neg_y, color=INK, sw=1.8))
    # Резистор Rin
    rx1, rx2 = in_x - 100, in_x - 50
    f.append(rect(rx1, in_neg_y - 10, 50, 20, fill="#ffffff", stroke=INK, sw=1.8))
    f.append(text((rx1 + rx2) / 2, in_neg_y - 14, "Rin", size=12, bold=True))
    f.append(arrow(rx1 - 40, in_neg_y, rx1, in_neg_y, color=NEG, sw=2))
    f.append(text(rx1 - 45, in_neg_y - 12, "Uвх", size=13, color=NEG, bold=True, anchor="end"))

    # Вузол інвертувального входу (віртуальний нуль)
    f.append(circle(in_x - 35, in_neg_y, 3.5, fill=INK, stroke=INK))
    f.append(text(in_x - 35, in_neg_y + 18, "вірт. 0", size=10, color=MUTED))

    # Зворотний зв'язок Rf
    f.append(line(in_x - 35, in_neg_y, in_x - 35, in_neg_y - 65, color=INK, sw=1.8))
    f.append(line(in_x - 35, in_neg_y - 65, lx - 25, in_neg_y - 65, color=INK, sw=1.8))
    f.append(rect(lx - 25, in_neg_y - 75, 50, 20, fill="#ffffff", stroke=INK, sw=1.8))
    f.append(text(lx, in_neg_y - 80, "Rf", size=12, bold=True))
    f.append(line(lx + 25, in_neg_y - 65, out_x + 35, in_neg_y - 65, color=INK, sw=1.8))
    f.append(line(out_x + 35, in_neg_y - 65, out_x + 35, ly, color=INK, sw=1.8))

    # Вихід
    f.append(line(out_x, ly, out_x + 65, ly, color=INK, sw=2))
    f.append(circle(out_x + 35, ly, 3.5, fill=INK, stroke=INK))
    f.append(arrow(out_x + 65, ly, out_x + 85, ly, color=NEG, sw=2))
    f.append(text(out_x + 92, ly - 8, "Uвих", size=13, color=NEG, bold=True, anchor="start"))

    # Пояснення знизу зліва
    body_l, _, _ = textbox(W / 4, 345,
                           "Сигнал іде на мінус-вхід.\nВихід: Uвих = −(Rf / Rin) · Uвх\nПідсилення сигналу може бути < 1 (атенюатор).",
                           size=11, fill="#f4f6f8", stroke=NEG)
    f.append(body_l)

    # ── Права половина: Шлях внутрішнього шуму / зміщення Vos ──
    f.append(text(3 * W / 4, 32, "Шлях внутрішнього шуму та Vos", size=15, bold=True, color=INK))
    f.append(text(3 * W / 4, 52, "Gшум = 1 + Rf / Rin = 1/β  (завжди ≥ 1)", size=12, color=POS, bold=True))

    rx_c, ry_c = 3 * W / 4 + 40, 190
    f.append(opamp_symbol(rx_c, ry_c, scale=1.1))

    rin_neg_y = ry_c - 15
    rin_pos_y = ry_c + 15
    rout_x = rx_c + 33
    rin_x = rx_c - 33

    # Джерело шуму e_n / Vos на неінвертувальному вході
    f.append(line(rin_x, rin_pos_y, rin_x - 20, rin_pos_y, color=INK, sw=1.8))
    # кружечок джерела
    f.append(circle(rin_x - 38, rin_pos_y, 14, fill="#ffffff", stroke=POS, sw=2))
    f.append(text(rin_x - 38, rin_pos_y + 4, "en, Vos", size=10, color=POS, bold=True))
    f.append(line(rin_x - 52, rin_pos_y, rin_x - 70, rin_pos_y, color=INK, sw=1.8))
    f.append(line(rin_x - 70, rin_pos_y, rin_x - 70, rin_pos_y + 25, color=INK, sw=1.8))
    # земля
    f.append(line(rin_x - 82, rin_pos_y + 25, rin_x - 58, rin_pos_y + 25, color=INK, sw=2))
    f.append(line(rin_x - 77, rin_pos_y + 29, rin_x - 63, rin_pos_y + 29, color=INK, sw=1.5))
    f.append(line(rin_x - 73, rin_pos_y + 33, rin_x - 67, rin_pos_y + 33, color=INK, sw=1))

    # Інвертувальний вхід (-) через Rin ЗАЗЕМЛЕНИЙ (бо для шуму вхід сигналу = 0)
    f.append(line(rin_x, rin_neg_y, rin_x - 50, rin_neg_y, color=INK, sw=1.8))
    rrx1, rrx2 = rin_x - 100, rin_x - 50
    f.append(rect(rrx1, rin_neg_y - 10, 50, 20, fill="#ffffff", stroke=INK, sw=1.8))
    f.append(text((rrx1 + rrx2) / 2, rin_neg_y - 14, "Rin", size=12, bold=True))
    f.append(line(rrx1, rin_neg_y, rrx1 - 25, rin_neg_y, color=INK, sw=1.8))
    f.append(line(rrx1 - 25, rin_neg_y, rrx1 - 25, rin_neg_y + 25, color=INK, sw=1.8))
    # земля входу Rin
    f.append(line(rrx1 - 37, rin_neg_y + 25, rrx1 - 13, rin_neg_y + 25, color=INK, sw=2))
    f.append(line(rrx1 - 32, rin_neg_y + 29, rrx1 - 18, rin_neg_y + 29, color=INK, sw=1.5))
    f.append(line(rrx1 - 28, rin_neg_y + 33, rrx1 - 22, rin_neg_y + 33, color=INK, sw=1))
    f.append(text(rrx1 - 25, rin_neg_y - 10, "0 В (AC)", size=10, color=MUTED, anchor="middle"))

    # Вузол зворотного зв'язку
    f.append(circle(rin_x - 35, rin_neg_y, 3.5, fill=INK, stroke=INK))

    # Зворотний зв'язок Rf
    f.append(line(rin_x - 35, rin_neg_y, rin_x - 35, rin_neg_y - 65, color=INK, sw=1.8))
    f.append(line(rin_x - 35, rin_neg_y - 65, rx_c - 25, rin_neg_y - 65, color=INK, sw=1.8))
    f.append(rect(rx_c - 25, rin_neg_y - 75, 50, 20, fill="#ffffff", stroke=INK, sw=1.8))
    f.append(text(rx_c, rin_neg_y - 80, "Rf", size=12, bold=True))
    f.append(line(rx_c + 25, rin_neg_y - 65, rout_x + 35, rin_neg_y - 65, color=INK, sw=1.8))
    f.append(line(rout_x + 35, rin_neg_y - 65, rout_x + 35, ry_c, color=INK, sw=1.8))

    # Вихід
    f.append(line(rout_x, ry_c, rout_x + 65, ry_c, color=INK, sw=2))
    f.append(circle(rout_x + 35, ry_c, 3.5, fill=INK, stroke=INK))
    f.append(arrow(rout_x + 65, ry_c, rout_x + 85, ry_c, color=POS, sw=2))
    f.append(text(rout_x + 92, ry_c - 8, "Uвих,шум", size=13, color=POS, bold=True, anchor="start"))

    # Пояснення знизу справа
    body_r, _, _ = textbox(3 * W / 4, 345,
                           "Для власного джерела шуму вхід заглушено (0 В).\nДільник Rin-Rf діє як у неінвертувальній схемі!\nUвих,шум = (1 + Rf / Rin) · en = (1/β) · en",
                           size=11, fill="#fdecea", stroke=POS)
    f.append(body_r)

    render(os.path.join(IMG, "signal-vs-noise-gain.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. bode-rate-of-closure.svg: Графік Боде, смуга GBP/NG і швидкість зближення ROC
# ════════════════════════════════════════════════════════════════════════════
def fig_bode_rate_of_closure():
    W, H = 760, 440
    f = []

    ox, oy = 80, 360
    axw, axh = 620, 300

    # Осі
    f.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.8))
    f.append(text(ox + axw - 10, oy + 26, "частота f (лог. шкала)", size=12, color=INK, anchor="end"))
    f.append(text(ox - 14, oy - axh + 10, "Підсилення, дБ", size=12, color=INK, bold=True, anchor="end"))

    # Рівень 0 дБ
    y0db = oy - 20
    f.append(line(ox, y0db, ox + axw - 20, y0db, color=MUTED, sw=1.2, dash="5 5"))
    f.append(text(ox - 10, y0db + 4, "0 дБ", size=11, color=MUTED, anchor="end"))

    # Крива A(f) — власне підсилення ОП: поличка 100 дБ до fp, далі спад -20 дБ/дек
    y_a0 = oy - 270
    x_fp = ox + 90
    x_unity = ox + 550

    f.append(line(ox, y_a0, x_fp, y_a0, color=FIELD, sw=2.6))
    f.append(line(x_fp, y_a0, x_unity, y0db, color=FIELD, sw=2.6))
    f.append(line(x_unity, y0db, ox + axw - 20, y0db + 30, color=FIELD, sw=2.6))
    f.append(text(ox + 45, y_a0 - 10, "A(f) (відкритий контур)", size=12, color=FIELD, bold=True))
    f.append(text(x_fp + 100, y_a0 + 60, "спад −20 дБ/дек", size=11, color=FIELD))

    # ft / GBP
    f.append(circle(x_unity, y0db, 4, fill=FIELD, stroke=FIELD))
    f.append(line(x_unity, y0db, x_unity, oy, color=FIELD, sw=1.2, dash="3 3"))
    f.append(text(x_unity, oy + 18, "GBP (ft)", size=11, color=FIELD, bold=True))

    # Крива 1/beta 1: Стійка плоска крива шумового підсилення NG = 20 дБ (×10)
    y_ng1 = oy - 160
    # перетин з A(f): лінія A(f) йде від (x_fp, y_a0) до (x_unity, y0db)
    slope = (y0db - y_a0) / (x_unity - x_fp)
    x_cross1 = x_fp + (y_ng1 - y_a0) / slope

    f.append(line(ox, y_ng1, x_cross1, y_ng1, color=NEG, sw=2.4))
    f.append(circle(x_cross1, y_ng1, 5, fill="#ffffff", stroke=NEG, sw=2.4))
    f.append(text(ox + 70, y_ng1 - 10, "1/β = NG = 20 дБ (×10)", size=12, color=NEG, bold=True))

    # Проєкція частоти зрізу замкненого кола f_cl = GBP / NG
    f.append(line(x_cross1, y_ng1, x_cross1, oy, color=NEG, sw=1.4, dash="4 4"))
    f.append(text(x_cross1, oy + 18, "fзрізу = GBP / NG", size=11, color=NEG, bold=True))

    # Петльове підсилення T = A·β (відстань між A та 1/β)
    mid_x = (x_fp + x_cross1) / 2
    mid_y_a = y_a0 + (mid_x - x_fp) * slope
    f.append(arrow(mid_x, y_ng1, mid_x, mid_y_a, color=INK, sw=1.8))
    f.append(arrow(mid_x, mid_y_a, mid_x, y_ng1, color=INK, sw=1.8))
    body_t, _, _ = textbox(mid_x - 65, (y_ng1 + mid_y_a) / 2, "Петльове\nпідсилення\nT = A·β (дБ)", size=10, fill="#eef2ff", stroke=NEG)
    f.append(body_t)

    # Кут зближення (ROC) для стійкого випадку
    f.append(text(x_cross1 + 80, y_ng1 - 25, "ROC = 20 дБ/дек\n(стійко, запас фази ≈ 90°)", size=11, color=FIELD, bold=True))
    f.append(arrow(x_cross1 + 40, y_ng1 - 15, x_cross1 + 8, y_ng1 - 4, color=FIELD, sw=1.6))

    # Крива 1/beta 2: Нестійка зростаюча крива (+20 дБ/дек через нуль 1/beta від ємності на вході)
    y_ng2_start = oy - 60
    x_zero = ox + 150
    x_cross2 = (y_ng2_start - y_a0 + x_zero * slope + x_fp * slope) / (2 * slope)
    y_cross2 = y_ng2_start - (x_cross2 - x_zero) * slope

    f.append(line(ox, y_ng2_start, x_zero, y_ng2_start, color=POS, sw=2, dash="6 4"))
    f.append(line(x_zero, y_ng2_start, x_cross2 + 50, y_cross2 - 50 * slope, color=POS, sw=2.4))
    f.append(circle(x_cross2, y_cross2, 5, fill="#ffffff", stroke=POS, sw=2.4))
    f.append(text(x_zero + 40, y_ng2_start + 18, "+20 дБ/дек (нуль у 1/β)", size=10, color=POS, bold=True))

    # Підпис нестійкого перетину (ROC = 40 дБ/дек)
    body_roc, _, _ = textbox(x_cross2 + 95, y_cross2 + 25,
                             "ROC = 40 дБ/дек!\nЗапас фази → 0°\n(дзвін / самозбудження)",
                             size=11, fill="#fdecea", stroke=POS)
    f.append(body_roc)
    f.append(arrow(x_cross2 + 25, y_cross2 + 15, x_cross2 + 6, y_cross2 + 3, color=POS, sw=1.6))

    render(os.path.join(IMG, "bode-rate-of-closure.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 3. noise-gain-peaking-tia.svg: Ємність на вході, сплеск 1/beta та компенсація Cf
# ════════════════════════════════════════════════════════════════════════════
def fig_noise_gain_peaking_tia():
    W, H = 760, 430
    f = []

    ox, oy = 80, 360
    axw, axh = 620, 290

    # Осі
    f.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.8))
    f.append(text(ox + axw - 10, oy + 26, "частота f (лог)", size=12, color=INK, anchor="end"))
    f.append(text(ox - 14, oy - axh + 10, "|1/β|, дБ", size=12, color=INK, bold=True, anchor="end"))

    # A(f) ОП (сіра фонова лінія)
    y_a0 = oy - 250
    x_fp = ox + 80
    x_unity = ox + 540
    y0db = oy - 20
    slope = (y0db - y_a0) / (x_unity - x_fp)

    f.append(line(ox, y_a0, x_fp, y_a0, color=MUTED, sw=1.8, dash="4 4"))
    f.append(line(x_fp, y_a0, x_unity, y0db, color=MUTED, sw=2, dash="4 4"))
    f.append(text(x_fp + 130, y_a0 + 45, "A(f) ОП (−20 дБ/дек)", size=11, color=MUTED))

    # Базовий рівень 1/beta на НЧ (0 дБ для TIA або 1+Rf/Rin)
    y_dc = oy - 50
    x_fz = ox + 140
    f.append(line(ox, y_dc, x_fz, y_dc, color=INK, sw=2))
    f.append(text(ox + 50, y_dc - 10, "1/β = 0 дБ (1)", size=11, color=INK))

    # Некомпенсована крива (червона) — продовжує зростати до перетину з A(f)
    x_cross_uncomp = (y_dc - y_a0 + x_fz * slope + x_fp * slope) / (2 * slope)
    y_cross_uncomp = y_dc - (x_cross_uncomp - x_fz) * slope

    f.append(line(x_fz, y_dc, x_cross_uncomp + 40, y_cross_uncomp - 40 * slope, color=POS, sw=2.4))
    f.append(circle(x_cross_uncomp, y_cross_uncomp, 5, fill="#ffffff", stroke=POS, sw=2.4))
    f.append(text(x_fz, oy + 18, "fz = 1/(2π·Rf·Cin)", size=10, color=POS, bold=True))
    f.append(line(x_fz, y_dc, x_fz, oy, color=POS, sw=1.2, dash="3 3"))

    body_uncomp, _, _ = textbox(x_cross_uncomp - 40, y_cross_uncomp - 55,
                                "Без компенсації (Cf = 0):\nперетин на 40 дБ/дек → генерація,\nвелетенський шумовий пік!",
                                size=11, fill="#fdecea", stroke=POS)
    f.append(body_uncomp)

    # Компенсована крива (зелена) — Cf створює полюс fp = 1/(2π·Rf·Cf) і згладжує поличку
    x_fp_comp = ox + 280
    y_comp_flat = y_dc - (x_fp_comp - x_fz) * slope

    f.append(line(x_fz, y_dc, x_fp_comp, y_comp_flat, color=FIELD, sw=2.6))
    # після fp_comp крива йде горизонтально до перетину з A(f)
    x_cross_comp = x_fp + (y_comp_flat - y_a0) / slope
    f.append(line(x_fp_comp, y_comp_flat, x_cross_comp, y_comp_flat, color=FIELD, sw=2.6))
    f.append(circle(x_cross_comp, y_comp_flat, 5, fill="#ffffff", stroke=FIELD, sw=2.6))

    f.append(text(x_fp_comp, oy + 18, "fp = 1/(2π·Rf·Cf)", size=10, color=FIELD, bold=True))
    f.append(line(x_fp_comp, y_comp_flat, x_fp_comp, oy, color=FIELD, sw=1.2, dash="3 3"))

    body_comp, _, _ = textbox(x_cross_comp + 80, y_comp_flat + 50,
                              "З конденсатором Cf:\n1/β вирівнюється,\nROC = 20 дБ/дек (стійко),\nшум придушено.",
                              size=11, fill="#eef7f0", stroke=FIELD)
    f.append(body_comp)
    f.append(arrow(x_cross_comp + 20, y_comp_flat + 25, x_cross_comp + 6, y_comp_flat + 4, color=FIELD, sw=1.6))

    render(os.path.join(IMG, "noise-gain-peaking-tia.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 4. noise-gain-manipulation.svg: Стабілізація декомпенсованого ОП (Rdummy)
# ════════════════════════════════════════════════════════════════════════════
def fig_noise_gain_manipulation():
    W, H = 760, 420
    f = []

    # ── Ліва частина: Принципова схема з Rdummy + Cdummy між входами ──
    f.append(text(190, 32, "Схема штучного завищення NG", size=15, bold=True, color=INK))

    lx, ly = 210, 190
    f.append(opamp_symbol(lx, ly, scale=1.1))

    in_neg_y = ly - 15
    in_pos_y = ly + 15
    out_x = lx + 33
    in_x = lx - 33

    # Неінвертувальний вхід (+) на землю
    f.append(line(in_x, in_pos_y, in_x - 30, in_pos_y, color=INK, sw=1.8))
    f.append(line(in_x - 30, in_pos_y, in_x - 30, in_pos_y + 40, color=INK, sw=1.8))
    # земля
    f.append(line(in_x - 42, in_pos_y + 40, in_x - 18, in_pos_y + 40, color=INK, sw=2))
    f.append(line(in_x - 37, in_pos_y + 44, in_x - 23, in_pos_y + 44, color=INK, sw=1.5))
    f.append(line(in_x - 33, in_pos_y + 48, in_x - 27, in_pos_y + 48, color=INK, sw=1))

    # Інвертувальний вхід (-) через Rin до Uвх
    f.append(line(in_x, in_neg_y, in_x - 50, in_neg_y, color=INK, sw=1.8))
    rx1, rx2 = in_x - 100, in_x - 50
    f.append(rect(rx1, in_neg_y - 10, 50, 20, fill="#ffffff", stroke=INK, sw=1.8))
    f.append(text((rx1 + rx2) / 2, in_neg_y - 14, "Rin", size=12, bold=True))
    f.append(arrow(rx1 - 35, in_neg_y, rx1, in_neg_y, color=NEG, sw=2))
    f.append(text(rx1 - 40, in_neg_y - 12, "Uвх", size=13, color=NEG, bold=True, anchor="end"))

    # Вузол на інвертувальному вході
    f.append(circle(in_x - 35, in_neg_y, 3.5, fill=INK, stroke=INK))
    # Вузол на неінвертувальному вході
    f.append(circle(in_x - 30, in_pos_y, 3.5, fill=INK, stroke=INK))

    # Ланцюг стабілізації Rdummy + Cdummy між входами + та -
    # Йде вертикально між вузлом інвертувального та неінвертувального
    cx_stab = in_x - 15
    f.append(line(in_x - 35, in_neg_y, cx_stab, in_neg_y, color=POS, sw=1.8))
    f.append(line(cx_stab, in_neg_y, cx_stab, in_neg_y + 8, color=POS, sw=1.8))
    # Резистор Rd
    f.append(rect(cx_stab - 8, in_neg_y + 8, 16, 26, fill="#fdecea", stroke=POS, sw=1.8))
    f.append(text(cx_stab + 14, in_neg_y + 24, "Rш", size=11, color=POS, bold=True, anchor="start"))
    # Конденсатор Cd
    f.append(line(cx_stab, in_neg_y + 34, cx_stab, in_neg_y + 44, color=POS, sw=1.8))
    f.append(line(cx_stab - 10, in_neg_y + 44, cx_stab + 10, in_neg_y + 44, color=POS, sw=2))
    f.append(line(cx_stab - 10, in_neg_y + 48, cx_stab + 10, in_neg_y + 48, color=POS, sw=2))
    f.append(text(cx_stab + 14, in_neg_y + 50, "Cш", size=11, color=POS, bold=True, anchor="start"))
    f.append(line(cx_stab, in_neg_y + 48, cx_stab, in_pos_y, color=POS, sw=1.8))
    f.append(line(cx_stab, in_pos_y, in_x - 30, in_pos_y, color=POS, sw=1.8))

    # Зворотний зв'язок Rf
    f.append(line(in_x - 35, in_neg_y, in_x - 35, in_neg_y - 65, color=INK, sw=1.8))
    f.append(line(in_x - 35, in_neg_y - 65, lx - 25, in_neg_y - 65, color=INK, sw=1.8))
    f.append(rect(lx - 25, in_neg_y - 75, 50, 20, fill="#ffffff", stroke=INK, sw=1.8))
    f.append(text(lx, in_neg_y - 80, "Rf", size=12, bold=True))
    f.append(line(lx + 25, in_neg_y - 65, out_x + 35, in_neg_y - 65, color=INK, sw=1.8))
    f.append(line(out_x + 35, in_neg_y - 65, out_x + 35, ly, color=INK, sw=1.8))

    # Вихід
    f.append(line(out_x, ly, out_x + 65, ly, color=INK, sw=2))
    f.append(circle(out_x + 35, ly, 3.5, fill=INK, stroke=INK))
    f.append(arrow(out_x + 65, ly, out_x + 85, ly, color=NEG, sw=2))
    f.append(text(out_x + 92, ly - 8, "Uвих", size=13, color=NEG, bold=True, anchor="start"))

    body_sch, _, _ = textbox(190, 350,
                             "Rш || Cш стоять між вірт. нулем і землею:\nСтрум сигналу через них = 0 (Gсигн не змінюється!),\nале зворотна частка β падає → NG зростає на ВЧ.",
                             size=11, fill="#f4f6f8", stroke=INK)
    f.append(body_sch)

    # ── Права частина: Графік частотних характеристик ──
    f.append(text(570, 32, "Підсилення сигналу проти шуму", size=15, bold=True, color=INK))

    gox, goy = 440, 280
    gaxw, gaxh = 280, 210

    f.append(arrow(gox, goy, gox + gaxw, goy, color=INK, sw=1.8))
    f.append(arrow(gox, goy, gox, goy - gaxh, color=INK, sw=1.8))
    f.append(text(gox + gaxw - 10, goy + 24, "частота f (лог)", size=11, color=INK, anchor="end"))
    f.append(text(gox - 10, goy - gaxh + 10, "дБ", size=11, color=INK, bold=True, anchor="end"))

    # Постійне підсилення сигналу |G_signal| = -Rf/Rin = 0 дБ (×1)
    y_sig = goy - 40
    f.append(line(gox, y_sig, gox + 200, y_sig, color=NEG, sw=2.4))
    f.append(line(gox + 200, y_sig, gox + 260, y_sig + 60, color=NEG, sw=2.4))
    f.append(text(gox + 80, y_sig - 10, "|Gсигн| = 1 (0 дБ)", size=11, color=NEG, bold=True))

    # Крива шумового підсилення NG(f):
    # На НЧ: NG = 1 + Rf/Rin = 2 (6 дБ)
    # На ВЧ: через Cш підключається Rш, і NG зростає до 1 + Rf/(Rin||Rш) = 14 дБ (×5)
    y_ng_low = goy - 60
    y_ng_high = goy - 150
    x_step_start = gox + 70
    x_step_end = gox + 140

    f.append(line(gox, y_ng_low, x_step_start, y_ng_low, color=POS, sw=2.4))
    f.append(line(x_step_start, y_ng_low, x_step_end, y_ng_high, color=POS, sw=2.4))
    f.append(line(x_step_end, y_ng_high, gox + 230, y_ng_high, color=POS, sw=2.4))

    f.append(text(gox + 45, y_ng_low - 10, "NG(НЧ) = 2", size=10, color=POS))
    f.append(text(gox + 180, y_ng_high - 10, "NG(ВЧ) = 5 (≥ NGмін)", size=11, color=POS, bold=True))

    # A(f) декомпенсованого ОП
    f.append(line(gox + 160, goy - 190, gox + 250, goy - 40, color=FIELD, sw=2, dash="4 4"))
    f.append(circle(gox + 215, y_ng_high, 4, fill=FIELD, stroke=FIELD))
    f.append(text(gox + 200, goy - 180, "A(f) ОП", size=11, color=FIELD, bold=True))

    body_res, _, _ = textbox(570, 360,
                             "ОП бачить NG = 5 у точці перетину з A(f) → не збуджується!\nКорисний сигнал не послаблюється і проходить без спотворень.",
                             size=11, fill="#eef7f0", stroke=FIELD)
    f.append(body_res)

    render(os.path.join(IMG, "noise-gain-manipulation.svg"), W, H, *f)


if __name__ == "__main__":
    fig_signal_vs_noise_gain()
    fig_bode_rate_of_closure()
    fig_noise_gain_peaking_tia()
    fig_noise_gain_manipulation()
    print("OK: всі 4 фігури згенеровано у", IMG)
