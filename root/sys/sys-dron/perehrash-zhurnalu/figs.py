#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми 'Переграш журналу: рішення на записаних даних'."""

import os
import sys

# Підключення svgkit із scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

def build_replay_injection_architecture(path):
    """Фігура 1: Архітектура заміни сенсорних джерел та впорскування логів у EKF."""
    w, h = 1000, 580
    frags = []

    # Загальний заголовок
    frags.append(text(500, 28, "Порівняння архітектури польотного контуру та детерміністичного переграшу логів", size=15, bold=True))

    # Ліва колонка: Штатний польотний режим
    frags.append(rect(20, 50, 460, 510, fill="#fcfdfe", stroke=LINE, rx=6))
    frags.append(fitbox(35, 65, 430, 32, "1. Штатний польотний контур (Real Flight)", size=13, fill="#ebf3fb", stroke=NEG, color=NEG, bold=True))

    # Блоки лівої колонки
    frags.append(fitbox(45, 115, 410, 60, "Фізичні сенсори платформи\nICM-42688P (IMU), BMP388 (Baro), U-Blox F9P (GNSS)", size=11, fill="#ffffff", stroke="#cbd5e1", bold=False))
    frags.append(arrow(250, 175, 250, 205, color=LINE))
    frags.append(text(255, 193, "SPI / I2C / UART", size=9, color=MUTED, anchor="start"))

    frags.append(fitbox(45, 205, 410, 60, "Драйвери RTOS (NuttX / ChibiOS)\nОпитування переривань, DMA-буфери, калібрування", size=11, fill="#ffffff", stroke="#cbd5e1", bold=False))
    frags.append(arrow(250, 265, 250, 295, color=LINE))
    frags.append(text(255, 283, "orb_publish()", size=9, color=MUTED, anchor="start"))

    frags.append(fitbox(45, 295, 410, 65, "Бортова шина uORB / AP_HAL\nsensor_combined (1000 Гц), vehicle_gps_position (10 Гц)\nvehicle_air_data (50 Гц), vehicle_magnetometer (100 Гц)", size=10, fill="#f8fafc", stroke=LINE, bold=False))

    # Розгалуження: в EKF і в Logger
    frags.append(arrow(160, 360, 160, 395, color=LINE))
    frags.append(arrow(340, 360, 340, 395, color=POS))

    frags.append(fitbox(45, 395, 230, 65, "Навігаційний фільтр EKF2\nОцінка орієнтації, швидкості,\nпозиції та зсувів гіроскопів", size=10, fill="#ffffff", stroke="#cbd5e1", bold=False))
    frags.append(fitbox(290, 395, 165, 65, "Logger Module\nЗапис ULog / BIN\nна карту MicroSD", size=10, fill="#fef2f2", stroke=POS, color=POS, bold=False))

    frags.append(arrow(160, 460, 160, 485, color=LINE))
    frags.append(fitbox(45, 485, 230, 50, "Контролери та мікшер моторів\nГенерація сигналів DShot / PWM", size=10, fill="#ffffff", stroke="#cbd5e1", bold=False))


    # Права колонка: Режим детерміністичного Replay
    frags.append(rect(520, 50, 460, 510, fill="#fcfdfe", stroke=LINE, rx=6))
    frags.append(fitbox(535, 65, 430, 32, "2. Детерміністичний переграш (SITL Replay)", size=13, fill="#f0fdf4", stroke=FIELD, color=FIELD, bold=True))

    frags.append(fitbox(545, 115, 410, 60, "Записаний польотний лог (ULog / DataFlash)\nБінарні повідомлення, точні часові мітки, схеми полів", size=11, fill="#ffffff", stroke=FIELD, bold=False))
    frags.append(arrow(750, 175, 750, 205, color=FIELD))
    frags.append(text(755, 193, "Потокове читання з SSD", size=9, color=FIELD, anchor="start"))

    frags.append(fitbox(545, 205, 410, 60, "Модуль Replay Engine & Віртуальний годинник\nПріоритетна черга за timestamp, дискретний Simulated Time", size=11, fill="#f0fdf4", stroke=FIELD, bold=False))
    frags.append(arrow(750, 265, 750, 295, color=FIELD))
    frags.append(text(755, 283, "Впорскування через orb_publish", size=9, color=FIELD, anchor="start"))

    frags.append(fitbox(545, 295, 410, 65, "Віртуальна шина повідомлень SITL\n[Драйвери апаратних сенсорів ВИМКНЕНО]\nПідміна вхідних потоків даними з логу з точним таймінгом", size=10, fill="#f8fafc", stroke=LINE, bold=False))
    frags.append(arrow(750, 360, 750, 395, color=FIELD))

    frags.append(fitbox(545, 395, 410, 65, "Контур оцінювання EKF2 (Цільовий алгоритм)\nПідключення GDB, модифікація коду фільтра,\nваріація шумових параметрів без ризику падіння борту", size=10, fill="#ffffff", stroke=FIELD, bold=False))
    frags.append(arrow(750, 460, 750, 485, color=FIELD))

    frags.append(fitbox(545, 485, 410, 50, "Діагностичний вивід та Root Cause Analysis\nНовий переграний ULog-файл, графіки інновацій, порівняння", size=10, fill="#f0fdf4", stroke=FIELD, bold=False))

    render(path, w, h, *frags)


