#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми derevo-povedinky (sys-dron).
Вивід у ./img/
"""

import sys
import os

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_drone_behavior_tree_structure():
    """Фігура 1: Ієрархічна структура дерева поведінки автономного дрона."""
    w, h = 920, 480
    frags = []

    # Фон полотна
    frags.append(rect(0, 0, w, h, fill="#ffffff", stroke="#e5e7eb", sw=1.0, rx=0))

    # Легенда типів вузлів вгорі праворуч
    frags.append(rect(670, 15, 235, 105, fill="#f8fafc", stroke="#cbd5e1", sw=1.0, rx=4))
    frags.append(text(787, 32, "Легенда типів вузлів:", size=11, color="#334155", bold=True))
    frags.append(rect(680, 42, 16, 12, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=2))
    frags.append(text(705, 52, "Fallback / Селектор (?)", size=10, color="#1e293b", anchor="start"))
    frags.append(rect(680, 58, 16, 12, fill="#d1fae5", stroke="#059669", sw=1.2, rx=2))
    frags.append(text(705, 68, "Sequence / Послідовність (→)", size=10, color="#1e293b", anchor="start"))
    frags.append(rect(680, 74, 16, 12, fill="#ede9fe", stroke="#7c3aed", sw=1.2, rx=2))
    frags.append(text(705, 84, "Condition / Умова (круглі)", size=10, color="#1e293b", anchor="start"))
    frags.append(rect(680, 90, 16, 12, fill="#e0f2fe", stroke="#0284c7", sw=1.2, rx=2))
    frags.append(text(705, 100, "Action / Дія (прямокутні)", size=10, color="#1e293b", anchor="start"))

    # З'єднувальні лінії дерева (малюємо ДО блоків, щоб лінії не перетинали текст)
    # Корінь (450, 45) -> Діти рівня 1: Failsafe (160, 130), Avoidance (450, 130), Mission (740, 130)
    frags.append(line(450, 68, 160, 108, color="#475569", sw=1.8))
    frags.append(line(450, 68, 450, 108, color="#475569", sw=1.8))
    frags.append(line(450, 68, 740, 108, color="#475569", sw=1.8))

    # Branch 1 (Failsafe Sequence at 160, 130) -> Leaves at y=235
    frags.append(line(160, 152, 90, 210, color="#475569", sw=1.5))
    frags.append(line(160, 152, 230, 210, color="#475569", sw=1.5))

    # Branch 2 (Avoidance Sequence at 450, 130) -> Leaves at y=235
    frags.append(line(450, 152, 380, 210, color="#475569", sw=1.5))
    frags.append(line(450, 152, 520, 210, color="#475569", sw=1.5))

    # Branch 3 (Mission Sequence at 740, 130) -> Leaves & Subtree at y=235
    frags.append(line(740, 152, 650, 210, color="#475569", sw=1.5))
    frags.append(line(740, 152, 830, 210, color="#475569", sw=1.5))

    # Subtree (Navigate Waypoint Sequence at 830, 235) -> Leaves at y=340
    frags.append(line(830, 258, 740, 315, color="#475569", sw=1.5))
    frags.append(line(830, 258, 850, 315, color="#475569", sw=1.5))

    # Subtree (Waypoint Check Fallback at 740, 340) -> Leaves at y=435
    frags.append(line(740, 362, 680, 415, color="#475569", sw=1.5))
    frags.append(line(740, 362, 800, 415, color="#475569", sw=1.5))

    # Рівень 0: Корінь (Root Reactive Fallback)
    b_root, _, _ = textbox(450, 45, "Root Fallback (Reactive ?)\n[Пріоритетний селектор місії]",
                           size=11, pad=8, fill="#fef3c7", stroke="#d97706", sw=2.0, bold=True)
    frags.append(b_root)

    # Рівень 1: Гілки за спаданням пріоритету (зліва направо)
    # Гілка 1: Аварійний захист (Failsafe)
    b_f1, _, _ = textbox(160, 130, "Sequence (→)\n1. Аварійний контур",
                         size=10, pad=6, fill="#d1fae5", stroke="#059669", sw=1.5, bold=True)
    frags.append(b_f1)

    # Гілка 2: Реактивне ухилення від перешкод
    b_f2, _, _ = textbox(450, 130, "Sequence (→)\n2. Реактивне ухилення",
                         size=10, pad=6, fill="#d1fae5", stroke="#059669", sw=1.5, bold=True)
    frags.append(b_f2)

    # Гілка 3: Штатна місія
    b_f3, _, _ = textbox(740, 130, "Sequence (→)\n3. Виконання місії",
                         size=10, pad=6, fill="#d1fae5", stroke="#059669", sw=1.5, bold=True)
    frags.append(b_f3)

    # Рівень 2: Листки гілки 1 (Failsafe)
    b_c1, _, _ = textbox(90, 235, "Condition\nБатарея < 20% або\nвтрата лінка",
                         size=9, pad=6, fill="#ede9fe", stroke="#7c3aed", sw=1.3, rx=12)
    frags.append(b_c1)

    b_a1, _, _ = textbox(230, 235, "Action\nВиконати RTL або\nекстрену посадку",
                         size=9, pad=6, fill="#e0f2fe", stroke="#0284c7", sw=1.3, rx=4)
    frags.append(b_a1)

    # Рівень 2: Листки гілки 2 (Avoidance)
    b_c2, _, _ = textbox(380, 235, "Condition\nПерешкода < 3.0 м\n(LiDAR / Сонар)",
                         size=9, pad=6, fill="#ede9fe", stroke="#7c3aed", sw=1.3, rx=12)
    frags.append(b_c2)

    b_a2, _, _ = textbox(520, 235, "Action\nМаневр обльоту\n(DWA локальний)",
                         size=9, pad=6, fill="#e0f2fe", stroke="#0284c7", sw=1.3, rx=4)
    frags.append(b_a2)

    # Рівень 2: Листки гілки 3 (Mission)
    b_a3, _, _ = textbox(650, 235, "Action\nЗліт до ешелону\n(Takeoff 30m)",
                         size=9, pad=6, fill="#e0f2fe", stroke="#0284c7", sw=1.3, rx=4)
    frags.append(b_a3)

    b_seq_nav, _, _ = textbox(830, 235, "Sequence (→)\nПроліт точок",
                              size=10, pad=6, fill="#d1fae5", stroke="#059669", sw=1.5, bold=True)
    frags.append(b_seq_nav)

    # Рівень 3: Підгілка навігації місії
    b_sel_wp, _, _ = textbox(740, 340, "Fallback (?)\nОбробка WP",
                             size=10, pad=6, fill="#fef3c7", stroke="#d97706", sw=1.5, bold=True)
    frags.append(b_sel_wp)

    b_a_fly, _, _ = textbox(850, 340, "Action\nПоліт до цілі WP\n(V = 12 м/с)",
                            size=9, pad=6, fill="#e0f2fe", stroke="#0284c7", sw=1.3, rx=4)
    frags.append(b_a_fly)

    # Рівень 4: Перевірка досягнення точки і скидання
    b_c_wp, _, _ = textbox(680, 435, "Condition\nDist to WP < 1.5м",
                           size=9, pad=5, fill="#ede9fe", stroke="#7c3aed", sw=1.3, rx=12)
    frags.append(b_c_wp)

    b_a_drop, _, _ = textbox(800, 435, "Action\nСкидання вантажу +\nнаступна WP",
                            size=9, pad=5, fill="#e0f2fe", stroke="#0284c7", sw=1.3, rx=4)
    frags.append(b_a_drop)

    # Пояснювальні анотації пріоритету
    frags.append(line(40, 100, 280, 100, color="#dc2626", sw=1.2, dash="3,3"))
    frags.append(text(160, 92, "◄ НАЙВИЩИЙ ПРІОРИТЕТ ◄", size=9, color="#dc2626", bold=True))

    render(os.path.join(IMG_DIR, "drone-behavior-tree-structure.svg"), w, h, *frags,
           title="Ієрархічна структура дерева поведінки автономного дрона")


def fig_bt_tick_and_blackboard():
    """Фігура 2: Конвеєр Тіку (Tick) та обмін даними через Дошку Оголошень (Blackboard)."""
    w, h = 920, 450
    frags = []

    # Фон полотна
    frags.append(rect(0, 0, w, h, fill="#ffffff", stroke="#e5e7eb", sw=1.0, rx=0))

    # Секція 1 (Зліва): Дерево поведінки та цикл Тіку
    frags.append(rect(15, 15, 420, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(225, 38, "Конвеєр Тіку Дерева Поведінки (20–50 Гц)", size=12, color="#0f172a", bold=True))

    # Тік генератор зверху
    b_tick_gen, _, _ = textbox(225, 75, "Польотний планувач (20–50 Гц)\nТік (Tick) від кореня до листків",
                               size=10, pad=6, fill="#e0e7ff", stroke="#4338ca", sw=1.5, bold=True)
    frags.append(b_tick_gen)

    # Стрілка тіку вниз
    frags.append(arrow(225, 100, 225, 130, color="#4338ca", sw=2.0))
    frags.append(text(235, 118, "Tick()", size=9, color="#4338ca", bold=True, anchor="start"))

    # Вузол дерева Root
    b_t_root, _, _ = textbox(225, 150, "Reactive Fallback (?)\nПріоритетна оцінка умов",
                             size=10, pad=5, fill="#fef3c7", stroke="#d97706", sw=1.5, bold=True)
    frags.append(b_t_root)

    # Розгалуження тіку до листків
    frags.append(line(225, 172, 115, 210, color="#64748b", sw=1.5))
    frags.append(line(225, 172, 335, 210, color="#64748b", sw=1.5))

    # Вузол Condition (Перевірка перешкоди)
    b_t_cond, _, _ = textbox(115, 235, "Condition Node\n(dist < 3.0 м?)\nПовертає: SUCCESS/FAIL",
                             size=9, pad=5, fill="#ede9fe", stroke="#7c3aed", sw=1.3, rx=10)
    frags.append(b_t_cond)

    # Вузол Action (Політ по траєкторії)
    b_t_act, _, _ = textbox(335, 235, "Action Node\n[FlyToWaypoint]\nПовертає: RUNNING",
                            size=9, pad=5, fill="#e0f2fe", stroke="#0284c7", sw=1.3, rx=4)
    frags.append(b_t_act)

    # Стрілки повернення статусів вгору
    frags.append(arrow(115, 268, 115, 310, color="#059669", sw=1.5))
    frags.append(text(115, 325, "Статус: SUCCESS / FAIL\n(Миттєвий висновок)", size=9, color="#059669", bold=True))

    frags.append(arrow(335, 268, 335, 310, color="#0284c7", sw=1.5))
    frags.append(text(335, 325, "Статус: RUNNING\n(Тривала асинхронна дія)", size=9, color="#0284c7", bold=True))

    # Блок переривання (Preemption)
    b_halt, _, _ = textbox(225, 385, "Реактивне переривання (Preemption):\nЯкщо умова змінилась -> виклик Halt() для Action",
                           size=9, pad=5, fill="#fee2e2", stroke="#dc2626", sw=1.2, rx=4)
    frags.append(b_halt)

    # Секція 2 (Справа): Дошка Оголошень (Blackboard)
    frags.append(rect(460, 15, 445, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(682, 38, "Дошка Оголошень (Blackboard Hub)", size=12, color="#0f172a", bold=True))

    # Зовнішні джерела (EKF, Сенсори) пишуть в Blackboard
    b_sensors, _, _ = textbox(682, 75, "Сенсорний шар (EKF, LiDAR, Батарея, GNSS)\nЗапис телеметрії через атомарні порти",
                              size=9, pad=5, fill="#f1f5f9", stroke="#475569", sw=1.3)
    frags.append(b_sensors)

    frags.append(arrow(682, 100, 682, 125, color="#475569", sw=1.8))
    frags.append(text(692, 115, "Write: Стан дрона", size=9, color="#475569", anchor="start"))

    # Центральна таблиця ключів Blackboard
    frags.append(rect(475, 130, 415, 160, fill="#ffffff", stroke="#0284c7", sw=1.5, rx=4))
    frags.append(rect(475, 130, 415, 25, fill="#e0f2fe", stroke="#0284c7", sw=1.0, rx=4))
    frags.append(text(682, 147, "Потокобезпечний K-V простір ключів Blackboard", size=10, color="#0369a1", bold=True))

    frags.append(text(490, 172, "drone/battery_voltage  : float  = 14.85 V", size=9, color="#1e293b", anchor="start"))
    frags.append(text(490, 192, "sensor/lidar_min_dist  : float  = 1.82 m", size=9, color="#1e293b", anchor="start"))
    frags.append(text(490, 212, "mission/current_wp_idx : uint16 = 4", size=9, color="#1e293b", anchor="start"))
    frags.append(text(490, 232, "nav/target_pos_ned     : vec3   = [120, 45, -30]", size=9, color="#1e293b", anchor="start"))
    frags.append(text(490, 252, "cmd/velocity_setpoint  : vec3   = [8.0, 0.0, 0.0]", size=9, color="#1e293b", anchor="start"))
    frags.append(text(490, 272, "status/safety_override : bool   = false", size=9, color="#1e293b", anchor="start"))

    # Зв'язки між BT і Blackboard (Читання та Запис)
    # Condition читає sensor/lidar_min_dist
    frags.append(arrow(475, 192, 190, 235, color="#7c3aed", sw=1.5))
    frags.append(text(305, 202, "Read Port (lidar_dist)", size=9, color="#7c3aed", bold=True))

    # Action читає nav/target_pos_ned і пише cmd/velocity_setpoint
    frags.append(arrow(475, 232, 415, 235, color="#0284c7", sw=1.5))
    frags.append(text(445, 222, "Read Target", size=9, color="#0284c7", bold=True))

    frags.append(arrow(415, 252, 475, 252, color="#059669", sw=1.5))
    frags.append(text(445, 266, "Write Setpoint", size=9, color="#059669", bold=True))

    # Нижня частина Blackboard -> Видача на контури автопілота
    frags.append(arrow(682, 295, 682, 330, color="#475569", sw=1.8))
    frags.append(text(692, 315, "Read Setpoints", size=9, color="#475569", anchor="start"))

    b_actuators, _, _ = textbox(682, 365, "Контури керування польотом (PX4 / ArduPilot / ROS2)\nПозиційний PID-регулятор -> Розподіл тяги моторів",
                                size=9, pad=5, fill="#f1f5f9", stroke="#475569", sw=1.3)
    frags.append(b_actuators)

    render(os.path.join(IMG_DIR, "bt-tick-and-blackboard.svg"), w, h, *frags,
           title="Конвеєр Тіку та обмін даними через Дошку Оголошень")


if __name__ == "__main__":
    fig_drone_behavior_tree_structure()
    fig_bt_tick_and_blackboard()
    print("Фігури успішно згенеровано у ./img/")
