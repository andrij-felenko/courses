# -*- coding: utf-8 -*-
"""Генерація SVG-ілюстрацій для теми flight-log-formats."""

import os
import sys

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    BG, FIELD, FILL, FONT, INK, LINE, MUTED, NEG, POS,
    arrow, circle, fitbox, line, mtext, rect, render, text, textbox,
)

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_ring_buffer_sd_latency():
    """Ілюстрація: архітектура буферизації логів та вплив затримок SD-карти."""
    w, h = 880, 480
    frags = []

    # Заголовок зверху
    frags.append(text(440, 30, "Архітектура логування: кільцевий буфер RAM та затримки запису SD", size=16, bold=True))

    # Секція 1: Високочастотні потоки реального часу (RTOS)
    frags.append(rect(30, 60, 230, 240, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    frags.append(text(145, 85, "Потоки реального часу (RTOS)", size=13, bold=True, color=INK))

    frags.append(fitbox(45, 105, 200, 42, "Опитування IMU / Давачі\n1000–2000 Гц (DMA/SPI)", size=12, fill="#eaf2fd", stroke=NEG))
    frags.append(fitbox(45, 160, 200, 42, "Оцінювач стану (EKF2/EKF3)\n250–400 Гц (Hard Real-Time)", size=12, fill="#eaf2fd", stroke=NEG))
    frags.append(fitbox(45, 215, 200, 42, "Контур стабілізації (PID)\n400–1000 Гц (Керування)", size=12, fill="#eaf2fd", stroke=NEG))

    frags.append(text(145, 280, "Постійний потік: 50–250 КБ/с", size=11, bold=True, color=NEG))

    # Стрілки від RTOS до Кільцевого буфера
    frags.append(arrow(245, 126, 305, 160, color=NEG, sw=2))
    frags.append(arrow(245, 181, 305, 180, color=NEG, sw=2))
    frags.append(arrow(245, 236, 305, 200, color=NEG, sw=2))

    # Секція 2: Lockless Ring Buffer в SRAM
    frags.append(rect(310, 60, 260, 240, fill="#fdfefe", stroke=LINE, sw=2, rx=8))
    frags.append(text(440, 85, "Lockless Ring Buffer (SRAM)", size=13, bold=True, color=INK))
    frags.append(text(440, 103, "Місткість: 32–256 КБ (Atomic Head/Tail)", size=11, color=MUTED))

    # Візуалізація сегментів буфера
    # Записані дані
    frags.append(rect(330, 120, 140, 45, fill="#d5e8d4", stroke=FIELD, sw=1.5, rx=4))
    frags.append(text(400, 147, "Дані в черзі", size=12, bold=True, color=FIELD))

    # Вільний простір
    frags.append(rect(470, 120, 80, 45, fill="#f5f5f5", stroke=MUTED, sw=1.5, rx=4))
    frags.append(text(510, 147, "Вільний", size=12, color=MUTED))

    # Покажчики Head / Tail
    frags.append(line(470, 115, 470, 170, color=POS, sw=2))
    frags.append(text(470, 182, "Head (Запис)", size=11, bold=True, color=POS))

    frags.append(line(330, 115, 330, 170, color=NEG, sw=2))
    frags.append(text(330, 182, "Tail (Зчитування)", size=11, bold=True, color=NEG))

    frags.append(fitbox(330, 205, 220, 48, "При переповненні:\nфіксація Drop / лічильника втрат", size=11, fill="#fdecea", stroke=POS))
    frags.append(text(440, 280, "Атомарний рух без блокувань", size=11, italic=True, color=MUTED))

    # Стрілка від буфера до фонового потоку
    frags.append(arrow(570, 180, 625, 180, color=LINE, sw=2))

    # Секція 3: Низькопріоритетний потік та накопичувач
    frags.append(rect(630, 60, 220, 240, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    frags.append(text(740, 85, "Фоновий запис (SD / Flash)", size=13, bold=True, color=INK))

    frags.append(fitbox(645, 110, 190, 45, "Logger Thread (Low Priority)\nБлоки 512–4096 байтів", size=11, fill="#f4f6f8", stroke=LINE))
    frags.append(arrow(740, 155, 740, 180, color=LINE, sw=1.5))
    frags.append(fitbox(645, 180, 190, 45, "FATFS / LittleFS\nSDMMC / SPI DMA", size=11, fill="#f4f6f8", stroke=LINE))
    frags.append(arrow(740, 225, 740, 245, color=LINE, sw=1.5))
    frags.append(fitbox(645, 245, 190, 40, "MicroSD (NAND Flash)", size=12, bold=True, fill="#fff2cc", stroke="#d6b656"))

    # Секція 4: Часова діаграма затримок SD-карти (нижня частина)
    frags.append(rect(30, 320, 820, 140, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(440, 342, "Часова шкала запису на SD: вплив сплесків затримки (Latency Spikes)", size=13, bold=True))

    # Вісь часу
    frags.append(arrow(50, 420, 830, 420, color=LINE, sw=2))
    frags.append(text(830, 438, "Час (t)", size=11, bold=True, anchor="end"))

    # Звичайний запис (короткі імпульси затримки)
    for x in (80, 140, 200, 260):
        frags.append(rect(x, 395, 25, 25, fill="#d5e8d4", stroke=FIELD, sw=1))
        frags.append(text(x + 12, 388, "1–2 мс", size=9, color=FIELD))

    frags.append(text(170, 440, "Нормальний запис блоків по 4 КБ", size=11, color=FIELD))

    # Сплеск затримки (NAND Erase / GC)
    frags.append(rect(340, 370, 280, 50, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    frags.append(text(480, 392, "Сплеск затримки контролера SD: 100–250 мс", size=12, bold=True, color=POS))
    frags.append(text(480, 410, "Збирання сміття (GC) та стирання блоків NAND (1–4 МБ)", size=11, color=POS))

    # Рівень буфера під час сплеску
    frags.append(text(480, 440, "Кільцевий буфер поглинає накопичені 25–50 КБ даних або переповнюється", size=11, color=POS, italic=True))

    # Відновлення після сплеску
    for x in (670, 730, 790):
        frags.append(rect(x, 395, 25, 25, fill="#d5e8d4", stroke=FIELD, sw=1))
        frags.append(text(x + 12, 388, "1–2 мс", size=9, color=FIELD))
    frags.append(text(745, 440, "Скидання буфера", size=11, color=FIELD))

    return render(os.path.join(IMG_DIR, "ring-buffer-sd-latency.svg"), w, h, *frags)


def fig_ulog_binary_layout():
    """Ілюстрація: побайтова структура двійкового формату PX4 ULog."""
    w, h = 880, 500
    frags = []

    frags.append(text(440, 30, "Побайтова структура та типи секцій формату PX4 ULog", size=16, bold=True))

    # Рівень 1: Заголовок файлу (File Header)
    frags.append(rect(30, 60, 820, 75, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(440, 82, "Заголовок файлу ULog (16 байтів)", size=13, bold=True))

    # Поля заголовка
    frags.append(fitbox(45, 95, 260, 30, "Магічні байти: 0x55 0x4C 0x6F 0x67 (ULog)", size=11, bold=True, fill="#fff2cc", stroke="#d6b656"))
    frags.append(fitbox(315, 95, 110, 30, "Версія: 0x01", size=11, fill="#eaf2fd", stroke=NEG))
    frags.append(fitbox(435, 95, 130, 30, "Сумісність: 0x12 0x35", size=11, fill="#eaf2fd", stroke=NEG))
    frags.append(fitbox(575, 95, 260, 30, "Часова мітка старту: uint64_t (мкс)", size=11, bold=True, fill="#d5e8d4", stroke=FIELD))

    # Рівень 2: Секція визначень та метаданих (Definitions Section)
    frags.append(rect(30, 150, 820, 145, fill="#ffffff", stroke=MUTED, sw=1.5, rx=6))
    frags.append(text(160, 172, "Секція визначень та метаданих", size=13, bold=True, color=INK))

    # Повідомлення 'F' - Format
    frags.append(rect(45, 185, 375, 45, fill="#eaf2fd", stroke=NEG, sw=1.2, rx=4))
    frags.append(text(232, 202, "Тип 'F' (Format) — схема повідомлення uORB", size=11, bold=True, color=NEG))
    frags.append(text(232, 218, "format_name:uint64_t timestamp;float[3] gyro_rad;...", size=10, color=INK))

    # Повідомлення 'I' / 'M' - Info
    frags.append(rect(430, 185, 405, 45, fill="#f3e5f5", stroke="#8e24aa", sw=1.2, rx=4))
    frags.append(text(632, 202, "Тип 'I' / 'M' (Information) — метадані системи", size=11, bold=True, color="#8e24aa"))
    frags.append(text(632, 218, "key_len (uint8) + key_name (string) + value (sys_name, ver_sw)", size=10, color=INK))

    # Повідомлення 'P' - Parameter
    frags.append(rect(45, 240, 375, 45, fill="#fff2cc", stroke="#d6b656", sw=1.2, rx=4))
    frags.append(text(232, 257, "Тип 'P' (Parameter) — початкові параметри", size=11, bold=True, color="#b78103"))
    frags.append(text(232, 273, "key_len + key_name + value (MC_ROLL_P, MPC_XY_VEL_MAX)", size=10, color=INK))

    # Повідомлення 'A' - Add subscription
    frags.append(rect(430, 240, 405, 45, fill="#d5e8d4", stroke=FIELD, sw=1.2, rx=4))
    frags.append(text(632, 257, "Тип 'A' (Add Logged Msg) — підписка на потік", size=11, bold=True, color=FIELD))
    frags.append(text(632, 273, "multi_id (uint8) + msg_id (uint16) + message_name", size=10, color=INK))

    # Рівень 3: Секція даних реального часу (Data Section)
    frags.append(rect(30, 310, 820, 170, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(150, 332, "Секція даних реального часу", size=13, bold=True, color=INK))

    # Структура контейнера повідомлення ULog
    frags.append(rect(45, 345, 790, 40, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    frags.append(fitbox(50, 350, 120, 30, "msg_size (uint16)", size=11, bold=True, fill="#eaf2fd", stroke=NEG))
    frags.append(fitbox(175, 350, 110, 30, "msg_type (uint8)", size=11, bold=True, fill="#fff2cc", stroke="#d6b656"))
    frags.append(fitbox(290, 350, 540, 30, "Корисне навантаження (довжина = msg_size байтів)", size=11, fill="#f4f6f8", stroke=LINE))

    # Повідомлення 'D' - Data
    frags.append(rect(45, 395, 375, 45, fill="#d5e8d4", stroke=FIELD, sw=1.2, rx=4))
    frags.append(text(232, 412, "Тип 'D' (Data) — бінарні вибірки", size=11, bold=True, color=FIELD))
    frags.append(text(232, 428, "msg_id (uint16) + бінарне тіло згідно зі схемою 'F'", size=10, color=INK))

    # Повідомлення 'L' - Log text
    frags.append(rect(430, 395, 405, 45, fill="#f4f6f8", stroke=MUTED, sw=1.2, rx=4))
    frags.append(text(632, 412, "Тип 'L' / 'C' (Log String) — текстові логи", size=11, bold=True, color=INK))
    frags.append(text(632, 428, "log_level (uint8) + timestamp (uint64) + UTF-8 string", size=10, color=MUTED))

    # Повідомлення 'S' - Sync / Dropout
    frags.append(rect(45, 445, 790, 25, fill="#fdecea", stroke=POS, sw=1.2, rx=4))
    frags.append(text(440, 462, "Тип 'S' (Sync / Dropout): тривалість пропуску duration (uint16, мс) — маркер втрати пакетів", size=11, bold=True, color=POS))

    return render(os.path.join(IMG_DIR, "ulog-binary-layout.svg"), w, h, *frags)


def fig_dataflash_binary_layout():
    """Ілюстрація: побайтова структура формату ArduPilot DataFlash (.BIN)."""
    w, h = 880, 480
    frags = []

    frags.append(text(440, 30, "Побайтова структура та самоописні кадри ArduPilot DataFlash (BIN)", size=16, bold=True))

    # Загальний вигляд потоку кадрування
    frags.append(rect(30, 60, 820, 75, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(440, 82, "Кадрування потоку DataFlash: кожен пакет має 3-байтний заголовок", size=13, bold=True))

    frags.append(fitbox(45, 95, 140, 30, "0xA3 (HEAD1)", size=11, bold=True, fill="#fff2cc", stroke="#d6b656"))
    frags.append(fitbox(190, 95, 140, 30, "0x95 (HEAD2)", size=11, bold=True, fill="#fff2cc", stroke="#d6b656"))
    frags.append(fitbox(335, 95, 140, 30, "Type ID (uint8)", size=11, bold=True, fill="#eaf2fd", stroke=NEG))
    frags.append(fitbox(480, 95, 355, 30, "Корисне навантаження повідомлення (довжина = FMT.Length - 3)", size=11, fill="#d5e8d4", stroke=FIELD))

    # Повідомлення опису схеми: FMT (Type 0x80 = 128)
    frags.append(rect(30, 150, 820, 160, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(440, 172, "Повідомлення опису схеми: FMT (Type 0x80, фіксована довжина 89 байтів)", size=13, bold=True, color=INK))

    frags.append(fitbox(45, 190, 110, 40, "Type (uint8)\nID типу (напр. 5)", size=10, fill="#eaf2fd", stroke=NEG))
    frags.append(fitbox(160, 190, 110, 40, "Length (uint8)\nПовна довжина", size=10, fill="#eaf2fd", stroke=NEG))
    frags.append(fitbox(275, 190, 130, 40, "Name (char[4])\nНазва (ATT, GPS)", size=10, bold=True, fill="#fff2cc", stroke="#d6b656"))
    frags.append(fitbox(410, 190, 180, 40, "Format (char[16])\nСпецифікатор типів (Qfffe)", size=10, bold=True, fill="#fdecea", stroke=POS))
    frags.append(fitbox(595, 190, 240, 40, "Columns (char[64])\nНазви полів (TimeUS,Roll,Pitch...)", size=10, fill="#f4f6f8", stroke=MUTED))

    # Додатковий опис одиниць: FMTU
    frags.append(rect(45, 240, 790, 55, fill="#f9fbe7", stroke="#afb42b", sw=1.2, rx=4))
    frags.append(text(440, 258, "Повідомлення одиниць вимірювання та множників: FMTU (Type 0x2A)", size=11, bold=True, color="#827717"))
    frags.append(text(440, 275, "Type (uint8) + Units char[16] ('s'=м/с, 'd'=град, 'm'=метри) + Multipliers char[16] ('2'=100, 'e'=0.01, '1'=1)", size=10, color=INK))

    # Приклади бінарних повідомлень даних
    frags.append(rect(30, 325, 820, 140, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=6))
    frags.append(text(440, 347, "Приклади бінарних касет даних (розпаковуються згідно з FMT)", size=13, bold=True, color=INK))

    # Повідомлення ATT (Орієнтація)
    frags.append(rect(45, 362, 380, 48, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    frags.append(text(235, 380, "ATT (Attitude): 0xA3 0x95 0x05 + 28 байтів", size=11, bold=True, color=NEG))
    frags.append(text(235, 397, "TimeUS (uint64), Roll (float), Pitch (float), Yaw (float)", size=10, color=MUTED))

    # Повідомлення GPS (Навігація)
    frags.append(rect(440, 362, 395, 48, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    frags.append(text(637, 380, "GPS: 0xA3 0x95 0x01 + 45 байтів", size=11, bold=True, color=FIELD))
    frags.append(text(637, 397, "TimeUS, Status, Lat/Lng (int32 / 1e7), Alt (float), Spd (float)", size=10, color=MUTED))

    # Повідомлення PARM (Параметри)
    frags.append(rect(45, 415, 790, 40, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    frags.append(text(440, 432, "PARM (Параметр): 0xA3 0x95 0x81 + TimeUS (uint64) + Name (char[16]) + Value (float32)", size=11, bold=True, color=INK))
    frags.append(text(440, 447, "MSG (Текстовий лог): 0xA3 0x95 0x82 + TimeUS (uint64) + Text (char[50])", size=10, color=MUTED))

    return render(os.path.join(IMG_DIR, "dataflash-binary-layout.svg"), w, h, *frags)


def fig_stream_framing_comparison():
    """Ілюстрація: порівняння стратегій кадрування ULog проти DataFlash."""
    w, h = 880, 440
    frags = []

    frags.append(text(440, 30, "Порівняння схем кадрування: потоковий ULog проти кадрового DataFlash", size=16, bold=True))

    # Колонка 1: PX4 ULog (Потокове кадрування через довжину блоку)
    frags.append(rect(30, 60, 400, 360, fill="#f8fafc", stroke=NEG, sw=1.5, rx=8))
    frags.append(text(230, 85, "PX4 ULog: Потоковий формат", size=14, bold=True, color=NEG))

    frags.append(fitbox(45, 105, 370, 48, "Заголовок 'ULog' лише на початку файлу.\nДалі безперервний потік: [Length (2B)][Type (1B)][Payload]", size=11, fill="#ffffff", stroke=NEG))

    frags.append(text(230, 175, "Переваги архітектури:", size=12, bold=True, color=INK))
    frags.append(mtext(230, 195, [
        "• Мінімальний оверхед (3 байти заголовка на пакет)",
        "• Підтримка вкладених та динамічних типів uORB",
        "• Розділення визначення (Add 'A') та даних ('D')",
        "• Компактний 2-байтний msg_id замість повтору схеми"
    ], size=11, color=INK, anchor="middle", lh=1.35))

    frags.append(rect(45, 275, 370, 65, fill="#fdecea", stroke=POS, sw=1, rx=4))
    frags.append(text(230, 293, "Слабке місце кадрування:", size=11, bold=True, color=POS))
    frags.append(text(230, 312, "При пошкодженні байтів поля довжини (Length)", size=10, color=POS))
    frags.append(text(230, 328, "парсер втрачає потік до кінця сесії або блоку.", size=10, color=POS))

    frags.append(fitbox(45, 350, 370, 55, "Призначення: максимальна щільність запису\nта глибока інтеграція з мікроядерною шиною uORB", size=11, bold=True, fill="#eaf2fd", stroke=NEG))

    # Колонка 2: ArduPilot DataFlash (Покадрове кадрування з синхронізуючим маркером)
    frags.append(rect(450, 60, 400, 360, fill="#f8fafc", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(650, 85, "ArduPilot DataFlash: Покадровий формат", size=14, bold=True, color=FIELD))

    frags.append(fitbox(465, 105, 370, 48, "Синхромаркер 0xA3 0x95 перед КОЖНИМ повідомленням.\nФіксована довжина касет після їх реєстрації у FMT.", size=11, fill="#ffffff", stroke=FIELD))

    frags.append(text(650, 175, "Переваги архітектури:", size=12, bold=True, color=INK))
    frags.append(mtext(650, 195, [
        "• Миттєве відновлення синхронізації при втраті байтів",
        "• Можливість довільного позиціонування (Seek / Jump)",
        "• Простий лінійний парсинг без стану складних структур",
        "• Стійкість до апаратного скидання живлення в польоті"
    ], size=11, color=INK, anchor="middle", lh=1.35))

    frags.append(rect(465, 275, 370, 65, fill="#fff2cc", stroke="#d6b656", sw=1, rx=4))
    frags.append(text(650, 293, "Слабке місце кадрування:", size=11, bold=True, color="#b78103"))
    frags.append(text(650, 312, "Додаткові 3 байти (0xA3 0x95 Type) на КОЖЕН семпл", size=10, color="#b78103"))
    frags.append(text(650, 328, "і фіксований ліміт на 16 полів на один пакет FMT.", size=10, color="#b78103"))

    frags.append(fitbox(465, 350, 370, 55, "Призначення: висока надійність збереження даних\nу разі аварійних вимкнень та пошкоджень носія", size=11, bold=True, fill="#d5e8d4", stroke=FIELD))

    return render(os.path.join(IMG_DIR, "stream-framing-comparison.svg"), w, h, *frags)


def main():
    fig_ring_buffer_sd_latency()
    fig_dataflash_binary_layout()
    fig_ulog_binary_layout()
    fig_stream_framing_comparison()
    print("Всі SVG-фігури згенеровано успішно.")


if __name__ == "__main__":
    main()
