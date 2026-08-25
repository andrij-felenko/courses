# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT  = "#fbfcff"
WARM  = "#fdf3e7"
COOL  = "#eaf0fd"
GREEN = "#eafaf0"
GREY  = "#f1f2f4"
ALERT = "#fdecea"


# ── 1. Архітектура dm-cache ──────────────────────────────────────────────────
def fig_dm_cache_arch():
    W, H = 1100, 620
    p = []

    p.append(text(W / 2, 40, "Архітектура трикомпонентного блокового кешу dm-cache", size=16, bold=True, color=INK))

    # Верхній шар: Віртуальний блоковий пристрій
    p.append(fitbox(W / 2 - 250, 75, 500, 56, "Віртуальний пристрій /dev/mapper/cached-vol\n(VFS / Файлова система / БД)", size=13, fill=COOL, stroke=NEG))

    p.append(arrow(W / 2, 131, W / 2, 175, color=INK, sw=2))

    # Середній шар: dm-cache target & SMQ engine
    p.append(rect(150, 180, 800, 160, fill=SOFT, stroke=LINE, sw=1.8, rx=8))
    p.append(text(W / 2, 205, "Драйвер dm-cache (Device Mapper Target)", size=14, bold=True, color=INK))

    p.append(fitbox(180, 230, 340, 90, "Політика SMQ (Stochastic Multiqueue)\n• Облік популярності чанків (promotions)\n• Витіснення найменш вживаних (demotions)", size=11.5, fill=WARM, stroke="#e67e22"))
    p.append(fitbox(580, 230, 340, 90, "Диспетчер вводу-виводу\n• Перенаправлення читань/записів\n• Відстеження брудних блоків (dirty ratio)", size=11.5, fill=GREEN, stroke=FIELD))

    # Нижній шар: три компоненти (Origin, Cache Data, Cache Metadata)
    p.append(arrow(300, 340, 250, 420, color=LINE, sw=1.8))
    p.append(fitbox(70, 420, 360, 120, "Оригінальний пристрій (Origin)\n/dev/sdb (HDD / RAID)\n• Велика ємність (терабайти)\n• Повільний довільний доступ", size=12, fill=GREY, stroke=LINE))

    p.append(arrow(W / 2, 340, W / 2, 420, color=NEG, sw=2))
    p.append(fitbox(370, 420, 360, 120, "Пристрій даних кешу (Cache Data)\n/dev/nvme0n1p2 (NVMe / SSD)\n• Гарячі чанки (32 КіБ .. 1 ГіБ)\n• Висока швидкість IOPS", size=12, fill=GREEN, stroke=FIELD))

    p.append(arrow(800, 340, 850, 420, color=POS, sw=1.8))
    p.append(fitbox(670, 420, 360, 120, "Пристрій метаданих (Metadata)\n/dev/nvme0n1p1 (SSD / PMEM)\n• Карта відповідності чанків\n• Транзакційний суперблок", size=12, fill=WARM, stroke=POS))

    # Зв'язок скидання (flush) між Cache Data та Origin HDD
    p.append(arrow(370, 480, 430, 480, color=POS, sw=1.6))
    p.append(mtext(400, 510, "фоновий flush брудних блоків", size=10.5, color=POS, anchor="middle"))

    render(os.path.join(OUT, "dm-cache-arch.svg"), W, H, *p,
           title="Компоненти та структура dm-cache")


