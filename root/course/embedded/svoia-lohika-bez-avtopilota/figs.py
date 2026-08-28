# -*- coding: utf-8 -*-
"""Генератор векторних SVG-фігур для теми svoia-lohika-bez-avtopilota."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_architecture_layers():
    w, h = 820, 440
    frags = []

    frags.append(rect(20, 40, 780, 80, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(40, 68, "Рівень 3: Декларативна черга цілей (Goal Queue Engine, 1–5 Гц)", size=13, bold=True, anchor="start"))
    frags.append(text(40, 95, "Черга кроків місії: Waypoint(X,Y) → WaitTrigger → InspectArea. Контроль таймаутів і критеріїв.", size=11, color=MUTED, anchor="start"))

    frags.append(rect(20, 145, 780, 100, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(40, 172, "Рівень 2: Диспетчер подій та Ієрархічний автомат (Event Dispatcher + HSM, 20–50 Гц)", size=13, bold=True, color="#166534", anchor="start"))
    frags.append(text(40, 196, "Обробка черги подій (Run-to-Completion), перевірка guard-умов, перемикання режимів.", size=11, color=MUTED, anchor="start"))
    frags.append(text(40, 218, "Передає цільові уставки на нижній контур; приймає події датчиків і завершення дій.", size=11, color=MUTED, anchor="start"))

    frags.append(rect(20, 270, 780, 75, fill="#eff6ff", stroke=NEG, sw=1.5, rx=8))
    frags.append(text(40, 296, "Рівень 1: Швидкі контури стабілізації та оцінки (100–1000 Гц)", size=13, bold=True, color=NEG, anchor="start"))
    frags.append(text(40, 322, "ПІД-регулятори моторів, орієнтація за IMU, фільтрація давачів, апаратний захист.", size=11, color=MUTED, anchor="start"))

    frags.append(rect(20, 365, 780, 50, fill="#faf5ff", stroke="#7e22ce", sw=1.5, rx=8))
    frags.append(text(40, 396, "Рівень 0: Апаратні переривання (ISR) та DMA — драйвери шин SPI, I2C, UART, таймери ШІМ", size=12, bold=True, color="#6b21a8", anchor="start"))

    # Стрілки
    frags.append(arrow(240, 120, 240, 143, color=LINE, sw=1.8))
    frags.append(text(250, 134, "активація цілі", size=10, color=MUTED, anchor="start"))

    frags.append(arrow(580, 145, 580, 122, color=LINE, sw=1.8))
    frags.append(text(590, 134, "ціль досягнуто / збій", size=10, color=MUTED, anchor="start"))

    frags.append(arrow(240, 247, 240, 268, color=LINE, sw=1.8))
    frags.append(text(250, 259, "уставки (v, ω, pitch)", size=10, color=MUTED, anchor="start"))

    frags.append(arrow(580, 270, 580, 247, color=LINE, sw=1.8))
    frags.append(text(590, 259, "події оцінки", size=10, color=MUTED, anchor="start"))

    frags.append(arrow(410, 365, 410, 347, color=LINE, sw=1.8))
    frags.append(text(420, 358, "сирі відліки давачів", size=10, color=MUTED, anchor="start"))

    render(os.path.join(IMG_DIR, "architecture-layers.svg"), w, h, *frags)


def fig_hsm_hierarchy():
    w, h = 820, 420
    frags = []

    # Зовнішній супер-стан OPERATIONAL
    frags.append(rect(20, 40, 490, 360, fill="#f8fafc", stroke="#475569", sw=2, rx=10))
    frags.append(text(35, 68, "Суперстан: OPERATIONAL (виконання завдань)", size=13, bold=True, anchor="start", color="#1e293b"))
    frags.append(text(35, 88, "Вхід: увімкнути живлення приводів · Вихід: скинути уставки, зафіксувати гальма", size=10, color=MUTED, anchor="start"))

    # Підстани всередині OPERATIONAL
    b1, _, _ = textbox(140, 150, "NAVIGATING\nРух до точки маршруту\nКонтроль курсу й дистанції", size=11, fill="#eff6ff", stroke=NEG, min_w=170)
    frags.append(b1)

    b2, _, _ = textbox(380, 150, "AVOID_OBSTACLE\nЛокальний об'їзд\nОпитування ультразвуку/ToF", size=11, fill="#fef3c7", stroke="#d97706", min_w=170)
    frags.append(b2)

    b3, _, _ = textbox(260, 295, "HOLD_STATION\nУтримання позиції\nОчікування події / тригера", size=11, fill="#f0fdf4", stroke=FIELD, min_w=190)
    frags.append(b3)

    # Переходи всередині OPERATIONAL
    frags.append(arrow(225, 138, 290, 138, color=LINE, sw=1.5))
    frags.append(text(258, 130, "EV_OBSTACLE", size=9.5, color=POS, bold=True))

    frags.append(arrow(290, 162, 225, 162, color=LINE, sw=1.5))
    frags.append(text(258, 175, "EV_CLEAR", size=9.5, color=FIELD, bold=True))

    frags.append(arrow(140, 195, 200, 260, color=LINE, sw=1.5))
    frags.append(text(145, 235, "EV_REACHED", size=9.5, color=MUTED))

    frags.append(arrow(320, 260, 380, 195, color=LINE, sw=1.5))
    frags.append(text(375, 235, "EV_RESUME", size=9.5, color=MUTED))

    # Стан IDLE справа вгорі
    b_idle, _, _ = textbox(660, 100, "IDLE\nОчікування місії\nПриводи знеструмлені", size=11, fill="#f1f5f9", stroke="#64748b", min_w=160)
    frags.append(b_idle)

    # Стан FAILSAFE справа внизу
    b_fail, _, _ = textbox(660, 300, "EMERGENCY_FAILSAFE\nАварійна зупинка\nОчищення черги цілей\nСигнал тривоги", size=11, fill="#fef2f2", stroke=POS, min_w=160)
    frags.append(b_fail)

    # Переходи між OPERATIONAL та IDLE/FAILSAFE
    frags.append(arrow(660, 145, 510, 145, color=LINE, sw=1.6))
    frags.append(text(585, 135, "EV_START_MISSION", size=9.5, color=FIELD, bold=True))

    frags.append(arrow(510, 185, 660, 185, color=LINE, sw=1.6))
    frags.append(text(585, 175, "EV_MISSION_DONE", size=9.5, color=MUTED))

    # Батьківський аварійний перехід з усього OPERATIONAL
    frags.append(arrow(510, 300, 580, 300, color=POS, sw=2.2))
    frags.append(text(545, 288, "EV_CRITICAL_FAULT", size=10, color=POS, bold=True))
    frags.append(text(545, 318, "(розряд, обрив датчика)", size=9.5, color=MUTED))

    render(os.path.join(IMG_DIR, "hsm-state-hierarchy.svg"), w, h, *frags)


def fig_superloop_timing():
    w, h = 820, 380
    frags = []

    # Загальна шкала
    frags.append(rect(20, 40, 780, 55, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))
    frags.append(text(410, 62, "Один кадр суперциклу (базовий такт планування T = 100 мс)", size=13, bold=True))
    frags.append(text(410, 82, "Кожен слот виконує неблокуючий крок алгоритму з фіксованим дедлайном WCET", size=10.5, color=MUTED))

    # Слот 1: 1 кГц
    frags.append(rect(20, 115, 145, 145, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(92, 138, "Слот 1 кГц (ISR)", size=11.5, bold=True, color=NEG))
    frags.append(text(92, 156, "Таймерне переривання", size=9.5, color=MUTED))
    frags.append(text(30, 180, "• Опитування IMU", size=10, anchor="start"))
    frags.append(text(30, 198, "• ПІД швидкості коліс", size=10, anchor="start"))
    frags.append(text(30, 216, "• Оновлення ШІМ", size=10, anchor="start"))
    frags.append(text(92, 245, "WCET ≤ 120 мкс", size=10.5, bold=True, color=NEG))

    # Слот 2: 100 Гц
    frags.append(rect(175, 115, 175, 145, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(262, 138, "Слот 100 Гц (10 мс)", size=11.5, bold=True, color="#166534"))
    frags.append(text(262, 156, "Одометрія та сенсори", size=9.5, color=MUTED))
    frags.append(text(185, 180, "• Фільтр орієнтації", size=10, anchor="start"))
    frags.append(text(185, 198, "• Енкодери коліс", size=10, anchor="start"))
    frags.append(text(185, 216, "• Далекоміри ToF", size=10, anchor="start"))
    frags.append(text(262, 245, "WCET ≤ 450 мкс", size=10.5, bold=True, color="#166534"))

    # Слот 3: 20 Гц
    frags.append(rect(360, 115, 185, 145, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6))
    frags.append(text(452, 138, "Слот 20 Гц (50 мс)", size=11.5, bold=True, color="#92400e"))
    frags.append(text(452, 156, "Логіка рішень", size=9.5, color=MUTED))
    frags.append(text(370, 180, "• Диспетчеризація подій", size=10, anchor="start"))
    frags.append(text(370, 198, "• Крок автомата HSM", size=10, anchor="start"))
    frags.append(text(370, 216, "• Оцінка прогресу цілі", size=10, anchor="start"))
    frags.append(text(452, 245, "WCET ≤ 800 мкс", size=10.5, bold=True, color="#92400e"))

    # Слот 4: 5 Гц
    frags.append(rect(555, 115, 150, 145, fill="#f5f3ff", stroke="#7c3aed", sw=1.5, rx=6))
    frags.append(text(630, 138, "Слот 5 Гц (200 мс)", size=11.5, bold=True, color="#5b21b6"))
    frags.append(text(630, 156, "Зв'язок і сервіс", size=9.5, color=MUTED))
    frags.append(text(565, 180, "• Пакет телеметрії", size=10, anchor="start"))
    frags.append(text(565, 198, "• Watchdog tick", size=10, anchor="start"))
    frags.append(text(565, 216, "• Лог у Flash", size=10, anchor="start"))
    frags.append(text(630, 245, "WCET ≤ 600 мкс", size=10.5, bold=True, color="#5b21b6"))

    # Слот 5: Сон
    frags.append(rect(715, 115, 85, 145, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(757, 145, "Сон WFI", size=11, bold=True, color="#475569"))
    frags.append(text(757, 180, "Запас", size=10, color=MUTED))
    frags.append(text(757, 198, "часу", size=10, color=MUTED))
    frags.append(text(757, 216, "> 85%", size=10.5, bold=True, color=FIELD))
    frags.append(text(757, 245, "Економія", size=9.5, color="#475569"))

    # Підсумок утилізації
    frags.append(rect(20, 280, 780, 80, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(40, 305, "Гарантія детермінізму: сумарна зайнятість процесора U = Σ (WCET_i / T_i) < 15%", size=12, bold=True, anchor="start", color="#0f172a"))
    frags.append(text(40, 328, "Будь-яка критична подія аварії обробляється максимум за 1 мс у перериванні,", size=10.5, color=MUTED, anchor="start"))
    frags.append(text(40, 346, "а зміна стану HSM та гальмування гарантовано відбуваються протягом одного кроку 10–50 мс.", size=10.5, color=MUTED, anchor="start"))

    render(os.path.join(IMG_DIR, "superloop-time-slots.svg"), w, h, *frags)


def fig_goal_lifecycle():
    w, h = 820, 380
    frags = []

    # 5 блоків життєвого циклу
    b1, _, _ = textbox(85, 80, "1. QUEUED\nЦіль у кільцевому\nбуфері місії", size=11, fill="#f8fafc", stroke="#64748b", min_w=120)
    frags.append(b1)

    b2, _, _ = textbox(250, 80, "2. VALIDATING\nПеревірка guard-умов\n(заряд, сенсори)", size=11, fill="#eff6ff", stroke=NEG, min_w=135)
    frags.append(b2)

    b3, _, _ = textbox(430, 80, "3. ACTIVE\nВиконання цілі:\nуставки на приводи", size=11, fill="#f0fdf4", stroke=FIELD, min_w=135)
    frags.append(b3)

    b4, _, _ = textbox(615, 80, "4. MONITORING\nПеревірка критерію\nзавершення / часу", size=11, fill="#fef3c7", stroke="#d97706", min_w=135)
    frags.append(b4)

    b5, _, _ = textbox(755, 80, "5. DONE\nЗняття цілі,\nнаступна", size=11, fill="#f0fdf4", stroke=FIELD, min_w=80)
    frags.append(b5)

    # Стрілки нормального потоку
    frags.append(arrow(145, 80, 180, 80, color=LINE, sw=1.5))
    frags.append(arrow(320, 80, 360, 80, color=LINE, sw=1.5))
    frags.append(arrow(500, 80, 545, 80, color=LINE, sw=1.5))
    frags.append(arrow(685, 80, 712, 80, color=LINE, sw=1.5))

    # Нижній рівень: аварійне скидання
    frags.append(rect(140, 200, 540, 150, fill="#fef2f2", stroke=POS, sw=2, rx=8))
    frags.append(text(410, 226, "ПРОТОКОЛ АВАРІЙНОГО СКИДАННЯ (EMERGENCY ABORT)", size=13, bold=True, color=POS))
    frags.append(text(410, 252, "1. Негайне знеструмлення або активне гальмування приводів (Zero Setpoint)", size=11, anchor="middle", color="#7f1d1d"))
    frags.append(text(410, 276, "2. Виклик деструктора поточної активної цілі: goal.on_abort() (паркування, скид)", size=11, anchor="middle", color="#7f1d1d"))
    frags.append(text(410, 300, "3. Атомарне очищення черги: goal_queue_clear() — видалення всіх кроків", size=11, anchor="middle", color="#7f1d1d"))
    frags.append(text(410, 324, "4. Генерація події EV_ABORTED_TO_FAILSAFE для переведення HSM в аварійний стан", size=11, anchor="middle", color="#7f1d1d"))

    # Червоні стрілки скидання
    frags.append(arrow(430, 125, 430, 198, color=POS, sw=2))
    frags.append(text(440, 160, "Критичний збій", size=10, color=POS, bold=True, anchor="start"))

    frags.append(arrow(250, 125, 250, 198, color=POS, sw=1.6))
    frags.append(text(240, 160, "Guard-відмова", size=10, color=POS, anchor="end"))

    render(os.path.join(IMG_DIR, "goal-lifecycle-abort.svg"), w, h, *frags)


def main():
    fig_architecture_layers()
    fig_hsm_hierarchy()
    fig_superloop_timing()
    fig_goal_lifecycle()
    print("All figures successfully generated in %s" % IMG_DIR)


if __name__ == "__main__":
    main()
