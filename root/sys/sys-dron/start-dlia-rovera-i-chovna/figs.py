#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми start-dlia-rovera-i-chovna.
Вивід у ./img/
"""

import sys
import os
import math

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_dock_exit_stages():
    """Фігура 1: П'ять фаз автомата виходу ровера з зарядної станції."""
    w, h = 820, 240
    elements = []
    
    stages = [
        ("1. Перевірка живлення", "Розрив силового реле\nV_sense ≈ 0 В\nI_charge < 50 мА", 20, 45, 140, 140, "#eff6ff", "#1d4ed8"),
        ("2. Зняття гальма", "Оцінка кута схилу α\nPre-Torque на моторах\nРозтискання колодок", 180, 45, 140, 140, "#fefce8", "#a16207"),
        ("3. Сліпий реверс", "Трапеція швидкості\nРух по рейках (0.1 м/с)\nТільки енкодери + IMU", 340, 45, 140, 140, "#f0fdf4", "#15803d"),
        ("4. Тест зчеплення", "Аналіз slip ratio s\nОцінка струму коліс\nПодолання порогу дока", 500, 45, 140, 140, "#faf5ff", "#7e22ce"),
        ("5. Вільна місія", "Валідація компаса\nНабір швидкості GNSS\nПерехід до Waypoints", 660, 45, 140, 140, "#f8fafc", "#334155"),
    ]
    
    for title_text, desc_text, x, y, bw, bh, bg_color, stroke_color in stages:
        elements.append(rect(x, y, bw, bh, fill=bg_color, stroke=stroke_color, sw=1.6, rx=6))
        elements.append(text(x + bw/2, y + 24, title_text, size=11, color=stroke_color, bold=True))
        elements.append(line(x + 10, y + 36, x + bw - 10, y + 36, color=stroke_color, sw=0.8))
        lines = desc_text.split("\n")
        for i, l in enumerate(lines):
            elements.append(text(x + bw/2, y + 62 + i * 24, l, size=10, color=INK))
            
    # Стрілки між блоками
    arrow_xs = [160, 320, 480, 640]
    for ax in arrow_xs:
        elements.append(arrow(ax + 2, 115, ax + 18, 115, color=LINE, sw=1.5))
        
    # Нижня часова вісь
    elements.append(line(30, 215, 790, 215, color=MUTED, sw=1.2))
    elements.append(arrow(780, 215, 795, 215, color=MUTED, sw=1.2))
    elements.append(text(410, 230, "Часовий прогрес процедури виходу з дока (дискретний FSM-контроль)", size=10, color=MUTED, italic=True))
    
    render(os.path.join(IMG_DIR, "dock-exit-stages.svg"), w, h, *elements)


