#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор векторних SVG діаграм для теми «Драйвер модуля з власним мозком»."""

import os
import sys

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, textbox, fitbox, rect, line, arrow, text, mtext, circle,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG
)

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_smart_module_arch():
    """Фігура 1: Архітектура взаємодії хост-МК та смарт-модуля з власним процесором."""
    w, h = 880, 420
    frags = []

    # Тло та заголовок
    frags.append(rect(10, 10, w - 20, h - 20, fill="#fdfefe", stroke="#d0d7de", sw=1, rx=8))

    # Хост-мікроконтролер (ліва панель)
    frags.append(rect(30, 45, 360, 350, fill="#f0f7ff", stroke="#0969da", sw=2, rx=8))
    frags.append(text(210, 75, "Головний мікроконтролер (Host MCU)", size=15, bold=True, color="#0969da"))
    frags.append(text(210, 95, "STM32 / ESP32 / Nordic nRF / RP2040", size=12, color=MUTED))

    # Блоки всередині хоста
    f_app, _, _ = textbox(210, 140, "Прикладна логіка (App Tasks / Threads)\nТелеметрія, керування, збереження", size=12, pad=8, fill="#ffffff", stroke="#0969da")
    frags.append(f_app)

    f_fsm, _, _ = textbox(210, 220, "Скінченний автомат драйвера (AT / FSM Engine)\nЧерга команд · Тайм-аути · URC-роутер", size=12, pad=8, fill="#ffffff", stroke="#0969da", bold=True)
    frags.append(f_fsm)

    f_dma, _, _ = textbox(210, 310, "Кільцевий буфер на UART DMA\nIdle Line Detection · Нуль-копіювання", size=12, pad=8, fill="#ffffff", stroke="#0969da")
    frags.append(f_dma)

    # Стрілки всередині хоста
    frags.append(arrow(210, 168, 210, 195, color="#0969da", sw=1.5))
    frags.append(arrow(210, 248, 210, 285, color="#0969da", sw=1.5))

    # Смарт-модуль (права панель)
    frags.append(rect(490, 45, 360, 350, fill="#fff8f2", stroke="#bf8700", sw=2, rx=8))
    frags.append(text(670, 75, "Смарт-модуль (Cellular / Wi-Fi / GNSS)", size=15, bold=True, color="#9a6700"))
    frags.append(text(670, 95, "Quectel / SIMCom / ESP32-AT / u-blox", size=12, color=MUTED))

    # Блоки всередині модуля
    f_rtos, _, _ = textbox(670, 140, "Внутрішній процесор та RTOS модуля\nДиспетчер завдань · Управління пам'яттю", size=12, pad=8, fill="#ffffff", stroke="#bf8700")
    frags.append(f_rtos)

    f_stack, _, _ = textbox(670, 220, "Мережевий стек та Baseband-двигун\n3GPP LTE / Wi-Fi MAC / TCP-IP / GNSS", size=12, pad=8, fill="#ffffff", stroke="#bf8700", bold=True)
    frags.append(f_stack)

    f_uart_m, _, _ = textbox(670, 310, "UART контролер модуля\nЧерга відповідей та спонтанних URC", size=12, pad=8, fill="#ffffff", stroke="#bf8700")
    frags.append(f_uart_m)

    # Стрілки всередині модуля
    frags.append(arrow(670, 168, 670, 195, color="#bf8700", sw=1.5))
    frags.append(arrow(670, 248, 670, 285, color="#bf8700", sw=1.5))

    # Зв'язки між хостом та модулем (посередині x=390..490)
    # 1. TX: Команди
    frags.append(arrow(360, 215, 490, 215, color="#1a7f37", sw=2))
    frags.append(text(440, 205, "AT-команди", size=11, bold=True, color="#1a7f37"))

    # 2. RX: Відповіді на команди
    frags.append(arrow(490, 250, 360, 250, color="#0969da", sw=2))
    frags.append(text(440, 242, "OK / ERROR", size=11, bold=True, color="#0969da"))

    # 3. RX: Асинхронні URC
    frags.append(arrow(490, 330, 360, 330, color="#cf222e", sw=2))
    frags.append(text(440, 320, "URC: RING, +QIURC", size=10, bold=True, color="#cf222e"))

    # 4. Апаратні лінії (зверху)
    frags.append(arrow(360, 130, 490, 130, color="#8250df", sw=1.5))
    frags.append(text(440, 120, "PWRKEY / RESET", size=10, bold=True, color="#8250df"))

    # Підписи збоку
    frags.append(text(440, 375, "Асинхронний фізичний канал (UART)", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT_DIR, "smart-module-arch.svg"), w, h, *frags)


