# -*- coding: utf-8 -*-
"""Фігури теми «Патерни кешування». Вивід — ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)

GREEN_F = "#d4edda"
RED_F   = "#fdecea"
BLUE_F  = "#eaf0fd"
GRAY_F  = "#f4f6f8"


# ── 1. read-topologies: Cache-Aside проти Read-Through ───────────────────────
def fig_read_topologies():
    W, H = 1000, 480
    f = []

    # Розділювач ліворуч / праворуч
    f.append(line(500, 50, 500, 450, color=MUTED, sw=1, dash="4,4"))

    # ЛІВА СТОРОНА: Cache-Aside (Оркестрація застосунком)
    f.append(text(250, 60, "Cache-Aside (кешування збоку)", size=16, bold=True))
    f.append(text(250, 82, "Застосунок сам керує і кешем, і базою", size=12, color=MUTED))

    # Вузли ліворуч
    f.append(fitbox(170, 110, 160, 46, "Застосунок", size=14, bold=True, fill=BLUE_F, stroke=NEG))
    f.append(fitbox(50, 240, 150, 50, "Кеш (Redis / RAM)\n1. перевірка / 3. запис", size=12, fill=GREEN_F, stroke=FIELD))
    f.append(fitbox(300, 240, 150, 50, "База даних (SQL)\n2. читання на промах", size=12, fill=GRAY_F, stroke=LINE))

    # Стрілки ліворуч
    f.append(arrow(210, 156, 140, 240, color=FIELD, sw=1.8))
    f.append(text(140, 185, "1. get(key)", size=11, color=FIELD, bold=True, anchor="end"))

    f.append(arrow(290, 156, 360, 240, color=INK, sw=1.8))
    f.append(text(355, 185, "2. SELECT (промах)", size=11, color=INK, bold=True, anchor="start"))

    f.append(arrow(250, 156, 175, 240, color=FIELD, sw=1.8))
    f.append(text(240, 215, "3. set(key, val)", size=11, color=FIELD, bold=True, anchor="middle"))

    f.append(fitbox(50, 340, 400, 90,
                    "Порядок читання:\n"
                    "1. Застосунок питає кеш: є → повертає значення (влучання).\n"
                    "2. Немає (промах) → застосунок іде в базу даних.\n"
                    "3. Застосунок сам записує результат у кеш із TTL.",
                    size=12, pad=10, fill=FILL, stroke=MUTED))

    # ПРАВА СТОРОНА: Read-Through (Наскрізний кеш)
    f.append(text(750, 60, "Read-Through (наскрізне читання)", size=16, bold=True))
    f.append(text(750, 82, "Кеш стоїть проксі між кодом і сховищем", size=12, color=MUTED))

    # Вузли праворуч
    f.append(fitbox(670, 110, 160, 46, "Застосунок", size=14, bold=True, fill=BLUE_F, stroke=NEG))
    f.append(fitbox(670, 210, 160, 50, "Кеш (Проксі / Бібліотека)\nАвтозавантажувач", size=12, bold=True, fill=GREEN_F, stroke=FIELD))
    f.append(fitbox(670, 310, 160, 50, "База даних (SQL)\nПершоджерело", size=12, fill=GRAY_F, stroke=LINE))

    # Стрілки праворуч
    f.append(arrow(750, 156, 750, 210, color=FIELD, sw=1.8))
    f.append(text(760, 185, "1. get(key)", size=11, color=FIELD, bold=True, anchor="start"))

    f.append(arrow(750, 260, 750, 310, color=INK, sw=1.8))
    f.append(text(760, 285, "2. fetch on miss", size=11, color=INK, bold=True, anchor="start"))

    f.append(fitbox(550, 380, 400, 75,
                    "Порядок читання:\n"
                    "1. Застосунок завжди звертається лише до кешу.\n"
                    "2. На промах кеш сам прозоро вантажить дані з бази,\n"
                    "   зберігає в себе та віддає застосунку.",
                    size=12, pad=10, fill=FILL, stroke=MUTED))

    render(out("read-topologies.svg"), W, H, *f,
           title="Топології читання: оркестрація застосунком (Cache-Aside) проти наскрізного проксі (Read-Through)")


# ── 2. write-topologies: Write-Through, Write-Behind, Write-Around ───────────
def fig_write_topologies():
    W, H = 1060, 400
    f = []

    # Колонка 1: Write-Through
    f.append(fitbox(30, 60, 310, 40, "1. Write-Through (наскрізний)", size=14, bold=True, fill=BLUE_F, stroke=NEG))
    f.append(fitbox(105, 120, 160, 40, "Застосунок", size=13, bold=True))
    f.append(fitbox(105, 195, 160, 44, "Кеш", size=13, fill=GREEN_F, stroke=FIELD, bold=True))
    f.append(fitbox(105, 270, 160, 44, "База даних", size=13, fill=GRAY_F, stroke=LINE))

    f.append(arrow(185, 160, 185, 195, color=FIELD, sw=1.8))
    f.append(text(195, 180, "запис", size=11, color=FIELD, bold=True, anchor="start"))
    f.append(arrow(185, 239, 185, 270, color=INK, sw=1.8))
    f.append(text(195, 256, "синхронно", size=11, color=INK, bold=True, anchor="start"))

    f.append(fitbox(30, 330, 310, 55, "Синхронний запис в обидва сховища.\nСтрога узгодженість, вища затримка запису.", size=11, fill=FILL, stroke=MUTED))

    # Колонка 2: Write-Behind
    f.append(fitbox(375, 60, 310, 40, "2. Write-Behind (відкладений)", size=14, bold=True, fill=GREEN_F, stroke=FIELD))
    f.append(fitbox(450, 120, 160, 40, "Застосунок", size=13, bold=True))
    f.append(fitbox(450, 195, 160, 44, "Кеш + Черга/WAL", size=13, fill=GREEN_F, stroke=FIELD, bold=True))
    f.append(fitbox(450, 270, 160, 44, "База даних", size=13, fill=GRAY_F, stroke=LINE))

    f.append(arrow(530, 160, 530, 195, color=FIELD, sw=1.8))
    f.append(text(540, 180, "швидкий ACK", size=11, color=FIELD, bold=True, anchor="start"))
    f.append(arrow(530, 239, 530, 270, color=POS, sw=1.8))
    f.append(text(540, 256, "асинхронно / пачка", size=11, color=POS, bold=True, anchor="start"))

    f.append(fitbox(375, 330, 310, 55, "Запис у пам'ять, асинхронний злив у базу.\nМінімальна затримка, ризик втрати даних при збої.", size=11, fill=FILL, stroke=MUTED))

    # Колонка 3: Write-Around
    f.append(fitbox(720, 60, 310, 40, "3. Write-Around (в обхід)", size=14, bold=True, fill=GRAY_F, stroke=LINE))
    f.append(fitbox(795, 120, 160, 40, "Застосунок", size=13, bold=True))
    f.append(fitbox(730, 210, 120, 44, "Кеш\n(інвалідація)", size=11, fill=RED_F, stroke=POS, bold=True))
    f.append(fitbox(880, 210, 120, 44, "База даних\n(запис)", size=11, fill=GRAY_F, stroke=LINE, bold=True))

    f.append(arrow(835, 160, 790, 210, color=POS, sw=1.8))
    f.append(text(765, 180, "DEL key", size=11, color=POS, bold=True, anchor="end"))
    f.append(arrow(915, 160, 940, 210, color=INK, sw=1.8))
    f.append(text(950, 180, "UPDATE", size=11, color=INK, bold=True, anchor="start"))

    f.append(fitbox(720, 330, 310, 55, "Прямий запис у базу, кеш скидається (delete).\nНе засмічує RAM даними без наступних читань.", size=11, fill=FILL, stroke=MUTED))

    render(out("write-topologies.svg"), W, H, *f,
           title="Стратегії запису: синхронний наскрізний, асинхронний відкладений та запис в обхід")


# ── 3. dual-write-race: Чому оновлення кешу програє інвалідації ───────────────
def fig_dual_write_race():
    W, H = 1000, 450
    f = []

    # Розділювач
    f.append(line(500, 50, 500, 430, color=MUTED, sw=1, dash="4,4"))

    # ЛІВА СТОРОНА: Гонка оновлення (Update on write) -> РОЗХОДЖЕННЯ
    f.append(text(250, 60, "Помилка: оновлення кешу при записі", size=15, bold=True, color=POS))
    f.append(text(250, 80, "Два паралельні клієнти 1 і 2", size=12, color=MUTED))

    # Схема кроків ліворуч
    steps_left = [
        "1. Клієнт 1 пише в БД: v = 1",
        "2. Клієнт 2 пише в БД: v = 2",
        "3. Клієнт 2 оновлює кеш: set(v = 2)",
        "4. Клієнт 1 запізнився мережею: set(v = 1)"
    ]
    for i, st in enumerate(steps_left):
        y = 115 + i * 45
        f.append(fitbox(60, y, 380, 36, st, size=12, fill=FILL, stroke=LINE))

    f.append(fitbox(60, 310, 380, 100,
                    "Результат гонки:\n"
                    "• У базі даних лишилося: v = 2 (свіже)\n"
                    "• У кеші записалося: v = 1 (застаріле!)\n"
                    "✖ Кеш перманентно розсинхронізовано з базою!",
                    size=12, fill=RED_F, stroke=POS, color=POS, bold=True))

    # ПРАВА СТОРОНА: Інвалідація (Delete on write) -> БЕЗПЕКА
    f.append(text(750, 60, "Правильно: інвалідація (видалення)", size=15, bold=True, color=FIELD))
    f.append(text(750, 80, "Скидання ключа на будь-який запис", size=12, color=MUTED))

    steps_right = [
        "1. Клієнт 1 пише в БД: v = 1",
        "2. Клієнт 2 пише в БД: v = 2",
        "3. Клієнт 2 видаляє ключ: del(key)",
        "4. Клієнт 1 видаляє ключ: del(key)"
    ]
    for i, st in enumerate(steps_right):
        y = 115 + i * 45
        f.append(fitbox(560, y, 380, 36, st, size=12, fill=FILL, stroke=LINE))

    f.append(fitbox(560, 310, 380, 100,
                    "Результат інвалідації:\n"
                    "• У базі даних: v = 2 (свіже)\n"
                    "• У кеші: ключа немає (промах)\n"
                    "✓ Наступне читання прочитає з БД свіже v = 2\n"
                    "   і прогріє кеш без будь-якої розсинхронізації!",
                    size=12, fill=GREEN_F, stroke=FIELD, color=FIELD, bold=True))

    render(out("dual-write-race.svg"), W, H, *f,
           title="Гонка паралельних записів: чому інвалідація (delete) надійна, а пряме оновлення (set) веде до розсинхронізації")


if __name__ == "__main__":
    fig_read_topologies()
    fig_write_topologies()
    fig_dual_write_race()
    print("All figures generated successfully.")
