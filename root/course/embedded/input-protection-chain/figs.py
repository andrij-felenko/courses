# -*- coding: utf-8 -*-
"""Фігури до теми «Захист входу: полярність, перенапруга, кидок».
Запуск:  python figs.py   → створює SVG-файли у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def ground_sym(cx, y, color=LINE, sw=1.6):
    """Символ землі GND (3 горизонтальні риски)."""
    out = line(cx, y, cx, y + 6, color=color, sw=sw)
    for i, w in enumerate((16, 10, 4)):
        out += line(cx - w / 2, y + 6 + i * 4, cx + w / 2, y + 6 + i * 4, color=color, sw=sw)
    return out


def tvs_sym_v(cx, ty, by, color=INK, sw=1.8):
    """Вертикальний TVS-супресор (зустрічно-послідовний або однонапрямлений зенероподібний)."""
    h = 20
    midy = (ty + by) / 2
    out = line(cx, ty, cx, midy - h / 2, color=color, sw=sw)
    out += line(cx, by, cx, midy + h / 2, color=color, sw=sw)
    # трикутник анода
    tri = "%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (cx - 9, midy + h / 2, cx + 9, midy + h / 2, cx, midy - h / 2)
    out += '<polygon points="%s" fill="#fdecea" stroke="%s" stroke-width="%.1f"/>' % (tri, color, sw)
    # катодна планка з гачками
    ky = midy - h / 2
    out += line(cx - 10, ky, cx + 10, ky, color=color, sw=sw + 0.5)
    out += line(cx - 10, ky, cx - 10, ky - 4, color=color, sw=sw)
    out += line(cx + 10, ky, cx + 10, ky + 4, color=color, sw=sw)
    return out


def mov_sym_v(cx, ty, by, color=INK, sw=1.8):
    """Символ варистора (прямокутник із діагональною лінією зі зламом)."""
    w, h = 18, 30
    midy = (ty + by) / 2
    out = line(cx, ty, cx, midy - h / 2, color=color, sw=sw)
    out += line(cx, by, cx, midy + h / 2, color=color, sw=sw)
    out += rect(cx - w / 2, midy - h / 2, w, h, fill="#fef9e7", stroke=color, sw=sw, rx=2)
    # риска зі зламом через варистор
    out += line(cx - w / 2 - 5, midy + h / 2 + 4, cx + w / 2 + 5, midy - h / 2 - 4, color=color, sw=sw)
    out += line(cx + w / 2 + 5, midy - h / 2 - 4, cx + w / 2 + 10, midy - h / 2 - 4, color=color, sw=sw)
    return out


# ── 1. Ієрархія багатокаскадного вхідного захисту ──────────────────────────────
def fig_input_hierarchy():
    W, H = 840, 360
    f = [text(W / 2, 24, "Багатокаскадна ієрархія захисту лінії живлення (Power Protection Chain)",
              size=15, bold=True)]

    # Координати шин
    v_in_y = 120
    gnd_y = 260
    x_start = 50
    x_end = 790

    # Основні шини
    f.append(line(x_start, v_in_y, x_end, v_in_y, color=POS, sw=2.2))
    f.append(line(x_start, gnd_y, x_end, gnd_y, color=NEG, sw=2.2))
    f.append(text(x_start - 25, v_in_y + 5, "+VIN", size=12, bold=True, color=POS))
    f.append(text(x_start - 25, gnd_y + 5, "GND", size=12, bold=True, color=NEG))
    f.append(text(x_end + 25, v_in_y + 5, "+VOUT", size=12, bold=True, color=POS))
    f.append(text(x_end + 25, gnd_y + 5, "GND", size=12, bold=True, color=NEG))

    # Каскади по осі X
    # 1. Запобіжник (Fuse/PTC)
    x_fuse = 115
    f.append(rect(x_fuse - 22, v_in_y - 12, 44, 24, fill="#ffffff", stroke=POS, sw=2, rx=3))
    f.append(line(x_fuse - 18, v_in_y, x_fuse + 18, v_in_y, color=POS, sw=1.5))
    b, _, _ = textbox(x_fuse, v_in_y - 42, "1. Струмовий захист\nFuse / PTC", size=10, fill="#fdedec", stroke=POS, bold=True)
    f.append(b)

    # 2. Варистор (MOV)
    x_mov = 210
    f.append(mov_sym_v(x_mov, v_in_y, gnd_y, color=LINE, sw=1.8))
    b, _, _ = textbox(x_mov, gnd_y + 35, "2. Грубий Surge\nMOV (джоулі)", size=10, fill="#fef9e7", stroke=LINE, bold=True)
    f.append(b)

    # 3. Розв'язувальний дросель L_d
    x_ind = 305
    f.append(rect(x_ind - 22, v_in_y - 14, 44, 28, fill="#ffffff", stroke=LINE, sw=2, rx=3))
    f.append(text(x_ind, v_in_y + 4, "L_d", size=11, bold=True, color=LINE))
    b, _, _ = textbox(x_ind, v_in_y - 42, "3. Розв'язка L_d\n10–22 мкГн (dI/dt)", size=10, fill="#f4f6f8", stroke=LINE, bold=True)
    f.append(b)

    # 4. Прецизійний TVS
    x_tvs = 400
    f.append(tvs_sym_v(x_tvs, v_in_y, gnd_y, color=FIELD, sw=1.8))
    b, _, _ = textbox(x_tvs, gnd_y + 35, "4. Точний кламп\nTVS (<1 нс, V_C)", size=10, fill="#eafaf1", stroke=FIELD, bold=True)
    f.append(b)

    # 5. Захист від переполюсування (Reverse Polarity - Ideal Diode / P-FET)
    x_rev = 510
    f.append(rect(x_rev - 32, v_in_y - 20, 64, 40, fill="#ffffff", stroke=POS, sw=2, rx=4))
    f.append(text(x_rev, v_in_y + 4, "Ideal Diode\n(MOSFET)", size=10, bold=True, color=POS))
    b, _, _ = textbox(x_rev, v_in_y - 42, "5. Переполюсовка\nQ_rev (P-FET / IC)", size=10, fill="#fdedec", stroke=POS, bold=True)
    f.append(b)

    # 6. Обмеження пуску та вимикач OVP (eFuse / Soft-Start)
    x_efuse = 640
    f.append(rect(x_efuse - 35, v_in_y - 20, 70, 40, fill="#ffffff", stroke=FIELD, sw=2, rx=4))
    f.append(text(x_efuse, v_in_y + 4, "eFuse / OVP\n+ Soft-Start", size=10, bold=True, color=FIELD))
    b, _, _ = textbox(x_efuse, v_in_y - 42, "6. Пуск + OVP\nTPS2595 / SoftStart", size=10, fill="#eafaf1", stroke=FIELD, bold=True)
    f.append(b)

    # 7. Вихідна накопичувальна ємність (C_bulk)
    x_cap = 740
    f.append(line(x_cap, v_in_y, x_cap, v_in_y + 45, color=POS, sw=1.8))
    f.append(line(x_cap, gnd_y, x_cap, gnd_y - 45, color=NEG, sw=1.8))
    f.append(line(x_cap - 12, v_in_y + 45, x_cap + 12, v_in_y + 45, color=LINE, sw=2.5))
    f.append(line(x_cap - 12, gnd_y - 45, x_cap + 12, gnd_y - 45, color=LINE, sw=2.5))
    b, _, _ = textbox(x_cap, gnd_y + 35, "7. Буферна ємність\nC_bulk (DC-DC)", size=10, fill="#f4f6f8", stroke=LINE, bold=True)
    f.append(b)

    # Хвиля перешкоди на вході
    f.append(arrow(x_start - 10, v_in_y + 35, x_start + 45, v_in_y + 35, color=POS, sw=2))
    f.append(text(x_start + 18, v_in_y + 52, "Сплески, реверс,\nкидки струму", size=9.5, color=POS, bold=True))

    render(os.path.join(IMG, "input-protection-hierarchy.svg"), W, H, *f)


# ── 2. Порівняння схем захисту від переполюсування ────────────────────────────
def fig_reverse_polarity():
    W, H = 840, 320
    f = [text(W / 2, 22, "Топології захисту від переполюсовки: діод Шотткі проти P-MOSFET та контролера",
              size=15, bold=True)]

    # Три колонки
    # Схема A: Послідовний Шотткі
    xa = 140
    ya = 60
    f.append(rect(xa - 110, ya, 220, 230, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    f.append(text(xa, ya + 22, "А) Діод Шотткі (пасивний)", size=12, bold=True, color=POS))
    f.append(line(xa - 85, ya + 75, xa - 20, ya + 75, color=POS, sw=2))
    f.append(line(xa + 20, ya + 75, xa + 85, ya + 75, color=POS, sw=2))
    # Діод Шотткі
    tri = "%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (xa - 15, ya + 65, xa - 15, ya + 85, xa + 15, ya + 75)
    f.append('<polygon points="%s" fill="#fdecea" stroke="%s" stroke-width="2"/>' % (tri, POS))
    f.append(line(xa + 15, ya + 63, xa + 15, ya + 87, color=POS, sw=2))
    f.append(line(xa + 15, ya + 63, xa + 19, ya + 63, color=POS, sw=1.8))
    f.append(line(xa + 15, ya + 87, xa + 11, ya + 87, color=POS, sw=1.8))
    f.append(line(xa - 85, ya + 155, xa + 85, ya + 155, color=NEG, sw=2))
    f.append(text(xa - 85, ya + 65, "+VIN", size=10, bold=True, color=POS))
    f.append(text(xa + 85, ya + 65, "+VOUT", size=10, bold=True, color=POS))
    f.append(text(xa, ya + 110, "V_drop = 0.4–0.6 В", size=11, bold=True, color=POS))
    f.append(text(xa, ya + 130, "Втрати: P = I · V_f (1.5 Вт @ 3А)", size=9.5, color=MUTED))
    f.append(text(xa, ya + 190, "Високий зворотний витік\nпри нагріванні (>1 мА)", size=10, color=POS, bold=True))

    # Схема B: P-MOSFET
    xb = 420
    f.append(rect(xb - 130, ya, 260, 230, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    f.append(text(xb, ya + 22, "Б) P-MOSFET (High-Side)", size=12, bold=True, color=FIELD))
    # Лінії живлення
    f.append(line(xb - 105, ya + 65, xb - 35, ya + 65, color=POS, sw=2))
    f.append(line(xb + 35, ya + 65, xb + 105, ya + 65, color=POS, sw=2))
    f.append(line(xb - 105, ya + 155, xb + 105, ya + 155, color=NEG, sw=2))
    # Символ P-MOSFET (Source зліва, Drain справа, Gate знизу)
    f.append(rect(xb - 35, ya + 50, 70, 30, fill="#eafaf1", stroke=FIELD, sw=2, rx=4))
    f.append(text(xb, ya + 69, "P-FET (S→D)", size=11, bold=True, color=FIELD))
    # Затвор і підтяжка
    f.append(line(xb - 15, ya + 80, xb - 15, ya + 155, color=LINE, sw=1.5))
    f.append(rect(xb - 22, ya + 105, 14, 28, fill="#ffffff", stroke=LINE, sw=1.5, rx=2))
    f.append(text(xb - 40, ya + 122, "R_g\n100k", size=9, bold=True, color=LINE))
    # Стабілітрон захисту затвора (між S і G)
    f.append(line(xb - 30, ya + 65, xb - 30, ya + 100, color=LINE, sw=1.4))
    f.append(line(xb - 30, ya + 100, xb - 15, ya + 100, color=LINE, sw=1.4))
    f.append(text(xb - 45, ya + 88, "Dz 12V", size=9, color=FIELD))
    f.append(text(xb, ya + 185, "V_drop = I · R_DS(on) ≈ 30 мВ\nВтрати: P = 90 мВт @ 3А (R=10мОм)", size=10, bold=True, color=FIELD))
    f.append(text(xb, ya + 215, "Мінус: пропускає зворотний струм", size=9.5, color=MUTED))

    # Схема C: Контролер ідеального діода
    xc = 705
    f.append(rect(xc - 120, ya, 240, 230, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    f.append(text(xc, ya + 22, "В) Контролер (N-FET + Pump)", size=12, bold=True, color=FIELD))
    f.append(line(xc - 95, ya + 65, xc - 35, ya + 65, color=POS, sw=2))
    f.append(line(xc + 35, ya + 65, xc + 95, ya + 65, color=POS, sw=2))
    f.append(line(xc - 95, ya + 155, xc + 95, ya + 155, color=NEG, sw=2))
    # N-FET блок
    f.append(rect(xc - 35, ya + 50, 70, 30, fill="#eafaf1", stroke=FIELD, sw=2, rx=4))
    f.append(text(xc, ya + 69, "N-FET", size=11, bold=True, color=FIELD))
    # Мікросхема контролера (LM74610 / MAX16171)
    f.append(rect(xc - 40, ya + 95, 80, 45, fill="#f4f6f8", stroke=LINE, sw=1.8, rx=4))
    f.append(text(xc, ya + 115, "Ideal Diode IC\nLM74610", size=10, bold=True, color=LINE))
    f.append(line(xc, ya + 95, xc, ya + 80, color=FIELD, sw=1.6))
    f.append(text(xc + 15, ya + 90, "GATE", size=9.5, color=FIELD))
    f.append(text(xc, ya + 185, "Наднизький R_DS(on) N-каналу\nМиттєве вимикання (<0.5 мкс)", size=10, bold=True, color=FIELD))
    f.append(text(xc, ya + 215, "Повний захист від зворотного струму", size=9.5, color=MUTED))

    render(os.path.join(IMG, "reverse-polarity-schemes.svg"), W, H, *f)


# ── 3. Координація енергії Surge: Fuse + MOV + L_d + TVS ───────────────────────
def fig_surge_coordination():
    W, H = 820, 340
    f = [text(W / 2, 22, "Координація імпульсного захисту: розподіл енергії між MOV та TVS через L_d",
              size=15, bold=True)]

    # Схема каскаду зверху
    y_top = 70
    f.append(line(80, y_top, 740, y_top, color=POS, sw=2.2))
    f.append(line(80, y_top + 100, 740, y_top + 100, color=NEG, sw=2.2))
    f.append(text(50, y_top + 4, "+VIN", size=11, bold=True, color=POS))
    f.append(text(50, y_top + 104, "GND", size=11, bold=True, color=NEG))

    # Варистор
    x_m = 220
    f.append(mov_sym_v(x_m, y_top, y_top + 100, color=LINE, sw=1.8))
    f.append(text(x_m, y_top - 12, "MOV (56V)", size=11, bold=True, color=LINE))

    # Дросель
    x_l = 380
    f.append(rect(x_l - 25, y_top - 14, 50, 28, fill="#ffffff", stroke=LINE, sw=2, rx=3))
    f.append(text(x_l, y_top + 4, "L_d 22μH", size=10.5, bold=True, color=LINE))
    f.append(text(x_l, y_top - 24, "V_L = L · (dI/dt)", size=11, bold=True, color=POS))

    # TVS
    x_t = 540
    f.append(tvs_sym_v(x_t, y_top, y_top + 100, color=FIELD, sw=1.8))
    f.append(text(x_t, y_top - 12, "TVS (SMBJ33A)", size=11, bold=True, color=FIELD))

    # Навантаження DC-DC
    x_load = 680
    f.append(rect(x_load - 25, y_top + 15, 50, 70, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=4))
    f.append(text(x_load, y_top + 52, "DC-DC\nLoad", size=10, bold=True, color=LINE))

    # Пояснювальні блоки внизу
    yb = 210
    # Блок 1: Без дроселя
    f.append(rect(80, yb, 310, 105, fill="#fdedec", stroke=POS, sw=1.5, rx=6))
    f.append(text(235, yb + 20, "БЕЗ розв'язки L_d (помилка):", size=11.5, bold=True, color=POS))
    f.append(text(235, yb + 42, "• TVS відкривається при V_BR ≈ 36 В", size=10, color=INK))
    f.append(text(235, yb + 62, "• Напруга лінії затиснута нижче 56 В (порогу MOV)", size=10, color=INK))
    f.append(text(235, yb + 84, "• TVS бере 100% енергії сплеску і вибухає!", size=10.5, bold=True, color=POS))

    # Блок 2: З дроселем
    f.append(rect(430, yb, 330, 105, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=6))
    f.append(text(595, yb + 20, "З дроселем L_d (координовано):", size=11.5, bold=True, color=FIELD))
    f.append(text(595, yb + 42, "• TVS затискає напругу виходу на рівні ~38 В", size=10, color=INK))
    f.append(text(595, yb + 62, "• Струм dI/dt створює спад V_L на L_d (+20 В)", size=10, color=INK))
    f.append(text(595, yb + 84, "• V_MOV = V_TVS + V_L > 56 В → MOV гасить 95%!", size=10.5, bold=True, color=FIELD))

    render(os.path.join(IMG, "surge-coordination-energy.svg"), W, H, *f)


# ── 4. Активний плавний пуск (Soft-Start) на P-MOSFET ──────────────────────────
def fig_inrush_softstart():
    W, H = 820, 330
    f = [text(W / 2, 22, "Активне обмеження пускового струму (Soft-Start) на інтеграторі Міллера",
              size=15, bold=True)]

    # Схема зліва
    xs = 50
    ys = 60
    f.append(rect(xs, ys, 360, 240, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    f.append(text(xs + 180, ys + 22, "Схема плавного пуску на P-MOSFET", size=12, bold=True, color=FIELD))

    # Шини
    f.append(line(xs + 30, ys + 60, xs + 120, ys + 60, color=POS, sw=2))
    f.append(line(xs + 220, ys + 60, xs + 330, ys + 60, color=POS, sw=2))
    f.append(line(xs + 30, ys + 200, xs + 330, ys + 200, color=NEG, sw=2))
    f.append(text(xs + 20, ys + 60, "+VIN", size=10, bold=True, color=POS))
    f.append(text(xs + 340, ys + 60, "+VOUT", size=10, bold=True, color=POS))
    f.append(text(xs + 20, ys + 200, "GND", size=10, bold=True, color=NEG))

    # P-FET транзистор
    f.append(rect(xs + 120, ys + 45, 100, 30, fill="#eafaf1", stroke=FIELD, sw=2, rx=4))
    f.append(text(xs + 170, ys + 64, "P-FET (Q1)", size=11, bold=True, color=FIELD))

    # Затворні ланцюги
    # R_pullup до землі
    f.append(line(xs + 140, ys + 75, xs + 140, ys + 200, color=LINE, sw=1.5))
    f.append(rect(xs + 133, ys + 115, 14, 30, fill="#ffffff", stroke=LINE, sw=1.5, rx=2))
    f.append(text(xs + 105, ys + 132, "R_g\n100k", size=9, bold=True, color=LINE))

    # Міллерівський конденсатор C_gd (між Drain і Gate)
    f.append(line(xs + 245, ys + 60, xs + 245, ys + 110, color=FIELD, sw=1.6))
    f.append(line(xs + 140, ys + 110, xs + 245, ys + 110, color=FIELD, sw=1.6))
    f.append(rect(xs + 180, ys + 102, 26, 16, fill="#ffffff", stroke=FIELD, sw=1.6, rx=2))
    f.append(text(xs + 193, ys + 94, "C_gd (Міллер) 100 нФ", size=9.5, bold=True, color=FIELD))

    # Вихідний конденсатор C_load
    f.append(line(xs + 300, ys + 60, xs + 300, ys + 100, color=POS, sw=1.6))
    f.append(line(xs + 300, ys + 200, xs + 300, ys + 160, color=NEG, sw=1.6))
    f.append(line(xs + 290, ys + 100, xs + 310, ys + 100, color=LINE, sw=2.2))
    f.append(line(xs + 290, ys + 160, xs + 310, ys + 160, color=LINE, sw=2.2))
    f.append(text(xs + 300, ys + 132, "C_load\n470 μF", size=9.5, bold=True, color=LINE))

    # Графіки перехідного процесу справа
    xg = 440
    yg = 60
    f.append(rect(xg, yg, 340, 240, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    f.append(text(xg + 170, yg + 22, "Осцилограма пуску (Inrush Plateau)", size=12, bold=True, color=INK))

    # Осі
    f.append(line(xg + 40, yg + 190, xg + 310, yg + 190, color=LINE, sw=1.5))  # вісь t
    f.append(line(xg + 40, yg + 45, xg + 40, yg + 190, color=LINE, sw=1.5))   # вісь V/I
    f.append(text(xg + 315, yg + 194, "t", size=11, bold=True, color=LINE))

    # Крива V_OUT (лінійне наростання)
    f.append('<path d="M %d %d L %d %d L %d %d L %d %d" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (xg + 40, yg + 190, xg + 80, yg + 190, xg + 220, yg + 70, xg + 290, yg + 70, POS))
    f.append(text(xg + 245, yg + 65, "V_OUT (24V)", size=10, bold=True, color=POS))

    # Крива струму I_inrush (прямокутний імпульс постійного струму)
    f.append('<path d="M %d %d L %d %d L %d %d L %d %d L %d %d" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="4,3"/>'
             % (xg + 40, yg + 190, xg + 80, yg + 190, xg + 80, yg + 120, xg + 220, yg + 120, xg + 220, yg + 190, FIELD))
    f.append(text(xg + 150, yg + 110, "I_inrush = C · (dV/dt) = 0.8 A", size=10, bold=True, color=FIELD))

    # Часова мітка t_rise
    f.append(line(xg + 80, yg + 200, xg + 220, yg + 200, color=MUTED, sw=1.2))
    f.append(text(xg + 150, yg + 215, "t_rise ≈ 14 мс", size=10, bold=True, color=MUTED))
    f.append(text(xg + 170, yg + 232, "Без схеми: піковий I > 80 A за 50 мкс!", size=9.5, color=POS, bold=True))

    render(os.path.join(IMG, "inrush-softstart-miller.svg"), W, H, *f)


# ── 5. Захист від перенапруги: Crowbar проти eFuse ─────────────────────────────
def fig_crowbar_vs_efuse():
    W, H = 840, 310
    f = [text(W / 2, 22, "Захист від постійної перенапруги (OVP): Crowbar (тиристор) vs eFuse (TPS2595)",
              size=15, bold=True)]

    # Ліва колонка: Crowbar
    xa = 50
    ya = 60
    f.append(rect(xa, ya, 350, 225, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    f.append(text(xa + 175, ya + 22, "А) Тиристорний Crowbar (жорстке замикання)", size=11.5, bold=True, color=POS))
    # Шини
    f.append(line(xa + 25, ya + 65, xa + 110, ya + 65, color=POS, sw=2))
    f.append(line(xa + 110, ya + 65, xa + 325, ya + 65, color=POS, sw=2))
    f.append(line(xa + 25, ya + 155, xa + 325, ya + 155, color=NEG, sw=2))
    # Запобіжник
    f.append(rect(xa + 55, ya + 53, 35, 24, fill="#ffffff", stroke=POS, sw=1.8, rx=2))
    f.append(text(xa + 72, ya + 45, "Fuse", size=10, bold=True, color=POS))
    # Тиристор (SCR)
    x_scr = xa + 180
    f.append(line(x_scr, ya + 65, x_scr, ya + 155, color=LINE, sw=1.8))
    f.append(rect(x_scr - 18, ya + 95, 36, 30, fill="#fdedec", stroke=POS, sw=1.8, rx=3))
    f.append(text(x_scr, ya + 114, "SCR", size=10, bold=True, color=POS))
    # Стабілітрон керування
    f.append(line(xa + 130, ya + 65, xa + 130, ya + 110, color=LINE, sw=1.4))
    f.append(line(xa + 130, ya + 110, x_scr - 18, ya + 110, color=LINE, sw=1.4))
    f.append(text(xa + 115, ya + 95, "Dz\n33V", size=9.5, color=LINE))
    # Опис
    f.append(text(xa + 175, ya + 180, "• При V > 33V тиристор закорочує шину на GND", size=9.5, color=INK))
    f.append(text(xa + 175, ya + 198, "• Спалює запобіжник (Fuse) за мілісекунди", size=9.5, color=INK))
    f.append(text(xa + 175, ya + 216, "Мінус: одноразовий ремонтний випадок", size=9.5, bold=True, color=POS))

    # Права колонка: eFuse
    xb = 440
    f.append(rect(xb, ya, 350, 225, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    f.append(text(xb + 175, ya + 22, "Б) Електронний ключ eFuse (TPS2595)", size=11.5, bold=True, color=FIELD))
    # Шини
    f.append(line(xb + 25, ya + 65, xb + 100, ya + 65, color=POS, sw=2))
    f.append(line(xb + 240, ya + 65, xb + 325, ya + 65, color=POS, sw=2))
    f.append(line(xb + 25, ya + 155, xb + 325, ya + 155, color=NEG, sw=2))
    # eFuse IC
    f.append(rect(xb + 100, ya + 45, 140, 75, fill="#eafaf1", stroke=FIELD, sw=2, rx=5))
    f.append(text(xb + 170, ya + 68, "eFuse IC (TPS2595)", size=11, bold=True, color=FIELD))
    f.append(text(xb + 170, ya + 86, "MOSFET + OVP + CurrentLimit", size=9.5, color=MUTED))
    f.append(text(xb + 170, ya + 104, "Час відсікання: < 2 мкс", size=9.5, bold=True, color=FIELD))
    # Сигнал FLT до МК
    f.append(line(xb + 170, ya + 120, xb + 170, ya + 155, color=LINE, sw=1.4))
    f.append(text(xb + 195, ya + 140, "FLT → MCU", size=9.5, color=LINE))
    # Опис
    f.append(text(xb + 175, ya + 180, "• Миттєве розмикання ключа при V_in > V_ovp", size=9.5, color=INK))
    f.append(text(xb + 175, ya + 198, "• Не руйнує схему, авто-відновлення (Auto-Retry)", size=9.5, color=INK))
    f.append(text(xb + 175, ya + 216, "Плюс: багаторазовий активний захист + моніторинг", size=9.5, bold=True, color=FIELD))

    render(os.path.join(IMG, "crowbar-vs-efuse.svg"), W, H, *f)


if __name__ == "__main__":
    fig_input_hierarchy()
    fig_reverse_polarity()
    fig_surge_coordination()
    fig_inrush_softstart()
    fig_crowbar_vs_efuse()
    print("Всі фігури згенеровано успішно.")
