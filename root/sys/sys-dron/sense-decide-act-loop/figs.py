#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми sense-decide-act-loop.
Вивід у ./img/
"""

import sys
import os

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_loop_timing_hierarchy():
    """Фігура 1: Ієрархія частот та розподіл контурів керування між Companion та FCU."""
    w, h = 860, 430
    elements = []

    # Фон
    elements.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))

    # Зона 1: Companion Computer (Soft Real-Time)
    elements.append(rect(20, 20, 820, 100, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    elements.append(text(40, 42, "Бортовий комп'ютер (Companion Computer, Linux / ROS 2) — Soft Real-Time (20–50 Гц)", 
                         size=13, color="#1e293b", bold=True, anchor="start"))
    
    # Модулі компаньйона
    b_cam, _, _ = textbox(120, 80, "Сенсори одометрії\n(Stereo, LiDAR, VIO)", size=11, pad=6, fill=FILL, stroke=LINE, min_w=140)
    elements.append(b_cam)

    elements.append(arrow(195, 80, 235, 80, color=LINE, sw=1.5))

    b_slam, _, _ = textbox(320, 80, "SLAM та навігація\n(Локалізація карти)", size=11, pad=6, fill=FILL, stroke=LINE, min_w=150)
    elements.append(b_slam)

    elements.append(arrow(400, 80, 430, 80, color=LINE, sw=1.5))

    b_plan, _, _ = textbox(525, 80, "Планувальник шляху\n(Trajectory Generation)", size=11, pad=6, fill=FILL, stroke=LINE, min_w=165)
    elements.append(b_plan)

    elements.append(arrow(610, 80, 640, 80, color=LINE, sw=1.5))

    b_node, _, _ = textbox(725, 80, "Offboard-вузол\n(Rate Matcher & WD)", size=11, pad=6, fill="#e0f2fe", stroke="#0284c7", min_w=150)
    elements.append(b_node)

    # Канал зв'язку (Шина між Companion та FCU)
    elements.append(rect(180, 150, 500, 36, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6))
    elements.append(text(430, 172, "UART (921.6k–3M baud) / Ethernet IP — MAVLink (#84) або Micro-XRCE-DDS", 
                         size=11, color="#92400e", bold=True))

    # Стрілки обміну
    elements.append(arrow(750, 120, 750, 150, color="#0284c7", sw=1.8))
    elements.append(text(760, 137, "Сетпоінти 20–50 Гц", size=10, color="#0284c7", bold=True, anchor="start"))

    elements.append(arrow(95, 150, 95, 120, color="#475569", sw=1.8))
    elements.append(text(90, 137, "Стан/Одометрія", size=10, color="#475569", anchor="end"))

    # Зона 2: Flight Controller (Hard Real-Time)
    elements.append(rect(20, 205, 820, 205, fill="#f1f5f9", stroke="#334155", sw=1.5, rx=8))
    elements.append(text(40, 228, "Польотний контролер (FCU, RTOS NuttX / STM32H7) — Hard Real-Time (100–1000 Гц)", 
                         size=13, color="#0f172a", bold=True, anchor="start"))

    # Підсистеми FCU
    b_fcu_rx, _, _ = textbox(120, 268, "Приймач команд та\nWatchdog (500 мс)", size=11, pad=6, fill="#fee2e2", stroke="#dc2626", min_w=150)
    elements.append(b_fcu_rx)

    elements.append(arrow(120, 186, 120, 245, color="#dc2626", sw=1.8))

    b_pos, _, _ = textbox(320, 260, "Контур позиції\n(50–100 Гц, PID)", size=11, pad=6, fill=FILL, stroke=LINE, min_w=140)
    elements.append(b_pos)

    elements.append(arrow(200, 260, 245, 260, color=LINE, sw=1.5))

    b_att, _, _ = textbox(510, 260, "Контур орієнтації\n(250–500 Гц, Quat)", size=11, pad=6, fill=FILL, stroke=LINE, min_w=145)
    elements.append(b_att)

    elements.append(arrow(395, 260, 430, 260, color=LINE, sw=1.5))

    b_rate, _, _ = textbox(700, 260, "Контур кутових шв.\n(400–1000 Гц, Rates)", size=11, pad=6, fill=FILL, stroke=LINE, min_w=155)
    elements.append(b_rate)

    elements.append(arrow(585, 260, 615, 260, color=LINE, sw=1.5))

    # Нижній рівень FCU: EKF2, Actuator Allocation, Мотори
    b_ekf, _, _ = textbox(225, 350, "Оцінка стану (EKF2, 100–250 Гц)\nIMU + Барометр + GNSS/VIO", 
                          size=11, pad=6, fill="#e2e8f0", stroke="#475569", min_w=230)
    elements.append(b_ekf)

    elements.append(arrow(345, 350, 430, 350, color=LINE, sw=1.5))

    b_alloc, _, _ = textbox(540, 350, "Actuator Allocation & Mixer\n(DShot 600 / PWM 1–8 кГц)", 
                            size=11, pad=6, fill="#e2e8f0", stroke="#475569", min_w=210)
    elements.append(b_alloc)

    elements.append(arrow(650, 350, 715, 350, color=LINE, sw=1.5))

    b_esc, _, _ = textbox(760, 350, "ESC / Мотори\n(Тяга)", size=10, pad=5, fill="#fef08a", stroke="#ca8a04", min_w=85)
    elements.append(b_esc)

    # Зворотний зв'язок EKF2 -> Контури
    elements.append(arrow(225, 320, 225, 290, color="#475569", sw=1.5))
    elements.append(arrow(700, 290, 590, 325, color=LINE, sw=1.5))

    # Збірка SVG
    defs = '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="#333333"/></marker></defs>'
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n%s\n%s\n</svg>'
           % (w, h, w, h, defs, "\n".join(elements)))

    path = os.path.join(IMG_DIR, 'loop-timing-hierarchy.svg')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f"Згенеровано: {path}")


def fig_failsafe_watchdog_timeline():
    """Фігура 2: Часова діаграма таймауту Offboard і спрацьовування Watchdog Failsafe."""
    w, h = 840, 300
    elements = []

    elements.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))

    # Заголовок осі часу
    elements.append(text(40, 30, "Часова шкала потоку команд Offboard та реакція Watchdog FCU", 
                         size=13, color=INK, bold=True, anchor="start"))

    # Вісь часу
    elements.append(arrow(50, 80, 780, 80, color=LINE, sw=2.0))
    elements.append(text(795, 85, "t (час)", size=12, color=INK, bold=True))

    # Позначки часу
    times = [
        (80, "0 мс", "Пакет #1"),
        (160, "50 мс", "Пакет #2"),
        (240, "100 мс", "Пакет #3"),
        (320, "150 мс", "Пакет #4"),
        (400, "200 мс", "Пакет #5 (Останній!)"),
    ]
    for x, label_t, label_p in times:
        elements.append(line(x, 72, x, 88, color=LINE, sw=2))
        elements.append(circle(x, 80, 5, fill="#0284c7", stroke="#0369a1", sw=1.5))
        elements.append(text(x, 62, label_p, size=10, color="#0284c7", bold=True))
        elements.append(text(x, 105, label_t, size=10, color=MUTED))

    # Зона нормальної роботи (Offboard Mode Active)
    elements.append(rect(70, 125, 340, 32, fill="#dcfce7", stroke="#16a34a", sw=1.5, rx=4))
    elements.append(text(240, 145, "Режим OFFBOARD активний (інтервал Δt = 50 мс < 500 мс)", size=11, color="#15803d", bold=True))

    # Вікно очікування таймера 500 мс
    elements.append(rect(400, 170, 240, 35, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=4))
    elements.append(text(520, 192, "Таймаут втрати зв'язку: COM_OF_LOSS_T = 500 мс", size=10, color="#b45309", bold=True))

    # Пунктир очікування на осі часу
    elements.append(line(400, 80, 640, 80, color="#dc2626", sw=3, dash="4,4"))

    # Позначка зависання компаньйона
    elements.append(text(460, 48, "Зависання VIO / сплеск CPU", size=10, color="#b91c1c", bold=True))
    elements.append(arrow(460, 55, 460, 75, color="#b91c1c", sw=1.5))

    # Точка спрацьовування Failsafe (t = 700 мс = 200 + 500)
    fs_x = 640
    elements.append(line(fs_x, 65, fs_x, 95, color="#dc2626", sw=2.5))
    elements.append(circle(fs_x, 80, 7, fill="#ef4444", stroke="#991b1b", sw=2))
    elements.append(text(fs_x, 50, "FAILSAFE TRIGGER", size=11, color="#b91c1c", bold=True))
    elements.append(text(fs_x, 105, "t = 700 мс", size=10, color="#b91c1c", bold=True))

    # Зона аварійного режиму (Failsafe Action)
    elements.append(rect(640, 125, 170, 55, fill="#fee2e2", stroke="#dc2626", sw=1.5, rx=4))
    elements.append(text(725, 145, "Аварійне перемикання:", size=10, color="#991b1b", bold=True))
    elements.append(text(725, 165, "HOLD / RTL / LAND", size=11, color="#991b1b", bold=True))

    # Пояснення внизу
    elements.append(text(420, 255, "FCU вимагає безперервного потоку сетпоінтів: якщо пауза перевищує 500 мс,", size=11, color=INK))
    elements.append(text(420, 275, "автопілот миттєво перехоплює керування, не дозволяючи дрону летіти за застарілим вектором.", size=11, color=INK, italic=True))

    defs = '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="#333333"/></marker></defs>'
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n%s\n%s\n</svg>'
           % (w, h, w, h, defs, "\n".join(elements)))

    path = os.path.join(IMG_DIR, 'failsafe-watchdog-timeline.svg')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f"Згенеровано: {path}")


def fig_feedforward_interpolation():
    """Фігура 3: Порівняння ступінчастого сетпоінта позиції та комбінованого Feed-Forward керування."""
    w, h = 840, 360
    elements = []

    elements.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))

    # Ліва колонка: Лише позиція (Сходинки та сплески)
    elements.append(rect(20, 20, 385, 320, fill="#fff1f2", stroke="#f43f5e", sw=1.5, rx=8))
    elements.append(text(212, 45, "Керування лише позицією (Position Only)", size=12, color="#9f1239", bold=True))
    elements.append(text(212, 65, "Сетпоінт 20 Гц без швидкості -> Ривки PID на 100 Гц", size=10, color="#be123c"))

    # Графік 1: Сходинки позиції
    elements.append(line(45, 140, 380, 140, color="#94a3b8", sw=1))
    elements.append(line(45, 80, 45, 150, color="#94a3b8", sw=1))
    elements.append(text(40, 85, "x", size=11, color="#64748b", bold=True))
    elements.append(text(375, 152, "t", size=10, color="#64748b"))

    # Сходинки
    pts_step = [(45, 135), (105, 135), (105, 115), (175, 115), (175, 95), (245, 95), (245, 80), (320, 80)]
    for i in range(len(pts_step)-1):
        elements.append(line(pts_step[i][0], pts_step[i][1], pts_step[i+1][0], pts_step[i+1][1], color="#e11d48", sw=2))
    for x, y in [(105, 115), (175, 95), (245, 80)]:
        elements.append(circle(x, y, 4, fill="#e11d48", stroke="#9f1239", sw=1))

    elements.append(text(212, 160, "Дискретні стрибки позиції кожні 50 мс", size=10, color="#9f1239"))

    # Графік 2: Сплески похідної (швидкості/моменту)
    elements.append(line(45, 250, 380, 250, color="#94a3b8", sw=1))
    elements.append(line(45, 185, 45, 260, color="#94a3b8", sw=1))
    elements.append(text(40, 190, "v, τ", size=11, color="#64748b", bold=True))

    # Імпульсні сплески
    spikes = [(105, 200), (175, 200), (245, 200)]
    for sx, sy in spikes:
        elements.append(line(sx-10, 250, sx, sy, color="#be123c", sw=2))
        elements.append(line(sx, sy, sx+10, 250, color="#be123c", sw=2))
        elements.append(circle(sx, sy, 3, fill="#be123c", stroke="none"))

    elements.append(text(212, 280, "Сплески D-терма -> вібрації моторів та перегрів ESC", size=10, color="#9f1239", bold=True))
    elements.append(text(212, 305, "Постійне відставання через затримку інтегратора", size=10, color="#881337", italic=True))

    # Права колонка: Комбінований сетпоінт (Feed-Forward)
    elements.append(rect(435, 20, 385, 320, fill="#f0fdf4", stroke="#22c55e", sw=1.5, rx=8))
    elements.append(text(627, 45, "Комбінований Feed-Forward (Pos + Vel + Accel)", size=12, color="#166534", bold=True))
    elements.append(text(627, 65, "Сетпоінт 20 Гц + вектор швидкості -> Гладка інтеграція", size=10, color="#15803d"))

    # Графік 3: Гладка траєкторія позиції
    elements.append(line(460, 140, 795, 140, color="#94a3b8", sw=1))
    elements.append(line(460, 80, 460, 150, color="#94a3b8", sw=1))
    elements.append(text(455, 85, "x", size=11, color="#64748b", bold=True))
    elements.append(text(790, 152, "t", size=10, color="#64748b"))

    # Гладка крива
    path_smooth = "M 460 135 C 520 135, 540 115, 600 105 C 660 95, 700 80, 770 80"
    elements.append(f'<path d="{path_smooth}" fill="none" stroke="#16a34a" stroke-width="2.5"/>')
    for x, y in [(520, 125), (600, 105), (680, 88)]:
        elements.append(circle(x, y, 4, fill="#16a34a", stroke="#14532d", sw=1))

    elements.append(text(627, 160, "Неперервна екстраполяція між точками 20 Гц", size=10, color="#166534"))

    # Графік 4: Гладкий профіль швидкості та керування
    elements.append(line(460, 250, 795, 250, color="#94a3b8", sw=1))
    elements.append(line(460, 185, 460, 260, color="#94a3b8", sw=1))
    elements.append(text(455, 190, "v, τ", size=11, color="#64748b", bold=True))

    path_v = "M 460 250 Q 550 205, 640 215 T 770 250"
    elements.append(f'<path d="{path_v}" fill="none" stroke="#15803d" stroke-width="2"/>')

    elements.append(text(627, 280, "Пряме введення швидкості (Feed-Forward Gain)", size=10, color="#166534", bold=True))
    elements.append(text(627, 305, "Мінімальна помилка стеження, відсутність ударів по моторах", size=10, color="#14532d", italic=True))

    defs = '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="#333333"/></marker></defs>'
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n%s\n%s\n</svg>'
           % (w, h, w, h, defs, "\n".join(elements)))

    path = os.path.join(IMG_DIR, 'feedforward-interpolation.svg')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f"Згенеровано: {path}")


if __name__ == '__main__':
    fig_loop_timing_hierarchy()
    fig_failsafe_watchdog_timeline()
    fig_feedforward_interpolation()
