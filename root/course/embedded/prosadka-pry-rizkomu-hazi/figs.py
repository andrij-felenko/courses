# -*- coding: utf-8 -*-
"""Фігури для теми prosadka-pry-rizkomu-hazi (Просадка при різкому газі: brown-out контролера).
svgkit імпортуємо з scripts/, не копіюємо (AUTHORING §5).

    python figs.py    # вивід у ./img/
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. sag-mechanism: Схема бортової мережі та падіння напруги ────────────────
def fig_sag_mechanism():
    W, H = 880, 430
    p = []

    # Блок 1: Батарея LiPo 6S
    p.append(rect(15, 25, 175, 385, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(text(102, 48, "LiPo-батарея (6S)", size=12, bold=True, color=INK))

    # Джерело ЕРС
    p.append(circle(55, 115, 18, fill="#ffffff", stroke=POS, sw=1.8))
    p.append(text(55, 110, "E_ocv", size=10.5, bold=True, color=POS))
    p.append(text(55, 125, "25.2 В", size=9.5, color=MUTED))
    p.append(plus(55, 84, r=6))
    p.append(minus(55, 146, r=6))

    # Внутрішній опір R_int
    p.append(line(55, 84, 55, 68, color=LINE, sw=1.6))
    p.append(line(55, 68, 90, 68, color=LINE, sw=1.6))
    r_box, _, _ = textbox(130, 68, "R_int\n25 мОм", size=9.5, fill="#fff8e7", stroke="#d48800", sw=1.4)
    p.append(r_box)

    # Мінусова шина батареї
    p.append(line(55, 146, 55, 375, color=LINE, sw=1.6))
    p.append(line(55, 375, 190, 375, color=LINE, sw=1.6))

    # Вихід плюса батареї
    p.append(line(162, 68, 190, 68, color=LINE, sw=1.6))

    # Блок 2: Дроти та роз'єм XT60
    p.append(rect(195, 25, 140, 385, fill="#fdfefe", stroke="#cbd5e1", sw=1.0, rx=6))
    p.append(text(265, 48, "Дріт та XT60", size=11, bold=True, color=INK))

    l_box, _, _ = textbox(265, 68, "R_wire + L_wire\n6 мОм, 80 нГн", size=9.5, fill="#f1f5f9", stroke=MUTED, sw=1.2)
    p.append(l_box)
    p.append(line(190, 68, 210, 68, color=LINE, sw=1.6))
    p.append(line(320, 68, 340, 68, color=LINE, sw=1.6))
    p.append(line(190, 375, 340, 375, color=LINE, sw=1.6))

    # Стрілка струму
    p.append(arrow(225, 110, 305, 110, color=POS, sw=2.0))
    p.append(text(265, 128, "I_peak до 180 А", size=10, bold=True, color=POS))
    p.append(text(265, 150, "ΔV_wire = I·R + L·di/dt", size=9, color=MUTED))

    # Блок 3: Силова шина V_bat, конденсатор, TVS, 4 ESC
    p.append(rect(345, 25, 230, 385, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(text(460, 48, "Силова шина V_bat та ESC", size=12, bold=True, color=INK))

    # Плюсова шина
    p.append(line(340, 68, 580, 68, color=POS, sw=2.2))
    p.append(text(365, 58, "V_bat", size=10, bold=True, color=POS))

    # Конденсатор C_bulk
    p.append(line(385, 68, 385, 175, color=LINE, sw=1.5))
    c_box, _, _ = textbox(385, 215, "C_bulk\n1000 мкФ\nLow-ESR\n12 мОм", size=9.5, fill="#e0f2fe", stroke="#0284c7", sw=1.3)
    p.append(c_box)
    p.append(line(385, 255, 385, 375, color=LINE, sw=1.5))

    # TVS-діод
    p.append(line(450, 68, 450, 185, color=LINE, sw=1.5))
    tvs_box, _, _ = textbox(450, 215, "TVS-діод\nSMBJ28A\n(захист\nвід піків)", size=9.5, fill="#fef2f2", stroke=POS, sw=1.3)
    p.append(tvs_box)
    p.append(line(450, 245, 450, 375, color=LINE, sw=1.5))

    # 4 ESC мотори
    p.append(line(515, 68, 515, 180, color=LINE, sw=1.5))
    esc_box, _, _ = textbox(515, 215, "4x ESC\n4 BLDC\nмотори\n(до 180 А)", size=9.5, fill="#f0fdf4", stroke=FIELD, sw=1.3)
    p.append(esc_box)
    p.append(line(515, 250, 515, 375, color=LINE, sw=1.5))

    # Мінусова шина силової частини
    p.append(line(340, 375, 580, 375, color=LINE, sw=2.2))
    p.append(text(365, 390, "GND (силова)", size=9, color=MUTED))

    # Блок 4: Польотний контролер (FC) і периферія
    p.append(rect(585, 25, 280, 385, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(text(725, 48, "Польотний контролер (FC)", size=12, bold=True, color=INK))

    # Лінія до BEC
    p.append(line(580, 68, 630, 68, color=POS, sw=1.8))
    p.append(line(630, 68, 630, 90, color=POS, sw=1.8))

    # Блок BEC 5V (Buck)
    bec_box, _, _ = textbox(725, 115, "Імпульсний BEC (Buck)\nВхід: V_bat (до 25.2 В) → Вихід: 5.0 В\nМін. вхід: 6.5 В (Dropout ~1.5 В)", size=9.5, fill="#faf5ff", stroke="#9333ea", sw=1.3)
    p.append(bec_box)

    # Вихід 5V
    p.append(line(725, 140, 725, 170, color=POS, sw=1.8))
    p.append(text(745, 158, "Шина 5.0 В", size=9.5, bold=True, color=POS))

    # Відгалуження на VTX / RX
    p.append(line(725, 170, 645, 170, color=POS, sw=1.5))
    p.append(line(645, 170, 645, 195, color=POS, sw=1.5))
    vtx_box, _, _ = textbox(645, 220, "Приймач RX\nта VTX 5V\n(чутливі\nдо провалу)", size=9, fill="#fff7ed", stroke="#ea580c", sw=1.2)
    p.append(vtx_box)

    # До LDO 3.3V
    p.append(line(725, 170, 800, 170, color=POS, sw=1.5))
    p.append(line(800, 170, 800, 195, color=POS, sw=1.5))
    ldo_box, _, _ = textbox(800, 220, "LDO 3.3V\n(Drop ~0.3 В)\nВихід: 3.3 В", size=9, fill="#ecfdf5", stroke="#059669", sw=1.2)
    p.append(ldo_box)

    # До MCU STM32
    p.append(line(800, 245, 800, 280, color=POS, sw=1.5))
    p.append(line(800, 280, 725, 280, color=POS, sw=1.5))
    p.append(line(725, 280, 725, 295, color=POS, sw=1.5))
    mcu_box, _, _ = textbox(725, 330, "STM32 MCU (F4/F7/H7)\nЖивлення ядра 3.3 В\nBrown-out Reset (BOR)\nПоріг скидання: 2.7–2.9 В", size=9.5, fill="#fef2f2", stroke=POS, sw=1.4)
    p.append(mcu_box)

    # Загальний нуль логіки
    p.append(line(645, 245, 645, 375, color=LINE, sw=1.5))
    p.append(line(725, 365, 725, 375, color=LINE, sw=1.5))
    p.append(line(580, 375, 855, 375, color=LINE, sw=1.8))
    p.append(text(725, 390, "GND (логіка FC)", size=9, color=MUTED))

    render(os.path.join(OUT, "sag-mechanism.svg"), W, H, *p)


# ── 2. voltage-current-transient: Осцилограми перехідного процесу ───────────────
def fig_voltage_current_transient():
    W, H = 860, 500
    p = []

    # Заголовок
    p.append(rect(15, 15, 830, 470, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(text(430, 35, "Осцилограма перехідного процесу при різкому газі (Throttle Punch)", size=12, bold=True, color=INK))

    # Спільна сітка часу: x0 = 130, x_max = 800, t = 0..100 ms
    x0 = 130
    x_step = 230  # t = 10 ms (газ вгору)
    x_peak = 290  # t = 20 ms (пік струму)
    x_settle = 480  # t = 50 ms (стабілізація)
    x_end = 800

    # 1. Графік газу Throttle (0..100%)
    p.append(line(x0, 60, x0, 115, color=LINE, sw=1.2))
    p.append(line(x0, 115, x_end, 115, color=LINE, sw=1.2))
    p.append(text(70, 75, "Газ (Throttle)", size=10, bold=True, color=INK))
    p.append(text(115, 70, "100%", size=9, color=MUTED, anchor="end"))
    p.append(text(115, 115, "0%", size=9, color=MUTED, anchor="end"))
    # Форма сигналу
    p.append(line(x0, 115, x_step, 115, color="#2563eb", sw=2.0))
    p.append(line(x_step, 115, x_step + 10, 70, color="#2563eb", sw=2.0))
    p.append(line(x_step + 10, 70, x_end, 70, color="#2563eb", sw=2.0))

    # 2. Графік струму I_total (0..180 A)
    p.append(line(x0, 145, x0, 220, color=LINE, sw=1.2))
    p.append(line(x0, 220, x_end, 220, color=LINE, sw=1.2))
    p.append(text(70, 160, "Струм I_bat", size=10, bold=True, color=POS))
    p.append(text(115, 150, "180 A", size=9, color=POS, anchor="end"))
    p.append(text(115, 185, "70 A", size=9, color=MUTED, anchor="end"))
    p.append(text(115, 220, "10 A", size=9, color=MUTED, anchor="end"))
    # Форма струму
    i_pts = [
        (x0, 215), (x_step, 215), (x_step + 15, 175), (x_peak, 150),
        (x_peak + 40, 165), (x_settle, 185), (x_end, 185)
    ]
    for i in range(len(i_pts) - 1):
        p.append(line(i_pts[i][0], i_pts[i][1], i_pts[i+1][0], i_pts[i+1][1], color=POS, sw=2.2))
    p.append(text(x_peak + 5, 138, "Піковий струм розгону", size=9.5, color=POS))

    # 3. Графік напруги V_bat (25.2V -> 16.5V)
    p.append(line(x0, 250, x0, 345, color=LINE, sw=1.2))
    p.append(line(x0, 345, x_end, 345, color=LINE, sw=1.2))
    p.append(text(70, 265, "Напруга V_bat", size=10, bold=True, color="#d97706"))
    p.append(text(115, 255, "25.2 В", size=9, color=MUTED, anchor="end"))
    p.append(text(115, 295, "20.0 В", size=9, color=MUTED, anchor="end"))
    p.append(text(115, 340, "15.5 В", size=9, color=POS, anchor="end"))
    # Крива напруги батареї
    v_pts = [
        (x0, 255), (x_step, 255), (x_step + 15, 295), (x_peak, 340),
        (x_peak + 20, 330), (x_peak + 40, 320), (x_settle, 295), (x_end, 295)
    ]
    for i in range(len(v_pts) - 1):
        p.append(line(v_pts[i][0], v_pts[i][1], v_pts[i+1][0], v_pts[i+1][1], color="#d97706", sw=2.2))
    p.append(text(x_peak + 15, 355, "Просадка: ΔV = I·R_int + L·(di/dt)", size=9.5, color="#d97706"))

    # 4. Графік шини 3.3V MCU і поріг BOR
    p.append(line(x0, 380, x0, 455, color=LINE, sw=1.2))
    p.append(line(x0, 455, x_end, 455, color=LINE, sw=1.2))
    p.append(text(70, 395, "Логіка 3.3 В", size=10, bold=True, color=FIELD))
    p.append(text(115, 390, "3.3 В", size=9, color=FIELD, anchor="end"))
    p.append(text(115, 420, "2.7 В", size=9, color=POS, anchor="end"))
    p.append(text(115, 455, "0.0 В", size=9, color=MUTED, anchor="end"))

    # Пунктирний поріг BOR
    p.append(line(x0, 420, x_end, 420, color=POS, sw=1.2, dash="4,4"))
    p.append(text(730, 412, "Поріг Brown-out Reset (BOR)", size=9, color=POS))

    # Траєкторія шини 3.3V з провалом і ресетом
    p.append(line(x0, 390, x_step, 390, color=FIELD, sw=2.0))
    p.append(line(x_step, 390, x_peak - 10, 395, color=FIELD, sw=2.0))
    p.append(line(x_peak - 10, 395, x_peak + 15, 430, color=POS, sw=2.2))  # провал нижче BOR
    p.append(line(x_peak + 15, 430, x_peak + 30, 455, color=POS, sw=2.0))  # падіння до 0
    p.append(line(x_peak + 30, 455, x_peak + 90, 455, color=POS, sw=2.0))  # MCU в ресеті
    p.append(line(x_peak + 90, 455, x_peak + 110, 390, color=FIELD, sw=2.0)) # перезапуск
    p.append(line(x_peak + 110, 390, x_end, 390, color=FIELD, sw=2.0))

    # Позначка аварії
    p.append(circle(x_peak + 15, 430, 4, fill=POS, stroke=POS))
    p.append(text(x_peak + 70, 442, "Brownout: Ресет MCU і аварія", size=9.5, bold=True, color=POS))

    # Вісь часу знизу
    p.append(text(x_step, 475, "t = 10 мс", size=9, color=MUTED))
    p.append(text(x_peak, 475, "t = 20 мс", size=9, color=MUTED))
    p.append(text(x_settle, 475, "t = 50 мс", size=9, color=MUTED))
    p.append(text(x_end - 20, 475, "t = 100 мс", size=9, color=MUTED))

    # Вертикальні лінії зв'язку між графіками
    p.append(line(x_step, 60, x_step, 455, color="#94a3b8", sw=0.8, dash="2,2"))
    p.append(line(x_peak, 60, x_peak, 455, color="#f87171", sw=0.8, dash="2,2"))

    render(os.path.join(OUT, "voltage-current-transient.svg"), W, H, *p)


# ── 3. capacitor-esr-ripple: Пульсації та роль Low-ESR конденсатора ───────────
def fig_capacitor_esr_ripple():
    W, H = 840, 380
    p = []

    # Заголовок
    p.append(rect(15, 15, 810, 350, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(text(420, 36, "Вплив силового Low-ESR конденсатора на пульсації та індуктивні викиди", size=12, bold=True, color=INK))

    # Ліва панель: БЕЗ конденсатора
    p.append(rect(30, 55, 375, 290, fill="#fff1f2", stroke="#fca5a5", sw=1.2, rx=6))
    p.append(text(217, 75, "БЕЗ Low-ESR конденсатора", size=11, bold=True, color=POS))

    # Графік напруги з викидами
    p.append(line(50, 175, 385, 175, color=LINE, sw=1.0))
    p.append(text(60, 95, "Напруга шини V_bat", size=9.5, bold=True, color=POS))
    p.append(text(50, 115, "35 В (пік)", size=9, color=POS))
    p.append(text(50, 170, "22 В (ном)", size=9, color=MUTED))
    p.append(text(50, 235, "12 В (провал)", size=9, color=POS))

    # Нестабільна синусоїда з різкими спайками
    spikes = [
        (65, 175), (80, 115), (95, 235), (110, 130), (125, 220), (140, 110),
        (155, 240), (170, 120), (185, 230), (200, 105), (215, 245), (230, 125),
        (245, 225), (260, 115), (275, 235), (290, 130), (305, 220), (320, 175),
        (370, 175)
    ]
    for i in range(len(spikes) - 1):
        p.append(line(spikes[i][0], spikes[i][1], spikes[i+1][0], spikes[i+1][1], color=POS, sw=1.8))

    # Опис проблем зліва
    t_left1, _, _ = textbox(217, 275, "Шум ШІМ (24–48 кГц) та викиди L·di/dt > 35 В\nПерегрів MOSFET, провал BEC, перезапуск MCU", size=9.5, fill="#ffffff", stroke=POS, sw=1.0)
    p.append(t_left1)

    # Права панель: З Low-ESR конденсатором 1000 мкФ
    p.append(rect(435, 55, 375, 290, fill="#f0fdf4", stroke="#86efac", sw=1.2, rx=6))
    p.append(text(622, 75, "З конденсатором 1000 мкФ Low-ESR + TVS", size=11, bold=True, color=FIELD))

    # Графік згладженої напруги
    p.append(line(455, 175, 790, 175, color=LINE, sw=1.0))
    p.append(text(465, 95, "Напруга шини V_bat", size=9.5, bold=True, color=FIELD))
    p.append(text(455, 150, "25.2 В", size=9, color=MUTED))
    p.append(text(455, 170, "22.2 В", size=9, color=MUTED))
    p.append(text(455, 205, "19.5 В", size=9, color=FIELD))

    # Згладжена лінія з незначною пульсацією (<0.5 В)
    smooth = [
        (470, 160), (510, 160), (530, 195), (560, 195),
        (620, 190), (670, 185), (730, 175), (780, 175)
    ]
    for i in range(len(smooth) - 1):
        p.append(line(smooth[i][0], smooth[i][1], smooth[i+1][0], smooth[i+1][1], color=FIELD, sw=2.2))

    # Пульсації ШІМ (дрібні)
    for px in range(470, 780, 15):
        p.append(line(px, 173, px + 7, 177, color="#15803d", sw=1.2))
        p.append(line(px + 7, 177, px + 15, 173, color="#15803d", sw=1.2))

    # Опис переваг справа
    t_right1, _, _ = textbox(622, 275, "Пульсації згладжено до <0.4 В, викиди зрізано TVS\nСтабільна робота BEC 5V, надійний радіозв'язок", size=9.5, fill="#ffffff", stroke=FIELD, sw=1.0)
    p.append(t_right1)

    render(os.path.join(OUT, "capacitor-esr-ripple.svg"), W, H, *p)


# ── 4. slew-rate-control: Програмне обмеження швидкості газу ──────────────────
def fig_slew_rate_control():
    W, H = 840, 380
    p = []

    # Заголовок
    p.append(rect(15, 15, 810, 350, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(text(420, 36, "Програмне обмеження швидкості газу (Throttle Slew Rate Limit)", size=12, bold=True, color=INK))

    # Лівий блок: Миттєвий крок (Step)
    p.append(rect(30, 55, 375, 290, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(217, 75, "Без обмеження (Миттєвий стрибок)", size=11, bold=True, color=POS))

    # Графік газу і струму
    p.append(line(55, 160, 380, 160, color=LINE, sw=1.0))
    p.append(line(55, 160, 55, 95, color=LINE, sw=1.0))
    p.append(text(65, 92, "Газ 0 → 100%", size=9, color="#2563eb"))
    p.append(line(55, 160, 95, 160, color="#2563eb", sw=2.0))
    p.append(line(95, 160, 100, 105, color="#2563eb", sw=2.0))
    p.append(line(100, 105, 380, 105, color="#2563eb", sw=2.0))

    # Струм (пік)
    p.append(line(55, 160, 95, 160, color=POS, sw=1.8))
    p.append(line(95, 160, 115, 75, color=POS, sw=2.2))
    p.append(line(115, 75, 145, 130, color=POS, sw=2.0))
    p.append(line(145, 130, 380, 130, color=POS, sw=1.8))
    p.append(text(125, 70, "I_peak = 180 A (di/dt = 36 A/мс)", size=9, bold=True, color=POS))

    # Напруга V_bat (провал нижче норми)
    p.append(line(55, 200, 380, 200, color=LINE, sw=1.0))
    p.append(line(55, 200, 95, 200, color="#d97706", sw=1.8))
    p.append(line(95, 200, 115, 260, color=POS, sw=2.2))
    p.append(line(115, 260, 150, 220, color="#d97706", sw=1.8))
    p.append(line(150, 220, 380, 220, color="#d97706", sw=1.8))

    # Лінія BOR
    p.append(line(55, 250, 380, 250, color=POS, sw=1.0, dash="3,3"))
    p.append(text(285, 244, "Поріг відмови (16.0 В)", size=9, color=POS))

    t_box_l, _, _ = textbox(217, 305, "Катастрофічна просадка напруги ΔV = 5.4 В\nВисокий ризик Brownout і втрати апарата", size=9.5, fill="#fff1f2", stroke=POS, sw=1.0)
    p.append(t_box_l)

    # Правий блок: З обмеженням Slew-Rate
    p.append(rect(435, 55, 375, 290, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(622, 75, "З обмеженням Slew Rate (25–40 мс рамп)", size=11, bold=True, color=FIELD))

    # Графік газу з плавним наростанням
    p.append(line(460, 160, 785, 160, color=LINE, sw=1.0))
    p.append(line(460, 160, 460, 95, color=LINE, sw=1.0))
    p.append(text(470, 92, "Газ (плавний рамп)", size=9, color="#2563eb"))
    p.append(line(460, 160, 500, 160, color="#2563eb", sw=2.0))
    p.append(line(500, 160, 560, 105, color="#2563eb", sw=2.0))
    p.append(line(560, 105, 785, 105, color="#2563eb", sw=2.0))

    # Струм (керований, без пікового перевантаження)
    p.append(line(460, 160, 500, 160, color=FIELD, sw=1.8))
    p.append(line(500, 160, 560, 120, color=FIELD, sw=2.2))
    p.append(line(560, 120, 785, 125, color=FIELD, sw=1.8))
    p.append(text(535, 110, "I_max = 95 A (di/dt ≤ 5 A/мс)", size=9, bold=True, color=FIELD))

    # Напруга V_bat (безпечний плавний спад)
    p.append(line(460, 200, 785, 200, color=LINE, sw=1.0))
    p.append(line(460, 200, 500, 200, color=FIELD, sw=1.8))
    p.append(line(500, 200, 560, 222, color=FIELD, sw=2.2))
    p.append(line(560, 222, 785, 220, color=FIELD, sw=1.8))

    # Лінія BOR
    p.append(line(460, 250, 785, 250, color=POS, sw=1.0, dash="3,3"))
    p.append(text(690, 244, "Поріг відмови (16.0 В)", size=9, color=POS))

    t_box_r, _, _ = textbox(622, 305, "Плавний спад без глибокого провалу (V_min > 20 В)\nТяга наростає без затримки, нульовий ризик Brownout", size=9.5, fill="#f0fdf4", stroke=FIELD, sw=1.0)
    p.append(t_box_r)

    render(os.path.join(OUT, "slew-rate-control.svg"), W, H, *p)


def main():
    fig_sag_mechanism()
    fig_voltage_current_transient()
    fig_capacitor_esr_ripple()
    fig_slew_rate_control()
    print("All figures successfully generated in img/")


if __name__ == "__main__":
    main()
