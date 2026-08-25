# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми inspect-a-foreign-binary."""
import sys, os

# Додаємо scripts/ до шляху пошуку модулів
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def fig_triage_pipeline(out_dir):
    """Фігура 1: Конвеєр безпечного неінвазивного аудиту чужого бінарника."""
    w, h = 940, 480
    frags = []

    # Фон і загальна рамка
    frags.append(rect(10, 10, 920, 460, fill="#fafbfc", stroke="#d1d5db", sw=1.5, rx=8))
    frags.append(text(470, 40, "Послідовний конвеєр статичного аудиту невідомого бінарника", size=16, bold=True))

    steps = [
        {
            "x": 30, "y": 70, "w": 205, "h": 370,
            "title": "1. Експрес-паспорт", "sub": "Утиліта: file",
            "color": NEG, "bg": "#eff6ff",
            "items": [
                ("Магічні байти:", "ELF64 / ELF32"),
                ("Архітектура:", "x86-64 / ARM64"),
                ("Порядок байтів:", "Little / Big Endian"),
                ("Тип файлу:", "EXEC / DYN (PIE)"),
                ("Лінкування:", "Static / Dynamic"),
                ("Символи:", "stripped / not stripped")
            ],
            "footer": "Результат: Цільова платформа"
        },
        {
            "x": 255, "y": 70, "w": 205, "h": 370,
            "title": "2. Безпечні залежності", "sub": "readelf -d | grep NEEDED",
            "color": FIELD, "bg": "#f0fdf4",
            "items": [
                ("Заборона ldd:", "Ризик виконання коду"),
                ("Спільні ліби:", "libc, libssl, libcrypto"),
                ("Інтерпретатор:", "PT_INTERP (ld-linux)"),
                ("Шляхи лінкування:", "DT_RUNPATH / RPATH"),
                ("Динамічні теги:", "DT_SONAME, DT_FLAGS"),
                ("Відсутні .so:", "Аудит перед пуском")
            ],
            "footer": "Результат: Граф бібліотек"
        },
        {
            "x": 480, "y": 70, "w": 205, "h": 370,
            "title": "3. Анатомія структури", "sub": "readelf -l -S -s / objdump",
            "color": "#8b5cf6", "bg": "#f5f3ff",
            "items": [
                ("Заголовки:", "Program / Section Headers"),
                ("Сегменти:", "PT_LOAD, PT_GNU_STACK"),
                ("Безпека пам'яті:", "NX-біт, Full/Partial RELRO"),
                ("Символи .dynsym:", "Імпорт (UND) / Експорт"),
                ("Секції даних:", ".text, .rodata, .bss"),
                ("Точка входу:", "e_entry (_start / main)")
            ],
            "footer": "Результат: Модель пам'яті й API"
        },
        {
            "x": 705, "y": 70, "w": 205, "h": 370,
            "title": "4. Текстовий аудит", "sub": "strings -a -n 8 / grep",
            "color": POS, "bg": "#fef2f2",
            "items": [
                ("Мережеві адреси:", "URL, IPv4/IPv6, домени"),
                ("Секрети / токени:", "API-ключі, сертифікати"),
                ("Файлові шляхи:", "/etc, /tmp, /dev, .so"),
                ("Параметри CLI:", "Опції, прапорці, env vars"),
                ("Повідомлення логів:", "Формати printf, помилки"),
                ("Шляхи компіляції:", "GCC/Clang, DWARF-файли")
            ],
            "footer": "Результат: Приховані константи"
        }
    ]

    for s in steps:
        frags.append(rect(s["x"], s["y"], s["w"], s["h"], fill=s["bg"], stroke=s["color"], sw=1.5, rx=6))
        frags.append(text(s["x"] + s["w"]/2, s["y"] + 24, s["title"], size=13, color=s["color"], bold=True))
        frags.append(text(s["x"] + s["w"]/2, s["y"] + 42, s["sub"], size=11, color=MUTED, italic=True))
        frags.append(line(s["x"] + 10, s["y"] + 52, s["x"] + s["w"] - 10, s["y"] + 52, color=s["color"], sw=1, dash="2,2"))

        item_y = s["y"] + 74
        for label, val in s["items"]:
            frags.append(text(s["x"] + 12, item_y, label, size=11, color=INK, anchor="start", bold=True))
            frags.append(text(s["x"] + 12, item_y + 16, val, size=11, color="#374151", anchor="start"))
            item_y += 40

        frags.append(rect(s["x"] + 10, s["y"] + s["h"] - 38, s["w"] - 20, 26, fill=s["color"], stroke=s["color"], rx=4))
        frags.append(text(s["x"] + s["w"]/2, s["y"] + s["h"] - 21, s["footer"], size=11, color="#ffffff", bold=True))

    out_path = os.path.join(out_dir, "foreign-binary-triage-pipeline.svg")
    render(out_path, w, h, *frags)


