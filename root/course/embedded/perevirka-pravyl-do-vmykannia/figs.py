#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генерація SVG-ілюстрацій для теми perevirka-pravyl-do-vmykannia."""

import os
import sys

# Шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_sil_pipeline():
    """Чотири рівні верифікації логіки автоматизації перед силовим увімкненням."""
    w, h = 860, 420
    frags = []

    # Заголовок блоків
    frags.append(text(430, 28, "Етапи верифікації правил до подачі напруги на навантаження", size=16, bold=True))

    # 4 послідовні колонки (етапи)
    steps = [
        ("1. Табличний аналіз", "Повний перебір 2^N станів", "Виявлення конфліктів,\nсуперечностей і глухих\nкутів (deadlocks)", "#eaf2fd", NEG),
        ("2. Ін'єкція входів", "Sensor Mocking & Faults", "Подача 150 °C, 0 бар, NaN,\nобривів зв'язку та\nаномальних комбінацій", "#fef6e7", "#d97706"),
        ("3. Суха прогонка", "Dry Run / Disarm Mode", "Виконання на залізі,\nале силові ключі знеструмлені;\nаудит вихідного логу дій", "#f3e8ff", "#7e22ce"),
        ("4. SIL-симулятор", "Software-in-the-Loop", "Замкнений контур із фізичною\nмоделлю об'єкта (Plant Model)\nта віртуальним часом", "#ecfdf5", FIELD),
    ]

    col_w = 180
    col_h = 240
    start_x = 35
    start_y = 60
    gap = 26

    for i, (title, subtitle, desc, fill_col, stroke_col) in enumerate(steps):
        x = start_x + i * (col_w + gap)
        # Карточка етапу
        frags.append(rect(x, start_y, col_w, col_h, fill=fill_col, stroke=stroke_col, sw=1.8, rx=8))
        # Заголовок етапу
        frags.append(text(x + col_w / 2, start_y + 28, title, size=13, bold=True, color=stroke_col))
        frags.append(text(x + col_w / 2, start_y + 50, subtitle, size=11, bold=False, color=MUTED, italic=True))
        frags.append(line(x + 15, start_y + 64, x + col_w - 15, start_y + 64, color=stroke_col, sw=1.0, dash="3,3"))
        # Опис
        frags.append(mtext(x + col_w / 2, start_y + 90, desc, size=11, color=INK, lh=1.4))

        # Стрілка переходу до наступного етапу
        if i < 3:
            ax1 = x + col_w + 3
            ax2 = x + col_w + gap - 4
            ay = start_y + col_h / 2
            frags.append(arrow(ax1, ay, ax2, ay, color=LINE, sw=1.6))

    # Підсумковий блок унизу: Фізичний об'єкт
    gate_y = 330
    frags.append(rect(start_x, gate_y, 798, 65, fill="#fef2f2", stroke=POS, sw=2.0, rx=8))
    frags.append(text(430, gate_y + 25, "СИЛОВЕ ВМИКАННЯ (ARMED STATE): РЕЛЕ, ТЕНИ, НАСОСИ, КЛАПАНИ", size=13, bold=True, color=POS))
    frags.append(text(430, gate_y + 48, "Подача живлення на приводи дозволена лише за 100% проходження перевірок 1-4 без порушення інваріантів безпеки", size=11, color=INK))

    # Стрілка зверху вниз до силового блоку
    frags.append(arrow(430, start_y + col_h + 4, 430, gate_y - 4, color=POS, sw=2.0))

    render(os.path.join(OUT_DIR, 'sil-verification-pipeline.svg'), w, h, *frags)


