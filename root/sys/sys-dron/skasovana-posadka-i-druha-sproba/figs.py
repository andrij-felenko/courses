#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми skasovana-posadka-i-druha-sproba (sys-dron).
Вивід у ./img/
"""

import sys
import os

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_go_around_trajectory():
    """Фігура 1: Кінематичний профіль скасування посадки та виходу на друге коло."""
    w, h = 860, 380
    frags = []

    # 1. Земля
    frags.append(rect(0, 320, w, 60, fill="#e5e7eb", stroke=LINE, sw=1.5, rx=0))
    frags.append(text(80, 355, "Рівень землі (Z = 0)", size=12, color=MUTED, bold=True))

    # Посадковий майданчик
    frags.append(rect(230, 312, 100, 8, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=2))
    frags.append(text(280, 305, "Посадковий майданчик", size=10, color=FIELD, bold=True))

    # Раптова перешкода на майданчику
    frags.append(rect(265, 275, 30, 37, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    frags.append(text(280, 295, "⚠️", size=14, color=POS))
    frags.append(text(280, 265, "Перешкода", size=10, color=POS, bold=True))

    # Горизонтальні рівні висоти (пунктирні лінії)
    # Безпечна висота маневрування h_missed (25 м -> Y=70)
    frags.append(line(40, 70, 820, 70, color=NEG, sw=1.5, dash="6,4"))
    frags.append(text(720, 58, "Missed Approach Alt (25 м)", size=11, color=NEG, bold=True))

    # Висота прийняття рішення h_decision (4 м -> Y=230)
    frags.append(line(40, 230, 420, 230, color="#d97706", sw=1.2, dash="4,3"))
    frags.append(text(120, 220, "Висота рішення h_dec (4 м)", size=10, color="#d97706", bold=True))

    # 2. Траєкторія зниження (Approach)
    b_app, _, _ = textbox(110, 85, "1. Зниження (Approach)\nV_z = -1.2 м/с", size=10, pad=5, fill="#eff6ff", stroke=NEG)
    frags.append(b_app)
    frags.append(arrow(110, 115, 240, 225, color=LINE, sw=2.0))

    # Точка виявлення перешкоди й активації Abort (x=245, y=230)
    frags.append(circle(245, 230, 7, fill="#fee2e2", stroke=POS, sw=2))
    frags.append(text(245, 210, "Тригер Abort!", size=10, color=POS, bold=True))

    # 3. Динамічна просадка (Spool-up & Sinkage)
    frags.append(line(245, 230, 275, 260, color=POS, sw=2.0, dash="3,2"))
    frags.append(circle(275, 260, 5, fill="#ffffff", stroke=POS, sw=1.5))
    frags.append(text(355, 265, "Просадка Δh_sink (1.2 м)", size=10, color=POS))

    # 4. Вертикальний набір тяги (Climb-out)
    frags.append(arrow(275, 260, 275, 75, color=FIELD, sw=2.5))
    b_climb, _, _ = textbox(375, 160, "2. Вертикальний набір (Climb)\nT = T_max, V_z = +3.0 м/с\nКрен/тангаж = 0°", 
                            size=10, pad=5, fill="#f0fdf4", stroke=FIELD, bold=True)
    frags.append(b_climb)

    # 5. Вихід на ешелон Missed Approach і перехід у коло очікування
    frags.append(circle(275, 70, 6, fill="#eff6ff", stroke=NEG, sw=2))
    frags.append(arrow(285, 70, 500, 70, color=NEG, sw=2.0))
    b_loiter, _, _ = textbox(390, 95, "3. Вихід на Missed Approach Alt", size=10, pad=4, fill="#eff6ff", stroke=NEG)
    frags.append(b_loiter)

    # 6. Коло очікування / друге коло (Circuit Pattern)
    frags.append(arrow(500, 70, 630, 110, color=LINE, sw=2.0))
    frags.append(arrow(630, 110, 630, 190, color=LINE, sw=2.0))
    frags.append(arrow(630, 190, 520, 210, color=LINE, sw=2.0))
    frags.append(arrow(520, 210, 430, 150, color=LINE, sw=2.0))

    b_circuit, _, _ = textbox(575, 150, "4. Коло повторного\nзаходу (Holding Pattern)\nАудит батареї", 
                              size=10, pad=5, fill="#faf5ff", stroke="#9333ea")
    frags.append(b_circuit)

    # 7. Гілка повернення на повторну глісаду
    frags.append(arrow(430, 150, 480, 110, color=FIELD, sw=1.8))
    frags.append(text(465, 120, "На FAF", size=10, color=FIELD, bold=True))

    # 8. Аварійна гілка (Failsafe Divert)
    frags.append(arrow(630, 190, 760, 280, color=POS, sw=1.8))
    b_fail, _, _ = textbox(750, 240, "Батарея < критичної:\nВідхід на Rally Point", 
                           size=9, pad=4, fill="#fee2e2", stroke=POS)
    frags.append(b_fail)
    frags.append(rect(730, 312, 80, 8, fill="#fee2e2", stroke=POS, sw=1.5, rx=2))
    frags.append(text(770, 305, "Rally Point", size=10, color=POS, bold=True))

    render(os.path.join(IMG_DIR, "go-around-trajectory.svg"), w, h, *frags,
           title="Кінематичний профіль процедури Go-Around та виходу на друге коло")


def fig_go_around_fsm():
    """Фігура 2: Граф кінцевого автомата Go-Around та перевірки енергетичного бюджету."""
    w, h = 860, 360
    frags = []

    # Стан 1: Зниження та моніторинг
    b1 = fitbox(30, 50, 170, 80, "APPROACH_DESCENT\nЗниження на глісаді\nКонтроль датчиків", size=11, pad=6, fill="#eff6ff", stroke=NEG, bold=True)
    frags.append(b1)

    # Перехід 1->2 (Тригер)
    frags.append(arrow(200, 90, 280, 90, color=POS, sw=2.0))
    frags.append(text(240, 75, "Тригер Abort", size=10, color=POS, bold=True))
    frags.append(text(240, 108, "Лідар / Вітер / RC", size=9, color=MUTED))

    # Стан 2: Екстрений вертикальний набір
    b2 = fitbox(280, 50, 180, 80, "BRAKE_AND_CLIMB\nМаксимальна тяга T_max\nЗатискання крену 0°", size=11, pad=6, fill="#f0fdf4", stroke=FIELD, bold=True)
    frags.append(b2)

    # Перехід 2->3 (Досягнуто безпечної висоти)
    frags.append(arrow(460, 90, 540, 90, color=LINE, sw=2.0))
    frags.append(text(500, 75, "h ≥ h_safe", size=10, color=FIELD, bold=True))
    frags.append(text(500, 108, "Вихід на ешелон", size=9, color=MUTED))

    # Стан 3: Аудит енергії та спроб
    b3 = fitbox(540, 50, 180, 80, "ENERGY_AUDIT\nОцінка заряду батареї\nЛічильник спроб N", size=11, pad=6, fill="#fef3c7", stroke="#d97706", bold=True)
    frags.append(b3)

    # Гілка успіху (Бюджет OK) 3 -> 4
    frags.append(arrow(630, 130, 630, 210, color=FIELD, sw=2.0))
    frags.append(mtext(700, 165, ["SOC ≥ E_circuit", "Спроби < MAX"], size=9, color=FIELD, bold=True))

    # Стан 4: Коло очікування та повторний захід
    b4 = fitbox(540, 210, 180, 80, "CIRCUIT_LOITER\nКоло очікування\nВихід на точку FAF", size=11, pad=6, fill="#faf5ff", stroke="#9333ea", bold=True)
    frags.append(b4)

    # Повернення 4 -> 1
    frags.append(arrow(540, 250, 115, 250, color=LINE, sw=1.8))
    frags.append(arrow(115, 250, 115, 130, color=LINE, sw=1.8))
    frags.append(text(330, 238, "Повторний захват глісади (Re-entry)", size=10, color=INK, bold=True))

    # Гілка вичерпання (Бюджет FAIL або Спроби >= MAX) 3 -> 5
    frags.append(arrow(720, 90, 760, 90, color=POS, sw=2.0))
    frags.append(arrow(760, 90, 760, 210, color=POS, sw=2.0))
    frags.append(mtext(805, 145, ["SOC < E_min", "або Спроби ≥ MAX"], size=9, color=POS, bold=True))

    # Стан 5: Failsafe Emergency Landing
    b5 = fitbox(680, 210, 160, 80, "EMERGENCY_FAILSAFE\nВибір Rally Point або\nпосадка на місці", size=10, pad=5, fill="#fee2e2", stroke=POS, bold=True)
    frags.append(b5)

    # Нормальна посадка зі Стан 1 -> TOUCHDOWN
    frags.append(arrow(115, 50, 115, 18, color=MUTED, sw=1.5))
    frags.append(text(115, 10, "Нормальне торкання → LANDED", size=9, color=MUTED))

    render(os.path.join(IMG_DIR, "go-around-fsm.svg"), w, h, *frags,
           title="Граф станів та переходів автомата Go-Around")


def main():
    fig_go_around_trajectory()
    fig_go_around_fsm()
    print("Всі SVG-фігури успішно згенеровано.")


if __name__ == "__main__":
    main()