def fig_unmooring_thrust_burst():
    """Фігура 2: Динаміка відчалювання катера (USV) при притискному вітрі біля причалу."""
    w, h = 820, 290
    elements = []
    
    # Причал (бетонна стінка) ліворуч
    elements.append(rect(20, 30, 70, 220, fill="#e2e8f0", stroke=LINE, sw=2, rx=2))
    elements.append(text(55, 140, "Бетонний пірс", size=11, color=INK, bold=True))
    
    # Відбійники (fenders) на пірсі
    for fy in [60, 110, 160, 210]:
        elements.append(rect(90, fy, 10, 25, fill="#334155", stroke=LINE, sw=1, rx=3))
        
    # Водна акваторія
    elements.append(rect(105, 30, 700, 220, fill="#f0f9ff", stroke="#bae6fd", sw=1.2, rx=4))
    elements.append(text(720, 50, "Акваторія", size=11, color="#0369a1", bold=True))
    
    # Вітер і хвилі — стрілки, що тиснуть до причалу
    elements.append(arrow(600, 75, 450, 75, color="#0284c7", sw=1.8))
    elements.append(arrow(580, 105, 430, 105, color="#0284c7", sw=1.8))
    elements.append(text(520, 63, "Притискний вітер F_wind", size=10, color="#0284c7", bold=True))
    
    # Траєкторія відчалювання
    # 1) Положення біля стінки
    elements.append(rect(115, 80, 55, 110, fill="#fed7aa", stroke="#c2410c", sw=1.5, rx=12))
    elements.append(text(142, 135, "USV у доку", size=9, color="#9a3412", bold=True))
    
    # 2) Фаза Bow Kick: поворот носа
    elements.append(arrow(170, 95, 230, 70, color=POS, sw=1.6))
    elements.append(text(215, 58, "1. Bow Kick (розпорка носа)", size=9, color=POS, bold=True))
    
    # 3) Фаза Thrust Burst
    elements.append(rect(280, 100, 60, 110, fill="#fef08a", stroke="#ca8a04", sw=1.5, rx=12))
    elements.append(text(310, 155, "Thrust Burst", size=9, color="#854d0e", bold=True))
    elements.append(arrow(340, 155, 430, 185, color="#b45309", sw=2))
    elements.append(text(410, 170, "2. Відхід від турбулентної стінки", size=9, color="#b45309", bold=True))
    
    # 4) Безпечна вільна вода
    elements.append(rect(520, 120, 60, 110, fill="#bbf7d0", stroke="#15803d", sw=1.5, rx=12))
    elements.append(text(550, 175, "Вільна вода", size=9, color="#166534", bold=True))
    elements.append(arrow(580, 175, 660, 175, color="#15803d", sw=2))
    elements.append(text(620, 160, "3. Вихід на курс", size=9, color="#15803d", bold=True))
    
    # Підпис знизу
    elements.append(text(410, 275, "Маневр активного відчалювання (Unmooring Thrust Burst) для подолання ефекту присмоктування стінки", size=11, color=INK, bold=False))
    
    render(os.path.join(IMG_DIR, "unmooring-thrust-burst.svg"), w, h, *elements)


def fig_traction_brake_release():
    """Фігура 3: Процедура старту ровера на похилій поверхні: Pre-Torque та зняття гальма."""
    w, h = 820, 270
    elements = []
    
    # Рамка графіків
    elements.append(rect(50, 30, 720, 205, fill="#f8fafc", stroke=LINE, sw=1.4, rx=6))
    
    # Осі координат
    elements.append(line(120, 200, 740, 200, color=LINE, sw=1.5))  # Вісь t
    elements.append(arrow(730, 200, 750, 200, color=LINE, sw=1.5))
    elements.append(text(755, 204, "t", size=12, color=INK, bold=True))
    
    elements.append(line(120, 200, 120, 45, color=LINE, sw=1.5))   # Вісь Y
    elements.append(arrow(120, 55, 120, 40, color=LINE, sw=1.5))
    elements.append(text(95, 45, "Сигнали", size=10, color=INK, bold=True))
    
    # Часові мітки
    elements.append(line(260, 45, 260, 200, color="#cbd5e1", sw=1, dash="4,4"))
    elements.append(text(260, 215, "t₁ (Pre-Torque)", size=10, color=MUTED))
    
    elements.append(line(420, 45, 420, 200, color="#cbd5e1", sw=1, dash="4,4"))
    elements.append(text(420, 215, "t₂ (Release Brake)", size=10, color=MUTED))
    
    elements.append(line(580, 45, 580, 200, color="#cbd5e1", sw=1, dash="4,4"))
    elements.append(text(580, 215, "t₃ (Drive Ramp)", size=10, color=MUTED))
    
    # Лінія 1: Гальмо (Червона лінія)
    elements.append(line(120, 75, 420, 75, color=POS, sw=2))
    elements.append(line(420, 75, 430, 185, color=POS, sw=2))
    elements.append(line(430, 185, 720, 185, color=POS, sw=2))
    elements.append(text(230, 67, "Стоянкове гальмо (Locked → Released)", size=10, color=POS, bold=True))
    
    # Лінія 2: Момент мотора M_m (Зелена лінія)
    elements.append(line(120, 185, 260, 185, color="#16a34a", sw=2.2))
    elements.append(line(260, 185, 420, 125, color="#16a34a", sw=2.2))
    elements.append(line(420, 125, 580, 95, color="#16a34a", sw=2.2))
    elements.append(line(580, 95, 720, 95, color="#16a34a", sw=2.2))
    elements.append(text(340, 115, "Момент тяги M_hold (Pre-Torque)", size=10, color="#16a34a", bold=True))
    
    # Лінія 3: Швидкість ровера (Синя лінія)
    elements.append(line(120, 185, 420, 185, color=NEG, sw=2, dash="6,3"))
    elements.append(line(420, 185, 580, 140, color=NEG, sw=2, dash="6,3"))
    elements.append(line(580, 140, 720, 140, color=NEG, sw=2, dash="6,3"))
    elements.append(text(600, 130, "Швидкість v (без відкату)", size=10, color=NEG, bold=True))
    
    # Підпис знизу
    elements.append(text(410, 255, "Запобігання скочуванню (Hill-Start Anti-Rollback): узгодження моменту мотора з розтисканням гальма", size=11, color=INK))
    
    render(os.path.join(IMG_DIR, "traction-brake-release.svg"), w, h, *elements)


