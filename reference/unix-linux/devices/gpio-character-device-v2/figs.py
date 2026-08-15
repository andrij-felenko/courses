# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import render, textbox, arrow, rect, text

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

# Кольорова палітра
BG_BLUE = "#eaf0fd"
BG_GREEN = "#eaf6ef"
BG_WARM = "#fff6e5"
BG_RED = "#fdecea"

LINE_DARK = "#2c3e50"
LINE_BLUE = "#2980b9"
LINE_GREEN = "#27ae60"
LINE_RED = "#c0392b"
LINE_ORANGE = "#d35400"


def fig_chardev_v2_architecture():
    path = os.path.join(IMG, 'chardev-v2-architecture.svg')
    frags = []

    # Контейнер Userspace
    frags.append(rect(40, 40, 1120, 160, fill=BG_BLUE, stroke=LINE_BLUE, sw=2, rx=8))
    frags.append(text(70, 70, "Простір користувача (Userspace)", size=16, bold=True, color=LINE_BLUE, anchor="start"))

    b_app, _, _ = textbox(250, 130, ["Прикладна програма / Демон", "(C / C++ / Rust / Go)"], size=13, pad=12, fill="#ffffff", stroke=LINE_DARK)
    frags.append(b_app)

    b_lib, _, _ = textbox(650, 130, ["Бібліотека libgpiod v2", "(gpiod_chip, gpiod_line_request)"], size=13, pad=12, fill="#ffffff", stroke=LINE_BLUE)
    frags.append(b_lib)

    b_raw, _, _ = textbox(980, 130, ["Прямі системні виклики", "ioctl(fd, GPIO_V2_...)"], size=13, pad=12, fill="#ffffff", stroke=LINE_ORANGE)
    frags.append(b_raw)

    frags.append(arrow(370, 130, 525, 130, sw=2, color=LINE_DARK))
    frags.append(arrow(370, 130, 890, 130, sw=2, color=LINE_ORANGE))

    # Стрілки вниз до VFS
    frags.append(arrow(650, 200, 650, 265, sw=2.5, color=LINE_BLUE))
    frags.append(arrow(980, 200, 980, 265, sw=2.5, color=LINE_ORANGE))

    # Контейнер VFS & chardev
    frags.append(rect(40, 270, 1120, 180, fill=BG_WARM, stroke=LINE_ORANGE, sw=2, rx=8))
    frags.append(text(70, 300, "Віртуальна файлова система (VFS) та Символьний пристрій", size=16, bold=True, color=LINE_ORANGE, anchor="start"))

    b_chip_fd, _, _ = textbox(300, 370, ["/dev/gpiochipN (Chardev FD)", "GPIO_GET_CHIPINFO_IOCTL", "GPIO_V2_GET_LINE_IOCTL"], size=13, pad=12, fill="#ffffff", stroke=LINE_DARK)
    frags.append(b_chip_fd)

    b_line_fd, _, _ = textbox(820, 370, ["Окремий Line FD (Request FD)", "GPIO_V2_LINE_GET/SET_VALUES", "read() -> struct gpio_v2_line_event"], size=13, pad=12, fill="#ffffff", stroke=LINE_GREEN)
    frags.append(b_line_fd)

    frags.append(arrow(475, 370, 640, 370, sw=2, color=LINE_GREEN))

    # Стрілка вниз до Kernel Core
    frags.append(arrow(600, 450, 600, 515, sw=2.5, color=LINE_DARK))

    # Контейнер Kernel Subsystem
    frags.append(rect(40, 520, 1120, 180, fill=BG_GREEN, stroke=LINE_GREEN, sw=2, rx=8))
    frags.append(text(70, 550, "Простір ядра (Kernel Subsystem: gpiolib-cdev)", size=16, bold=True, color=LINE_GREEN, anchor="start"))

    b_cdev, _, _ = textbox(250, 620, ["gpiolib-cdev.c", "Обробка ioctl v2, кільцевий", "буфер подій, epoll notify"], size=13, pad=12, fill="#ffffff", stroke=LINE_GREEN)
    frags.append(b_cdev)

    b_core, _, _ = textbox(600, 620, ["gpiolib core", "struct gpio_desc, перевірка", "прав та стану ліній"], size=13, pad=12, fill="#ffffff", stroke=LINE_DARK)
    frags.append(b_core)

    b_drv, _, _ = textbox(950, 620, ["Драйвер SoC / pinctrl", "struct gpio_chip -> апаратні", "регістри GPIO та IRQ"], size=13, pad=12, fill="#ffffff", stroke=LINE_BLUE)
    frags.append(b_drv)

    frags.append(arrow(370, 620, 480, 620, sw=2, color=LINE_DARK))
    frags.append(arrow(720, 620, 830, 620, sw=2, color=LINE_DARK))

    render(path, 1200, 740, *frags)


