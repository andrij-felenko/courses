#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми parametry-povedinky (Параметри поведінки).
Вивід у ./img/
"""

import sys
import os

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_parameter_hierarchy():
    """Фігура 1: Трирівнева піраміда параметризації польотного контролера."""
    w, h = 860, 360
    elements = []

    # Фон
    elements.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))

    # Заголовок зверху
    elements.append(text(w / 2, 28, "Ієрархія параметризації автопілота: від констант до поведінки", size=15, color=INK, bold=True))

    # Ліва частина: Піраміда / 3 яруси
    # Ярус 3 (Вершина): Поведінкові та місійні параметри
    elements.append(rect(40, 55, 460, 80, fill="#e8f5e9", stroke=FIELD, sw=2, rx=6))
    elements.append(text(270, 78, "Рівень 3: Поведінкові та місійні параметри (Behavior)", size=13, color=FIELD, bold=True))
    elements.append(text(270, 98, "NAV_ACC_RAD, NAV_LOITER_RAD, NAV_CRUISE_SPD, RTL_ALT, OBS_STOP_DIST", size=11, color=INK))
    elements.append(text(270, 118, "Зміна: на льоту через MAVLink · Без перезавантаження · Ризик: локальний", size=10, color=MUTED, italic=True))

    # Ярус 2 (Середина): Калібрувальні та апаратні параметри
    elements.append(rect(40, 145, 460, 85, fill="#fff8e1", stroke="#d97706", sw=2, rx=6))
    elements.append(text(270, 168, "Рівень 2: Калібрувальні та апаратні параметри (Tuning)", size=13, color="#b45309", bold=True))
    elements.append(text(270, 188, "PID коефіцієнти (MC_ROLL_P), офсети сенсорів (ACC_OFF_X), матриця інерції", size=11, color=INK))
    elements.append(text(270, 208, "Зміна: на землі / Disarmed · Потребує валідації та перезапуску · Ризик: високий", size=10, color=MUTED, italic=True))

    # Ярус 1 (Основа): Жорстко зашиті інваріанти безпеки
    elements.append(rect(40, 240, 460, 90, fill="#fdecea", stroke=POS, sw=2, rx=6))
    elements.append(text(270, 263, "Рівень 1: Жорстко зашиті інваріанти безпеки (Hard Limits)", size=13, color=POS, bold=True))
    elements.append(text(270, 283, "MAX_TILT_ANGLE (60°), ESC_MAX_CURRENT, MIN_GYRO_RATE (1 kHz), NYQUIST_CUTOFF", size=11, color=INK))
    elements.append(text(270, 303, "Зміна: ТІЛЬКИ перезбирання прошивки · constexpr / static_assert · Захист від аварії", size=10, color=MUTED, italic=True))

    # Права частина: Характеристики та атрибути доступу
    # Блок Рівня 3
    elements.append(rect(520, 55, 300, 80, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    elements.append(text(670, 78, "Доступ: Оператор місії / GCS", size=11, color=INK, bold=True))
    elements.append(text(670, 98, "Сховище: Flash / FRAM / RAM кеш", size=10, color=INK))
    elements.append(text(670, 118, "Валідація: Range Check + Semantic Rules", size=10, color=FIELD))

    # Блок Рівня 2
    elements.append(rect(520, 145, 300, 85, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    elements.append(text(670, 168, "Доступ: Інженер з налаштування", size=11, color=INK, bold=True))
    elements.append(text(670, 188, "Сховище: Non-Volatile Flash / EEPROM", size=10, color=INK))
    elements.append(text(670, 208, "Валідація: Arming Checks + Hardware Sanity", size=10, color="#b45309"))

    # Блок Рівня 1
    elements.append(rect(520, 240, 300, 90, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    elements.append(text(670, 263, "Доступ: Архітектор коду (Hardcoded)", size=11, color=INK, bold=True))
    elements.append(text(670, 283, "Сховище: ROM / Flash Text Segment (.rodata)", size=10, color=INK))
    elements.append(text(670, 303, "Валідація: Compile-time static assertions", size=10, color=POS))

    # З'єднувальні стрілки зліва направо
    elements.append(arrow(500, 95, 520, 95, color=FIELD, sw=1.5))
    elements.append(arrow(500, 187, 520, 187, color="#d97706", sw=1.5))
    elements.append(arrow(500, 285, 520, 285, color=POS, sw=1.5))

    path = os.path.join(IMG_DIR, 'parameter-hierarchy-levels.svg')
    render(path, w, h, *elements)
    print(f"Generated {path}")


def fig_storage_pipeline():
    """Фігура 2: Архітектура сховища параметрів, валідація, CRC32 та MAVLink."""
    w, h = 860, 340
    elements = []

    # Фон
    elements.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))

    # Заголовок
    elements.append(text(w / 2, 26, "Конвеєр обробки, валідації та збереження параметрів", size=15, color=INK, bold=True))

    # Блок 1: MAVLink Transport
    elements.append(rect(30, 55, 160, 100, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=6))
    elements.append(text(110, 80, "MAVLink PARAM", size=12, color=NEG, bold=True))
    elements.append(text(110, 100, "PARAM_SET packet", size=10, color=INK))
    elements.append(text(110, 120, "param_id: NAV_ACC_RAD", size=9, color=MUTED))
    elements.append(text(110, 138, "value: 3.5f (float32)", size=9, color=MUTED))

    # Стрілка 1 -> 2
    elements.append(arrow(190, 105, 230, 105, color=LINE, sw=1.6))
    elements.append(text(210, 95, "raw", size=9, color=INK))

    # Блок 2: Багаторівнева валідація
    elements.append(rect(230, 45, 220, 120, fill="#fff8e1", stroke="#d97706", sw=1.6, rx=6))
    elements.append(text(340, 70, "Валідація та Sanity Check", size=12, color="#b45309", bold=True))
    elements.append(text(340, 92, "1. Range: min ≤ val ≤ max", size=10, color=INK))
    elements.append(text(340, 112, "2. State: Disarmed only?", size=10, color=INK))
    elements.append(text(340, 132, "3. Semantic: ACC_RAD < LOITER_RAD", size=9, color=INK))
    elements.append(text(340, 150, "4. Enum / Bitmask validity", size=9, color=MUTED))

    # Стрілка 2 -> 3
    elements.append(arrow(450, 105, 490, 105, color=FIELD, sw=1.8))
    elements.append(text(470, 95, "Valid", size=9, color=FIELD, bold=True))

    # Блок 3: RAM Registry
    elements.append(rect(490, 55, 170, 100, fill="#e8f5e9", stroke=FIELD, sw=1.6, rx=6))
    elements.append(text(575, 80, "RAM Кеш Реєстру", size=12, color=FIELD, bold=True))
    elements.append(text(575, 100, "Thread-Safe Storage", size=10, color=INK))
    elements.append(text(575, 120, "Atomic Handle Lookup", size=9, color=INK))
    elements.append(text(575, 138, "Оновлення за O(1)", size=9, color=MUTED))

    # Стрілка 3 -> 4 (Вниз у сховище)
    elements.append(arrow(575, 155, 575, 205, color=LINE, sw=1.6))
    elements.append(text(620, 180, "Dirty Flag / Save", size=9, color=INK))

    # Стрілка 3 -> Контури керування (Вправо)
    elements.append(arrow(660, 105, 710, 105, color=LINE, sw=1.6))
    elements.append(text(685, 95, "Notify", size=9, color=INK))

    # Блок 5: Контури реального часу
    elements.append(rect(710, 55, 125, 100, fill=FILL, stroke=LINE, sw=1.4, rx=6))
    elements.append(text(772, 80, "Контури ТРЧ", size=11, color=INK, bold=True))
    elements.append(text(772, 100, "Navigator", size=10, color=INK))
    elements.append(text(772, 120, "Attitude PID", size=10, color=INK))
    elements.append(text(772, 138, "Failsafe Engine", size=9, color=MUTED))

    # Блок 4: Двобуферне сховище Flash / FRAM
    elements.append(rect(230, 205, 500, 115, fill="#f4f6f8", stroke=LINE, sw=1.6, rx=6))
    elements.append(text(480, 226, "Двобуферне енергонезалежне сховище (Flash / FRAM)", size=12, color=INK, bold=True))

    # Сектор A
    elements.append(rect(250, 240, 215, 65, fill="#ffffff", stroke=FIELD, sw=1.4, rx=4))
    elements.append(text(357, 258, "Сектор A (Active, Seq=14)", size=10, color=FIELD, bold=True))
    elements.append(text(357, 276, "Magic | Ver | Records | CRC32", size=9, color=INK))
    elements.append(text(357, 294, "Стан: Перевірено OK ✓", size=9, color=FIELD))

    # Сектор B
    elements.append(rect(495, 240, 215, 65, fill="#ffffff", stroke=MUTED, sw=1.2, rx=4))
    elements.append(text(602, 258, "Сектор B (Standby / Backup)", size=10, color=MUTED, bold=True))
    elements.append(text(602, 276, "Ready for next atomic commit", size=9, color=MUTED))
    elements.append(text(602, 294, "Fallback при збої CRC32", size=9, color=MUTED))

    # Зворотна лінія-стрілка від валідації на помилку (NACK / Rejection)
    elements.append(line(340, 165, 340, 180, color=POS, sw=1.5, dash="4,3"))
    elements.append(line(340, 180, 110, 180, color=POS, sw=1.5, dash="4,3"))
    elements.append(arrow(110, 180, 110, 155, color=POS, sw=1.5))
    elements.append(text(225, 195, "Invalid: NACK / Залишаємо старе", size=9, color=POS, bold=True))

    path = os.path.join(IMG_DIR, 'param-storage-validation-pipeline.svg')
    render(path, w, h, *elements)
    print(f"Generated {path}")


if __name__ == '__main__':
    fig_parameter_hierarchy()
    fig_storage_pipeline()
