# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
WARM = "#b8860b"


# ── 1. Втрата метаданих при наївному копіюванні проти збереження ──────────────
def fig_metadata_loss_vs_preserved():
    W, H = 1260, 780
    p = []

    p.append(fitbox(50, 35, 1160, 58,
                    "Наївне копіювання (cp -r) перезаписує атрибути через umask і системні виклики поточного користувача.\n"
                    "Архівний режим (cp -a, rsync -aHAX) повноцінно відтворює стан об'єктів VFS на стороні призначення",
                    size=14, fill=FILL, stroke=LINE, bold=True))

    # Стовпчики
    COL_SRC_X, COL_SRC_W = 50, 340
    COL_NAIVE_X, COL_NAIVE_W = 440, 360
    COL_ACC_X, COL_ACC_W = 850, 360

    p.append(fitbox(COL_SRC_X, 110, COL_SRC_W, 44, "Джерело (Оригінал VFS)", size=14, fill=WARM_FILL, stroke=WARM, bold=True))
    p.append(fitbox(COL_NAIVE_X, 110, COL_NAIVE_W, 44, "Наївне копіювання (cp -r)", size=14, fill=RED_FILL, stroke=POS, bold=True))
    p.append(fitbox(COL_ACC_X, 110, COL_ACC_W, 44, "Точне копіювання (cp -a / rsync -aHAX)", size=14, fill=GREEN_FILL, stroke=FIELD, bold=True))

    rows = [
        ("Мітки часу (mtime, atime):\n2021-04-12 10:00:00",
         "Перезапис на ПОТОЧНИЙ ЧАС\n(ламає кеші, make, бекапи)",
         "Точний час у наносекундах\n(utimensat відтворює mtime/atime)",
         RED_FILL, POS, GREEN_FILL, FIELD),

        ("Права доступу та біти:\nmode 0600 (rw-------) + SUID",
         "Накладання umask (022 → 0644),\nскидання бітів SUID/SGID",
         "Повний збіг mode 0600,\nзбереження бітів SUID/SGID/Sticky",
         RED_FILL, POS, GREEN_FILL, FIELD),

        ("Власник та група:\nUID=1000 (mysql), GID=1000",
         "UID/GID процесу, що копіює\n(mysql втрачає доступ до бази)",
         "Збереження UID/GID 1000:1000\n(fchownat за наявності прав root)",
         RED_FILL, POS, GREEN_FILL, FIELD),

        ("Жорсткі посилання (Hardlinks):\n2 файли → 1 спільний inode",
         "Дублювання: 2 окремі inode,\nподвійна витрата місця на диску",
         "Таблиця (dev,ino) → linkat:\nзбережено 1 inode та 2 посилання",
         RED_FILL, POS, GREEN_FILL, FIELD),

        ("Розріджені файли (Sparse):\n100 ГБ логічно, 5 ГБ на диску",
         "Запис нулів: фізичне роздування\nфайлу до повних 100 ГБ на диску",
         "Детекція дірок (SEEK_HOLE):\nвиділено лише 5 ГБ блоків",
         RED_FILL, POS, GREEN_FILL, FIELD),

        ("Атрибути xattr, ACL, SELinux:\nsystem.posix_acl, security.selinux",
         "Втрачено повністю:\nатрибути ігноруються",
         "Збережено через lsetxattr:\nвсі простори імен xattr, ACL, SELinux",
         RED_FILL, POS, GREEN_FILL, FIELD),
    ]

    y = 168
    RH = 78
    GAP = 12
    for src_text, naive_text, acc_text, n_fill, n_stroke, a_fill, a_stroke in rows:
        p.append(fitbox(COL_SRC_X, y, COL_SRC_W, RH, src_text, size=12, fill=BG, stroke=MUTED))
        p.append(fitbox(COL_NAIVE_X, y, COL_NAIVE_W, RH, naive_text, size=12, fill=n_fill, stroke=n_stroke))
        p.append(fitbox(COL_ACC_X, y, COL_ACC_W, RH, acc_text, size=12, fill=a_fill, stroke=a_stroke))
        y += RH + GAP

    p.append(fitbox(50, 715, 1160, 48,
                    "Головне правило: звичайний read() / write() передає лише потік байтів вмісту, відкидаючи всі метадані вузла VFS",
                    size=13, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'metadata-loss-vs-preserved.svg'), W, H, *p,
           title="Порівняння втрати метаданих при звичайному та точному копіюванні")