def fig_decision_table():
    """Простір станів комбінацій дискретних входів та зони конфліктів."""
    w, h = 820, 360
    frags = []

    frags.append(text(410, 26, "Комбінаторний простір входів (2^N) та перевірка інваріантів безпеки", size=16, bold=True))

    # Таблиця комбінацій (ліворуч)
    tx, ty = 40, 55
    tw, th = 380, 275
    frags.append(rect(tx, ty, tw, th, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    frags.append(text(tx + tw / 2, ty + 24, "Таблиця рішень дискретних входів", size=13, bold=True))

    headers = ["Рівень_L", "Рівень_H", "Тиск_OK", "Помпа", "Клапан", "Статус інваріанта"]
    hx_offsets = [35, 95, 155, 215, 275, 340]
    
    # Заголовок рядка
    frags.append(rect(tx + 8, ty + 38, tw - 16, 24, fill="#e5e7eb", stroke="#d1d5db", sw=1.0, rx=3))
    for h_name, hx in zip(headers, hx_offsets):
        frags.append(text(tx + hx, ty + 54, h_name, size=9.5, bold=True))

    rows = [
        ("0", "0", "0", "0", "0", "Норма (порожній)", "#ecfdf5", FIELD),
        ("1", "0", "1", "1", "1", "Норма (наповнення)", "#ecfdf5", FIELD),
        ("1", "1", "1", "0", "0", "Норма (повний)", "#ecfdf5", FIELD),
        ("0", "1", "X", "0", "0", "ФІЗИЧНИЙ ПАРАДОКС", "#fdecea", POS),
        ("1", "0", "0", "1", "0", "СУПЕРЕЧНІСТЬ ПРАВИЛ", "#fef6e7", "#d97706"),
        ("0", "0", "1", "?", "?", "DEADLOCK (нема дії)", "#f3e8ff", "#7e22ce"),
    ]

    for idx, (l, h_val, p, pump, valve, status, bg_col, txt_col) in enumerate(rows):
        ry = ty + 68 + idx * 30
        frags.append(rect(tx + 8, ry, tw - 16, 26, fill=bg_col, stroke=txt_col, sw=1.0, rx=3))
        vals = [l, h_val, p, pump, valve]
        for val, hx in zip(vals, hx_offsets[:5]):
            frags.append(text(tx + hx, ry + 17, val, size=11, bold=(val not in ("0", "1"))))
        frags.append(text(tx + hx_offsets[5], ry + 17, status, size=9.5, bold=True, color=txt_col))

    # Права панель: Аналогові межі та гістерезис
    ax, ay = 450, 55
    aw, ah = 330, 275
    frags.append(rect(ax, ay, aw, ah, fill="#fafafa", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(ax + aw / 2, ay + 24, "Крайові точки аналогових входів", size=13, bold=True))

    # Вісь температури / значень
    axis_x = ax + 50
    axis_y_top = ay + 50
    axis_y_bot = ay + 245
    frags.append(line(axis_x, axis_y_bot, axis_x, axis_y_top, color=LINE, sw=2.0))
    frags.append(arrow(axis_x, axis_y_top + 10, axis_x, axis_y_top - 5, color=LINE, sw=2.0))

    # Діапазони
    ranges = [
        (axis_y_top + 15, axis_y_top + 45, "> 120 °C (Аварійний перегрів)", "#fdecea", POS),
        (axis_y_top + 45, axis_y_top + 95, "95..120 °C (Гістерезис вимкнення)", "#fef6e7", "#d97706"),
        (axis_y_top + 95, axis_y_top + 145, "60..95 °C (Робочий діапазон)", "#ecfdf5", FIELD),
        (axis_y_top + 145, axis_y_bot - 10, "< 60 °C (Поріг увімкнення нагріву)", "#eaf2fd", NEG),
    ]

    for y1, y2, label, fill_col, border_col in ranges:
        frags.append(rect(axis_x + 15, y1, aw - 80, y2 - y1 - 4, fill=fill_col, stroke=border_col, sw=1.2, rx=4))
        frags.append(text(axis_x + 25 + (aw - 80) / 2, (y1 + y2) / 2 + 3, label, size=10, color=border_col, bold=True))
        frags.append(line(axis_x - 5, (y1 + y2) / 2, axis_x + 15, (y1 + y2) / 2, color=border_col, sw=1.2))

    # Позначка вильоту / помилки датчика
    frags.append(text(ax + aw / 2, ay + ah - 12, "Спецзначення: NaN, Open-Loop, Rate Spike (dT/dt > 50 °C/s)", size=9, color=POS, italic=True))

    render(os.path.join(OUT_DIR, 'decision-table-space.svg'), w, h, *frags)


def fig_dry_run_interceptor():
    """Архітектура перехоплення драйверів (Mock HAL / Actuator Disarm)."""
    w, h = 840, 380
    frags = []

    frags.append(text(420, 26, "Архітектура сухої прогонки: розділення логіки та силового драйвера", size=16, bold=True))

    # Лівий блок: Джерела даних (Датчики / Ін'єктор)
    frags.append(rect(30, 60, 180, 270, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(120, 85, "Джерела сигналів", size=13, bold=True))

    frags.append(rect(45, 110, 150, 50, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    frags.append(text(120, 130, "Фізичні датчики", size=11, bold=True))
    frags.append(text(120, 146, "ADC, I2C, GPIO In", size=9.5, color=MUTED))

    frags.append(rect(45, 185, 150, 65, fill="#fef6e7", stroke="#d97706", sw=1.5, rx=6))
    frags.append(text(120, 206, "Ін'єктор входів", size=11, bold=True, color="#d97706"))
    frags.append(text(120, 222, "Virtual Sensor Mock", size=9.5, color=INK))
    frags.append(text(120, 238, "150 °C / 0 бар / NaN", size=9.5, color=POS))

    frags.append(text(120, 290, "Селектор джерела", size=10, bold=True))
    frags.append(rect(70, 305, 100, 18, fill="#e2e8f0", stroke="#64748b", sw=1.0, rx=3))
    frags.append(text(120, 317, "MODE_SIM / REAL", size=9, color=INK))

    # Центральний блок: Рушій правил
    frags.append(rect(260, 60, 260, 270, fill="#f0fdf4", stroke=FIELD, sw=2.0, rx=8))
    frags.append(text(390, 88, "Рушій правил (Rule Engine)", size=14, bold=True, color=FIELD))

    components = [
        ("Обробка гістерезису й фільтрів", 115),
        ("Таблиця правил та пріоритетів", 160),
        ("Охоронці стану (State Guards)", 205),
        ("Формування команд на виходи", 250),
    ]
    for c_title, cy in components:
        frags.append(rect(280, cy, 220, 35, fill="#ffffff", stroke="#86efac", sw=1.2, rx=5))
        frags.append(text(390, cy + 22, c_title, size=11, bold=True))

    # Стрілка від датчиків до рушія
    frags.append(arrow(210, 195, 258, 195, color=LINE, sw=1.8))
    frags.append(text(235, 185, "State", size=9.5, bold=True))

    # Правий блок: Виконання та перехоплення (Dry Run Interceptor)
    frags.append(rect(570, 60, 240, 270, fill="#fdf4ff", stroke="#7e22ce", sw=1.5, rx=8))
    frags.append(text(690, 85, "Шар вихідного драйвера", size=13, bold=True, color="#7e22ce"))

    # Гілка 1: Режим Dry Run (Логування)
    frags.append(rect(585, 110, 210, 75, fill="#ffffff", stroke="#c084fc", sw=1.5, rx=6))
    frags.append(text(690, 132, "РЕЖИМ DRY RUN (DISARM)", size=11, bold=True, color="#7e22ce"))
    frags.append(text(690, 150, "Силові виходи ВИМКНЕНІ (0 В)", size=9.5, color=POS, bold=True))
    frags.append(text(690, 168, "Запис подій у пам'ять / лог-файл", size=9.5, color=MUTED))

    # Гілка 2: Реальні силові ключі
    frags.append(rect(585, 210, 210, 75, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    frags.append(text(690, 232, "РЕЖИМ ARMED (СИЛОВИЙ)", size=11, bold=True, color=POS))
    frags.append(text(690, 250, "GPIO / MOSFET / Реле 230 В", size=9.5, color=INK))
    frags.append(text(690, 268, "Апаратний захист струму/КЗ", size=9.5, color=MUTED))

    # Стрілка від рушія до драйвера
    frags.append(arrow(520, 195, 568, 195, color=LINE, sw=1.8))
    frags.append(text(545, 185, "Cmd", size=9.5, bold=True))

    # Перемикач
    frags.append(circle(555, 195, 4, fill=LINE, stroke=LINE))

    render(os.path.join(OUT_DIR, 'dry-run-interceptor.svg'), w, h, *frags)


def main():
    print("Генерація SVG-ілюстрацій...")
    fig_sil_pipeline()
    fig_decision_table()
    fig_dry_run_interceptor()
    print("Готово!")


if __name__ == "__main__":
    main()
