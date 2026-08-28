# -*- coding: utf-8 -*-
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_quad_failure_dynamics():
    W, H = 940, 440
    p = []

    # Три панелі: Нормальний політ, Момент відмови, Пастка класичного PID
    w_card = 286
    gap = 20
    h_card = 390
    y_card = 25

    panels = [
        ("1. Штатний політ (4 мотори)", "#f8fafc", "#cbd5e1"),
        ("2. Фізика відмови мотора M4", "#fef2f2", "#fca5a5"),
        ("3. Наслідок: пастка PID-регулятора", "#fff7ed", "#fdba74")
    ]

    for i, (title, fcolor, scolor) in enumerate(panels):
        x = 20 + i * (w_card + gap)
        p.append(rect(x, y_card, w_card, h_card, fill=fcolor, stroke=scolor, sw=1.5, rx=8))
        p.append(text(x + w_card / 2, y_card + 28, title, size=13, color=INK, bold=True))

    # --- Панель 1: Штатний політ ---
    cx1, cy1 = 20 + w_card / 2, y_card + 130
    arm = 52
    # Промені рами
    p.append(line(cx1 - arm, cy1 - arm, cx1 + arm, cy1 + arm, color=LINE, sw=3))
    p.append(line(cx1 - arm, cy1 + arm, cx1 + arm, cy1 - arm, color=LINE, sw=3))
    p.append(circle(cx1, cy1, 16, fill="#e2e8f0", stroke=LINE, sw=1.5))
    p.append(text(cx1, cy1 + 4, "FC", size=10, color=INK, bold=True))

    # 4 мотори
    coords1 = [
        (cx1 + arm, cy1 - arm, "M1", "CCW", NEG),
        (cx1 - arm, cy1 - arm, "M2", "CW", POS),
        (cx1 - arm, cy1 + arm, "M3", "CCW", NEG),
        (cx1 + arm, cy1 + arm, "M4", "CW", POS),
    ]
    for mx, my, name, rot, color in coords1:
        p.append(circle(mx, my, 18, fill="#ffffff", stroke=color, sw=2))
        p.append(text(mx, my + 4, name, size=10, color=color, bold=True))
        p.append(text(mx, my + 27, rot, size=9.5, color=MUTED))

    # Текстовий блок під схемою
    t1_lines = [
        "• 4 незалежні актуатори",
        "• Рівновага тяги: ∑F_z = m·g",
        "• Моменти: τ_roll=0, τ_pitch=0",
        "• Реактивний момент:",
        "  2 CW + 2 CCW → τ_yaw = 0"
    ]
    ty1 = y_card + 255
    for idx, ln in enumerate(t1_lines):
        p.append(text(20 + 20, ty1 + idx * 22, ln, size=11, color=INK, anchor="start"))

    # --- Панель 2: Відмова M4 ---
    cx2, cy2 = 20 + w_card + gap + w_card / 2, y_card + 130
    p.append(line(cx2 - arm, cy2 - arm, cx2 + arm, cy2 + arm, color=LINE, sw=3))
    p.append(line(cx2 - arm, cy2 + arm, cx2 + arm, cy2 - arm, color=LINE, sw=3))
    p.append(circle(cx2, cy2, 16, fill="#e2e8f0", stroke=LINE, sw=1.5))
    p.append(text(cx2, cy2 + 4, "FC", size=10, color=INK, bold=True))

    # M1, M2, M3 активні, M4 мертвий
    coords2 = [
        (cx2 + arm, cy2 - arm, "M1", "CCW", NEG, True),
        (cx2 - arm, cy2 - arm, "M2", "CW", POS, True),
        (cx2 - arm, cy2 + arm, "M3", "CCW", NEG, True),
        (cx2 + arm, cy2 + arm, "M4", "0 RPM", "#94a3b8", False),
    ]
    for mx, my, name, rot, color, active in coords2:
        if active:
            p.append(circle(mx, my, 18, fill="#ffffff", stroke=color, sw=2))
            p.append(text(mx, my + 4, name, size=10, color=color, bold=True))
        else:
            p.append(circle(mx, my, 18, fill="#fee2e2", stroke=POS, sw=2))
            p.append(line(mx - 10, my - 10, mx + 10, my + 10, color=POS, sw=2.5))
            p.append(line(mx - 10, my + 10, mx + 10, my - 10, color=POS, sw=2.5))
        p.append(text(mx, my + 27, rot, size=9.5, color=MUTED))

    # Зміщений центр тяги
    c_thrust_x, c_thrust_y = cx2 - arm / 3, cy2 - arm / 3
    p.append(circle(c_thrust_x, c_thrust_y, 5, fill=FIELD, stroke="#15803d", sw=1.5))
    p.append(arrow(cx2, cy2, c_thrust_x - 12, c_thrust_y - 12, color=POS, sw=2))
    p.append(text(c_thrust_x - 15, c_thrust_y - 5, "Зсув тяги", size=9.5, color=POS, bold=True, anchor="end"))

    t2_lines = [
        "• Втрата 25% сумарної тяги",
        "• Центр підйому зсунуто до M2",
        "• Виникає перекидний момент",
        "• Дисбаланс обертання:",
        "  2 CCW проти 1 CW → розгін yaw"
    ]
    ty2 = y_card + 255
    for idx, ln in enumerate(t2_lines):
        p.append(text(20 + w_card + gap + 20, ty2 + idx * 22, ln, size=11, color=INK, anchor="start"))

    # --- Панель 3: Пастка PID ---
    cx3, cy3 = 20 + 2 * (w_card + gap) + w_card / 2, y_card + 130
    p.append(line(cx3 - arm, cy3 - arm, cx3 + arm, cy3 + arm, color=LINE, sw=3))
    p.append(line(cx3 - arm, cy3 + arm, cx3 + arm, cy3 - arm, color=LINE, sw=3))

    # M2 і M3 розганяються до 100%, M1 до мінімуму, M4 мовчить
    p.append(circle(cx3 - arm, cy3 - arm, 22, fill="#fee2e2", stroke=POS, sw=3))
    p.append(text(cx3 - arm, cy3 - arm + 4, "100%", size=9.5, color=POS, bold=True))
    p.append(circle(cx3 - arm, cy3 + arm, 22, fill="#fee2e2", stroke=POS, sw=3))
    p.append(text(cx3 - arm, cy3 + arm + 4, "100%", size=9.5, color=POS, bold=True))
    p.append(circle(cx3 + arm, cy3 - arm, 14, fill="#f1f5f9", stroke=MUTED, sw=1.5))
    p.append(text(cx3 + arm, cy3 - arm + 4, "min", size=9, color=MUTED))
    p.append(circle(cx3 + arm, cy3 + arm, 18, fill="#fee2e2", stroke=POS, sw=2))
    p.append(line(cx3 + arm - 10, cy3 + arm - 10, cx3 + arm + 10, cy3 + arm + 10, color=POS, sw=2))
    p.append(line(cx3 + arm - 10, cy3 + arm + 10, cx3 + arm + 10, cy3 + arm - 10, color=POS, sw=2))

    t3_lines = [
        "1. Помилка кута росте в бік M4",
        "2. Інтегратор I-term насичується",
        "3. PID намагається витягнути крен,",
        "   витискаючи M2 і M3 на 100%",
        "4. Наслідок: некероване перекидання",
        "   (катастрофічний death-roll за 0.1 с)"
    ]
    ty3 = y_card + 235
    for idx, ln in enumerate(t3_lines):
        col = POS if idx >= 4 else INK
        p.append(text(20 + 2 * (w_card + gap) + 15, ty3 + idx * 22, ln, size=11, color=col, bold=(idx >= 4), anchor="start"))

    render(os.path.join(OUT, "quad-failure-dynamics.svg"), W, H, *p)