# ── 2. Алгоритм дельта-передачі rsync ─────────────────────────────────────────
def fig_rsync_delta_algorithm():
    W, H = 1240, 780
    p = []

    p.append(fitbox(50, 35, 1140, 56,
                    "Алгоритм дельта-передачі rsync: мінімізація мережевого трафіку шляхом порівняння\n"
                    "блокових хешів замість передачі всього файлу цілком",
                    size=14, fill=FILL, stroke=LINE, bold=True))

    # Стовпчики: Отримувач (Receiver) та Відправник (Sender)
    RX_X, RX_W = 50, 480
    TX_X, TX_W = 710, 480

    p.append(fitbox(RX_X, 110, RX_W, 46, "Отримувач (Receiver / Цільовий файл)", size=14, fill=BLUE_FILL, stroke=NEG, bold=True))
    p.append(fitbox(TX_X, 110, TX_W, 46, "Відправник (Sender / Вихідний файл)", size=14, fill=GREEN_FILL, stroke=FIELD, bold=True))

    # Блоки цільового файлу
    p.append(fitbox(RX_X, 175, RX_W, 140,
                    "1. Розбиття наявного файлу на фіксовані блоки (наприклад, 4 КБ):\n"
                    "• Блок 0: Adler-32 (32 біти) + MD5/MD4 (128 бітів)\n"
                    "• Блок 1: Adler-32 (32 біти) + MD5/MD4 (128 бітів)\n"
                    "• Блок 2: Adler-32 (32 біти) + MD5/MD4 (128 бітів)\n"
                    "• ...\n"
                    "Складання компактної таблиці контрольних сум",
                    size=12, fill=BG, stroke=LINE))

    # Передача таблиці хешів від Receiver до Sender
    p.append(arrow(RX_X + RX_W + 10, 245, TX_X - 10, 245, color=NEG))
    p.append(fitbox(545, 215, 150, 60, "Передача таблиці\nхешів блоків\n(мережа / сокет)", size=11, fill=BLUE_FILL, stroke=NEG))

    # Робота Sender
    p.append(fitbox(TX_X, 175, TX_W, 230,
                    "2. Побайтовий пошук збігів у джерелі:\n"
                    "• Обчислення ковзної контрольної суми (Rolling Adler-32)\n"
                    "  для вікна розміром у блок на кожному зміщенні i, i+1, i+2...\n"
                    "• Швидка перевірка: чи є такий Adler-32 у хеш-таблиці?\n"
                    "  – НІ: поточний байт додається до буфера нових даних\n"
                    "  – ТАК: обчислюється сильний хеш MD5 для підтвердження\n"
                    "• При збігу сильного хешу: фіксується тотожний блок,\n"
                    "  вікно пересувається одразу на довжину цілого блоку",
                    size=12, fill=BG, stroke=LINE))

    # Передача інструкцій від Sender до Receiver
    p.append(arrow(TX_X - 10, 450, RX_X + RX_W + 10, 450, color=FIELD))
    p.append(fitbox(545, 420, 150, 60, "Передача дельти:\n[сирі байти] +\n[номери блоків]", size=11, fill=GREEN_FILL, stroke=FIELD))

    # Відновлення на Receiver
    p.append(fitbox(RX_X, 355, RX_W, 200,
                    "3. Реконструкція цільового файлу:\n"
                    "• Створення тимчасового файлу (.filename.XXXXXX)\n"
                    "• Запис нових байтів із потоку відправника\n"
                    "• Пряме копіювання збіглих блоків із наявного локального файлу\n"
                    "• Атомарне перейменування rename() поверх старого файлу\n"
                    "• Застосування прав, xattr, ACL та timestamps (utimensat)",
                    size=12, fill=BG, stroke=LINE))

    p.append(fitbox(50, 580, 1140, 160,
                    "Чому дельта-алгоритм такий швидкий:\n"
                    "• Ковзна сума Adler-32 обчислюється за O(1) операцій на кожен зсув байта (віднімання вибулого байта + додавання нового)\n"
                    "• Важкий криптографічний хеш рахується лише у разі збігу легкого 32-бітного хешу\n"
                    "• При повторній синхронізації 10 ГБ файлу зі зміною в 1 МБ мережею передається лише ~1 МБ даних та кілька кілобайтів хешів",
                    size=13, fill=WARM_FILL, stroke=WARM))

    render(os.path.join(IMG, 'rsync-delta-algorithm.svg'), W, H, *p,
           title="Принцип роботи блочного дельта-алгоритму rsync")


