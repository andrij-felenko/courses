# -*- coding: utf-8 -*-
"""Генератор векторних SVG-фігур до теми «VID: код напруги від процесора до регулятора»."""
import sys, os, math

# Імпортуємо спільний модуль svgkit із кореневої папки scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)


# ── 1. Замкнений контур керування напругою (CPU <-> VRM Loop) ─────────────────
def fig_vid_closed_loop():
    W, H = 860, 480
    frags = []
    frags.append(text(W / 2, 24, "Замкнений контур керування та телеметрії: процесор і регулятор напруги", size=15, bold=True))

    # Лівий блок: Процесор (CPU / SoC / PCU)
    x_cpu, y_cpu, w_cpu, h_cpu = 40, 60, 240, 380
    frags.append(rect(x_cpu, y_cpu, w_cpu, h_cpu, fill="#eff6ff", stroke=NEG, sw=2, rx=8))
    frags.append(text(x_cpu + w_cpu / 2, y_cpu + 28, "Процесор (CPU / SoC)", size=14, color=NEG, bold=True))
    frags.append(line(x_cpu + 15, y_cpu + 38, x_cpu + w_cpu - 15, y_cpu + 38, color="#bfdbfe", sw=1.5))

    # Внутрішні модулі CPU
    frags.append(rect(x_cpu + 15, y_cpu + 55, w_cpu - 30, 80, fill="#ffffff", stroke="#93c5fd", sw=1.2, rx=5))
    frags.append(text(x_cpu + w_cpu / 2, y_cpu + 78, "Блок керування живленням", size=12, color=INK, bold=True))
    frags.append(text(x_cpu + w_cpu / 2, y_cpu + 98, "(PCU / DVFS Governor)", size=11, color=MUTED))
    frags.append(text(x_cpu + w_cpu / 2, y_cpu + 118, "Розрахунок V-f точки за мікросекунди", size=10, color=FIELD))

    frags.append(rect(x_cpu + 15, y_cpu + 150, w_cpu - 30, 75, fill="#ffffff", stroke="#93c5fd", sw=1.2, rx=5))
    frags.append(text(x_cpu + w_cpu / 2, y_cpu + 172, "Обчислювальні ядра", size=12, color=INK, bold=True))
    frags.append(text(x_cpu + w_cpu / 2, y_cpu + 192, "Vcore: 0.5 – 1.4 В", size=11, color=POS, bold=True))
    frags.append(text(x_cpu + w_cpu / 2, y_cpu + 210, "Струм до 200–400 А (навантаження)", size=10, color=MUTED))

    frags.append(rect(x_cpu + 15, y_cpu + 240, w_cpu - 30, 85, fill="#ffffff", stroke="#93c5fd", sw=1.2, rx=5))
    frags.append(text(x_cpu + w_cpu / 2, y_cpu + 262, "Контролер шини VID", size=12, color=INK, bold=True))
    frags.append(text(x_cpu + w_cpu / 2, y_cpu + 282, "SVID Master / SVI3", size=11, color=NEG, bold=True))
    frags.append(text(x_cpu + w_cpu / 2, y_cpu + 302, "Обробка ALERT#, TMON, IMON", size=10, color=MUTED))

    # Дросельний сенсинг на кристалі
    frags.append(rect(x_cpu + 15, y_cpu + 340, w_cpu - 30, 30, fill="#ffffff", stroke="#93c5fd", sw=1.2, rx=4))
    frags.append(text(x_cpu + w_cpu / 2, y_cpu + 360, "Кельвінівські виводи (VCC_SENSE / VSS_SENSE)", size=9, color=LINE))

    # Правий блок: Регулятор напруги (VRM / VR Controller)
    x_vrm, y_vrm, w_vrm, h_vrm = 580, 60, 240, 380
    frags.append(rect(x_vrm, y_vrm, w_vrm, h_vrm, fill="#f0fdf4", stroke=FIELD, sw=2, rx=8))
    frags.append(text(x_vrm + w_vrm / 2, y_vrm + 28, "ШІМ-контролер VRM", size=14, color=FIELD, bold=True))
    frags.append(line(x_vrm + 15, y_vrm + 38, x_vrm + w_vrm - 15, y_vrm + 38, color="#bbf7d0", sw=1.5))

    # Внутрішні модулі VRM
    frags.append(rect(x_vrm + 15, y_vrm + 55, w_vrm - 30, 75, fill="#ffffff", stroke="#86efac", sw=1.2, rx=5))
    frags.append(text(x_vrm + w_vrm / 2, y_vrm + 76, "SVID Slave / Логіка протоколу", size=12, color=INK, bold=True))
    frags.append(text(x_vrm + w_vrm / 2, y_vrm + 94, "Регістри VID, Slew Rate, Offsets", size=10, color=MUTED))
    frags.append(text(x_vrm + w_vrm / 2, y_vrm + 112, "Швидкісний ЦАП (DAC) 5–10 мВ крок", size=10, color=FIELD, bold=True))

    frags.append(rect(x_vrm + 15, y_vrm + 145, w_vrm - 30, 85, fill="#ffffff", stroke="#86efac", sw=1.2, rx=5))
    frags.append(text(x_vrm + w_vrm / 2, y_vrm + 166, "Контур регулювання (PWM Engine)", size=12, color=INK, bold=True))
    frags.append(text(x_vrm + w_vrm / 2, y_vrm + 186, "Підсилювач помилки + AVP (Droop)", size=10, color=MUTED))
    frags.append(text(x_vrm + w_vrm / 2, y_vrm + 204, "Генератор фаз (Multi-phase Buck)", size=10, color=LINE))

    frags.append(rect(x_vrm + 15, y_vrm + 245, w_vrm - 30, 80, fill="#ffffff", stroke="#86efac", sw=1.2, rx=5))
    frags.append(text(x_vrm + w_vrm / 2, y_vrm + 266, "Телеметрія та захист", size=12, color=INK, bold=True))
    frags.append(text(x_vrm + w_vrm / 2, y_vrm + 286, "АЦП струму (IMON) та темп. (TMON)", size=10, color=MUTED))
    frags.append(text(x_vrm + w_vrm / 2, y_vrm + 304, "Компаратори OVP, UVP, OCP, VR_HOT", size=10, color=POS))

    frags.append(rect(x_vrm + 15, y_vrm + 340, w_vrm - 30, 30, fill="#ffffff", stroke="#86efac", sw=1.2, rx=4))
    frags.append(text(x_vrm + w_vrm / 2, y_vrm + 360, "Силові каскади (DrMOS / Power Stages)", size=10, color=LINE, bold=True))

    # Центральні лінії зв'язку
    # 1. Силова шина живлення (Power Rail)
    y_pwr = 180
    frags.append(line(x_vrm, y_pwr, x_cpu + w_cpu, y_pwr, color=POS, sw=3))
    frags.append(arrow(x_cpu + w_cpu + 30, y_pwr, x_cpu + w_cpu, y_pwr, color=POS, sw=3))
    frags.append(rect(340, y_pwr - 22, 180, 26, fill="#fef2f2", stroke="#fca5a5", sw=1, rx=4))
    frags.append(text(430, y_pwr - 5, "Vcore (Силове живлення)", size=11, color=POS, bold=True))

    # 2. Шина цифрового керування VID (Serial VID / SVID)
    y_svid = 280
    frags.append(line(x_cpu + w_cpu, y_svid - 10, x_vrm, y_svid - 10, color=NEG, sw=2))
    frags.append(arrow(x_vrm - 30, y_svid - 10, x_vrm, y_svid - 10, color=NEG, sw=2))
    frags.append(line(x_vrm, y_svid + 10, x_cpu + w_cpu, y_svid + 10, color=NEG, sw=2))
    frags.append(arrow(x_cpu + w_cpu + 30, y_svid + 10, x_cpu + w_cpu, y_svid + 10, color=NEG, sw=2))

    frags.append(rect(320, y_svid - 36, 220, 24, fill="#eff6ff", stroke="#93c5fd", sw=1, rx=4))
    frags.append(text(430, y_svid - 20, "SCLK (25 МГц) + SDATA (SetVID)", size=11, color=NEG, bold=True))

    frags.append(rect(320, y_svid + 16, 220, 24, fill="#eff6ff", stroke="#93c5fd", sw=1, rx=4))
    frags.append(text(430, y_svid + 32, "ALERT# + Телеметрія (IMON/TMON)", size=11, color=NEG, bold=True))

    # 3. Кельвінівський зворотний зв'язок (Remote Sensing)
    y_sense = 390
    frags.append(line(x_cpu + w_cpu, y_sense, x_vrm, y_sense, color=LINE, sw=1.5, dash="4,3"))
    frags.append(arrow(x_vrm - 30, y_sense, x_vrm, y_sense, color=LINE, sw=1.5))
    frags.append(rect(330, y_sense - 12, 200, 24, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(430, y_sense + 4, "Диференційний V_SENSE (AVP)", size=10, color=LINE))

    render(os.path.join(IMG, "vid-closed-loop.svg"), W, H, *frags)


# ── 2. Порівняння: Паралельний VID проти Послідовного VID (SVID) ───────────────
def fig_parallel_vs_serial():
    W, H = 840, 430
    frags = []
    frags.append(text(W / 2, 24, "Архітектурна еволюція: паралельна шина VID проти послідовної SVID", size=15, bold=True))

    # Ліва колонка: Паралельний VID (VRM 8.x - 11.x)
    x1, y1, w1, h1 = 30, 55, 370, 350
    frags.append(rect(x1, y1, w1, h1, fill="#fefce8", stroke="#eab308", sw=1.5, rx=8))
    frags.append(text(x1 + w1 / 2, y1 + 25, "Паралельний VID (VRM 8.x – 11.1)", size=13, color="#854d0e", bold=True))
    frags.append(line(x1 + 15, y1 + 35, x1 + w1 - 15, y1 + 35, color="#fef08a", sw=1.2))

    # CPU блок
    frags.append(rect(x1 + 20, y1 + 55, 90, 160, fill="#ffffff", stroke="#ca8a04", sw=1, rx=5))
    frags.append(text(x1 + 65, y1 + 80, "CPU", size=13, color=INK, bold=True))
    frags.append(text(x1 + 65, y1 + 105, "GPIO Pins", size=10, color=MUTED))
    frags.append(text(x1 + 65, y1 + 125, "VID[0..7]", size=11, color="#ca8a04", bold=True))
    frags.append(text(x1 + 65, y1 + 160, "Односпрям.", size=9, color=MUTED))
    frags.append(text(x1 + 65, y1 + 175, "Без зворот.", size=9, color=MUTED))
    frags.append(text(x1 + 65, y1 + 190, "зв'язку", size=9, color=MUTED))

    # VRM блок
    frags.append(rect(x1 + 260, y1 + 55, 90, 160, fill="#ffffff", stroke="#ca8a04", sw=1, rx=5))
    frags.append(text(x1 + 305, y1 + 80, "VRM DAC", size=13, color=INK, bold=True))
    frags.append(text(x1 + 305, y1 + 105, "Резистивна", size=10, color=MUTED))
    frags.append(text(x1 + 305, y1 + 120, "матриця", size=10, color=MUTED))
    frags.append(text(x1 + 305, y1 + 145, "8-біт ЦАП", size=11, color="#ca8a04", bold=True))
    frags.append(text(x1 + 305, y1 + 175, "Статична", size=9, color=MUTED))
    frags.append(text(x1 + 305, y1 + 190, "напруга", size=9, color=MUTED))

    # 8 паралельних ліній
    y_lines_start = y1 + 75
    for i in range(8):
        yl = y_lines_start + i * 16
        frags.append(line(x1 + 110, yl, x1 + 260, yl, color="#ca8a04", sw=1.2))
        frags.append(arrow(x1 + 235, yl, x1 + 260, yl, color="#ca8a04", sw=1.2))

    frags.append(rect(x1 + 140, y1 + 110, 90, 36, fill="#fef9c3", stroke="#eab308", sw=1, rx=4))
    frags.append(text(x1 + 185, y1 + 126, "8 сигнальних", size=10, color="#854d0e", bold=True))
    frags.append(text(x1 + 185, y1 + 138, "доріжок на шину", size=9, color="#854d0e"))

    # Підсумкові властивості
    frags.append(rect(x1 + 15, y1 + 230, w1 - 30, 105, fill="#ffffff", stroke="#eab308", sw=1, rx=5))
    frags.append(text(x1 + 25, y1 + 250, "• 8 виводів сокета на ОДНЕ силове коло", size=11, color=INK, anchor="start"))
    frags.append(text(x1 + 25, y1 + 270, "• Немає телеметрії струму (IMON) і темп. (TMON)", size=11, color=POS, anchor="start"))
    frags.append(text(x1 + 25, y1 + 290, "• Ризик збою при асинхронному перемиканні бітів", size=11, color=POS, anchor="start"))
    frags.append(text(x1 + 25, y1 + 310, "• Неможливо масштабувати на 4–6 незалежних шин", size=11, color=POS, anchor="start"))

    # Права колонка: Послідовний VID (SVID / SVI2 / SVI3 / AVSBus)
    x2, y2, w2, h2 = 440, 55, 370, 350
    frags.append(rect(x2, y2, w2, h2, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(x2 + w2 / 2, y2 + 25, "Послідовний SVID / SVI3 / AVSBus", size=13, color="#166534", bold=True))
    frags.append(line(x2 + 15, y2 + 35, x2 + w2 - 15, y2 + 35, color="#bbf7d0", sw=1.2))

    # CPU блок
    frags.append(rect(x2 + 20, y2 + 55, 90, 160, fill="#ffffff", stroke=FIELD, sw=1, rx=5))
    frags.append(text(x2 + 65, y2 + 80, "CPU", size=13, color=INK, bold=True))
    frags.append(text(x2 + 65, y2 + 105, "SVID Master", size=11, color=FIELD, bold=True))
    frags.append(text(x2 + 65, y2 + 125, "25 МГц", size=10, color=MUTED))
    frags.append(text(x2 + 65, y2 + 150, "Керує всіма", size=9, color=MUTED))
    frags.append(text(x2 + 65, y2 + 165, "силовими", size=9, color=MUTED))
    frags.append(text(x2 + 65, y2 + 180, "доменами", size=9, color=MUTED))

    # VRM блок
    frags.append(rect(x2 + 260, y2 + 55, 90, 160, fill="#ffffff", stroke=FIELD, sw=1, rx=5))
    frags.append(text(x2 + 305, y2 + 80, "VRM Hub", size=13, color=INK, bold=True))
    frags.append(text(x2 + 305, y2 + 105, "SVID Slaves", size=11, color=FIELD, bold=True))
    frags.append(text(x2 + 305, y2 + 125, "Vcore, Vgt...", size=10, color=MUTED))
    frags.append(text(x2 + 305, y2 + 150, "Цифровий", size=9, color=MUTED))
    frags.append(text(x2 + 305, y2 + 165, "DSP / ЦАП", size=9, color=MUTED))
    frags.append(text(x2 + 305, y2 + 180, "+ АЦП моніт.", size=9, color=MUTED))

    # 3 лінії SVID
    y_s = y2 + 85
    # SCLK
    frags.append(line(x2 + 110, y_s, x2 + 260, y_s, color=NEG, sw=1.8))
    frags.append(arrow(x2 + 235, y_s, x2 + 260, y_s, color=NEG, sw=1.8))
    frags.append(text(x2 + 185, y_s - 7, "SCLK (25 МГц)", size=10, color=NEG, bold=True))

    # SDATA (двоспрямована)
    y_sd = y_s + 40
    frags.append(line(x2 + 110, y_sd, x2 + 260, y_sd, color=FIELD, sw=1.8))
    frags.append(arrow(x2 + 235, y_sd, x2 + 260, y_sd, color=FIELD, sw=1.8))
    frags.append(arrow(x2 + 135, y_sd, x2 + 110, y_sd, color=FIELD, sw=1.8))
    frags.append(text(x2 + 185, y_sd - 7, "SDATA (команди/дані)", size=10, color=FIELD, bold=True))

    # ALERT#
    y_al = y_sd + 40
    frags.append(line(x2 + 260, y_al, x2 + 110, y_al, color=POS, sw=1.8))
    frags.append(arrow(x2 + 135, y_al, x2 + 110, y_al, color=POS, sw=1.8))
    frags.append(text(x2 + 185, y_al - 7, "ALERT# (переривання)", size=10, color=POS, bold=True))

    # Підсумкові властивості
    frags.append(rect(x2 + 15, y2 + 230, w2 - 30, 105, fill="#ffffff", stroke=FIELD, sw=1, rx=5))
    frags.append(text(x2 + 25, y2 + 250, "• Лише 3 виводи на ВСІ силові домени (адресація)", size=11, color=FIELD, bold=True, anchor="start"))
    frags.append(text(x2 + 25, y2 + 270, "• Повна телеметрія: струм (IMON), темп. (TMON), стан", size=11, color=INK, anchor="start"))
    frags.append(text(x2 + 25, y2 + 290, "• Програмне керування швидкістю наростання (Slew Rate)", size=11, color=INK, anchor="start"))
    frags.append(text(x2 + 25, y2 + 310, "• Контроль парності, захист від помилок передачі", size=11, color=INK, anchor="start"))

    render(os.path.join(IMG, "parallel-vs-serial.svg"), W, H, *frags)


# ── 3. Динаміка перехідного процесу при зміні VID (Slew Rate & DVFS) ──────────
def fig_dynamic_vid_transition():
    W, H = 840, 460
    frags = []
    frags.append(text(W / 2, 24, "Динамічний перехід напруги (DVFS) та вплив швидкості наростання (Slew Rate)", size=15, bold=True))

    # Осі координат
    x0, y0 = 80, 240
    x_max = 760

    # Сітка та рівні напруги
    y_v_high = 70    # 1.25 В (P0 стан)
    y_v_low = 190    # 0.75 В (P3 стан)

    frags.append(line(x0, y_v_high, x_max, y_v_high, color="#cbd5e1", sw=1, dash="4,4"))
    frags.append(line(x0, y_v_low, x_max, y_v_low, color="#cbd5e1", sw=1, dash="4,4"))

    frags.append(text(x0 - 10, y_v_high + 4, "1.25 В (P0)", size=11, color=POS, anchor="end", bold=True))
    frags.append(text(x0 - 10, y_v_low + 4, "0.75 В (P3)", size=11, color=NEG, anchor="end", bold=True))

    # Горизонтальні осі
    frags.append(line(x0, y_v_low + 30, x_max + 20, y_v_low + 30, color=LINE, sw=1.5))
    frags.append(arrow(x_max, y_v_low + 30, x_max + 20, y_v_low + 30, color=LINE, sw=1.5))
    frags.append(text(x_max + 25, y_v_low + 34, "t", size=12, color=INK, italic=True))

    # 1. Крива швидкого наростання: Fast Slew Rate (20–40 мВ/мкс)
    # З 0.75 В до 1.25 В за 20 мкс
    x_step_start = 140
    x_fast_end = 220
    pts_fast = [
        (x0, y_v_low),
        (x_step_start, y_v_low),
        (x_fast_end, y_v_high - 8),     # легкий викид
        (x_fast_end + 30, y_v_high + 3), # коливання
        (x_fast_end + 70, y_v_high),
        (460, y_v_high)
    ]
    p_fast_str = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_fast)
    frags.append(f'<path d="{p_fast_str}" fill="none" stroke="{POS}" stroke-width="2.5"/>')
    frags.append(text(x_fast_end + 10, y_v_high - 16, "SetVID_Fast (напр. 30 мВ/мкс)", size=11, color=POS, bold=True, anchor="start"))

    # 2. Крива повільного наростання: Slow Slew Rate (2.5–5 мВ/мкс)
    x_slow_end = 380
    pts_slow = [
        (x0, y_v_low),
        (x_step_start, y_v_low),
        (x_slow_end, y_v_high),
        (460, y_v_high)
    ]
    p_slow_str = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_slow)
    frags.append(f'<path d="{p_slow_str}" fill="none" stroke="{FIELD}" stroke-width="2.2" stroke-dasharray="6,3"/>')
    frags.append(text(x_slow_end - 40, y_v_high + 26, "SetVID_Slow (напр. 5 мВ/мкс)", size=11, color=FIELD, bold=True, anchor="end"))

    # Спад: Керування спадом (Decay vs Active Step-down)
    x_down_start = 460
    x_active_down = 540
    x_decay_down = 680

    # Активний спад (Fast Step-down)
    pts_act_down = [
        (x_down_start, y_v_high),
        (x_active_down, y_v_low + 5),
        (x_active_down + 30, y_v_low),
        (x_max, y_v_low)
    ]
    p_act_down = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_act_down)
    frags.append(f'<path d="{p_act_down}" fill="none" stroke="{POS}" stroke-width="2.5"/>')
    frags.append(text(x_active_down + 20, y_v_low - 35, "Активне форсоване зниження", size=10, color=POS, bold=True, anchor="start"))

    # Пасивний спад (Decay Mode - розряд тільки навантаженням)
    pts_decay = [
        (x_down_start, y_v_high),
        (x_down_start + 60, y_v_high + (y_v_low - y_v_high) * 0.5),
        (x_decay_down, y_v_low),
        (x_max, y_v_low)
    ]
    p_decay = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_decay)
    frags.append(f'<path d="{p_decay}" fill="none" stroke="{NEG}" stroke-width="2" stroke-dasharray="5,4"/>')
    frags.append(text(x_decay_down - 20, y_v_low - 15, "SetVID_Decay (пасивне згасання)", size=10, color=NEG, bold=True, anchor="end"))

    # Нижній графік: Додатковий ємнісний струм заряджання батареї конденсаторів I_cap = C * (dV/dt)
    y_i_base = 360
    frags.append(line(x0, y_i_base, x_max + 20, y_i_base, color=LINE, sw=1.5))
    frags.append(arrow(x_max, y_i_base, x_max + 20, y_i_base, color=LINE, sw=1.5))
    frags.append(text(x_max + 25, y_i_base + 4, "t", size=12, color=INK, italic=True))
    frags.append(text(x0 - 10, y_i_base + 4, "I_cap = 0", size=11, color=MUTED, anchor="end"))

    frags.append(text(x0, y_i_base - 85, "Ємнісний струм перехідного процесу: I_cap = C_out · (dV/dt)", size=12, color=INK, bold=True, anchor="start"))

    # Імпульс струму Fast
    pts_i_fast = [
        (x0, y_i_base),
        (x_step_start, y_i_base),
        (x_step_start + 5, y_i_base - 65),
        (x_fast_end - 5, y_i_base - 65),
        (x_fast_end, y_i_base),
        (x_down_start, y_i_base),
        (x_down_start + 5, y_i_base + 55),
        (x_active_down - 5, y_i_base + 55),
        (x_active_down, y_i_base),
        (x_max, y_i_base)
    ]
    p_i_fast = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_i_fast)
    frags.append(f'<path d="{p_i_fast}" fill="none" stroke="{POS}" stroke-width="2"/>')
    frags.append(text(x_step_start + 45, y_i_base - 70, "+30 А (додатковий струм заряду C_out)", size=10, color=POS, bold=True, anchor="middle"))
    frags.append(text(x_down_start + 40, y_i_base + 68, "-25 А (скидання енергії в індуктивності)", size=10, color=POS, bold=True, anchor="middle"))

    # Імпульс струму Slow
    pts_i_slow = [
        (x0, y_i_base),
        (x_step_start, y_i_base),
        (x_step_start + 5, y_i_base - 18),
        (x_slow_end - 5, y_i_base - 18),
        (x_slow_end, y_i_base),
        (x_max, y_i_base)
    ]
    p_i_slow = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_i_slow)
    frags.append(f'<path d="{p_i_slow}" fill="none" stroke="{FIELD}" stroke-width="1.8" stroke-dasharray="4,3"/>')
    frags.append(text(x_slow_end - 50, y_i_base - 24, "+5 А (помірний струм)", size=10, color=FIELD, bold=True, anchor="middle"))

    render(os.path.join(IMG, "dynamic-vid-transition.svg"), W, H, *frags)


