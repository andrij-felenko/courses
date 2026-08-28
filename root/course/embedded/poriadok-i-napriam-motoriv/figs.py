# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — Порівняння стандартів нумерації Betaflight vs PX4 Quad-X
# ════════════════════════════════════════════════════════════════════════════
def fig_motor_order_standards():
    W, H = 880, 460
    body = ""

    panels = [
        (25, 400, "Betaflight / Cleanflight (Quad-X)", [
            ("M1: Задній Правий (RR)", "CCW (Props In)", POS),
            ("M2: Передній Правий (FR)", "CW (Props In)", NEG),
            ("M3: Задній Лівий (RL)", "CW (Props In)", NEG),
            ("M4: Передній Лівий (FL)", "CCW (Props In)", POS),
        ], [
            (1, 65, 55, "1 (RR)", POS, "CCW ↺"),
            (2, 65, -55, "2 (FR)", NEG, "CW ↻"),
            (3, -65, 55, "3 (RL)", NEG, "CW ↻"),
            (4, -65, -55, "4 (FL)", POS, "CCW ↺"),
        ]),
        (455, 400, "PX4 / ArduPilot (Quad-X)", [
            ("M1: Передній Правий (FR)", "CCW (Стандарт)", POS),
            ("M2: Задній Лівий (RL)", "CCW (Стандарт)", POS),
            ("M3: Передній Лівий (FL)", "CW (Стандарт)", NEG),
            ("M4: Задній Правий (RR)", "CW (Стандарт)", NEG),
        ], [
            (1, 65, -55, "1 (FR)", POS, "CCW ↺"),
            (2, -65, 55, "2 (RL)", POS, "CCW ↺"),
            (3, -65, -55, "3 (FL)", NEG, "CW ↻"),
            (4, 65, 55, "4 (RR)", NEG, "CW ↻"),
        ]),
    ]

    for px, pw, title, motors_info, motors_pos in panels:
        py = 35
        ph = 345
        body += rect(px, py, pw, ph, fill=FILL, stroke=LINE, sw=1.5, rx=8)
        body += text(px + pw / 2, py + 22, title, size=13, color=INK, bold=True)

        cx = px + pw / 2
        cy = py + 125

        # Стрілка носа
        body += arrow(cx, cy - 25, cx, cy - 72, color=FIELD, sw=2)
        body += text(cx, cy - 78, "Ніс (Forward)", size=10.5, color=FIELD, bold=True)

        # Промені рами X
        body += line(cx - 65, cy - 55, cx + 65, cy + 55, color="#94a3b8", sw=4)
        body += line(cx - 65, cy + 55, cx + 65, cy - 55, color="#94a3b8", sw=4)

        # Центр FC
        body += rect(cx - 20, cy - 20, 40, 40, fill="#e2e8f0", stroke=LINE, sw=1.5, rx=4)
        body += text(cx, cy + 4, "FC", size=11, color=INK, bold=True)

        # Мотори
        for num, mx, my, label, col, spin in motors_pos:
            mcx = cx + mx
            mcy = cy + my
            body += circle(mcx, mcy, 24, fill="#ffffff", stroke=col, sw=2)
            body += text(mcx, mcy - 3, str(num), size=12, color=col, bold=True)
            body += text(mcx, mcy + 10, spin, size=9.5, color=col, bold=True)
            lbl_x = mcx + (32 if mx > 0 else -32)
            lbl_y = mcy + (4 if my > 0 else -4)
            lbl_anchor = "start" if mx > 0 else "end"
            body += text(lbl_x, lbl_y, label, size=10, color=INK, bold=True, anchor=lbl_anchor)

        # Таблиця таймерів
        ty = py + 238
        body += line(px + 15, ty - 10, px + pw - 15, ty - 10, color="#cbd5e1", sw=1)
        body += text(px + pw / 2, ty + 2, "Призначення таймерних виходів FC:", size=11, color=MUTED, bold=True)
        ty += 22
        for mot_name, rot_name, col in motors_info:
            body += circle(px + 30, ty - 3, 3, fill=col, stroke=col, sw=1)
            body += text(px + 42, ty, mot_name, size=10.5, color=INK, bold=True, anchor="start")
            body += text(px + pw - 25, ty, rot_name, size=10, color=col, bold=True, anchor="end")
            ty += 19

    # Банер попередження
    by = 395
    body += rect(25, by, 830, 48, fill="#fee2e2", stroke=POS, sw=1.5, rx=6)
    body += text(440, by + 18, "УВАГА: Нумерації абсолютно несумісні! Мотор 1 у Betaflight — це Задній Правий, а в PX4 — Передній Правий.", size=11, color=POS, bold=True)
    body += text(440, by + 34, "Якщо перенести прошивку без перемапінгу ресурсів — контролер миттєво перекине апарат при спробі зльоту.", size=10.5, color=POS)

    render(os.path.join(OUT, "motor-order-standards.svg"), W, H, body,
           title="Стандарти нумерації та обертання моторів: Betaflight проти PX4 Quad-X")


# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Фізика петлі позитивного зворотного зв'язку (Positive Feedback)
# ════════════════════════════════════════════════════════════════════════════
def fig_positive_feedback_loop():
    W, H = 860, 390
    body = ""

    # 1. Верхній блок
    body += rect(25, 30, 810, 160, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8)
    body += text(40, 52, "1. Негативний зворотний зв'язок (Правильний мікшер): Самостабілізація", size=12, color=FIELD, bold=True, anchor="start")

    bx_y = 105
    body += rect(40, bx_y - 25, 120, 50, fill="#ffffff", stroke=LINE, sw=1.5, rx=4)
    body += text(100, bx_y - 6, "Збурення", size=10.5, color=INK, bold=True)
    body += text(100, bx_y + 10, "+ω (крен вправо)", size=9.5, color=POS)

    body += arrow(160, bx_y, 195, bx_y, color=LINE, sw=1.5)

    body += rect(195, bx_y - 25, 130, 50, fill="#ffffff", stroke=LINE, sw=1.5, rx=4)
    body += text(260, bx_y - 6, "Гіроскоп + PID", size=10.5, color=INK, bold=True)
    body += text(260, bx_y + 10, "Помилка e = 0 − ω", size=9.5, color=MUTED)

    body += arrow(325, bx_y, 360, bx_y, color=LINE, sw=1.5)

    body += rect(360, bx_y - 25, 150, 50, fill="#ffffff", stroke=FIELD, sw=1.5, rx=4)
    body += text(435, bx_y - 6, "Мікшер (знак −)", size=10.5, color=FIELD, bold=True)
    body += text(435, bx_y + 10, "Тяга M_прав ↑, M_лів ↓", size=9.5, color=INK)

    body += arrow(510, bx_y, 545, bx_y, color=FIELD, sw=1.5)

    body += rect(545, bx_y - 25, 135, 50, fill="#ffffff", stroke=LINE, sw=1.5, rx=4)
    body += text(612, bx_y - 6, "Момент рами", size=10.5, color=INK, bold=True)
    body += text(612, bx_y + 10, "τ_віднов = −K·ω", size=9.5, color=FIELD, bold=True)

    body += arrow(680, bx_y, 715, bx_y, color=FIELD, sw=1.5)

    body += rect(715, bx_y - 25, 105, 50, fill="#ffffff", stroke=FIELD, sw=1.5, rx=4)
    body += text(767, bx_y - 6, "Результат", size=10.5, color=FIELD, bold=True)
    body += text(767, bx_y + 10, "e(t) → 0", size=10.5, color=FIELD, bold=True)

    body += text(430, 168, "PID створює протидіючий момент: крен вправо компенсується підняттям правого боку. Апарат вирівнюється.", size=10.5, color=INK)

    # 2. Нижній блок
    body += rect(25, 205, 810, 165, fill="#fef2f2", stroke=POS, sw=1.5, rx=8)
    body += text(40, 227, "2. Позитивний зворотний зв'язок (Переплутано мотори / інвертовано мікшер): Лавиноподібний переворот", size=12, color=POS, bold=True, anchor="start")

    bx2_y = 280
    body += rect(40, bx2_y - 25, 120, 50, fill="#ffffff", stroke=LINE, sw=1.5, rx=4)
    body += text(100, bx2_y - 6, "Мікро-збурення", size=10.5, color=INK, bold=True)
    body += text(100, bx2_y + 10, "+ω (вітер / люфт)", size=9.5, color=POS)

    body += arrow(160, bx2_y, 195, bx2_y, color=LINE, sw=1.5)

    body += rect(195, bx2_y - 25, 130, 50, fill="#ffffff", stroke=LINE, sw=1.5, rx=4)
    body += text(260, bx2_y - 6, "Гіроскоп + PID", size=10.5, color=INK, bold=True)
    body += text(260, bx2_y + 10, "Команда: «підняти»", size=9.5, color=MUTED)

    body += arrow(325, bx2_y, 360, bx2_y, color=LINE, sw=1.5)

    body += rect(360, bx2_y - 25, 150, 50, fill="#ffffff", stroke=POS, sw=1.5, rx=4)
    body += text(435, bx2_y - 6, "Помилковий мікшер", size=10.5, color=POS, bold=True)
    body += text(435, bx2_y + 10, "Тяга M_лів ↑ (НЕ ТОЙ!)", size=9.5, color=POS, bold=True)

    body += arrow(510, bx2_y, 545, bx2_y, color=POS, sw=1.5)

    body += rect(545, bx2_y - 25, 135, 50, fill="#ffffff", stroke=LINE, sw=1.5, rx=4)
    body += text(612, bx2_y - 6, "Момент рами", size=10.5, color=POS, bold=True)
    body += text(612, bx2_y + 10, "τ_руйн = +K·ω (розгін!)", size=9.5, color=POS, bold=True)

    body += arrow(680, bx2_y, 715, bx2_y, color=POS, sw=1.5)

    body += rect(715, bx2_y - 25, 105, 50, fill="#ffffff", stroke=POS, sw=1.5, rx=4)
    body += text(767, bx2_y - 6, "Наслідок", size=10.5, color=POS, bold=True)
    body += text(767, bx2_y + 10, "Фліп за 100 мс", size=10.5, color=POS, bold=True)

    body += text(430, 345, "Замість гальмування PID розкручує помилковий мотор: помилка росте експоненційно e(t) = e₀·exp(λt) до 100% насичення.", size=10.5, color=POS)

    render(os.path.join(OUT, "positive-feedback-loop.svg"), W, H, body,
           title="Негативний зворотний зв'язок проти небезпечної петлі позитивного зв'язку")


# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Схеми обертання: Props In проти Props Out
# ════════════════════════════════════════════════════════════════════════════
def fig_props_in_vs_props_out():
    W, H = 880, 430
    body = ""

    panels = [
        (25, 400, "Props In (Обертання всередину — Стандарт)", [
            ("Сміття та трава летять у камеру", POS),
            ("Зачіпання гілки затягує дрон у перешкоду", POS),
            ("Класична схема за замовчуванням", MUTED),
        ], False),
        (455, 400, "Props Out (Обертання назовні — Реверс)", [
            ("Трава, вода та бруд відкидаються від лінзи", FIELD),
            ("Удар об перешкоду відштовхує дрон назовні", FIELD),
            ("Менший вошаут (washout) при різкому маневрі", FIELD),
        ], True),
    ]

    for px, pw, title, notes, is_props_out in panels:
        py = 35
        ph = 375
        body += rect(px, py, pw, ph, fill=FILL, stroke=LINE, sw=1.5, rx=8)
        body += text(px + pw / 2, py + 22, title, size=12.5, color=INK, bold=True)

        cx = px + pw / 2
        cy = py + 145

        # Камера спереду рами
        body += rect(cx - 15, cy - 85, 30, 22, fill="#1e293b", stroke=LINE, sw=1.5, rx=3)
        body += circle(cx, cy - 80, 5, fill="#38bdf8", stroke="#0284c7", sw=1)
        body += text(cx, cy - 92, "Камера", size=10, color=MUTED, bold=True)

        # Промені рами
        body += line(cx - 70, cy - 55, cx + 70, cy + 55, color="#94a3b8", sw=4)
        body += line(cx - 70, cy + 55, cx + 70, cy - 55, color="#94a3b8", sw=4)
        body += rect(cx - 18, cy - 18, 36, 36, fill="#cbd5e1", stroke=LINE, sw=1.5, rx=4)
        body += text(cx, cy + 4, "FC", size=11, color=INK, bold=True)

        fl_spin = "CW ↻" if is_props_out else "CCW ↺"
        fr_spin = "CCW ↺" if is_props_out else "CW ↻"
        rl_spin = "CCW ↺" if is_props_out else "CW ↻"
        rr_spin = "CW ↻" if is_props_out else "CCW ↺"

        motors = [
            (cx - 70, cy - 55, "FL", fl_spin, FIELD if is_props_out else POS),
            (cx + 70, cy - 55, "FR", fr_spin, FIELD if is_props_out else POS),
            (cx - 70, cy + 55, "RL", rl_spin, MUTED),
            (cx + 70, cy + 55, "RR", rr_spin, MUTED),
        ]

        for mx, my, name, spin_text, col in motors:
            body += circle(mx, my, 26, fill="#ffffff", stroke=col, sw=2)
            body += text(mx, my - 4, name, size=11, color=INK, bold=True)
            body += text(mx, my + 9, spin_text, size=9.5, color=col, bold=True)

        if not is_props_out:
            body += arrow(cx - 45, cy - 55, cx - 18, cy - 70, color=POS, sw=2)
            body += arrow(cx + 45, cy - 55, cx + 18, cy - 70, color=POS, sw=2)
            body += text(cx, cy - 50, "Бруд летить на лінзу", size=10, color=POS, bold=True)
            body += rect(cx - 120, cy - 80, 10, 40, fill="#78350f", stroke="#451a03", sw=1, rx=2)
            body += text(cx - 115, cy - 86, "Гілка", size=9.5, color="#78350f", bold=True)
            body += arrow(cx - 70, cy - 55, cx - 105, cy - 65, color=POS, sw=1.8)
            body += text(cx - 65, cy - 20, "Втягує у гілку", size=9.5, color=POS, bold=True)
        else:
            body += arrow(cx - 45, cy - 65, cx - 75, cy - 85, color=FIELD, sw=2)
            body += arrow(cx + 45, cy - 65, cx + 75, cy - 85, color=FIELD, sw=2)
            body += text(cx, cy - 50, "Чиста лінза камери", size=10, color=FIELD, bold=True)
            body += rect(cx - 120, cy - 80, 10, 40, fill="#78350f", stroke="#451a03", sw=1, rx=2)
            body += text(cx - 115, cy - 86, "Гілка", size=9.5, color="#78350f", bold=True)
            body += arrow(cx - 95, cy - 65, cx - 60, cy - 55, color=FIELD, sw=1.8)
            body += text(cx - 65, cy - 20, "Відштовхує від гілки", size=9.5, color=FIELD, bold=True)

        ty = py + 275
        body += line(px + 20, ty - 10, px + pw - 20, ty - 10, color="#cbd5e1", sw=1)
        for note_txt, col in notes:
            body += circle(px + 25, ty - 3, 3, fill=col, stroke=col, sw=1)
            body += text(px + 36, ty, note_txt, size=10.5, color=INK, anchor="start")
            ty += 23

    render(os.path.join(OUT, "props-in-vs-props-out.svg"), W, H, body,
           title="Порівняння конфігурацій обертання гвинтів: Props In проти Props Out")


