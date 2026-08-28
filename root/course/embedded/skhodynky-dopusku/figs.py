# -*- coding: utf-8 -*-
"""Фігури для статті skhodynky-dopusku («Сходинки допуску»).
svgkit імпортуємо зі scripts/, не переписуємо (AUTHORING §5).

    python figs.py    # вивід у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. admission-ladder-overview: 4 сходинки допуску ─────────────────────────
def fig_admission_ladder_overview():
    W, H = 840, 430
    p = []

    step_w = 180
    gap = 20
    start_x = 35

    steps_data = [
        {
            "num": "1. Тіньовий режим",
            "en": "Shadow Mode",
            "who_ctrl": "Людина / Базовий",
            "algo_role": "Фоновий розрахунок",
            "actuators": "Ізольовано (0%)",
            "risk": "Нульовий",
            "h": 160,
            "y": 215,
            "color": "#3b82f6",
            "fill": "#eff6ff"
        },
        {
            "num": "2. Порадник",
            "en": "Advisory Mode",
            "who_ctrl": "Людина (ручно)",
            "algo_role": "Пропонує маневр",
            "actuators": "Через клік (0%)",
            "risk": "Мінімальний",
            "h": 210,
            "y": 165,
            "color": "#8b5cf6",
            "fill": "#f5f3ff"
        },
        {
            "num": "3. Під наглядом",
            "en": "Supervised",
            "who_ctrl": "Алгоритм (напряму)",
            "algo_role": "Повне керування",
            "actuators": "Прямий доступ (100%)",
            "risk": "Контрольований",
            "h": 260,
            "y": 115,
            "color": "#f59e0b",
            "fill": "#fffbeb"
        },
        {
            "num": "4. Вузький домен",
            "en": "Bounded ODD",
            "who_ctrl": "Автономія в межах",
            "algo_role": "Повна автономія",
            "actuators": "Автономно (100%)",
            "risk": "Обмежений ODD",
            "h": 310,
            "y": 65,
            "color": FIELD,
            "fill": "#ecfdf5"
        },
    ]

    for i, s in enumerate(steps_data):
        x = start_x + i * (step_w + gap)
        # card background
        p.append(rect(x, s["y"], step_w, s["h"], fill=s["fill"], stroke=s["color"], sw=2.0, rx=8))

        # header badge
        p.append(rect(x + 8, s["y"] + 8, step_w - 16, 26, fill=s["color"], stroke=s["color"], sw=1, rx=4))
        p.append(text(x + step_w / 2, s["y"] + 25, s["num"], size=12, color="#ffffff", bold=True))

        # english subtitle
        p.append(text(x + step_w / 2, s["y"] + 48, s["en"], size=11, color=MUTED, italic=True))

        # content separator
        cy = s["y"] + 70
        p.append(line(x + 12, cy - 8, x + step_w - 12, cy - 8, color=s["color"], sw=1.0, dash="3 2"))

        # Details
        labels = [
            ("Керує:", s["who_ctrl"]),
            ("Роль ШІ:", s["algo_role"]),
            ("Приводи:", s["actuators"]),
            ("Ризик:", s["risk"])
        ]
        for lbl, val in labels:
            if cy + 24 > s["y"] + s["h"]:
                break
            p.append(text(x + 14, cy + 6, lbl, size=11, color=INK, bold=True, anchor="start"))
            p.append(text(x + 14, cy + 22, val, size=11, color=s["color"], anchor="start"))
            cy += 36

        # Arrow to next step
        if i < 3:
            ax1 = x + step_w + 2
            ax2 = ax1 + gap - 4
            ay = s["y"] + s["h"] / 2
            p.append(arrow(ax1, ay, ax2, ay - 25, color=MUTED, sw=1.6))
            p.append(text((ax1 + ax2) / 2, ay - 32, "допуск", size=10, color=MUTED, italic=True))

    # Bottom timeline / safety base
    p.append(rect(start_x, 390, W - 2 * start_x, 26, fill=FILL, stroke=LINE, sw=1.2, rx=4))
    p.append(text(W / 2, 407, "Зростання прав доступу до приводів ── Накопичення доказів безпеки та надійності", size=11, color=INK, bold=True))

    render(os.path.join(OUT, "admission-ladder-overview.svg"), W, H, *p)


# ── 2. shadow-divergence-pipeline: Тіньовий режим та аналізатор розбіжностей ─
def fig_shadow_divergence_pipeline():
    W, H = 840, 370
    p = []

    # Sensors block (Left)
    p.append(rect(25, 75, 170, 205, fill=FILL, stroke=LINE, sw=1.6, rx=6))
    p.append(text(110, 100, "Сенсорний потік", size=13, color=INK, bold=True))
    p.append(line(40, 112, 180, 112, color=LINE, sw=1.0))
    p.append(text(110, 137, "IMU / Гіроскопи", size=11, color=INK))
    p.append(text(110, 162, "GNSS / Одометрія", size=11, color=INK))
    p.append(text(110, 187, "Оптичний потік", size=11, color=INK))
    p.append(text(110, 212, "Далекоміри / LiDAR", size=11, color=INK))
    p.append(text(110, 245, "Частота: 50–400 Гц", size=10, color=MUTED, italic=True))

    # Split arrows
    p.append(arrow(195, 130, 265, 90, color=LINE, sw=1.6))
    p.append(text(230, 98, "потік", size=10, color=MUTED))

    p.append(arrow(195, 220, 265, 250, color=LINE, sw=1.6))
    p.append(text(230, 248, "копія", size=10, color=MUTED))

    # Top Branch: Human / Active Flight Controller
    p.append(rect(265, 50, 220, 80, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=6))
    p.append(text(375, 75, "Штатний пілот / FC", size=12, color=NEG, bold=True))
    p.append(text(375, 95, "Ручний / базовий автопілот", size=11, color=INK))
    p.append(text(375, 115, "Уставка: U_real(t)", size=11, color=NEG, bold=True))

    # Bottom Branch: Shadow Autonomous Algorithm
    p.append(rect(265, 210, 220, 85, fill="#eff6ff", stroke="#3b82f6", sw=1.8, rx=6))
    p.append(text(375, 235, "Тіньовий алгоритм", size=12, color="#3b82f6", bold=True))
    p.append(text(375, 255, "Нейромережа / новий планер", size=11, color=INK))
    p.append(text(375, 278, "Уставка: U_shadow(t)", size=11, color="#3b82f6", bold=True))

    # MUX / Actuators (Top Right)
    p.append(arrow(485, 90, 560, 90, color=NEG, sw=2.0))
    p.append(rect(560, 55, 245, 70, fill="#ecfdf5", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(682, 80, "Сервоприводи / ESC", size=13, color=FIELD, bold=True))
    p.append(text(682, 105, "Фізичний рух апарата (100% реальний)", size=11, color=INK))

    # Divergence Comparator & Logger (Bottom Right)
    p.append(arrow(485, 252, 560, 252, color="#3b82f6", sw=1.6))
    # Feedback from real pilot to comparator
    p.append(line(520, 90, 520, 215, color=NEG, sw=1.4, dash="4 3"))
    p.append(arrow(520, 215, 560, 215, color=NEG, sw=1.4))

    p.append(rect(560, 185, 245, 125, fill="#fef2f2", stroke=POS, sw=1.8, rx=6))
    p.append(text(682, 210, "Аналізатор розбіжності", size=12, color=POS, bold=True))
    p.append(text(682, 233, "ΔU = |U_real − U_shadow|", size=11, color=INK, bold=True))
    p.append(text(682, 256, "Оцінка шуму та перевантажень", size=11, color=INK))
    p.append(text(682, 281, "Запис у Blackbox / Flash", size=11, color=POS, italic=True))

    # Isolation barrier
    p.append(line(495, 150, 545, 150, color=POS, sw=2.0, dash="6 3"))
    p.append(text(520, 168, "ІЗОЛЯЦІЯ ВІД ПРИВОДІВ", size=9, color=POS, bold=True))

    render(os.path.join(OUT, "shadow-divergence-pipeline.svg"), W, H, *p)


# ── 3. bumpless-takeover-timeline: Перехоплення та плавний перехід уставок ─
def fig_bumpless_takeover_timeline():
    W, H = 840, 400
    p = []

    ox, oy = 70, 210
    aw = 700

    # Horizontal time axis
    p.append(arrow(ox, oy, ox + aw, oy, color=LINE, sw=1.6))
    p.append(text(ox + aw - 10, oy + 28, "Час t", size=12, color=INK, italic=True))

    # Events on timeline
    t_event = ox + 220     # 290
    t_blend_end = ox + 380 # 450

    # Zone 1: Autonomous Supervised
    p.append(rect(ox, 35, 220, 125, fill="#fffbeb", stroke="#f59e0b", sw=1.2, rx=4))
    p.append(text(ox + 110, 60, "Під наглядом (Supervised)", size=12, color="#f59e0b", bold=True))
    p.append(text(ox + 110, 83, "Алгоритм веде траєкторію", size=11, color=INK))
    p.append(text(ox + 110, 105, "Людина тримає перемикач", size=11, color=MUTED))

    # Zone 2: Takeover & Blending
    p.append(rect(t_event, 35, 160, 125, fill="#fef2f2", stroke=POS, sw=1.5, rx=4))
    p.append(text(t_event + 80, 60, "Вікно змішування", size=12, color=POS, bold=True))
    p.append(text(t_event + 80, 83, "T_blend = 200 мс", size=11, color=POS, bold=True))
    p.append(text(t_event + 80, 105, "Плавний кросфейд", size=11, color=INK))

    # Zone 3: Manual Control
    p.append(rect(t_blend_end, 35, ox + aw - t_blend_end, 125, fill="#eff6ff", stroke=NEG, sw=1.2, rx=4))
    p.append(text((t_blend_end + ox + aw) / 2, 60, "Ручне перехоплення (Manual Override)", size=12, color=NEG, bold=True))
    p.append(text((t_blend_end + ox + aw) / 2, 83, "Людина повністю контролює борт", size=11, color=INK))
    p.append(text((t_blend_end + ox + aw) / 2, 105, "Інтегратори скинуто / узгоджено", size=11, color=MUTED))

    # Vertical markers
    p.append(line(t_event, 30, t_event, 345, color=POS, sw=1.5, dash="4 3"))
    p.append(text(t_event, 365, "Тригер перехоплення (Stick / Switch)", size=11, color=POS, bold=True))

    p.append(line(t_blend_end, 30, t_blend_end, 345, color=NEG, sw=1.2, dash="4 3"))
    p.append(text(t_blend_end, 365, "Завершення переходу", size=11, color=NEG))

    # Bad jump (Step discontinuity) - red dashed
    p.append(line(ox + 20, oy - 45, t_event, oy - 45, color="#f59e0b", sw=2.2))
    p.append(line(t_event, oy - 45, t_event, oy + 75, color=POS, sw=2.0, dash="3 3"))
    p.append(line(t_event, oy + 75, ox + aw - 20, oy + 75, color=POS, sw=1.5, dash="3 3"))
    p.append(text(t_event + 80, oy + 98, "Ступінчастий удар (небезпечно)", size=10, color=POS, italic=True))

    # Good bumpless curve (Smooth s-curve / linear blend) - green solid
    p.append(line(t_event, oy - 45, t_blend_end, oy + 75, color=FIELD, sw=2.8))
    p.append(line(t_blend_end, oy + 75, ox + aw - 20, oy + 75, color=NEG, sw=2.2))

    # Labels on curves (positioned away from intersections)
    p.append(text(ox + 90, oy - 58, "Уставка алгоритму U_auto", size=11, color="#f59e0b", bold=True))
    p.append(text(ox + aw - 110, oy + 60, "Уставка пілота U_pilot", size=11, color=NEG, bold=True))

    # Clean badge for Bumpless label
    b, bw, bh = textbox(t_event + 80, oy - 20, "Плавний перехід (Bumpless)", size=10, color=FIELD, bold=True, fill="#ecfdf5", stroke=FIELD, sw=1.2)
    p.append(b)

    render(os.path.join(OUT, "bumpless-takeover-timeline.svg"), W, H, *p)


# ── 4. bounded-odd-envelopes: Вузький домен автономії та бар'єри безпеки ────
def fig_bounded_odd_envelopes():
    W, H = 840, 390
    p = []

    # Outer Container: Physical Environment
    p.append(rect(25, 25, 790, 340, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(175, 50, "Зовнішній світ: фізичне середовище польоту", size=13, color=MUTED, bold=True))

    # Layer 1: Geofence (Spatial Bounds)
    p.append(rect(50, 70, 460, 275, fill="#f0fdf4", stroke=FIELD, sw=2.0, rx=8))
    p.append(text(180, 95, "1. Просторовий домен (3D Geofence)", size=12, color=FIELD, bold=True))
    p.append(text(180, 115, "Радіус: ≤ 1200 м, Висота: 20–120 м AGL", size=11, color=INK))

    # Layer 2: Environmental Bounds inside Geofence
    p.append(rect(70, 135, 420, 195, fill="#eff6ff", stroke="#3b82f6", sw=1.6, rx=6))
    p.append(text(200, 160, "2. Сенсорні та погодні межі (ODD)", size=12, color="#3b82f6", bold=True))
    p.append(text(200, 180, "Вітер: ≤ 10 м/с, Освітленість: ≥ 150 люкс", size=11, color=INK))
    p.append(text(200, 200, "Похибка EKF: інновації давачів < 2.0σ", size=11, color=INK))

    # Layer 3: Fully Autonomous Core
    p.append(rect(90, 220, 380, 95, fill="#ecfdf5", stroke=FIELD, sw=2.2, rx=6))
    p.append(text(280, 250, "3. ЗОНА ПОВНОЇ АВТОНОМІЇ (Bounded)", size=12, color=FIELD, bold=True))
    p.append(text(280, 275, "Самостійне прийняття рішень та політ без втручання", size=11, color=INK))

    # Right Column: Safety Fallbacks (Fail-safe Arbiter)
    p.append(rect(535, 70, 260, 275, fill="#fff1f2", stroke=POS, sw=1.8, rx=8))
    p.append(text(665, 95, "Захисний арбітр (Safety Arbiter)", size=12, color=POS, bold=True))
    p.append(line(550, 108, 780, 108, color=POS, sw=1.0))

    fallbacks = [
        ("Вихід за геозону", "Повернення на базу (RTH)"),
        ("Пориви вітру > 12 м/с", "Зниження / Зависання"),
        ("Обрив зв'язку > 3 с", "Детермінована програма"),
        ("Деградація сенсорів", "Аварійна посадка (Land)")
    ]

    fy = 135
    for trigger, action in fallbacks:
        p.append(text(550, fy, trigger + ":", size=11, color=POS, bold=True, anchor="start"))
        p.append(text(550, fy + 18, "↳ " + action, size=11, color=INK, anchor="start"))
        fy += 45

    # Connectors from zones to fallbacks
    p.append(arrow(490, 175, 535, 175, color=POS, sw=1.6))
    p.append(text(512, 165, "порушення", size=9, color=POS))

    p.append(arrow(470, 265, 535, 265, color=POS, sw=1.6))
    p.append(text(502, 255, "відмова", size=9, color=POS))

    render(os.path.join(OUT, "bounded-odd-envelopes.svg"), W, H, *p)


if __name__ == "__main__":
    fig_admission_ladder_overview()
    fig_shadow_divergence_pipeline()
    fig_bumpless_takeover_timeline()
    fig_bounded_odd_envelopes()
    print("Generated all 4 figures successfully.")
