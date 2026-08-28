#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми slipi-zony-i-khybne-halmuvannia.
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


def fig_blind_zones_tilt_yaw():
    """Фігура 1: Геометрія сліпих зон при нахилі корпусу (Pitch) та швидкому розвороті (Yaw)."""
    w, h = 860, 420
    elements = []

    # Тло
    elements.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))

    # Ліва панель: Динамічне затінення при нахилі корпусу на швидкості (Pitch)
    elements.append(rect(20, 20, 400, 380, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    elements.append(text(220, 45, "1. Затінення при нахилі корпусу (Pitch)", size=12, color="#0f172a", bold=True))
    elements.append(text(220, 65, "Швидкість vx = 10 м/с -> Нахил корпусу θ = 25°", size=10, color="#475569"))

    # Схема дрона під нахилом
    cx, cy = 125, 205
    
    # Горизонтальна лінія горизонту
    elements.append(line(50, cy, 390, cy, color="#cbd5e1", sw=1, dash="4,4"))
    elements.append(text(370, cy - 8, "Горизонт", size=10, color="#94a3b8", anchor="end"))

    # Тіло дрона під нахилом -25 градусів (ніс нахилений вниз праворуч)
    rad = math.radians(25)
    dx = 42 * math.cos(rad)
    dy = 42 * math.sin(rad)
    
    # Рама дрона
    elements.append(line(cx - dx, cy - dy, cx + dx, cy + dy, color="#1e293b", sw=4))
    # Пропелери
    elements.append(line(cx - dx - 14, cy - dy - 5, cx - dx + 14, cy - dy + 5, color="#0284c7", sw=2))
    elements.append(line(cx + dx - 14, cy + dy - 5, cx + dx + 14, cy + dy + 5, color="#0284c7", sw=2))
    # Сенсор на носі дрона
    sx, sy = cx + dx, cy + dy
    elements.append(circle(sx, sy, 5, fill="#ef4444", stroke="#991b1b", sw=1.5))
    elements.append(text(sx - 10, sy + 18, "Сенсор", size=10, color="#ef4444", bold=True, anchor="end"))

    # Промені кута огляду (FOV = 50 град: симетрично +/-25 від оптичної осі)
    fov_len = 175
    top_x = sx + fov_len * math.cos(0)
    top_y = sy + fov_len * math.sin(0)
    bot_x = sx + fov_len * math.cos(math.radians(50))
    bot_y = sy + fov_len * math.sin(math.radians(50))

    # Сектор огляду (FOV)
    path_fov = f"M {sx} {sy} L {top_x:.1f} {top_y:.1f} A {fov_len} {fov_len} 0 0 1 {bot_x:.1f} {bot_y:.1f} Z"
    elements.append(f'<path d="{path_fov}" fill="#dcfce7" fill-opacity="0.6" stroke="#16a34a" stroke-width="1.5"/>')
    elements.append(text(sx + 90, sy + 50, "Активний FOV", size=10, color="#15803d", bold=True))

    # Верхня сліпа зона (де повинні бути кабелі/гілки)
    path_blind_top = f"M {sx} {sy} L {top_x:.1f} {top_y:.1f} L {top_x:.1f} 100 L {sx} 100 Z"
    elements.append(f'<path d="{path_blind_top}" fill="#fee2e2" fill-opacity="0.6" stroke="#dc2626" stroke-width="1.5" stroke-dasharray="3,3"/>')
    elements.append(text(250, 140, "Верхня сліпа зона!", size=10, color="#b91c1c", bold=True))
    elements.append(text(250, 160, "(кабелі, гілки, балки)", size=10, color="#991b1b"))

    # Земля та відблиски внизу
    elements.append(line(50, 350, 390, 350, color="#78716c", sw=2))
    elements.append(text(85, 368, "Поверхня землі", size=10, color="#78716c"))
    # Хибне засвічення землі
    elements.append(text(290, 368, "Хибний відблиск / пил", size=10, color="#d97706", bold=True))
    elements.append(circle(290, 350, 4, fill="#f59e0b", stroke="#b45309", sw=1))

    # Пояснення внизу лівої панелі
    elements.append(rect(35, 305, 150, 30, fill="#ffffff", stroke="#94a3b8", sw=1, rx=4))
    elements.append(text(110, 324, "Кут нахилу: θ = 25°", size=10, color="#0f172a", bold=True))

    # Права панель: Мертві зони під час маневру за курсом (Yaw)
    elements.append(rect(440, 20, 400, 380, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    elements.append(text(640, 45, "2. Мертві зони при розвороті (Yaw)", size=12, color="#0f172a", bold=True))
    elements.append(text(640, 65, "Кутова швидкість ωz = 90°/с -> Затримка сенсора Δt", size=10, color="#475569"))

    # Вигляд зверху (Top View)
    dcx, dcy = 640, 205

    # Кругова сітка сканування 360
    elements.append(f'<circle cx="{dcx}" cy="{dcy}" r="115" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2" stroke-dasharray="3,3"/>')

    # Сектор переднього огляду (FOV = 70 град по курсу)
    yaw_fov_r = 115
    ang1 = math.radians(90 - 35)
    ang2 = math.radians(90 + 35)
    
    yf_x1 = dcx + yaw_fov_r * math.cos(ang1)
    yf_y1 = dcy - yaw_fov_r * math.sin(ang1)
    yf_x2 = dcx + yaw_fov_r * math.cos(ang2)
    yf_y2 = dcy - yaw_fov_r * math.sin(ang2)

    path_yaw_fov = f"M {dcx} {dcy} L {yf_x1:.1f} {yf_y1:.1f} A {yaw_fov_r} {yaw_fov_r} 0 0 0 {yf_x2:.1f} {yf_y2:.1f} Z"
    elements.append(f'<path d="{path_yaw_fov}" fill="#dcfce7" fill-opacity="0.6" stroke="#16a34a" stroke-width="1.5"/>')
    elements.append(text(dcx, dcy - 65, "Фронтальний FOV (70°)", size=10, color="#15803d", bold=True))

    # Бічні та тильні сліпі зони
    path_yaw_blind = f"M {dcx} {dcy} L {yf_x2:.1f} {yf_y2:.1f} A {yaw_fov_r} {yaw_fov_r} 0 1 0 {yf_x1:.1f} {yf_y1:.1f} Z"
    elements.append(f'<path d="{path_yaw_blind}" fill="#fee2e2" fill-opacity="0.4" stroke="#dc2626" stroke-width="1.2" stroke-dasharray="3,3"/>')
    
    elements.append(text(dcx - 65, dcy + 45, "Сліпий борт", size=10, color="#b91c1c", bold=True))
    elements.append(text(dcx, dcy + 85, "Тильна сліпа зона (290°)", size=10, color="#b91c1c", bold=True))

    # Корпус дрона зверху (хрестовина)
    elements.append(line(dcx - 25, dcy - 25, dcx + 25, dcy + 25, color="#334155", sw=3))
    elements.append(line(dcx - 25, dcy + 25, dcx + 25, dcy - 25, color="#334155", sw=3))
    elements.append(circle(dcx, dcy, 10, fill="#0284c7", stroke="#0369a1", sw=1.5))
    
    # 4 мотори
    for mx, my in [(dcx - 25, dcy - 25), (dcx + 25, dcy + 25), (dcx - 25, dcy + 25), (dcx + 25, dcy - 25)]:
        elements.append(circle(mx, my, 6, fill="#e2e8f0", stroke="#64748b", sw=1))

    # Стрілка розвороту по Yaw
    path_rot = f"M {dcx + 50} {dcy - 15} A 55 55 0 0 1 {dcx + 20} {dcy + 50}"
    elements.append(f'<path d="{path_rot}" fill="none" stroke="#7c3aed" stroke-width="2.5" marker-end="url(#arrow)"/>')
    elements.append(text(dcx + 80, dcy + 25, "ωz = 90°/с", size=10, color="#7c3aed", bold=True))

    # Прихована перешкода збоку (поза сектором огляду)
    elements.append(rect(dcx - 140, dcy - 30, 16, 45, fill="#334155", stroke="#0f172a", sw=1.5, rx=2))
    elements.append(text(dcx - 132, dcy - 38, "Стовп", size=10, color="#0f172a", bold=True))

    # Пояснення внизу правої панелі
    elements.append(rect(455, 345, 370, 42, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    elements.append(text(640, 362, "При швидкому нишпоренні автопілот зміщує корпус у бік,", size=10, color="#334155"))
    elements.append(text(640, 377, "де сенсор ще не встиг оновити карту простору.", size=10, color="#334155", italic=True))

    defs = '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="#7c3aed"/></marker></defs>'
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n%s\n%s\n</svg>'
           % (w, h, w, h, defs, "\n".join(elements)))

    path = os.path.join(IMG_DIR, 'blind-zones-tilt-yaw.svg')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f"Згенеровано: {path}")


def fig_noise_filtering_pipeline():
    """Фігура 2: Конвеєр фільтрації хибних спрацювань та просторово-часової валідації."""
    w, h = 860, 400
    elements = []

    elements.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))

    # Заголовок
    elements.append(text(430, 28, "Багаторівневий конвеєр фільтрації шуму та захисту від хибного гальмування", 
                         size=13, color=INK, bold=True))

    # Блок 1: Сирі сенсорні дані (ToF / Stereo / LiDAR)
    b1, _, _ = textbox(110, 85, "Сирі виміри (Raw)\nLiDAR / ToF / Stereo\n(Пил, сонце, краплі)", 
                       size=10, pad=6, fill="#fee2e2", stroke="#dc2626", min_w=150)
    elements.append(b1)

    elements.append(arrow(185, 85, 235, 85, color=LINE, sw=1.8))
    elements.append(text(210, 75, "Точки", size=10, color=MUTED))

    # Блок 2: Статистичний фільтр викидів (SOR)
    b2, _, _ = textbox(325, 85, "1. Фільтр викидів (SOR)\nОцінка k-NN сусідів\nВідсікання: d > μ + α·σ", 
                       size=10, pad=6, fill="#fef3c7", stroke="#d97706", min_w=160)
    elements.append(b2)

    elements.append(arrow(405, 85, 455, 85, color=LINE, sw=1.8))
    elements.append(text(430, 75, "Очищено", size=10, color=MUTED))

    # Блок 3: Просторово-часова персистентність
    b3, _, _ = textbox(555, 85, "2. Часова персистентність\nВоксельна сітка хітів\n+Chit при детекції, -Cdecay", 
                       size=10, pad=6, fill="#e0f2fe", stroke="#0284c7", min_w=180)
    elements.append(b3)

    elements.append(arrow(645, 85, 695, 85, color=LINE, sw=1.8))
    elements.append(text(670, 75, "Верифіковано", size=10, color=MUTED))

    # Блок 4: Узгодження з динамікою та локальний обхід
    b4, _, _ = textbox(775, 85, "3. Динамічний захист\nКонус безпеки Dstop(v)\nОбмеження швидкості", 
                       size=10, pad=6, fill="#dcfce7", stroke="#16a34a", min_w=145)
    elements.append(b4)

    # Нижня частина: деталізація трьох етапів
    # Етап 1: Розподіл відстаней SOR
    elements.append(rect(20, 160, 260, 220, fill="#fffbeb", stroke="#f59e0b", sw=1.2, rx=6))
    elements.append(text(150, 182, "Статистика відстаней (SOR)", size=11, color="#b45309", bold=True))
    
    # Графік гаусового розподілу
    elements.append(line(40, 280, 260, 280, color="#94a3b8", sw=1))
    elements.append(line(40, 205, 40, 285, color="#94a3b8", sw=1))
    elements.append(text(35, 210, "P(d)", size=10, color="#64748b"))
    elements.append(text(255, 292, "d", size=10, color="#64748b"))

    # Крива Гауса
    path_gauss = "M 50 280 Q 110 280, 130 215 Q 150 215, 170 280 L 250 280"
    elements.append(f'<path d="{path_gauss}" fill="none" stroke="#d97706" stroke-width="2"/>')
    # Межа відсікання
    elements.append(line(190, 205, 190, 280, color="#dc2626", sw=1.5, dash="3,3"))
    elements.append(text(190, 200, "μ + α·σ", size=10, color="#dc2626", bold=True))
    elements.append(text(225, 240, "Шум", size=10, color="#dc2626", bold=True))
    elements.append(text(225, 255, "(викид)", size=9, color="#dc2626"))
    elements.append(text(150, 320, "Відсікання розріджених точок пилу,", size=10, color="#78350f"))
    elements.append(text(150, 338, "аерозолю та сонячних бліків.", size=10, color="#78350f"))
    elements.append(text(150, 360, "Складність: O(N) через Spatial Hash", size=9, color="#92400e", italic=True))

    # Етап 2: Вокселі та часова стійкість
    elements.append(rect(300, 160, 260, 220, fill="#f0f9ff", stroke="#0284c7", sw=1.2, rx=6))
    elements.append(text(430, 182, "Персистентність у часі", size=11, color="#0369a1", bold=True))

    # Воксельна сітка
    for vx in range(330, 520, 32):
        for vy in range(205, 275, 32):
            elements.append(rect(vx, vy, 28, 28, fill="#ffffff", stroke="#bae6fd", sw=1, rx=2))
    
    # Заповнені стабільні вокселі (стіна)
    for vy in range(205, 275, 32):
        elements.append(rect(426, vy, 28, 28, fill="#0284c7", stroke="#0369a1", sw=1, rx=2))
        elements.append(text(440, vy + 17, "Hit", size=9, color="#ffffff", bold=True))

    # Фантомний воксель (згасає)
    elements.append(rect(362, 237, 28, 28, fill="#fecaca", stroke="#ef4444", sw=1, rx=2))
    elements.append(text(376, 254, "Decay", size=9, color="#991b1b"))

    elements.append(text(430, 320, "Одиночний сплеск швидко згасає,", size=10, color="#075985"))
    elements.append(text(430, 338, "реальна перешкода накопичує вагу.", size=10, color="#075985"))
    elements.append(text(430, 360, "Поріг підтвердження: Tocc > 3 кадрів", size=9, color="#0369a1", italic=True))

    # Етап 3: Узгодження з траєкторією
    elements.append(rect(580, 160, 260, 220, fill="#f0fdf4", stroke="#16a34a", sw=1.2, rx=6))
    elements.append(text(710, 182, "Динамічний конус безпеки", size=11, color="#15803d", bold=True))

    # Траєкторія дрона з конусом
    elements.append(circle(615, 240, 8, fill="#1e293b", stroke="#0f172a", sw=1.5))
    elements.append(arrow(615, 240, 700, 240, color="#16a34a", sw=2.5))
    elements.append(text(655, 225, "v = 8 м/с", size=10, color="#15803d", bold=True))

    # Зона безпеки гальмування
    path_cone = "M 615 240 L 755 210 L 755 270 Z"
    elements.append(f'<path d="{path_cone}" fill="#dcfce7" fill-opacity="0.5" stroke="#22c55e" stroke-width="1.2" stroke-dasharray="2,2"/>')
    elements.append(text(765, 240, "Dstop", size=10, color="#166534", bold=True, anchor="start"))

    elements.append(text(710, 320, "Зона перевірки масштабується як v²/2a.", size=10, color="#14532d"))
    elements.append(text(710, 338, "Ігнорування шумів поза коридором руху.", size=10, color="#14532d"))
    elements.append(text(710, 360, "Плавне гальмування без зриву орієнтації", size=9, color="#15803d", italic=True))

    defs = '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="#333333"/></marker></defs>'
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n%s\n%s\n</svg>'
           % (w, h, w, h, defs, "\n".join(elements)))

    path = os.path.join(IMG_DIR, 'noise-filtering-pipeline.svg')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f"Згенеровано: {path}")


if __name__ == '__main__':
    fig_blind_zones_tilt_yaw()
    fig_noise_filtering_pipeline()