def fig_spin_recovery_mechanism():
    W, H = 940, 420
    p = []

    # Дві великі панелі: (1) Усереднення моменту через швидке обертання, (2) Фазова модуляція тяги
    w1 = 440
    gap = 20
    h_card = 370
    y_card = 25

    # Панель 1: Гіроскопічне усереднення
    p.append(rect(20, y_card, w1, h_card, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(20 + w1 / 2, y_card + 28, "1. Гіроскопічне усереднення (Spinning Control)", size=13, color=INK, bold=True))

    cx1, cy1 = 20 + w1 / 2, y_card + 140
    # Коло траєкторії обертання
    p.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s" stroke-width="%.1f" stroke-dasharray="4,4"/>' %
             (cx1, cy1, 70, "#f1f5f9", "#94a3b8", 1.5))

    # Стрілка обертання курсу ω_z
    p.append('<path d="M %d %d A 85 85 0 0 1 %d %d" fill="none" stroke="%s" stroke-width="2.5" marker-end="url(#arrow)"/>' %
             (cx1 - 60, cy1 - 60, cx1 + 60, cy1 - 60, POS))
    p.append(text(cx1, cy1 - 70, "ω_z = 20...30 рад/с (неконтрольований yaw)", size=10, color=POS, bold=True))

    # Тіло дрона під кутом
    p.append(circle(cx1, cy1, 14, fill="#e2e8f0", stroke=LINE, sw=1.5))
    p.append(text(cx1, cy1 + 4, "Z_b", size=9, color=INK, bold=True))

    # Стрілки тяги 3 моторів, що обертаються
    for ang, lbl in [(0, "M1"), (120, "M2"), (240, "M3")]:
        rad = math.radians(ang)
        mx = cx1 + 55 * math.cos(rad)
        my = cy1 + 55 * math.sin(rad)
        p.append(circle(mx, my, 12, fill="#ffffff", stroke=NEG, sw=1.5))
        p.append(text(mx, my + 3, lbl, size=9.5, color=NEG, bold=True))

    # Текстовий блок
    lines1 = [
        "• Жертвування віссю курсу (τ_yaw ≠ 0)",
        "• Неперервне обертання рами навколо осі Z_body",
        "• Бічні перекидні моменти інтегруються за період",
        "  обертання T_spin = 2π/ω_z та дають нуль у просторі:",
        "  ∫ τ_xy(t) dt = 0  →  кути Roll/Pitch стабільні!",
        "• Середній вектор тяги спрямований вздовж осі Z_world"
    ]
    for idx, ln in enumerate(lines1):
        col = FIELD if "∫" in ln else INK
        p.append(text(20 + 20, y_card + 235 + idx * 21, ln, size=11, color=col, bold=("∫" in ln), anchor="start"))

    # Панель 2: Фазова модуляція тяги для керування вектором
    x2 = 20 + w1 + gap
    p.append(rect(x2, y_card, w1, h_card, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(x2 + w1 / 2, y_card + 28, "2. Фазова модуляція тяги (Cyclic Thrust)", size=13, color=INK, bold=True))

    # Графік синусоїди тяги від кута повороту
    gx0, gy0 = x2 + 50, y_card + 140
    gw, gh = 340, 70

    # Осі
    p.append(line(gx0, gy0 + gh / 2, gx0 + gw, gy0 + gh / 2, color="#94a3b8", sw=1.2))
    p.append(line(gx0, gy0 - 10, gx0, gy0 + gh + 10, color="#94a3b8", sw=1.2))
    p.append(text(gx0 + gw - 10, gy0 + gh / 2 + 16, "Кут курсу ψ(t)", size=9, color=MUTED, anchor="end"))
    p.append(text(gx0 + 5, gy0 - 15, "Тяга мотора f_i(t)", size=9, color=MUTED, anchor="start"))

    # Синусоїда
    sin_pts = []
    for step in range(gw):
        ang = step / gw * 2 * math.pi * 2
        sy = (gy0 + gh / 2) - 26 * math.sin(ang - 0.8)
        sin_pts.append("%.1f,%.1f" % (gx0 + step, sy))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(sin_pts), NEG))

    # Позначення постійної складової та імпульсу
    p.append(line(gx0, gy0 + gh / 2, gx0 + gw, gy0 + gh / 2, color=LINE, sw=1, dash="3,3"))
    p.append(text(gx0 + gw + 8, gy0 + gh / 2 + 3, "f_0 (тяга висоти)", size=9, color=INK, anchor="start"))

    p.append(arrow(gx0 + 95, gy0 + gh / 2, gx0 + 95, gy0 + 9, color=POS, sw=1.5))
    p.append(text(gx0 + 102, gy0 + 18, "+Δf (імпульс нахилу)", size=9, color=POS, bold=True, anchor="start"))

    lines2 = [
        "• Модель автомата перекосу (Cyclic Pitch/Thrust):",
        "  f_i(t) = f_0 + Δf · cos(ψ(t) − φ_target)",
        "• f_0 утримує висоту та задає швидкість спуску",
        "• Δf синхронізовано з фазою кута орієнтації ψ(t)",
        "• Створює постійний бічний нахил у системі NED",
        "• Забезпечує керований дрейф у безпечну зону посадки"
    ]
    for idx, ln in enumerate(lines2):
        col = POS if "f_i(t)" in ln else INK
        p.append(text(x2 + 20, y_card + 235 + idx * 21, ln, size=11, color=col, bold=("f_i(t)" in ln), anchor="start"))

    render(os.path.join(OUT, "spin-recovery-mechanism.svg"), W, H, *p)


