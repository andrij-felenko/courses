#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми missions-waypoints.
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


def fig_mission_item_structure():
    """Фігура 1: Анатомія структури елемента місії (MISSION_ITEM_INT)."""
    w, h = 860, 320
    elements = []
    
    # Фон
    elements.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))
    
    # Заголовок блоку структури
    elements.append(rect(20, 20, 820, 280, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    elements.append(text(430, 46, "Структура корисного навантаження MISSION_ITEM_INT (#73, 38 байтів)", size=14, color=INK, bold=True))
    
    # Секція 1: Параметри 1..4 (float32, 16 байтів)
    elements.append(rect(40, 70, 380, 100, fill="#edf2f7", stroke=LINE, sw=1.2, rx=6))
    elements.append(text(230, 92, "Плаваюча кома: 4 × float32 (16 байтів)", size=12, color=INK, bold=True))
    elements.append(text(230, 115, "param1: Hold Time (с) / Loiter Turns / Min Pitch", size=11, color=INK))
    elements.append(text(230, 133, "param2: Acceptance Radius R_acc (м)", size=11, color=INK))
    elements.append(text(230, 151, "param3: Pass / Orbit Radius (м) [+CW, -CCW]", size=11, color=INK))
    elements.append(text(230, 169, "param4: Desired Yaw Angle (град або NaN)", size=11, color=MUTED))
    
    # Секція 2: Просторові координати X, Y, Z (12 байтів)
    elements.append(rect(440, 70, 380, 100, fill="#e8f4fd", stroke=LINE, sw=1.2, rx=6))
    elements.append(text(630, 92, "Просторові координати: 2 × int32 + 1 × float32", size=12, color=INK, bold=True))
    elements.append(text(630, 115, "x (int32_t): Широта Latitude × 10⁷ (degE7)", size=11, color=INK))
    elements.append(text(630, 133, "y (int32_t): Довгота Longitude × 10⁷ (degE7)", size=11, color=INK))
    elements.append(text(630, 151, "z (float): Висота Altitude (м) [AMSL / Rel / Terrain]", size=11, color=INK))
    elements.append(text(630, 169, "Дискретність: 10⁻⁷ град ≈ 1.11 см на екваторі", size=11, color=NEG, bold=True))
    
    # Секція 3: Службові поля, команда та фрейм (10 байтів)
    elements.append(rect(40, 185, 780, 95, fill="#fef9e7", stroke=LINE, sw=1.2, rx=6))
    elements.append(text(430, 207, "Службові поля послідовності, навігаційної команди та фрейму", size=12, color=INK, bold=True))
    
    # Підколонки службових полів
    elements.append(text(160, 232, "seq (uint16_t, 2 байта)", size=11, color=INK, bold=True))
    elements.append(text(160, 252, "Порядковий індекс 0..N-1", size=11, color=MUTED))
    
    elements.append(text(340, 232, "command (uint16_t, 2 байта)", size=11, color=INK, bold=True))
    elements.append(text(340, 252, "MAV_CMD (NAV, DO, CONDITION)", size=11, color=MUTED))
    
    elements.append(text(520, 232, "frame (uint8_t, 1 байт)", size=11, color=INK, bold=True))
    elements.append(text(520, 252, "GLOBAL_REL / TERRAIN_ALT", size=11, color=MUTED))
    
    elements.append(text(700, 232, "current / autocontinue / type", size=11, color=INK, bold=True))
    elements.append(text(700, 252, "3 × uint8_t (активна ціль, прапорці)", size=11, color=MUTED))
    
    render(os.path.join(IMG_DIR, "mission-item-structure.svg"), w, h, *elements)


def fig_navigation_command_trajectories():
    """Фігура 2: Кінематичні профілі навігаційних команд (WAYPOINT, SPLINE, LOITER, TAKEOFF, LAND)."""
    w, h = 860, 360
    elements = []
    
    # Фон
    elements.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))
    
    # Картка 1: Прямий WAYPOINT (Fly-through vs Stop)
    elements.append(rect(20, 20, 260, 150, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    elements.append(text(150, 42, "1. NAV_WAYPOINT (#16)", size=12, color=INK, bold=True))
    # Траєкторія
    elements.append(circle(50, 110, 5, fill=NEG, stroke=LINE, sw=1.2))
    elements.append(text(50, 130, "WP0", size=10, color=INK))
    elements.append(circle(150, 75, 5, fill=FIELD, stroke=LINE, sw=1.2))
    elements.append('<circle cx="150.0" cy="75.0" r="20.0" fill="none" stroke="%s" stroke-width="1.0" stroke-dasharray="3,3"/>' % FIELD)
    elements.append(text(150, 62, "WP1 (R_acc)", size=10, color=INK))
    elements.append(circle(240, 110, 5, fill=NEG, stroke=LINE, sw=1.2))
    elements.append(text(240, 130, "WP2", size=10, color=INK))
    elements.append(line(50, 110, 135, 80, color=LINE, sw=1.8))
    elements.append(line(165, 80, 240, 110, color=LINE, sw=1.8))
    elements.append(text(150, 152, "Пряма ламана, зупинка або зріз кута", size=10, color=MUTED))
    
    # Картка 2: Сплайн SPLINE_WAYPOINT
    elements.append(rect(300, 20, 260, 150, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    elements.append(text(430, 42, "2. NAV_SPLINE_WAYPOINT (#82)", size=12, color=INK, bold=True))
    elements.append(circle(330, 120, 5, fill=NEG, stroke=LINE, sw=1.2))
    elements.append(circle(430, 70, 5, fill=FIELD, stroke=LINE, sw=1.2))
    elements.append(circle(530, 120, 5, fill=NEG, stroke=LINE, sw=1.2))
    # Гладка крива
    path_spline = '<path d="M 330 120 C 370 70, 390 70, 430 70 C 470 70, 490 70, 530 120" fill="none" stroke="%s" stroke-width="2.0"/>' % POS
    elements.append(path_spline)
    elements.append(text(430, 92, "Cubic Hermite Spline", size=10, color=POS, bold=True))
    elements.append(text(430, 152, "Неперервна швидкість v > 0 без гальмування", size=10, color=MUTED))
    
    # Картка 3: Очікування LOITER_TIME / TURNS
    elements.append(rect(580, 20, 260, 150, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    elements.append(text(710, 42, "3. NAV_LOITER_TIME (#19)", size=12, color=INK, bold=True))
    elements.append(circle(710, 90, 4, fill=LINE, stroke=LINE, sw=1.0))
    elements.append('<circle cx="710.0" cy="90.0" r="32.0" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="4,2"/>' % POS)
    elements.append(arrow(742, 90, 742, 98, color=POS, sw=1.8))
    elements.append(text(710, 94, "R_orbit", size=10, color=INK))
    elements.append(text(710, 134, "Таймер Hold Time після входу в сферу", size=10, color=INK))
    elements.append(text(710, 152, "Або LOITER_TURNS (#18) N обертів", size=10, color=MUTED))
    
    # Картка 4: Зліт TAKEOFF
    elements.append(rect(140, 190, 280, 150, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    elements.append(text(280, 212, "4. NAV_TAKEOFF (#22)", size=12, color=INK, bold=True))
    elements.append(line(170, 300, 390, 300, color=LINE, sw=2.0))
    elements.append(text(200, 316, "Земля (Alt=0)", size=10, color=MUTED))
    elements.append(circle(180, 300, 5, fill=NEG, stroke=LINE, sw=1.2))
    elements.append(arrow(180, 300, 350, 245, color=FIELD, sw=2.0))
    elements.append(circle(350, 245, 5, fill=FIELD, stroke=LINE, sw=1.2))
    elements.append(line(350, 245, 390, 245, color=MUTED, sw=1.0, dash="2,2"))
    elements.append(text(370, 235, "Target Alt Z", size=10, color=FIELD, bold=True))
    elements.append(text(280, 332, "Крива набору висоти до порогу Alt ± dZ", size=10, color=MUTED))
    
    # Картка 5: Посадка LAND
    elements.append(rect(440, 190, 280, 150, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    elements.append(text(580, 212, "5. NAV_LAND (#21)", size=12, color=INK, bold=True))
    elements.append(line(470, 300, 690, 300, color=LINE, sw=2.0))
    elements.append(circle(480, 235, 5, fill=FIELD, stroke=LINE, sw=1.2))
    elements.append(arrow(480, 235, 570, 275, color=POS, sw=1.8))
    elements.append(text(525, 250, "Швидкий спуск", size=10, color=INK))
    elements.append(arrow(570, 275, 630, 300, color=POS, sw=1.8))
    elements.append(text(645, 285, "Flare 0.5 м/с", size=10, color=POS))
    elements.append(circle(630, 300, 5, fill=NEG, stroke=LINE, sw=1.2))
    elements.append(text(580, 332, "Touchdown детектор → Auto Disarm", size=10, color=MUTED))
    
    render(os.path.join(IMG_DIR, "navigation-command-trajectories.svg"), w, h, *elements)


def fig_mission_upload_protocol_fsm():
    """Фігура 3: Транзакційний протокол завантаження місії над радіоканалом."""
    w, h = 860, 420
    elements = []
    
    # Фон
    elements.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))
    
    # Дві вертикальні лінії учасників: GCS (Земля) та Autopilot (Борт)
    elements.append(rect(100, 20, 160, 36, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    elements.append(text(180, 43, "GCS (Наземна станція)", size=12, color=INK, bold=True))
    elements.append(line(180, 56, 180, 395, color=MUTED, sw=1.2, dash="4,4"))
    
    elements.append(rect(600, 20, 160, 36, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    elements.append(text(680, 43, "Autopilot (Борт FC)", size=12, color=INK, bold=True))
    elements.append(line(680, 56, 680, 395, color=MUTED, sw=1.2, dash="4,4"))
    
    # Крок 1: MISSION_COUNT
    y1 = 90
    elements.append(arrow(180, y1, 680, y1, color=LINE, sw=1.8))
    elements.append(text(430, y1 - 8, "MISSION_COUNT (count=N, type=MISSION)", size=11, color=INK, bold=True))
    elements.append(text(710, y1 + 5, "Буфер RAM очищено", size=10, color=MUTED, anchor="start"))
    
    # Крок 2: MISSION_REQUEST_INT(0)
    y2 = 135
    elements.append(arrow(680, y2, 180, y2, color=FIELD, sw=1.8))
    elements.append(text(430, y2 - 8, "MISSION_REQUEST_INT (seq=0)", size=11, color=FIELD, bold=True))
    
    # Крок 3: MISSION_ITEM_INT(0)
    y3 = 180
    elements.append(arrow(180, y3, 680, y3, color=LINE, sw=1.8))
    elements.append(text(430, y3 - 8, "MISSION_ITEM_INT (seq=0: TAKEOFF)", size=11, color=INK, bold=True))
    
    # Крок 4: Загублений запит seq=1 та таймаут
    y4 = 225
    elements.append(line(680, y4, 450, y4, color=POS, sw=1.8))
    elements.append(text(440, y4 + 4, "✗", size=14, color=POS, bold=True))
    elements.append(text(430, y4 - 8, "MISSION_REQUEST_INT (seq=1) [ВТРАЧЕНО В ЕФІРІ]", size=11, color=POS, bold=True))
    
    # Крок 5: Таймаут автопілота та повторний запит seq=1
    y5 = 275
    elements.append(rect(660, 240, 160, 30, fill="#fdecea", stroke=POS, sw=1.0, rx=4))
    elements.append(text(740, 258, "Таймаут 1500 мс → Retry #1", size=10, color=POS, bold=True))
    elements.append(arrow(680, y5, 180, y5, color=FIELD, sw=1.8))
    elements.append(text(430, y5 - 8, "MISSION_REQUEST_INT (seq=1: Повтор)", size=11, color=FIELD, bold=True))
    
    # Крок 6: MISSION_ITEM_INT(1)
    y6 = 320
    elements.append(arrow(180, y6, 680, y6, color=LINE, sw=1.8))
    elements.append(text(430, y6 - 8, "MISSION_ITEM_INT (seq=1: WAYPOINT)", size=11, color=INK, bold=True))
    
    # Крок 7: Фінальний комміт та MISSION_ACK
    y7 = 370
    elements.append(rect(660, 335, 175, 30, fill="#edf2f7", stroke=LINE, sw=1.0, rx=4))
    elements.append(text(745, 353, "Запис у FRAM + CRC Verify", size=10, color=INK, bold=True))
    elements.append(arrow(680, y7, 180, y7, color=FIELD, sw=2.0))
    elements.append(text(430, y7 - 8, "MISSION_ACK (type=MAV_MISSION_ACCEPTED = 0)", size=12, color=FIELD, bold=True))
    
    render(os.path.join(IMG_DIR, "mission-upload-protocol-fsm.svg"), w, h, *elements)


def fig_flash_fram_storage_layout():
    """Фігура 4: Схема організації енергонезалежної пам'яті (Flash/FRAM Dual-Slot Layout)."""
    w, h = 860, 340
    elements = []
    
    # Фон
    elements.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))
    
    # Загальний контейнер пам'яті NVRAM
    elements.append(rect(20, 20, 820, 300, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    elements.append(text(430, 45, "Організація енергонезалежної пам'яті: Dual-Slot транзакційне сховище", size=14, color=INK, bold=True))
    
    # Сектор Покажчика Активного Слота (Active Pointer Sector)
    elements.append(rect(40, 70, 780, 50, fill="#fef9e7", stroke=LINE, sw=1.2, rx=6))
    elements.append(text(430, 92, "Сектор метаданих (Active Slot Pointer): 1 байт активного слота (0x01 = Слот A, 0x02 = Слот B)", size=11, color=INK, bold=True))
    elements.append(text(430, 110, "Атомарне оновлення: зміна 1 байта після повної верифікації CRC нового слота", size=10, color=MUTED))
    
    # Слот A (Active / Valid)
    elements.append(rect(40, 135, 375, 170, fill="#e8f4fd", stroke=FIELD, sw=1.8, rx=6))
    elements.append(text(227, 158, "Слот A (АКТИВНИЙ СЛОТ, CRC OK)", size=12, color=FIELD, bold=True))
    
    elements.append(rect(55, 170, 345, 36, fill=BG, stroke=LINE, sw=1.0, rx=4))
    elements.append(text(227, 192, "Header (32B): Magic 'MISS' | Count N | CRC-16", size=10, color=INK, bold=True))
    
    elements.append(rect(55, 212, 345, 55, fill=BG, stroke=LINE, sw=1.0, rx=4))
    elements.append(text(227, 230, "Масив точок: MissionItem[0..N-1]", size=10, color=INK))
    elements.append(text(227, 248, "Packed Structs (N × 38 байтів)", size=10, color=MUTED))
    elements.append(text(227, 288, "Статус: Робоча місія для виконання навігатором", size=10, color=FIELD, bold=True))
    
    # Слот B (Staging / Inactive)
    elements.append(rect(445, 135, 375, 170, fill="#edf2f7", stroke=MUTED, sw=1.2, rx=6))
    elements.append(text(632, 158, "Слот B (STAGING / ТІНЬОВИЙ СЛОТ)", size=12, color=MUTED, bold=True))
    
    elements.append(rect(460, 170, 345, 36, fill=BG, stroke=LINE, sw=1.0, rx=4))
    elements.append(text(632, 192, "Header (32B): Новий лічильник M | CRC_staging", size=10, color=MUTED, bold=True))
    
    elements.append(rect(460, 212, 345, 55, fill=BG, stroke=LINE, sw=1.0, rx=4))
    elements.append(text(632, 230, "Масив точок: Нова завантажувана місія", size=10, color=MUTED))
    elements.append(text(632, 248, "Поетапний запис по мірі надходження пакетів", size=10, color=MUTED))
    elements.append(text(632, 288, "Захист: Знеструмлення під час запису НЕ псує Слот A", size=10, color=POS, bold=True))
    
    render(os.path.join(IMG_DIR, "flash-fram-storage-layout.svg"), w, h, *elements)


def main():
    fig_mission_item_structure()
    fig_navigation_command_trajectories()
    fig_mission_upload_protocol_fsm()
    fig_flash_fram_storage_layout()
    print("Усі 4 фігури успішно згенеровано.")


if __name__ == "__main__":
    main()
