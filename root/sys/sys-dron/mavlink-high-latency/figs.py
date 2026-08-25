# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми mavlink-high-latency (Протокол великої затримки MAVLink)."""

import os
import sys

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_high_latency_architecture():
    """Фігура 1: Архітектура каналів зв'язку БПЛА: радіолінія прямої видимості та супутниковий міст."""
    W, H = 840, 470
    p = []

    # Загальний контур
    p.append(rect(15, 15, 810, 440, fill="#fdfefe", stroke=LINE, sw=1.2, rx=8))
    p.append(text(420, 38, "Архітектура каналів зв'язку БПЛА: лінія прямої видимості та супутниковий міст", size=13, color=INK, bold=True))

    # Бортовий апарат (верхня частина)
    p.append(rect(35, 60, 770, 130, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(420, 80, "Бортовий комплекс безпілотного апарата (БПЛА)", size=12, color=INK, bold=True))

    # FCU
    p.append(rect(50, 95, 200, 80, fill="#eff6ff", stroke=NEG, sw=1.5, rx=5))
    p.append(text(150, 118, "Автопілот (FCU)", size=11, color=NEG, bold=True))
    p.append(mtext(150, 138, "PX4 / ArduPilot\nДиспетчер потоків MAVLink", size=9.5, color=INK))

    # MAVLink Router / Demux
    p.append(rect(290, 95, 220, 80, fill="#f8fafc", stroke=LINE, sw=1.2, rx=5))
    p.append(text(400, 118, "Маршрутизатор каналів", size=11, color=INK, bold=True))
    p.append(mtext(400, 138, "Визначення стану каналів\nПеремикання Standard ↔ HLP", size=9.5, color=MUTED))

    p.append(arrow(250, 135, 290, 135, color=LINE, sw=1.5))

    # Бортові модеми
    # RF Modem
    p.append(rect(550, 95, 115, 38, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(607, 118, "RF-модем (UART1)", size=9.5, color=FIELD, bold=True))

    # Satellite Modem
    p.append(rect(550, 137, 115, 38, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=4))
    p.append(text(607, 160, "Iridium SBD (UART2)", size=9.5, color="#92400e", bold=True))

    p.append(arrow(510, 114, 550, 114, color=FIELD, sw=1.5))
    p.append(arrow(510, 156, 550, 156, color="#d97706", sw=1.5))

    # Бортові антени
    p.append(circle(710, 114, 15, fill="#f0fdf4", stroke=FIELD, sw=1.2))
    p.append(text(710, 119, "433M", size=9, color=FIELD, bold=True))

    p.append(circle(710, 156, 15, fill="#fef3c7", stroke="#d97706", sw=1.2))
    p.append(text(710, 160, "SAT", size=9, color="#92400e", bold=True))

    p.append(line(665, 114, 695, 114, color=FIELD, sw=1.2))
    p.append(line(665, 156, 695, 156, color="#d97706", sw=1.2))

    # Середня зона: Канали передачі даних
    # Лінія RF
    p.append(rect(35, 205, 375, 115, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(222, 226, "Основний канал: Пряма радіовидимість (LOS)", size=11, color=FIELD, bold=True))
    p.append(mtext(222, 248, "Частота: 433 / 868 / 915 МГц або Wi-Fi / COFDM\nПропускна здатність: 57.6 .. 115.2 кбіт/с\nЗатримка (RTT): 20 .. 80 мс\nПовний потік телеметрії: 2000 байт/с (10..50 Гц)", size=9.5, color=INK))

    # Лінія SAT
    p.append(rect(430, 205, 375, 115, fill="#fffbeb", stroke="#d97706", sw=1.2, rx=6))
    p.append(text(617, 226, "Резервний канал: Супутниковий зв'язок (BVLOS)", size=11, color="#92400e", bold=True))
    p.append(mtext(617, 248, "Супутникова мережа: Iridium SBD / Inmarsat IDP\nПропускна здатність: лімітовані пакети (SBD ~340 B)\nЗатримка (RTT): 5 .. 30 секунд\nАгреговане повідомлення HIGH_LATENCY2: 3.85 байт/с", size=9.5, color=INK))

    # З'єднувальні стрілки зверху вниз
    p.append(arrow(607, 195, 222, 205, color=FIELD, sw=1.5))
    p.append(arrow(607, 195, 617, 205, color="#d97706", sw=1.5))

    # Наземний сегмент (нижня частина)
    p.append(rect(35, 335, 770, 105, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(420, 355, "Наземна станція керування (GCS: QGroundControl / Mission Planner)", size=12, color=INK, bold=True))

    p.append(rect(50, 370, 350, 58, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(225, 388, "Режим прямого зв'язку (Standard)", size=10.5, color=FIELD, bold=True))
    p.append(mtext(225, 407, "Плавний авіагоризонт, жива телеметрія 20 Гц,\nмиттєве підтвердження команд оператора", size=9.5, color=INK))

    p.append(rect(440, 370, 350, 58, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=4))
    p.append(text(615, 388, "Режим високої затримки (High Latency)", size=10.5, color="#92400e", bold=True))
    p.append(mtext(615, 407, "Оновлення позиції 1 раз на 20..100 с, тайм-аути\nкоманд 60 с, відображення бітових прапорців відмов", size=9.5, color=INK))

    p.append(arrow(222, 320, 222, 370, color=FIELD, sw=1.5))
    p.append(arrow(617, 320, 617, 370, color="#d97706", sw=1.5))

    render(os.path.join(OUT, "high-latency-architecture.svg"), W, H, *p)


def fig_high_latency2_packet_structure():
    """Фігура 2: Анатомія агрегованого кадру HIGH_LATENCY2 (#235) та методи квантування."""
    W, H = 840, 480
    p = []

    p.append(rect(15, 15, 810, 450, fill="#fdfefe", stroke=LINE, sw=1.2, rx=8))
    p.append(text(420, 38, "Анатомія повідомлення HIGH_LATENCY2 (#235): 65 байтів агрегованого стану", size=13, color=INK, bold=True))

    # Верхній блок: Повний MAVLink 2 кадр
    p.append(rect(25, 55, 790, 80, fill="#ffffff", stroke=LINE, sw=1.0, rx=6))
    p.append(text(420, 72, "Структура кадру MAVLink v2 на фізичному каналі (Загальний розмір: 77 байтів без підпису)", size=11, color=MUTED, bold=True))

    # Заголовок
    p.append(rect(35, 85, 120, 40, fill="#ffffff", stroke=LINE, sw=1.2, rx=3))
    p.append(mtext(95, 102, "Заголовок v2 (10 B)\nSTX, LEN=65, ID=235", size=9.5, color=INK, bold=True))

    # Payload
    p.append(rect(160, 85, 540, 40, fill="#eff6ff", stroke=NEG, sw=1.8, rx=3))
    p.append(mtext(430, 102, "Корисне навантаження HIGH_LATENCY2 (65 байтів)\nАгреговані та квантовані навігаційні, системні й діагностичні поля", size=9.5, color=NEG, bold=True))

    # CRC
    p.append(rect(705, 85, 100, 40, fill="#ffffff", stroke=LINE, sw=1.2, rx=3))
    p.append(mtext(755, 102, "CRC-16 (2 B)\nCRC_EXTRA=179", size=9.5, color=INK, bold=True))

    # Деталізація Payload (65 байтів)
    p.append(rect(25, 145, 790, 310, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    p.append(text(420, 165, "Розподіл 65 байтів корисного навантаження за функціональними групами", size=11.5, color=INK, bold=True))

    # Група 1: Ідентифікація та режим (8 B)
    p.append(rect(35, 180, 245, 125, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(157, 198, "Ідентифікація та режим (8 B)", size=10.5, color=INK, bold=True))
    p.append(mtext(157, 218, "timestamp (uint32_t, 4 B) — час у мс\ntype (uint8_t, 1 B) — тип апарата\nautopilot (uint8_t, 1 B) — тип автопілота\ncustom_mode (uint16_t, 2 B) — польотний режим", size=9.5, color=MUTED))

    # Група 2: Високоточні координати (8 B)
    p.append(rect(290, 180, 245, 125, fill="#ffffff", stroke=POS, sw=1.5, rx=4))
    p.append(text(412, 198, "Глобальна позиція (8 B)", size=10.5, color=POS, bold=True))
    p.append(mtext(412, 218, "latitude (int32_t, 4 B) — 1e-7 град (~1.1 см)\nlongitude (int32_t, 4 B) — 1e-7 град\nЗбереження повної точності GPS\nбез втрати розрізнення", size=9.5, color=INK))

    # Група 3: Квантована навігація (10 B)
    p.append(rect(545, 180, 260, 125, fill="#ffffff", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(675, 198, "Квантована навігація (10 B)", size=10.5, color=FIELD, bold=True))
    p.append(mtext(675, 218, "altitude (int16_t, 2 B) — висота в метрах\ntarget_altitude (int16_t, 2 B) — ціль у метрах\nheading (uint8_t, 1 B) — курс / 2 (0..358°)\ntarget_heading (uint8_t, 1 B) — ціль / 2\ntarget_distance (uint16_t, 2 B) — 10 м кроки\nwp_num (uint16_t, 2 B) — номер точки місії", size=9, color=INK))

    # Група 4: Швидкості та тяга (5 B)
    p.append(rect(35, 315, 245, 130, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(157, 333, "Швидкості та тяга (5 B)", size=10.5, color=INK, bold=True))
    p.append(mtext(157, 353, "throttle (uint8_t, 1 B) — газ 0..100%\nairspeed (uint8_t, 1 B) — м/с × 5\nairspeed_sp (uint8_t, 1 B) — завдання м/с × 5\ngroundspeed (uint8_t, 1 B) — шлях. шв. × 5\nclimb_rate (int8_t, 1 B) — вертик. шв. × 10", size=9, color=MUTED))

    # Група 5: Живлення та сенсори (6 B)
    p.append(rect(290, 315, 245, 130, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(412, 333, "Живлення та сенсори (6 B)", size=10.5, color=INK, bold=True))
    p.append(mtext(412, 353, "battery_remaining (int8_t, 1 B) — %\ncurrent_battery (int16_t, 2 B) — 0.1 А\ntemperature (int8_t, 1 B) — темп. автопілота\ntemperature_air (int8_t, 1 B) — темп. повітря\nfailsafe (uint8_t, 1 B) — статус failsafe", size=9, color=MUTED))

    # Група 6: Діагностика відмов (5 B)
    p.append(rect(545, 315, 260, 130, fill="#fff5f5", stroke=POS, sw=1.5, rx=4))
    p.append(text(675, 333, "Діагностика відмов (5 B)", size=10.5, color=POS, bold=True))
    p.append(mtext(675, 353, "failure_flags (uint16_t, 2 B) — бітова маска:\n  HL_FAILURE_FLAG_GPS / COMPASS\n  HL_FAILURE_FLAG_BATTERY / RC\n  HL_FAILURE_FLAG_AIRSPEED / ENGINE\ncustom0..2 (int8_t, 3 B) — дані користувача", size=9, color=POS, bold=True))

    render(os.path.join(OUT, "high-latency2-packet-structure.svg"), W, H, *p)


def fig_control_mode_handshake():
    """Фігура 3: Алгоритм перемикання режимів зв'язку та керування MAV_CMD_CONTROL_HIGH_LATENCY."""
    W, H = 840, 440
    p = []

    p.append(rect(15, 15, 810, 410, fill="#fdfefe", stroke=LINE, sw=1.2, rx=8))
    p.append(text(420, 38, "Перемикання та керування режимом High Latency (MAV_CMD_CONTROL_HIGH_LATENCY)", size=13, color=INK, bold=True))

    # Колоночні ролі
    p.append(rect(45, 55, 210, 40, fill="#eff6ff", stroke=NEG, sw=1.2, rx=4))
    p.append(text(150, 80, "Наземна станція (GCS)", size=11, color=NEG, bold=True))

    p.append(rect(315, 55, 210, 40, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=4))
    p.append(text(420, 80, "Супутниковий шлюз / SBD", size=11, color="#92400e", bold=True))

    p.append(rect(585, 55, 210, 40, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(690, 80, "Бортовий автопілот (FCU)", size=11, color=FIELD, bold=True))

    # Пунктирні вертикальні лінії (розбиті на сегменти щоб не перетинати блоки)
    # GCS (x=150)
    p.append(line(150, 95, 150, 115, color=MUTED, sw=1.2, dash="4,3"))
    p.append(line(150, 170, 150, 240, color=MUTED, sw=1.2, dash="4,3"))
    p.append(line(150, 305, 150, 335, color=MUTED, sw=1.2, dash="4,3"))
    p.append(line(150, 385, 150, 395, color=MUTED, sw=1.2, dash="4,3"))

    # SBD (x=420)
    p.append(line(420, 95, 420, 185, color=MUTED, sw=1.2, dash="4,3"))
    p.append(line(420, 235, 420, 275, color=MUTED, sw=1.2, dash="4,3"))
    p.append(line(420, 330, 420, 395, color=MUTED, sw=1.2, dash="4,3"))

    # FCU (x=690)
    p.append(line(690, 95, 690, 115, color=MUTED, sw=1.2, dash="4,3"))
    p.append(line(690, 175, 690, 205, color=MUTED, sw=1.2, dash="4,3"))
    p.append(line(690, 260, 690, 345, color=MUTED, sw=1.2, dash="4,3"))
    p.append(line(690, 390, 690, 395, color=MUTED, sw=1.2, dash="4,3"))

    # Подія 1: Втрата прямого радіозв'язку
    p.append(rect(595, 115, 190, 55, fill="#fff5f5", stroke=POS, sw=1.5, rx=3))
    p.append(mtext(690, 133, "LOS Timeout: Heartbeat > 10 с\nВтрата прямої радіолінії!\nАктивація HLP Failsafe", size=9.5, color=POS, bold=True))

    p.append(arrow(690, 175, 690, 205, color=POS, sw=1.5))

    # Подія 2: FCU генерує HIGH_LATENCY2
    p.append(rect(595, 205, 190, 50, fill="#ffffff", stroke=FIELD, sw=1.2, rx=3))
    p.append(mtext(690, 223, "Зупинка потоків 20 Гц\nГенерація HIGH_LATENCY2\nВідправка в UART модема", size=9.5, color=FIELD, bold=True))

    # Передача в SBD модем
    p.append(arrow(595, 230, 425, 230, color="#d97706", sw=1.8))
    p.append(text(510, 222, "AT+SBDWT (65 B)", size=9.5, color="#92400e", bold=True))

    # Подія 3: SBD сесія в космос
    p.append(rect(325, 240, 190, 45, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=3))
    p.append(mtext(420, 258, "Сесія Iridium SBDIX\nЗатримка каналу: 5..15 с", size=9.5, color="#92400e", bold=True))

    p.append(arrow(325, 262, 155, 262, color=NEG, sw=1.8))
    p.append(text(240, 254, "HIGH_LATENCY2 (#235)", size=9.5, color=NEG, bold=True))

    # Подія 4: GCS адаптується
    p.append(rect(55, 265, 190, 40, fill="#eff6ff", stroke=NEG, sw=1.2, rx=3))
    p.append(mtext(150, 282, "GCS: режим High Latency\nЗбільшення тайм-аутів до 60 с", size=9, color=NEG, bold=True))

    # Подія 5: Команда відновлення або примусового перемикання
    p.append(rect(55, 335, 190, 48, fill="#ffffff", stroke=LINE, sw=1.2, rx=3))
    p.append(mtext(150, 352, "Оператор: MAV_CMD_CONTROL_\nHIGH_LATENCY (#2600)\nparam1 = 1 (вкл) або 0 (викл)", size=9, color=INK, bold=True))

    p.append(arrow(245, 360, 685, 360, color=LINE, sw=1.8))
    p.append(text(465, 352, "COMMAND_LONG (#2600) через SBD/RF", size=9.5, color=INK, bold=True))

    p.append(rect(595, 345, 190, 45, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=3))
    p.append(mtext(690, 363, "COMMAND_ACK (ACCEPTED)\nЗміна темпу або вимкнення HLP", size=9.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "control-mode-handshake.svg"), W, H, *p)


def fig_bandwidth_cost_comparison():
    """Фігура 4: Порівняння трафіку та вартості каналу: стандартна телеметрія проти HIGH_LATENCY2."""
    W, H = 840, 440
    p = []

    p.append(rect(15, 15, 810, 410, fill="#fdfefe", stroke=LINE, sw=1.2, rx=8))
    p.append(text(420, 38, "Порівняння обсягу трафіку та вартості: Стандартний потік vs HIGH_LATENCY2", size=13, color=INK, bold=True))

    # Порівняльні стовпчики: Трафік
    p.append(rect(35, 60, 375, 180, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(222, 82, "Швидкість передачі даних (Traffic Rate)", size=11.5, color=INK, bold=True))

    # Стовпчик 1: Стандартна телеметрія
    p.append(rect(55, 105, 150, 115, fill="#fee2e2", stroke=POS, sw=1.5, rx=4))
    p.append(text(130, 125, "Стандартний потік", size=10, color=POS, bold=True))
    p.append(mtext(130, 150, "2000 байт/с\n(16.0 кбіт/с)\n7.2 МБ / год", size=10, color=POS, bold=True))
    p.append(text(130, 205, "100% (базовий)", size=9, color=MUTED))

    # Стовпчик 2: HIGH_LATENCY2 (0.05 Гц)
    p.append(rect(235, 145, 150, 75, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(310, 165, "HIGH_LATENCY2 (0.05 Гц)", size=9.5, color=FIELD, bold=True))
    p.append(mtext(310, 185, "3.85 байт/с (13.8 КБ/год)\nЕкономія: 99.8%", size=9, color=FIELD, bold=True))
    p.append(text(310, 210, "Стиснення ~520 : 1", size=9, color=FIELD, bold=True))

    # Порівняльні стовпчики: Фінансові витрати (Iridium SBD)
    p.append(rect(430, 60, 375, 180, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(617, 82, "Фінансові витрати через Iridium SBD ($ / год)", size=11.5, color=INK, bold=True))

    # Стовпчик 1: Без оптимізації
    p.append(rect(450, 105, 150, 115, fill="#fee2e2", stroke=POS, sw=1.5, rx=4))
    p.append(text(525, 125, "Без HLP (неприпустимо)", size=9.5, color=POS, bold=True))
    p.append(mtext(525, 150, "~$12 000 / год\n(240 000 SBD msg)\nКанал перевантажено", size=9.5, color=POS, bold=True))
    p.append(text(525, 205, "Буфер переповнено", size=9, color=POS))

    # Стовпчик 2: З HIGH_LATENCY2
    p.append(rect(630, 145, 150, 75, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(705, 165, "З HIGH_LATENCY2 (0.05 Гц)", size=9.5, color=FIELD, bold=True))
    p.append(mtext(705, 185, "180 SBD msg / год\n~$9.00 / год", size=9.5, color=FIELD, bold=True))
    p.append(text(705, 210, "0.01 Гц: ~$1.80 / год", size=9, color=FIELD, bold=True))

    # Нижня частина: Таблиця порівняння параметрів
    p.append(rect(35, 255, 770, 155, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    p.append(text(420, 275, "Зведена таблиця характеристик протоколів телеметрії", size=11, color=INK, bold=True))

    # Рядки таблиці
    p.append(rect(45, 290, 750, 30, fill="#ffffff", stroke=LINE, sw=1.0, rx=3))
    p.append(text(130, 310, "Параметр", size=9.5, color=MUTED, bold=True))
    p.append(text(310, 310, "Стандартна телеметрія (RF)", size=9.5, color=MUTED, bold=True))
    p.append(text(510, 310, "HIGH_LATENCY2 (0.05 Гц)", size=9.5, color=MUTED, bold=True))
    p.append(text(690, 310, "HIGH_LATENCY2 (0.01 Гц)", size=9.5, color=MUTED, bold=True))

    p.append(rect(45, 323, 750, 24, fill="#fdfefe", stroke=LINE, sw=0.6, rx=2))
    p.append(text(130, 339, "Період передачі", size=9, color=INK))
    p.append(text(310, 339, "20..100 мс (10..50 Гц)", size=9, color=INK))
    p.append(text(510, 339, "20 секунд (0.05 Гц)", size=9, color=FIELD, bold=True))
    p.append(text(690, 339, "100 секунд (0.01 Гц)", size=9, color=FIELD, bold=True))

    p.append(rect(45, 349, 750, 24, fill="#ffffff", stroke=LINE, sw=0.6, rx=2))
    p.append(text(130, 365, "Розмір за транзакцію", size=9, color=INK))
    p.append(text(310, 365, "20..40 пакетів/с (~2000 B)", size=9, color=INK))
    p.append(text(510, 365, "1 пакет = 77 байтів", size=9, color=FIELD, bold=True))
    p.append(text(690, 365, "1 пакет = 77 байтів", size=9, color=FIELD, bold=True))

    p.append(rect(45, 375, 750, 24, fill="#fdfefe", stroke=LINE, sw=0.6, rx=2))
    p.append(text(130, 391, "Цільове призначення", size=9, color=INK))
    p.append(text(310, 391, "Ручне керування, FPV, посадка", size=9, color=INK))
    p.append(text(510, 391, "BVLOS патрулювання, моніторинг", size=9, color=FIELD, bold=True))
    p.append(text(690, 391, "Трансокеанські місії, автономія", size=9, color=FIELD, bold=True))

    render(os.path.join(OUT, "bandwidth-cost-comparison.svg"), W, H, *p)


if __name__ == "__main__":
    fig_high_latency_architecture()
    fig_high_latency2_packet_structure()
    fig_control_mode_handshake()
    fig_bandwidth_cost_comparison()
    print("Всі 4 SVG-фігури успішно згенеровано.")
