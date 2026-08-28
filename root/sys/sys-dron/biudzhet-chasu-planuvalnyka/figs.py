#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми biudzhet-chasu-planuvalnyka.
Вивід у ./img/
"""

import sys
import os

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_planning_latency_braking():
    """Фігура 1: Структура затримки реакції та розрахунок гальмівної дистанції."""
    w, h = 880, 410
    elements = []

    # Заголовок секції 1: Часова шкала
    elements.append(text(440, 26, "Часовий ланцюг затримки планувальника (t_latency = 90 мс)", size=14, color=INK, bold=True))

    x0 = 50
    w_sens = int(30 * 8.2)   # 246 px
    w_comp = int(40 * 8.2)   # 328 px
    w_comm = int(5 * 8.2)    # 41 px
    w_act = 740 - (w_sens + w_comp + w_comm) # 125 px

    y_bar = 52
    h_bar = 56

    # 1. Sensing
    elements.append(rect(x0, y_bar, w_sens, h_bar, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=4))
    elements.append(text(x0 + w_sens / 2, y_bar + 24, "1. Збір сенсорів (Sense)", size=12, color="#0369a1", bold=True))
    elements.append(text(x0 + w_sens / 2, y_bar + 44, "LiDAR / VIO / Карта (30 мс)", size=11, color="#0369a1"))

    # 2. Compute
    x_comp = x0 + w_sens
    elements.append(rect(x_comp, y_bar, w_comp, h_bar, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=4))
    elements.append(text(x_comp + w_comp / 2, y_bar + 24, "2. Обчислення траєкторії (Compute)", size=12, color="#b45309", bold=True))
    elements.append(text(x_comp + w_comp / 2, y_bar + 44, "Anytime-планувальник: SFC + QP (40 мс)", size=11, color="#b45309"))

    # 3. Comm
    x_comm = x_comp + w_comp
    elements.append(rect(x_comm, y_bar, w_comm, h_bar, fill="#f3e8ff", stroke="#9333ea", sw=1.5, rx=4))
    elements.append(text(x_comm + w_comm / 2, y_bar + 24, "3. Шина", size=10, color="#7e22ce", bold=True))
    elements.append(text(x_comm + w_comm / 2, y_bar + 44, "5 мс", size=10, color="#7e22ce"))

    # 4. Actuation
    x_act = x_comm + w_comm
    elements.append(rect(x_act, y_bar, w_act, h_bar, fill="#fee2e2", stroke="#dc2626", sw=1.5, rx=4))
    elements.append(text(x_act + w_act / 2, y_bar + 24, "4. Приводи (Act)", size=12, color="#b91c1c", bold=True))
    elements.append(text(x_act + w_act / 2, y_bar + 44, "PID + ESC (15 мс)", size=11, color="#b91c1c"))

    # Загальна фігурна дужка / лінія затримки
    elements.append(line(x0, y_bar + h_bar + 10, x0 + 740, y_bar + h_bar + 10, color=LINE, sw=1.5))
    elements.append(line(x0, y_bar + h_bar + 5, x0, y_bar + h_bar + 15, color=LINE, sw=1.5))
    elements.append(line(x0 + 740, y_bar + h_bar + 5, x0 + 740, y_bar + h_bar + 15, color=LINE, sw=1.5))
    elements.append(text(420, y_bar + h_bar + 28, "Повна затримка ланцюга реагування: t_latency = 90 мс (0.090 с)", size=12, color=INK, bold=True))

    # Розділювач
    elements.append(line(30, 160, 850, 160, color="#e5e7eb", sw=1.2))

    # Заголовок секції 2: Просторова шкала
    elements.append(text(440, 185, "Просторова діаграма гальмування при польоті на v₀ = 10 м/с (a_max = 5 м/с²)", size=13, color=INK, bold=True))

    x_s0 = 50
    scale_m = 55.0 # px per meter

    d_react = 0.90   # м
    d_brake = 10.00  # м
    d_stop = 10.90   # м
    d_sensor = 12.00 # м

    w_s_react = d_react * scale_m # 49.5 px
    w_s_brake = d_brake * scale_m # 550.0 px
    w_s_margin = (d_sensor - d_stop) * scale_m # 60.5 px

    y_sp = 214
    h_sp = 48

    # 1. Реакція (сліпий проліт)
    elements.append(rect(x_s0, y_sp, w_s_react, h_sp, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    elements.append(text(x_s0 + w_s_react / 2, y_sp - 8, "d_react = 0.9 м", size=10, color=POS, bold=True))
    elements.append(text(x_s0 + w_s_react / 2, y_sp + 28, "Політ v₀", size=10, color=POS, bold=True))

    # 2. Активне гальмування
    x_s_br = x_s0 + w_s_react
    elements.append(rect(x_s_br, y_sp, w_s_brake, h_sp, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=3))
    elements.append(text(x_s_br + w_s_brake / 2, y_sp + 22, "Активне гальмування: d_brake = v₀² / (2 · a_max) = 10.0 м", size=12, color="#92400e", bold=True))
    elements.append(text(x_s_br + w_s_brake / 2, y_sp + 39, "Час гальмування: t_brake = v₀ / a_max = 2.0 с", size=11, color="#92400e"))

    # 3. Запас безпеки
    x_s_mg = x_s_br + w_s_brake
    elements.append(rect(x_s_mg, y_sp, w_s_margin, h_sp, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=3))
    elements.append(text(x_s_mg + w_s_margin / 2, y_sp - 8, "Запас: 1.1 м", size=10, color=FIELD, bold=True))
    elements.append(text(x_s_mg + w_s_margin / 2, y_sp + 28, "Безпека", size=10, color=FIELD, bold=True))

    # Перешкода праворуч: ширина 90 px, щоб напис вільно поміщався
    x_obs = x_s_mg + w_s_margin
    elements.append(rect(x_obs, y_sp - 15, 96, h_sp + 30, fill="#374151", stroke="#111827", sw=1.8, rx=4))
    elements.append(text(x_obs + 48, y_sp + 28, "ПЕРЕШКОДА", size=11, color="#f9fafb", bold=True, anchor="middle"))

    # Лінія повної зупинки
    elements.append(line(x_s0, y_sp + h_sp + 14, x_s_mg, y_sp + h_sp + 14, color=POS, sw=2.0))
    elements.append(line(x_s0, y_sp + h_sp + 8, x_s0, y_sp + h_sp + 20, color=POS, sw=2.0))
    elements.append(line(x_s_mg, y_sp + h_sp + 8, x_s_mg, y_sp + h_sp + 20, color=POS, sw=2.0))
    elements.append(text((x_s0 + x_s_mg) / 2, y_sp + h_sp + 32, "Повна дистанція зупинки: d_stop = d_react + d_brake = 10.9 м", size=12, color=POS, bold=True))

    # Сенсорний горизонт
    elements.append(line(x_s0, y_sp + h_sp + 52, x_obs, y_sp + h_sp + 52, color=NEG, sw=1.6, dash="5,4"))
    elements.append(line(x_s0, y_sp + h_sp + 46, x_s0, y_sp + h_sp + 58, color=NEG, sw=1.6))
    elements.append(line(x_obs, y_sp + h_sp + 46, x_obs, y_sp + h_sp + 58, color=NEG, sw=1.6))
    elements.append(text((x_s0 + x_obs) / 2, y_sp + h_sp + 70, "Горизонт сенсора (LiDAR / Stereo): d_sensor = 12.0 м", size=12, color=NEG, bold=True))

    path = os.path.join(IMG_DIR, 'planning-latency-braking.svg')
    render(path, w, h, *elements)
    print(f"Generated {path}")


def fig_multirate_planning_hierarchy():
    """Фігура 2: Багаторівнева ієрархія планування та контурів стабілізації за частотами."""
    w, h = 880, 440
    elements = []

    elements.append(text(440, 24, "Багаторівнева каскадна ієрархія планування та керування за частотами", size=14, color=INK, bold=True))

    # 4 рівні
    # Зсуваємо вправо: x = 110, w = 680
    x_box = 110
    w_box = 680

    y4 = 48
    h4 = 66
    elements.append(rect(x_box, y4, w_box, h4, fill="#f8fafc", stroke="#64748b", sw=1.6, rx=6))
    elements.append(text(x_box + 140, y4 + 24, "Рівень 4: Глобальний оптимізатор місії", size=13, color="#1e293b", bold=True))
    elements.append(text(x_box + 140, y4 + 48, "Частота: 0.5–2 Гц  |  Горизонт: 100–5000 м  |  Граф, A*, RRT", size=11, color="#475569"))
    elements.append(text(x_box + 530, y4 + 24, "Вихід: Опорні вейпоінти", size=12, color="#0f766e", bold=True))
    elements.append(text(x_box + 530, y4 + 48, "Soft Real-Time (Linux CPU)", size=11, color="#64748b"))

    # Стрілка 4 -> 3
    elements.append(arrow(x_box + 340, y4 + h4, x_box + 340, y4 + h4 + 20, color=LINE, sw=1.6))
    elements.append(text(x_box + 410, y4 + h4 + 14, "Коридор цілей", size=10, color=MUTED, bold=True))

    y3 = 138
    h3 = 76
    elements.append(rect(x_box, y3, w_box, h3, fill="#fef3c7", stroke="#d97706", sw=1.8, rx=6))
    elements.append(text(x_box + 140, y3 + 24, "Рівень 3: Локальний Anytime-планувальник", size=13, color="#92400e", bold=True))
    elements.append(text(x_box + 140, y3 + 46, "Частота: 10–20 Гц  |  Квант часу: 40–80 мс  |  Горизонт: 2–5 с", size=11, color="#b45309"))
    elements.append(text(x_box + 140, y3 + 64, "SFC + QP оптимізація сплайна (поліноми 5-го степеня)", size=11, color="#78350f"))
    elements.append(text(x_box + 530, y3 + 24, "Вихід: Сплайн p(t), v(t), a(t)", size=12, color="#92400e", bold=True))
    elements.append(text(x_box + 530, y3 + 48, "Anytime Failsafe Fallback", size=11, color="#dc2626", bold=True))

    # Стрілка 3 -> 2
    elements.append(arrow(x_box + 340, y3 + h3, x_box + 340, y3 + h3 + 20, color=LINE, sw=1.6))
    elements.append(text(x_box + 415, y3 + h3 + 14, "Сетпоінти стану", size=10, color=MUTED, bold=True))

    y2 = 238
    h2 = 72
    elements.append(rect(x_box, y2, w_box, h2, fill="#e0f2fe", stroke="#0284c7", sw=1.6, rx=6))
    elements.append(text(x_box + 140, y2 + 24, "Рівень 2: Локальний трекер траєкторії SE(3)", size=13, color="#0369a1", bold=True))
    elements.append(text(x_box + 140, y2 + 46, "Частота: 50–100 Гц  |  Період: 10–20 мс", size=11, color="#0284c7"))
    elements.append(text(x_box + 140, y2 + 62, "Геометричний контролер положення + Feedforward", size=11, color="#075985"))
    elements.append(text(x_box + 530, y2 + 24, "Вихід: Кватерніон q_des, Тяга", size=12, color="#0369a1", bold=True))
    elements.append(text(x_box + 530, y2 + 48, "Hard RT / Companion or MCU", size=11, color="#64748b"))

    # Стрілка 2 -> 1
    elements.append(arrow(x_box + 340, y2 + h2, x_box + 340, y2 + h2 + 20, color=LINE, sw=1.6))
    elements.append(text(x_box + 420, y2 + h2 + 14, "Бажана орієнтація", size=10, color=MUTED, bold=True))

    y1 = 334
    h1_box = 72
    elements.append(rect(x_box, y1, w_box, h1_box, fill="#fee2e2", stroke=POS, sw=1.8, rx=6))
    elements.append(text(x_box + 140, y1 + 24, "Рівень 1: Внутрішній контур кутових швидкостей", size=13, color=POS, bold=True))
    elements.append(text(x_box + 140, y1 + 46, "Частота: 250–1000 Гц  |  Період: 1–4 мс  |  Джиттер < 10 мкс", size=11, color="#991b1b"))
    elements.append(text(x_box + 140, y1 + 62, "Швидкий каскадний PID моменту + мікшер моторів", size=11, color="#7f1d1d"))
    elements.append(text(x_box + 530, y1 + 24, "Вихід: DShot / PWM на ESC", size=12, color=POS, bold=True))
    elements.append(text(x_box + 530, y1 + 48, "Hard Real-Time (MCU RTOS)", size=11, color=POS, bold=True))

    # Бічний зв'язок: Watchdog перехоплення при перевищенні кванту часу
    # Розміщуємо акуратно ліворуч від блоків
    elements.append(line(55, y3 + 38, 55, y2 + 36, color=POS, sw=1.8, dash="4,3"))
    elements.append(line(x_box, y3 + 38, 55, y3 + 38, color=POS, sw=1.8, dash="4,3"))
    elements.append(arrow(55, y2 + 36, x_box - 2, y2 + 36, color=POS, sw=1.8))
    
    # Текстова плашка на лінії таймауту
    elements.append(rect(15, (y3 + y2) / 2 + 10, 80, 24, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    elements.append(text(55, (y3 + y2) / 2 + 26, "Таймаут", size=10, color=POS, bold=True, anchor="middle"))

    path = os.path.join(IMG_DIR, 'multirate-planning-hierarchy.svg')
    render(path, w, h, *elements)
    print(f"Generated {path}")


if __name__ == '__main__':
    fig_planning_latency_braking()
    fig_multirate_planning_hierarchy()