def fig_elf_dual_view(out_dir):
    """Фігура 2: Двоїста природа ELF: Segments (ядро) проти Sections (аналітик)."""
    w, h = 920, 470
    frags = []

    frags.append(rect(10, 10, 900, 450, fill="#ffffff", stroke="#d1d5db", sw=1.5, rx=8))
    frags.append(text(460, 36, "Двоїста архітектура ELF: Program Headers (сегменти) та Section Headers (секції)", size=15, bold=True))

    # Ліва колонка: Execution View (Segments)
    frags.append(rect(30, 60, 250, 380, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(155, 86, "Execution View (Ядро)", size=14, color=NEG, bold=True))
    frags.append(text(155, 104, "Program Headers (readelf -l)", size=11, color=MUTED))

    seg_boxes = [
        (30 + 15, 120, 220, 42, "PT_PHDR / PT_INTERP", "Шлях динамічного лінкера", "#dbeafe"),
        (30 + 15, 172, 220, 75, "PT_LOAD (Код & Сталі)", "Права: R-E (RX)\nВідображається в пам'ять", "#bfdbfe"),
        (30 + 15, 257, 220, 75, "PT_LOAD (Змінні дані)", "Права: RW- (RW)\nВідображається в пам'ять", "#bfdbfe"),
        (30 + 15, 342, 220, 42, "PT_DYNAMIC", "Таблиця лінкування", "#dbeafe"),
        (30 + 15, 392, 220, 36, "PT_GNU_STACK / RELRO", "Захист: NX / RO після релокацій", "#e0e7ff")
    ]
    for bx, by, bw, bh, title, desc, bg_c in seg_boxes:
        frags.append(rect(bx, by, bw, bh, fill=bg_c, stroke=NEG, sw=1, rx=4))
        frags.append(text(bx + bw/2, by + 16, title, size=11, color=NEG, bold=True))
        lines = desc.split("\n")
        if len(lines) == 1:
            frags.append(text(bx + bw/2, by + 30, lines[0], size=10, color=INK))
        else:
            frags.append(text(bx + bw/2, by + 34, lines[0], size=10, color=INK))
            frags.append(text(bx + bw/2, by + 48, lines[1], size=9, color=MUTED))

    # Центральна колонка: Фізичний ELF файл
    frags.append(rect(340, 60, 240, 380, fill="#f9fafb", stroke="#4b5563", sw=1.5, rx=6))
    frags.append(text(460, 86, "Фізичний бінарний файл", size=14, color=INK, bold=True))
    frags.append(text(460, 104, "Зміщення байтів (Offsets)", size=11, color=MUTED))

    file_blocks = [
        (355, 120, 210, 30, "ELF Header (64 байти)", "#e5e7eb"),
        (355, 155, 210, 35, "Program Header Table", "#dbeafe"),
        (355, 195, 210, 50, ".interp, .rodata, .text", "#c7d2fe"),
        (355, 250, 210, 45, ".data, .got, .dynamic", "#fed7aa"),
        (355, 300, 210, 30, ".bss (NOBITS, 0 байт у файлі)", "#ffedd5"),
        (355, 335, 210, 45, ".symtab, .strtab, .debug_*", "#dcfce7"),
        (355, 385, 210, 45, "Section Header Table", "#bbf7d0")
    ]
    for bx, by, bw, bh, title, bg_c in file_blocks:
        frags.append(rect(bx, by, bw, bh, fill=bg_c, stroke="#6b7280", sw=1, rx=4))
        frags.append(text(bx + bw/2, by + bh/2 + 4, title, size=11, color=INK, bold=True))

    # Права колонка: Linking View (Sections)
    frags.append(rect(640, 60, 250, 380, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(765, 86, "Linking View (Аналітик)", size=14, color=FIELD, bold=True))
    frags.append(text(765, 104, "Section Headers (readelf -S)", size=11, color=MUTED))

    sec_boxes = [
        (640 + 15, 120, 220, 40, ".text", "Машинні інструкції коду", "#dcfce7"),
        (640 + 15, 168, 220, 40, ".rodata", "Рядкові літерали та константи", "#dcfce7"),
        (640 + 15, 216, 220, 40, ".data", "Ініціалізовані глобальні змінні", "#fef3c7"),
        (640 + 15, 264, 220, 40, ".bss", "Неініціалізовані змінні (нулі)", "#fef3c7"),
        (640 + 15, 312, 220, 40, ".dynsym / .dynstr", "Динамічні символи рантайму", "#e0e7ff"),
        (640 + 15, 360, 220, 68, ".symtab / .debug_*", "Символи для відлагодження\n(видаляються утилітою strip)", "#fee2e2")
    ]
    for bx, by, bw, bh, title, desc, bg_c in sec_boxes:
        frags.append(rect(bx, by, bw, bh, fill=bg_c, stroke=FIELD, sw=1, rx=4))
        frags.append(text(bx + bw/2, by + 16, title, size=11, color=FIELD, bold=True))
        lines = desc.split("\n")
        if len(lines) == 1:
            frags.append(text(bx + bw/2, by + 30, lines[0], size=10, color=INK))
        else:
            frags.append(text(bx + bw/2, by + 34, lines[0], size=10, color=INK))
            frags.append(text(bx + bw/2, by + 48, lines[1], size=9, color=MUTED))

    # З'єднувальні стрілки між колонками
    frags.append(arrow(280, 210, 335, 210, color=NEG, sw=1.5))
    frags.append(arrow(280, 290, 335, 290, color=NEG, sw=1.5))
    frags.append(arrow(640, 140, 585, 210, color=FIELD, sw=1.5))
    frags.append(arrow(640, 236, 585, 270, color=FIELD, sw=1.5))
    frags.append(arrow(640, 394, 585, 360, color=FIELD, sw=1.5))

    out_path = os.path.join(out_dir, "elf-dual-view-segments-sections.svg")
    render(out_path, w, h, *frags)


def fig_ldd_trap(out_dir):
    """Фігура 3: Пастка ldd проти безпечного аудиту через readelf."""
    w, h = 920, 440
    frags = []

    frags.append(rect(10, 10, 900, 420, fill="#fafbfc", stroke="#d1d5db", sw=1.5, rx=8))
    frags.append(text(460, 38, "Небезпека ldd для невідомого коду проти безпечного статичного аналізу", size=15, bold=True))

    # Ліва половина: Пастка ldd (Червона зона)
    frags.append(rect(30, 65, 415, 345, fill="#fff5f5", stroke=POS, sw=1.5, rx=6))
    frags.append(text(237, 95, "ПАСТКА: Запуск ldd на чужому файлі", size=14, color=POS, bold=True))
    frags.append(text(237, 114, "ldd — це shell-скрипт, який ВИКОНУЄ програму", size=11, color=MUTED))

    ldd_steps = [
        (50, 135, 375, 45, "1. Запуск через завантажувач", "ldd встановлює LD_TRACE_LOADED_OBJECTS=1\nі викликає інтерпретатор для файлу", "#fee2e2"),
        (50, 190, 375, 55, "2. Пастка PT_INTERP", "Якщо PT_INTERP вказує на шкідливий бінарник,\nядро запустить його з повними правами користувача!", "#fecaca"),
        (50, 255, 375, 55, "3. Виконання .init_array / DT_INIT", "Конструктори бібліотек та ініціалізатори\nможуть виконатися ДО завершення трасування!", "#fca5a5"),
        (50, 320, 375, 75, "Результат: Компрометація хоста", "Довільний код виконується у вашій системі!\nНіколи не застосовуйте ldd до підозрілих файлів.", POS)
    ]
    for bx, by, bw, bh, title, desc, bg_c in ldd_steps:
        if bg_c == POS:
            frags.append(rect(bx, by, bw, bh, fill=POS, stroke=POS, rx=4))
            frags.append(text(bx + bw/2, by + 22, title, size=12, color="#ffffff", bold=True))
            lines = desc.split("\n")
            frags.append(text(bx + bw/2, by + 44, lines[0], size=10, color="#ffffff"))
            frags.append(text(bx + bw/2, by + 58, lines[1], size=10, color="#ffffff", bold=True))
        else:
            frags.append(rect(bx, by, bw, bh, fill=bg_c, stroke=POS, sw=1, rx=4))
            frags.append(text(bx + bw/2, by + 16, title, size=11, color=POS, bold=True))
            lines = desc.split("\n")
            frags.append(text(bx + bw/2, by + 32, lines[0], size=10, color=INK))
            if len(lines) > 1:
                frags.append(text(bx + bw/2, by + 45, lines[1], size=9, color=MUTED))

    # Права половина: Безпечний аудит (Зелена зона)
    frags.append(rect(475, 65, 415, 345, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(682, 95, "БЕЗПЕЧНО: Статичний парсинг readelf", size=14, color=FIELD, bold=True))
    frags.append(text(682, 114, "Читання байтів файлу без завантаження та запуску", size=11, color=MUTED))

    safe_steps = [
        (495, 135, 375, 45, "1. readelf -d binary | grep NEEDED", "Парсить виключно записи DT_NEEDED у секції .dynamic\nбез виконання жодної інструкції", "#dcfce7"),
        (495, 190, 375, 55, "2. readelf -l binary | grep INTERP", "Безпечно зчитує рядок динамічного інтерпретатора\nяк простий масив символів", "#bbf7d0"),
        (495, 255, 375, 55, "3. readelf -d binary | grep RPATH", "Витягує зашиті шляхи пошуку бібліотек\n(DT_RUNPATH / DT_RPATH)", "#86efac"),
        (495, 320, 375, 75, "Результат: 100% Безпечний аналіз", "Повний перелік залежностей без ризику\nвиконання шкідливого коду або конструкторів.", FIELD)
    ]
    for bx, by, bw, bh, title, desc, bg_c in safe_steps:
        if bg_c == FIELD:
            frags.append(rect(bx, by, bw, bh, fill=FIELD, stroke=FIELD, rx=4))
            frags.append(text(bx + bw/2, by + 22, title, size=12, color="#ffffff", bold=True))
            lines = desc.split("\n")
            frags.append(text(bx + bw/2, by + 44, lines[0], size=10, color="#ffffff"))
            frags.append(text(bx + bw/2, by + 58, lines[1], size=10, color="#ffffff", bold=True))
        else:
            frags.append(rect(bx, by, bw, bh, fill=bg_c, stroke=FIELD, sw=1, rx=4))
            frags.append(text(bx + bw/2, by + 16, title, size=11, color=FIELD, bold=True))
            lines = desc.split("\n")
            frags.append(text(bx + bw/2, by + 32, lines[0], size=10, color=INK))
            if len(lines) > 1:
                frags.append(text(bx + bw/2, by + 45, lines[1], size=9, color=MUTED))

    out_path = os.path.join(out_dir, "ldd-execution-trap-vs-safe-audit.svg")
    render(out_path, w, h, *frags)


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "img")
    if not os.path.exists(out):
        os.makedirs(out)
    fig_triage_pipeline(out)
    fig_elf_dual_view(out)
    fig_ldd_trap(out)
    print("All figures generated successfully.")
