# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми «Відкат на правило, коли модель мовчить або марить»."""

import os
import sys

# Підключення svgkit із scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    FONT, BG, INK, LINE, MUTED, POS, NEG, FIELD, FILL,
    rect, line, arrow, text, mtext, circle, textbox, fitbox, render
)

def build_supervisor_architecture(path):
    w, h = 900, 480
    frags = []

    # 1. Сенсорний блок ліворуч
    frags.append(rect(15, 45, 175, 410, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    frags.append(text(102, 75, "Сенсорний шар", size=14, bold=True, color=INK))
    
    t_cam, _, _ = textbox(102, 130, "Відеопотік / Камера\n(RAW / RGB фрейми)", size=11, pad=6, fill=FILL, min_w=155)
    t_imu, _, _ = textbox(102, 235, "Інерційні давачі\n(IMU / Гіроскопи)", size=11, pad=6, fill=FILL, min_w=155)
    t_nav, _, _ = textbox(102, 345, "Навігація / Одометрія\n(GNSS / Лідар / EKF)", size=11, pad=6, fill=FILL, min_w=155)
    frags.extend([t_cam, t_imu, t_nav])

    # 2. Обчислювальний рівень нейромережі (AI / NPU)
    frags.append(rect(215, 45, 245, 185, fill="#fdf2e9", stroke="#d35400", sw=1.5, rx=8))
    frags.append(text(337, 75, "ML-Контур (NPU / GPU)", size=14, bold=True, color="#a04000"))
    t_ml_inf, _, _ = textbox(337, 120, "Нейромережевий інференс\n(Детекція / Планування)", size=11, pad=6, fill="#ffffff", min_w=220)
    t_ml_prop, _, _ = textbox(337, 185, "Пропозиція керування u_ml\n(Негарантована затримка)", size=11, pad=5, fill="#fff5ec", color="#a04000", min_w=220)
    frags.extend([t_ml_inf, t_ml_prop])

    # 3. Детермінований резервний контур (Rule Fallback)
    frags.append(rect(215, 255, 245, 200, fill="#eaf2f8", stroke="#2980b9", sw=1.5, rx=8))
    frags.append(text(337, 285, "Резервний контур (MCU)", size=14, bold=True, color="#1b4f72"))
    t_fb_alg, _, _ = textbox(337, 335, "Детерміновані правила\n(Утримання курсу / EKF)", size=11, pad=6, fill="#ffffff", min_w=220)
    t_fb_prop, _, _ = textbox(337, 405, "Резервна команда u_rule\n(Жорсткий детермінізм)", size=11, pad=5, fill="#ebf5fb", color="#1b4f72", min_w=220)
    frags.extend([t_fb_alg, t_fb_prop])

    # 4. Монітор здоров'я моделі (Health & OOD Monitor)
    frags.append(rect(485, 45, 190, 185, fill="#fbfcfc", stroke=MUTED, sw=1.2, rx=8))
    frags.append(text(580, 75, "Монітор аномалій", size=13, bold=True, color=INK))
    t_m1, _, _ = textbox(580, 105, "• Deadline Watchdog", size=11, pad=4, fill="#ffffff", min_w=165)
    t_m2, _, _ = textbox(580, 135, "• OOD & Енергія кадру", size=11, pad=4, fill="#ffffff", min_w=165)
    t_m3, _, _ = textbox(580, 165, "• Ентропія / Впевненість", size=11, pad=4, fill="#ffffff", min_w=165)
    t_m4, _, _ = textbox(580, 195, "• Темпоральний джитер", size=11, pad=4, fill="#ffffff", min_w=165)
    frags.extend([t_m1, t_m2, t_m3, t_m4])

    # 5. Детермінований супервізор та арбітр (Safe Supervisor)
    frags.append(rect(485, 255, 190, 200, fill="#eaeded", stroke="#16a085", sw=1.8, rx=8))
    frags.append(text(580, 285, "Safe Supervisor", size=14, bold=True, color="#0e6655"))
    t_sup_fsm, _, _ = textbox(580, 335, "Автомат станів (FSM)\nГістерезис N з M", size=11, pad=5, fill="#ffffff", min_w=165)
    t_sup_bump, _, _ = textbox(580, 405, "Bumpless Transfer\nТіньовий супровід", size=11, pad=5, fill="#e8f8f5", color="#0e6655", min_w=165)
    frags.extend([t_sup_fsm, t_sup_bump])

    # 6. Блок актуаторів праворуч
    frags.append(rect(705, 145, 175, 195, fill="#f4f6f7", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(792, 175, "Актуатори", size=14, bold=True, color=INK))
    t_act1, _, _ = textbox(792, 225, "Сервоприводи /\nКермові поверхні", size=11, pad=5, fill="#ffffff", min_w=145)
    t_act2, _, _ = textbox(792, 295, "Регулятори тяги\n(ESC / Мотори)", size=11, pad=5, fill="#ffffff", min_w=145)
    frags.extend([t_act1, t_act2])

    # З'єднувальні стрілки
    # Від камери до ML
    frags.append(arrow(190, 130, 215, 130, color=LINE, sw=1.5))

    # Від IMU/GNSS до резервного контуру
    frags.append(arrow(190, 235, 215, 335, color=LINE, sw=1.5))
    frags.append(arrow(190, 345, 215, 345, color=LINE, sw=1.5))

    # Від ML до Монітора (телеметрія інференсу)
    frags.append(arrow(460, 120, 485, 120, color="#d35400", sw=1.5))
    
    # Від Монітора до Супервізора (Health Status)
    frags.append(arrow(580, 230, 580, 255, color=POS, sw=1.8))
    frags.append(text(625, 245, "Метрики", size=10, bold=True, color=POS))

    # Від ML та Rule до Супервізора
    frags.append(arrow(337, 210, 485, 360, color="#d35400", sw=1.5)) # ML пропозиція
    frags.append(arrow(460, 405, 485, 405, color="#2980b9", sw=1.5)) # Rule пропозиція

    # Від Супервізора до актуаторів (Санкціонована дія u_safe)
    frags.append(arrow(675, 350, 705, 260, color=FIELD, sw=2.2))
    frags.append(text(690, 295, "u_safe", size=11, bold=True, color=FIELD))

    render(path, w, h, *frags, title=None)


def build_supervisor_fsm(path):
    w, h = 900, 400
    frags = []

    # 4 стани автомата
    # Стан 1: ML_ACTIVE (Зелений)
    s1, _, _ = textbox(130, 190, "STATE_NOMINAL_ML\n\n• Повне керування моделлю\n• Валідний латентний простір\n• Deadline & ентропія в нормі\n• Тіньовий PID стежить за u", size=11, pad=10, fill="#eafaf1", stroke="#27ae60", sw=2, min_w=205)

    # Стан 2: DEGRADED_HOLD (Жовтий)
    s2, _, _ = textbox(410, 85, "STATE_DEGRADED_HOLD\n\n• 1–2 пропущені кадри\n• Сплеск ентропії / завада\n• Екстраполяція траєкторії\n• Slew-rate обмеження кутів", size=11, pad=10, fill="#fefde8", stroke="#f39c12", sw=1.8, min_w=215)

    # Стан 3: RULE_FALLBACK (Синій / Помаранчевий)
    s3, _, _ = textbox(690, 190, "STATE_RULE_FALLBACK\n\n• Відкат на детерміноване правило\n• Утримання курсу за IMU/GNSS\n• Безударний вхід (Bumpless)\n• Модель ізольована в тінь", size=11, pad=10, fill="#ebf5fb", stroke="#2980b9", sw=2, min_w=215)

    # Стан 4: EMERGENCY_SAFE (Червоний)
    s4, _, _ = textbox(410, 310, "STATE_EMERGENCY_SAFE\n\n• Відмова сенсорів / таймаут > 1 с\n• Аварійне зависання / посадка\n• Примусове глушіння тяги\n• Фіксація відмови в NVS", size=11, pad=10, fill="#fdebd0", stroke="#c0392b", sw=2, min_w=215)

    frags.extend([s1, s2, s3, s4])

    # Переходи між станами
    # 1 -> 2: Одинична аномалія
    frags.append(arrow(200, 135, 300, 95, color="#f39c12", sw=1.6))
    frags.append(text(215, 105, "1 пропуск / OOD-сплеск", size=10, bold=True, color="#b7950b"))

    # 2 -> 1: Швидке відновлення
    frags.append(arrow(300, 115, 230, 150, color="#27ae60", sw=1.5))
    frags.append(text(225, 140, "Кадр валідний", size=10, bold=True, color="#27ae60"))

    # 2 -> 3: Стійка аномалія (N з M)
    frags.append(arrow(520, 95, 620, 135, color="#c0392b", sw=1.8))
    frags.append(text(605, 105, "N з M збоїв (напр. 3 з 5)", size=10, bold=True, color=POS))

    # 1 -> 3: Прямий збій (жорсткий таймаут або грубий вихід з меж)
    frags.append(arrow(235, 190, 580, 190, color=POS, sw=1.8))
    frags.append(text(410, 180, "Критичний таймаут watchdog / Грубий вихід з інваріантів", size=10, bold=True, color=POS))

    # 3 -> 1: Гістерезисне повернення (довге вікно спостереження)
    frags.append(arrow(580, 225, 235, 225, color="#27ae60", sw=1.6))
    frags.append(text(410, 240, "Повернення: T_recovery > 50 тактів стабільності + нульовий розрив", size=10, bold=True, color="#27ae60"))

    # 3 -> 4: Відмова правила або тривала дезорієнтація
    frags.append(arrow(670, 255, 520, 310, color=POS, sw=1.6))
    frags.append(text(620, 300, "Втрата навігації / Батарея", size=10, bold=True, color=POS))

    # 1 -> 4: Катастрофічна аномалія
    frags.append(arrow(200, 245, 300, 300, color=POS, sw=1.5))
    frags.append(text(210, 285, "Апаратний Fault", size=10, bold=True, color=POS))

    render(path, w, h, *frags, title=None)


def build_bumpless_transfer(path):
    w, h = 900, 420
    frags = []

    # Верхня секція: Жорсткий розрив (Hard Switching)
    frags.append(text(260, 30, "Жорсткий перемикач (Hard Switching) — УДАР", size=13, bold=True, color=POS))
    # Вісь часу
    frags.append(line(80, 150, 440, 150, color=LINE, sw=1.5))
    frags.append(line(80, 45, 80, 160, color=LINE, sw=1.5))
    frags.append(text(435, 165, "t", size=12, italic=True))
    frags.append(text(65, 55, "u(t)", size=12, italic=True))

    # Модельна траєкторія до t_fail
    frags.append(line(80, 85, 240, 85, color="#d35400", sw=2.5))
    frags.append(text(150, 75, "u_ml = +12.5°", size=11, bold=True, color="#d35400"))

    # Момент t_fail (x=240)
    frags.append(line(240, 45, 240, 155, color=MUTED, sw=1, dash="3,3"))
    frags.append(text(240, 170, "t_fail", size=11, bold=True, color=POS))

    # Миттєвий стрибок на правило u_rule = -8 град (y=135)
    frags.append(line(240, 85, 240, 135, color=POS, sw=2.5, dash="2,2"))
    frags.append(line(240, 135, 430, 135, color="#2980b9", sw=2.5))
    frags.append(text(340, 125, "u_rule = −8.0°", size=11, bold=True, color="#2980b9"))

    # Спайк/розрив маркер
    frags.append(circle(240, 85, 4, fill=POS, stroke=POS))
    frags.append(circle(240, 135, 4, fill=POS, stroke=POS))
    frags.append(text(300, 105, "Δu = 20.5° (Удар!)", size=11, bold=True, color=POS))

    # Нижня секція: Безударний перехід (Bumpless Transfer)
    frags.append(text(680, 30, "Безударний перехід (Bumpless Transfer)", size=13, bold=True, color=FIELD))
    frags.append(line(500, 150, 860, 150, color=LINE, sw=1.5))
    frags.append(line(500, 45, 500, 160, color=LINE, sw=1.5))
    frags.append(text(855, 165, "t", size=12, italic=True))
    frags.append(text(485, 55, "u(t)", size=12, italic=True))

    # До t_fail (x=660)
    frags.append(line(500, 85, 660, 85, color="#d35400", sw=2.5))
    frags.append(line(660, 45, 660, 155, color=MUTED, sw=1, dash="3,3"))
    frags.append(text(660, 170, "t_fail", size=11, bold=True, color=POS))

    # Тіньовий регулятор відстежує стан: I_term підлаштовано під u_ml!
    # Плавний перехід Slew-Rate / Blending від 660 до 770 (y від 85 до 135)
    frags.append(line(660, 85, 770, 135, color=FIELD, sw=2.8))
    frags.append(line(770, 135, 850, 135, color="#2980b9", sw=2.5))
    frags.append(text(725, 95, "Плавний Slew / Blending", size=11, bold=True, color=FIELD))
    frags.append(text(780, 125, "u_rule", size=11, bold=True, color="#2980b9"))

    # Пояснювальна таблиця механізмів знизу
    frags.append(rect(40, 220, 820, 170, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    frags.append(text(450, 245, "Ключові компоненти безударного стику (Bumpless Architecture)", size=13, bold=True, color=INK))

    b1, _, _ = textbox(175, 315, "1. Тіньове стеження (Tracking)\nІнтегратор PID підганяється під u_ml:\nI(t) = u_ml − (Kp·e + Kd·ė)", size=11, pad=6, fill="#ffffff", min_w=240)
    b2, _, _ = textbox(450, 315, "2. Динамічне злиття (Cross-Fading)\nu(t) = (1 − α(t))·u_hold + α(t)·u_rule\nα(t) плавно зростає 0 → 1 за T_trans", size=11, pad=6, fill="#ffffff", min_w=240)
    b3, _, _ = textbox(725, 315, "3. Обмеження темпу (Slew Rate)\n|du/dt| ≤ R_max\nУнеможливлює кидки струму привода", size=11, pad=6, fill="#ffffff", min_w=240)
    frags.extend([b1, b2, b3])

    render(path, w, h, *frags, title=None)


def main():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)

    fig1 = os.path.join(img_dir, "supervisor-architecture.svg")
    build_supervisor_architecture(fig1)
    print(f"Rendered: {fig1}")

    fig2 = os.path.join(img_dir, "supervisor-fsm-states.svg")
    build_supervisor_fsm(fig2)
    print(f"Rendered: {fig2}")

    fig3 = os.path.join(img_dir, "bumpless-transfer-blending.svg")
    build_bumpless_transfer(fig3)
    print(f"Rendered: {fig3}")


if __name__ == "__main__":
    main()