def fig_line_request_config_layout():
    path = os.path.join(IMG, 'line-request-config-layout.svg')
    frags = []

    # Головна структура gpio_v2_line_request
    frags.append(rect(40, 40, 1120, 220, fill=BG_BLUE, stroke=LINE_BLUE, sw=2, rx=8))
    frags.append(text(70, 70, "struct gpio_v2_line_request (Запит на захоплення групи ліній)", size=16, bold=True, color=LINE_BLUE, anchor="start"))

    b_req1, _, _ = textbox(220, 140, ["offsets[64]", "Масив індексів ліній", "(наприклад: [4, 17, 22])"], size=12, pad=10, fill="#ffffff", stroke=LINE_DARK)
    frags.append(b_req1)

    b_req2, _, _ = textbox(500, 140, ["consumer[32]", "Назва процесу / споживача", "для debugfs"], size=12, pad=10, fill="#ffffff", stroke=LINE_DARK)
    frags.append(b_req2)

    b_req3, _, _ = textbox(780, 140, ["config", "Вбудована структура", "gpio_v2_line_config"], size=12, pad=10, fill="#ffffff", stroke=LINE_GREEN)
    frags.append(b_req3)

    b_req4, _, _ = textbox(1020, 140, ["num_lines / fd", "Кількість ліній (до 64)", "та повернутий Line FD"], size=12, pad=10, fill="#ffffff", stroke=LINE_ORANGE)
    frags.append(b_req4)

    # Деталізація gpio_v2_line_config
    frags.append(arrow(780, 200, 780, 290, sw=2.5, color=LINE_GREEN))

    frags.append(rect(40, 290, 1120, 320, fill=BG_GREEN, stroke=LINE_GREEN, sw=2, rx=8))
    frags.append(text(70, 320, "struct gpio_v2_line_config (Глобальні прапори та масив індивідуальних атрибутів)", size=16, bold=True, color=LINE_GREEN, anchor="start"))

    b_cfg1, _, _ = textbox(250, 380, ["flags (64-bit)", "Глобальні прапори за замовчуванням:", "INPUT / OUTPUT / ACTIVE_LOW / BIAS..."], size=12, pad=10, fill="#ffffff", stroke=LINE_DARK)
    frags.append(b_cfg1)

    b_cfg2, _, _ = textbox(750, 380, ["attrs[10] (gpio_v2_line_config_attribute)", "Масив перевизначень конкретних атрибутів для окремих ліній"], size=12, pad=10, fill="#ffffff", stroke=LINE_GREEN)
    frags.append(b_cfg2)

    # Приклади атрибутів усередині attrs[10]
    b_attr1, _, _ = textbox(300, 520, ["attr[0]: ID_DEBOUNCE", "mask = 0x01 (Лінія 4)", "debounce_period_us = 5000 мкс"], size=12, pad=10, fill="#ffffff", stroke=LINE_BLUE)
    frags.append(b_attr1)

    b_attr2, _, _ = textbox(600, 520, ["attr[1]: ID_OUTPUT_VALUES", "mask = 0x04 (Лінія 22)", "values = 0x01 (HIGH)"], size=12, pad=10, fill="#ffffff", stroke=LINE_ORANGE)
    frags.append(b_attr2)

    b_attr3, _, _ = textbox(900, 520, ["attr[2]: ID_FLAGS", "mask = 0x02 (Лінія 17)", "flags = BIAS_PULL_UP | EDGE_RISING"], size=12, pad=10, fill="#ffffff", stroke=LINE_GREEN)
    frags.append(b_attr3)

    frags.append(arrow(750, 430, 300, 465, sw=1.5, color=LINE_BLUE))
    frags.append(arrow(750, 430, 600, 465, sw=1.5, color=LINE_ORANGE))
    frags.append(arrow(750, 430, 900, 465, sw=1.5, color=LINE_GREEN))

    render(path, 1200, 640, *frags)


