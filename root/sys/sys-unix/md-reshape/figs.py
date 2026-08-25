# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL  = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
WARM_FILL  = "#fff6e5"
RED_FILL   = "#fdecea"
GREY_FILL  = "#f4f6f8"
PURPLE_FILL = "#f3e8fd"

# ── 1. Проблема перекриття смуг при розширенні ─────────────────────────────
def fig_stripe_overlapping():
    W, H = 1000, 520
    p = []

    p.append(text(250, 45, "Стара розкладка (3 диски, 2 блоки даних + 1 P)", size=14, bold=True))
    p.append(text(750, 45, "Нова розкладка (4 диски, 3 блоки даних + 1 P)", size=14, bold=True))

    # Стара сітка (3 диски, 3 смуги)
    disks3 = ["Диск 0", "Диск 1", "Диск 2"]
    col3_w = 90
    col3_x = [115 + i * (col3_w + 10) for i in range(3)]
    for x, d in zip(col3_x, disks3):
        p.append(text(x + col3_w / 2, 75, d, size=12, bold=True, color=MUTED))

    # Смуги старої розкладки:
    # смуга 0: D0, D1, P0
    # смуга 1: D2, P1, D3
    # смуга 2: P2, D4, D5
    old_grid = [
        [("D0", BLUE_FILL), ("D1", BLUE_FILL), ("P0", WARM_FILL)],
        [("D2", RED_FILL),  ("P1", WARM_FILL), ("D3", BLUE_FILL)],
        [("D4", BLUE_FILL), ("P2", WARM_FILL), ("D5", BLUE_FILL)],
    ]
    row_h = 45
    for r, row in enumerate(old_grid):
        y = 90 + r * (row_h + 10)
        p.append(text(50, y + row_h / 2 + 4, "Смуга %d" % r, size=12, bold=True, anchor="start", color=MUTED))
        for x, (lbl, fill) in zip(col3_x, row):
            p.append(fitbox(x, y, col3_w, row_h, [lbl], size=14, pad=6, fill=fill, stroke=LINE, sw=1.4, bold=True))

    # Нова сітка (4 диски, 2 смуги)
    disks4 = ["Диск 0", "Диск 1", "Диск 2", "Диск 3 (новий)"]
    col4_w = 90
    col4_x = [580 + i * (col4_w + 10) for i in range(4)]
    for x, d in zip(col4_x, disks4):
        p.append(text(x + col4_w / 2, 75, d, size=11, bold=True, color=MUTED))

    # Смуги нової розкладки:
    # нова смуга 0: D0, D1, D2, P0'
    # нова смуга 1: D3, D4, D5, P1'
    new_grid = [
        [("D0", BLUE_FILL), ("D1", BLUE_FILL), ("D2", RED_FILL),  ("P0'", WARM_FILL)],
        [("D3", BLUE_FILL), ("D4", BLUE_FILL), ("P1'", WARM_FILL), ("D5", BLUE_FILL)],
    ]
    for r, row in enumerate(new_grid):
        y = 90 + r * (row_h + 10)
        p.append(text(500, y + row_h / 2 + 4, "Нова %d" % r, size=12, bold=True, anchor="start", color=MUTED))
        for x, (lbl, fill) in zip(col4_x, row):
            p.append(fitbox(x, y, col4_w, row_h, [lbl], size=14, pad=6, fill=fill, stroke=LINE, sw=1.4, bold=True))

    # Пояснення колізії (стрілка між старим D2 і новим записом)
    p.append(arrow(365, 168, 570, 112, color=POS, sw=2.0))
    
    # Інформаційні блоки внизу
    b1_y = 270
    p.append(fitbox(50, b1_y, 420, 110,
                    "КОЛІЗІЯ ПЕРЕЗАПИСУ (Stripe Overwrite):\n"
                    "• Нова смуга 0 вимагає блоків D0, D1 і D2.\n"
                    "• Блок D2 у старій геометрії лежить у смузі 1 на Диску 0.\n"
                    "• Якщо писати нову смугу 0 на початок дисків, вона\n"
                    "  затирає сектори старої смуги 0 до зчитування всіх даних!",
                    size=12, pad=10, fill=RED_FILL, stroke=POS, sw=1.5, bold=False))

    p.append(fitbox(510, b1_y, 440, 110,
                    "ДВА СПОСОБИ БЕЗПЕЧНОГО РОЗВ'ЯЗАННЯ:\n"
                    "1. Зворотний хід (Backward Reshape):\n"
                    "   Перебудова йде з кінця масиву до початку (max → 0).\n"
                    "2. Зсув простору даних (Data Offset Shifting):\n"
                    "   Нова геометрія пишеться у вільний проміжок перед даними.",
                    size=12, pad=10, fill=GREEN_FILL, stroke=FIELD, sw=1.5, bold=False))

    # Нижній висновок
    p.append(fitbox(50, 400, 900, 80,
                    "Головне правило: якщо нова смуга ширша за стару, читання і запис конкурують за ті самі фізичні сектори.\n"
                    "Ядро обирає напрямок перебудови (forwards/backwards) або використовує резервний файл (--backup-file),\n"
                    "щоб жоден блок старої смуги не був затертий до того, як його вичитано й зафіксовано в новій структурі.",
                    size=12, pad=10, fill=GREY_FILL, stroke=LINE, sw=1.2))

    render(os.path.join(IMG, 'stripe-overlapping.svg'), W, H, *p)


