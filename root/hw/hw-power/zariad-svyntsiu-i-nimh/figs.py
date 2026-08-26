# -*- coding: utf-8 -*-
"""Фігури до теми «Заряд свинцю й NiMH».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Профіль IUoU для свинцево-кислотного акумулятора ───────────────────────
def fig_iuou():
    W, H = 840, 450
    f = [text(W / 2, 26, "Три стадії заряду свинцево-кислотного акумулятора (профіль IUoU, 12 В)",
              size=15, bold=True)]

    ox, oy = 80, 360
    span_x = 680
    top = 68

    # Осі
    f.append(line(ox, oy, ox + span_x, oy, color=MUTED, sw=1.4))
    f.append(line(ox, oy, ox, top, color=MUTED, sw=1.4))
    f.append(line(ox + span_x, oy, ox + span_x, top, color=MUTED, sw=1.4))
    f.append(text(ox + span_x / 2, oy + 42, "Час заряду (t) →", size=12, color=INK, anchor="middle", bold=True))

    # Вертикальні межі фаз
    x_bulk = ox + int(span_x * 0.38)
    x_abs  = ox + int(span_x * 0.72)

    # Фонова заливка фаз
    f.append(rect(ox, top, x_bulk - ox, oy - top, fill="#f4f7fc", stroke="none", rx=0))
    f.append(rect(x_bulk, top, x_abs - x_bulk, oy - top, fill="#fbf8f2", stroke="none", rx=0))
    f.append(rect(x_abs, top, ox + span_x - x_abs, oy - top, fill="#f2f9f4", stroke="none", rx=0))

    f.append(line(x_bulk, top, x_bulk, oy, color=MUTED, sw=1.2, dash="4,4"))
    f.append(line(x_abs, top, x_abs, oy, color=MUTED, sw=1.2, dash="4,4"))

    # Заголовки фаз
    f.append(text((ox + x_bulk) / 2, top + 20, "1. Bulk (I)", size=13, bold=True, color=NEG))
    f.append(text((ox + x_bulk) / 2, top + 36, "Сталий струм (0.1–0.2C)", size=10.5, color=MUTED))

    f.append(text((x_bulk + x_abs) / 2, top + 20, "2. Absorption (Uo)", size=13, bold=True, color=POS))
    f.append(text((x_bulk + x_abs) / 2, top + 36, "Стала напруга (14.4 В)", size=10.5, color=MUTED))

    f.append(text((x_abs + ox + span_x) / 2, top + 20, "3. Float (U)", size=13, bold=True, color=FIELD))
    f.append(text((x_abs + ox + span_x) / 2, top + 36, "Буферний підзаряд (13.6 В)", size=10.5, color=MUTED))

    # Напруга: шкала від 11.5 В (oy) до 15.0 В (top + 40)
    def v_to_y(v):
        return oy - (v - 11.5) / (15.0 - 11.5) * (oy - (top + 40))

    # Струм: шкала від 0 (oy) до I_max (top + 50)
    def i_to_y(i_rel):
        return oy - i_rel * (oy - (top + 50))

    # Рівні напруги
    y_14_4 = v_to_y(14.4)
    y_13_6 = v_to_y(13.6)
    y_12_0 = v_to_y(12.0)

    f.append(line(ox, y_14_4, ox + span_x, y_14_4, color=POS, sw=0.9, dash="3,3"))
    f.append(text(ox - 8, y_14_4 + 4, "14.4 В", size=11, color=POS, anchor="end", bold=True))

    f.append(line(ox, y_13_6, ox + span_x, y_13_6, color=FIELD, sw=0.9, dash="3,3"))
    f.append(text(ox - 8, y_13_6 + 4, "13.6 В", size=11, color=FIELD, anchor="end", bold=True))

    f.append(text(ox - 8, y_12_0 + 4, "12.0 В", size=10.5, color=MUTED, anchor="end"))
    f.append(text(ox - 10, top + 15, "Напруга (В)", size=11.5, color=POS, anchor="end", bold=True))

    # Струм підписи справа
    f.append(text(ox + span_x + 10, i_to_y(1.0) + 4, "I_max (0.1C)", size=11, color=NEG, anchor="start", bold=True))
    f.append(text(ox + span_x + 10, i_to_y(0.05) + 4, "I_tail (C/50)", size=10.5, color=MUTED, anchor="start"))
    f.append(text(ox + span_x + 10, top + 15, "Струм (А)", size=11.5, color=NEG, anchor="start", bold=True))

    # Побудова кривих
    v_pts = []
    i_pts = []

    steps = 200
    for s in range(steps + 1):
        x = ox + s * span_x / steps
        if x <= x_bulk:
            # Bulk: струм сталий (1.0), напруга росте від 11.8 до 14.4
            t_rel = (x - ox) / (x_bulk - ox)
            v = 11.8 + (14.4 - 11.8) * math.sqrt(t_rel)
            i_val = 1.0
        elif x <= x_abs:
            # Absorption: напруга 14.4, струм спадає від 1.0 до 0.05
            t_rel = (x - x_bulk) / (x_abs - x_bulk)
            v = 14.4
            i_val = 0.05 + 0.95 * math.exp(-3.5 * t_rel)
        else:
            # Float: напруга 13.6, струм мізерний (~0.02)
            t_rel = (x - x_abs) / (ox + span_x - x_abs)
            v = 13.6
            i_val = 0.02
        v_pts.append((x, v_to_y(v)))
        i_pts.append((x, i_to_y(i_val)))

    # Малюємо криві
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
             % (" ".join("%.1f,%.1f" % p for p in v_pts), POS))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" stroke-dasharray="7,3"/>'
             % (" ".join("%.1f,%.1f" % p for p in i_pts), NEG))

    # Підписи до кривих
    f.append(text(ox + 80, v_to_y(12.8) - 14, "Напруга U(t)", size=12, color=POS, bold=True))
    f.append(text(ox + 80, i_to_y(1.0) - 10, "Струм I(t)", size=12, color=NEG, bold=True))

    # Стрілки й примітки переходів
    f.append(circle(x_bulk, y_14_4, 4, fill=BG, stroke=POS, sw=2))
    f.append(text(x_bulk, y_14_4 - 10, "U = 14.4 В", size=10.5, color=POS, anchor="middle", bold=True))

    f.append(circle(x_abs, i_to_y(0.05), 4, fill=BG, stroke=NEG, sw=2))
    f.append(text(x_abs - 10, i_to_y(0.05) - 12, "I < I_tail", size=10.5, color=NEG, anchor="end", bold=True))

    # Підсумковий бокс
    b, _, _ = textbox(W / 2, 424,
                      "Bulk дає ~80% заряду; Absorption розчиняє залишки PbSO4; Float компенсує саморозряд роками",
                      size=11, fill=FILL, stroke=MUTED)
    f.append(b)

    render(os.path.join(IMG, "iuou-profile.svg"), W, H, *f)


# ── 2. Температурна компенсація свинцю ────────────────────────────────────────
def fig_temp_comp():
    W, H = 820, 440
    f = [text(W / 2, 26, "Температурна компенсація напруги свинцевого акумулятора (−24 мВ/°C, 12 В)",
              size=15, bold=True)]

    ox, oy = 80, 360
    span_x = 660
    top = 66

    f.append(line(ox, oy, ox + span_x, oy, color=MUTED, sw=1.4))
    f.append(line(ox, oy, ox, top, color=MUTED, sw=1.4))
    f.append(text(ox + span_x / 2, oy + 42, "Температура електроліту (°C) →", size=12, color=INK, anchor="middle", bold=True))
    f.append(text(ox - 10, top + 15, "Напруга заряду (В)", size=11.5, color=INK, anchor="end", bold=True))

    # Шкала X: від -20°C до +50°C (діапазон 70°C)
    def t_to_x(t_c):
        return ox + (t_c - (-20)) / 70.0 * span_x

    # Шкала Y: від 12.5 В до 16.0 В (діапазон 3.5 В)
    def v_to_y(v):
        return oy - (v - 12.5) / 3.5 * (oy - top)

    # Відмітки по X
    for t_val in [-20, -10, 0, 10, 20, 25, 30, 40, 50]:
        x = t_to_x(t_val)
        f.append(line(x, oy, x, oy + 5, color=MUTED, sw=1.0))
        is_ref = (t_val == 25)
        col = POS if is_ref else MUTED
        f.append(text(x, oy + 18, "%d°" % t_val, size=10.5, color=col, bold=is_ref))
        if is_ref:
            f.append(line(x, top, x, oy, color=POS, sw=1.0, dash="3,3"))

    # Відмітки по Y
    for v_val in [13.0, 13.5, 14.0, 14.5, 15.0, 15.5]:
        y = v_to_y(v_val)
        f.append(line(ox - 5, y, ox, y, color=MUTED, sw=1.0))
        f.append(text(ox - 8, y + 4, "%.1f" % v_val, size=10.5, color=MUTED, anchor="end"))

    # Формула компенсації: V(T) = V(25) - 0.024 * (T - 25)
    def v_abs_t(t_c):
        return 14.40 - 0.024 * (t_c - 25.0)

    def v_flt_t(t_c):
        return 13.60 - 0.024 * (t_c - 25.0)

    x_m20 = t_to_x(-20)
    x_p50 = t_to_x(50)

    y_abs_m20 = v_to_y(v_abs_t(-20))  # 14.40 - 0.024*(-45) = 15.48 В
    y_abs_p50 = v_to_y(v_abs_t(50))   # 14.40 - 0.024*(+25) = 13.80 В

    y_flt_m20 = v_to_y(v_flt_t(-20))  # 13.60 - 0.024*(-45) = 14.68 В
    y_flt_p50 = v_to_y(v_flt_t(50))   # 13.60 - 0.024*(+25) = 13.00 В

    # Зони небезпеки
    f.append(rect(t_to_x(30), top + 20, t_to_x(50) - t_to_x(30), 80,
                  fill="#fdecea", stroke=POS, sw=1.0, rx=4))
    f.append(mtext(t_to_x(40), top + 50, "Небезпека без компенсації:\nкипіння, сушіння VRLA,\nтепловий розгін",
                   size=10.5, color=POS, bold=True))

    f.append(rect(t_to_x(-20), v_to_y(13.6), t_to_x(5) - t_to_x(-20), 80,
                  fill="#eaf0fd", stroke=NEG, sw=1.0, rx=4))
    f.append(mtext(t_to_x(-7), v_to_y(13.6) + 30, "Без компенсації на морозі:\nнедозаряд, сульфатація,\nзамерзання розведеної H2SO4",
                   size=10.5, color=NEG, bold=True))

    # Лінії напруг
    f.append(line(x_m20, y_abs_m20, x_p50, y_abs_p50, color=POS, sw=2.8))
    f.append(line(x_m20, y_flt_m20, x_p50, y_flt_p50, color=FIELD, sw=2.8))

    # Точки 25°C
    x_25 = t_to_x(25)
    y_abs_25 = v_to_y(14.40)
    y_flt_25 = v_to_y(13.60)

    f.append(circle(x_25, y_abs_25, 4.5, fill=BG, stroke=POS, sw=2))
    f.append(circle(x_25, y_flt_25, 4.5, fill=BG, stroke=FIELD, sw=2))

    f.append(text(x_p50 - 6, y_abs_p50 - 12, "Absorption: 14.4 В @ 25°C", size=11, color=POS, anchor="end", bold=True))
    f.append(text(x_p50 - 6, y_flt_p50 - 12, "Float: 13.6 В @ 25°C", size=11, color=FIELD, anchor="end", bold=True))

    f.append(text(x_m20 + 8, y_abs_m20 - 10, "15.48 В (−20°C)", size=10.5, color=POS, anchor="start"))
    f.append(text(x_m20 + 8, y_flt_m20 - 10, "14.68 В (−20°C)", size=10.5, color=FIELD, anchor="start"))

    b, _, _ = textbox(W / 2, 420,
                      "−4 мВ/°C на кожну з 6 комірок = −24 мВ/°C на всю 12-вольтову батарею",
                      size=11, fill=FILL, stroke=MUTED)
    f.append(b)

    render(os.path.join(IMG, "temp-compensation.svg"), W, H, *f)


# ── 3. Криві заряду NiMH: −ΔV та похідна температури dT/dt ────────────────────
def fig_nimh_curves():
    W, H = 840, 460
    f = [text(W / 2, 26, "Динаміка заряду NiMH: напруга, температура й спад −ΔV",
              size=15, bold=True)]

    ox, oy = 80, 370
    span_x = 670
    top = 68

    f.append(line(ox, oy, ox + span_x, oy, color=MUTED, sw=1.4))
    f.append(line(ox, oy, ox, top, color=MUTED, sw=1.4))
    f.append(line(ox + span_x, oy, ox + span_x, top, color=MUTED, sw=1.4))
    f.append(text(ox + span_x / 2, oy + 42, "Час заряду сталим струмом 1C (t) →", size=12, color=INK, anchor="middle", bold=True))

    # Зони: Ендотермічна (0-80%), Перезаряд/Рекомбінація O2 (80-100%), Стоп/Trickle
    x_endo = ox + int(span_x * 0.65)
    x_peak = ox + int(span_x * 0.84)

    f.append(rect(ox, top, x_endo - ox, oy - top, fill="#f2f8f5", stroke="none", rx=0))
    f.append(rect(x_endo, top, x_peak - x_endo, oy - top, fill="#fdf3eb", stroke="none", rx=0))
    f.append(rect(x_peak, top, ox + span_x - x_peak, oy - top, fill="#f9f9f9", stroke="none", rx=0))

    f.append(line(x_endo, top, x_endo, oy, color=MUTED, sw=1.0, dash="3,3"))
    f.append(line(x_peak, top, x_peak, oy, color=MUTED, sw=1.2, dash="4,4"))

    f.append(text((ox + x_endo) / 2, top + 18, "Ендотермічна фаза (0–80%)", size=12, bold=True, color=FIELD))
    f.append(text((ox + x_endo) / 2, top + 32, "Поглинання тепла, стабільна напруга", size=10, color=MUTED))

    f.append(text((x_endo + x_peak) / 2, top + 18, "Рекомбінація O2", size=12, bold=True, color=POS))
    f.append(text((x_endo + x_peak) / 2, top + 32, "Екзотермічний розігрів", size=10, color=POS))

    f.append(text((x_peak + ox + span_x) / 2, top + 18, "Trickle (C/30)", size=12, bold=True, color=MUTED))
    f.append(text((x_peak + ox + span_x) / 2, top + 32, "Краплинний дозаряд", size=10, color=MUTED))

    # Шкали
    # Напруга: 1.0 В (oy) до 1.55 В (top + 40)
    def v_to_y(v):
        return oy - (v - 1.0) / 0.55 * (oy - (top + 40))

    # Температура: 20°C (oy) до 50°C (top + 40)
    def t_to_y(t):
        return oy - (t - 20.0) / 30.0 * (oy - (top + 40))

    # Підписи осей
    f.append(text(ox - 10, top + 15, "Напруга (В)", size=11.5, color=NEG, anchor="end", bold=True))
    f.append(text(ox + span_x + 10, top + 15, "Температура (°C)", size=11.5, color=POS, anchor="start", bold=True))

    for v_val in [1.1, 1.2, 1.3, 1.4, 1.5]:
        y = v_to_y(v_val)
        f.append(line(ox - 4, y, ox, y, color=MUTED, sw=1.0))
        f.append(text(ox - 8, y + 4, "%.2f" % v_val, size=10.5, color=MUTED, anchor="end"))

    for t_val in [25, 30, 35, 40, 45]:
        y = t_to_y(t_val)
        f.append(line(ox + span_x, y, ox + span_x + 4, y, color=MUTED, sw=1.0))
        f.append(text(ox + span_x + 8, y + 4, "%d°" % t_val, size=10.5, color=MUTED, anchor="start"))

    # Крива напруги й температури
    v_pts = []
    t_pts = []
    steps = 220
    for s in range(steps + 1):
        x = ox + s * span_x / steps
        if x <= x_endo:
            # Плато напруги ~1.38-1.42 В, температура 23-25°C
            t_rel = (x - ox) / (x_endo - ox)
            v = 1.20 + 0.18 * (t_rel ** 0.3) + 0.04 * t_rel
            t_deg = 24.0 + 1.0 * math.sin(t_rel * 3.14)
        elif x <= x_peak:
            # Напруга стрімко росте до піку 1.48 В, потім падає на 5 мВ (-dV)
            t_rel = (x - x_endo) / (x_peak - x_endo)
            if t_rel < 0.8:
                v = 1.42 + 0.07 * (t_rel / 0.8)
            else:
                v = 1.49 - 0.015 * ((t_rel - 0.8) / 0.2)
            t_deg = 25.0 + 18.0 * (t_rel ** 2.2)
        else:
            # Після стопу напруга падає до OCV ~1.36 В, температура спадає
            t_rel = (x - x_peak) / (ox + span_x - x_peak)
            v = 1.475 - 0.10 * (1.0 - math.exp(-3.0 * t_rel))
            t_deg = 43.0 - 15.0 * (1.0 - math.exp(-2.0 * t_rel))
        v_pts.append((x, v_to_y(v)))
        t_pts.append((x, t_to_y(t_deg)))

    # Малюємо криві
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
             % (" ".join("%.1f,%.1f" % p for p in v_pts), NEG))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
             % (" ".join("%.1f,%.1f" % p for p in t_pts), POS))

    # Спад -dV
    y_peak_v = v_to_y(1.49)
    x_peak_pt = x_endo + int((x_peak - x_endo) * 0.8)
    f.append(circle(x_peak_pt, y_peak_v, 4.5, fill=BG, stroke=NEG, sw=2))
    f.append(text(x_peak_pt, y_peak_v - 12, "Пік V_max", size=11, color=NEG, anchor="middle", bold=True))

    y_drop_v = v_to_y(1.475)
    f.append(circle(x_peak, y_drop_v, 4.5, fill=BG, stroke=POS, sw=2))
    f.append(text(x_peak + 8, y_drop_v + 16, "−ΔV (3–5 мВ)", size=11, color=POS, anchor="start", bold=True))

    # dT/dt стрілка
    y_t_spike = t_to_y(38)
    f.append(text(x_peak - 42, y_t_spike - 12, "dT/dt > 1°C/хв", size=11, color=POS, anchor="end", bold=True))
    f.append(arrow(x_peak - 38, y_t_spike, x_peak - 8, y_t_spike + 15, color=POS, sw=2))

    # Підписи кривих
    f.append(text(ox + 90, v_to_y(1.36) - 12, "Напруга U(t)", size=12, color=NEG, bold=True))
    f.append(text(ox + 90, t_to_y(26) + 18, "Температура T(t)", size=12, color=POS, bold=True))

    b, _, _ = textbox(W / 2, 432,
                      "Рекомбінація кисню гріє комірку → опір падає → напруга дає спад −ΔV і різкий стрибок dT/dt",
                      size=11, fill=FILL, stroke=MUTED)
    f.append(b)

    render(os.path.join(IMG, "nimh-curves.svg"), W, H, *f)


# ── 4. Кінцевий автомат універсального зарядника ──────────────────────────────
def fig_fsm():
    W, H = 860, 440
    f = [text(W / 2, 26, "Кінцевий автомат контролера заряду: Lead-Acid (IUoU) та NiMH",
              size=15, bold=True)]

    # Спільний стан STANDBY зліва
    bx_idle, w_idle, h_idle = textbox(90, 200, "STANDBY\n(Очікування /\nвизначення АКБ)",
                                      size=11.5, fill="#edf2f7", stroke=INK, sw=1.8)
    f.append(bx_idle)

    # Гілка Lead-Acid (зверху)
    f.append(text(380, 70, "Профіль Свинцю (Lead-Acid / AGM / GEL)", size=13, bold=True, color=POS))

    bx_bulk = fitbox(210, 95, 120, 52, "BULK (CC)\nI = 0.1–0.2C", size=11, fill="#fdecea", stroke=POS, bold=True)
    bx_abs  = fitbox(380, 95, 130, 52, "ABSORPTION (CV)\nU = 14.4 В (T-comp)", size=11, fill="#fdecea", stroke=POS, bold=True)
    bx_flt  = fitbox(560, 95, 120, 52, "FLOAT (CV)\nU = 13.6 В (T-comp)", size=11, fill="#eafaf1", stroke=FIELD, bold=True)

    f.append(bx_bulk)
    f.append(bx_abs)
    f.append(bx_flt)

    # Стрілки свинцю
    f.append(arrow(155, 175, 210, 125, color=POS, sw=1.6))
    f.append(text(175, 140, "Свинець", size=10.5, color=POS, bold=True))

    f.append(arrow(330, 121, 380, 121, color=POS, sw=1.6))
    f.append(text(355, 112, "U ≥ 14.4 В", size=9.5, color=POS, anchor="middle"))

    f.append(arrow(510, 121, 560, 121, color=POS, sw=1.6))
    f.append(text(535, 112, "I < C/50", size=9.5, color=POS, anchor="middle"))

    # Гілка NiMH (знизу)
    f.append(text(380, 245, "Профіль NiMH (Fast CC + dT/dt / −ΔV)", size=13, bold=True, color=NEG))

    bx_pre  = fitbox(210, 265, 120, 52, "PRECHARGE\nI = 0.1C (якщо <1V)", size=11, fill="#eaf0fd", stroke=NEG, bold=True)
    bx_fast = fitbox(380, 265, 130, 52, "FAST CHARGE (CC)\nI = 0.5–1.0C", size=11, fill="#eaf0fd", stroke=NEG, bold=True)
    bx_trig = fitbox(560, 265, 120, 52, "TRICKLE / TOP-OFF\nI = C/30", size=11, fill="#eafaf1", stroke=FIELD, bold=True)

    f.append(bx_pre)
    f.append(bx_fast)
    f.append(bx_trig)

    # Стрілки NiMH
    f.append(arrow(155, 225, 210, 285, color=NEG, sw=1.6))
    f.append(text(175, 268, "NiMH", size=10.5, color=NEG, bold=True))

    f.append(arrow(330, 291, 380, 291, color=NEG, sw=1.6))
    f.append(text(355, 282, "U > 1.0 В", size=9.5, color=NEG, anchor="middle"))

    f.append(arrow(510, 291, 560, 291, color=NEG, sw=1.6))
    f.append(mtext(535, 308, "−ΔV ≥ 3 мВ\ndT/dt ≥ 1°C", size=9.5, color=NEG, anchor="middle"))

    # Аварійний стан FAULT справа
    bx_flt_state = fitbox(720, 180, 115, 75, "FAULT\n(Аварія / СТОП)\nOVP / OTP / Time", size=11,
                          fill="#fbeee6", stroke=POS, bold=True, rx=8)
    f.append(bx_flt_state)

    # Стрілки в FAULT
    f.append(arrow(680, 121, 720, 195, color=POS, sw=1.4))
    f.append(arrow(680, 291, 720, 235, color=POS, sw=1.4))
    f.append(text(710, 145, "Таймаут/Перегрів", size=9, color=POS, anchor="end"))

    # Повернення до STANDBY
    f.append(line(777, 255, 777, 375, color=MUTED, sw=1.2, dash="3,3"))
    f.append(line(777, 375, 90, 375, color=MUTED, sw=1.2, dash="3,3"))
    f.append(arrow(90, 375, 90, 245, color=MUTED, sw=1.2))
    f.append(text(430, 365, "Акумулятор від'єднано або скидання помилки", size=10.5, color=MUTED, anchor="middle"))

    b, _, _ = textbox(W / 2, 415,
                      "Обидва профілі контролюють струм, напругу, NTC-температуру та максимальний час роботи",
                      size=11, fill=FILL, stroke=MUTED)
    f.append(b)

    render(os.path.join(IMG, "charger-fsm.svg"), W, H, *f)


if __name__ == "__main__":
    fig_iuou()
    fig_temp_comp()
    fig_nimh_curves()
    fig_fsm()
    print("Всі 4 фігури згенеровано успішно.")
