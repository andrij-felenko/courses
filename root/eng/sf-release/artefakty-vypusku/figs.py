# -*- coding: utf-8 -*-
import sys, os

# Додаємо шлях до scripts/ у корені репозиторію (4 рівні вгору від root/eng/sf-release/artefakty-vypusku)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фіг. 1: Анатомія повного релізного пакета ──────────────────────────────
def fig_release_bundle_anatomy():
    W, H = 1060, 620
    p = []
    
    # Загальне тло
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(W / 2, 40, "Анатомія повного релізного пакета вбудованого продукту", size=16, color="#0f172a", bold=True))
    p.append(text(W / 2, 60, "Комплект постачання: від виконавчого бінарника до сертифікатів безпеки та довгострокового архіву", size=11, color="#64748b"))
    
    # Головний контейнер пакета
    box_x, box_y, box_w, box_h = 30, 85, 680, 510
    p.append(rect(box_x, box_y, box_w, box_h, fill="#f8fafc", stroke="#2563eb", sw=1.8, rx=6))
    p.append(text(box_x + 20, box_y + 28, "Релізний архів випуску (firmware-v2.4.0-release.tar.zst)", size=13, color="#1e40af", bold=True, anchor="start"))
    
    # 6 ключових артефактів всередині
    artifacts = [
        ("1. Виробничий бінарний образ", "firmware.bin / firmware.hex / app.dfu", "Чистий виконуваний код для прошивки у Flash мікроконтролера через завантажувач чи JTAG.", "#0284c7", "#eff6ff"),
        ("2. Налагоджувальний ELF з DWARF", "firmware.elf (повні секції .debug_*)", "Таблиці символів, типів, змінних і номерів рядків коду для розбору аварійних дампів.", "#7c3aed", "#faf5ff"),
        ("3. Файл мапи лінкера (Memory Map)", "firmware.map (секції, крос-референси)", "Точні фізичні адреси Flash/RAM, розміри функцій і статичних буферів, межі стека й купи.", "#059669", "#f0fdf4"),
        ("4. Підписаний маніфест прошивки", "manifest.json + manifest.sig (Ed25519)", "Версія, ревізія заліза, лічильник анти-відкату, геш образу та криптографічний підпис.", "#d97706", "#fffbeb"),
        ("5. Специфікація компонентів (SBOM)", "sbom.spdx.json / sbom.cdx.json", "Машиночитаний перелік усіх сторонніх бібліотек, ліцензій, версій і pURL для аудиту CVE.", "#dc2626", "#fef2f2"),
        ("6. Звіти верифікації та контрольні суми", "tests-junit.xml, misra.sarif, SHA256SUMS", "Протоколи прогону модульних тестів, статичного аналізу, HIL-тестів та SHA-256 хеші.", "#475569", "#f1f5f9"),
    ]
    
    card_w = 310
    card_h = 135
    for i, (title, fname, desc, col, bg_col) in enumerate(artifacts):
        col_idx = i % 2
        row_idx = i // 2
        cx = box_x + 20 + col_idx * (card_w + 20)
        cy = box_y + 45 + row_idx * (card_h + 15)
        
        p.append(rect(cx, cy, card_w, card_h, fill=bg_col, stroke=col, sw=1.2, rx=5))
        p.append(text(cx + 12, cy + 22, title, size=11, color=col, bold=True, anchor="start"))
        p.append(rect(cx + 12, cy + 32, card_w - 24, 24, fill="#ffffff", stroke="#cbd5e1", sw=0.8, rx=3))
        p.append(text(cx + 18, cy + 48, fname, size=9.5, color="#1e293b", bold=True, anchor="start"))
        
        tb, _, _ = textbox(cx + card_w / 2, cy + 92, desc, size=9.5, pad=6, fill="none", stroke="none", color="#475569", min_w=card_w - 24)
        p.append(tb)

    # Правий блок: Цільові споживачі артефактів
    dest_x = 735
    p.append(text(dest_x + 150, box_y + 20, "Цільові споживачі та сценарії", size=13, color="#0f172a", bold=True))
    
    destinations = [
        ("Завантажувач / OTA / Фабрика", "Приймає .bin та перевіряє manifest.sig", "#0284c7", box_y + 45),
        ("Інженери підтримки / Тріаж", "Декодують HardFault через .elf та .map", "#7c3aed", box_y + 160),
        ("Відділ кібербезпеки / DevSecOps", "Аналізують SBOM на відомі вразливості CVE", "#dc2626", box_y + 275),
        ("Орган сертифікації / Аудит (10+ років)", "Перевіряють звіти тестів та SHA256SUMS", "#059669", box_y + 390),
    ]
    
    for title, role, col, dy in destinations:
        p.append(rect(dest_x, dy, 295, 95, fill="#ffffff", stroke=col, sw=1.4, rx=5))
        p.append(circle(dest_x + 20, dy + 28, 6, fill=col, stroke="none"))
        p.append(text(dest_x + 35, dy + 32, title, size=11, color=col, bold=True, anchor="start"))
        p.append(text(dest_x + 35, dy + 58, role, size=9.5, color="#334155", anchor="start"))
        p.append(line(box_x + box_w, dy + 47, dest_x, dy + 47, color=col, sw=1.2, dash="4,3"))
        p.append(circle(box_x + box_w, dy + 47, 3, fill=col, stroke="none"))

    render(os.path.join(OUT, "release-bundle-anatomy.svg"), W, H, *p)


