#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми povernennia-na-dok-i-na-zariadku (sys-dron).
Вивід у ./img/
"""

import sys
import os

# Додаємо шлях до scripts/ у корені репо (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_docking_approach_phases():
    """Фігура 1: Ієрархічні фази прецизійної посадки на док-станцію."""
    w, h = 840, 480
    frags = []

    # Заголовок секцій ліворуч (Ешелони та датчики)
    frags.append(rect(15, 15, 810, 450, fill="#fcfdfe", stroke=LINE, sw=1.2, rx=6))

    # Стовпчики / Ешелони
    # 1. RTK-GNSS (h: 50м -> 15м)
    frags.append(rect(30, 40, 780, 95, fill="#eff6ff", stroke=NEG, sw=1.5, rx=5))
    frags.append(text(45, 65, "Фаза 1: Грубе наближення (RTK-GNSS / Moving Baseline)", size=13, color=NEG, anchor="start", bold=True))
    frags.append(text(45, 88, "• Діапазон: 1000 м → 15 м над платформою  |  Точність позиціювання: ±10–20 см", size=11, color=INK, anchor="start"))
    frags.append(text(45, 108, "• Датчики: Дводіапазонний RTK-приймач (L1/L2), трансляція RTCM v3 поправок від базової станції дока", size=11, color=MUTED, anchor="start"))
    frags.append(circle(760, 85, 22, fill="#ffffff", stroke=NEG, sw=1.5))
    frags.append(text(760, 90, "RTK", size=11, color=NEG, bold=True))

    # Стрілка переходу 1 -> 2
    frags.append(arrow(420, 137, 420, 152, color=LINE, sw=2))

    # 2. Оптичне / ІЧ наведення (h: 15м -> 0.5м)
    frags.append(rect(30, 155, 780, 105, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=5))
    frags.append(text(45, 180, "Фаза 2: Прецизійне візуальне та ІЧ наведення (AprilTag / IR-Beacon)", size=13, color=FIELD, anchor="start", bold=True))
    frags.append(text(45, 203, "• Діапазон: 15 м → 0.5 м  |  Точність розрахунку положення: ±1–2 см, курсу Yaw: ±0.5°", size=11, color=INK, anchor="start"))
    frags.append(text(45, 223, "• Вкладені маркери: Великий тег (висота 15–3 м) + Малий внутрішній тег (висота 3–0.5 м, без насичення)", size=11, color=MUTED, anchor="start"))
    frags.append(text(45, 241, "• ІЧ-маяк: Модульована піднесуча 38 кГц для виділення на тлі прямого сонячного засвічення", size=11, color=MUTED, anchor="start"))
    frags.append(circle(760, 205, 22, fill="#ffffff", stroke=FIELD, sw=1.5))
    frags.append(text(760, 210, "Vision", size=10, color=FIELD, bold=True))

    # Стрілка переходу 2 -> 3
    frags.append(arrow(420, 262, 420, 277, color=LINE, sw=2))

    # 3. Механічне центрування (h: 0.5м -> 0м)
    frags.append(rect(30, 280, 780, 85, fill="#fffbeb", stroke="#d97706", sw=1.5, rx=5))
    frags.append(text(45, 305, "Фаза 3: Механічне спрямування та фіксація (Mechanical Funnel & Clamps)", size=13, color="#b45309", anchor="start", bold=True))
    frags.append(text(45, 328, "• Діапазон: 0.5 м → торкання  |  Кінцева точність посадки: ±1.0 мм за осями X, Y, Yaw", size=11, color=INK, anchor="start"))
    frags.append(text(45, 348, "• Механізми: Напрямні конуси/воронки, активні сервоприводні штанги позиціювання, затискачі шасі", size=11, color=MUTED, anchor="start"))
    frags.append(circle(760, 320, 22, fill="#ffffff", stroke="#d97706", sw=1.5))
    frags.append(text(760, 325, "Align", size=10, color="#b45309", bold=True))

    # Стрілка переходу 3 -> 4
    frags.append(arrow(420, 367, 420, 382, color=LINE, sw=2))

    # 4. Електричний контакт і зарядка
    frags.append(rect(30, 385, 780, 70, fill="#fef2f2", stroke=POS, sw=1.5, rx=5))
    frags.append(text(45, 410, "Фаза 4: Електричний контакт та замикання силового контуру", size=13, color=POS, anchor="start", bold=True))
    frags.append(text(45, 432, "• Пружні позолочені контакти / концентричні кільця  |  Вимірювання R_контакту (<40 мОм)", size=11, color=INK, anchor="start"))
    frags.append(circle(760, 420, 22, fill="#ffffff", stroke=POS, sw=1.5))
    frags.append(text(760, 425, "Charge", size=10, color=POS, bold=True))

    render(os.path.join(IMG_DIR, "docking-approach-phases-and-sensors.svg"), w, h, *frags)


def fig_dock_charging_circuit():
    """Фігура 2: Принципова схема безпечної комутації та діагностики заряду."""
    w, h = 840, 440
    frags = []

    # Загальне тло
    frags.append(rect(15, 15, 810, 410, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))

    # Блок док-станції (ліворуч)
    frags.append(rect(30, 35, 360, 370, fill="#f8fafc", stroke=NEG, sw=1.5, rx=5))
    frags.append(text(210, 60, "ДОК-СТАНЦІЯ (Ground Station)", size=13, color=NEG, bold=True))

    # Силове джерело (CC/CV PSU)
    frags.append(rect(50, 80, 320, 50, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    frags.append(text(210, 102, "Силове джерело (CC / CV Power Supply)", size=11, color=INK, bold=True))
    frags.append(text(210, 118, "U_out = 25.2V / 50.4V, I_limit = 15.0A", size=10, color=MUTED))

    # Силове реле комутації
    frags.append(rect(50, 145, 320, 50, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    frags.append(text(210, 167, "Силове реле захисту (Power Interlock MOSFET/Relay)", size=11, color=POS, bold=True))
    frags.append(text(210, 183, "Розімкнено у стані спокою, увімкнення лише після handshake", size=10, color=MUTED))

    # Вимірювальний міст Кельвіна та шунт
    frags.append(rect(50, 210, 320, 65, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    frags.append(text(210, 230, "Вузол 4-провідної діагностики контакту", size=11, color=FIELD, bold=True))
    frags.append(text(210, 248, "Тестовий зонд струму: I_probe = 200 мА", size=10, color=INK))
    frags.append(text(210, 263, "Контроль падіння напруги dU → розрахунок R_contact", size=10, color=MUTED))

    # Контролер док-станції
    frags.append(rect(50, 290, 320, 100, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    frags.append(text(210, 312, "Керівний MCU / Safety Watchdog", size=11, color=INK, bold=True))
    frags.append(text(210, 332, "• Перевірка полярності напруги (Reverse Polarity)", size=10, color=MUTED))
    frags.append(text(210, 350, "• Примусове аварійне розмикання при струмі КЗ (<10 мкс)", size=10, color=MUTED))
    frags.append(text(210, 368, "• Моніторинг балансування комірок по CAN / SMBus", size=10, color=MUTED))

    # Контактна пара по центру
    frags.append(line(390, 105, 450, 105, color=POS, sw=2))
    frags.append(line(390, 240, 450, 240, color=FIELD, sw=1.8, dash="4,3"))
    frags.append(line(390, 370, 450, 370, color=NEG, sw=2))

    frags.append(rect(405, 95, 30, 20, fill="#fef08a", stroke="#ca8a04", sw=1.5, rx=3))
    frags.append(text(420, 109, "V+", size=10, color="#854d0e", bold=True))

    frags.append(rect(405, 230, 30, 20, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=3))
    frags.append(text(420, 244, "Sense", size=9, color="#166534", bold=True))

    frags.append(rect(405, 360, 30, 20, fill="#e2e8f0", stroke="#475569", sw=1.5, rx=3))
    frags.append(text(420, 374, "GND", size=10, color="#1e293b", bold=True))

    # Блок дрона (праворуч)
    frags.append(rect(450, 35, 360, 370, fill="#f8fafc", stroke=FIELD, sw=1.5, rx=5))
    frags.append(text(630, 60, "БОРТ ДРОНА (UAV Onboard)", size=13, color=FIELD, bold=True))

    # Вхідні захисні діоди та TVS
    frags.append(rect(470, 80, 320, 50, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    frags.append(text(630, 102, "Захисний модуль (TVS + Ідеальний діод)", size=11, color=INK, bold=True))
    frags.append(text(630, 118, "Захист від переполюсовки, іскрогасник soft-start", size=10, color=MUTED))

    # Батарея та комірки
    frags.append(rect(470, 145, 320, 75, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    frags.append(text(630, 167, "LiPo / Li-ion Акумуляторний блок (6S–12S)", size=11, color=POS, bold=True))
    frags.append(text(630, 185, "• NTC термистори: T_max ≤ 45°C під час заряду", size=10, color=MUTED))
    frags.append(text(630, 203, "• Окремий балансувальний порт комірок", size=10, color=MUTED))

    # BMS контролер
    frags.append(rect(470, 235, 320, 75, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    frags.append(text(630, 257, "Смарт-BMS (Battery Management System)", size=11, color=FIELD, bold=True))
    frags.append(text(630, 276, "• Контроль напруги кожної комірки (±1 мВ)", size=10, color=MUTED))
    frags.append(text(630, 294, "• Автоматичний захист від перезаряду (>4.22 В/ком)", size=10, color=MUTED))

    # Бортовий комп'ютер / Автопілот
    frags.append(rect(470, 325, 320, 65, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    frags.append(text(630, 347, "Польотний контролер / Companion Computer", size=11, color=INK, bold=True))
    frags.append(text(630, 365, "Телеметрія стану батареї по CAN / MAVLink", size=10, color=MUTED))
    frags.append(text(630, 379, "Блокування зльоту під час підключеного кабелю", size=9, color=MUTED))

    render(os.path.join(IMG_DIR, "dock-charging-circuit-and-state-machine.svg"), w, h, *frags)


if __name__ == '__main__':
    fig_docking_approach_phases()
    fig_dock_charging_circuit()
    print("Фігури успішно згенеровано у", IMG_DIR)
