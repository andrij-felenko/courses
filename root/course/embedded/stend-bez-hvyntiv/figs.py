#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор схем для теми stend-bez-hvyntiv (Стенд без гвинтів).
Вивід: ./img/*.svg
"""

import os
import sys

# Підключаємо svgkit із кореня репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, textbox, rect, text, line, arrow, circle, mtext,
    INK, MUTED, POS, NEG, FIELD, LINE as STROKE_LINE, FILL, BG, FONT
)

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")


def make_bench_safety_power_chain():
    """Схема 1: Ланцюг безпечного живлення на стенді."""
    w, h = 880, 360
    frags = []

    # Заголовок блоків
    frags.append(text(440, 28, "Стендовий ланцюг живлення: захист від короткого замикання та неконтрольованого пуску", size=16, bold=True))

    # 1. Джерело живлення (Батарея або Лабораторний БЖ)
    b1, _, _ = textbox(130, 130, "Джерело струму\nLiPo 4S-6S (14.8-25.2 В)\nабо Лабораторний БЖ\n(CC limit = 1.0 A)", size=12, fill="#eef4fc", stroke=NEG, pad=12)
    frags.append(b1)

    # Стрілка живлення
    frags.append(arrow(230, 130, 300, 130, color=POS, sw=2.5))
    frags.append(text(265, 118, "DC+", size=11, color=POS, bold=True))
    frags.append(text(265, 148, "GND", size=11, color=INK))

    # 2. Струмовий запобіжник (SmokeStopper)
    b2, _, _ = textbox(410, 130, "Струмовий захист (SmokeStopper)\nЕлектронний самовідновний ключ\nПоріг вимикання: 1.0 - 2.0 A\nЧас відсікання: < 15 мс", size=12, fill="#fef8e7", stroke="#d35400", pad=12)
    frags.append(b2)

    # Стрілка на плату
    frags.append(arrow(520, 130, 590, 130, color=FIELD, sw=2.5))
    frags.append(text(555, 118, "V_prot", size=11, color=FIELD, bold=True))

    # 3. Бортова електроніка
    b3, _, _ = textbox(720, 130, "Польотний стек\nПольотний контролер (FC)\n+ 4-in-1 регулятор ESC\nЖивлення логіки 5V/9V BEC", size=12, fill="#eafaf1", stroke=FIELD, pad=12)
    frags.append(b3)

    # Мотори та заборона гвинтів унизу
    frags.append(arrow(670, 200, 670, 245, color=STROKE_LINE, sw=2.0))
    frags.append(arrow(770, 200, 770, 245, color=STROKE_LINE, sw=2.0))

    # Блок моторів
    b_mot, _, _ = textbox(720, 290, "4× BLDC Мотори (Холостий хід)\nСтрум споживання: 0.3 - 0.8 A на мотор\nКритична умова: ПРОПЕЛЕРИ ДЕМОНТОВАНО", size=12, fill="#fdf2e9", stroke=POS, pad=12)
    frags.append(b_mot)

    # Значок заборони пропелерів ліворуч унизу
    frags.append(circle(200, 285, 38, fill="#fadbd8", stroke=POS, sw=2.5))
    frags.append(line(173, 260, 227, 310, color=POS, sw=3.5))
    frags.append(text(200, 280, "NO PROPS", size=12, color=POS, bold=True))
    frags.append(text(200, 298, "ГВИНТИ ЗНЯТО", size=10, color=POS, bold=True))

    # Пояснювальний текст знизу
    b_note, _, _ = textbox(440, 285, "Золоте правило безпеки:\nБудь-яке підключення силового акумулятора\nна столі виконується ВИКЛЮЧНО без пропелерів.\nЗапобіжник рятує MOSFET від КЗ при першому запуску.", size=11, fill="#f8f9fa", stroke=MUTED, pad=8)
    frags.append(b_note)

    render(os.path.join(IMG_DIR, "bench-safety-power-chain.svg"), w, h, *frags)


def make_pid_negative_feedback():
    """Схема 2: Від'ємний зворотний зв'язок PID при тестуванні в руках."""
    w, h = 900, 420
    frags = []

    frags.append(text(450, 26, "Перевірка відгуку PID: Від'ємний зворотний зв'язок (Negative Feedback) проти розгону", size=16, bold=True))

    # Ліва колонка: ПРАВИЛЬНА робота (Від'ємний зворотний зв'язок)
    frags.append(rect(40, 60, 390, 335, fill="#f4fbf7", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(235, 88, "ПРАВИЛЬНО: Опір збуренню (Negative Feedback)", size=13, color=FIELD, bold=True))

    # Стан 1: Ручний нахил
    b_l1, _, _ = textbox(235, 140, "1. Зовнішня дія:\nОператор нахиляє дрон рукою праворуч (+Roll)", size=11, fill="#ffffff", stroke=MUTED, pad=8)
    frags.append(b_l1)
    frags.append(arrow(235, 175, 235, 205, color=FIELD, sw=2.0))

    # Стан 2: Відгук датчика
    b_l2, _, _ = textbox(235, 240, "2. Сенсорний відгук:\nГіроскоп фіксує ω_roll > 0; помилка Error = -ω_roll\nPID видає коригувальний момент вліво (-Torque)", size=11, fill="#ffffff", stroke=MUTED, pad=8)
    frags.append(b_l2)
    frags.append(arrow(235, 275, 235, 305, color=FIELD, sw=2.0))

    # Стан 3: Реакція моторів
    b_l3, _, _ = textbox(235, 345, "3. Реакція моторів:\nПраві (нижні) мотори РОЗКРУЧУЮТЬСЯ,\nліві (верхні) сповільнюються -> опір нахилу", size=11, fill="#e8f8f0", stroke=FIELD, pad=8)
    frags.append(b_l3)

    # Права колонка: ФАТАЛЬНА ПОМИЛКА (Додатний зворотний зв'язок / Перевернута вісь)
    frags.append(rect(470, 60, 390, 335, fill="#fdf4f4", stroke=POS, sw=1.5, rx=8))
    frags.append(text(665, 88, "АВАРІЯ: Додатний зворотний зв'язок (Positive Feedback)", size=13, color=POS, bold=True))

    # Стан 1
    b_r1, _, _ = textbox(665, 140, "1. Зовнішня дія:\nОператор нахиляє дрон рукою праворуч (+Roll)", size=11, fill="#ffffff", stroke=MUTED, pad=8)
    frags.append(b_r1)
    frags.append(arrow(665, 175, 665, 205, color=POS, sw=2.0))

    # Стан 2
    b_r2, _, _ = textbox(665, 240, "2. Помилка орієнтації (Inverted Axis):\nЧерез неправильну орієнтацію сенсора/мікшера\nконтролер вважає, що нахил відбувається вліво", size=11, fill="#ffffff", stroke=MUTED, pad=8)
    frags.append(b_r2)
    frags.append(arrow(665, 275, 665, 305, color=POS, sw=2.0))

    # Стан 3
    b_r3, _, _ = textbox(665, 345, "3. Катастрофічний результат:\nЛіві (верхні) мотори розганяються, посилюючи нахил!\nУ польоті це призводить до миттєвого перевороту", size=11, fill="#fadbd8", stroke=POS, pad=8)
    frags.append(b_r3)

    render(os.path.join(IMG_DIR, "pid-negative-feedback-hand-test.svg"), w, h, *frags)


def make_failsafe_state_machine():
    """Схема 3: Автомат станів Failsafe на стенді."""
    w, h = 900, 360
    frags = []

    frags.append(text(450, 26, "Автомат станів Failsafe: перевірка реакції на вимкнення передавача (TX Off)", size=16, bold=True))

    # Стан 0: RC Link Active
    b0, _, _ = textbox(130, 150, "Нормальний зв'язок\n(RC_LINK_OK)\nПриймання пакетів RC\nЧастота: 50 - 500 Гц\nМотори активні (Arm)", size=12, fill="#eafaf1", stroke=FIELD, pad=10)
    frags.append(b0)

    # Перехід 1
    frags.append(arrow(225, 150, 315, 150, color=POS, sw=2.2))
    frags.append(text(270, 132, "Втрата сигналу", size=11, color=POS, bold=True))
    frags.append(text(270, 168, "TX Off / Jamming", size=10, color=MUTED))

    # Стан 1: Stage 1 Guard
    b1, _, _ = textbox(430, 150, "Failsafe: Етап 1 (Stage 1)\nЗатримка: 0.4 - 1.0 с\nУтримання останніх команд\nабо вирівнювання горизонту\nОчікування поновлення", size=12, fill="#fef9e7", stroke="#f39c12", pad=10)
    frags.append(b1)

    # Перехід 2
    frags.append(arrow(545, 150, 635, 150, color=POS, sw=2.2))
    frags.append(text(590, 132, "Таймаут вичерпано", size=11, color=POS, bold=True))
    frags.append(text(590, 168, "t > t_guard", size=10, color=MUTED))

    # Стан 2: Stage 2 Action
    b2, _, _ = textbox(760, 150, "Failsafe: Етап 2 (Stage 2)\nДія: Drop (Вимкнення) або RTH\nНа столі: МИТТЄВА ЗУПИНКА\nГаз = 0, Disarm = TRUE\nЗвуковий сигнал маяка", size=12, fill="#fadbd8", stroke=POS, pad=10)
    frags.append(b2)

    # Зворотна стрілка поновлення сигналу
    frags.append(arrow(430, 220, 130, 220, color=FIELD, sw=1.8))
    frags.append(text(280, 240, "Поновлення сигналу на Stage 1 -> Відновлення повного керування", size=11, color=FIELD))

    # Блокування після Stage 2
    b_lock, _, _ = textbox(450, 310, "Блокування повторного армінгу після Failsafe:\nПісля переходу в Stage 2 повторний запуск блокується прапорцем FAILSAFE / RX_LOSS.\nДля відновлення потрібно пересмикнути тумблер Arming у положення Disarm -> Arm.", size=11, fill="#f8f9fa", stroke=STROKE_LINE, pad=8)
    frags.append(b_lock)

    render(os.path.join(IMG_DIR, "failsafe-state-machine-bench.svg"), w, h, *frags)


def make_motor_order_and_props():
    """Схема 4: Нумерація моторів, порядок та напрямок обертання (Props In vs Props Out)."""
    w, h = 900, 380
    frags = []

    frags.append(text(450, 26, "Геометрія квадрокоптера Quad-X: Нумерація моторів та конфігурації обертання", size=16, bold=True))

    # Ліва половина: Props In (Стандарт)
    frags.append(rect(40, 55, 390, 305, fill="#f9fbfd", stroke=NEG, sw=1.5, rx=8))
    frags.append(text(235, 80, "Конфігурація «Props In» (Всередину)", size=13, color=NEG, bold=True))

    # Мотори Props In
    # M4 (FR-LF): Front-Left (CW)
    frags.append(circle(140, 140, 28, fill="#ffffff", stroke=STROKE_LINE, sw=2))
    frags.append(text(140, 135, "M4", size=12, bold=True))
    frags.append(text(140, 150, "CW ↻", size=10, color=POS))

    # M2 (FR-RT): Front-Right (CCW)
    frags.append(circle(330, 140, 28, fill="#ffffff", stroke=STROKE_LINE, sw=2))
    frags.append(text(330, 135, "M2", size=12, bold=True))
    frags.append(text(330, 150, "CCW ↺", size=10, color=NEG))

    # Центр рами
    frags.append(rect(215, 185, 40, 40, fill="#d6eaf8", stroke=NEG, sw=1.5, rx=4))
    frags.append(text(235, 208, "FC ▲", size=11, bold=True))
    # Промені
    frags.append(line(160, 155, 215, 195, color=MUTED, sw=2))
    frags.append(line(310, 155, 255, 195, color=MUTED, sw=2))
    frags.append(line(160, 255, 215, 215, color=MUTED, sw=2))
    frags.append(line(310, 255, 255, 215, color=MUTED, sw=2))

    # M3 (RR-LF): Rear-Left (CCW)
    frags.append(circle(140, 270, 28, fill="#ffffff", stroke=STROKE_LINE, sw=2))
    frags.append(text(140, 265, "M3", size=12, bold=True))
    frags.append(text(140, 280, "CCW ↺", size=10, color=NEG))

    # M1 (RR-RT): Rear-Right (CW)
    frags.append(circle(330, 270, 28, fill="#ffffff", stroke=STROKE_LINE, sw=2))
    frags.append(text(330, 265, "M1", size=12, bold=True))
    frags.append(text(330, 280, "CW ↻", size=10, color=POS))

    frags.append(text(235, 335, "Передні лопаті кидають потік на ніс / камеру", size=10, color=MUTED, italic=True))

    # Права половина: Props Out (Назовні / Реверс)
    frags.append(rect(470, 55, 390, 305, fill="#fdfbf7", stroke="#d35400", sw=1.5, rx=8))
    frags.append(text(665, 80, "Конфігурація «Props Out» (Назовні / Reversed)", size=13, color="#d35400", bold=True))

    # M4 (Front-Left): CCW
    frags.append(circle(570, 140, 28, fill="#ffffff", stroke=STROKE_LINE, sw=2))
    frags.append(text(570, 135, "M4", size=12, bold=True))
    frags.append(text(570, 150, "CCW ↺", size=10, color=NEG))

    # M2 (Front-Right): CW
    frags.append(circle(760, 140, 28, fill="#ffffff", stroke=STROKE_LINE, sw=2))
    frags.append(text(760, 135, "M2", size=12, bold=True))
    frags.append(text(760, 150, "CW ↻", size=10, color=POS))

    # Центр рами
    frags.append(rect(645, 185, 40, 40, fill="#fdebd0", stroke="#d35400", sw=1.5, rx=4))
    frags.append(text(665, 208, "FC ▲", size=11, bold=True))
    frags.append(line(590, 155, 645, 195, color=MUTED, sw=2))
    frags.append(line(740, 155, 685, 195, color=MUTED, sw=2))
    frags.append(line(590, 255, 645, 215, color=MUTED, sw=2))
    frags.append(line(740, 255, 685, 215, color=MUTED, sw=2))

    # M3 (Rear-Left): CW
    frags.append(circle(570, 270, 28, fill="#ffffff", stroke=STROKE_LINE, sw=2))
    frags.append(text(570, 265, "M3", size=12, bold=True))
    frags.append(text(570, 280, "CW ↻", size=10, color=POS))

    # M1 (Rear-Right): CCW
    frags.append(circle(760, 270, 28, fill="#ffffff", stroke=STROKE_LINE, sw=2))
    frags.append(text(760, 265, "M1", size=12, bold=True))
    frags.append(text(760, 280, "CCW ↺", size=10, color=NEG))

    frags.append(text(665, 335, "Відкидає траву й бруд геть від лінзи камери", size=10, color=MUTED, italic=True))

    render(os.path.join(IMG_DIR, "motor-order-and-props-direction.svg"), w, h, *frags)


def main():
    os.makedirs(IMG_DIR, exist_ok=True)
    make_bench_safety_power_chain()
    make_pid_negative_feedback()
    make_failsafe_state_machine()
    make_motor_order_and_props()
    print("OK: bench-safety-power-chain.svg, pid-negative-feedback-hand-test.svg, failsafe-state-machine-bench.svg, motor-order-and-props-direction.svg")


if __name__ == "__main__":
    main()
