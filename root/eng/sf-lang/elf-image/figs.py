# -*- coding: utf-8 -*-
"""Генератор векторних SVG-фігур для теми 'elf-image'."""

import sys
import os

# 4 рівні вгору до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_elf_binary_layout_structure():
    """Фігура 1: Анатомія ELF-образу: двоїстий погляд (лінкер/завантажувач) та внутрішні таблиці."""
    w, h = 980, 560
    frags = []

    # Заголовок фігури
    frags.append(text(w / 2, 28, "Внутрішня структура двійкового ELF-образу: двоїстий погляд (Dual View)", size=16, bold=True))

    # --- Ліва колонка: Фізичний макет файлу на диску ---
    frags.append(text(170, 68, "Фізичний ELF-файл на диску", size=14, bold=True, color=INK))

    file_blocks = [
        ("ELF Header (Elf32_Ehdr / Elf64_Ehdr)\nMagic 0x7F 'ELF', Клас, Ендіан, e_entry, e_phoff, e_shoff", 40, 95, 260, 52, "#f4f6f8", LINE, True),
        ("Program Header Table (таблиця сегментів)\nElf32_Phdr: PT_LOAD 1 (RX), PT_LOAD 2 (RW)", 40, 155, 260, 46, "#eafaf1", FIELD, True),
        ("Секція .isr_vector (Таблиця векторів переривань)", 40, 209, 260, 32, "#fcf3cf", "#b7950b", False),
        ("Секція .text (Машинний код функцій / Flash)", 40, 247, 260, 34, "#e8f8f5", FIELD, False),
        ("Секція .rodata (Рядкові константи, таблиці)", 40, 287, 260, 34, "#e8f8f5", FIELD, False),
        ("Секція .data (Початкові значення змінних)", 40, 327, 260, 34, "#fadbd8", POS, False),
        ("Секція .symtab & .strtab (Таблиця імен і символів)", 40, 367, 260, 34, "#ebf5fb", NEG, False),
        ("Секції .debug_* (DWARF інформація налагодження)", 40, 407, 260, 34, "#f5eef8", "#7d3c98", False),
        ("Секція .shstrtab (Рядки імен секцій)", 40, 447, 260, 32, "#ebf5fb", NEG, False),
        ("Section Header Table (таблиця заголовків секцій)\nElf32_Shdr: зміщення, розміри, прапорці SHF_*", 40, 487, 260, 48, "#fdebd0", POS, True),
    ]

    for title, bx, by, bw, bh, fill_c, strk_c, is_b in file_blocks:
        frags.append(fitbox(bx, by, bw, bh, title, size=11, fill=fill_c, stroke=strk_c, bold=is_b))

    # --- Центральна частина: Погляд завантажувача (Program Headers / Segments) ---
    frags.append(text(490, 68, "Погляд завантажувача (Execution View)", size=14, bold=True, color=FIELD))

    # Сегмент 1: Flash RX
    frags.append(rect(340, 100, 290, 205, fill="#fdfefe", stroke=FIELD, sw=1.8, rx=6))
    frags.append(rect(340, 100, 290, 30, fill="#d5f5e3", stroke=FIELD, sw=1.8, rx=6))
    frags.append(text(485, 120, "Сегмент PT_LOAD 1: FLASH (R-X)", size=12, bold=True, color=FIELD))
    frags.append(fitbox(350, 136, 270, 40, "p_vaddr = p_paddr = 0x08000000\np_flags = PF_R | PF_X\np_filesz = p_memsz", size=10, fill="#ffffff", stroke=FIELD))
    frags.append(fitbox(350, 180, 270, 34, "Включає секції коду та констант:\n.isr_vector + .text + .rodata", size=10, fill="#eafaf1", stroke=FIELD))
    frags.append(fitbox(350, 218, 270, 42, "LMA образ даних .data (Flash):\nСирі початкові байти для RAM", size=10, fill="#fcf3cf", stroke="#b7950b"))
    frags.append(fitbox(350, 264, 270, 34, "Заливається у Flash безпосередньо", size=10, fill="#e8f8f5", stroke=FIELD, bold=True))

    # Сегмент 2: RAM RW
    frags.append(rect(340, 325, 290, 210, fill="#fdfefe", stroke=POS, sw=1.8, rx=6))
    frags.append(rect(340, 325, 290, 30, fill="#fadbd8", stroke=POS, sw=1.8, rx=6))
    frags.append(text(485, 345, "Сегмент PT_LOAD 2: RAM (RW-)", size=12, bold=True, color=POS))
    frags.append(fitbox(350, 361, 270, 40, "p_vaddr = 0x20000000 (VMA в RAM)\np_paddr = LMA у Flash (звідки копіювати)\np_flags = PF_R | PF_W", size=10, fill="#ffffff", stroke=POS))
    frags.append(fitbox(350, 405, 270, 38, ".data: p_filesz байтів з файлу\n(початкові значення змінних)", size=10, fill="#fadbd8", stroke=POS))
    frags.append(fitbox(350, 447, 270, 42, ".bss: p_memsz - p_filesz байтів\n(у файлі немає, обнуляється в RAM)", size=10, fill="#f4f6f8", stroke=LINE))
    frags.append(fitbox(350, 493, 270, 34, "Розгортається в оперативній пам'яті", size=10, fill="#fadbd8", stroke=POS, bold=True))

    # --- Права колонка: Погляд лінкера та зневаджувача (Section Headers / Tooling) ---
    frags.append(text(810, 68, "Погляд лінкера / GDB (Linkage View)", size=14, bold=True, color=NEG))

    frags.append(rect(660, 100, 290, 435, fill="#fdfefe", stroke=NEG, sw=1.8, rx=6))
    frags.append(rect(660, 100, 290, 30, fill="#ebf5fb", stroke=NEG, sw=1.8, rx=6))
    frags.append(text(805, 120, "Таблиця Section Headers (Elf32_Shdr)", size=12, bold=True, color=NEG))

    shdr_items = [
        ("sh_name -> .text (PROGBITS, ALLOC|EXEC)\nsh_addr = 0x08000100, sh_offset = 0x1000", "#e8f8f5", FIELD),
        ("sh_name -> .rodata (PROGBITS, ALLOC)\nsh_addr = 0x08008000, sh_offset = 0x8F00", "#e8f8f5", FIELD),
        ("sh_name -> .data (PROGBITS, ALLOC|WRITE)\nsh_addr = 0x20000000, sh_offset = 0x9800", "#fadbd8", POS),
        ("sh_name -> .bss (NOBITS, ALLOC|WRITE)\nsh_addr = 0x20000400, sh_offset = 0 (0 байт у файлі!)", "#f4f6f8", LINE),
        ("sh_name -> .symtab (SYMTAB, нічого в чип!)\nТаблиця символів: функції, адреси, змінні", "#ebf5fb", NEG),
        ("sh_name -> .strtab (STRTAB, рядки символів)\nІмена функцій: main, Reset_Handler...", "#ebf5fb", NEG),
        ("sh_name -> .debug_info (DWARF для GDB)\nВідповідність адрес рядкам сирцевого коду", "#f5eef8", "#7d3c98"),
    ]

    sy = 136
    for itm_text, fill_c, strk_c in shdr_items:
        frags.append(fitbox(670, sy, 270, 52, itm_text, size=10, fill=fill_c, stroke=strk_c))
        sy += 56

    # Стрілки зв'язку
    frags.append(arrow(302, 178, 338, 178, color=FIELD, sw=1.5))
    frags.append(arrow(302, 344, 338, 370, color=POS, sw=1.5))
    frags.append(arrow(302, 511, 658, 480, color=NEG, sw=1.5))

    render(os.path.join(OUT_DIR, "elf-binary-layout-structure.svg"), w, h, *frags)


