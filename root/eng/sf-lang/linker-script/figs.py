# -*- coding: utf-8 -*-
"""Генератор векторних SVG-фігур для теми 'linker-script'."""

import sys
import os

# 4 рівні вгору до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_memory_regions_lma_vma():
    """Фігура 1: Фізичний адресний простір, LMA та VMA, розміщення у Flash та RAM."""
    w, h = 940, 520
    frags = []

    frags.append(text(w / 2, 28, "Фізичний адресний простір, LMA (завантаження) та VMA (виконання)", size=16, bold=True))

    # --- Ліва колонка: Енергонезалежна пам'ять Flash (LMA) ---
    frags.append(text(220, 65, "FLASH (ROM / NVM) — LMA", size=14, bold=True, color=POS))
    frags.append(text(220, 83, "0x08000000..0x08080000 (512 KB, rx)", size=11, color=MUTED))

    # Рамка Flash
    frags.append(rect(60, 95, 320, 370, fill="#fdf2e9", stroke=POS, sw=1.5, rx=8))

    # Секції у Flash
    b1 = fitbox(75, 110, 290, 55, ".isr_vector (Вектори переривань)\nVMA = 0x08000000 | LMA = 0x08000000\nПочатковий MSP + адреса Reset_Handler", size=11, fill="#fadbd8", stroke=POS, bold=False)
    frags.append(b1)

    b2 = fitbox(75, 175, 290, 65, ".text (Машинні інструкції коду)\nVMA = 0x08000100 | LMA = 0x08000100\nПряме виконання з Flash (XIP — I-Code bus)", size=11, fill="#fdebd0", stroke="#d35400", bold=False)
    frags.append(b2)

    b3 = fitbox(75, 250, 290, 55, ".rodata (Константи, рядкові літерали)\nVMA = 0x08005400 | LMA = 0x08005400\nНезмінні таблиці, const-дані (D-Code bus)", size=11, fill="#fef9e7", stroke="#f39c12", bold=False)
    frags.append(b3)

    b4 = fitbox(75, 315, 290, 80, "Початкові значення .data (_sidata)\nLMA = 0x08006200  (зберігається у Flash!)\nКопіюється стартовим кодом у RAM при Reset\nFlash зберігає стан між вимкненнями живлення", size=11, fill="#d5f5e3", stroke=FIELD, bold=False)
    frags.append(b4)

    b5 = fitbox(75, 405, 290, 48, "Вільний простір Flash (Unused ROM)\n0x08006800 .. 0x0807FFFF (~486 KB вільних)", size=10, fill="#eaeded", stroke=MUTED, bold=False)
    frags.append(b5)

    # --- Права колонка: Оперативна пам'ять RAM (VMA) ---
    frags.append(text(720, 65, "SRAM (RAM) — VMA", size=14, bold=True, color=NEG))
    frags.append(text(720, 83, "0x20000000..0x20020000 (128 KB, xrw)", size=11, color=MUTED))

    # Рамка RAM
    frags.append(rect(560, 95, 320, 370, fill="#ebf5fb", stroke=NEG, sw=1.5, rx=8))

    # Секції у RAM
    b6 = fitbox(575, 110, 290, 65, ".data (Ініціалізовані змінні)\nVMA = 0x20000000..0x20000600\nЗмінні з ненульовим початком: int x = 42;\nСюди копіюються дані з _sidata при старті", size=11, fill="#d5f5e3", stroke=FIELD, bold=False)
    frags.append(b6)

    b7 = fitbox(575, 185, 290, 60, ".bss (Нульові змінні та буфери)\nVMA = 0x20000600..0x20002100\nint y = 0; static char buf[4096];\nСтартовий код обнуляє ділянку (0x00)", size=11, fill="#d6eaf8", stroke=NEG, bold=False)
    frags.append(b7)

    b8 = fitbox(575, 255, 290, 55, "._user_heap_stack (Купа та стек)\nКупа росте вгору (-> 0x20002100+)\nСтек росте вниз (<- _estack = 0x20020000)", size=11, fill="#e8daef", stroke="#8e44ad", bold=False)
    frags.append(b8)

    b9 = fitbox(575, 320, 290, 55, "CCMRAM / Backup SRAM (Спеціальні банки)\n0x10000000 (64 KB швидкої RAM для FPU/DSP)\n0x40024000 (4 KB пам'яті батарейного живлення)", size=10, fill="#fcf3cf", stroke="#b7950b", bold=False)
    frags.append(b9)

    b10 = fitbox(575, 385, 290, 68, "Верхівка стека (_estack = 0x20020000)\nMSP апаратно завантажується з адреси 0x08000000\nпри виникненні апаратного сигналу RESET", size=10, fill="#fdedec", stroke=POS, bold=False)
    frags.append(b10)

    # --- Зв'язувальні лінії LMA -> VMA (обхідні, без накладання) ---
    # Маршрут: вихід праворуч з Flash .data (365, 355) -> вниз і вправо -> підйом -> вхід у RAM .data (560, 142)
    frags.append(line(365, 355, 410, 355, color=FIELD, sw=2.0))
    frags.append(line(410, 355, 410, 210, color=FIELD, sw=2.0))
    frags.append(line(410, 210, 480, 210, color=FIELD, sw=2.0))
    frags.append(line(480, 210, 480, 142, color=FIELD, sw=2.0))
    frags.append(arrow(480, 142, 560, 142, color=FIELD, sw=2.0))

    # Текстовий блок по центру у вільній зоні (y=235..285, x=395..545)
    frags.append(fitbox(395, 235, 150, 50, "Стартове копіювання:\nFlash LMA -> SRAM VMA", size=10, fill="#ffffff", stroke=FIELD, bold=True))

    # Нижній висновок
    b_bot = fitbox(60, 475, 820, 36, "VMA (Virtual/Execution Address) — де код і змінні знаходяться під час виконання.\nLMA (Load Memory Address) — де секція фізично зберігається у прошивці до запуску.", size=11, fill="#f4f6f8", stroke=LINE)
    frags.append(b_bot)

    out_file = os.path.join(OUT_DIR, "memory-regions-lma-vma.svg")
    render(out_file, w, h, *frags)


