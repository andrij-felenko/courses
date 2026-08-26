# -*- coding: utf-8 -*-
"""Фігури до статті «Динамічна потужність КМОН» (hw/hw-digital/dynamichna-potuzhnist-kmon).

Фігури:
  1. inverter-currents.svg       — складові динамічного струму КМОН-інвертора: ємнісний та наскрізний
  2. energy-split.svg            — енергетичний баланс повного циклу перезаряду: 50% у поле, 50% у тепло
  3. transient-waveforms.svg     — часові діаграми напруг, ємнісного та наскрізного струмів під час перемикання
  4. dynamic-power-reduction.svg — фактори формули P_dyn = alpha * C_L * V_DD^2 * f та методи їх оптимізації

Запуск: python figs.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Кольори для схем і графіків
VDD_COL = "#c0392b"    # живлення / червоний
GND_COL = "#2457d6"    # земля / синій
CAP_COL = "#27ae60"    # ємнісний струм / зелений
SC_COL  = "#e67e22"    # наскрізний струм / помаранчевий
WARN_COL = "#d35400"
MUTED_BG = "#f8f9fa"


# ── 1. inverter-currents.svg ──────────────────────────────────────────────────
def fig_inverter_currents():
    W, H = 760, 440
    body = []
    
    # Заголовок
    body.append(text(W / 2, 28, "Складові динамічного струму під час перемикання інвертора", size=16, bold=True))

    # Ліва частина: Схема інвертора
    # Рейки живлення
    body.append(line(80, 70, 360, 70, color=VDD_COL, sw=2.5))
    body.append(text(70, 65, "V_DD", size=14, color=VDD_COL, bold=True, anchor="end"))
    
    body.append(line(80, 380, 360, 380, color=GND_COL, sw=2.5))
    body.append(text(70, 385, "GND (0 В)", size=13, color=GND_COL, bold=True, anchor="end"))

    # Вхідна лінія
    body.append(line(90, 225, 170, 225, color=LINE, sw=2.0))
    body.append(line(170, 140, 170, 310, color=LINE, sw=2.0))
    body.append(circle(170, 225, 3.5, fill=LINE, stroke=LINE))
    body.append(text(80, 220, "V_in", size=14, color=INK, bold=True, anchor="end"))
    body.append(text(125, 245, "0 → V_DD", size=11, color=MUTED, anchor="middle"))

    # PMOS (верхній)
    body.append(line(170, 140, 195, 140, color=LINE, sw=1.8))
    body.append(circle(200, 140, 4.5, fill="#ffffff", stroke=LINE, sw=1.8)) # інверсний кружечок на затворі
    body.append(line(205, 120, 205, 160, color=LINE, sw=2.2)) # затвор пластина
    body.append(line(212, 115, 212, 165, color=LINE, sw=2.2)) # канал
    body.append(line(212, 125, 235, 125, color=LINE, sw=1.8)) # витік
    body.append(line(235, 70, 235, 125, color=LINE, sw=1.8))
    body.append(line(212, 155, 235, 155, color=LINE, sw=1.8)) # стік
    body.append(line(235, 155, 235, 225, color=LINE, sw=1.8))
    body.append(text(255, 135, "PMOS", size=13, color=VDD_COL, bold=True, anchor="start"))

    # NMOS (нижній)
    body.append(line(170, 310, 205, 310, color=LINE, sw=1.8)) # прямий затвор
    body.append(line(205, 290, 205, 330, color=LINE, sw=2.2)) # затвор пластина
    body.append(line(212, 285, 212, 335, color=LINE, sw=2.2)) # канал
    body.append(line(212, 295, 235, 295, color=LINE, sw=1.8)) # стік
    body.append(line(235, 225, 235, 295, color=LINE, sw=1.8))
    body.append(line(212, 325, 235, 325, color=LINE, sw=1.8)) # витік
    body.append(line(235, 325, 235, 380, color=LINE, sw=1.8))
    body.append(text(255, 315, "NMOS", size=13, color=GND_COL, bold=True, anchor="start"))

    # Вузол виходу
    body.append(circle(235, 225, 4, fill=LINE, stroke=LINE))
    body.append(line(235, 225, 330, 225, color=LINE, sw=2.0))
    body.append(circle(330, 225, 3.5, fill=LINE, stroke=LINE))
    body.append(text(340, 220, "V_out", size=14, color=INK, bold=True, anchor="start"))

    # Навантажувальна ємність C_L
    body.append(line(310, 225, 310, 280, color=LINE, sw=1.8))
    body.append(circle(310, 225, 3.5, fill=LINE, stroke=LINE))
    body.append(line(295, 280, 325, 280, color=LINE, sw=2.5)) # пластина 1
    body.append(line(295, 288, 325, 288, color=LINE, sw=2.5)) # пластина 2
    body.append(line(310, 288, 310, 380, color=LINE, sw=1.8))
    body.append(circle(310, 380, 3.5, fill=LINE, stroke=LINE))
    body.append(text(335, 288, "C_L", size=14, color=CAP_COL, bold=True, anchor="start"))

    # Стрілка наскрізного струму (i_sc)
    body.append(arrow(225, 90, 225, 360, color=SC_COL, sw=3.0))
    body.append(text(215, 225, "i_sc", size=14, color=SC_COL, bold=True, anchor="end"))

    # Стрілка ємнісного струму (i_cap)
    body.append(arrow(245, 90, 300, 255, color=CAP_COL, sw=2.5))
    body.append(text(285, 175, "i_cap", size=13, color=CAP_COL, bold=True, anchor="start"))

    # Права частина: Пояснювальні картки
    # Картка 1: Ємнісний струм перезаряду
    b1, _, _ = textbox(560, 135,
                       "1. Ємнісний струм перезаряду (i_cap)\n"
                       "• Заряджає/розряджає паразитну ємність C_L\n"
                       "• Виникає лише під час зміни стану 0→1 або 1→0\n"
                       "• Потужність: P_cap = α · C_L · V_DD² · f",
                       size=12, pad=12, fill="#eef9f1", stroke=CAP_COL, sw=1.6, min_w=340)
    body.append(b1)

    # Картка 2: Наскрізний струм (crowbar / short-circuit)
    b2, _, _ = textbox(560, 275,
                       "2. Наскрізний струм к.з. (i_sc, crowbar)\n"
                       "• Тече прямо від V_DD до GND крізь обидва транзистори\n"
                       "• Виникає в зоні V_th,n < V_in < V_DD − |V_th,p|\n"
                       "• Залежить від тривалості фронту перемикання t_rf\n"
                       "• Потужність: P_sc = I_mean · V_DD",
                       size=12, pad=12, fill="#fef6ee", stroke=SC_COL, sw=1.6, min_w=340)
    body.append(b2)

    # Підсумковий рядок уніфікації
    b3, _, _ = textbox(560, 390,
                       "Повна динамічна потужність: P_dyn = P_cap + P_sc",
                       size=13, pad=10, fill="#f4f6f8", stroke=LINE, sw=1.5, bold=True, min_w=340)
    body.append(b3)

    render(os.path.join(IMG, "inverter-currents.svg"), W, H, *body)


# ── 2. energy-split.svg ───────────────────────────────────────────────────────
def fig_energy_split():
    W, H = 760, 420
    body = []

    body.append(text(W / 2, 28, "Енергетичний баланс перемикання КМОН: правило 50% / 50%", size=16, bold=True))

    # Фаза 1: Перехід 0 → 1 (Заряд ємності)
    body.append(rect(40, 60, 320, 270, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    body.append(text(200, 88, "ФАЗА ЗАРЯДУ (перехід 0 → 1)", size=14, color=VDD_COL, bold=True))
    
    # Від джерела живлення
    b_sup, _, _ = textbox(200, 130, "Джерело живлення постачає:\nE_VDD = Q · V_DD = C_L · V_DD²",
                          size=12, pad=8, fill="#fdedec", stroke=VDD_COL, sw=1.4, min_w=280)
    body.append(b_sup)

    body.append(arrow(200, 160, 140, 195, color=LINE, sw=1.8))
    body.append(arrow(200, 160, 260, 195, color=LINE, sw=1.8))

    # Розподіл 50/50
    b_field, _, _ = textbox(130, 245, "50% накопичено в C_L\n(в електричному полі):\nE_cap = ½ C_L · V_DD²",
                            size=11, pad=8, fill="#eef9f1", stroke=CAP_COL, sw=1.4, min_w=140)
    body.append(b_field)

    b_heat_p, _, _ = textbox(270, 245, "50% розсіяно в тепло\n(на опорі PMOS R_on,p):\nE_PMOS = ½ C_L · V_DD²",
                             size=11, pad=8, fill="#fdf2e9", stroke=WARN_COL, sw=1.4, min_w=140)
    body.append(b_heat_p)

    body.append(text(200, 315, "Втрата на PMOS не залежить від R_on!", size=11, color=MUTED, bold=True))

    # Фаза 2: Перехід 1 → 0 (Розряд ємності)
    body.append(rect(400, 60, 320, 270, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    body.append(text(560, 88, "ФАЗА РОЗРЯДУ (перехід 1 → 0)", size=14, color=GND_COL, bold=True))

    # Джерело відключене
    b_dis_sup, _, _ = textbox(560, 130, "Джерело живлення не бере участі:\nE_VDD = 0 (PMOS закритий)",
                              size=12, pad=8, fill="#f4f6f8", stroke=MUTED, sw=1.4, min_w=280)
    body.append(b_dis_sup)

    body.append(arrow(560, 160, 560, 200, color=LINE, sw=1.8))

    # Скидання всієї накопиченої енергії
    b_heat_n, _, _ = textbox(560, 245, "100% енергії конденсатора\nскидається крізь NMOS у GND:\nE_NMOS = ½ C_L · V_DD² (усе в тепло)",
                             size=11, pad=8, fill="#fdf2e9", stroke=WARN_COL, sw=1.4, min_w=280)
    body.append(b_heat_n)

    body.append(text(560, 315, "Конденсатор повністю спустошується до 0 В", size=11, color=MUTED, bold=True))

    # Підсумкова плашка знизу
    b_sum, _, _ = textbox(W / 2, 375,
                          "ПОВНИЙ ЦИКЛ (0 → 1 → 0): Сумарно розсіяно в тепло E_total = C_L · V_DD².\n"
                          "Середня потужність при частоті f та активності α:   P_cap = α · C_L · V_DD² · f",
                          size=13, pad=12, fill="#eaf2f8", stroke=NEG, sw=1.8, bold=True, min_w=680)
    body.append(b_sum)

    render(os.path.join(IMG, "energy-split.svg"), W, H, *body)


# ── 3. transient-waveforms.svg ────────────────────────────────────────────────
def fig_transient_waveforms():
    W, H = 760, 480
    body = []

    body.append(text(W / 2, 26, "Часові діаграми напруг і струмів під час перемикання 0 → 1", size=16, bold=True))

    t0 = 120
    t_end = 680
    
    # 3 осі Y:
    # Графік 1: Напруги V_in та V_out
    y1_base = 130
    body.append(line(t0, y1_base, t_end, y1_base, color=LINE, sw=1.2))
    body.append(line(t0, y1_base - 70, t0, y1_base + 10, color=LINE, sw=1.2))
    body.append(text(t0 - 15, y1_base - 35, "Напруги [В]", size=12, color=INK, anchor="end", bold=True))
    body.append(text(t0 - 5, y1_base - 60, "V_DD", size=11, color=VDD_COL, anchor="end"))
    body.append(text(t0 - 5, y1_base, "0 В", size=11, color=MUTED, anchor="end"))
    
    # V_in (трапеція: 0 -> V_DD)
    t_r_start = 220
    t_r_end = 360
    v_in_path = f"M {t0} {y1_base} L {t_r_start} {y1_base} L {t_r_end} {y1_base - 60} L {t_end} {y1_base - 60}"
    body.append(f'<path d="{v_in_path}" fill="none" stroke="{LINE}" stroke-width="2.2"/>')
    body.append(text(460, y1_base - 68, "V_in (вхід)", size=12, color=LINE, bold=True))

    # V_out (спад від V_DD до 0)
    v_out_path = f"M {t0} {y1_base - 60} L {t_r_start + 30} {y1_base - 60} C 320 {y1_base - 50}, 360 {y1_base - 10}, 440 {y1_base} L {t_end} {y1_base}"
    body.append(f'<path d="{v_out_path}" fill="none" stroke="{GND_COL}" stroke-width="2.2" stroke-dasharray="5,3"/>')
    body.append(text(460, y1_base - 15, "V_out (вихід)", size=12, color=GND_COL, bold=True))

    # Позначення зони одночасної провідності (V_th,n < V_in < V_DD - |V_th,p|)
    t_th_n = 260
    t_th_p = 330
    body.append(f'<rect x="{t_th_n}" y="55" width="{t_th_p - t_th_n}" height="360" fill="#fef9e7" stroke="#f39c12" stroke-width="1.0" stroke-dasharray="3,3"/>')
    body.append(text((t_th_n + t_th_p) / 2, 48, "Обидва транзистори відкриті", size=11, color="#b7950b", bold=True))

    # Графік 2: Струми (i_cap та i_sc)
    y2_base = 270
    body.append(line(t0, y2_base, t_end, y2_base, color=LINE, sw=1.2))
    body.append(line(t0, y2_base - 70, t0, y2_base + 10, color=LINE, sw=1.2))
    body.append(text(t0 - 15, y2_base - 35, "Струми [мА]", size=12, color=INK, anchor="end", bold=True))

    # i_sc (наскрізний купол)
    sc_path = f"M {t0} {y2_base} L {t_th_n} {y2_base} Q {(t_th_n + t_th_p) / 2} {y2_base - 55} {t_th_p} {y2_base} L {t_end} {y2_base}"
    body.append(f'<path d="{sc_path}" fill="#fdebd0" stroke="{SC_COL}" stroke-width="2.2"/>')
    body.append(text((t_th_n + t_th_p) / 2 + 50, y2_base - 42, "i_sc (наскрізний струм)", size=12, color=SC_COL, bold=True))

    # i_cap (струм розряду ємності через NMOS)
    cap_path = f"M {t0} {y2_base} L {t_th_n} {y2_base} Q 310 {y2_base - 45} 360 {y2_base - 30} Q 410 {y2_base - 10} 460 {y2_base} L {t_end} {y2_base}"
    body.append(f'<path d="{cap_path}" fill="none" stroke="{CAP_COL}" stroke-width="2.0" stroke-dasharray="4,2"/>')
    body.append(text(390, y2_base - 22, "i_cap (розряд C_L)", size=12, color=CAP_COL, bold=True))

    # Графік 3: Миттєва потужність p(t)
    y3_base = 410
    body.append(line(t0, y3_base, t_end, y3_base, color=LINE, sw=1.2))
    body.append(line(t0, y3_base - 70, t0, y3_base + 10, color=LINE, sw=1.2))
    body.append(text(t0 - 15, y3_base - 35, "Потужність p(t)", size=12, color=INK, anchor="end", bold=True))

    p_path = f"M {t0} {y3_base} L {t_th_n} {y3_base} Q 305 {y3_base - 60} 350 {y3_base - 40} Q 400 {y3_base - 12} 460 {y3_base} L {t_end} {y3_base}"
    body.append(f'<path d="{p_path}" fill="#fadbd8" stroke="{VDD_COL}" stroke-width="2.2"/>')
    body.append(text(410, y3_base - 45, "p(t) = i_total(t) · V_DD", size=12, color=VDD_COL, bold=True))

    # Вісь часу
    body.append(arrow(t0, y3_base + 15, t_end + 30, y3_base + 15, color=LINE, sw=1.5))
    body.append(text(t_end + 35, y3_base + 18, "Час t", size=12, color=INK, bold=True, anchor="start"))
    body.append(text(t_r_start, y3_base + 32, "t_start", size=11, color=MUTED, anchor="middle"))
    body.append(text(t_r_end, y3_base + 32, "t_end", size=11, color=MUTED, anchor="middle"))

    # Пояснення знизу
    body.append(text(W / 2, 465, "Сплеск потужності існує виключно під час зміни напруги на вході (в спокої p(t) ≈ 0)", size=12, color=MUTED, bold=True, italic=True))

    render(os.path.join(IMG, "transient-waveforms.svg"), W, H, *body)


# ── 4. dynamic-power-reduction.svg ───────────────────────────────────────────
def fig_dynamic_power_reduction():
    W, H = 760, 430
    body = []

    body.append(text(W / 2, 28, "Важелі впливу на динамічну потужність КМОН", size=16, bold=True))

    # Центральна формула
    b_formula, _, _ = textbox(W / 2, 85, "P_динамічна = α · C_L · V_DD² · f",
                              size=18, pad=14, fill="#eaf2f8", stroke=NEG, sw=2.2, bold=True, min_w=460)
    body.append(b_formula)

    # 4 стовпчики оптимізацій
    cols_x = [110, 290, 470, 650]
    box_w = 165

    # 1: alpha (Activity Factor)
    b_a, _, _ = textbox(cols_x[0], 250,
                        "α — активність\n\n"
                        "• Тактове стробування\n  (Clock Gating)\n"
                        "• Кодування шин\n  (Bus Invert)\n"
                        "• Усунення глітчів\n  (Glitch Filtering)\n"
                        "• Спеціалізовані FSM\n  (Gray-кодування)",
                        size=11, pad=10, fill="#fdfefe", stroke=CAP_COL, sw=1.5, min_w=box_w)
    body.append(b_a)
    body.append(arrow(240, 115, cols_x[0], 165, color=CAP_COL, sw=1.8))
    body.append(text(cols_x[0], 155, "Зменшення переходів", size=11, color=CAP_COL, bold=True))

    # 2: C_L (Ємність)
    b_c, _, _ = textbox(cols_x[1], 250,
                        "C_L — ємність\n\n"
                        "• Мінімізація транзисторів\n  (Gate Sizing)\n"
                        "• Короткі траси на кристалі\n  (Floorplanning)\n"
                        "• Low-k діелектрики\n  між шарами металу\n"
                        "• Зменшення fan-out",
                        size=11, pad=10, fill="#fdfefe", stroke=LINE, sw=1.5, min_w=box_w)
    body.append(b_c)
    body.append(arrow(330, 115, cols_x[1], 165, color=LINE, sw=1.8))
    body.append(text(cols_x[1], 155, "Фізична геометрія", size=11, color=LINE, bold=True))

    # 3: V_DD^2 (Напруга живлення)
    b_v, _, _ = textbox(cols_x[2], 250,
                        "V_DD² — напруга\n\n"
                        "• Квадратичний ефект!\n  (найпотужніший важіль)\n"
                        "• DVFS (динамічне масштабування)\n"
                        "• Кілька доменів живлення\n  (Multi-VDD)\n"
                        "• Зниження до субпорогових\n  рівнів (Near-Threshold)",
                        size=11, pad=10, fill="#fef5e7", stroke=VDD_COL, sw=1.8, min_w=box_w)
    body.append(b_v)
    body.append(arrow(430, 115, cols_x[2], 165, color=VDD_COL, sw=2.2))
    body.append(text(cols_x[2], 155, "Квадратичний вплив", size=11, color=VDD_COL, bold=True))

    # 4: f (Частота)
    b_f, _, _ = textbox(cols_x[3], 250,
                        "f — частота\n\n"
                        "• Динамічне регулювання\n  тактової частоти (DFS)\n"
                        "• Асинхронні домени\n  (GALS-архітектури)\n"
                        "• Паралелізм замість\n  надвисоких частот\n  (багатоядерність)",
                        size=11, pad=10, fill="#fdfefe", stroke=NEG, sw=1.5, min_w=box_w)
    body.append(b_f)
    body.append(arrow(520, 115, cols_x[3], 165, color=NEG, sw=1.8))
    body.append(text(cols_x[3], 155, "Частотна шкала", size=11, color=NEG, bold=True))

    # Нижній висновок
    b_bot, _, _ = textbox(W / 2, 385,
                          "Найефективніший підхід: одночасне зменшення V_DD та f (DVFS) у періоди низького навантаження,\n"
                          "плюс агресивне тактове стробування (Clock Gating) для усунення перемикань неактивних блоків.",
                          size=12, pad=10, fill="#f4f6f8", stroke=LINE, sw=1.4, min_w=710)
    body.append(b_bot)

    render(os.path.join(IMG, "dynamic-power-reduction.svg"), W, H, *body)


if __name__ == "__main__":
    fig_inverter_currents()
    fig_energy_split()
    fig_transient_waveforms()
    fig_dynamic_power_reduction()
    print("All figures generated successfully.")