def fig_lma_vma_memory_mapping():
    """Фігура 2: Зіставлення LMA (Flash) та VMA (RAM) під час старту мікроконтролера."""
    w, h = 980, 520
    frags = []

    frags.append(text(w / 2, 28, "Відображення пам'яті мікроконтролера: LMA (Flash) проти VMA (SRAM)", size=16, bold=True))

    # --- Ліва панель: Flash пам'ять (LMA простір) ---
    frags.append(text(210, 68, "Flash пам'ять (LMA — Load Memory Address)", size=14, bold=True, color=FIELD))

    # Flash Box
    frags.append(rect(50, 95, 320, 390, fill="#fdfefe", stroke=FIELD, sw=2, rx=8))
    frags.append(rect(50, 95, 320, 32, fill="#d5f5e3", stroke=FIELD, sw=2, rx=8))
    frags.append(text(210, 116, "Flash (Енергонезалежна ROM: 0x08000000)", size=12, bold=True, color=FIELD))

    flash_sections = [
        ("0x08000000: .isr_vector (Вектори Cortex-M)\nПочатковий SP (_estack) та Reset_Handler", 60, 135, 300, 48, "#fcf3cf", "#b7950b"),
        ("0x08000100: .text (Машинні інструкції коду)\nВиконується процесором прямо з Flash (XIP)", 60, 189, 300, 52, "#e8f8f5", FIELD),
        ("0x08008000: .rodata (Незмінні константи)\nРядкові літерали, таблиці перерахунку", 60, 247, 300, 48, "#e8f8f5", FIELD),
        ("0x08009800: .data (Початковий образ у Flash)\nLMA адреса = символ _sidata\n(Сирі початкові значення змінних)", 60, 301, 300, 65, "#fadbd8", POS),
        ("Вільний залишок Flash пам'яті\n(Доступний для розширення коду)", 60, 372, 300, 44, "#f4f6f8", LINE),
        (".bss у Flash МІСЦЯ НЕ ЗАЙМАЄ! (0 байтів)", 60, 422, 300, 36, "#ffffff", POS),
    ]

    for title, bx, by, bw, bh, fill_c, strk_c in flash_sections:
        frags.append(fitbox(bx, by, bw, bh, title, size=10, fill=fill_c, stroke=strk_c))

    # --- Центральна частина: Дії стартового коду Reset_Handler ---
    frags.append(text(490, 68, "Ініціалізація C/C++ рантайму", size=13, bold=True, color=INK))

    frags.append(rect(390, 160, 200, 130, fill="#fef9e7", stroke="#f39c12", sw=1.5, rx=6))
    frags.append(text(490, 182, "1. Копіювання .data", size=12, bold=True, color="#b7950b"))
    frags.append(fitbox(396, 196, 188, 86, "memcpy(\n  &_sdata,\n  &_sidata,\n  &_edata - &_sdata\n);\nКопіює Flash LMA -> RAM VMA", size=9.5, fill="#ffffff", stroke="#f39c12"))

    frags.append(rect(390, 310, 200, 130, fill="#ebf5fb", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(490, 332, "2. Очищення .bss", size=12, bold=True, color=NEG))
    frags.append(fitbox(396, 346, 188, 86, "memset(\n  &_sbss,\n  0,\n  &_ebss - &_sbss\n);\nОбнуляє статичні змінні\nбез початкових значень", size=9.5, fill="#ffffff", stroke=NEG))

    # Стрілки копіювання
    frags.append(arrow(362, 335, 388, 230, color=POS, sw=1.8))
    frags.append(arrow(592, 230, 618, 175, color=POS, sw=1.8))
    frags.append(arrow(592, 375, 618, 245, color=NEG, sw=1.8))

    # --- Права панель: SRAM пам'ять (VMA простір) ---
    frags.append(text(770, 68, "SRAM пам'ять (VMA — Virtual Memory Address)", size=14, bold=True, color=POS))

    frags.append(rect(610, 95, 320, 390, fill="#fdfefe", stroke=POS, sw=2, rx=8))
    frags.append(rect(610, 95, 320, 32, fill="#fadbd8", stroke=POS, sw=2, rx=8))
    frags.append(text(770, 116, "SRAM (Оперативна RAM: 0x20000000)", size=12, bold=True, color=POS))

    ram_sections = [
        ("0x20000000: .data (_sdata .. _edata)\nVMA = адреса виконання в RAM\n(Змінні читаються і записуються CPU)", 620, 135, 300, 55, "#fadbd8", POS),
        ("0x20000400: .bss (_sbss .. _ebss)\nЗмінні за замовчуванням = 0\n(Ініціалізуються нулями під час старту)", 620, 196, 300, 55, "#eaf2f8", NEG),
        ("0x20000800: Купа (Heap / _ebss .. _end)\nДинамічна пам'ять malloc / new\n(Зростає за адресами ВГОРУ ->)", 620, 257, 300, 52, "#eafaf1", FIELD),
        ("Вільна пам'ять SRAM (Запас між стеком і купою)\nКонтроль переповнення стека", 620, 315, 300, 46, "#f4f6f8", LINE),
        ("0x2001FFFC: Стек (Stack / _estack)\nЛокальні змінні, кадри функцій\n(Зростає за адресами ВНИЗ <-)", 620, 367, 300, 54, "#fcf3cf", "#b7950b"),
        ("0x20020000: Вершина RAM (Кінець фізичної SRAM)", 620, 427, 300, 32, "#ffffff", LINE),
    ]

    for title, bx, by, bw, bh, fill_c, strk_c in ram_sections:
        frags.append(fitbox(bx, by, bw, bh, title, size=10, fill=fill_c, stroke=strk_c))

    render(os.path.join(OUT_DIR, "lma-vma-memory-mapping.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_elf_binary_layout_structure()
    fig_lma_vma_memory_mapping()
    print("Всі фігури згенеровано успішно у ./img/")