def fig_dma_ring_buffer_parser():
    """Фігура 2: Принцип роботи кільцевого буфера UART DMA з обробкою IDLE переривання та парсером."""
    w, h = 900, 440
    frags = []

    frags.append(rect(10, 10, w - 20, h - 20, fill="#fdfefe", stroke="#d0d7de", sw=1, rx=8))

    # Заголовок зверху
    frags.append(text(450, 35, "Архітектура неблокуючого прийому: UART DMA Circular Buffer та диспетчер рядків", size=15, bold=True, color=INK))

    # Кільцевий буфер (масив комірок)
    cell_w, cell_h = 44, 45
    start_x, start_y = 60, 85
    cells = ["A", "T", "+", "C", "S", "Q", "\\r", "\\n", "O", "K", "\\r", "\\n", "+", "C", "R", "E", "G"]

    frags.append(text(start_x + 350, 68, "Кільцевий буфер у RAM (UART DMA Rx Buffer, N байтів)", size=12, bold=True, color="#0969da"))

    for i, c in enumerate(cells):
        cx = start_x + i * cell_w
        is_term = c in ["\\r", "\\n"]
        bg_col = "#ffebe9" if is_term else ("#e6f6ff" if i < 12 else "#fff8c5")
        border_col = POS if is_term else ("#0969da" if i < 12 else "#bf8700")
        frags.append(rect(cx, start_y, cell_w, cell_h, fill=bg_col, stroke=border_col, sw=1.5, rx=4))
        frags.append(text(cx + cell_w / 2, start_y + 28, c, size=13, bold=True, color=INK))

    # Покажчики Head і Tail
    # Tail (Software read pointer) на індексі 0
    frags.append(arrow(start_x + cell_w / 2, start_y + cell_h + 30, start_x + cell_w / 2, start_y + cell_h + 5, color="#1a7f37", sw=2))
    frags.append(text(start_x + cell_w / 2, start_y + cell_h + 45, "Tail (Зчитування)", size=11, bold=True, color="#1a7f37"))

    # Head (DMA write pointer) на індексі 17
    head_x = start_x + 16 * cell_w + cell_w / 2
    frags.append(arrow(head_x, start_y + cell_h + 30, head_x, start_y + cell_h + 5, color="#cf222e", sw=2))
    frags.append(text(head_x, start_y + cell_h + 45, "Head (DMA CNDTR)", size=11, bold=True, color="#cf222e"))

    # Середній ярус: IDLE переривання та виділення рядків
    f_idle, _, _ = textbox(230, 225, "UART IDLE Line Interrupt\nФіксує паузу на шині (кінець пакета)", size=12, pad=8, fill="#f6f8fa", stroke="#8250df", bold=True)
    frags.append(f_idle)

    f_line, _, _ = textbox(620, 225, "Диспетчер рядків (Line Extractor)\nПошук \\r\\n · Нуль-термінація (Zero-Copy)", size=12, pad=8, fill="#e6f6ff", stroke="#0969da", bold=True)
    frags.append(f_line)

    frags.append(arrow(230, 190, 230, 150, color="#8250df", sw=1.5))
    frags.append(arrow(370, 225, 480, 225, color="#0969da", sw=1.8))

    # Нижній ярус: Розподіл між Response та URC
    f_resp, _, _ = textbox(280, 335, "Обробник відповідей на команди\nЗвірка з активною командою: OK / ERROR / Data", size=11, pad=8, fill="#dafbe1", stroke="#1a7f37", bold=True)
    frags.append(f_resp)

    f_urc, _, _ = textbox(680, 335, "Диспетчер спонтанних URC\nТаблиця префіксів: +CREG, +QIURC, RING", size=11, pad=8, fill="#fff8c5", stroke="#bf8700", bold=True)
    frags.append(f_urc)

    frags.append(arrow(560, 255, 360, 305, color="#1a7f37", sw=1.8))
    frags.append(arrow(680, 255, 680, 305, color="#bf8700", sw=1.8))

    # Пояснення знизу
    frags.append(text(450, 410, "Повна ізоляція: URC-події не блокують очікування відповіді на поточну команду", size=12, color=MUTED, italic=True))

    render(os.path.join(OUT_DIR, "dma-ring-buffer-parser.svg"), w, h, *frags)