# ── Фіг. 2: Відокремлення налагоджувальних символів DWARF від бінарника ─────
def fig_elf_stripping_and_symbol_separation():
    W, H = 1060, 580
    p = []
    
    # Загальне тло
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(W / 2, 38, "Розділення налагоджувальних символів DWARF та виконуваного образу", size=16, color="#0f172a", bold=True))
    p.append(text(W / 2, 58, "Формування компактного бінарника для Flash-пам'яті та збереження повного ELF для тріажу крашів", size=11, color="#64748b"))
    
    # Лівий блок: Монолітний вихід лінкера
    p.append(rect(30, 85, 270, 465, fill="#f8fafc", stroke="#475569", sw=1.5, rx=6))
    p.append(text(165, 112, "Повний вихід лінкера (LD)", size=13, color="#1e293b", bold=True))
    p.append(text(165, 130, "firmware.elf (~4.8 МБ)", size=10, color="#64748b"))
    
    elf_sections = [
        (".text (машинний код)", "Виконуваний код мікроконтролера", "#0284c7"),
        (".rodata (константи, рядки)", "Таблиці, рядкові літерали", "#0284c7"),
        (".data (ініціалізовані дані)", "Початкові значення змінних", "#0284c7"),
        (".bss (неініціалізовані дані)", "Обнулені змінні в RAM", "#059669"),
        (".symtab & .strtab", "Таблиця імен та глобальних символів", "#7c3aed"),
        (".debug_info & .debug_line", "DWARF: відповідність адрес рядкам коду", "#7c3aed"),
        (".debug_frame & .debug_loc", "DWARF: розгортання стека та регістри", "#7c3aed"),
    ]
    
    for idx, (sname, sdesc, scol) in enumerate(elf_sections):
        sy = 150 + idx * 52
        p.append(rect(45, sy, 240, 44, fill="#ffffff", stroke=scol, sw=1.0, rx=4))
        p.append(text(55, sy + 18, sname, size=10, color=scol, bold=True, anchor="start"))
        p.append(text(55, sy + 34, sdesc, size=9, color="#64748b", anchor="start"))
        
    # Центральний блок: Операції утиліт objcopy та strip
    p.append(rect(335, 175, 300, 110, fill="#eff6ff", stroke="#2563eb", sw=1.3, rx=5))
    p.append(text(485, 200, "1. Виділення бінарника для Flash", size=11, color="#1d4ed8", bold=True))
    p.append(text(485, 220, "arm-none-eabi-objcopy -O binary", size=9.5, color="#0f172a"))
    p.append(text(485, 238, "firmware.elf firmware.bin", size=9.5, color="#0f172a"))
    p.append(text(485, 262, "Відсікання всіх .debug_* секцій", size=9, color="#64748b"))
    
    p.append(rect(335, 345, 300, 110, fill="#faf5ff", stroke="#7c3aed", sw=1.3, rx=5))
    p.append(text(485, 370, "2. Ізоляція налагоджувального образу", size=11, color="#6d28d9", bold=True))
    p.append(text(485, 390, "arm-none-eabi-objcopy --only-keep-debug", size=9.5, color="#0f172a"))
    p.append(text(485, 408, "firmware.elf firmware.debug", size=9.5, color="#0f172a"))
    p.append(text(485, 432, "Збереження DWARF для довгострокового архіву", size=9, color="#64748b"))
    
    # Зв'язувальні лінії
    p.append(arrow(300, 230, 335, 230, color="#2563eb", sw=1.5))
    p.append(arrow(300, 400, 335, 400, color="#7c3aed", sw=1.5))
    
    # Правий блок: Результати та застосування
    # 1. Flash binary
    p.append(rect(670, 150, 360, 155, fill="#f0fdf4", stroke="#059669", sw=1.4, rx=5))
    p.append(text(685, 175, "Виробничий образ: firmware.bin (192 КБ)", size=12, color="#047857", bold=True, anchor="start"))
    p.append(text(685, 198, "• Містить лише секції завантаження: .text + .rodata + .data", size=9.5, color="#1e293b", anchor="start"))
    p.append(text(685, 218, "• Нульовий оверхед розміру — швидке прошивання по OTA", size=9.5, color="#1e293b", anchor="start"))
    p.append(text(685, 238, "• Прошивається в фізичну Flash-пам'ять пристрою", size=9.5, color="#1e293b", anchor="start"))
    p.append(text(685, 275, "УВАГА: Без ELF аналіз крашів у полі неможливий!", size=9.5, color="#dc2626", bold=True, anchor="start"))
    p.append(arrow(635, 230, 670, 230, color="#059669", sw=1.5))
    
    # 2. Crash Triage with ELF
    p.append(rect(670, 330, 360, 220, fill="#f8fafc", stroke="#7c3aed", sw=1.4, rx=5))
    p.append(text(685, 355, "Розслідування аварії (Crash Triage)", size=12, color="#6d28d9", bold=True, anchor="start"))
    
    p.append(rect(685, 370, 330, 50, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    p.append(text(695, 388, "Дамп регістра при HardFault: PC = 0x08004F2C", size=9.5, color="#b91c1c", bold=True, anchor="start"))
    p.append(text(695, 406, "Без символів адреса 0x08004F2C — це невідомі байти.", size=9, color="#64748b", anchor="start"))
    
    p.append(text(685, 438, "addr2line -e firmware.elf 0x08004F2C", size=9.5, color="#0f172a", bold=True, anchor="start"))
    
    p.append(rect(685, 450, 330, 50, fill="#f0fdf4", stroke="#86efac", sw=1.0, rx=4))
    p.append(text(695, 468, "РЕЗУЛЬТАТ: sensor_driver.c:142", size=9.5, color="#15803d", bold=True, anchor="start"))
    p.append(text(695, 486, "Функція: bme280_read_pressure_raw()", size=9, color="#1e293b", anchor="start"))
    
    p.append(text(685, 532, "Архів ELF гарантує відновлення контексту через роки", size=9, color="#4338ca", bold=True, anchor="start"))
    p.append(arrow(635, 400, 670, 400, color="#7c3aed", sw=1.5))
    
    render(os.path.join(OUT, "elf-stripping-and-symbol-separation.svg"), W, H, *p)


# ── Фіг. 3: Структура мапи пам'яті (Memory Map) ────────────────────────────
def fig_memory_map_analysis_flow():
    W, H = 1060, 600
    p = []
    
    # Загальне тло
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(W / 2, 38, "Анатомія файлу мапи лінкера (Linker Memory Map)", size=16, color="#0f172a", bold=True))
    p.append(text(W / 2, 58, "Розподіл простору Flash і RAM, таблиця перехресних посилань і контроль колізії стека й купи", size=11, color="#64748b"))
    
    # Ліва колонка: Фізична пам'ять Flash (ROM)
    fx, fy, fw, fh = 40, 85, 300, 485
    p.append(rect(fx, fy, fw, fh, fill="#eff6ff", stroke="#2563eb", sw=1.6, rx=6))
    p.append(text(fx + fw / 2, fy + 26, "Регіон FLASH (ROM) [512 КБ]", size=13, color="#1d4ed8", bold=True))
    p.append(text(fx + fw / 2, fy + 44, "Адреси: 0x08000000 - 0x08080000", size=9.5, color="#64748b"))
    
    flash_blocks = [
        ("0x08000000", ".isr_vector (Вектори переривань)", "1 КБ | Таблиця векторів ARM Cortex-M", "#1e40af"),
        ("0x08000400", ".text (Машинні інструкції коду)", "148 КБ | Функції застосунку та RTOS", "#0284c7"),
        ("0x08025400", ".rodata (Константи, таблиці LUT)", "32 КБ | Рядкові літерали, конфігурація", "#0891b2"),
        ("0x0802D400", ".data (Образ завантаження LMA)", "12 КБ | Початкові значення для RAM", "#d97706"),
        ("0x08030400", "[ Вільний простір FLASH ]", "319 КБ | Запас для майбутніх OTA оновлень", "#059669"),
    ]
    for idx, (addr, title, sub, col) in enumerate(flash_blocks):
        by = fy + 65 + idx * 80
        p.append(rect(fx + 15, by, fw - 30, 68, fill="#ffffff", stroke=col, sw=1.1, rx=4))
        p.append(text(fx + 25, by + 18, addr, size=9, color="#64748b", bold=True, anchor="start"))
        p.append(text(fx + 25, by + 36, title, size=10, color=col, bold=True, anchor="start"))
        p.append(text(fx + 25, by + 54, sub, size=9, color="#475569", anchor="start"))
        
    # Центральна колонка: Фізична пам'ять SRAM (RAM)
    rx, ry, rw, rh = 380, 85, 300, 485
    p.append(rect(rx, ry, rw, rh, fill="#fdf4ff", stroke="#c026d3", sw=1.6, rx=6))
    p.append(text(rx + rw / 2, ry + 26, "Регіон SRAM (RAM) [128 КБ]", size=13, color="#a21caf", bold=True))
    p.append(text(rx + rw / 2, ry + 44, "Адреси: 0x20000000 - 0x20020000", size=9.5, color="#64748b"))
    
    ram_blocks = [
        ("0x20000000", ".data (Ініціалізовані змінні)", "12 КБ | Копіюються з Flash під час Startup", "#d97706"),
        ("0x20003000", ".bss (Обнулені змінні)", "48 КБ | Буфери пакетів, стан FreeRTOS", "#7c3aed"),
        ("0x2000F000", "Купа (Heap) [Зростає вгору ↑]", "Символ _end: динамічне виділення пам'яті", "#2563eb"),
        ("0x2001A000", "[ Запас безпеки: Зазор стека ]", "20 КБ | Бар'єр захисту від переповнення", "#059669"),
        ("0x20020000", "Стек (Stack) [Зростає вниз ↓]", "Символ _estack: локальні змінні, фрейми", "#dc2626"),
    ]
    for idx, (addr, title, sub, col) in enumerate(ram_blocks):
        by = ry + 65 + idx * 80
        p.append(rect(rx + 15, by, rw - 30, 68, fill="#ffffff", stroke=col, sw=1.1, rx=4))
        p.append(text(rx + 25, by + 18, addr, size=9, color="#64748b", bold=True, anchor="start"))
        p.append(text(rx + 25, by + 36, title, size=10, color=col, bold=True, anchor="start"))
        p.append(text(rx + 25, by + 54, sub, size=9, color="#475569", anchor="start"))

    # Права колонка: Що саме релізний аудит витягує з .map файлу
    px, py, pw, ph = 720, 85, 305, 485
    p.append(rect(px, py, pw, ph, fill="#f8fafc", stroke="#475569", sw=1.4, rx=6))
    p.append(text(px + pw / 2, py + 26, "Ключові метрики файлу .map", size=13, color="#0f172a", bold=True))
    p.append(text(px + pw / 2, py + 44, "Генерація: -Wl,-Map=firmware.map,--cref", size=9.5, color="#64748b"))
    
    metrics = [
        ("1. Перевірка лімітів пам'яті", "Чи не перевищує розмір .text + .rodata доступну Flash-пам'ять, і який відсоток RAM зайнято статично.", "#1e293b"),
        ("2. Розподіл за модулями", "Таблиця розмірів кожного об'єктного файлу (.o): хто саме вніс найбільший внесок у роздування пам'яті.", "#1e293b"),
        ("3. Крос-референси (--cref)", "Повний граф викликів: який файл і функція посилаються на кожен символ, виявлення мертвого коду.", "#1e293b"),
        ("4. Запобігання колізії стека й купи", "Оцінка відстані між вершиною купи (_end) та початком стека (_estack) під час пікового навантаження.", "#dc2626"),
        ("5. Порівняння релізів (Diff Map)", "Порівняння мапи v1.0.0 і v1.0.1 виявляє неочікуване розширення буферів перед релізом.", "#059669")
    ]
    for idx, (mtitle, mdesc, mcol) in enumerate(metrics):
        my = py + 65 + idx * 80
        p.append(rect(px + 12, my, pw - 24, 68, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
        p.append(text(px + 20, my + 20, mtitle, size=10.5, color=mcol, bold=True, anchor="start"))
        tb, _, _ = textbox(px + pw / 2, my + 44, mdesc, size=9, pad=4, fill="none", stroke="none", color="#475569", min_w=pw - 36)
        p.append(tb)

    render(os.path.join(OUT, "memory-map-analysis-flow.svg"), W, H, *p)


# ── Фіг. 4: Конвеєр довгострокового архівування на 10+ років ────────────────
def fig_long_term_archival_pipeline():
    W, H = 1060, 580
    p = []
    
    # Загальне тло
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(W / 2, 38, "Конвеєр довгострокового архівування релізних артефактів (10+ років)", size=16, color="#0f172a", bold=True))
    p.append(text(W / 2, 58, "Герметичне середовище збірки, незмінне сховище (WORM) та захист від деградації носіїв (Bit-rot)", size=11, color="#64748b"))
    
    # Етап 1: Герметичний вхід збірки
    s1_x, s1_y, s1_w, s1_h = 30, 90, 220, 450
    p.append(rect(s1_x, s1_y, s1_w, s1_h, fill="#eff6ff", stroke="#2563eb", sw=1.4, rx=6))
    p.append(text(s1_x + s1_w / 2, s1_y + 26, "1. Вхідні дані збірки", size=12.5, color="#1d4ed8", bold=True))
    p.append(text(s1_x + s1_w / 2, s1_y + 44, "Герметичні залежності", size=9.5, color="#64748b"))
    
    in_items = [
        ("Git Commit Hash", "Повний зріз вихідного коду та сабмодулів", "#1e293b"),
        ("OCI Container Digest", "Фіксація компілятора GCC, libc, CMake за sha256", "#1e293b"),
        ("Скрипти лінкера (.ld)", "Конфігурація апаратної пам'яті та периферії", "#1e293b"),
        ("Підписаний тег версії", "Семантична версія v2.4.0 підписана GPG", "#1e293b"),
    ]
    for idx, (ititle, idesc, icol) in enumerate(in_items):
        iy = s1_y + 65 + idx * 90
        p.append(rect(s1_x + 12, iy, s1_w - 24, 76, fill="#ffffff", stroke="#93c5fd", sw=1.0, rx=4))
        p.append(text(s1_x + 20, iy + 22, ititle, size=10, color=icol, bold=True, anchor="start"))
        tb, _, _ = textbox(s1_x + s1_w / 2, iy + 48, idesc, size=9, pad=4, fill="none", stroke="none", color="#64748b", min_w=s1_w - 36)
        p.append(tb)
        
    p.append(arrow(s1_x + s1_w, 315, s1_x + s1_w + 35, 315, color="#2563eb", sw=1.8))
    
    # Етап 2: Генерація та пакування пакета
    s2_x, s2_y, s2_w, s2_h = 285, 90, 220, 450
    p.append(rect(s2_x, s2_y, s2_w, s2_h, fill="#faf5ff", stroke="#7c3aed", sw=1.4, rx=6))
    p.append(text(s2_x + s2_w / 2, s2_y + 26, "2. Релізний пакет", size=12.5, color="#6d28d9", bold=True))
    p.append(text(s2_x + s2_w / 2, s2_y + 44, "Комплект 7 артефактів", size=9.5, color="#64748b"))
    
    pkg_items = [
        ("Виробничий .bin / .hex", "Чистий виконуваний образ", "#0284c7"),
        ("Налагоджувальний .elf", "DWARF-символи та типи", "#7c3aed"),
        ("Мапа пам'яті .map", "Точні адреси та ліміти", "#059669"),
        ("SBOM (SPDX / CDX)", "Інвентар компонентів", "#dc2626"),
        ("Маніфест + Підписи", "manifest.sig, SHA256SUMS", "#d97706"),
    ]
    for idx, (ititle, idesc, icol) in enumerate(pkg_items):
        iy = s2_y + 65 + idx * 72
        p.append(rect(s2_x + 12, iy, s2_w - 24, 60, fill="#ffffff", stroke=icol, sw=1.0, rx=4))
        p.append(text(s2_x + 20, iy + 22, ititle, size=9.5, color=icol, bold=True, anchor="start"))
        p.append(text(s2_x + 20, iy + 42, idesc, size=9, color="#64748b", anchor="start"))
        
    p.append(arrow(s2_x + s2_w, 315, s2_x + s2_w + 35, 315, color="#7c3aed", sw=1.8))
    
    # Етап 3: Довгострокове незмінне сховище (WORM & Tape)
    s3_x, s3_y, s3_w, s3_h = 540, 90, 240, 450
    p.append(rect(s3_x, s3_y, s3_w, s3_h, fill="#f0fdf4", stroke="#059669", sw=1.4, rx=6))
    p.append(text(s3_x + s3_w / 2, s3_y + 26, "3. Довгостроковий архів", size=12.5, color="#047857", bold=True))
    p.append(text(s3_x + s3_w / 2, s3_y + 44, "Зберігання 10-25 років", size=9.5, color="#64748b"))
    
    store_items = [
        ("WORM Cloud Object Lock", "Неможливість видалення чи модифікації файлів навіть адміністратором (Compliance Mode).", "#047857"),
        ("Стрічкові картриджі LTO", "Фізично ізольоване (Air-gapped) автономне зберігання в сейфі датацентру.", "#047857"),
        ("Регулярний скрабінг гешів", "Автоматична фонова перевірка SHA-256 сум раз на 6 місяців проти біт-роту (Bit-rot).", "#047857"),
    ]
    for idx, (ititle, idesc, icol) in enumerate(store_items):
        iy = s3_y + 65 + idx * 120
        p.append(rect(s3_x + 12, iy, s3_w - 24, 105, fill="#ffffff", stroke="#86efac", sw=1.0, rx=4))
        p.append(text(s3_x + 20, iy + 22, ititle, size=10, color=icol, bold=True, anchor="start"))
        tb, _, _ = textbox(s3_x + s3_w / 2, iy + 58, idesc, size=9, pad=4, fill="none", stroke="none", color="#334155", min_w=s3_w - 36)
        p.append(tb)
        
    p.append(arrow(s3_x + s3_w, 315, s3_x + s3_w + 35, 315, color="#059669", sw=1.8))
    
    # Етап 4: Сценарії через 5–10 років
    s4_x, s4_y, s4_w, s4_h = 815, 90, 215, 450
    p.append(rect(s4_x, s4_y, s4_w, s4_h, fill="#fffbeb", stroke="#d97706", sw=1.4, rx=6))
    p.append(text(s4_x + s4_w / 2, s4_y + 26, "4. Використання в майбутньому", size=12.5, color="#b45309", bold=True))
    p.append(text(s4_x + s4_w / 2, s4_y + 44, "Через 5, 10 або 15 років", size=9.5, color="#64748b"))
    
    future_items = [
        ("Тріаж інцидентів у полі", "Розбір HardFault на ретро-пристрої за оригінальним ELF та мапою .map", "#b45309"),
        ("Аудит безпеки (CVE)", "Миттєва перевірка за SBOM без розбирання бінарника", "#b45309"),
        ("Гарантійні рекламації", "Звіти HIL-тестів як доказ коректності на момент релізу", "#b45309"),
        ("Екстрений патч", "Відтворення збірки байт-у-байт у зафіксованому OCI-контейнері", "#b45309"),
    ]
    for idx, (ititle, idesc, icol) in enumerate(future_items):
        iy = s4_y + 65 + idx * 90
        p.append(rect(s4_x + 10, iy, s4_w - 20, 76, fill="#ffffff", stroke="#fcd34d", sw=1.0, rx=4))
        p.append(text(s4_x + 18, iy + 22, ititle, size=9.5, color=icol, bold=True, anchor="start"))
        tb, _, _ = textbox(s4_x + s4_w / 2, iy + 48, idesc, size=9, pad=4, fill="none", stroke="none", color="#475569", min_w=s4_w - 30)
        p.append(tb)

    render(os.path.join(OUT, "long-term-archival-pipeline.svg"), W, H, *p)


def main():
    fig_release_bundle_anatomy()
    fig_elf_stripping_and_symbol_separation()
    fig_memory_map_analysis_flow()
    fig_long_term_archival_pipeline()
    print("Generated 4 SVG figures successfully.")

if __name__ == "__main__":
    main()
