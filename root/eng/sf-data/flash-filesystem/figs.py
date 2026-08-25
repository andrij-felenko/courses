# -*- coding: utf-8 -*-
"""Фігури до статті «Файлові системи у Flash».
Генерує векторні схеми SVG у теці ./img/:
1. flash-physics-asymmetry.svg — фізична асиметрія флеш-пам'яті (блок стирання проти сторінки запису)
2. raw-vs-managed-flash.svg — стеки пам'яті: «сирий» Flash (MTD + Flash FS) проти керованого (FTL + Block FS)
3. log-structured-cow-cycle.svg — цикл оновлення out-of-place, маркування недійсних сторінок та збирання сміття
4. littlefs-metadata-ctz.svg — архітектура LittleFS: пара метаданих і CTZ-пропускний список блоків даних
5. ubifs-ubi-architecture.svg — дворівнева архітектура UBI та UBIFS у Linux
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# 1. Фізична асиметрія Flash-пам'яті
# ─────────────────────────────────────────────────────────────────────────────
def fig_flash_physics_asymmetry():
    W, H = 840, 440
    parts = []

    # Тло
    parts.append(rect(15, 15, 810, 410, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(420, 45, "Фізична асиметрія Flash: стирання блоками проти запису сторінками", size=16, color=INK, bold=True))

    # Ліва панель: Блок стирання
    parts.append(rect(40, 75, 360, 325, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=6))
    parts.append(text(220, 102, "Блок стирання (Erase Block: 128 КБ – 4 МБ)", size=13, color="#1e293b", bold=True))
    parts.append(text(220, 122, "Мінімальна неподільна одиниця очищення", size=11, color="#64748b"))

    # Сторінки всередині блоку
    page_y = 140
    page_h = 36
    pages = [
        ("Сторінка 0 (2–4 КБ)", "0x00 (Записано дані)", "#fee2e2", "#ef4444", "#991b1b"),
        ("Сторінка 1 (2–4 КБ)", "0x00 (Записано дані)", "#fee2e2", "#ef4444", "#991b1b"),
        ("Сторінка 2 (2–4 КБ)", "0xFF (Чиста, готова до запису)", "#dcfce7", "#22c55e", "#166534"),
        ("Сторінка 3..N", "0xFF (Чисті сторінки)", "#dcfce7", "#22c55e", "#166534"),
    ]

    for i, (p_title, p_state, bg_c, brd_c, txt_c) in enumerate(pages):
        y = page_y + i * 44
        parts.append(rect(60, y, 320, page_h, fill=bg_c, stroke=brd_c, sw=1.2, rx=4))
        parts.append(text(135, y + 22, p_title, size=11, color="#1e293b", bold=True))
        parts.append(text(285, y + 22, p_state, size=10, color=txt_c))

    parts.append(rect(60, 325, 320, 60, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=4))
    parts.append(text(220, 345, "Стирання: переводить усі біти 0 → 1 (0xFF)", size=11, color="#334155", bold=True))
    parts.append(text(220, 365, "Вимагає високої напруги (~15–20 В) та 1–5 мс часу", size=10, color="#64748b"))

    # Права панель: Операції та обмеження
    parts.append(rect(430, 75, 370, 325, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=6))
    parts.append(text(615, 102, "Правила переходу станів комірки", size=13, color="#1e293b", bold=True))
    parts.append(text(615, 122, "Односпрямованість бітових змін", size=11, color="#64748b"))

    # Блок Програмування
    parts.append(rect(450, 140, 330, 72, fill="#eff6ff", stroke="#3b82f6", sw=1.2, rx=6))
    parts.append(text(615, 162, "1. Програмування (Program / Write)", size=12, color="#1d4ed8", bold=True))
    parts.append(text(615, 182, "Перехід 1 → 0 (зарядження плаваючого затвора)", size=11, color="#1e40af"))
    parts.append(text(615, 199, "Виконується посторінково; час: 200–800 мкс", size=10, color="#475569"))

    # Блок Неможливості перезапису
    parts.append(rect(450, 222, 330, 72, fill="#fef2f2", stroke="#ef4444", sw=1.2, rx=6))
    parts.append(text(615, 244, "2. Неможливість перезапису на місці", size=12, color="#b91c1c", bold=True))
    parts.append(text(615, 264, "Перехід 0 → 1 неможливий без стирання всього блоку!", size=10, color="#991b1b", bold=True))
    parts.append(text(615, 281, "Оновлення вимагає запису в нове вільне місце (out-of-place)", size=10, color="#475569"))

    # Блок Ресурсу
    parts.append(rect(450, 304, 330, 81, fill="#fffbeb", stroke="#f59e0b", sw=1.2, rx=6))
    parts.append(text(615, 324, "3. Обмежений ресурс (P/E Cycles)", size=12, color="#b45309", bold=True))
    parts.append(text(615, 344, "SLC: 50k–100k · MLC: 3k–10k · TLC: 1k–3k циклів", size=10, color="#78350f"))
    parts.append(text(615, 361, "Нерівномірний знос призводить до деградації оксиду", size=10, color="#475569"))
    parts.append(text(615, 376, "і появи незворотних збійних блоків (Bad Blocks)", size=10, color="#475569"))

    render(os.path.join(OUT, "flash-physics-asymmetry.svg"), W, H, "\n".join(parts))


# ─────────────────────────────────────────────────────────────────────────────
# 2. Стеки пам'яті: Raw Flash проти Managed Flash
# ─────────────────────────────────────────────────────────────────────────────
def fig_raw_vs_managed_flash():
    W, H = 840, 420
    parts = []

    parts.append(rect(15, 15, 810, 390, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(420, 45, "Архітектурні стеки: «сирий» Flash проти керованого носія", size=16, color=INK, bold=True))

    col_w = 360
    col_h = 320
    y_top = 75

    # Ліва колонка: Керований Flash (SSD, eMMC, SD-картка)
    x_left = 45
    parts.append(rect(x_left, y_top, col_w, col_h, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=6))
    parts.append(text(x_left + col_w / 2, y_top + 28, "Керований Flash (SSD / eMMC / SD)", size=14, color="#1e293b", bold=True))

    layers_l = [
        ("Файлова система ОС (ext4, FAT32, NTFS)", "Працює з фіксованими 512B / 4KB LBA секторами", "#e2e8f0", "#64748b"),
        ("Блоковий рівень ядра (Block Device)", "Черги запитів, планувальник вводу/виводу", "#e2e8f0", "#64748b"),
        ("Апаратний контролер носія з FTL", "Трансляція LBA→PBA, Wear Leveling, GC у залізі", "#dbeafe", "#2563eb"),
        ("Фізичні масиви NAND Flash", "Закриті за інтерфейсом NVMe / SATA / eMMC / SPI", "#fee2e2", "#dc2626"),
    ]

    for i, (l_title, l_desc, bg_c, brd_c) in enumerate(layers_l):
        ly = y_top + 48 + i * 62
        parts.append(rect(x_left + 15, ly, col_w - 30, 52, fill=bg_c, stroke=brd_c, sw=1.2, rx=4))
        parts.append(text(x_left + col_w / 2, ly + 20, l_title, size=11, color="#0f172a", bold=True))
        parts.append(text(x_left + col_w / 2, ly + 38, l_desc, size=9, color="#475569"))

    # Права колонка: «Сирий» Flash (NOR / NAND у мікроконтролерах та Linux MTD)
    x_right = 435
    parts.append(rect(x_right, y_top, col_w, col_h, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=6))
    parts.append(text(x_right + col_w / 2, y_top + 28, "«Сирий» Flash (NOR / NAND без FTL)", size=14, color="#1e293b", bold=True))

    layers_r = [
        ("Спеціалізована Flash FS (LittleFS, UBIFS)", "Log-structured метадані, контроль зносу, захист живлення", "#dcfce7", "#16a34a"),
        ("Рівень абстракції (MTD / Block Driver)", "Доступ до фізичних операцій: read, prog, erase", "#e2e8f0", "#64748b"),
        ("Контролер шини SPI / QSPI / Parallel", "Апаратний інтерфейс мікроконтролера / SoC", "#e2e8f0", "#64748b"),
        ("Відкритий масив NOR / NAND Flash", "Прямий доступ програми до блоків і сторінок", "#fee2e2", "#dc2626"),
    ]

    for i, (l_title, l_desc, bg_c, brd_c) in enumerate(layers_r):
        ly = y_top + 48 + i * 62
        parts.append(rect(x_right + 15, ly, col_w - 30, 52, fill=bg_c, stroke=brd_c, sw=1.2, rx=4))
        parts.append(text(x_right + col_w / 2, ly + 20, l_title, size=11, color="#0f172a", bold=True))
        parts.append(text(x_right + col_w / 2, ly + 38, l_desc, size=9, color="#475569"))

    render(os.path.join(OUT, "raw-vs-managed-flash.svg"), W, H, "\n".join(parts))


# ─────────────────────────────────────────────────────────────────────────────
# 3. Log-Structured оновлення та цикл Garbage Collection
# ─────────────────────────────────────────────────────────────────────────────
def fig_log_structured_cow_cycle():
    W, H = 840, 480
    parts = []

    parts.append(rect(15, 15, 810, 450, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(420, 45, "Журнальний запис (Out-of-place) та цикл збирання сміття (GC)", size=16, color=INK, bold=True))

    # Стан 1: Початковий запис
    y1 = 80
    parts.append(rect(35, y1, 235, 360, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=6))
    parts.append(text(152, y1 + 25, "1. Початковий стан", size=13, color="#1e293b", bold=True))
    parts.append(text(152, y1 + 45, "Блок A: файл v1 записано", size=10, color="#64748b"))

    parts.append(rect(50, y1 + 65, 205, 42, fill="#dcfce7", stroke="#22c55e", sw=1.2, rx=4))
    parts.append(text(152, y1 + 90, "Стор. 0: Дані А (v1) [Дійсна]", size=10, color="#166534", bold=True))

    parts.append(rect(50, y1 + 115, 205, 42, fill="#dcfce7", stroke="#22c55e", sw=1.2, rx=4))
    parts.append(text(152, y1 + 140, "Стор. 1: Дані B (v1) [Дійсна]", size=10, color="#166534", bold=True))

    parts.append(rect(50, y1 + 165, 205, 42, fill="#f1f5f9", stroke="#cbd5e1", sw=1.2, rx=4))
    parts.append(text(152, y1 + 190, "Стор. 2: Чиста (0xFF)", size=10, color="#64748b"))

    parts.append(rect(50, y1 + 215, 205, 42, fill="#f1f5f9", stroke="#cbd5e1", sw=1.2, rx=4))
    parts.append(text(152, y1 + 240, "Стор. 3: Чиста (0xFF)", size=10, color="#64748b"))

    parts.append(text(152, y1 + 290, "Блок B (Повністю чистий)", size=11, color="#475569", bold=True))
    parts.append(rect(50, y1 + 305, 205, 38, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=4))
    parts.append(text(152, y1 + 328, "Усі сторінки 0xFF", size=10, color="#64748b"))

    # Стан 2: Оновлення даних (Out-of-place append)
    y2 = 80
    parts.append(rect(300, y2, 240, 360, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=6))
    parts.append(text(420, y2 + 25, "2. Оновлення блоку А", size=13, color="#1e293b", bold=True))
    parts.append(text(420, y2 + 45, "Нові дані пишуться в хвіст", size=10, color="#64748b"))

    parts.append(rect(315, y2 + 65, 210, 42, fill="#fee2e2", stroke="#ef4444", sw=1.2, rx=4))
    parts.append(text(420, y2 + 90, "Стор. 0: Дані А (v1) [ЗАСТАРІЛА]", size=10, color="#991b1b"))

    parts.append(rect(315, y2 + 115, 210, 42, fill="#dcfce7", stroke="#22c55e", sw=1.2, rx=4))
    parts.append(text(420, y2 + 140, "Стор. 1: Дані B (v1) [Дійсна]", size=10, color="#166534", bold=True))

    parts.append(rect(315, y2 + 165, 210, 42, fill="#dbeafe", stroke="#3b82f6", sw=1.2, rx=4))
    parts.append(text(420, y2 + 190, "Стор. 2: Дані А (v2) [ДІЙСНА]", size=10, color="#1e40af", bold=True))

    parts.append(rect(315, y2 + 215, 210, 42, fill="#f1f5f9", stroke="#cbd5e1", sw=1.2, rx=4))
    parts.append(text(420, y2 + 240, "Стор. 3: Чиста (0xFF)", size=10, color="#64748b"))

    parts.append(text(420, y2 + 290, "Покажчик файлу оновлено", size=11, color="#1d4ed8", bold=True))
    parts.append(text(420, y2 + 315, "Стор. 0 позначено недійсною", size=10, color="#b91c1c"))
    parts.append(text(420, y2 + 333, "Місце в Блоці A вичерпується", size=10, color="#64748b"))

    # Стан 3: Збирання сміття (Compaction & Erase)
    y3 = 80
    parts.append(rect(570, y3, 235, 360, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=6))
    parts.append(text(687, y3 + 25, "3. Збирання сміття (GC)", size=13, color="#1e293b", bold=True))
    parts.append(text(687, y3 + 45, "Копіювання дійсних + стирання", size=10, color="#64748b"))

    parts.append(text(687, y3 + 70, "Новий Блок B (Компактифікований):", size=10, color="#1e293b", bold=True))

    parts.append(rect(585, y3 + 85, 205, 40, fill="#dcfce7", stroke="#22c55e", sw=1.2, rx=4))
    parts.append(text(687, y3 + 109, "Стор. 0: Дані B (v1) [Скопійовано]", size=9, color="#166534", bold=True))

    parts.append(rect(585, y3 + 130, 205, 40, fill="#dcfce7", stroke="#22c55e", sw=1.2, rx=4))
    parts.append(text(687, y3 + 154, "Стор. 1: Дані A (v2) [Скопійовано]", size=9, color="#166534", bold=True))

    parts.append(rect(585, y3 + 175, 205, 36, fill="#f1f5f9", stroke="#cbd5e1", sw=1.2, rx=4))
    parts.append(text(687, y3 + 198, "Стор. 2..3: Чисті (0xFF)", size=9, color="#64748b"))

    parts.append(text(687, y3 + 240, "Старий Блок A:", size=10, color="#b91c1c", bold=True))
    parts.append(rect(585, y3 + 255, 205, 50, fill="#fee2e2", stroke="#ef4444", sw=1.2, rx=4))
    parts.append(text(687, y3 + 276, "ERASE BLOCK A", size=11, color="#991b1b", bold=True))
    parts.append(text(687, y3 + 293, "Увесь блок стерто у 0xFF", size=9, color="#7f1d1d"))

    parts.append(text(687, y3 + 330, "Лічильник стирань +1", size=10, color="#475569", bold=True))
    parts.append(text(687, y3 + 348, "Блок A готовий до нового циклу", size=9, color="#64748b"))

    render(os.path.join(OUT, "log-structured-cow-cycle.svg"), W, H, "\n".join(parts))


# ─────────────────────────────────────────────────────────────────────────────
# 4. LittleFS: Пара метаданих та CTZ Skip-list
# ─────────────────────────────────────────────────────────────────────────────
def fig_littlefs_metadata_ctz():
    W, H = 840, 440
    parts = []

    parts.append(rect(15, 15, 810, 410, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(420, 45, "LittleFS: Пара блоків метаданих та CTZ-пропускний список файлу", size=16, color=INK, bold=True))

    # Верхня половина: Metadata Pair
    parts.append(rect(35, 70, 770, 155, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=6))
    parts.append(text(420, 95, "Пара метаданих каталогу (Two-Block Metadata Pair)", size=13, color="#1e293b", bold=True))
    parts.append(text(420, 113, "Атомарне чергування ревізій забезпечує захист від раптового вимкнення живлення", size=11, color="#64748b"))

    # Блок 0
    parts.append(rect(55, 130, 335, 80, fill="#eff6ff", stroke="#3b82f6", sw=1.2, rx=4))
    parts.append(text(222, 152, "Блок 0 (Поточна ревізія: N=42)", size=11, color="#1d4ed8", bold=True))
    parts.append(text(222, 172, "Тег: Ревізія 42 | CRC32: 0x8F3A12 | Список тегів...", size=9, color="#1e40af"))
    parts.append(text(222, 192, "[АКТИВНИЙ БЛОК: містить валідний зріз каталогу]", size=9, color="#166534", bold=True))

    # Блок 1
    parts.append(rect(450, 130, 335, 80, fill="#fef2f2", stroke="#ef4444", sw=1.2, rx=4))
    parts.append(text(617, 152, "Блок 1 (Застаріла ревізія: N=41 або Компакція)", size=11, color="#b91c1c", bold=True))
    parts.append(text(617, 172, "Стирання перед записом N+1 або черговий лог змін", size=9, color="#991b1b"))
    parts.append(text(617, 192, "[РЕЗЕРВНИЙ БЛОК: оновлюється без ризику для Блоку 0]", size=9, color="#475569"))

    # Нижня половина: CTZ Skip-list
    parts.append(rect(35, 240, 770, 170, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=6))
    parts.append(text(420, 265, "CTZ-список блоків даних файлу (Count Trailing Zeros)", size=13, color="#1e293b", bold=True))
    parts.append(text(420, 283, "Зворотний зв'язок: блок містить покажчики на 2^k попередніх блоків; додавання в кінець O(1)", size=11, color="#64748b"))

    blocks = [
        ("Блок 0", "ctz(0)=0", "Покажчик: NULL", 80),
        ("Блок 1", "ctz(1)=0", "Покажчик -> Блок 0", 250),
        ("Блок 2", "ctz(2)=1", "-> Блок 1, -> Блок 0", 430),
        ("Блок 3", "ctz(3)=0", "-> Блок 2 (Голова)", 610),
    ]

    for b_title, b_ctz, b_ptrs, bx in blocks:
        parts.append(rect(bx, 305, 150, 88, fill="#dbeafe", stroke="#2563eb", sw=1.2, rx=4))
        parts.append(text(bx + 75, 328, b_title, size=11, color="#1e3a8a", bold=True))
        parts.append(text(bx + 75, 348, b_ctz, size=10, color="#1d4ed8"))
        parts.append(text(bx + 75, 368, b_ptrs, size=9, color="#475569"))

    render(os.path.join(OUT, "littlefs-metadata-ctz.svg"), W, H, "\n".join(parts))


# ─────────────────────────────────────────────────────────────────────────────
# 5. Дворівнева архітектура UBIFS та UBI
# ─────────────────────────────────────────────────────────────────────────────
def fig_ubifs_ubi_architecture():
    W, H = 840, 450
    parts = []

    parts.append(rect(15, 15, 810, 420, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(420, 45, "Архітектура стеку UBIFS / UBI у вбудованому Linux", size=16, color=INK, bold=True))

    y_start = 75
    box_w = 750
    box_x = 45

    # 1. Рівень VFS / Додатків
    parts.append(rect(box_x, y_start, box_w, 48, fill="#e2e8f0", stroke="#64748b", sw=1.2, rx=4))
    parts.append(text(420, y_start + 22, "Рівень POSIX VFS / Системні виклики (open, write, fsync, readdir)", size=12, color="#0f172a", bold=True))
    parts.append(text(420, y_start + 38, "Стандартний файловий інтерфейс ядра Linux для додатків", size=10, color="#475569"))

    # 2. Рівень UBIFS
    y_ubifs = y_start + 60
    parts.append(rect(box_x, y_ubifs, box_w, 105, fill="#dcfce7", stroke="#16a34a", sw=1.5, rx=6))
    parts.append(text(420, y_ubifs + 24, "Рівень UBIFS (UBI File System)", size=13, color="#14532d", bold=True))
    parts.append(text(420, y_ubifs + 44, "Працює поверх логічних блоків стирання (LEB). Не сканує весь чип при монтуванні (O(1) mount time)", size=10, color="#166534"))

    parts.append(rect(box_x + 20, y_ubifs + 55, 220, 40, fill="#f0fdf4", stroke="#22c55e", sw=1, rx=4))
    parts.append(text(box_x + 130, y_ubifs + 79, "TNC (Індексне B-дерево в RAM)", size=10, color="#15803d", bold=True))

    parts.append(rect(box_x + 260, y_ubifs + 55, 220, 40, fill="#f0fdf4", stroke="#22c55e", sw=1, rx=4))
    parts.append(text(box_x + 370, y_ubifs + 79, "Журнал змін (Journal / Log)", size=10, color="#15803d", bold=True))

    parts.append(rect(box_x + 500, y_ubifs + 55, 220, 40, fill="#f0fdf4", stroke="#22c55e", sw=1, rx=4))
    parts.append(text(box_x + 610, y_ubifs + 79, "LPT (Таблиця властивостей LEB)", size=10, color="#15803d", bold=True))

    # 3. Рівень UBI
    y_ubi = y_ubifs + 118
    parts.append(rect(box_x, y_ubi, box_w, 98, fill="#eff6ff", stroke="#2563eb", sw=1.5, rx=6))
    parts.append(text(420, y_ubi + 24, "Рівень UBI (Unsorted Block Images)", size=13, color="#1e3a8a", bold=True))
    parts.append(text(420, y_ubi + 44, "Трансляція LEB → PEB, управління збійними блоками, статичний та динамічний Wear Leveling", size=10, color="#1e40af"))

    parts.append(rect(box_x + 20, y_ubi + 55, 340, 32, fill="#dbeafe", stroke="#3b82f6", sw=1, rx=4))
    parts.append(text(box_x + 190, y_ubi + 75, "Erase Counters (EC Header у кожному PEB)", size=9, color="#1e40af", bold=True))

    parts.append(rect(box_x + 380, y_ubi + 55, 340, 32, fill="#dbeafe", stroke="#3b82f6", sw=1, rx=4))
    parts.append(text(box_x + 550, y_ubi + 75, "Volume ID + LEB Number (VID Header)", size=9, color="#1e40af", bold=True))

    # 4. Рівень MTD та апаратного NAND
    y_mtd = y_ubi + 110
    parts.append(rect(box_x, y_mtd, box_w, 58, fill="#fee2e2", stroke="#dc2626", sw=1.2, rx=4))
    parts.append(text(420, y_mtd + 22, "Підсистема Linux MTD (Memory Technology Devices) & Контролер NAND", size=11, color="#7f1d1d", bold=True))
    parts.append(text(420, y_mtd + 42, "Фізичні стирання блоків (PEB), запис сторінок, апаратний ECC (BCH / Reed-Solomon)", size=10, color="#991b1b"))

    render(os.path.join(OUT, "ubifs-ubi-architecture.svg"), W, H, "\n".join(parts))


if __name__ == "__main__":
    fig_flash_physics_asymmetry()
    fig_raw_vs_managed_flash()
    fig_log_structured_cow_cycle()
    fig_littlefs_metadata_ctz()
    fig_ubifs_ubi_architecture()
    print("All figures successfully generated in ./img/")
