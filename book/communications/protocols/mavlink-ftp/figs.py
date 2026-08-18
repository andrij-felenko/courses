# -*- coding: utf-8 -*-
"""Генератор фігур для теми «MAVFTP: передача файлів поверх MAVLink»."""

import os
import sys

# Підключення svgkit від кореня репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_frame_structure():
    """Фігура 1: Структура повідомлення FILE_TRANSFER_PROTOCOL (#110) та PayloadHeader."""
    w, h = 860, 520
    frags = []

    # Заголовок секції MAVLink v2
    frags.append(text(430, 25, "Структура кадру MAVLink v2 та повідомлення FILE_TRANSFER_PROTOCOL (#110)", size=16, bold=True))

    # Верхній рівень: Кадр MAVLink v2
    frags.append(rect(40, 50, 780, 70, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(430, 70, "Кадр MAVLink v2 (загальна довжина 280 байтів)", size=13, color=MUTED, bold=True))

    # Блоки кадру MAVLink v2
    blocks_v2 = [
        (45, 80, 55, 32, "STX\n0xFD", "#e2e8f0"),
        (105, 80, 60, 32, "LEN\n254 B", "#e2e8f0"),
        (170, 80, 70, 32, "FLAGS\n2 B", "#e2e8f0"),
        (245, 80, 55, 32, "SEQ\n1 B", "#e2e8f0"),
        (305, 80, 75, 32, "SYS/COMP\n2 B", "#e2e8f0"),
        (385, 80, 85, 32, "MSG ID\n110 (3 B)", "#e0e7ff"),
        (475, 80, 265, 32, "Корисне навантаження кадру (254 байти)", "#dbeafe"),
        (745, 80, 70, 32, "CRC-16\n2 B", "#fef3c7"),
    ]
    for bx, by, bw, bh, btxt, bfill in blocks_v2:
        frags.append(fitbox(bx, by, bw, bh, btxt, size=11, fill=bfill, stroke=LINE, sw=1.2, rx=4))

    # Розгортка корисного навантаження (Payload MAVLink)
    frags.append(arrow(607, 125, 607, 155, color=NEG, sw=1.8))
    frags.append(rect(40, 160, 780, 90, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(430, 180, "Корисне навантаження повідомлення #110 (254 байти)", size=13, color=NEG, bold=True))

    blocks_msg = [
        (50, 195, 120, 45, "target_network\n1 байт (зазвичай 0)", "#ffffff"),
        (175, 195, 120, 45, "target_system\n1 байт (SYSID борту)", "#ffffff"),
        (300, 195, 130, 45, "target_component\n1 байт (COMPID)", "#ffffff"),
        (435, 195, 375, 45, "Вкладений пакет MAVFTP payload[251] (251 байт)", "#dcfce7"),
    ]
    for bx, by, bw, bh, btxt, bfill in blocks_msg:
        frags.append(fitbox(bx, by, bw, bh, btxt, size=11, fill=bfill, stroke=LINE, sw=1.2, rx=4))

    # Розгортка MAVFTP Payload: PayloadHeader (12 байтів) + data (239 байтів)
    frags.append(arrow(622, 255, 622, 285, color=FIELD, sw=1.8))
    frags.append(rect(40, 290, 780, 210, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(430, 312, "Вкладений пакет MAVFTP: PayloadHeader (12 B) + data (239 B)", size=13, color=FIELD, bold=True))

    # Блоки заголовка PayloadHeader (12 байтів)
    hdr_blocks = [
        (50, 330, 85, 55, "seq_number\n2 байти (LE)\n№ пакета", "#ffffff"),
        (140, 330, 65, 55, "session\n1 байт\nID сесії", "#ffffff"),
        (210, 330, 65, 55, "opcode\n1 байт\nОпкод", "#fef08a"),
        (280, 330, 55, 55, "size\n1 байт\nДовжина", "#ffffff"),
        (340, 330, 85, 55, "req_opcode\n1 байт\nОпкод запиту", "#fef08a"),
        (430, 330, 95, 55, "burst_complete\n1 байт\nФініш burst", "#ffffff"),
        (530, 330, 65, 55, "padding\n1 байт\nРезерв", "#f3f4f6"),
        (600, 330, 95, 55, "offset\n4 байти (LE)\nЗсув у файлі", "#ffffff"),
        (700, 330, 110, 55, "data[239]\n239 байтів\nТіло фрагмента", "#dbeafe"),
    ]
    for bx, by, bw, bh, btxt, bfill in hdr_blocks:
        frags.append(fitbox(bx, by, bw, bh, btxt, size=10, fill=bfill, stroke=LINE, sw=1.1, rx=4))

    # Пояснювальний блок унизу
    desc_txt = (
        "PayloadHeader (12 байтів) містить усі поля для керування сесією, зміщенням (offset) та контролем втрат.\n"
        "Масив data[239] переносить фрагмент файлу, шлях до директорії або коди помилок у разі NAK."
    )
    frags.append(fitbox(50, 400, 760, 85, desc_txt, size=11, fill="#ffffff", stroke=MUTED, sw=1.0, rx=4))

    render(os.path.join(IMG_DIR, "mavftp-frame-structure.svg"), w, h, *frags)


def fig_stop_and_wait_vs_burst():
    """Фігура 2: Порівняння Stop-and-Wait (ReadFile) та Burst Read (BurstReadFile)."""
    w, h = 860, 520
    frags = []

    frags.append(text(430, 25, "Порівняння пропускної здатності: Stop-and-Wait проти Burst Read", size=16, bold=True))

    # Ліва колонка: Stop-and-Wait
    frags.append(rect(40, 55, 375, 445, fill="#fff5f5", stroke=POS, sw=1.5, rx=6))
    frags.append(text(227, 80, "Звичайне зчитування (ReadFile)", size=14, color=POS, bold=True))
    frags.append(text(227, 98, "Stop-and-Wait: 1 пакет на 1 RTT (затримка 100-200 мс)", size=11, color=MUTED))

    # Лінії часу ліворуч
    frags.append(text(100, 125, "Клієнт (GCS)", size=12, bold=True))
    frags.append(text(350, 125, "Борт (FC)", size=12, bold=True))
    frags.append(line(100, 135, 100, 435, color=LINE, sw=1.5, dash="4,4"))
    frags.append(line(350, 135, 350, 435, color=LINE, sw=1.5, dash="4,4"))

    # Події ліворуч
    frags.append(arrow(100, 150, 350, 175, color=POS, sw=1.5))
    frags.append(text(225, 155, "ReadFile (offset=0, size=239)", size=10, color=INK))

    frags.append(arrow(350, 195, 100, 220, color=FIELD, sw=1.5))
    frags.append(text(225, 200, "ACK (239 байтів даних)", size=10, color=INK))

    frags.append(rect(60, 225, 80, 40, fill="#fee2e2", stroke=POS, sw=1.0, rx=3))
    frags.append(fitbox(60, 225, 80, 40, "Простій\nканалу RTT", size=10, fill="#fee2e2", stroke=POS, sw=1.0))

    frags.append(arrow(100, 275, 350, 300, color=POS, sw=1.5))
    frags.append(text(225, 280, "ReadFile (offset=239, size=239)", size=10, color=INK))

    frags.append(arrow(350, 320, 100, 345, color=FIELD, sw=1.5))
    frags.append(text(225, 325, "ACK (239 байтів даних)", size=10, color=INK))

    frags.append(rect(60, 350, 80, 40, fill="#fee2e2", stroke=POS, sw=1.0, rx=3))
    frags.append(fitbox(60, 350, 80, 40, "Простій\nканалу RTT", size=10, fill="#fee2e2", stroke=POS, sw=1.0))

    frags.append(fitbox(55, 445, 345, 45, "Швидкість: ~1.2 КБ/с (канал зайнятий на 15%)\nФайл 20 МБ качається 4.6 години", size=10, fill="#ffffff", stroke=POS, sw=1.2))

    # Права колонка: Burst Read
    frags.append(rect(445, 55, 375, 445, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(632, 80, "Пакетне зчитування (BurstReadFile)", size=14, color=FIELD, bold=True))
    frags.append(text(632, 98, "Конвеєр: безперервний потік без очікування ACK", size=11, color=MUTED))

    # Лінії часу праворуч
    frags.append(text(505, 125, "Клієнт (GCS)", size=12, bold=True))
    frags.append(text(755, 125, "Борт (FC)", size=12, bold=True))
    frags.append(line(505, 135, 505, 435, color=LINE, sw=1.5, dash="4,4"))
    frags.append(line(755, 135, 755, 435, color=LINE, sw=1.5, dash="4,4"))

    # Події праворуч
    frags.append(arrow(505, 150, 755, 175, color=POS, sw=1.5))
    frags.append(text(630, 155, "BurstReadFile (offset=0)", size=10, color=INK))

    # Потік пакетів від автопілота
    stream_y = [190, 225, 260, 295, 330, 365]
    for i, sy in enumerate(stream_y):
        frags.append(arrow(755, sy, 505, sy + 25, color=FIELD, sw=1.5))
        frags.append(text(630, sy + 10, "ACK chunk #%d (offset=%d)" % (i + 1, i * 239), size=10, color=INK))

    frags.append(fitbox(460, 445, 345, 45, "Швидкість: ~5.5 КБ/с (100% насичення лінії UART)\nФайл 20 МБ качається близько 1 години", size=10, fill="#ffffff", stroke=FIELD, sw=1.2))

    render(os.path.join(IMG_DIR, "stop-and-wait-vs-burst.svg"), w, h, *frags)


def fig_session_read_flow():
    """Фігура 3: Діаграма послідовності завантаження файлу та відновлення після втрат."""
    w, h = 860, 540
    frags = []

    frags.append(text(430, 25, "Діаграма взаємодії MAVFTP: відкриття, потік Burst та закриття сесії", size=16, bold=True))

    # Вертикальні лінії сутностей
    frags.append(rect(80, 50, 160, 36, fill="#dbeafe", stroke=LINE, sw=1.5, rx=4))
    frags.append(text(160, 73, "Клієнт (QGC / станція)", size=12, bold=True))
    frags.append(line(160, 86, 160, 500, color=LINE, sw=1.5, dash="4,4"))

    frags.append(rect(620, 50, 160, 36, fill="#dcfce7", stroke=LINE, sw=1.5, rx=4))
    frags.append(text(700, 73, "Сервер (Автопілот / PX4)", size=12, bold=True))
    frags.append(line(700, 86, 700, 500, color=LINE, sw=1.5, dash="4,4"))

    # Фаза 1: Відкриття файлу
    frags.append(arrow(160, 110, 700, 130, color=NEG, sw=1.6))
    frags.append(text(430, 115, "1. OpenFileRO ('/fs/microsd/log01.bin')", size=11, bold=True))

    frags.append(arrow(700, 145, 160, 165, color=FIELD, sw=1.6))
    frags.append(text(430, 150, "2. ACK (session=1, size=4 B, data=file_length)", size=11, color=FIELD, bold=True))

    # Фаза 2: Запит BurstReadFile
    frags.append(arrow(160, 185, 700, 205, color=NEG, sw=1.6))
    frags.append(text(430, 190, "3. BurstReadFile (session=1, offset=0)", size=11, bold=True))

    # Потік пакетів і втрата
    frags.append(arrow(700, 220, 160, 240, color=FIELD, sw=1.6))
    frags.append(text(430, 225, "4. ACK (seq=1, offset=0, 239 B)", size=10))

    frags.append(arrow(700, 250, 160, 270, color=FIELD, sw=1.6))
    frags.append(text(430, 255, "5. ACK (seq=2, offset=239, 239 B)", size=10))

    # Втрачений пакет
    frags.append(line(700, 280, 430, 298, color=POS, sw=1.6, dash="3,3"))
    frags.append(text(410, 295, "✖ Втрачено в ефірі (seq=3, offset=478)", size=10, color=POS, bold=True))

    frags.append(arrow(700, 310, 160, 330, color=FIELD, sw=1.6))
    frags.append(text(430, 315, "6. ACK (seq=4, offset=717, 239 B)  → Клієнт помічає пропуск seq=3!", size=10, color=POS))

    # Фаза 3: Відновлення пропуску
    frags.append(arrow(160, 350, 700, 370, color=POS, sw=1.6))
    frags.append(text(430, 355, "7. BurstReadFile (session=1, offset=478)  → Запит з місця дірки", size=11, color=POS, bold=True))

    frags.append(arrow(700, 385, 160, 405, color=FIELD, sw=1.6))
    frags.append(text(430, 390, "8. ACK (seq=5, offset=478, 239 B)  → Пропуск закрито", size=10))

    frags.append(arrow(700, 415, 160, 435, color=FIELD, sw=1.6))
    frags.append(text(430, 420, "9. ACK (seq=6, offset=717, burst_complete=1, EOF)", size=10, color=FIELD, bold=True))

    # Фаза 4: Закриття сесії
    frags.append(arrow(160, 455, 700, 475, color=LINE, sw=1.6))
    frags.append(text(430, 460, "10. TerminateSession (session=1)", size=11, bold=True))

    frags.append(arrow(700, 485, 160, 505, color=FIELD, sw=1.6))
    frags.append(text(430, 490, "11. ACK (session=1, req_opcode=1)", size=11, color=FIELD, bold=True))

    render(os.path.join(IMG_DIR, "mavftp-session-read-flow.svg"), w, h, *frags)


def fig_fsm_states():
    """Фігура 4: Кінцевий автомат клієнта та сервера MAVFTP."""
    w, h = 860, 500
    frags = []

    frags.append(text(430, 25, "Кінцевий автомат (FSM) клієнта MAVFTP", size=16, bold=True))

    # Стани клієнта
    states = [
        (130, 100, 150, 60, "IDLE\n(Очікування задачі)", "#f3f4f6", LINE),
        (430, 100, 160, 60, "OPENING_FILE\n(Надіслано OpenRO/WO)", "#dbeafe", NEG),
        (730, 100, 160, 60, "SESSION_ACTIVE\n(Сесію відкрито)", "#dcfce7", FIELD),
        (730, 280, 160, 60, "BURST_STREAMING\n(Прийом пакетів Burst)", "#fef08a", LINE),
        (430, 280, 160, 60, "RETRY_GAP\n(Відновлення дірки)", "#fee2e2", POS),
        (130, 280, 150, 60, "CLOSING_SESSION\n(TerminateSession)", "#e2e8f0", LINE),
    ]

    for sx, sy, sw, sh, stxt, sfill, sstrk in states:
        frags.append(fitbox(sx - sw / 2, sy - sh / 2, sw, sh, stxt, size=12, fill=sfill, stroke=sstrk, sw=1.8, rx=6))

    # Переходи між станами
    # IDLE -> OPENING_FILE
    frags.append(arrow(205, 100, 350, 100, color=NEG, sw=1.6))
    frags.append(text(277, 90, "OpenFileRO/WO", size=10, color=NEG, bold=True))

    # OPENING_FILE -> SESSION_ACTIVE (ACK)
    frags.append(arrow(510, 100, 650, 100, color=FIELD, sw=1.6))
    frags.append(text(580, 90, "Отримано ACK", size=10, color=FIELD, bold=True))

    # OPENING_FILE -> IDLE (NAK або таймаут)
    frags.append(arrow(430, 130, 205, 125, color=POS, sw=1.4))
    frags.append(text(315, 140, "NAK / Таймаут 3x", size=10, color=POS))

    # SESSION_ACTIVE -> BURST_STREAMING
    frags.append(arrow(730, 130, 730, 250, color=FIELD, sw=1.6))
    frags.append(text(785, 190, "BurstReadFile", size=10, color=FIELD, bold=True))

    # BURST_STREAMING -> RETRY_GAP (виявлено пропуск seq)
    frags.append(arrow(650, 280, 510, 280, color=POS, sw=1.6))
    frags.append(text(580, 270, "Пропуск seq_number", size=10, color=POS, bold=True))

    # RETRY_GAP -> BURST_STREAMING (повторний Burst)
    frags.append(arrow(510, 305, 650, 305, color=FIELD, sw=1.4))
    frags.append(text(580, 320, "BurstReadFile(gap_offset)", size=10, color=FIELD))

    # BURST_STREAMING -> CLOSING_SESSION (EOF)
    frags.append(arrow(650, 310, 205, 300, color=LINE, sw=1.6))
    frags.append(text(410, 370, "Отримано EOF (burst_complete=1)", size=10, bold=True))

    # CLOSING_SESSION -> IDLE (ACK / таймаут)
    frags.append(arrow(130, 250, 130, 130, color=LINE, sw=1.6))
    frags.append(text(75, 190, "ACK / Reset", size=10, bold=True))

    # Інформаційна картка внизу
    info_txt = (
        "Гарантії надійності: клієнт веде лічильник спроб (зазвичай до 3-5 повторів з таймаутом 500-1000 мс).\n"
        "У разі збою автопілот скидає неактивні сесії за таймаутом бездіяльності (inactivity timeout ≈ 2-5 с)."
    )
    frags.append(fitbox(55, 410, 750, 65, info_txt, size=11, fill="#ffffff", stroke=MUTED, sw=1.0, rx=4))

    render(os.path.join(IMG_DIR, "mavftp-fsm-states.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_frame_structure()
    fig_stop_and_wait_vs_burst()
    fig_session_read_flow()
    fig_fsm_states()
    print("Фігури успішно згенеровано.")