# ── 2. Межа перебудови (reshape_position) та I/O ───────────────────────────
def fig_reshape_frontier():
    W, H = 1000, 480
    p = []

    p.append(text(W / 2, 40, "Межа перебудови (reshape_position) та маршрутизація активного вводу/виводу", size=15, bold=True))

    # Загальна смуга адресного простору
    bar_y = 110
    bar_h = 70
    
    # Зона 1: Вже перебудовано (ліворуч)
    p.append(fitbox(60, bar_y, 380, bar_h,
                    "ЗОНА НОВОЇ РОЗКЛАДКИ\n"
                    "(Сектори 0 .. reshape_position − 1)\n"
                    "Геометрія: new_level, new_layout, new_chunk, new_disks",
                    size=12, pad=8, fill=GREEN_FILL, stroke=FIELD, sw=1.5, bold=False))

    # Зона 2: Вікно блокування (посередині)
    p.append(fitbox(450, bar_y, 140, bar_h,
                    "КРИТИЧНА ЗОНА\n"
                    "[suspend_lo ..\n"
                    ".. suspend_hi]",
                    size=11, pad=6, fill=RED_FILL, stroke=POS, sw=2.0, bold=True))

    # Зона 3: Ще стара розкладка (праворуч)
    p.append(fitbox(600, bar_y, 340, bar_h,
                    "ЗОНА СТАРОЇ РОЗКЛАДКИ\n"
                    "(Сектори reshape_position .. кінець)\n"
                    "Геометрія: level, layout, chunksize, raid_disks",
                    size=12, pad=8, fill=BLUE_FILL, stroke=NEG, sw=1.5, bold=False))

    # Маркер межі reshape_position
    p.append(arrow(520, 70, 520, 105, color=POS, sw=2.5))
    p.append(text(520, 62, "reshape_position", size=12, bold=True, color=POS))

    # Стрілка напрямку перебудови
    p.append(arrow(470, 195, 570, 195, color=LINE, sw=2.0))
    p.append(text(520, 215, "Напрямок ходу (forwards)", size=11, bold=True, color=MUTED))

    # Маршрутизація I/O запитів (нижня частина)
    card_y = 250
    card_h = 180

    p.append(fitbox(60, card_y, 270, card_h,
                    "ВХІДНИЙ ЗАПИТ < reshape_pos\n\n"
                    "1. Запит bio потрапляє у вже змінену зону.\n"
                    "2. Драйвер md транслює адресу за НОВОЮ формулою:\n"
                    "   новий chunk, нова кількість дисків, новий offset.\n"
                    "3. Виконується негайно без очікування.",
                    size=11, pad=10, fill=GREEN_FILL, stroke=FIELD, sw=1.4))

    p.append(fitbox(365, card_y, 270, card_h,
                    "ЗАПИТ ПОТРАПЛЯЄ В [lo .. hi]\n\n"
                    "1. Адреса збігається з поточною смугою перебудови.\n"
                    "2. Потік запиту ПРИЗУПИНЯЄТЬСЯ (блокується на черзі suspend_lo/hi).\n"
                    "3. Reshape-потік записує смугу й просуває межу.\n"
                    "4. Запит розблоковується та йде за новою розкладкою.",
                    size=11, pad=10, fill=RED_FILL, stroke=POS, sw=1.5))

    p.append(fitbox(670, card_y, 270, card_h,
                    "ВХІДНИЙ ЗАПИТ ≥ reshape_pos\n\n"
                    "1. Запит bio потрапляє в зону, яку ще не рухали.\n"
                    "2. Драйвер md транслює адресу за СТАРОЮ формулою:\n"
                    "   старий chunk, старі диски, стара парність.\n"
                    "3. Виконується негайно без затримок.",
                    size=11, pad=10, fill=BLUE_FILL, stroke=NEG, sw=1.4))

    render(os.path.join(IMG, 'reshape-frontier.svg'), W, H, *p)