# ════════════════════════════════════════════════════════════════════════════
# Фігура 4 — Фізика балансу реактивних моментів за курсом (Yaw Torque)
# ════════════════════════════════════════════════════════════════════════════
def fig_yaw_reaction_torque_balance():
    W, H = 860, 370
    body = ""

    panels = [
        (25, "1. Висіння: Баланс реакцій", [
            ("2 мотори CCW дають момент +M_yaw", POS),
            ("2 мотори CW дають момент −M_yaw", NEG),
            ("Сума ΣM = 0 → курс стабільний", FIELD),
        ], 0),
        (300, "2. Розворот: Зміна балансу", [
            ("Пара CCW прискорюється (ω + Δ)", POS),
            ("Пара CW сповільнюється (ω − Δ)", NEG),
            ("Нескомпенсований момент повертає дрон", FIELD),
        ], 1),
        (575, "3. Помилка: Реверс одного мотора", [
            ("3 мотори в один бік, 1 у протилежний", POS),
            ("Постійний паразитний обертовий момент", POS),
            ("Шалена розкрутка («Spin of Death»)", POS),
        ], 2),
    ]

    for px, title, notes, mode in panels:
        pw = 260
        py = 35
        ph = 310
        body += rect(px, py, pw, ph, fill=FILL, stroke=LINE, sw=1.5, rx=8)
        body += text(px + pw / 2, py + 22, title, size=11.5, color=INK, bold=True)

        cx = px + pw / 2
        cy = py + 105

        body += line(cx - 45, cy - 35, cx + 45, cy + 35, color="#94a3b8", sw=3)
        body += line(cx - 45, cy + 35, cx + 45, cy - 35, color="#94a3b8", sw=3)
        body += circle(cx, cy, 10, fill="#cbd5e1", stroke=LINE, sw=1.5)

        if mode == 0:
            m_data = [
                (cx - 45, cy - 35, "CCW", POS, 15),
                (cx + 45, cy - 35, "CW", NEG, 15),
                (cx - 45, cy + 35, "CW", NEG, 15),
                (cx + 45, cy + 35, "CCW", POS, 15),
            ]
            body += text(cx, cy + 58, "Σ M_yaw = 0 (Нерухомий)", size=10.5, color=FIELD, bold=True)
        elif mode == 1:
            m_data = [
                (cx - 45, cy - 35, "CCW ↑", POS, 19),
                (cx + 45, cy - 35, "CW ↓", NEG, 11),
                (cx - 45, cy + 35, "CW ↓", NEG, 11),
                (cx + 45, cy + 35, "CCW ↑", POS, 19),
            ]
            body += arrow(cx - 15, cy - 22, cx + 15, cy - 22, color=FIELD, sw=2)
            body += text(cx, cy + 58, "Обертання за годинниковою ↷", size=10.5, color=FIELD, bold=True)
        else:
            m_data = [
                (cx - 45, cy - 35, "CCW", POS, 15),
                (cx + 45, cy - 35, "CCW!", POS, 15),
                (cx - 45, cy + 35, "CW", NEG, 15),
                (cx + 45, cy + 35, "CCW", POS, 15),
            ]
            body += arrow(cx - 18, cy - 20, cx + 18, cy - 20, color=POS, sw=2.5)
            body += text(cx, cy + 58, "Некерована дзиґа!", size=10.5, color=POS, bold=True)

        for mx, my, spin_lbl, col, rad in m_data:
            body += circle(mx, my, rad, fill="#ffffff", stroke=col, sw=1.8)
            body += text(mx, my + 3, spin_lbl, size=9.5, color=col, bold=True)

        ty = py + 200
        body += line(px + 15, ty - 10, px + pw - 15, ty - 10, color="#cbd5e1", sw=1)
        for note_txt, col in notes:
            body += circle(px + 20, ty - 3, 2.5, fill=col, stroke=col, sw=1)
            body += text(px + 28, ty, note_txt, size=10, color=INK, anchor="start")
            ty += 23

    render(os.path.join(OUT, "yaw-reaction-torque-balance.svg"), W, H, body,
           title="Фізика балансу реактивних моментів по осі курсу (Yaw)")