def fig_linker_script_architecture():
    """Фігура 2: Анатомія та внутрішні компоненти GNU LD скрипта компонування."""
    w, h = 940, 500
    frags = []

    frags.append(text(w / 2, 28, "Анатомія скрипта компонувальника GNU LD (.ld)", size=16, bold=True))

    # 1. Заголовок і точка входу
    b_entry = fitbox(40, 60, 260, 75, "ENTRY(Reset_Handler)\nВизначає точку входу для налагоджувача\n(gdb, OpenOCD, Segger J-Link)", size=11, fill="#e8f8f5", stroke=FIELD)
    frags.append(b_entry)

    # 2. Директива MEMORY
    b_mem = fitbox(340, 60, 560, 75, "MEMORY { FLASH (rx) : ORIGIN = 0x08000000, LENGTH = 512K\n         RAM (xrw)  : ORIGIN = 0x20000000, LENGTH = 128K }\nОголошує фізичні банки пам'яті, їхній розмір та права доступу (r/w/x)", size=11, fill="#fef9e7", stroke="#d35400")
    frags.append(b_mem)

    # 3. Директива SECTIONS
    frags.append(text(470, 160, "SECTIONS { ... } — Розподіл вхідних секцій об'єктних файлів (*.o) по вихідних сегментах", size=13, bold=True, color=INK))

    # Блок секцій
    frags.append(rect(40, 175, 860, 240, fill="#fbfcfc", stroke=LINE, sw=1.5, rx=8))

    # Стовпчик 1: Код і вектори
    b_sec_text = fitbox(60, 195, 255, 205, ".isr_vector : {\n  KEEP(*(.isr_vector))\n} >FLASH\n\n.text : {\n  . = ALIGN(4);\n  *(.text*)\n  *(.rodata*)\n  . = ALIGN(4);\n} >FLASH", size=11, fill="#fdf2e9", stroke=POS)
    frags.append(b_sec_text)

    # Стовпчик 2: Дані (LMA -> VMA)
    b_sec_data = fitbox(340, 195, 260, 205, ".data : {\n  . = ALIGN(4);\n  _sdata = .;\n  *(.data*)\n  . = ALIGN(4);\n  _edata = .;\n} >RAM AT>FLASH\n\n_sidata = LOADADDR(.data);", size=11, fill="#eafaf1", stroke=FIELD)
    frags.append(b_sec_data)

    # Стовпчик 3: BSS, стек і купа
    b_sec_bss = fitbox(625, 195, 255, 205, ".bss : {\n  . = ALIGN(4);\n  _sbss = .;\n  *(.bss*)\n  *(COMMON)\n  . = ALIGN(4);\n  _ebss = .;\n} >RAM\n\n_estack = ORIGIN(RAM) + LENGTH(RAM);", size=11, fill="#ebf5fb", stroke=NEG)
    frags.append(b_sec_bss)

    # Пояснення ключових операторів знизу
    b_foot = fitbox(40, 430, 860, 55, "Ключові оператори:  . (Location Counter) — поточна адреса  |  ALIGN(n) — вирівнювання за межею n байтів\nKEEP() — заборона видалення секції оптимізатором --gc-sections  |  PROVIDE() — умовний символ", size=11, fill="#f4f6f8", stroke=LINE)
    frags.append(b_foot)

    out_file = os.path.join(OUT_DIR, "linker-script-architecture.svg")
    render(out_file, w, h, *frags)