# ── 3. Архітектура трьох конвеєрів копіювання ─────────────────────────────────
def fig_copy_pipelines_architecture():
    W, H = 1260, 760
    p = []

    p.append(fitbox(50, 35, 1160, 56,
                    "Три архітектурні моделі копіювання дерев каталогів у Linux:\n"
                    "локальний CoW у просторі ядра, серіалізація потоку в конвеєрі та синхронізація дельти процесами",
                    size=14, fill=FILL, stroke=LINE, bold=True))

    BX, BW = 50, 360
    CX, CW = 450, 360
    DX, DW = 850, 360

    # 1. cp -a
    p.append(fitbox(BX, 110, BW, 48, "1. cp -a --reflink=auto\n(Локальне пряме VFS)", size=14, fill=GREEN_FILL, stroke=FIELD, bold=True))
    p.append(fitbox(BX, 170, BW, 440,
                    "Простір користувача:\n"
                    "Один процес cp рекурсивно обходить каталог\n"
                    "через openat() / readdir()\n\n"
                    "Простір ядра (VFS):\n"
                    "1. Створення вузла-приймача\n"
                    "2. copy_file_range() або ioctl(FICLONE)\n"
                    "   → Якщо CoW (Btrfs/XFS): шаринг екстентів,\n"
                    "     нуль читань/записів на фізичний носій!\n"
                    "   → Якщо звичайний диск: прямий копір блоків\n"
                    "3. lsetxattr() / fchownat() / fchmodat()\n"
                    "4. Пост-обхід: utimensat() для каталогів\n\n"
                    "Переваги: максимальна швидкість на NVMe,\n"
                    "миттєве копіювання при CoW reflink.\n"
                    "Обмеження: лише в межах одного хоста.",
                    size=12, fill=BG, stroke=LINE))

    # 2. tar | tar
    p.append(fitbox(CX, 110, CW, 48, "2. tar -cf - . | tar -xpf -\n(Байтовий потік через Pipe / SSH)", size=14, fill=BLUE_FILL, stroke=NEG, bold=True))
    p.append(fitbox(CX, 170, CW, 440,
                    "Процес 1 (Архіватор tar):\n"
                    "• Серіалізація файлів, каталогів, метаданих,\n"
                    "  xattr та ACL у суцільний потік USTAR/PAX\n"
                    "• Запис у стандартний вивід stdout\n\n"
                    "Міжпроцесний канал (Pipe / SSH сокет):\n"
                    "• Буферизація ядра (64 КБ pipe buffer)\n"
                    "• Опціональне стиснення zstd / gzip\n\n"
                    "Процес 2 (Розархіватор tar):\n"
                    "• Читання зі stdin потоку блоків по 512 байтів\n"
                    "• Відновлення вузлів, розпакування вмісту,\n"
                    "  відновлення прав, xattr та міток часу\n\n"
                    "Переваги: без проміжних файлів на диску,\n"
                    "ідеально для передачі мережею через SSH.",
                    size=12, fill=BG, stroke=LINE))

    # 3. rsync
    p.append(fitbox(DX, 110, DW, 48, "3. rsync -aHAX --sparse\n(Трійка процесів та дельта)", size=14, fill=WARM_FILL, stroke=WARM, bold=True))
    p.append(fitbox(DX, 170, DW, 440,
                    "Архітектура з трьох компонентів:\n"
                    "1. Generator (Ціль):\n"
                    "   Сканує приймач, формує список файлів\n"
                    "   та хеші наявних блоків\n\n"
                    "2. Sender (Джерело):\n"
                    "   Порівнює список, шукає дельти,\n"
                    "   відправляє лише змінені фрагменти\n\n"
                    "3. Receiver (Ціль):\n"
                    "   Збирає оновлений файл у тимчасовий вузол,\n"
                    "   здійснює атомарне перейменування rename()\n\n"
                    "Переваги: ідемпотентність, докачування (--partial),\n"
                    "мінімальний трафік при регулярних бекапах.",
                    size=12, fill=BG, stroke=LINE))

    p.append(fitbox(50, 630, 1160, 95,
                    "Практичний вибір інструмента:\n"
                    "• Локальний бекап на тому ж сервері / CoW файлова система → cp -a --reflink=auto\n"
                    "• Одноразове швидке перенесення великого дерева через швидку мережу без дельти → tar pipe через SSH / nc\n"
                    "• Регулярна синхронізація, повільна або нестабільна мережа, інкрементне оновлення → rsync -aHAX --sparse",
                    size=13, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'copy-pipelines-architecture.svg'), W, H, *p,
           title="Архітектура трьох конвеєрів копіювання: cp, tar, rsync")


fig_metadata_loss_vs_preserved()
fig_rsync_delta_algorithm()
fig_copy_pipelines_architecture()
print("figures ok")