# ════════════════════════════════════════════════════════════════════════════
# Фігура 5 — Архітектура 4-Way Passthrough для конфігурації через DShot / BLHeli
# ════════════════════════════════════════════════════════════════════════════
def fig_dshot_passthrough_architecture():
    W, H = 860, 360
    body = ""

    # 1. ПК
    body += rect(25, 50, 180, 250, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6)
    body += text(115, 78, "ПК (Робоче місце)", size=12, color=INK, bold=True)
    body += rect(40, 95, 150, 60, fill="#ffffff", stroke="#0284c7", sw=1.5, rx=4)
    body += text(115, 118, "Betaflight / ESC", size=11, color="#0284c7", bold=True)
    body += text(115, 136, "Configurator (GUI)", size=10, color=INK)

    body += text(115, 195, "Команди MSP:", size=10.5, color=MUTED, bold=True)
    body += text(115, 218, "MSP_SET_PASSTHROUGH", size=9.5, color=INK, bold=True)
    body += text(115, 240, "Read / Write EEPROM", size=9.5, color=MUTED)

    # Зв'язок USB
    body += line(205, 125, 275, 125, color="#0284c7", sw=2.5)
    body += text(240, 115, "USB CDC", size=10, color="#0284c7", bold=True)
    body += text(240, 142, "VCP (UART)", size=9.5, color=MUTED)

    # 2. FC
    body += rect(275, 50, 240, 250, fill="#f1f5f9", stroke=LINE, sw=1.5, rx=8)
    body += text(395, 75, "Польотний контролер (FC)", size=12, color=INK, bold=True)

    body += rect(295, 95, 200, 65, fill="#ffffff", stroke=LINE, sw=1.2, rx=4)
    body += text(395, 116, "Основний MCU (STM32/AT32)", size=10.5, color=INK, bold=True)
    body += text(395, 135, "Режим 4-Way Passthrough", size=10, color=FIELD, bold=True)
    body += text(395, 150, "(зупиняє PID-цикл, працює як міст)", size=9.5, color=MUTED)

    body += rect(295, 175, 200, 110, fill="#ffffff", stroke="#94a3b8", sw=1, rx=4)
    body += text(395, 195, "Таймерні канали (GPIO/DMA)", size=10, color=INK, bold=True)
    for idx, (pname, py_off) in enumerate([("M1 DShot PIN", 215), ("M2 DShot PIN", 233), ("M3 DShot PIN", 251), ("M4 DShot PIN", 269)]):
        body += text(310, py_off, pname, size=9.5, color=MUTED, anchor="start")
        body += circle(480, py_off - 3, 2.5, fill=LINE, stroke=LINE, sw=1)

    # 4 лінії DShot
    for idx, py_off in enumerate([105, 155, 205, 255]):
        body += line(480, 215 + idx * 18, 545, py_off, color=LINE, sw=1.5)
        body += arrow(545, py_off, 575, py_off, color=LINE, sw=1.5)

    # 3. Регулятор 4-in-1 ESC
    body += rect(575, 50, 260, 250, fill="#fefce8", stroke="#ca8a04", sw=1.5, rx=8)
    body += text(705, 75, "4-in-1 ESC (BLHeli_32 / AM32)", size=11.5, color="#854d0e", bold=True)

    for idx, (esc_name, py_off, d_state) in enumerate([
        ("ESC 1 MCU", 105, "Dir: Normal (0)"),
        ("ESC 2 MCU", 155, "Dir: Reversed (1)"),
        ("ESC 3 MCU", 205, "Dir: Reversed (1)"),
        ("ESC 4 MCU", 255, "Dir: Normal (0)"),
    ]):
        body += rect(590, py_off - 16, 230, 34, fill="#ffffff", stroke="#ca8a04", sw=1, rx=4)
        body += text(640, py_off + 3, esc_name, size=10, color=INK, bold=True)
        body += text(760, py_off + 3, d_state, size=9.5, color=FIELD if "Normal" in d_state else NEG, bold=True)

    body += text(430, 335, "Прошивка FC транслює команди GUI безпосередньо у флеш-реєстри напрямку кожного ESC.", size=10.5, color=INK, bold=True)

    render(os.path.join(OUT, "dshot-passthrough-architecture.svg"), W, H, body,
           title="Архітектура 4-Way Passthrough: зміна напрямку обертання ESC без паяльника")


# ════════════════════════════════════════════════════════════════════════════
# Запуск генерації
# ════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    fig_motor_order_standards()
    fig_positive_feedback_loop()
    fig_props_in_vs_props_out()
    fig_yaw_reaction_torque_balance()
    fig_dshot_passthrough_architecture()
    print("OK: All motor order and direction figures generated successfully.")