def fig_event_reading_flow():
    path = os.path.join(IMG, 'event-reading-flow.svg')
    frags = []

    # Джерело події (Залізо)
    frags.append(rect(40, 40, 220, 440, fill=BG_WARM, stroke=LINE_ORANGE, sw=2, rx=8))
    frags.append(text(65, 75, "Апаратний вивід", size=15, bold=True, color=LINE_ORANGE, anchor="start"))
    b_hw, _, _ = textbox(150, 150, ["Зміна сигналу", "на фізичному піні", "(Rising / Falling edge)"], size=12, pad=10, fill="#ffffff", stroke=LINE_DARK)
    frags.append(b_hw)

    # Крок 1: IRQ в ядрі
    frags.append(arrow(260, 150, 340, 150, sw=2.5, color=LINE_DARK))
    frags.append(rect(340, 40, 250, 440, fill=BG_RED, stroke=LINE_RED, sw=2, rx=8))
    frags.append(text(360, 75, "Обробник IRQ ядра", size=15, bold=True, color=LINE_RED, anchor="start"))

    b_irq, _, _ = textbox(465, 150, ["Отримання переривання", "Фіксація мітки часу", "(Monotonic / Realtime / HTE)"], size=12, pad=10, fill="#ffffff", stroke=LINE_RED)
    frags.append(b_irq)

    b_seq, _, _ = textbox(465, 310, ["Інкремент лічильників:", "global seqno та line_seqno"], size=12, pad=10, fill="#ffffff", stroke=LINE_DARK)
    frags.append(b_seq)
    frags.append(arrow(465, 210, 465, 260, sw=2, color=LINE_DARK))

    # Крок 2: Буфер cdev
    frags.append(arrow(590, 310, 670, 310, sw=2.5, color=LINE_DARK))
    frags.append(rect(670, 40, 250, 440, fill=BG_GREEN, stroke=LINE_GREEN, sw=2, rx=8))
    frags.append(text(690, 75, "Кільцевий буфер gpiolib", size=15, bold=True, color=LINE_GREEN, anchor="start"))

    b_buf, _, _ = textbox(795, 310, ["Запис у event_buffer", "struct gpio_v2_line_event", "Сигнал epoll / poll pollwait"], size=12, pad=10, fill="#ffffff", stroke=LINE_GREEN)
    frags.append(b_buf)

    # Крок 3: Читання з Userspace
    frags.append(arrow(920, 310, 1000, 310, sw=2.5, color=LINE_BLUE))
    frags.append(rect(1000, 40, 220, 440, fill=BG_BLUE, stroke=LINE_BLUE, sw=2, rx=8))
    frags.append(text(1020, 75, "Userspace app", size=15, bold=True, color=LINE_BLUE, anchor="start"))

    b_user, _, _ = textbox(1110, 310, ["read(linefd, &event, ...)", "Аналіз timestamp_ns,", "id, line_seqno"], size=12, pad=10, fill="#ffffff", stroke=LINE_BLUE)
    frags.append(b_user)

    render(path, 1260, 520, *frags)


if __name__ == '__main__':
    fig_chardev_v2_architecture()
    fig_line_request_config_layout()
    fig_event_reading_flow()
    print("Figures generated successfully.")