def fig_at_command_fsm():
    """Фігура 3: Скінченний автомат обробки AT-команд, таймаутів та ескалації відновлення."""
    w, h = 880, 440
    frags = []

    frags.append(rect(10, 10, w - 20, h - 20, fill="#fdfefe", stroke="#d0d7de", sw=1, rx=8))
    frags.append(text(440, 35, "Скінченний автомат драйвера (AT Command & Recovery FSM)", size=15, bold=True, color=INK))

    # Стани автомата
    # 1. IDLE
    f_idle, _, _ = textbox(110, 120, "STATE_IDLE\nОчікування команди", size=12, pad=10, fill="#f6f8fa", stroke=LINE, bold=True)
    frags.append(f_idle)

    # 2. TRANSMIT
    f_tx, _, _ = textbox(340, 120, "STATE_SEND_CMD\nВідправка в UART TX", size=12, pad=10, fill="#e6f6ff", stroke="#0969da", bold=True)
    frags.append(f_tx)

    # 3. WAIT_RESP
    f_wait, _, _ = textbox(600, 120, "STATE_WAIT_RESP\nОчікування відповіді", size=12, pad=10, fill="#fff8c5", stroke="#bf8700", bold=True)
    frags.append(f_wait)

    # 4. SUCCESS / CALLBACK
    f_ok, _, _ = textbox(800, 120, "Успіх (OK)\nВиклик callback", size=12, pad=8, fill="#dafbe1", stroke="#1a7f37", bold=True)
    frags.append(f_ok)

    # 5. RETRY BACKOFF
    f_retry, _, _ = textbox(600, 260, "STATE_RETRY_DELAY\nЕкспоненційна пауза", size=12, pad=8, fill="#fff1e5", stroke="#bc4c00")
    frags.append(f_retry)

    # 6. RECOVERY ESCALATION (Нижній рівень)
    f_rec1, _, _ = textbox(180, 370, "Рівень 1: AT Reset\nAT+CFUN=1,1", size=11, pad=8, fill="#ffebe9", stroke=POS)
    frags.append(f_rec1)

    f_rec2, _, _ = textbox(440, 370, "Рівень 2: HW Pin Pulse\nІмпульс RESET_N / PWRKEY", size=11, pad=8, fill="#ffebe9", stroke=POS)
    frags.append(f_rec2)

    f_rec3, _, _ = textbox(720, 370, "Рівень 3: Power Cycle\nВимкнення живлення MOSFET", size=11, pad=8, fill="#ffebe9", stroke=POS, bold=True)
    frags.append(f_rec3)

    # Переходи
    # IDLE -> TRANSMIT
    frags.append(arrow(185, 120, 260, 120, color="#0969da", sw=1.8))
    frags.append(text(222, 108, "Черга", size=10, color="#0969da", bold=True))

    # TRANSMIT -> WAIT_RESP
    frags.append(arrow(420, 120, 505, 120, color="#0969da", sw=1.8))
    frags.append(text(462, 108, "TX Done", size=10, color="#0969da", bold=True))

    # WAIT_RESP -> OK
    frags.append(arrow(695, 120, 740, 120, color="#1a7f37", sw=2))
    frags.append(text(718, 108, "OK", size=11, color="#1a7f37", bold=True))

    # OK -> IDLE (Повернення зверху)
    frags.append(line(800, 85, 800, 60, color="#1a7f37", sw=1.5))
    frags.append(line(800, 60, 110, 60, color="#1a7f37", sw=1.5))
    frags.append(arrow(110, 60, 110, 85, color="#1a7f37", sw=1.5))
    frags.append(text(440, 52, "Наступна команда з черги", size=10, color="#1a7f37"))

    # WAIT_RESP -> RETRY (ERROR або Timeout)
    frags.append(arrow(600, 160, 600, 225, color="#bc4c00", sw=1.8))
    frags.append(text(710, 190, "ERROR / Timeout (спроба < N)", size=10, color="#bc4c00", bold=True))

    # RETRY -> TRANSMIT
    frags.append(arrow(520, 260, 360, 160, color="#bc4c00", sw=1.5))
    frags.append(text(410, 230, "Повтор спроби", size=10, color="#bc4c00"))

    # RETRY -> ESCALATION (Вичерпано спроби)
    frags.append(arrow(600, 295, 600, 330, color=POS, sw=2))
    frags.append(text(700, 315, "Спроби вичерпано", size=10, color=POS, bold=True))

    # Ланцюг ескалації
    frags.append(arrow(260, 370, 340, 370, color=POS, sw=1.5))
    frags.append(arrow(540, 370, 610, 370, color=POS, sw=1.5))

    # Ескалація назад в IDLE після рестарту
    frags.append(line(180, 405, 180, 420, color=POS, sw=1.5))
    frags.append(line(180, 420, 60, 420, color=POS, sw=1.5))
    frags.append(line(60, 420, 60, 120, color=POS, sw=1.5))
    frags.append(arrow(60, 120, 70, 120, color=POS, sw=1.5))
    frags.append(text(120, 432, "Повний рестарт драйвера", size=10, color=POS))

    render(os.path.join(OUT_DIR, "at-command-fsm.svg"), w, h, *frags)


