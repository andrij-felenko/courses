# -*- coding: utf-8 -*-
"""Фігури до теми «Термінування ліній передачі».
Запуск: python figs.py  →  пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Фізика хвилі та відбиття на межі імпедансів ────────────────────────────
def fig_wave_reflection_concept():
    W, H = 820, 460
    f = [
        text(W / 2, 28, "Хвиля в лінії передачі: падаючий фронт, межа і відбиття", size=16, bold=True)
    ]

    # --- Верхня частина: Падаюча хвиля вздовж розподіленої лінії Z₀ ---
    f.append(text(80, 68, "1. Поширення падаючого фронту (V⁺, I⁺) у лінії з хвильовим опором Z₀", size=13, bold=True, anchor="start", color=INK))

    # Джерело TX
    f.append(rect(40, 85, 70, 70, fill="#eaf0fd", stroke=NEG, sw=1.8))
    f.append(text(75, 120, "TX", size=14, bold=True, color=NEG))
    f.append(text(75, 138, "V_step", size=11, color=MUTED))

    # Лінія передачі (провідник і опорна земля)
    f.append(line(110, 105, 710, 105, color=INK, sw=2.4))
    f.append(line(110, 145, 710, 145, color=MUTED, sw=2.0))
    f.append(text(410, 95, "Сигнальний провідник (L₀ на одиницю довжини)", size=11, color=INK))
    f.append(text(410, 160, "Опорна земля GND (C₀ на одиницю довжини) → Z₀ = √(L₀/C₀)", size=11, color=MUTED))

    # Хвильовий фронт що рухається вправо
    f.append(arrow(260, 105, 340, 105, color=POS, sw=3.0))
    f.append(text(300, 80, "Падаюча хвиля V⁺", size=12, bold=True, color=POS))
    f.append(text(300, 125, "I⁺ = V⁺ / Z₀", size=11, bold=True, color=POS))

    # Приймач RX (навантаження Z_L)
    f.append(rect(710, 85, 75, 70, fill="#fef6e7", stroke="#d97706", sw=1.8))
    f.append(text(747, 118, "RX", size=14, bold=True, color="#d97706"))
    f.append(text(747, 136, "Z_L", size=12, bold=True, color="#d97706"))

    # Розділювач
    f.append(line(40, 185, 780, 185, color="#d0d4d8", sw=1.2, dash="4,4"))

    # --- Нижня частина: Два крайні сценарії на межі навантаження ---
    f.append(text(80, 210, "2. Що відбувається на кінці лінії при розриві (Z_L = ∞) проти узгодження (Z_L = Z₀)", size=13, bold=True, anchor="start", color=INK))

    # Випадок А: Розірваний кінець (Z_L = ∞, Γ = +1)
    bx_a = fitbox(50, 230, 345, 205, [
        "Неузгоджений кінець (Z_L = ∞, розрив)",
        "Струм на розриві не може текти (I_L = 0).",
        "Щоб скомпенсувати струм I⁺, лінія",
        "породжує відбиту хвилю зі струмом I⁻ = −I⁺.",
        "При цьому напруга подвоюється:",
        "V⁻ = +V⁺  →  V_total = V⁺ + V⁻ = 2 · V⁺",
        "Коефіцієнт відбиття Γ = +1.0 (викид напруги!)"
    ], size=11.5, fill="#fdecea", stroke=POS, sw=1.5)
    f.append(bx_a)

    # Випадок Б: Ідеальне узгодження (Z_L = Z₀, Γ = 0)
    bx_b = fitbox(425, 230, 345, 205, [
        "Узгоджений кінець (Z_L = Z₀, термінатор)",
        "Резистор R_L = Z₀ приймає струм I_L = V⁺ / Z₀",
        "точно у відповідності до закону лінії.",
        "Уся енергія хвилі перетворюється на тепло.",
        "Відбита хвиля взагалі не виникає:",
        "V⁻ = 0  →  V_total = V⁺ (чистий фронт)",
        "Коефіцієнт відбиття Γ = 0.0 (нуль відлуння)"
    ], size=11.5, fill="#eafaf1", stroke=FIELD, sw=1.5)
    f.append(bx_b)

    render(os.path.join(IMG, "wave-reflection-concept.svg"), W, H, *f)


# ── 2. Дзвін (Ringing), викиди та помилкові спрацьовування компаратора ─────────
def fig_ringing_glitch():
    W, H = 820, 480
    f = [
        text(W / 2, 28, "Дзвін у неузгодженій лінії: викиди напруги та хибне тактування", size=16, bold=True)
    ]

    # Графік напруги V(t) на вході приймача RX
    gx, gy, gw, gh = 90, 80, 680, 240

    # Сітка та осі
    f.append(line(gx, gy + gh, gx + gw, gy + gh, color=LINE, sw=1.5))  # вісь t
    f.append(line(gx, gy, gx, gy + gh, color=LINE, sw=1.5))            # вісь V
    f.append(text(gx + gw + 15, gy + gh + 4, "t", size=13, bold=True, color=INK))
    f.append(text(gx - 10, gy + 10, "V", size=13, bold=True, color=INK, anchor="end"))

    # Рівні напруги: 0V, V_IL, V_threshold, V_IH, V_DD
    y_gnd = gy + gh - 40          # 0V (GND)
    y_vil = gy + gh - 90          # V_IL (0.8V)
    y_vth = gy + gh - 120         # V_th (1.65V)
    y_vih = gy + gh - 150         # V_IH (2.0V)
    y_vdd = gy + gh - 180         # V_DD (3.3V)

    # Пунктирні горизонталі рівнів
    f.append(line(gx, y_vdd, gx + gw, y_vdd, color=MUTED, sw=1.0, dash="3,3"))
    f.append(text(gx - 8, y_vdd + 4, "V_DD (3.3 В)", size=11, color=MUTED, anchor="end"))

    # Порогова невизначена зона (між V_IL та V_IH)
    f.append(rect(gx, y_vih, gw, y_vil - y_vih, fill="#fef3c7", stroke="none"))
    f.append(line(gx, y_vth, gx + gw, y_vth, color="#d97706", sw=1.2, dash="4,4"))
    f.append(text(gx - 8, y_vth + 4, "Порог V_th", size=11, bold=True, color="#d97706", anchor="end"))
    f.append(text(gx + gw - 10, y_vth - 8, "Невизначена зона (V_IL .. V_IH)", size=10, italic=True, color="#b45309", anchor="end"))

    f.append(line(gx, y_gnd, gx + gw, y_gnd, color=MUTED, sw=1.0))
    f.append(text(gx - 8, y_gnd + 4, "0 В (GND)", size=11, color=MUTED, anchor="end"))

    # Крива сигналу з сильним дзвоном (Ringing)
    # t0: (gx, y_gnd) -> швидкий перепад -> перший пік (overshoot) -> провал (undershoot) -> другий пік -> затухання
    # Координати точок дзвону
    pts = [
        (gx, y_gnd),
        (gx + 60, y_gnd),
        (gx + 110, y_vdd - 50),   # перший викид (Overshoot 5.2V)
        (gx + 160, y_vil + 20),   # глибокий провал нижче V_th і V_IL (Undershoot 0.6V!)
        (gx + 220, y_vdd - 25),   # другий викид (4.0V)
        (gx + 280, y_vth - 15),   # другий спад (2.1V)
        (gx + 340, y_vdd - 8),    # стабілізація
        (gx + 420, y_vdd),
        (gx + gw - 40, y_vdd)
    ]
    # Побудова плавної полілінії
    path_d = ["M %.1f %.1f" % pts[0]]
    for i in range(1, len(pts)):
        p0 = pts[i - 1]
        p1 = pts[i]
        # cubic bezier
        cx1 = (p0[0] + p1[0]) / 2.0
        path_d.append("C %.1f %.1f, %.1f %.1f, %.1f %.1f" % (cx1, p0[1], cx1, p1[1], p1[0], p1[1]))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(path_d), POS))

    # Ідеальний сигнал (пунктир зеленим)
    f.append('<path d="M %d %d L %d %d L %d %d L %d %d" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="4,4"/>' %
             (gx, y_gnd, gx + 60, y_gnd, gx + 110, y_vdd, gx + gw - 40, y_vdd, FIELD))
    f.append(text(gx + 400, y_vdd - 15, "Узгоджена лінія (чистий фронт)", size=11, bold=True, color=FIELD))

    # Стрілки та позначки критичних явищ
    # 1. Викид напруги Overshoot
    f.append(arrow(gx + 110, y_vdd - 75, gx + 110, y_vdd - 55, color=POS, sw=1.8))
    f.append(text(gx + 110, y_vdd - 82, "Викид Overshoot (+5.2 В)", size=11, bold=True, color=POS))
    f.append(text(gx + 110, y_vdd - 68, "Загроза пробою входу ESD", size=10, color=POS))

    # 2. Помилковий перетин порогу Glitch
    f.append(circle(gx + 138, y_vth, 6, fill="#fee2e2", stroke=POS, sw=2.0))
    f.append(circle(gx + 185, y_vth, 6, fill="#fee2e2", stroke=POS, sw=2.0))
    f.append(arrow(gx + 160, gy + gh + 15, gx + 160, y_vil + 25, color=POS, sw=1.8))
    f.append(text(gx + 160, gy + gh + 30, "Провал нижче порогу V_th!", size=11, bold=True, color=POS))
    f.append(text(gx + 160, gy + gh + 44, "→ Хибне повторне спрацьовування", size=10, bold=True, color=POS))

    # Нижня рамка з поясненням
    bx = fitbox(50, 390, 720, 75, [
        "Небезпека неузгодженої довгої лінії: коли фронт швидший за час подвійного пробігу (t_rise < 2 · t_prop),",
        "багаторазові відбиття породжують дзвін (Ringing). Провал напруги перетинає поріг спрацьовування",
        "компаратора вдруге — приймач фіксує фальшивий тактовий імпульс (Glitch), руйнуючи передачу даних."
    ], size=11.5, fill="#f8fafc", stroke=MUTED, sw=1.2)
    f.append(bx)

    render(os.path.join(IMG, "ringing-glitch.svg"), W, H, *f)


# ── 3. Топології термінування: послідовне, паралельне, Тевеніна, AC ────────────
def fig_series_vs_parallel_topologies():
    W, H = 840, 560
    f = [
        text(W / 2, 26, "Основні топології термінування цифрових ліній", size=16, bold=True)
    ]

    # Схема 1: Послідовне термінування біля джерела (Series Source Termination)
    f.append(text(60, 62, "А. Послідовне термінування біля джерела (Series Termination, SPI / SDIO / UART)", size=12.5, bold=True, anchor="start", color=INK))
    # TX
    f.append(rect(60, 78, 65, 45, fill="#eaf0fd", stroke=NEG, sw=1.5))
    f.append(text(92, 105, "TX", size=13, bold=True, color=NEG))
    # Резистор Rs
    f.append(line(125, 100, 160, 100, color=INK, sw=2.0))
    f.append(rect(160, 90, 45, 20, fill="#fef3c7", stroke="#d97706", sw=1.5))
    f.append(text(182, 104, "R_S", size=11, bold=True, color="#d97706"))
    f.append(line(205, 100, 480, 100, color=INK, sw=2.0))
    f.append(text(340, 90, "Лінія Z₀ (наприклад, 50 Ω)", size=10.5, color=MUTED))
    # RX
    f.append(rect(480, 78, 65, 45, fill="#fef6e7", stroke=LINE, sw=1.5))
    f.append(text(512, 105, "RX", size=13, bold=True, color=LINE))
    f.append(text(512, 135, "Вхід C_in (Z_L ≈ ∞)", size=10, color=MUTED))
    # Формула й опис праворуч
    bx1 = fitbox(570, 72, 240, 58, [
        "R_S = Z₀ − R_out (типово 22–33 Ω)",
        "• Нуль статичного споживання DC",
        "• Ідеально для ліній «точка–точка»"
    ], size=10.5, fill="#f4f6f8", stroke=MUTED, sw=1.0)
    f.append(bx1)

    # Схема 2: Паралельне термінування на кінці лінії (Parallel Termination)
    f.append(text(60, 185, "Б. Просте паралельне на кінці (Parallel Termination до GND або V_TT)", size=12.5, bold=True, anchor="start", color=INK))
    # TX
    f.append(rect(60, 200, 65, 45, fill="#eaf0fd", stroke=NEG, sw=1.5))
    f.append(text(92, 227, "TX", size=13, bold=True, color=NEG))
    f.append(line(125, 222, 480, 222, color=INK, sw=2.0))
    f.append(text(300, 212, "Лінія Z₀", size=10.5, color=MUTED))
    # RX
    f.append(rect(480, 200, 65, 45, fill="#fef6e7", stroke=LINE, sw=1.5))
    f.append(text(512, 227, "RX", size=13, bold=True, color=LINE))
    # Паралельний резистор R_L до GND
    f.append(line(450, 222, 450, 240, color=INK, sw=1.8))
    f.append(rect(440, 240, 20, 35, fill="#fef3c7", stroke="#d97706", sw=1.5))
    f.append(text(450, 260, "R_L", size=10.5, bold=True, color="#d97706"))
    f.append(line(450, 275, 450, 290, color=INK, sw=1.8))
    f.append(line(438, 290, 462, 290, color=MUTED, sw=2.0))  # GND
    bx2 = fitbox(570, 195, 240, 58, [
        "R_L = Z₀ (типово 50 Ω)",
        "• Поглинає хвилю без відбиття",
        "• Високе споживання DC струму!"
    ], size=10.5, fill="#f4f6f8", stroke=MUTED, sw=1.0)
    f.append(bx2)

    # Схема 3: Термінування Тевеніна / Дільник (Thevenin / Split Termination)
    f.append(text(60, 310, "В. Термінування Тевеніна (Thevenin Split: подільник VDD / GND)", size=12.5, bold=True, anchor="start", color=INK))
    f.append(rect(60, 325, 65, 45, fill="#eaf0fd", stroke=NEG, sw=1.5))
    f.append(text(92, 352, "TX", size=13, bold=True, color=NEG))
    f.append(line(125, 347, 480, 347, color=INK, sw=2.0))
    # RX
    f.append(rect(480, 325, 65, 45, fill="#fef6e7", stroke=LINE, sw=1.5))
    f.append(text(512, 352, "RX", size=13, bold=True, color=LINE))
    # Подільник R1 до VDD, R2 до GND
    f.append(line(450, 347, 450, 330, color=INK, sw=1.8))
    f.append(rect(440, 295, 20, 35, fill="#fef3c7", stroke="#d97706", sw=1.5))
    f.append(text(450, 315, "R1", size=10.5, bold=True, color="#d97706"))
    f.append(line(450, 295, 450, 282, color=POS, sw=1.8))
    f.append(text(450, 276, "V_DD", size=10, bold=True, color=POS))

    f.append(line(450, 347, 450, 365, color=INK, sw=1.8))
    f.append(rect(440, 365, 20, 35, fill="#fef3c7", stroke="#d97706", sw=1.5))
    f.append(text(450, 385, "R2", size=10.5, bold=True, color="#d97706"))
    f.append(line(450, 400, 450, 412, color=INK, sw=1.8))
    f.append(line(438, 412, 462, 412, color=MUTED, sw=2.0))  # GND
    bx3 = fitbox(570, 320, 240, 58, [
        "R1 || R2 = Z₀ ; V_th = V_DD · R2/(R1+R2)",
        "• Задає напругу спокою шини",
        "• Сталий струм через дільник"
    ], size=10.5, fill="#f4f6f8", stroke=MUTED, sw=1.0)
    f.append(bx3)

    # Схема 4: AC-термінування (AC Termination: RC-ланцюг)
    f.append(text(60, 435, "Г. AC-термінування (RC-ланцюг: узгодження тільки на фронтах)", size=12.5, bold=True, anchor="start", color=INK))
    f.append(rect(60, 450, 65, 45, fill="#eaf0fd", stroke=NEG, sw=1.5))
    f.append(text(92, 477, "TX", size=13, bold=True, color=NEG))
    f.append(line(125, 472, 480, 472, color=INK, sw=2.0))
    # RX
    f.append(rect(480, 450, 65, 45, fill="#fef6e7", stroke=LINE, sw=1.5))
    f.append(text(512, 477, "RX", size=13, bold=True, color=LINE))
    # RC коло
    f.append(line(450, 472, 450, 490, color=INK, sw=1.8))
    f.append(rect(440, 490, 20, 30, fill="#fef3c7", stroke="#d97706", sw=1.5))
    f.append(text(450, 507, "R", size=10.5, bold=True, color="#d97706"))
    f.append(line(450, 520, 450, 528, color=INK, sw=1.8))
    # Конденсатор C
    f.append(line(438, 528, 462, 528, color=INK, sw=2.0))
    f.append(line(438, 533, 462, 533, color=INK, sw=2.0))
    f.append(text(475, 532, "C", size=11, bold=True, color=INK))
    f.append(line(450, 533, 450, 545, color=INK, sw=1.8))
    f.append(line(438, 545, 462, 545, color=MUTED, sw=2.0))  # GND
    bx4 = fitbox(570, 445, 240, 58, [
        "R = Z₀ ; C > 3 · t_prop / Z₀ (типово 50–100 пФ)",
        "• Нуль постійного споживання DC!",
        "• Невелике збільшення затримки фронту"
    ], size=10.5, fill="#f4f6f8", stroke=MUTED, sw=1.0)
    f.append(bx4)

    render(os.path.join(IMG, "series-vs-parallel-topologies.svg"), W, H, *f)


# ── 4. Диференційне термінування шин: CAN / RS-485 та Split Termination ───────
def fig_differential_bus_termination():
    W, H = 840, 470
    f = [
        text(W / 2, 28, "Термінування магістральних диференційних шин (RS-485, CAN)", size=16, bold=True)
    ]

    # --- Верхня частина: Стандартне термінування на кінцях магістралі (120 Ω) ---
    f.append(text(60, 65, "1. Магістраль зі 120-омними термінаторами суворо на двох фізичних краях", size=13, bold=True, anchor="start", color=INK))

    # Дві диференційні лінії CAN_H / CAN_L або RS-485 A / B
    y_h = 100
    y_l = 140
    f.append(line(110, y_h, 730, y_h, color=POS, sw=2.4))
    f.append(text(80, y_h + 4, "CAN_H / A", size=11, bold=True, color=POS, anchor="end"))
    f.append(line(110, y_l, 730, y_l, color=NEG, sw=2.4))
    f.append(text(80, y_l + 4, "CAN_L / B", size=11, bold=True, color=NEG, anchor="end"))

    # Лівий термінатор 120 Ω
    f.append(line(130, y_h, 130, y_h + 10, color=INK, sw=1.8))
    f.append(rect(120, y_h + 10, 20, 20, fill="#fef3c7", stroke="#d97706", sw=1.5))
    f.append(text(130, y_h + 23, "120Ω", size=9.5, bold=True, color="#d97706"))
    f.append(line(130, y_h + 30, 130, y_l, color=INK, sw=1.8))
    f.append(text(130, y_l + 18, "Край 1", size=10.5, bold=True, color=FIELD))

    # Правий термінатор 120 Ω
    f.append(line(710, y_h, 710, y_h + 10, color=INK, sw=1.8))
    f.append(rect(700, y_h + 10, 20, 20, fill="#fef3c7", stroke="#d97706", sw=1.5))
    f.append(text(710, y_h + 23, "120Ω", size=9.5, bold=True, color="#d97706"))
    f.append(line(710, y_h + 30, 710, y_l, color=INK, sw=1.8))
    f.append(text(710, y_l + 18, "Край 2", size=10.5, bold=True, color=FIELD))

    # Проміжні вузли (Nodes) зі шлейфами (stubs)
    for nx, nname in [(270, "Вузол 1"), (420, "Вузол 2"), (570, "Вузол 3")]:
        f.append(line(nx - 5, y_h, nx - 5, y_h + 60, color=POS, sw=1.5, dash="2,2"))
        f.append(line(nx + 5, y_l, nx + 5, y_h + 60, color=NEG, sw=1.5, dash="2,2"))
        f.append(rect(nx - 35, y_h + 60, 70, 36, fill="#f4f6f8", stroke=MUTED, sw=1.2))
        f.append(text(nx, y_h + 82, nname, size=11, bold=True, color=INK))
        f.append(text(nx, y_h + 110, "Без R_term!", size=10, bold=True, color=POS))

    # Пояснення до верхньої частини
    f.append(text(420, y_h - 12, "Еквівалентний опір шини: 120 Ω || 120 Ω = 60 Ω", size=11, bold=True, color=FIELD))

    # Розділювач
    f.append(line(40, 275, 800, 275, color="#d0d4d8", sw=1.2, dash="4,4"))

    # --- Нижня частина: Роздільне термінування (Split Termination) у CAN ---
    f.append(text(60, 302, "2. Роздільне термінування (Split Termination): фільтрація синфазних завад", size=13, bold=True, anchor="start", color=INK))

    sy_h = 335
    sy_l = 415
    f.append(line(110, sy_h, 450, sy_h, color=POS, sw=2.4))
    f.append(text(80, sy_h + 4, "CAN_H", size=11, bold=True, color=POS, anchor="end"))
    f.append(line(110, sy_l, 450, sy_l, color=NEG, sw=2.4))
    f.append(text(80, sy_l + 4, "CAN_L", size=11, bold=True, color=NEG, anchor="end"))

    # Split termination: 60 Ω + C_split + 60 Ω
    cx = 320
    f.append(line(cx, sy_h, cx, sy_h + 12, color=INK, sw=1.8))
    f.append(rect(cx - 10, sy_h + 12, 20, 22, fill="#fef3c7", stroke="#d97706", sw=1.5))
    f.append(text(cx, sy_h + 27, "60Ω", size=10, bold=True, color="#d97706"))
    f.append(line(cx, sy_h + 34, cx, sy_h + 46, color=INK, sw=1.8))

    # Середня точка і конденсатор C_split до GND
    f.append(circle(cx, sy_h + 46, 3, fill=INK, stroke=INK))
    f.append(line(cx, sy_h + 46, cx + 45, sy_h + 46, color=INK, sw=1.8))
    # Конденсатор
    f.append(line(cx + 45, sy_h + 38, cx + 45, sy_h + 54, color=INK, sw=2.0))
    f.append(line(cx + 50, sy_h + 38, cx + 50, sy_h + 54, color=INK, sw=2.0))
    f.append(line(cx + 50, sy_h + 46, cx + 70, sy_h + 46, color=INK, sw=1.8))
    f.append(line(cx + 70, sy_h + 36, cx + 70, sy_h + 56, color=MUTED, sw=2.0))  # GND
    f.append(text(cx + 47, sy_h + 26, "C_split (4.7 нФ)", size=10, bold=True, color=MUTED))

    # Нижній резистор 60 Ω
    f.append(line(cx, sy_h + 46, cx, sy_h + 58, color=INK, sw=1.8))
    f.append(rect(cx - 10, sy_h + 58, 20, 22, fill="#fef3c7", stroke="#d97706", sw=1.5))
    f.append(text(cx, sy_h + 73, "60Ω", size=10, bold=True, color="#d97706"))
    f.append(line(cx, sy_h + 80, cx, sy_l, color=INK, sw=1.8))

    # Текстова врізка праворуч
    bx_split = fitbox(480, 310, 320, 135, [
        "Перевага Split Termination:",
        "• Для диференційного сигналу: R_diff = 60 + 60 = 120 Ω",
        "  (повна відповідність стандарту ISO 11898).",
        "• Для синфазної завади (Common-Mode Noise):",
        "  середня точка заземлена через C_split (4.7 нФ),",
        "  що ефективно зливає ВЧ-шум на землю й",
        "  значно знижує електромагнітне випромінювання (EMI)."
    ], size=11, fill="#f8fafc", stroke=MUTED, sw=1.2)
    f.append(bx_split)

    render(os.path.join(IMG, "differential-bus-termination.svg"), W, H, *f)


# ── 5. Діаграма відбиттів (Bounce Lattice Diagram) для math-вставки ───────────
def fig_bounce_diagram():
    W, H = 820, 520
    f = [
        text(W / 2, 28, "Ґраткова діаграма відбиттів (Bounce Diagram) для неузгодженої лінії", size=16, bold=True)
    ]

    # Дві вертикальні осі: x = 0 (TX, джерело) та x = L (RX, навантаження)
    x_src = 180
    x_ld = 540
    y_top = 80
    y_bot = 440

    # Вертикальні осі простору x
    f.append(line(x_src, y_top, x_src, y_bot, color=LINE, sw=2.0))
    f.append(line(x_ld, y_top, x_ld, y_bot, color=LINE, sw=2.0))

    f.append(text(x_src, y_top - 18, "Джерело x = 0 (TX)", size=13, bold=True, color=NEG))
    f.append(text(x_src, y_top - 4, "R_S = 10 Ω (Γ_S = −0.67)", size=11, color=NEG))

    f.append(text(x_ld, y_top - 18, "Навантаження x = L (RX)", size=13, bold=True, color=POS))
    f.append(text(x_ld, y_top - 4, "Z_L = ∞ (Γ_L = +1.0)", size=11, color=POS))

    # Стрілка часу t, що тече вниз
    f.append(arrow(60, y_top, 60, y_bot, color=MUTED, sw=2.0))
    f.append(text(45, y_top + 15, "Час t", size=12, bold=True, color=MUTED, anchor="end"))

    # Часові кроки t = 0, t_d, 2t_d, 3t_d, 4t_d, 5t_d
    step_y = 60
    times = [
        (0, "t = 0", "V_src = 2.75 В", ""),
        (1, "t = t_d", "", "V_load = 5.50 В (викид)"),
        (2, "t = 2t_d", "V_src = 0.92 В", ""),
        (3, "t = 3t_d", "", "V_load = 1.83 В (провал)"),
        (4, "t = 4t_d", "V_src = 4.28 В", ""),
        (5, "t = 5t_d", "", "V_load = 3.67 В"),
    ]

    for idx, tlabel, src_v, ld_v in times:
        y = y_top + idx * step_y
        f.append(line(55, y, 65, y, color=MUTED, sw=1.5))
        f.append(text(75, y + 4, tlabel, size=11, color=MUTED, anchor="start"))
        if src_v:
            f.append(text(x_src - 15, y + 4, src_v, size=11, bold=True, color=NEG, anchor="end"))
            f.append(circle(x_src, y, 4, fill=NEG, stroke=INK))
        if ld_v:
            f.append(text(x_ld + 15, y + 4, ld_v, size=11, bold=True, color=POS, anchor="start"))
            f.append(circle(x_ld, y, 4, fill=POS, stroke=INK))

    # Промені відбиття зиґзаґом (падаючі та відбиті хвилі)
    # 0 -> t_d: падаюча V1+ = +2.75 В
    f.append(arrow(x_src, y_top, x_ld, y_top + step_y, color=POS, sw=2.2))
    f.append(text((x_src + x_ld) / 2, y_top + step_y / 2 - 8, "V₁⁺ = +2.75 В", size=11, bold=True, color=POS))

    # t_d -> 2t_d: відбита V1- = +2.75 В (Γ_L = +1.0)
    f.append(arrow(x_ld, y_top + step_y, x_src, y_top + 2 * step_y, color=NEG, sw=2.2))
    f.append(text((x_src + x_ld) / 2, y_top + 1.5 * step_y - 8, "V₁⁻ = +2.75 В (відбиття від розриву)", size=11, bold=True, color=NEG))

    # 2t_d -> 3t_d: відбита від джерела V2+ = −1.83 В (Γ_S = −0.67)
    f.append(arrow(x_src, y_top + 2 * step_y, x_ld, y_top + 3 * step_y, color=POS, sw=2.2))
    f.append(text((x_src + x_ld) / 2, y_top + 2.5 * step_y - 8, "V₂⁺ = −1.83 В (перевертання фази)", size=11, bold=True, color=POS))

    # 3t_d -> 4t_d: відбита V2- = −1.83 В
    f.append(arrow(x_ld, y_top + 3 * step_y, x_src, y_top + 4 * step_y, color=NEG, sw=2.2))
    f.append(text((x_src + x_ld) / 2, y_top + 3.5 * step_y - 8, "V₂⁻ = −1.83 В", size=11, bold=True, color=NEG))

    # 4t_d -> 5t_d: V3+ = +1.22 В
    f.append(arrow(x_src, y_top + 4 * step_y, x_ld, y_top + 5 * step_y, color=POS, sw=1.8))
    f.append(text((x_src + x_ld) / 2, y_top + 4.5 * step_y - 8, "V₃⁺ = +1.22 В → асимптота до 3.3 В", size=10.5, color=MUTED))

    # Нижня плашка
    bx = fitbox(60, 455, 700, 55, [
        "Ґраткова діаграма унаочнює стрибки напруги: кожен промінь додає нову хвилю до поточної суми.",
        "При Γ_L = +1 (розрив) та Γ_S = −0.67 (потужний драйвер) напруга на навантаженні коливається:",
        "0 В  →  5.50 В (overshoot)  →  1.83 В (undershoot)  →  3.67 В  →  асимптотично до 3.30 В."
    ], size=11, fill="#f8fafc", stroke=MUTED, sw=1.2)
    f.append(bx)

    render(os.path.join(IMG, "bounce-diagram.svg"), W, H, *f)


if __name__ == "__main__":
    fig_wave_reflection_concept()
    fig_ringing_glitch()
    fig_series_vs_parallel_topologies()
    fig_differential_bus_termination()
    fig_bounce_diagram()
    print("Всі фігури згенеровано успішно у ./img/")