def fig_startup_initialization_flow():
    """Фігура 3: Послідовність виконання стартового коду та взаємодія з символами .ld."""
    w, h = 940, 520
    frags = []

    frags.append(text(w / 2, 28, "Апаратне скидання та послідовність виконання Startup-коду", size=16, bold=True))

    # Крок 1: Апаратний Reset
    b_step1 = fitbox(30, 65, 250, 110, "1. АПАРАТНИЙ RESET\nАпаратний контролер Cortex-M:\n• Зчитує 0x08000000 -> MSP (_estack)\n• Зчитує 0x08000004 -> PC (Reset_Handler)\n• Встановлює режим Thumb (T-біт = 1)", size=11, fill="#fadbd8", stroke=POS)
    frags.append(b_step1)

    frags.append(arrow(280, 120, 340, 120, color=POS, sw=2.0))

    # Крок 2: Копіювання .data
    b_step2 = fitbox(340, 65, 260, 110, "2. КОПІЮВАННЯ .data\nЦикл копіювання байтів/слів:\n• Джерело: Flash LMA (_sidata)\n• Приймач: RAM VMA (_sdata)\n• Межа: _edata\n• Відновлює ненульові змінні", size=11, fill="#d5f5e3", stroke=FIELD)
    frags.append(b_step2)

    frags.append(arrow(600, 120, 660, 120, color=FIELD, sw=2.0))

    # Крок 3: Обнулення .bss
    b_step3 = fitbox(660, 65, 250, 110, "3. ОБНУЛЕННЯ .bss\nЦикл запису нулів (0x00):\n• Початок: _sbss (RAM)\n• Кінець: _ebss (RAM)\n• Очищує пам'ять від випадкового\n  сміття після ввімкнення живлення", size=11, fill="#d6eaf8", stroke=NEG)
    frags.append(b_step3)

    frags.append(arrow(785, 175, 785, 230, color=NEG, sw=2.0))

    # Крок 4: Ініціалізація C++ рантайму
    b_step4 = fitbox(500, 230, 410, 100, "4. C++ КОНСТРУКТОРИ ТА СИСТЕМНІ ГОДИННИКИ\n• Виклик SystemInit() (налаштування тактування PLL, FPU, Flash Latency)\n• Виклик __libc_init_array() (обхід таблиці покажчиків .init_array)\n• Виконання конструкторів глобальних і статичних об'єктів C++", size=11, fill="#fef9e7", stroke="#d35400")
    frags.append(b_step4)

    frags.append(arrow(500, 280, 440, 280, color="#d35400", sw=2.0))

    # Крок 5: Вхід у main()
    b_step5 = fitbox(30, 230, 410, 100, "5. ВИКЛИК ГОЛОВНОЇ ПРОГРАМИ main()\n• main() починає виконання з гарантією підготовленої пам'яті\n• Усі глобальні змінні містять валідні значення\n• Стек сконфігурований, FPU увімкнено, периферія готова до роботи", size=11, fill="#e8f8f5", stroke=FIELD)
    frags.append(b_step5)

    # Деталізація ролі лінкерних символів
    b_symbols = fitbox(30, 355, 880, 140, "Символи компонувальника є точками синхронізації між .ld та кодом стартапу:\n• _estack — адреса верхівки стека в оперативній пам'яті (записується у нульовий слот таблиці векторів);\n• _sidata — початкова адреса джерела даних .data у Flash (повертається функцією LOADADDR(.data));\n• _sdata / _edata — діапазон адрес призначення секції .data в RAM (VMA);\n• _sbss / _ebss — діапазон адрес секції .bss в RAM, які обов'язково заповнюються нулями до виклику main().", size=11, fill="#f4f6f8", stroke=LINE)
    frags.append(b_symbols)

    out_file = os.path.join(OUT_DIR, "startup-initialization-flow.svg")
    render(out_file, w, h, *frags)


if __name__ == "__main__":
    fig_memory_regions_lma_vma()
    fig_linker_script_architecture()
    fig_startup_initialization_flow()
    print("Фігури успішно згенеровано.")
