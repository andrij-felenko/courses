# -*- coding: utf-8 -*-
"""Фігури до теми «Прив'язка до платформи (vendor lock-in)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (scripts/svgkit.py)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# Локальні відтінки
LOCK_FILL = "#fdecea"
LOCK_STROKE = POS
OPEN_FILL = "#eafaf1"
OPEN_STROKE = FIELD
NEUTRAL_FILL = "#f8f9fa"
BLUE_FILL = "#ebf5fb"
BLUE_STROKE = "#2980b9"


# ── 1. Порівняння стосу розробки: Lock-in проти Відкритого ───────────────────
def fig_stack_comparison():
    W, H = 860, 470
    parts = [text(W / 2, 28, "Порівняння стосу: вендорна прив'язка проти відкритої системи", size=15, bold=True)]

    # Підписи колонок
    parts.append(text(240, 64, "Пропрієтарний стек (Vendor Lock-in)", size=13, color=LOCK_STROKE, bold=True))
    parts.append(text(620, 64, "Відкритий портативний стек", size=13, color=OPEN_STROKE, bold=True))

    layers = [
        ("Редактор / IDE", "Keil µVision / IAR EW / MPLAB X", "VS Code / CLion / Neovim / Emacs"),
        ("Опис проєкту", "Пропрієтарний XML (.uvprojx, .ewp)", "Декларативний CMake / Ninja"),
        ("Компілятор", "Arm Compiler 5/6, IAR iccarm", "arm-none-eabi-gcc / LLVM Clang"),
        ("Ліцензування", "USB-донгл, FlexLM, прив'язка до MAC", "Вільна ліцензія (Open Source / FSF)"),
        ("Середовище CI/CD", "Фізичний ПК під столом (Windows GUI)", "Docker-контейнери на будь-якому Linux"),
    ]

    y = 82
    bh = 58
    for layer_name, lock_desc, open_desc in layers:
        # Ліва колонка — Lock-in
        box_l, _, _ = textbox(240, y + bh / 2, f"{layer_name}\n{lock_desc}", size=11,
                              fill=LOCK_FILL, stroke=LOCK_STROKE, pad=6, min_w=340, bold=False)
        parts.append(box_l)

        # Права колонка — Open
        box_r, _, _ = textbox(620, y + bh / 2, f"{layer_name}\n{open_desc}", size=11,
                              fill=OPEN_FILL, stroke=OPEN_STROKE, pad=6, min_w=340, bold=False)
        parts.append(box_r)

        y += bh + 10

    parts.append(text(W / 2, H - 14,
                      "відкритий стек замінює кожен пропрієтарний рівень стандартизованим інструментом без прив'язки до ОС чи ліцензії",
                      size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "lockin-vs-open-stack.svg"), W, H, *parts)


# ── 2. Архітектурне розв'язування: шари ізоляції ────────────────────────────
def fig_decoupling_layers():
    W, H = 840, 480
    parts = [text(W / 2, 28, "Архітектурне розв'язування: ізоляція логіки від вендорного заліза", size=15, bold=True)]

    # 1. Бізнес-логіка (нагорі)
    box_app, _, _ = textbox(420, 75, "Бізнес-логіка застосунку (алгоритми, протоколи, кінцеві автомати)\n100% чистий C/C++, компілюється і на цільовому МК, і на хості для Unit-тестів",
                            size=12, fill=BLUE_FILL, stroke=BLUE_STROKE, bold=True, pad=10, min_w=740)
    parts.append(box_app)

    parts.append(arrow(420, 110, 420, 138, color=LINE, sw=1.8))

    # 2. Тонкий шар абстракції (App-HAL / OSAL)
    box_hal, _, _ = textbox(420, 168, "Шар апаратної та операційної абстракції (App-HAL / OSAL)\nІнтерфейси шин (I2C, SPI, UART), таймерів, задач та пам'яті без вендорних типів",
                            size=12, fill="#fef9e7", stroke="#d68910", bold=True, pad=10, min_w=740)
    parts.append(box_hal)

    # Розгалуження на 4 адаптери
    parts.append(arrow(200, 203, 140, 238, color=LINE, sw=1.5))
    parts.append(arrow(340, 203, 320, 238, color=LINE, sw=1.5))
    parts.append(arrow(500, 203, 520, 238, color=LINE, sw=1.5))
    parts.append(arrow(640, 203, 700, 238, color=LINE, sw=1.5))

    # 3. Адаптери під конкретні платформи
    targets = [
        (140, 275, "Адаптер STM32\n(STM32Cube HAL / LL)"),
        (320, 275, "Адаптер NXP\n(MCUXpresso SDK)"),
        (520, 275, "Адаптер ESP32\n(ESP-IDF Drivers)"),
        (700, 275, "Native Mock\n(x86 Host Tests / CI)"),
    ]
    for cx, cy, label in targets:
        box_t, _, _ = textbox(cx, cy, label, size=11, fill=NEUTRAL_FILL, stroke=LINE, pad=8, min_w=160)
        parts.append(box_t)
        parts.append(arrow(cx, cy + 30, cx, cy + 58, color=LINE, sw=1.5))

    # 4. Рівень ядра та системних бібліотек
    cores = [
        (140, 375, "ARM CMSIS-Core\nCortex-M3/M4/M7"),
        (320, 375, "ARM CMSIS-Core\nCortex-M33"),
        (520, 375, "Xtensa / RISC-V\nFreeRTOS Core"),
        (700, 375, "OS Threads / Mock\nGoogleTest / Catch2"),
    ]
    for cx, cy, label in cores:
        box_c, _, _ = textbox(cx, cy, label, size=11, fill=OPEN_FILL, stroke=OPEN_STROKE, pad=8, min_w=160)
        parts.append(box_c)

    parts.append(text(W / 2, H - 14,
                      "зміна мікроконтролера зачіпає лише адаптерний шар; уся бізнес-логіка залишається недоторканою",
                      size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "firmware-decoupling-layers.svg"), W, H, *parts)


# ── 3. Пайплайн CI/CD: вузьке місце донгла проти контейнеризації ─────────────
def fig_ci_bottleneck():
    W, H = 860, 440
    parts = [text(W / 2, 28, "Пайплайн збірки: апаратне вузьке місце проти хмарного масштабування", size=15, bold=True)]

    # Секція 1: Пропрієтарний підхід із донглом
    parts.append(text(60, 65, "Вендорна модель (Dongle Bottleneck):", size=12, color=LOCK_STROKE, bold=True, anchor="start"))
    box_dev1, _, _ = textbox(130, 115, "Розробники\nGit Push", size=11, fill=NEUTRAL_FILL, stroke=LINE, pad=6, min_w=100)
    box_q, _, _ = textbox(310, 115, "Черга задач\n(1 потік збірки)", size=11, fill=LOCK_FILL, stroke=LOCK_STROKE, pad=6, min_w=130)
    box_pc, _, _ = textbox(540, 115, "Виділений ПК під столом\n(Windows + USB-донгл IAR/Keil)", size=11, fill=LOCK_FILL, stroke=LOCK_STROKE, pad=6, min_w=200, bold=True)
    box_res1, _, _ = textbox(760, 115, "Повільний білд\n(затримка годинами)", size=11, fill=LOCK_FILL, stroke=LOCK_STROKE, pad=6, min_w=130)

    parts += [box_dev1, box_q, box_pc, box_res1]
    parts.append(arrow(185, 115, 240, 115, color=LINE, sw=1.5))
    parts.append(arrow(380, 115, 435, 115, color=LOCK_STROKE, sw=1.8))
    parts.append(arrow(645, 115, 690, 115, color=LOCK_STROKE, sw=1.8))

    # Секція 2: Контейнеризований CI/CD
    parts.append(text(60, 205, "Контейнеризована модель (Hermetic & Scalable CI):", size=12, color=OPEN_STROKE, bold=True, anchor="start"))
    box_dev2, _, _ = textbox(130, 290, "Розробники\nGit Push", size=11, fill=NEUTRAL_FILL, stroke=LINE, pad=6, min_w=100)
    box_ci, _, _ = textbox(300, 290, "Хмарний CI Runner\n(GitHub / GitLab)", size=11, fill=BLUE_FILL, stroke=BLUE_STROKE, pad=6, min_w=130)

    parts += [box_dev2, box_ci]
    parts.append(arrow(185, 290, 230, 290, color=LINE, sw=1.5))

    # Паралельні контейнери
    c_jobs = [
        (540, 235, "Docker #1: Static Analysis\n(clang-tidy, cppcheck)"),
        (540, 290, "Docker #2: Unit Tests Host\n(x86 GCC + GoogleTest)"),
        (540, 345, "Docker #3: Target Build\n(arm-none-eabi-gcc + Ninja)"),
    ]
    for cx, cy, label in c_jobs:
        b_j, _, _ = textbox(cx, cy, label, size=10, fill=OPEN_FILL, stroke=OPEN_STROKE, pad=5, min_w=200)
        parts.append(b_j)
        parts.append(arrow(370, 290, 435, cy, color=OPEN_STROKE, sw=1.5))
        parts.append(arrow(645, cy, 700, 290, color=OPEN_STROKE, sw=1.5))

    box_res2, _, _ = textbox(770, 290, "Миттєвий звіт\n(детермінований .bin)", size=11, fill=OPEN_FILL, stroke=OPEN_STROKE, pad=6, min_w=130, bold=True)
    parts.append(box_res2)

    parts.append(text(W / 2, H - 14,
                      "відмова від ліцензійних донглів дозволяє безперешкодно масштабувати перевірку й збірку прошивок у хмарі",
                      size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "ci-pipeline-bottleneck.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_stack_comparison()
    fig_decoupling_layers()
    fig_ci_bottleneck()
    print("Figures generated successfully in ./img/")