def fig_hardware_control_lines():
    """Фігура 4: Схема апаратного підключення, лінії керування та захист від паразитарного живлення."""
    w, h = 880, 440
    frags = []

    frags.append(rect(10, 10, w - 20, h - 20, fill="#fdfefe", stroke="#d0d7de", sw=1, rx=8))
    frags.append(text(440, 32, "Апаратні лінії взаємодії та комутація живлення смарт-модуля", size=15, bold=True, color=INK))

    # Ліва частина: Хост-МК
    frags.append(rect(30, 60, 240, 350, fill="#f0f7ff", stroke="#0969da", sw=2, rx=6))
    frags.append(text(150, 85, "Host MCU (3.3V Logic)", size=14, bold=True, color="#0969da"))

    # Піни МК
    pins_mcu = [
        ("UART TX", 120),
        ("UART RX", 160),
        ("PWRKEY_CTRL", 200),
        ("RESET_CTRL", 240),
        ("DTR_SLEEP", 280),
        ("STATUS_IN", 320),
        ("POWER_EN", 360)
    ]
    for name, py in pins_mcu:
        frags.append(rect(45, py - 12, 110, 24, fill="#ffffff", stroke="#0969da", sw=1, rx=3))
        frags.append(text(100, py + 4, name, size=11, bold=True, color="#0969da"))

    # Права частина: Смарт-модуль
    frags.append(rect(610, 60, 240, 350, fill="#fff8f2", stroke="#bf8700", sw=2, rx=6))
    frags.append(text(730, 85, "Smart Module (1.8V / 3.3V)", size=14, bold=True, color="#bf8700"))

    # Піни модуля
    pins_mod = [
        ("UART RXD", 120),
        ("UART TXD", 160),
        ("PWRKEY", 200),
        ("RESET_N", 240),
        ("DTR / WAKE", 280),
        ("STATUS / VDD", 320),
        ("VBAT_PIN", 360)
    ]
    for name, py in pins_mod:
        frags.append(rect(725, py - 12, 110, 24, fill="#ffffff", stroke="#bf8700", sw=1, rx=3))
        frags.append(text(780, py + 4, name, size=11, bold=True, color="#bf8700"))

    # З'єднання посередині
    # 1. UART TX -> RX
    frags.append(arrow(155, 120, 725, 120, color="#1a7f37", sw=1.5))
    frags.append(text(400, 112, "UART Data Out (TX → RX)", size=10, color="#1a7f37", bold=True))

    # 2. UART RX <- TX
    frags.append(arrow(725, 160, 155, 160, color="#0969da", sw=1.5))
    frags.append(text(400, 152, "UART Data In (RX ← TX)", size=10, color="#0969da", bold=True))

    # 3. PWRKEY транзистор Open-Drain
    frags.append(arrow(155, 200, 350, 200, color="#8250df", sw=1.5))
    frags.append(rect(350, 188, 120, 24, fill="#f6f8fa", stroke="#8250df", sw=1, rx=4))
    frags.append(text(410, 204, "NPN / N-FET Key", size=10, bold=True, color="#8250df"))
    frags.append(arrow(470, 200, 725, 200, color="#8250df", sw=1.5))

    # 4. RESET транзистор Open-Drain
    frags.append(arrow(155, 240, 350, 240, color="#cf222e", sw=1.5))
    frags.append(rect(350, 228, 120, 24, fill="#f6f8fa", stroke="#cf222e", sw=1, rx=4))
    frags.append(text(410, 244, "Open-Drain Pull", size=10, bold=True, color="#cf222e"))
    frags.append(arrow(470, 240, 725, 240, color="#cf222e", sw=1.5))

    # 5. DTR Sleep pin
    frags.append(arrow(155, 280, 725, 280, color="#0969da", sw=1.5))
    frags.append(text(400, 272, "Сон / Пробудження (DTR)", size=10, color="#0969da"))

    # 6. STATUS / RI input
    frags.append(arrow(725, 320, 155, 320, color="#1a7f37", sw=1.5))
    frags.append(text(400, 312, "Контроль активності (STATUS)", size=10, color="#1a7f37"))

    # 7. Живлення через High-Side P-MOSFET
    frags.append(arrow(155, 360, 330, 360, color=POS, sw=2))
    frags.append(rect(330, 345, 160, 30, fill="#ffebe9", stroke=POS, sw=1.5, rx=4))
    frags.append(text(410, 364, "P-MOSFET High-Side Switch", size=10, bold=True, color=POS))
    frags.append(arrow(490, 360, 725, 360, color=POS, sw=2))

    # Попередження про паразитне живлення (внизу)
    frags.append(rect(180, 395, 520, 25, fill="#fff8c5", stroke="#bf8700", sw=1, rx=4))
    frags.append(text(440, 412, "Захист від Phantom Powering: при вимкненні VBAT переводити всі GPIO в High-Z / Analog!", size=10, bold=True, color="#7d4e00"))

    render(os.path.join(OUT_DIR, "hardware-control-lines.svg"), w, h, *frags)


def main():
    fig_smart_module_arch()
    fig_dma_ring_buffer_parser()
    fig_at_command_fsm()
    fig_hardware_control_lines()
    print("Всі SVG фігури успішно згенеровано.")


if __name__ == "__main__":
    main()