def build_deterministic_time_reconstruction(path):
    """Фігура 2: Часова діаграма відновлення подій та дискретна синхронізація часу."""
    w, h = 1000, 530
    frags = []

    frags.append(text(500, 26, "Дискретне квантування часу та впорядкування сенсорних потоків у черзі переграшу", size=15, bold=True))

    # Головна вісь віртуального часу
    frags.append(rect(40, 50, 920, 85, fill="#f8fafc", stroke=LINE, rx=5))
    frags.append(text(60, 75, "Віртуальна шкала часу Simulated Time (t_sim)", size=12, bold=True, anchor="start", color=FIELD))
    frags.append(line(80, 108, 900, 108, color=LINE, sw=2))

    # Засічки часу
    times = [
        (120, "1000000 мкс", "Крок 0"),
        (280, "1001000 мкс", "Крок 1 (+1 мс)"),
        (440, "1002000 мкс", "Крок 2 (+2 мс)"),
        (600, "1003000 мкс", "Крок 3 (+3 мс)"),
        (760, "1004000 мкс", "Крок 4 (+4 мс)"),
    ]
    for x, t_val, step_lbl in times:
        frags.append(line(x, 102, x, 114, color=LINE, sw=2))
        frags.append(text(x, 96, t_val, size=9, color=MUTED))
        frags.append(text(x, 126, step_lbl, size=9, bold=True, color=INK))

    # Потоки сенсорів з логу
    frags.append(rect(40, 145, 920, 215, fill="#ffffff", stroke="#cbd5e1", rx=5))
    frags.append(text(60, 168, "Багаточастотні пакети з ULog (вхідна черга пріоритетів за міткою часу)", size=12, bold=True, anchor="start", color=INK))

    # IMU
    frags.append(text(60, 198, "IMU (1000 Гц):", size=10, bold=True, anchor="start", color=NEG))
    frags.append(line(160, 194, 910, 194, color="#e2e8f0", sw=1))
    imu_pts = [120, 160, 200, 240, 280, 320, 360, 400, 440, 480, 520, 560, 600, 640, 680, 720, 760, 800, 840, 880]
    for pt in imu_pts:
        frags.append(circle(pt, 194, 4, fill=NEG, stroke=NEG))

    # Baro
    frags.append(text(60, 238, "Baro (100 Гц):", size=10, bold=True, anchor="start", color=POS))
    frags.append(line(160, 234, 910, 234, color="#e2e8f0", sw=1))
    baro_pts = [120, 280, 440, 600, 760]
    for pt in baro_pts:
        frags.append(rect(pt - 5, 229, 10, 10, fill=POS, stroke=POS, rx=2))

    # Mag
    frags.append(text(60, 278, "Mag (50 Гц):", size=10, bold=True, anchor="start", color="#8b5cf6"))
    frags.append(line(160, 274, 910, 274, color="#e2e8f0", sw=1))
    mag_pts = [120, 440, 760]
    for pt in mag_pts:
        frags.append(rect(pt - 5, 269, 10, 10, fill="#8b5cf6", stroke="#8b5cf6", rx=2))

    # GNSS
    frags.append(text(60, 318, "GNSS (10 Гц):", size=10, bold=True, anchor="start", color=FIELD))
    frags.append(line(160, 314, 910, 314, color="#e2e8f0", sw=1))
    gnss_pts = [280, 760]
    for pt in gnss_pts:
        frags.append(circle(pt, 314, 6, fill=FIELD, stroke=FIELD))

    # Легенда сенсорів
    frags.append(text(300, 345, "● IMU (Acc/Gyro)", size=9, color=NEG, bold=True))
    frags.append(text(480, 345, "■ Baro (Pressure/Alt)", size=9, color=POS, bold=True))
    frags.append(text(660, 345, "■ Mag (Heading)", size=9, color="#8b5cf6", bold=True))
    frags.append(text(840, 345, "● GNSS (Pos/Vel/Fix)", size=9, color=FIELD, bold=True))

    # Нижній блок: Синхронізація обчислювального кроку EKF
    frags.append(rect(40, 370, 920, 135, fill="#f8fafc", stroke=LINE, rx=5))
    frags.append(text(60, 393, "Механізм кроку симуляції Lockstep Execution (Без гонок потоків)", size=12, bold=True, anchor="start", color=INK))

    frags.append(fitbox(60, 408, 270, 80, "1. Вибірка з черги пріоритетів\nВилучення всіх повідомлень\nіз міткою t_msg <= t_sim_next", size=10, fill="#ffffff", stroke="#cbd5e1", bold=False))
    frags.append(arrow(335, 448, 365, 448, color=LINE))

    frags.append(fitbox(365, 408, 270, 80, "2. Публікація в uORB та крок EKF\nАтомарне оновлення буферів\nВиклик прогнозу і корекції EKF2", size=10, fill="#ffffff", stroke=FIELD, bold=False))
    frags.append(arrow(640, 448, 670, 448, color=LINE))

    frags.append(fitbox(670, 408, 270, 80, "3. Просування віртуального часу\nt_sim = t_sim + dt_step\nСкидання вихідного логу на диск", size=10, fill="#ffffff", stroke="#cbd5e1", bold=False))

    render(path, w, h, *frags)


def main():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)

    fig1_path = os.path.join(img_dir, "replay-injection-architecture.svg")
    build_replay_injection_architecture(fig1_path)
    print(f"Згенеровано: {fig1_path}")

    fig2_path = os.path.join(img_dir, "deterministic-time-reconstruction.svg")
    build_deterministic_time_reconstruction(fig2_path)
    print(f"Згенеровано: {fig2_path}")


if __name__ == "__main__":
    main()