# ── 4. Кадр протоколу та часова діаграма SVID ──────────────────────────────────
def fig_svid_frame_protocol():
    W, H = 840, 420
    frags = []
    frags.append(text(W / 2, 24, "Структура кадру протоколу Intel SVID (25 МГц послідовний пакет)", size=15, bold=True))

    # Верхня діаграма: поля пакету (Packet Anatomy)
    y_pkt = 65
    frags.append(text(40, y_pkt - 10, "1. Анатомія транзакції SVID (Master Command + Slave Acknowledge / Payload)", size=12, color=INK, bold=True, anchor="start"))

    # Блоки пакета
    fields = [
        ("START", 45, "#e2e8f0", "#475569", "Start bit\n(1 біт = 0)"),
        ("ADDR", 95, "#dbeafe", NEG, "Slave Addr\n(4 біти: 0..F)"),
        ("CMD", 150, "#fef3c7", "#b45309", "Command Code\n(5 бітів: SetVID/GetReg)"),
        ("DATA / PAYLOAD", 210, "#dcfce7", "#15803d", "Master Data Payload\n(8 бітів: VID код або Reg Offset)"),
        ("PARITY", 65, "#fee2e2", POS, "Parity (P)\n(Odd parity)"),
        ("TURN", 50, "#f1f5f9", MUTED, "Turn-around\n(TA, 1-2 такти)"),
        ("ACK / STATUS", 145, "#f3e8ff", "#7e22ce", "Slave Status / Data\n(ACK + Telemetry byte)")
    ]

    cur_x = 40
    for name, w_f, bg_c, stroke_c, desc in fields:
        frags.append(rect(cur_x, y_pkt + 8, w_f, 40, fill=bg_c, stroke=stroke_c, sw=1.5, rx=4))
        frags.append(text(cur_x + w_f / 2, y_pkt + 32, name, size=11, color=stroke_c, bold=True))
        # Опис під блоком
        lines_d = desc.split("\n")
        frags.append(text(cur_x + w_f / 2, y_pkt + 62, lines_d[0], size=9, color=INK))
        if len(lines_d) > 1:
            frags.append(text(cur_x + w_f / 2, y_pkt + 74, lines_d[1], size=9, color=MUTED))
        cur_x += w_f + 4

    # Нижня діаграма: Осцилограма сигналів SCLK, SDATA, ALERT#
    y_osc = 200
    frags.append(text(40, y_osc - 5, "2. Осцилограма сигнальних ліній шини SVID", size=12, color=INK, bold=True, anchor="start"))

    x_sig_start = 120
    x_sig_end = 790

    # Лінії назв
    frags.append(text(40, y_osc + 30, "SCLK (25 МГц)", size=11, color=NEG, bold=True, anchor="start"))
    frags.append(text(40, y_osc + 90, "SDATA", size=11, color=FIELD, bold=True, anchor="start"))
    frags.append(text(40, y_osc + 155, "ALERT#", size=11, color=POS, bold=True, anchor="start"))

    # SCLK меандр
    clk_step = 22
    num_clks = int((x_sig_end - x_sig_start) / clk_step)
    clk_pts = [(x_sig_start, y_osc + 35)]
    for i in range(num_clks):
        xc = x_sig_start + i * clk_step
        clk_pts.append((xc, y_osc + 15))
        clk_pts.append((xc + clk_step / 2, y_osc + 15))
        clk_pts.append((xc + clk_step / 2, y_osc + 35))
        clk_pts.append((xc + clk_step, y_osc + 35))

    p_clk = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in clk_pts)
    frags.append(f'<path d="{p_clk}" fill="none" stroke="{NEG}" stroke-width="1.8"/>')

    # SDATA рівні (символічні пакети бітів)
    y_sd_hi = y_osc + 75
    y_sd_lo = y_osc + 95
    sdata_pts = [
        (x_sig_start, y_sd_hi),
        (x_sig_start + clk_step * 1, y_sd_hi),
        (x_sig_start + clk_step * 1, y_sd_lo),   # Start bit = 0
        (x_sig_start + clk_step * 2, y_sd_lo),
        (x_sig_start + clk_step * 2, y_sd_hi),   # Addr bit 1
        (x_sig_start + clk_step * 3, y_sd_hi),
        (x_sig_start + clk_step * 3, y_sd_lo),   # Addr bit 0
        (x_sig_start + clk_step * 6, y_sd_lo),
        (x_sig_start + clk_step * 6, y_sd_hi),   # Cmd bits
        (x_sig_start + clk_step * 11, y_sd_hi),
        (x_sig_start + clk_step * 11, y_sd_lo),  # Data bits
        (x_sig_start + clk_step * 19, y_sd_lo),
        (x_sig_start + clk_step * 19, y_sd_hi),  # Parity bit
        (x_sig_start + clk_step * 20, y_sd_hi),
        (x_sig_start + clk_step * 21, y_sd_hi),  # TA
        (x_sig_start + clk_step * 22, y_sd_lo),  # Slave ACK
        (x_sig_start + clk_step * 27, y_sd_lo),
        (x_sig_end, y_sd_hi)
    ]
    p_sdata = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in sdata_pts)
    frags.append(f'<path d="{p_sdata}" fill="none" stroke="{FIELD}" stroke-width="2.2"/>')

    # Вертикальні розділювачі секцій на осцилограмі
    frags.append(line(x_sig_start + clk_step * 1, y_osc + 5, x_sig_start + clk_step * 1, y_osc + 115, color="#cbd5e1", sw=1, dash="3,3"))
    frags.append(line(x_sig_start + clk_step * 6, y_osc + 5, x_sig_start + clk_step * 6, y_osc + 115, color="#cbd5e1", sw=1, dash="3,3"))
    frags.append(line(x_sig_start + clk_step * 11, y_osc + 5, x_sig_start + clk_step * 11, y_osc + 115, color="#cbd5e1", sw=1, dash="3,3"))
    frags.append(line(x_sig_start + clk_step * 19, y_osc + 5, x_sig_start + clk_step * 19, y_osc + 115, color="#cbd5e1", sw=1, dash="3,3"))
    frags.append(line(x_sig_start + clk_step * 21, y_osc + 5, x_sig_start + clk_step * 21, y_osc + 115, color="#cbd5e1", sw=1, dash="3,3"))

    frags.append(text(x_sig_start + clk_step * 1.5, y_osc + 112, "Start", size=9, color=MUTED))
    frags.append(text(x_sig_start + clk_step * 3.5, y_osc + 112, "Addr", size=9, color=MUTED))
    frags.append(text(x_sig_start + clk_step * 8.5, y_osc + 112, "Cmd (SetVID)", size=9, color=MUTED))
    frags.append(text(x_sig_start + clk_step * 15, y_osc + 112, "VID Data (8 bit)", size=9, color=MUTED))
    frags.append(text(x_sig_start + clk_step * 24, y_osc + 112, "Slave Response", size=9, color=MUTED))

    # ALERT# лінія (Open-Drain активний низький рівень)
    y_al_hi = y_osc + 145
    y_al_lo = y_osc + 165
    alert_pts = [
        (x_sig_start, y_al_hi),
        (x_sig_start + clk_step * 14, y_al_hi),
        (x_sig_start + clk_step * 14, y_al_lo),  # VR генерує переривання (VR_HOT / OCP)
        (x_sig_start + clk_step * 25, y_al_lo),
        (x_sig_start + clk_step * 25, y_al_hi),  # Відновлення після читання статусу
        (x_sig_end, y_al_hi)
    ]
    p_alert = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in alert_pts)
    frags.append(f'<path d="{p_alert}" fill="none" stroke="{POS}" stroke-width="2"/>')
    frags.append(text(x_sig_start + clk_step * 19.5, y_al_lo + 18, "Апаратне переривання VR_HOT / OCP (VRM тягне лінію до GND)", size=10, color=POS, bold=True, anchor="middle"))

    render(os.path.join(IMG, "svid-frame-protocol.svg"), W, H, *frags)


if __name__ == "__main__":
    print("Генерація SVG-фігур...")
    fig_vid_closed_loop()
    fig_parallel_vs_serial()
    fig_dynamic_vid_transition()
    fig_svid_frame_protocol()
    print("Успішно згенеровано 4 фігури в папці img/")