# ── 3. Протокол резервного файлу (--backup-file) ───────────────────────────
def fig_backup_file_flow():
    W, H = 1000, 530
    p = []

    p.append(text(W / 2, 38, "Протокол захисту критичної смуги через резервний файл (--backup-file)", size=15, bold=True))

    steps = [
        ("1. Блокування I/O", "mddev->suspend_lo/hi\nзаморожує доступ\nдо вікна смуги", BLUE_FILL),
        ("2. Зчитування даних", "Зчитування критичних\nсмуг із дисків\nмасиву в RAM", BLUE_FILL),
        ("3. Запис у backup", "Збереження копії\nу файл + виклик\nfsync() на носій", WARM_FILL),
        ("4. Фіксація стану", "Запис reshape_position\nі прапорця в суперблок\nна дисках", WARM_FILL),
        ("5. Нова розкладка", "Обчислення нової\nпарності й запис нової\nсмуги на диски", GREEN_FILL),
        ("6. Зняття замка", "Просування suspend,\nрозмороження черги\nвводу/виводу", GREEN_FILL),
    ]

    col_w = 135
    gap = 18
    start_x = 50
    y_top = 75
    h_box = 105

    for i, (stitle, sdesc, sfill) in enumerate(steps):
        x = start_x + i * (col_w + gap)
        p.append(fitbox(x, y_top, col_w, h_box, "%s\n\n%s" % (stitle, sdesc), size=10, pad=6, fill=sfill, stroke=LINE, sw=1.4, bold=False))
        if i < len(steps) - 1:
            p.append(arrow(x + col_w + 2, y_top + h_box / 2, x + col_w + gap - 2, y_top + h_box / 2, color=LINE, sw=1.8))

    # Стрілка збою вниз
    p.append(arrow(435, y_top + h_box + 4, 435, 235, color=POS, sw=2.0))
    p.append(textbox(575, 210, "Збій живлення / аварія посеред запису", size=11, bold=True, color=POS, fill=RED_FILL, stroke=POS, sw=1.2)[0])

    # Блок відновлення
    rec_y = 245
    p.append(fitbox(50, rec_y, 900, 115,
                    "ВІДНОВЛЕННЯ ПІСЛЯ АВАРІЇ (CRASH RECOVERY):\n\n"
                    "1. При збиранні масиву: mdadm --assemble --backup-file=/path/to/backup /dev/md0 /dev/sd[a-d]1\n"
                    "2. Утиліта mdadm виявляє активний біт MD_FEATURE_RESHAPE_ACTIVE у суперблоці.\n"
                    "3. Зчитує збережені оригінальні блоки з backup-file і відновлює пошкоджену смугу на дисках масиву.\n"
                    "4. Ядро відновлює стан reshape_position і безпечно продовжує перебудову далі.",
                    size=11, pad=10, fill=RED_FILL, stroke=POS, sw=1.5))

    # Альтернатива (зсув data_offset)
    alt_y = 380
    p.append(fitbox(50, alt_y, 900, 115,
                    "АЛЬТЕРНАТИВА В МЕТАДАНИХ 1.1 ТА 1.2 — ЗСУВ ПРОСТОРУ ДАНИХ (DATA OFFSET SHIFTING):\n\n"
                    "Якщо суперблок має запас зміщення на початку розділу (data_offset: 2048 → 4096 секторів), нова смуга пишеться\n"
                    "у фізично вільне місце на диску. Стара смуга взагалі не перетирається in-place, тому окремий зовнішній\n"
                    "резервний файл не потрібен — захист від краху гарантується самою структурою простору на носії.",
                    size=11, pad=10, fill=PURPLE_FILL, stroke="#7e57c2", sw=1.4))

    render(os.path.join(IMG, 'backup-file-flow.svg'), W, H, *p)


