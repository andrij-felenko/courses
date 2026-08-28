#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми povernennia-dodomu (sys-dron).
Вивід у ./img/
"""

import sys
import os

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_rtl_phases_profile():
    """Фігура 1: Вертикально-горизонтальний профіль фаз RTL."""
    w, h = 820, 360
    frags = []
    
    # Земля та рельєф
    frags.append(rect(0, 300, w, 60, fill="#e5e7eb", stroke=LINE, sw=1.5, rx=0))
    frags.append(text(70, 335, "Рівень землі (Home Z=0)", size=12, color=MUTED, bold=True))
    
    # Домашня точка (Home Pad)
    frags.append(rect(40, 292, 60, 8, fill=FIELD, stroke=LINE, sw=1.5, rx=2))
    frags.append(circle(70, 285, 6, fill="#ffffff", stroke=POS, sw=2))
    frags.append(text(70, 272, "База (Home)", size=11, color=POS, bold=True))
    
    # Перешкоди на шляху
    # Дерево (x=240, h=60)
    frags.append(rect(237, 240, 6, 60, fill="#8b5a2b", stroke="none", rx=1))
    frags.append(circle(240, 230, 22, fill="#a7f3d0", stroke="#059669", sw=1.5))
    frags.append(text(240, 290, "Ліс 15 м", size=10, color=MUTED))
    
    # Опора ЛЕП (x=450, h=100)
    frags.append(line(440, 300, 450, 190, color=LINE, sw=1.5))
    frags.append(line(460, 300, 450, 190, color=LINE, sw=1.5))
    frags.append(line(435, 210, 465, 210, color=LINE, sw=1.5))
    frags.append(line(430, 235, 470, 235, color=LINE, sw=1.5))
    frags.append(line(420, 210, 480, 210, color=POS, sw=1.2, dash="3,2"))
    frags.append(text(450, 180, "ЛЕП 25 м", size=10, color=POS, bold=True))
    
    # Лінія безпечної висоти RTL Altitude (h=50м -> Y=90)
    frags.append(line(30, 90, 790, 90, color=NEG, sw=1.5, dash="6,4"))
    frags.append(text(710, 80, "RTL Altitude (50 м)", size=12, color=NEG, bold=True))
    
    # Початкова точка спрацьовування failsafe (x=730, y=230)
    frags.append(circle(730, 230, 8, fill="#fee2e2", stroke=POS, sw=2))
    frags.append(text(730, 255, "Збій (Failsafe)", size=11, color=POS, bold=True))
    frags.append(text(730, 270, "Висота h=18 м", size=10, color=MUTED))
    
    # Траєкторія RTL
    # Фаза 1: Набір безпечної висоти (вертикально вгору)
    frags.append(arrow(730, 220, 730, 95, color=LINE, sw=2.5))
    b1, _, _ = textbox(730, 150, "1. CLIMB\nПідйом до\nRTL Alt", size=10, pad=5, fill="#eff6ff", stroke=NEG)
    frags.append(b1)
    
    # Фаза 2: Крейсерський політ до точки Home (по горизонталі)
    frags.append(arrow(720, 90, 85, 90, color=LINE, sw=2.5))
    b2, _, _ = textbox(360, 60, "2. TRANSIT / RETURN (Політ над перешкодами до бази)", 
                       size=11, pad=6, fill="#f0fdf4", stroke=FIELD, bold=True)
    frags.append(b2)
    
    # Фаза 3: Зависання та оптичне вирівнювання (Loiter / Align)
    frags.append(circle(70, 90, 7, fill="#fef3c7", stroke="#d97706", sw=2))
    b3, _, _ = textbox(165, 115, "3. ALIGN / HOVER\nЗависання й пошук мітки", 
                       size=10, pad=5, fill="#fef3c7", stroke="#d97706")
    frags.append(b3)
    
    # Фаза 4: Зниження з контролем оптичної посадки
    frags.append(arrow(70, 100, 70, 230, color=LINE, sw=2))
    b4, _, _ = textbox(150, 190, "4. PRECISION DESCENT\nЗниження 1.5 м/с -> 0.5 м/с", 
                       size=10, pad=5, fill="#faf5ff", stroke="#9333ea")
    frags.append(b4)
    
    # Фаза 5: Детект контакту з землею і дисарм
    frags.append(arrow(70, 235, 70, 280, color=POS, sw=2))
    b5, _, _ = textbox(145, 255, "5. TOUCHDOWN & DISARM\nЗупинка двигунів", 
                       size=10, pad=5, fill="#fee2e2", stroke=POS)
    frags.append(b5)
    
    render(os.path.join(IMG_DIR, "rtl-phases-profile.svg"), w, h, *frags, 
           title="Фази автономного повернення додому (RTL Profile)")


def fig_reverse_path_vs_direct():
    """Фігура 2: Порівняння Direct Vector проти Reverse Path."""
    w, h = 820, 340
    frags = []
    
    # Ліва половина: Прямий вектор (Direct Vector)
    frags.append(rect(15, 15, 385, 310, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(207, 42, "Direct Vector (Прямий вектор)", size=14, color=POS, bold=True))
    
    # База
    frags.append(circle(60, 280, 8, fill=FIELD, stroke=LINE, sw=2))
    frags.append(text(60, 305, "База (Home)", size=11, color=INK, bold=True))
    
    # Перешкода (гора / забудова / зона РЕБ)
    frags.append(rect(140, 110, 120, 120, fill="#fee2e2", stroke=POS, sw=1.8, rx=6))
    frags.append(mtext(200, 160, ["Висотна забудова /", "гора / зона РЕБ"], size=11, color=POS, bold=True))
    
    # Точка збою
    frags.append(circle(340, 90, 8, fill="#fee2e2", stroke=POS, sw=2))
    frags.append(text(340, 70, "Точка відмови", size=11, color=POS, bold=True))
    
    # Пряма лінія повернення — зіткнення
    frags.append(line(335, 95, 65, 275, color=POS, sw=2.5, dash="6,3"))
    frags.append(circle(200, 185, 14, fill="#ffffff", stroke=POS, sw=2.5))
    frags.append(text(200, 190, "X", size=16, color=POS, bold=True))
    frags.append(text(200, 245, "Аварійне зіткнення!", size=12, color=POS, bold=True))
    
    # Права половина: Відкат по траєкторії (Reverse Path / Breadcrumbs)
    frags.append(rect(420, 15, 385, 310, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(612, 42, "Reverse Path (Відкат маршруту)", size=14, color=FIELD, bold=True))
    
    # База
    frags.append(circle(465, 280, 8, fill=FIELD, stroke=LINE, sw=2))
    frags.append(text(465, 305, "База (Home)", size=11, color=INK, bold=True))
    
    # Перешкода
    frags.append(rect(545, 110, 120, 120, fill="#fee2e2", stroke=POS, sw=1.8, rx=6))
    frags.append(mtext(605, 160, ["Висотна забудова /", "гора / зона РЕБ"], size=11, color=POS, bold=True))
    
    # Точка збою
    frags.append(circle(745, 90, 8, fill="#fee2e2", stroke=POS, sw=2))
    frags.append(text(745, 70, "Точка відмови", size=11, color=POS, bold=True))
    
    # Крихти хліба / точки виходу
    # WP1: (740, 250), WP2: (610, 270)
    frags.append(circle(745, 250, 6, fill="#bfdbfe", stroke=NEG, sw=1.5))
    frags.append(circle(605, 275, 6, fill="#bfdbfe", stroke=NEG, sw=1.5))
    
    # Стрілки руху вперед (бліді)
    frags.append(line(470, 280, 595, 275, color=MUTED, sw=1.2, dash="3,3"))
    frags.append(line(615, 275, 745, 250, color=MUTED, sw=1.2, dash="3,3"))
    frags.append(line(745, 245, 745, 100, color=MUTED, sw=1.2, dash="3,3"))
    
    # Стрілки відкату назад (зелені, чіткі)
    frags.append(arrow(745, 98, 745, 240, color=FIELD, sw=2.2))
    frags.append(arrow(740, 252, 615, 273, color=FIELD, sw=2.2))
    frags.append(arrow(595, 275, 475, 280, color=FIELD, sw=2.2))
    
    frags.append(text(612, 70, "Безпечний коридор місії", size=11, color=FIELD, bold=True))
    frags.append(text(612, 245, "Рух за збереженими крихтами", size=11, color=INK))
    
    render(os.path.join(IMG_DIR, "reverse-path-vs-direct.svg"), w, h, *frags,
           title="Стратегії повернення: прямий вектор проти безпечного відкату")


def fig_precision_landing_optics():
    """Фігура 3: Оптичне наведення та прецизійна посадка."""
    w, h = 820, 340
    frags = []
    
    # Корпус дрона
    frags.append(rect(340, 40, 140, 26, fill=FILL, stroke=LINE, sw=1.8, rx=4))
    frags.append(circle(320, 48, 14, fill="#e2e8f0", stroke=LINE, sw=1.5))
    frags.append(circle(500, 48, 14, fill="#e2e8f0", stroke=LINE, sw=1.5))
    frags.append(text(410, 58, "Дрон (RTL Align)", size=12, color=INK, bold=True))
    
    # Камера спрямована вниз
    frags.append(rect(400, 66, 20, 14, fill="#1e293b", stroke=LINE, sw=1.5, rx=2))
    frags.append(text(410, 95, "Оптична камера (Down-facing)", size=10, color=MUTED))
    
    # Поле зору камери (FOV cone)
    frags.append(line(405, 80, 160, 290, color=NEG, sw=1.5, dash="5,4"))
    frags.append(line(415, 80, 660, 290, color=NEG, sw=1.5, dash="5,4"))
    
    # Рівень посадкового майданчика
    frags.append(line(50, 290, 770, 290, color=LINE, sw=2))
    
    # Посадкова мітка (AprilTag / ArUco) зі зміщенням
    frags.append(rect(300, 282, 60, 16, fill="#0f172a", stroke=LINE, sw=1.5, rx=2))
    frags.append(rect(312, 285, 12, 10, fill="#ffffff", stroke="none", rx=1))
    frags.append(rect(336, 285, 12, 10, fill="#ffffff", stroke="none", rx=1))
    frags.append(text(330, 315, "Landing Target (AprilTag / ArUco)", size=11, color=INK, bold=True))
    
    # Проекція оптичної осі дрона
    frags.append(line(410, 80, 410, 290, color=MUTED, sw=1.2, dash="3,3"))
    frags.append(circle(410, 290, 4, fill=POS, stroke=POS))
    frags.append(text(410, 315, "Поточний центр дрона", size=10, color=POS))
    
    # Вектор похибки позиціювання ΔX, ΔY
    frags.append(arrow(410, 260, 335, 260, color=POS, sw=2))
    frags.append(text(372, 250, "Похибка ΔX (Offset)", size=11, color=POS, bold=True))
    
    # Блок алгоритму праворуч
    frags.append(rect(540, 100, 260, 160, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(670, 122, "Контур Precision Landing", size=12, color=INK, bold=True))
    frags.append(mtext(670, 150, [
        "1. Детекція кутів мітки у кадрі",
        "2. PnP-розв'язок: [X, Y, Z, Yaw]rel",
        "3. Фільтр Калмана: компенсація шуму",
        "4. Корекція швидкості: V_xy = K_p · ΔP",
        "5. Зниження лише при |ΔP| < R_safe"
    ], size=10, color=INK, anchor="middle", lh=1.4))
    
    render(os.path.join(IMG_DIR, "precision-landing-optics.svg"), w, h, *frags,
           title="Оптичне наведення на посадковий майданчик (Precision Landing)")


def fig_wind_climb_energy_balance():
    """Фігура 4: Динаміка тяги проти вітру та захист від просідання."""
    w, h = 820, 320
    frags = []
    
    # Ліва схема: Вектори сил при зустрічному вітрі
    frags.append(rect(15, 15, 385, 290, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(207, 40, "Декомпозиція тяги при нахилі", size=13, color=INK, bold=True))
    
    # Дрон під кутом тангажу theta
    cx, cy = 180, 160
    frags.append(line(130, 190, 230, 130, color=LINE, sw=4)) # корпус
    frags.append(circle(130, 190, 8, fill="#cbd5e1", stroke=LINE, sw=1.5))
    frags.append(circle(230, 130, 8, fill="#cbd5e1", stroke=LINE, sw=1.5))
    
    # Вектор вітру (зустрічний, праворуч наліво)
    frags.append(arrow(360, 140, 260, 140, color=NEG, sw=2.5))
    frags.append(text(310, 125, "Зустрічний вітер V_wind", size=11, color=NEG, bold=True))
    
    # Повна тяга T (перпендикулярна до рами, вгору і вперед)
    frags.append(arrow(cx, cy, 220, 80, color=POS, sw=2.5))
    frags.append(text(240, 80, "Повна тяга T_max", size=11, color=POS, bold=True))
    
    # Вертикальна складова T_z = T * cos(theta)
    frags.append(arrow(cx, cy, cx, 80, color=FIELD, sw=2))
    frags.append(text(125, 95, "T_z = T · cos θ", size=11, color=FIELD, bold=True))
    
    # Горизонтальна складова T_xy = T * sin(theta)
    frags.append(arrow(cx, cy, 240, cy, color="#d97706", sw=2))
    frags.append(text(260, 180, "T_xy = T · sin θ", size=11, color="#d97706", bold=True))
    
    # Сила тяжіння m*g
    frags.append(arrow(cx, cy, cx, 250, color=LINE, sw=2.2))
    frags.append(text(195, 240, "Вага m · g", size=11, color=INK, bold=True))
    
    # Права схема: Пріоритет висоти над швидкістю (Altitude Priority Governor)
    frags.append(rect(420, 15, 385, 290, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(612, 40, "Захист від втрати висоти (Climb Priority)", size=13, color=POS, bold=True))
    
    # Блоки логіки
    b1, _, _ = textbox(612, 85, "Оцінка вертикальної швидкості: V_z < V_z_min?", 
                       size=11, pad=6, fill="#eff6ff", stroke=NEG, min_w=320)
    frags.append(b1)
    
    frags.append(arrow(612, 108, 612, 130, color=LINE, sw=1.8))
    
    b2, _, _ = textbox(612, 160, "Насичення газу (Throttle Saturation > 95%)\nДвигуни не можуть утримати висоту!", 
                       size=11, pad=6, fill="#fee2e2", stroke=POS, min_w=320, bold=True)
    frags.append(b2)
    
    frags.append(arrow(612, 192, 612, 215, color=LINE, sw=1.8))
    
    b3, _, _ = textbox(612, 250, "Автоматичне обмеження кута крену/тангажу:\nθ_max = arccos(m·g / T_avail) -> Зменшення V_xy\nПріоритет: збереження висоти ціною швидкості", 
                       size=11, pad=6, fill="#f0fdf4", stroke=FIELD, min_w=340)
    frags.append(b3)
    
    render(os.path.join(IMG_DIR, "wind-climb-energy-balance.svg"), w, h, *frags,
           title="Дефіцит тяги при сильному вітрі та алгоритм захисту висоти")


def main():
    fig_rtl_phases_profile()
    fig_reverse_path_vs_direct()
    fig_precision_landing_optics()
    fig_wind_climb_energy_balance()
    print("Всі SVG-фігури успішно згенеровано.")


if __name__ == "__main__":
    main()