def fig_sensor_heading_fusion():
    """Фігура 4: Еволюція довіри до сенсорів курсу: від магнітних спотворень дока до GNSS COG."""
    w, h = 820, 260
    elements = []
    
    # Три зони навігаційного середовища
    zones = [
        ("Зона 1: Док-термінал", "Металоконструкції, кабелі 50 А\nКомпас спотворений (похибка 60°)\nДжерело: Фіксований азимут дока", 30, 40, 230, 150, "#fee2e2", "#b91c1c"),
        ("Зона 2: Сліпий коридор", "Відрив від станції (0–2 м)\nНизька швидкість (< 0.2 м/с)\nДжерело: Wheel Encoders + Z-Gyro", 295, 40, 230, 150, "#fef3c7", "#d97706"),
        ("Зона 3: Вільний простір", "Відстань > 2 м, швидкість > 0.8 м/с\nМагнітне поле стабільне\nДжерело: EKF (GNSS COG + Mag + IMU)", 560, 40, 230, 150, "#dcfce7", "#15803d"),
    ]
    
    for title_text, desc_text, x, y, bw, bh, bg_color, stroke_color in zones:
        elements.append(rect(x, y, bw, bh, fill=bg_color, stroke=stroke_color, sw=1.6, rx=6))
        elements.append(text(x + bw/2, y + 25, title_text, size=11, color=stroke_color, bold=True))
        elements.append(line(x + 10, y + 38, x + bw - 10, y + 38, color=stroke_color, sw=0.8))
        lines = desc_text.split("\n")
        for i, l in enumerate(lines):
            elements.append(text(x + bw/2, y + 68 + i * 26, l, size=10, color=INK))
            
    # Стрілки переходу
    elements.append(arrow(265, 115, 290, 115, color=LINE, sw=1.6))
    elements.append(arrow(530, 115, 555, 115, color=LINE, sw=1.6))
    
    # Індикатор ваги сенсорів знизу
    elements.append(line(40, 215, 780, 215, color=MUTED, sw=1.2))
    elements.append(arrow(770, 215, 785, 215, color=MUTED, sw=1.2))
    elements.append(text(145, 235, "Магнітометр: 0% ваги", size=9, color="#b91c1c", bold=True))
    elements.append(text(410, 235, "Одометрія + Гіроскоп: 100% ваги", size=9, color="#d97706", bold=True))
    elements.append(text(675, 235, "Повний EKF + GNSS COG", size=9, color="#15803d", bold=True))
    
    render(os.path.join(IMG_DIR, "sensor-heading-fusion.svg"), w, h, *elements)


def main():
    fig_dock_exit_stages()
    fig_unmooring_thrust_burst()
    fig_traction_brake_release()
    fig_sensor_heading_fusion()
    print("Всі SVG-фігури згенеровано успішно.")


if __name__ == "__main__":
    main()