# ── 4. Міграція рівнів масиву ──────────────────────────────────────────────
def fig_level_migration():
    W, H = 1000, 500
    p = []

    p.append(text(W / 2, 35, "Еволюція рівнів масиву без зупинки роботи: RAID1 → RAID5 → RAID6", size=15, bold=True))

    card_w = 270
    card_h = 320
    card_y = 70

    # Етап 1: RAID1 -> RAID5 (2 диски)
    p.append(fitbox(50, card_y, card_w, card_h,
                    "ЕТАП 1: RAID1 → RAID5\n(2 накопичувачі)\n\n"
                    "Команда:\nmdadm --grow /dev/md0 --level=5\n\n"
                    "• Дзеркало RAID1 перетворюється\n  на RAID5 із двох дисків.\n"
                    "• У 2-дисковому RAID5 один диск\n  містить дані (D), другий —\n  парність (P=D).\n"
                    "• Структура даних не змінюється,\n  масив готовий до додавання дисків.",
                    size=11, pad=10, fill=BLUE_FILL, stroke=NEG, sw=1.4))

    p.append(arrow(326, card_y + card_h / 2, 358, card_y + card_h / 2, color=LINE, sw=2.2))

    # Етап 2: Розширення RAID5 (3 диски)
    p.append(fitbox(365, card_y, card_w, card_h,
                    "ЕТАП 2: РОЗШИРЕННЯ RAID5\n(Додавання 3-го диска)\n\n"
                    "Команди:\nmdadm --add /dev/md0 /dev/sdc1\nmdadm --grow /dev/md0 \\\n  --raid-devices=3\n\n"
                    "• reshape перерозподіляє блоки:\n  парність P обертається по 3 дисках.\n"
                    "• Корисна ємність масиву зростає\n  вдвічі (з 1×Size до 2×Size) наживо!\n"
                    "• Ввід/вивід не зупиняється.",
                    size=11, pad=10, fill=GREEN_FILL, stroke=FIELD, sw=1.5))

    p.append(arrow(641, card_y + card_h / 2, 673, card_y + card_h / 2, color=LINE, sw=2.2))

    # Етап 3: RAID5 -> RAID6 (4 диски)
    p.append(fitbox(680, card_y, card_w, card_h,
                    "ЕТАП 3: RAID5 → RAID6\n(Додавання другого захисту Q)\n\n"
                    "Команди:\nmdadm --add /dev/md0 /dev/sdd1\nmdadm --grow /dev/md0 \\\n  --level=6 --raid-devices=4\n\n"
                    "• До кожної смуги обчислюється\n  другий синдром Q (GF(2⁸)).\n"
                    "• Розкладка переходить на 2 блоки\n  парності (P + Q) на смугу.\n"
                    "• Масив витримує одночасну відмову\n  двох будь-яких дисків.",
                    size=11, pad=10, fill=PURPLE_FILL, stroke="#7e57c2", sw=1.4))

    # Нижня плашка
    p.append(fitbox(50, 410, 900, 65,
                    "Усі перетворення виконуються прозоро для файлової системи зверху (ext4, XFS).\n"
                    "Після завершення перебудови файлову систему розширюють командою resize2fs або xfs_growfs.",
                    size=11, pad=10, fill=GREY_FILL, stroke=LINE, sw=1.2))

    render(os.path.join(IMG, 'level-migration.svg'), W, H, *p)


if __name__ == '__main__':
    fig_stripe_overlapping()
    fig_reshape_frontier()
    fig_backup_file_flow()
    fig_level_migration()
    print("All figures generated successfully.")