# ── 2. Архітектура dm-writecache ─────────────────────────────────────────────
def fig_dm_writecache_ring():
    W, H = 1100, 580
    p = []

    p.append(text(W / 2, 40, "Архітектура та журнал записів dm-writecache", size=16, bold=True, color=INK))

    p.append(fitbox(W / 2 - 250, 75, 500, 54, "Запит запису від додатка (write / pwrite)", size=13, bold=True, fill=COOL, stroke=NEG))

    p.append(arrow(W / 2, 129, W / 2, 165, color=INK, sw=2))

    # Драйвер dm-writecache
    p.append(rect(150, 165, 800, 100, fill=SOFT, stroke=LINE, sw=1.8, rx=8))
    p.append(text(W / 2, 190, "Драйвер dm-writecache (NVMe / PMEM DAX direct log)", size=14, bold=True, color=INK))
    p.append(text(W / 2, 215, "Миттєвий запис у швидкий журнал → підтвердження успіху додатку", size=12, color=FIELD))

    # Журнал кешу
    p.append(arrow(W / 2, 265, W / 2, 310, color=NEG, sw=2))

    p.append(rect(100, 310, 900, 110, fill=ALERT, stroke=POS, sw=1.8, rx=6))
    p.append(text(W / 2, 335, "Журнал записів на PMEM / NVMe (/dev/nvme0n1)", size=13, bold=True, color=POS))

    # Блоки журналу
    p.append(fitbox(130, 350, 160, 55, "Суперблок і\nмасив метаданих", size=11, fill=WARM, stroke=POS))
    p.append(fitbox(310, 350, 160, 55, "Брудний блок #1\n(4096 байтів)", size=11, fill=GREEN, stroke=FIELD))
    p.append(fitbox(490, 350, 160, 55, "Брудний блок #2\n(4096 байтів)", size=11, fill=GREEN, stroke=FIELD))
    p.append(fitbox(670, 350, 160, 55, "Брудний блок #3\n(4096 байтів)", size=11, fill=GREEN, stroke=FIELD))
    p.append(fitbox(850, 350, 130, 55, "Вільний\nпростір", size=11, fill=GREY, stroke=LINE))

    # Фоновий скидач на Origin
    p.append(arrow(570, 420, 570, 480, color=POS, sw=2))
    p.append(fitbox(300, 480, 540, 65, "Послідовне скидання (Sequential Flusher)\nСортування та злиття брудних блоків → Послідовний запис на Origin HDD", size=12, fill=GREY, stroke=LINE))

    render(os.path.join(OUT, "dm-writecache-ring.svg"), W, H, *p,
           title="Журнал записів та послідовне скидання dm-writecache")


# ── 3. Порівняння режимів кешування ──────────────────────────────────────────
def fig_cache_modes_comparison():
    W, H = 1200, 640
    p = []

    p.append(text(W / 2, 40, "Шляхи обробки запису: Writeback, Writethrough та Passthrough", size=16, bold=True, color=INK))

    BW, BH = 340, 500
    xs = [60, 430, 800]

    modes = [
        ("Режим Writeback", "Максимальна швидкість запису", ALERT, POS, [
            (90, "1. Додаток робить write()"),
            (160, "2. Запис у SSD кеш"),
            (230, "3. Повернення успіху в VFS"),
            (330, "4. Фоновий flush брудних\nблоків на Origin HDD"),
            (430, "Ризик: втрата брудних блоків\nпри аварії SSD")
        ]),
        ("Режим Writethrough", "Надійність і прискорення читань", COOL, NEG, [
            (90, "1. Додаток робить write()"),
            (160, "2. Паралельний запис у\nSSD кеш ТА Origin HDD"),
            (260, "3. Чекаємо завершення\nобох пристроїв"),
            (330, "4. Повернення успіху в VFS"),
            (430, "Надійність: HDD завжди\nмістить актуальні дані")
        ]),
        ("Режим Passthrough", "Обхід кешу (байпас)", GREY, LINE, [
            (90, "1. Додаток робить write()"),
            (170, "2. Прямий запис на Origin HDD\n(кеш оминається)"),
            (270, "3. Інвалідація застарілих\nблоків у SSD кеші"),
            (350, "4. Повернення успіху в VFS"),
            (430, "Використання: масовий бекап,\nщоб не вимивати кеш")
        ]),
    ]

    for x, (title, sub, bg, accent, steps) in zip(xs, modes):
        p.append(rect(x, 80, BW, BH, fill=bg, stroke=accent, sw=1.8, rx=8))
        p.append(text(x + BW / 2, 108, title, size=15, bold=True, color=INK))
        p.append(text(x + BW / 2, 128, sub, size=11, color=MUTED))
        p.append(line(x + 20, 140, x + BW - 20, 140, color=accent, sw=1.2))

        for (y, label) in steps:
            p.append(fitbox(x + 20, 80 + y, BW - 40, 50, label, size=11.5, fill=BG, stroke=accent, sw=1.2))

    render(os.path.join(OUT, "cache-modes-comparison.svg"), W, H, *p,
           title="Порівняння режимів роботи кешу на блоковому рівні")


fig_dm_cache_arch()
fig_dm_writecache_ring()
fig_cache_modes_comparison()
print("готово: фігури згенеровано")
