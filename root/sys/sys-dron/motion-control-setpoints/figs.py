#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор векторних діаграм для теми motion-control-setpoints."""

import sys
import os

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору від теки теми)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import (
    render, textbox, fitbox, text, mtext, rect, line, arrow, circle,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG
)

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_control_cascade():
    """Фігура 1: Каскадна структура контурів керування та точки входу уставок."""
    w, h = 820, 480
    frags = []

    # Заголовок
    frags.append(text(w / 2, 28, "Каскадна схема регуляторів польотного контролера та точки ін'єкції уставок", size=15, bold=True))

    # Зовнішній контур: Комп'ютер-компаньйон
    frags.append(rect(30, 55, 760, 95, fill="#f0f4fa", stroke=NEG, sw=1.5, rx=8))
    frags.append(text(410, 78, "Бортовий комп'ютер-компаньйон (Companion Computer / ROS / Trajectory Planner)", size=13, color=NEG, bold=True))
    frags.append(text(410, 100, "Генерація плавної траєкторії: бажані координати p(t), швидкість v(t), прискорення a(t), орієнтація q(t)", size=11, color=MUTED))
    frags.append(text(410, 122, "MAVLink потік (10..50 Гц): SET_POSITION_TARGET_LOCAL_NED (#84) або SET_ATTITUDE_TARGET (#82)", size=11, color=INK))

    # Внутрішній простір автопілота
    frags.append(rect(30, 175, 760, 275, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(160, 198, "Польотний контролер (PX4 / ArduPilot)", size=13, bold=True))

    # Блоки каскаду регуляторів
    # 1. Регулятор позиції
    b1, w1, h1 = textbox(110, 260, "Регулятор\nпозиції\n(P / PID)", size=12, pad=10, fill="#ffffff", stroke=LINE, min_w=100)
    frags.append(b1)

    # 2. Регулятор швидкості
    b2, w2, h2 = textbox(280, 260, "Регулятор\nшвидкості\n(PID + FF)", size=12, pad=10, fill="#ffffff", stroke=LINE, min_w=100)
    frags.append(b2)

    # 3. Регулятор орієнтації
    b3, w3, h3 = textbox(460, 260, "Регулятор\nкутів / кватерніона\n(P / Q-control)", size=12, pad=10, fill="#ffffff", stroke=LINE, min_w=110)
    frags.append(b3)

    # 4. Регулятор кутових швидкостей
    b4, w4, h4 = textbox(640, 260, "Регулятор\nкутових швидкостей\n(PID Rate Control)", size=12, pad=10, fill="#ffffff", stroke=LINE, min_w=110)
    frags.append(b4)

    # Блок мікшера моторів
    b5, w5, h5 = textbox(720, 390, "Мікшер\nмоторів", size=11, pad=8, fill="#eef8f2", stroke=FIELD, min_w=85)
    frags.append(b5)

    # Зв'язки між регуляторами
    frags.append(arrow(160, 260, 225, 260, color=LINE, sw=1.8))
    frags.append(text(192, 250, "v_cmd", size=10, color=MUTED))

    frags.append(arrow(335, 260, 400, 260, color=LINE, sw=1.8))
    frags.append(text(367, 250, "q_cmd", size=10, color=MUTED))

    frags.append(arrow(520, 260, 580, 260, color=LINE, sw=1.8))
    frags.append(text(550, 250, "ω_cmd", size=10, color=MUTED))

    frags.append(arrow(640, 310, 640, 390, color=LINE, sw=1.8))
    frags.append(arrow(640, 390, 672, 390, color=LINE, sw=1.8))
    frags.append(text(640, 410, "Моменти торку τ", size=10, color=MUTED))

    # Лінії ін'єкції з бортового комп'ютера
    # Позиція (вхід у регулятор позиції)
    frags.append(arrow(110, 150, 110, 215, color=NEG, sw=1.8))
    frags.append(text(110, 175, "Pos (p)", size=10, color=NEG, bold=True))

    # Прямий зв'язок швидкості (Feedforward) у регулятор швидкості
    frags.append(arrow(280, 150, 280, 215, color=FIELD, sw=1.8))
    frags.append(text(280, 175, "Vel FF (v)", size=10, color=FIELD, bold=True))

    # Прямий зв'язок прискорення (Feedforward) повз регулятори
    frags.append(arrow(460, 150, 460, 215, color=POS, sw=1.8))
    frags.append(text(460, 175, "Att / Acc FF", size=10, color=POS, bold=True))

    # Пряма тяга (Thrust) до мікшера
    frags.append(line(720, 150, 720, 345, color=POS, sw=1.8, dash="4,3"))
    frags.append(arrow(720, 345, 720, 360, color=POS, sw=1.8))
    frags.append(text(720, 175, "Thrust", size=10, color=POS, bold=True))

    # Датчиковий зворотний зв'язок (EKF2 / Одометрія)
    frags.append(rect(150, 360, 380, 60, fill="#fff8ee", stroke="#d97706", sw=1.2, rx=6))
    frags.append(text(340, 383, "Оцінювач стану (EKF2 / Одометрія)", size=12, color="#92400e", bold=True))
    frags.append(text(340, 403, "Зворотний зв'язок: положення p, швидкість v, кути q, кутові швидкості ω", size=10, color="#b45309"))

    # Стрілки зворотного зв'язку
    frags.append(arrow(200, 360, 110, 310, color="#d97706", sw=1.2))
    frags.append(arrow(280, 360, 280, 310, color="#d97706", sw=1.2))
    frags.append(arrow(420, 360, 460, 310, color="#d97706", sw=1.2))
    frags.append(arrow(500, 360, 600, 310, color="#d97706", sw=1.2))

    return render(os.path.join(OUT_DIR, "control-cascade.svg"), w, h, *frags)


def fig_typemask_logic():
    """Фігура 2: Структура бітової маски type_mask та логіка ігнорування/активації каналів."""
    w, h = 820, 440
    frags = []

    frags.append(text(w / 2, 28, "Структура бітової маски type_mask у повідомленні SET_POSITION_TARGET_LOCAL_NED", size=15, bold=True))
    frags.append(text(w / 2, 50, "Інверсна логіка MAVLink: біт = 1 означає ІГНОРУВАТИ поле, біт = 0 означає ОБРОБЛЯТИ", size=12, color=MUTED))

    # Смуга 16 біт (від біта 15 до біта 0)
    box_w = 46
    start_x = 42
    y_bits = 80

    bits_info = [
        ("15..12", "Зарезервовано", MUTED, "#f3f4f6"),
        ("11", "YawRate", NEG, "#eaf0fd"),
        ("10", "Yaw", NEG, "#eaf0fd"),
        ("9", "Force", POS, "#fdecea"),
        ("8", "Az", FIELD, "#eafaf1"),
        ("7", "Ay", FIELD, "#eafaf1"),
        ("6", "Ax", FIELD, "#eafaf1"),
        ("5", "Vz", "#d97706", "#fef3c7"),
        ("4", "Vy", "#d97706", "#fef3c7"),
        ("3", "Vx", "#d97706", "#fef3c7"),
        ("2", "Z", "#7c3aed", "#ede9fe"),
        ("1", "Y", "#7c3aed", "#ede9fe"),
        ("0", "X", "#7c3aed", "#ede9fe"),
    ]

    # Малюємо блоки бітів
    # Для бітів 15..12 виділимо ширший блок
    frags.append(rect(start_x, y_bits, box_w * 2, 45, fill="#f3f4f6", stroke=LINE, sw=1.2, rx=4))
    frags.append(text(start_x + box_w, y_bits + 20, "Біти 15..12", size=10, color=MUTED, bold=True))
    frags.append(text(start_x + box_w, y_bits + 36, "Резерв", size=9, color=MUTED))

    cur_x = start_x + box_w * 2 + 6
    for b_idx, (b_num, b_name, b_col, b_bg) in enumerate(bits_info[1:]):
        frags.append(rect(cur_x, y_bits, box_w, 45, fill=b_bg, stroke=LINE, sw=1.2, rx=4))
        frags.append(text(cur_x + box_w / 2, y_bits + 18, f"b{b_num}", size=11, color=b_col, bold=True))
        frags.append(text(cur_x + box_w / 2, y_bits + 34, b_name, size=9, color=INK))
        cur_x += box_w + 6

    # Приклади типових масок
    y_ex = 155
    frags.append(text(w / 2, y_ex, "Типові конфігурації керування та їхні шістнадцяткові значення", size=13, bold=True))

    examples = [
        (
            "Тільки позиція (Position Hold)",
            "0b0000 1101 1111 1000",
            "0x0DF8 (3576)",
            "Активні: X, Y, Z + Yaw. Швидкості та прискорення ігноруються автопілотом.",
            "#ede9fe",
            "#7c3aed"
        ),
        (
            "Тільки швидкість (Velocity Control)",
            "0b0000 1101 1100 0111",
            "0x0DC7 (3527)",
            "Активні: Vx, Vy, Vz + Yaw. Позиція та прискорення ігноруються (політ за вектором).",
            "#fef3c7",
            "#d97706"
        ),
        (
            "Позиція + Швидкість (Feedforward)",
            "0b0000 1101 1100 0000",
            "0x0DC0 (3520)",
            "Активні: X, Y, Z, Vx, Vy, Vz. Прямий зв'язок за швидкістю для усунення лагу контуру.",
            "#eafaf1",
            FIELD
        ),
        (
            "Повний стан (Full State p + v + a + yaw_rate)",
            "0b0000 0100 0000 0000",
            "0x0400 (1024)",
            "Активні: X, Y, Z, Vx, Vy, Vz, Ax, Ay, Az, YawRate. Максимальна точність слідування.",
            "#fdecea",
            POS
        ),
    ]

    cur_y = y_ex + 20
    for title, binary_str, hex_val, desc, bg_c, border_c in examples:
        frags.append(rect(42, cur_y, 736, 52, fill=bg_c, stroke=border_c, sw=1.4, rx=6))
        frags.append(text(55, cur_y + 20, title, size=11, color=INK, anchor="start", bold=True))
        frags.append(text(340, cur_y + 20, binary_str, size=11, color=MUTED, anchor="start"))
        frags.append(text(530, cur_y + 20, hex_val, size=11, color=border_c, anchor="start", bold=True))
        frags.append(text(55, cur_y + 39, desc, size=10, color=MUTED, anchor="start"))
        cur_y += 58

    return render(os.path.join(OUT_DIR, "typemask-logic.svg"), w, h, *frags)


def fig_offboard_failsafe_fsm():
    """Фігура 3: Кінцевий автомат переходів у режим Offboard та спрацювання Failsafe."""
    w, h = 820, 420
    frags = []

    frags.append(text(w / 2, 28, "Життєвий цикл режиму Offboard та спрацювання захисного таймера (Failsafe)", size=15, bold=True))

    # Стан 1: Неактивний / Ручний
    b1, _, _ = textbox(120, 110, "СТАН: MANUAL / HOLD\nАвтопілот утримує позицію\nабо керується оператором", size=11, pad=10, fill="#f3f4f6", stroke=LINE, min_w=170)
    frags.append(b1)

    # Стан 2: Прогрів потоку (Warmup)
    b2, _, _ = textbox(390, 110, "СТАН: WARMUP STREAM\nБортовий комп'ютер шле\nуставки з частотою >= 2 Гц", size=11, pad=10, fill="#eaf0fd", stroke=NEG, min_w=180)
    frags.append(b2)

    # Стан 3: Активний Offboard
    b3, _, _ = textbox(690, 110, "СТАН: OFFBOARD ACTIVE\nАвтопілот виконує уставки\nТаймер втрати скидається", size=11, pad=10, fill="#eafaf1", stroke=FIELD, min_w=180)
    frags.append(b3)

    # Переходи верхнього ряду
    frags.append(arrow(210, 110, 295, 110, color=NEG, sw=1.8))
    frags.append(text(252, 95, "Старт потоку", size=10, color=NEG))

    frags.append(arrow(485, 110, 595, 110, color=FIELD, sw=1.8))
    frags.append(text(540, 85, "MAV_CMD_DO_SET_MODE", size=9, color=FIELD, bold=True))
    frags.append(text(540, 99, "(Потік стабільний)", size=9, color=MUTED))

    # Нижній ряд: Спрацювання Failsafe
    b4, _, _ = textbox(690, 290, "ТАЙМАУТ ВТРАТИ ПОТОКУ\nНемає уставок > 500 мс\n(COM_OF_LOSS_T спрацював)", size=11, pad=10, fill="#fdecea", stroke=POS, min_w=180)
    frags.append(b4)

    # Дії Failsafe
    b5, _, _ = textbox(390, 290, "АВАРІЙНИЙ РЕЖИМ\nАвтономне зависання (Hold)\nабо повернення додому (RTL)", size=11, pad=10, fill="#fff8ee", stroke="#d97706", min_w=190)
    frags.append(b5)

    b6, _, _ = textbox(120, 290, "АВАРІЙНА ПОСАДКА (Land)\nЯкщо зв'язок не відновлено\nабо сідає батарея", size=11, pad=10, fill="#fdecea", stroke=POS, min_w=170)
    frags.append(b6)

    # Стрілка вниз до таймауту
    frags.append(arrow(690, 160, 690, 235, color=POS, sw=1.8))
    frags.append(text(745, 198, "dt > 500 мс", size=10, color=POS, bold=True))

    # Стрілка вліво до Аварійного режиму
    frags.append(arrow(595, 290, 490, 290, color="#d97706", sw=1.8))
    frags.append(text(542, 275, "Failsafe дія", size=10, color="#d97706"))

    # Стрілка від Аварійного режиму до Посадки
    frags.append(arrow(290, 290, 210, 290, color=POS, sw=1.8))
    frags.append(text(250, 275, "Таймаут Hold", size=10, color=POS))

    # Стрілка відновлення зв'язку
    frags.append(line(390, 235, 390, 185, color=FIELD, sw=1.5, dash="3,3"))
    frags.append(arrow(390, 185, 600, 140, color=FIELD, sw=1.5))
    frags.append(text(460, 190, "Потік відновлено (Auto-recover)", size=9, color=FIELD))

    # Інформаційна плашка знизу
    frags.append(rect(42, 365, 736, 42, fill="#f8fafc", stroke=LINE, sw=1.0, rx=5))
    frags.append(text(410, 383, "Правило безпеки: комп'ютер-компаньйон зобов'язаний тримати потік навіть при нерухомому висінні дрона", size=10, color=INK))
    frags.append(text(410, 397, "Припинення надсилання координат автопілот розцінює як зависання або аварію керуючої програми", size=9, color=MUTED))

    return render(os.path.join(OUT_DIR, "offboard-failsafe-fsm.svg"), w, h, *frags)


def fig_trajectory_feedforward():
    """Фігура 4: Порівняння ступінчастої уставки позиції та гладкої траєкторії з прямим зв'язком (Feedforward)."""
    w, h = 820, 450
    frags = []

    frags.append(text(w / 2, 28, "Порівняння відпрацювання ступінчастої уставки та гладкого профілю з Feedforward", size=15, bold=True))

    # Ліва колонка: Тільки позиція (Step Setpoint)
    frags.append(rect(35, 55, 360, 375, fill="#fffaf9", stroke=POS, sw=1.4, rx=8))
    frags.append(text(215, 80, "Ступінчаста уставка (Тільки позиція)", size=13, color=POS, bold=True))
    frags.append(text(215, 98, "Передача лише цільової точки p_target без v_ff та a_ff", size=10, color=MUTED))

    # Графік 1: Позиція з перерегулюванням
    frags.append(rect(55, 115, 320, 80, fill="#ffffff", stroke=LINE, sw=1.0, rx=4))
    frags.append(text(65, 130, "Позиція x(t)", size=9, color=MUTED, anchor="start"))
    # Уставка (сходинка)
    frags.append(line(70, 180, 120, 180, color=MUTED, sw=1.5, dash="3,3"))
    frags.append(line(120, 180, 120, 135, color=MUTED, sw=1.5, dash="3,3"))
    frags.append(line(120, 135, 360, 135, color=MUTED, sw=1.5, dash="3,3"))
    # Реальний відгук (перерегулювання і коливання)
    frags.append(line(70, 180, 120, 180, color=POS, sw=2.0))
    frags.append(line(120, 180, 180, 125, color=POS, sw=2.0))
    frags.append(line(180, 125, 230, 142, color=POS, sw=2.0))
    frags.append(line(230, 142, 280, 133, color=POS, sw=2.0))
    frags.append(line(280, 133, 360, 135, color=POS, sw=2.0))
    frags.append(text(205, 120, "Перерегулювання!", size=9, color=POS, bold=True))

    # Графік 2: Швидкість (стрибок і насичення)
    frags.append(rect(55, 210, 320, 80, fill="#ffffff", stroke=LINE, sw=1.0, rx=4))
    frags.append(text(65, 225, "Швидкість v(t)", size=9, color=MUTED, anchor="start"))
    frags.append(line(70, 270, 120, 270, color=POS, sw=2.0))
    frags.append(line(120, 270, 140, 225, color=POS, sw=2.0))
    frags.append(line(140, 225, 220, 225, color=POS, sw=2.0))
    frags.append(line(220, 225, 280, 270, color=POS, sw=2.0))
    frags.append(line(280, 270, 360, 270, color=POS, sw=2.0))
    frags.append(text(180, 240, "Насичення за швидкістю (V_max)", size=9, color=POS))

    # Графік 3: Моторне навантаження / Ривок
    frags.append(rect(55, 305, 320, 110, fill="#ffffff", stroke=LINE, sw=1.0, rx=4))
    frags.append(text(65, 322, "Наслідки для апарата:", size=10, color=POS, anchor="start", bold=True))
    frags.append(text(65, 342, "• Нескінченний теоретичний ривок (Jerk = d³x/dt³)", size=9, color=INK, anchor="start"))
    frags.append(text(65, 360, "• Ударне насичення регуляторів і моторів", size=9, color=INK, anchor="start"))
    frags.append(text(65, 378, "• Вібрації, розгойдування корисного навантаження", size=9, color=INK, anchor="start"))
    frags.append(text(65, 396, "• Затримка реакції контуру положення (Phase Lag)", size=9, color=INK, anchor="start"))

    # Права колонка: Сплайн + Feedforward (Pos + Vel + Acc)
    frags.append(rect(425, 55, 360, 375, fill="#f4faf6", stroke=FIELD, sw=1.4, rx=8))
    frags.append(text(605, 80, "Плавний сплайн + Feedforward (p + v + a)", size=13, color=FIELD, bold=True))
    frags.append(text(605, 98, "Передача узгодженого стану з полінома 5-го степеня", size=10, color=MUTED))

    # Графік 1: Гладка позиція (S-curve)
    frags.append(rect(445, 115, 320, 80, fill="#ffffff", stroke=LINE, sw=1.0, rx=4))
    frags.append(text(455, 130, "Позиція x(t)", size=9, color=MUTED, anchor="start"))
    frags.append(line(460, 180, 500, 180, color=FIELD, sw=2.0))
    frags.append(line(500, 180, 540, 172, color=FIELD, sw=2.0))
    frags.append(line(540, 172, 620, 145, color=FIELD, sw=2.0))
    frags.append(line(620, 145, 680, 135, color=FIELD, sw=2.0))
    frags.append(line(680, 135, 750, 135, color=FIELD, sw=2.0))
    frags.append(text(610, 160, "Плавне S-подібне наростання", size=9, color=FIELD))

    # Графік 2: Дзвоноподібна швидкість
    frags.append(rect(445, 210, 320, 80, fill="#ffffff", stroke=LINE, sw=1.0, rx=4))
    frags.append(text(455, 225, "Швидкість v(t) [Feedforward]", size=9, color=MUTED, anchor="start"))
    frags.append(line(460, 270, 500, 270, color=FIELD, sw=2.0))
    frags.append(line(500, 270, 560, 230, color=FIELD, sw=2.0))
    frags.append(line(560, 230, 620, 230, color=FIELD, sw=2.0))
    frags.append(line(620, 230, 680, 270, color=FIELD, sw=2.0))
    frags.append(line(680, 270, 750, 270, color=FIELD, sw=2.0))
    frags.append(text(600, 245, "Неперервний профіль швидкості", size=9, color=FIELD))

    # Графік 3: Переваги підходу
    frags.append(rect(445, 305, 320, 110, fill="#ffffff", stroke=LINE, sw=1.0, rx=4))
    frags.append(text(455, 322, "Переваги динамічного зв'язку:", size=10, color=FIELD, anchor="start", bold=True))
    frags.append(text(455, 342, "• Обмежений, контрольований ривок (Minimum Jerk)", size=9, color=INK, anchor="start"))
    frags.append(text(455, 360, "• Регулятор помилки відпрацьовує лише шум і вітер", size=9, color=INK, anchor="start"))
    frags.append(text(455, 378, "• Нульове фазове запізнення траєкторії", size=9, color=INK, anchor="start"))
    frags.append(text(455, 396, "• Економія заряду батареї та стабільність камери", size=9, color=INK, anchor="start"))

    return render(os.path.join(OUT_DIR, "trajectory-feedforward.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_control_cascade()
    fig_typemask_logic()
    fig_offboard_failsafe_fsm()
    fig_trajectory_feedforward()
    print("Усі фігури згенеровано успішно!")