def fig_hex_octo_reweighting():
    W, H = 940, 420
    p = []

    w_card = 440
    gap = 20
    h_card = 370
    y_card = 25

    # Панель 1: Гексакоптер
    p.append(rect(20, y_card, w_card, h_card, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(20 + w_card / 2, y_card + 28, "Гексакоптер (6 моторів → втрата 1)", size=13, color=INK, bold=True))

    cx1, cy1 = 20 + w_card / 2, y_card + 125
    r_hex = 60

    # 6 моторів гексакоптера
    hex_motors = [
        (0, "M1", "CW", POS, 0.65),
        (60, "M2", "CCW", NEG, 0.45),
        (120, "M3", "CW", POS, 0.95),
        (180, "M4", "CCW", NEG, 0.45),
        (240, "M5", "CW", POS, 0.95),
        (300, "M6", "FAIL", "#94a3b8", 0.0),
    ]

    for ang, name, rot, col, scale in hex_motors:
        rad = math.radians(ang - 90)
        mx = cx1 + r_hex * math.cos(rad)
        my = cy1 + r_hex * math.sin(rad)
        p.append(line(cx1, cy1, mx, my, color=LINE, sw=2))
        if scale > 0.0:
            p.append(circle(mx, my, 14, fill="#ffffff", stroke=col, sw=2))
            p.append(text(mx, my + 4, name, size=9, color=col, bold=True))
            p.append(text(mx + (18 if math.cos(rad) >= 0 else -18), my + 4,
                          "%.0f%%" % (scale * 100), size=9, color=col, bold=True,
                          anchor="start" if math.cos(rad) >= 0 else "end"))
        else:
            p.append(circle(mx, my, 14, fill="#fee2e2", stroke=POS, sw=2))
            p.append(line(mx - 7, my - 7, mx + 7, my + 7, color=POS, sw=2))
            p.append(line(mx - 7, my + 7, mx + 7, my - 7, color=POS, sw=2))

    p.append(circle(cx1, cy1, 12, fill="#e2e8f0", stroke=LINE, sw=1.5))

    lines1 = [
        "• Ранг матриці B_red = 4 (повні 6 DOF зберігаються)",
        "• Дисбаланс реактивного моменту: 3 CW проти 2 CCW",
        "• Для утримання курсу (τ_yaw = 0) контролер душить",
        "  протилежну групу моторів CCW (до ~45% тяги)",
        "• Штраф на сумарну тягу: втрата ~35-40% ліфту!",
        "• Запас TWR > 1.6 утримує висоту; інакше — спуск"
    ]
    for idx, ln in enumerate(lines1):
        col = POS if "Штраф" in ln else INK
        p.append(text(20 + 20, y_card + 225 + idx * 21, ln, size=11, color=col, bold=("Штраф" in ln), anchor="start"))

    # Панель 2: Октокоптер
    x2 = 20 + w_card + gap
    p.append(rect(x2, y_card, w_card, h_card, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(x2 + w_card / 2, y_card + 28, "Октокоптер (8 моторів → втрата 1 або 2)", size=13, color=INK, bold=True))

    cx2, cy2 = x2 + w_card / 2, y_card + 125
    r_octo = 60

    octo_motors = [
        (0, "M1", POS, 0.85), (45, "M2", NEG, 0.80), (90, "M3", POS, 0.85), (135, "M4", NEG, 0.80),
        (180, "M5", POS, 0.85), (225, "M6", NEG, 0.80), (270, "M7", POS, 0.85), (315, "M8", "#94a3b8", 0.0)
    ]
    for ang, name, col, scale in octo_motors:
        rad = math.radians(ang - 90)
        mx = cx2 + r_octo * math.cos(rad)
        my = cy2 + r_octo * math.sin(rad)
        p.append(line(cx2, cy2, mx, my, color=LINE, sw=1.5))
        if scale > 0.0:
            p.append(circle(mx, my, 12, fill="#ffffff", stroke=col, sw=1.8))
            p.append(text(mx, my + 3, name, size=9.5, color=col, bold=True))
        else:
            p.append(circle(mx, my, 12, fill="#fee2e2", stroke=POS, sw=2))
            p.append(line(mx - 6, my - 6, mx + 6, my + 6, color=POS, sw=1.8))
            p.append(line(mx - 6, my + 6, mx + 6, my - 6, color=POS, sw=1.8))

    p.append(circle(cx2, cy2, 12, fill="#e2e8f0", stroke=LINE, sw=1.5))

    lines2 = [
        "• Ранг матриці B_red = 4, надлишковість 7 із 8",
        "• Втрата тяги лише 12.5% від номінальної",
        "• Дисбаланс моменту легко компенсується (4 CW / 3 CCW)",
        "• Мінімальне зниження стелі загальної тяги (<15%)",
        "• Здатний пережити втрату 2 моторів (не суміжних)",
        "• Повноцінне продовження місії або стабільне RTH"
    ]
    for idx, ln in enumerate(lines2):
        col = FIELD if "Повноцінне" in ln else INK
        p.append(text(x2 + 20, y_card + 225 + idx * 21, ln, size=11, color=col, bold=("Повноцінне" in ln), anchor="start"))

    render(os.path.join(OUT, "hex-octo-reweighting.svg"), W, H, *p)


def fig_fdi_decision_tree():
    W, H = 940, 460
    p = []

    p.append(rect(20, 20, 900, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(470, 48, "Багаторівневий конвеєр виявлення та ізоляції відмови мотора (FDI)", size=14, color=INK, bold=True))

    # Рівень 1: Вхідні давачі та джерела телеметрії
    y_s = 75
    sensors = [
        ("DShot Bidirectional", "eRPM мотора (1 кГц)"),
        ("Телеметрія ESC", "Струм фази I_phase, T_esc"),
        ("Інерційний давач IMU", "Кутові прискорення dω/dt"),
        ("PID-регулятор", "Насичення інтегратора I-term")
    ]
    for i, (head, sub) in enumerate(sensors):
        x = 40 + i * 215
        p.append(rect(x, y_s, 200, 50, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
        p.append(text(x + 100, y_s + 20, head, size=11, color=INK, bold=True))
        p.append(text(x + 100, y_s + 38, sub, size=9, color=MUTED))
        p.append(arrow(x + 100, y_s + 50, x + 100, y_s + 78, color=LINE, sw=1.5))

    # Рівень 2: Модулі детекції (FDI детектори)
    y_d = 160
    detectors = [
        ("1. Нульові eRPM при команді", "cmd > 15% & RPM < 100", POS),
        ("2. Відрив пропелера", "RPM високі & струм ~0A", POS),
        ("3. Спостерігач розбіжності", "J·dω/dt << B·u_cmd", NEG),
        ("4. Насичення I-term", "|I_axis| == I_max > 80 мс", NEG)
    ]
    for i, (head, cond, col) in enumerate(detectors):
        x = 40 + i * 215
        p.append(rect(x, y_d, 200, 60, fill="#ffffff", stroke=col, sw=1.5, rx=6))
        p.append(text(x + 100, y_d + 22, head, size=10, color=col, bold=True))
        p.append(text(x + 100, y_d + 45, cond, size=9, color=INK))
        p.append(arrow(x + 100, y_d + 60, 470, y_d + 95, color=col, sw=1.2))

    # Рівень 3: Фільтр хибних спрацьовувань та арбітраж
    y_arb = 265
    p.append(rect(230, y_arb, 480, 50, fill="#ffffff", stroke="#3b82f6", sw=1.8, rx=6))
    p.append(text(470, y_arb + 20, "Арбітраж та захист від хибних спрацьовувань (Debounce)", size=11, color="#1d4ed8", bold=True))
    p.append(text(470, y_arb + 38, "Підтвердження тривалості 50...100 мс + перевірка загальної напруги батареї", size=9, color=MUTED))

    p.append(arrow(350, y_arb + 50, 240, y_arb + 80, color=POS, sw=2))
    p.append(arrow(590, y_arb + 50, 700, y_arb + 80, color=FIELD, sw=2))

    # Рівень 4: Дії за типом рами
    y_act = 350
    # Квадрокоптер
    p.append(rect(40, y_act, 400, 75, fill="#fff1f2", stroke="#f43f5e", sw=1.5, rx=6))
    p.append(text(240, y_act + 20, "Квадрокоптер (Quad): Аварійний режим", size=11, color="#be123c", bold=True))
    p.append(text(240, y_act + 40, "• Відключення I-term по осі Yaw (скидання курсу)", size=9, color=INK))
    p.append(text(240, y_act + 58, "• Запуск Single-Axis Spinning Recovery + керований спуск", size=9, color=INK))

    # Гекса / Октокоптер
    p.append(rect(500, y_act, 400, 75, fill="#f0fdf4", stroke="#22c55e", sw=1.5, rx=6))
    p.append(text(700, y_act + 20, "Гекса / Октокоптер: Перерахунок мікшера", size=11, color="#15803d", bold=True))
    p.append(text(700, y_act + 40, "• Moore-Penrose Pseudoinverse з нульовою вагою мотора", size=9, color=INK))
    p.append(text(700, y_act + 58, "• Стабілізація 6-DOF або безпечне RTH / керована посадка", size=9, color=INK))

    render(os.path.join(OUT, "fdi-decision-tree.svg"), W, H, *p)


if __name__ == "__main__":
    fig_quad_failure_dynamics()
    fig_spin_recovery_mechanism()
    fig_hex_octo_reweighting()
    fig_fdi_decision_tree()
    print("All figures generated successfully.")
